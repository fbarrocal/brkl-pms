---
name: sync
description: >-
  Reconcile the PMS with Todoist, the task surface. Use this whenever the user says "sync", "sincroniza", "update from Todoist", "pull my tasks", "what did I finish on my phone", or on the scheduled daily run; and whenever another skill (capture, plan, query, setup, lint) needs to push a task to Todoist or read the account. This is the only skill that talks to Todoist.
---

# Sync

The bridge between the files and Todoist. **This skill is authoritative for every Todoist call** — no other skill reads from or writes to Todoist; they call this one. Ownership is split by field (see `CLAUDE.md` § Todoist): Todoist owns execution state, the files own structure.

**Prerequisite:** `CLAUDE.md` — operate by it. `meta/GRAPH_SCHEMA.md` § Tasks and § Todoist mapping are the authority for which field goes where. `meta/SETTINGS.md` § Todoist holds this PMS's bindings and policies.

**If Todoist is unreachable** (connector missing, not authorized, or failing), stop before writing anything, say so in one line, and leave every file as it is. If the connector was never connected or has lost its authorization, offer to run setup's Step 0 (connect Todoist). Tasks without a `todoist_id` simply stay pending and the next run pushes them. Never fake a sync result.

## Rules that apply in every mode

- **Stay inside the bound projects.** Read and write only the Todoist projects bound to `area` nodes — in single mode, just the bucket. The Inbox and every other project belong to the user: never read them, never write to them, never adopt from them.
- **The join key is the description footer `PMS: <pms-id>/T-0042`** (`<pms-id>` from `meta/SETTINGS.md` § Todoist), the last line of every managed Todoist task's description. `todoist_id` in the file is a cache of the Todoist id, not identity. When a stored `todoist_id` no longer resolves, find the task again by searching for its footer **within the bound projects only**. **Check the match is exact** — search is a substring match, so `PMS: x/T-004` also matches `x/T-0042`, and another PMS in the same account has its own `T-0042`.
- **Labels merge, never replace.** Updating labels replaces the whole list. Read the task's current labels first, then add or remove only `pms-blocked` and `pms-dropped`. Any other label belongs to the user. **Verify the write:** the labels Todoist returns must still include every non-`pms-*` label that was there before. If one is missing, put it back at once and report it — losing a user's label is data loss, and nothing downstream can detect it later.
- **Never delete anything in Todoist.** A dropped task is completed and labelled `pms-dropped`. A section or project for a finished PMS project is left in place; offer to archive it, never delete it.
- **Never move a task's project, section or parent in Todoist unless the files say so.** Moves are structural, so the files own them. Send `projectId` / `sectionId` / `parentId` only when they change: each one is treated as a move, and a section move also lifts the task out from under its parent.
- **Dates:** change a date with the reschedule operation, not a task update, so recurrence is never destroyed. Only push `deadline` when `meta/SETTINGS.md` § Todoist has Deadlines `on` — on Todoist Free it fails with `PREMIUM_ONLY`.
- **Terminal states go bottom-up.** Push children before parents for `done` and `dropped`. Never complete a Todoist parent that still has open subtasks: Todoist would complete them too, and the next pull would record them as done.
- **Batch.** Use the batch forms (up to 25 items per call). When a batch reports per-item failures, retry only the failed items, never the whole batch — the rest already happened.
- **No echo.** When sync calls capture to apply something that came *from* Todoist, it tells capture so. Capture then writes the file and does **not** call sync to push it back; otherwise every pulled change would bounce straight back to Todoist. Sync pushes the few things that do need to go back (an adopted task's footer, a recomputed label) itself.
- **Record what you did.** A completed **pull** (Mode 2) ends by setting `todoist_synced_at` in `meta/GRAPH_INDEX.md` frontmatter to the current timestamp. A partial pull leaves it unchanged and says which step stopped. Pushes and reads don't touch it — it marks the last full reconcile.

## Mode 1 — Push (called by capture, setup, plan, and lint fixes)

Input: one or more task ids whose files changed, or "all pending" (every task file with no `todoist_id`).

1. **Resolve placement from the graph, not from the user's words.**
   - Walk the task's `part_of` edges up through any parent tasks to the nearest `project` node, and from there to its `area`. If there is no `part_of` chain, use an `about` edge that points at a `project` or `area` node.
   - The area's `todoist_project_id` is the Todoist project; the project's `todoist_section_id` is the section.
   - A task `part_of` another task becomes a subtask of that task's `todoist_id`.
   - A task that reaches an area but no project goes in the area's project with no section.
   - A task that reaches neither goes to the bucket (the `Bucket` area in `meta/SETTINGS.md` § Todoist), outside any section. Never the Inbox.
   - If the area or project has no Todoist binding yet, create it first (project for an area, section for a project), write the new id into that node's frontmatter, and include it in the report. In single mode, a new Todoist project is created only for the bucket, at setup. A second area means the user asked for `multiple` mode, so otherwise stop and ask.
   - **Binding without tasks:** setup and plan may ask for just this step — create the bucket's project or a new project's section — so it shows up in Todoist before any task is pushed. If Todoist refuses the creation because of a plan limit, stop, report the limit, and suggest upgrading. Never work around it by putting the tasks somewhere else.
2. **Parents before children.** Push in tree order so every `parentId` exists before its subtasks are sent.
3. **Create or update.**
   - No `todoist_id` → search for the footer first (an earlier run may have created it and then stopped). Found → adopt that id. Not found → create.
   - Has `todoist_id` → update only what changed on the files' side: description body, labels (merged), placement (only if moved in the files), `isUncompletable` for grouping tasks, and title, due or priority **only when the change came from chat** (on a pull, Todoist owns those).
   - **Description:** the task's context line(s), then `Waiting on: T-0041 (<title>)` lines for each unfinished `depends_on` target, then `Deadline: <date>` if the task has one and Deadlines are `off`, then a blank line and `PMS: T-0042`.
   - **Grouping tasks** (any task with `part_of` children that was created by `plan`) are pushed as **uncompletable** headers. Completing a Todoist parent completes all its open subtasks, so a tickable parent is a one-tap way to falsely finish a whole branch. **Todoist marks a header by prefixing its name with `* `** (`1. Agendar` comes back as `* 1. Agendar`). That prefix is Todoist's marker, not part of the title: never write it into the file, and remove it when clearing `isUncompletable`.
4. **Status out** (children before parents for terminal states):
   - `blocked` → label `pms-blocked`.
   - `open` / `doing` → no `pms-blocked` label. `doing` itself is not mirrored.
   - `done` → complete. For an uncompletable group, clear `isUncompletable` first.
   - `dropped` → add `pms-dropped`, then complete (clearing `isUncompletable` first for a group).
   - Reopened (terminal → open) → uncomplete, and remove `pms-dropped`.
5. **Write back** each new `todoist_id` into its file and bump `updated`.

## Mode 2 — Pull (the reconcile; scheduled daily, or "sync")

1. **Read the bindings.** Every `area` node with a `todoist_project_id` is a managed Todoist project. Read each one's active tasks (an overview grouped by section is the cheapest call), plus completed tasks since `todoist_synced_at` (or the last 7 days if unset). Nothing else is read: no Inbox, no other project. If `todoist_synced_at` is more than six days old, warn: Todoist Free keeps one week of activity history.
2. **Match** each Todoist task to a file by its `PMS:` footer, and sort everything into four groups:
   - **Matched** → step 3.
   - **Todoist task with no footer (or another PMS's footer — leave those alone), inside a bound project** → added on the phone. **Adopt it:** call capture (Mode A, `origin: capture`) with its title, due date, priority and placement. Placement is `part_of` the project node bound to its section, or the area node if it has no section, or its parent task if it is a subtask. Then push the footer back (Mode 1). Recurring tasks are the exception: leave them alone and list them once in the report.
   - **A section in a managed project that no `project` node is bound to** → created on the phone. Create the `project` node for it (from `meta/templates/project.md`, `part_of` the area, `todoist_section_id` set, title = section name), add it to the index, and report it. This is adoption, like the tasks inside it. Renames of known sections or projects on the phone are reported, not adopted, because files own structure.
   - **A non-terminal file whose task is neither active nor completed since the last sync** → fetch that task by `todoist_id`. Not found → it was deleted on the phone: do not delete the file, but call capture (Mode B) to set `status: dropped` with the note `deleted in Todoist on <date>`. Found completed → treat as matched (step 3).
3. **Apply the Todoist-owned fields to matched files** — through capture Mode B, not by editing files here:
   - completed in Todoist, open in the file → `done`, `closed` set to the completion date;
   - reopened in Todoist → back to `open`, `closed` removed;
   - due date, priority, title changed in Todoist → copy into the file. **Compare titles without a leading `* `**: on a grouping task it is the header marker, not a rename. Without this, every pull would report every phase as renamed. After a title change, update the task's index entry. Links stay valid because they resolve by file stem; their display text is now stale, which lint reports as housekeeping.
   - moved to a different section, project or parent in Todoist → **do not adopt silently.** Report it and ask whether to update the task's `part_of` / `about` to match, or move it back.
4. **Recompute what is blocked — this is the planner's main job.**
   - For every non-terminal task with `depends_on`: it is blocked if any target is non-terminal, and unblocked when all are `done` or `dropped`.
   - A task blocked only by a `notes` reason (no `depends_on`) keeps whatever the user set.
   - Push label and status changes (Mode 1).
   - **List the newly unblocked tasks first in the report** — that is the news. When a task was unblocked only because what it waited on was *dropped*, say so: the user may want to drop it too.
5. **Close finished groups.** A grouping task whose children are all terminal becomes `done` if any child is `done`, or `dropped` if every child was dropped. Set it through capture, then push it (Mode 1 clears `isUncompletable` and completes it).
6. **Report:**

```
Todoist sync — <date> <time>
Done since last sync (N): T-0042 "<title>", …
Now unblocked (N): T-0051 "<title>" (was waiting on T-0042), …
Adopted from Todoist (N): T-0060 "<title>" in <Area> / <Project>
Dropped in Todoist (N): T-0033 "<title>"
Needs a decision (N): T-0047 moved to <section> on the phone — update the plan, or move it back?
Pending push: N tasks still without a Todoist id   (or "none")
```

## Mode 3 — Read (called by query, setup and lint)

Three kinds of read, never a write:

- **Account** (setup Step 0 and Q5): account name, plan (Free or Pro), and the list of projects with their sections and active-task counts — names and counts only, so the user can pick a bucket. Task contents of unbound projects are never read. This read is also the connection probe.
- **Task state** (query): for "what's on my plate", "what's due" or "what's blocked", read the bound projects only. Use the date-range read for due questions and the label read for `pms-blocked`. Return id (from the footer), title, due date, labels and Todoist link.
- **Per-area snapshot** (lint #20): one read per bound area, returning every task with its footer, completion state and labels.

**Do not write anything in this mode** — not files, not Todoist. If Todoist is unreachable, say so; query then falls back to the index and labels its answer with the index's `todoist_synced_at`.
