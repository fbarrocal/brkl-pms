---
name: sync
description: >-
  Reconcile the PMS with Todoist, the task surface. Use this whenever the user says "sync", "sincroniza", "update from Todoist", "pull my tasks", "what did I finish on my phone", or on the scheduled daily run; and whenever another skill (capture, plan, query, lint) needs to push a task to Todoist or read its live state. This is the only skill that talks to Todoist.
---

# Sync

The bridge between the files and Todoist. **This skill is authoritative for every Todoist call** — no other skill reads from or writes to Todoist; they call this one. Ownership is split by field (see `CLAUDE.md` § Todoist): Todoist owns execution state, the files own structure.

**Prerequisite:** `CLAUDE.md` — operate by it. `meta/GRAPH_SCHEMA.md` § Tasks and § Todoist mapping are the authority for which field goes where. `meta/SETTINGS.md` § Todoist holds this PMS's bindings and policies.

**If Todoist is unreachable** (connector missing or failing), stop before writing anything, say so in one line, and leave every file as it is. Tasks without a `todoist_id` simply stay pending and the next run pushes them. Never fake a sync result.

## Rules that apply in every mode

- **The join key is the description footer `PMS: T-0042`**, the last line of every managed Todoist task's description. `todoist_id` in the file is a cache of the Todoist id, not identity. When a stored `todoist_id` no longer resolves, find the task again by searching for its footer, and **check the match is exact** — search is a substring match, so `PMS: T-004` also matches `T-0042`.
- **Labels merge, never replace.** Updating labels replaces the whole list. Read the task's current labels first, then add or remove only `pms-blocked` and `pms-dropped`. Any other label belongs to the user.
- **Never delete anything in Todoist.** A dropped task is completed and labelled `pms-dropped`. A section or project for a finished PMS project is left in place; offer to archive it, never delete it.
- **Never move a task's project, section or parent in Todoist unless the files say so.** Moves are structural, so the files own them. Send `projectId` / `sectionId` / `parentId` only when they change: each one is treated as a move, and a section move also lifts the task out from under its parent.
- **Dates:** change a date with the reschedule operation, not a task update, so recurrence is never destroyed. Only push `deadline` when `meta/SETTINGS.md` § Todoist says `deadlines: on` — on Todoist Free it fails with `PREMIUM_ONLY`.
- **Batch.** Use the batch forms (up to 25 items per call). When a batch reports per-item failures, retry only the failed items, never the whole batch — the rest already happened.
- **No echo.** When sync calls capture to apply something that came *from* Todoist, it tells capture so. Capture then writes the file and does **not** call sync to push it back; otherwise every pulled change would bounce straight back to Todoist. Sync pushes the few things that do need to go back (an adopted task's footer, a recomputed label) itself.
- **Record what you did.** Every run ends by setting `todoist_synced_at` in `meta/GRAPH_INDEX.md` frontmatter to the current timestamp, but only if the run completed. A partial run leaves it unchanged and says which step stopped.

## Mode 1 — Push (called by capture, plan, and lint fixes)

Input: one or more task ids whose files changed, or "all pending" (every task file with no `todoist_id`).

1. **Resolve placement from the graph, not from the user's words.** Walk the task's `part_of` edges up to the nearest `project` node and that project's `area`. The area's `todoist_project_id` is the Todoist project; the project's `todoist_section_id` is the section. A task `part_of` another task becomes a subtask of that task's `todoist_id`. A task with no project and no area goes to the project named in `meta/SETTINGS.md` § Todoist `unplaced` (default: Inbox).
   - If the area or project has no Todoist binding yet, create it first (project for an area, section for a project), write the new id into that node's frontmatter, and include it in the report. Before creating a project, check the Free-plan cap in `meta/SETTINGS.md` § Todoist; if it would be exceeded, stop and ask.
2. **Parents before children.** Push in tree order so every `parentId` exists before its subtasks are sent.
3. **Create or update.**
   - No `todoist_id` → search for the footer first (an earlier run may have created it and then stopped). Found → adopt that id. Not found → create.
   - Has `todoist_id` → update only the fields the files own and that changed: title (only on create — afterwards Todoist owns it), description body, labels (merged), placement (only if moved in the files), `isUncompletable` for grouping tasks.
   - **Description:** the task's context line(s), then `Waiting on: T-0041 (<title>)` lines for each unfinished `depends_on` target, then a blank line and `PMS: T-0042`.
   - **Grouping tasks** (any task with `part_of` children that was created by `plan`) are pushed as **uncompletable** headers. Completing a Todoist parent completes all its open subtasks, so a tickable parent is a one-tap way to falsely finish a whole branch.
4. **Status out:**
   - `blocked` → label `pms-blocked`.
   - `done` → complete.
   - `dropped` → add `pms-dropped`, then complete.
   - Reopened (terminal → open) → uncomplete.
   - `doing` is PMS-only and not mirrored.
5. **Write back** each new `todoist_id` into its file and bump `updated`.

## Mode 2 — Pull (the reconcile; scheduled daily, or "sync")

1. **Read the bindings.** Every `area` node with a `todoist_project_id` is a managed Todoist project. Read each one's active tasks (an overview grouped by section is the cheapest call), plus completed tasks since `todoist_synced_at` (or the last 7 days if unset). If `todoist_synced_at` is more than six days old, warn: Todoist Free keeps one week of activity history.
2. **Match** each Todoist task to a file by its `PMS:` footer. This gives four groups:
   - **Matched** → step 3.
   - **Todoist task with no footer, inside a managed section or project** → added on the phone. **Adopt it:** call capture (Mode A, `origin: capture`) with its title, due date and placement, then push the footer back (Mode 1). Recurring tasks are the exception: leave them alone and list them once in the report.
   - **File with a `todoist_id` that Todoist no longer has, active or completed** → deleted on the phone. Do not delete the file. Call capture (Mode B) to set `status: dropped` with the note `deleted in Todoist on <date>`.
   - **Inbox items with no footer** → not adopted. List up to ten, newest first, as triage suggestions ("want any of these in the PMS?").
3. **Apply the Todoist-owned fields to matched files** — through capture Mode B, not by editing files here:
   - completed in Todoist, open in the file → `done`, `closed` set to the completion date;
   - reopened in Todoist → back to `open`, `closed` removed;
   - due date, priority, title changed in Todoist → copy into the file. After a title change, update the task's index entry. Links stay valid because they resolve by file stem; their display text is now stale, which lint reports as housekeeping.
   - moved to a different section, project or parent in Todoist → **do not adopt silently.** Report it and ask whether to update the task's `part_of` / `about` to match, or move it back.
4. **Recompute what is blocked — this is the planner's main job.**
   - For every non-terminal task with `depends_on`: it is blocked if any target is non-terminal, and unblocked when all are `done` or `dropped`.
   - A task blocked only by a `notes` reason (no `depends_on`) keeps whatever the user set.
   - Push label and status changes (Mode 1).
   - **List the newly unblocked tasks first in the report** — that is the news.
5. **Close finished groups.** A grouping task whose children are all terminal is `done`. Set it through capture and push it: clear `isUncompletable`, then complete it.
6. **Report:**

```
Todoist sync — <date> <time>
Done since last sync (N): T-0042 "<title>", …
Now unblocked (N): T-0051 "<title>" (was waiting on T-0042), …
Adopted from Todoist (N): T-0060 "<title>" in <Area> / <Project>
Dropped in Todoist (N): T-0033 "<title>"
Needs a decision (N): T-0047 moved to <section> on the phone — update the plan, or move it back?
Inbox triage (N): "<title>", …          (or "none")
Pending push: N tasks still without a Todoist id   (or "none")
```

## Mode 3 — Read (called by query)

For "what's on my plate", "what's due", "what's blocked", read state from Todoist for the managed projects: the date-range read for due questions, the label read for `pms-blocked`. Return it to query as id, title, due date, labels and Todoist link. **Do not write anything in this mode** — not files, not Todoist. If Todoist is unreachable, say so; query then falls back to the index and labels its answer with the index's `todoist_synced_at`.
