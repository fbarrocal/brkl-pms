---
name: setup
description: Configure or evolve this Personal Management System's schema. Use on first run (setup_done is false or meta/SETTINGS.md is missing) to connect the services this PMS needs, interview the user and configure the PMS, and on later runs whenever the user wants to add or change node types, templates, or edge predicates — "add a node type", "configure o PMS", "configure o KB", "novo edge", "update the schema" — or when capture/ingest/lint flagged a type/predicate gap the user approved.
---

# Setup

Configures the two mutable rules files: `meta/SETTINGS.md` (purpose, language, conventions, `setup_done`) and `meta/GRAPH_SCHEMA.md` (node types, edge predicates) — plus templates in `meta/templates/`. **This skill is authoritative for both files**; no other skill edits them, and every schema change routes here. It never edits `CLAUDE.md`, and it never writes outside this PMS folder.

**Prerequisite:** `CLAUDE.md` — operate by it.

## Mode 1 — First run (`setup_done` false or `meta/SETTINGS.md` missing)

### Step 0 — Connect what this PMS needs (before the interview)

This PMS needs one connector: **Todoist**. One PMS serves one Todoist account. Check the connection before asking anything else: the Todoist answers in Q5 and Q6 depend on it, and a user who connects at the end has to be interviewed twice.

1. **Probe.** Ask sync for a read of the account (Mode 3: account info and project list). If it answers, note the account name and plan and go to the interview.
2. **If it can't reach Todoist, ask the user to authorize it.** If the host can present a connector card (for example, a connector-suggestion tool), use it to offer Todoist. Otherwise, tell the user in one line where to enable it: the Todoist connector in Claude's connector settings, for this project. Wait for them to say it's done, then probe again.
3. **Never ask for a password or API token in chat.** Authorization happens in the connector's own sign-in flow, not in this conversation.
4. **If the user declines or can't connect now,** carry on with the interview. Record `Connection: not connected` in `meta/SETTINGS.md` § Todoist and skip Q5 and Q6. Tasks are still captured; they wait as *pending push*. The next time any skill needs Todoist, sync will say so and offer this step again.

### The interview

Interview the user with the AskUserQuestion tool (structured options); fall back to plain chat questions if the tool is unavailable. Ask the questions themselves in whatever language the user is writing to you in. Keep it to six questions:

1. **Purpose.** What is this PMS for — a topic, a book, a project, personal notes, a work stream, a research area? Offer common options plus free text.
2. **Node types.** Based on the purpose, propose a small set to create. Examples: work PMS → `person`, `project`, `team`, `meeting`; a book → `character`, `place`, `event`; learning material → `formula`, `recipe`, `term`. The user approves, adjusts, or rejects each; the generic `entity` and `concept` always remain available, and `task` always exists (its schema is fixed — it is never proposed, extended, or removed).
3. **Edges.** Ask whether the shipped predicate set in `meta/GRAPH_SCHEMA.md` § Edges needs PMS-specific additions — a book might want `ally_of` / `enemy_of`; a work PMS might want `owns` or `blocks`. Propose; the user approves. **Cover task relationships in this same question**, and start from the position that nothing needs adding: subtasks are `part_of`, blocked tasks `depends_on`, a task's subject is `about`, an extracted action item is `introduced_by`. Only propose a task predicate the shipped set genuinely cannot express. If the user approved a `person` node type in Q2, this is also the moment to offer promoting the task `owner` string field into an `assigned_to` typed edge.
4. **Language.** What language should the *content* be written in — node titles, task titles, prose bodies, and answers? Default to the language the user is writing in, and offer the alternatives explicitly, because chat language and content language often differ (a user may write to you in Portuguese but want an English vault, or the reverse). This is the one setting that is expensive to change later: it is baked into every page title, and retitling pages breaks every wikilink pointing at them. Ask it even when the answer seems obvious.

5. **Todoist areas.** This PMS owns the connected Todoist account. List its existing projects from the Step 0 read. **By default each one becomes an `area` node** bound to that project's id; the user may exclude any, e.g. a project shared by someone else, or one that will stay a plain list. Excluded projects stay unmanaged, and sync never touches them. Take the plan (Free / Pro) from the account rather than asking: it sets `Plan` and `Deadlines` in `meta/SETTINGS.md` § Todoist. Do not create any Todoist project during setup — new areas are created when the first plan needs one.
6. **Schedule the sync.** Explain in one sentence why it matters: the sync is what brings phone completions into the PMS and unblocks the next steps, and Todoist Free keeps only one week of history. Then ask:
   - **Daily sync** — recommended; ask what time, in the user's timezone.
   - **Weekly quick lint** — optional.
   - **Not now.**
   If the user agrees and the host can create scheduled tasks, create them now, with prompts like *"Run the PMS sync (meta/skills/sync, Mode 2) and show me what got unblocked."* and *"Run the PMS lint, Pass A."* If the host can't schedule, give the user that exact text to add themselves. Record the outcome under `Sync schedule` in `meta/SETTINGS.md` § Todoist. Never schedule without a yes.

Then write it down, to the right file:

- **`meta/SETTINGS.md`** — the purpose under **Purpose**, the chosen language under **Language**, any convention the user changed, the § Todoist values from Step 0, Q5 and Q6, and `setup_done: true` in the frontmatter.
- **`meta/GRAPH_SCHEMA.md`** — the approved types under **Nodes** and any new predicates under **Edges**.
- **`knowledge/`** — one `area` node per Todoist project the user chose in Q5, from `meta/templates/area.md`, with `todoist_project_id` filled. Add each to the index.
- **`meta/templates/`** — one file per approved type, replicated from `meta/templates/_node.template.md`. Templates are optional; the user can skip them and add later when a kind of thing recurs enough to deserve structure. Never create or edit `_task.template.md` — the task shape is fixed.

Close with a one-line summary of what was configured and how to start: drop a file in `raw/` and ask to ingest, or just say what you need to do and it gets captured as a task.

## Mode 2 — Schema changes (`setup_done` true)

For adding or amending node types, templates, or predicates after first run:

1. Confirm the requested change (or the gap flagged by capture/ingest/lint that the user approved).
2. Propose the full definition — type name, fields, and template for a node type; predicate, meaning, and inverse for an edge. For a symmetric predicate, mark it **(symmetric)** in the inverse column — that marker is what makes the mirroring rule fire.
3. On approval: create or adjust the template in `meta/templates/`; register or update the entry in `meta/GRAPH_SCHEMA.md` § Nodes or § Edges.
4. Report what changed. Renames and removals follow the no-hard-delete rule: never remove a type or predicate still in use without explicit confirmation and a migration plan for the affected pages.

**Out of scope for Mode 2:** the task schema. `status` and `origin` are closed enums and the task field list is fixed in `meta/GRAPH_SCHEMA.md` § Tasks — changing them changes what every capture writes in every PMS, which makes it a rulebook decision, not a per-PMS one. If the user wants a sixth status, tell them plainly that the answer is a `notes` line or a `tags` entry, and that changing the enum means changing the template itself.

**Connectors and schedules** are also handled here after first run. "Connect Todoist" runs Step 0. "Schedule the sync" runs Q6. Neither re-runs the whole interview.

**Todoist bindings** are also a Mode 2 change: binding another existing Todoist project as an area, or unbinding one. Unbinding never touches Todoist. The area node keeps its history, its `todoist_project_id` is cleared, and its tasks become *unplaced* until re-homed.

Re-run the full Mode 1 interview only on request (or if the user sets `setup_done: false` again).
