<!-- PMS fills for core meta/GRAPH_SCHEMA.md. Only the fill blocks count; text between them is ignored. -->

<!-- fill:intro.todoist -->, Todoist policies<!-- /fill:intro.todoist -->

<!-- fill:nodes.ships -->Ships with four: two generic defaults (`entity`, `concept`) and the two that structure work (`area`, `project`).<!-- /fill:nodes.ships -->

<!-- fill:nodes.area-project -->
- **`area`** — a standing sphere of responsibility (health, a job, a hobby). Maps to a **Todoist project**. In the default single mode there is exactly **one** area — the PMS's bucket in Todoist, usually named after the PMS itself. More than one exists only in `multiple` mode (`meta/SETTINGS.md` § Todoist). Fields: `title`, `aliases`, `tags`, `todoist_project_id`, typed-edge fields, `see_also`. Template: `meta/templates/area.md`. Areas are long-lived; finished work closes at the project level, not the area level.
- **`project`** — a finite outcome with an end (move flat, launch X). Maps to a **section** of its area's Todoist project. Fields: `title`, `aliases`, `tags`, `todoist_section_id`, `part_of` (its area), optional `outcome`, typed-edge fields, `see_also`. Template: `meta/templates/project.md`.

`area` and `project` ship with the template and are always present. They are written by setup (binding existing Todoist projects and sections), by plan (new projects and areas), and by sync (sections created on the phone) — never by ingest from a source. That is why they are exempt from the provenance requirement: they record an intent, not something learned from a source.
<!-- /fill:nodes.area-project -->

<!-- fill:tasks-mapping -->
## Tasks

`task` is a node type like any other for the purposes of the graph — it carries typed edges, it is traversed, it appears in `meta/GRAPH_INDEX.md`. It differs in exactly two ways, and only these two:

1. **It lives in `tasks/`, not `knowledge/`** — because it has a completion lifecycle, while knowledge nodes accrete.
2. **It is not required to have `sources:`** — a task usually originates from a human intent, not from a file in `raw/`. Its `origin:` field records where it came from instead.

Unlike node types under **Nodes**, the task schema is **fixed** — it is not extended per PMS. Adding a field to it changes what every capture writes, so treat it as a rulebook-level change, not a setup-time one.

**Fields.** `type` (always the literal `task`), `id`, `title`, `status`, `origin`, `created`, `updated` are required. `due`, `deadline`, `priority` (`p1`–`p4`, as in Todoist), `owner`, `tags`, `notes` are optional and omitted entirely when unknown — never filled with a placeholder. `todoist_id` is written only by the sync skill. Its absence means the task has not been pushed yet. `closed` is required **once and only once the status is terminal**. Template: `meta/templates/_task.template.md`.

`closed` exists because `updated` cannot answer "how long has this been done?" — `updated` bumps on any edit, so a task finished two months ago and touched yesterday looks fresh. Without a separate date, the archive window is unenforceable and lint's archivable check is guesswork. Set `closed` to the date the status became `done` or `dropped`; clear it if the task is ever reopened.

**`status` — closed enum, exactly five values:**

| status | meaning |
|---|---|
| `open` | captured, not started |
| `doing` | actively in progress |
| `blocked` | cannot proceed; what it waits on is a `depends_on` edge or a `notes` line |
| `done` | completed |
| `dropped` | deliberately abandoned — kept, never deleted |

`done` and `dropped` are the two **terminal** states, and the only ones eligible for `tasks/archive/`. There is no sixth value and no free-text status; a state you cannot express with these five is a `notes` line, not a new status.

**Archiving removes the index entry.** A task in `tasks/archive/` is out of `meta/GRAPH_INDEX.md` entirely — exactly like an archived source in `raw/archive/`. This is what keeps the index bounded: tasks are the fastest-growing file type in the system, and an index that accumulates every one of them forever defeats the "one cheap read" that capture and query triage both depend on. Archived tasks keep their frontmatter and their edges; they are found by scanning `tasks/archive/`, which only a history question does.

**`origin` — closed enum, exactly four values:** `capture` (a human said so — in chat, or added directly in Todoist and adopted by sync), `ingest` (an action item extracted from a source in `raw/`), `query` (surfaced while answering), `plan` (designed by the plan skill as part of a project's tree). When `origin` is `ingest`, the task also carries `sources:` pointing at the archived source — that is the one case where a task has provenance.

**Ownership.** `owner` is a **plain string field**, not a typed edge, because a PMS with no `person` node type has nowhere to point. If this PMS later registers a `person` type, setup should offer to promote `owner` into an `assigned_to` typed edge and register the predicate below. Until then, do not write `assigned_to`.

## Todoist mapping

Fixed by the rulebook, like the task schema. The sync skill applies it.

| PMS | Todoist | Owned by |
|---|---|---|
| `area` node | project (`todoist_project_id`) | files |
| `project` node | section in its area's project (`todoist_section_id`) | files |
| task `part_of` a project | task in that section | files (placement) |
| task `part_of` an area, no project — or with no placement at all | task in the area's project (the bucket, in single mode), no section | files (placement) |
| task `part_of` a task | subtask | files (placement) |
| task with children, created by plan | **uncompletable** parent | files |
| `depends_on` | `pms-blocked` label + `Waiting on:` description line | files (recomputed by sync) |
| `status: done` / `closed` | completed / completion date | **Todoist** |
| `status: dropped` | completed + `pms-dropped` label | files |
| `status: open` / `doing` | active, no `pms-*` label (`doing` is not mirrored) | files |
| `due` | due date | **Todoist** |
| `deadline` | deadline (Pro only; see `meta/SETTINGS.md` § Todoist) | **Todoist** when enabled, else files |
| `title` | content | **Todoist** after creation |
| `id` | description footer `PMS: <pms-id>/T-0042` | files |
| `priority` | priority | **Todoist** |
| other labels, reminders | as in Todoist | **Todoist** (never copied into files) |

"Owned by **Todoist**" means a pull overwrites the file with Todoist's value. A change the user makes in chat is written to the file and pushed at once, so it doesn't conflict.

<!-- /fill:tasks-mapping -->

<!-- fill:edges.tasks --> The same vocabulary governs `knowledge/` and `tasks/` — a task does not get its own predicate set.<!-- /fill:edges.tasks -->

<!-- fill:edges.about -->/task<!-- /fill:edges.about -->

<!-- fill:edges.task-reuse -->
**Tasks reuse this vocabulary — they do not need additions to work.** The common task relationships already have predicates: a subtask is `part_of` its parent; a blocked task `depends_on` what it waits for; a task is `about` the topic or project it concerns; a task extracted from a source is `introduced_by` that source. Reach for an existing predicate before proposing a new one — the value of a closed vocabulary is that it stays small.

<!-- /fill:edges.task-reuse -->
