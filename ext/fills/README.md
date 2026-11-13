<!-- PMS fills for core README.md. Only the fill blocks count; text between them is ignored. -->

<!-- fill:intro -->
**v{{VERSION}}** — the PMS (a knowledge graph with a task layer) with **Todoist as the task surface**. The PMS plans: it breaks goals into tasks, tracks what waits on what, and links work to what you know. Todoist is where you see, get reminded about, and tick off the tasks, on every device. The files own structure; Todoist owns execution state. Design record: `docs/adr/001-todoist-task-surface.md` in the template repository.

It needs the **Todoist connector** enabled in Claude; setup asks you to connect it. Without it, the knowledge side works and tasks queue up as *pending push*.

Two things go in — material you want understood, and things you need to do — and both end up as typed, cross-referenced nodes in one graph.
<!-- /fill:intro -->

<!-- fill:blurb -->
> This project is a Personal Management System: a self-curated knowledge graph with a task layer. Sources go in, typed and cross-referenced knowledge comes out, goals are planned into tasks that live in Todoist, and questions are answered from all of it. `CLAUDE.md` in this folder is the operating manual — follow it for every request; it defines the curator's role and conduct and routes every operation (setup, capture, plan, ingest, query, sync, lint) to its procedure under `meta/skills/`. This PMS's vocabulary lives in `meta/GRAPH_SCHEMA.md` and its configuration in `meta/SETTINGS.md`.
<!-- /fill:blurb -->

<!-- fill:first-message -->
   - **Connect Todoist.** It checks the Todoist connector first. If it isn't authorized yet, it asks you to connect it and waits. It never asks for a password or token in chat.
   - **A short interview:** purpose, node types, edges, language, which Todoist project this PMS lives in (a new one named after it, by default), and whether to **schedule the daily sync** (plus an optional weekly lint). It creates the scheduled tasks only if you say yes.
   - **One exception:** if your first message is a task ("remind me to call Ana"), it captures the task first and offers setup after. That task reaches Todoist when setup finishes. You should never have to sit through an interview to write down one thing you need to do.
<!-- /fill:first-message -->

<!-- fill:use.tasks --> Say "remind me to…" and it becomes a task. Ask questions of either.<!-- /fill:use.tasks -->

<!-- fill:use.sync -->
6. **Don't skip the sync schedule.** The sync is what moves completions from your phone into the PMS and unblocks the next steps. If you said "not now" during setup, say "schedule the sync" any time.
<!-- /fill:use.sync -->

<!-- fill:layout.tasks -->
├── tasks/                   # one file per task; terminal ones move to tasks/archive/
<!-- /fill:layout.tasks -->

<!-- fill:layout.index --> — nodes + tasks, with aliases and statuses<!-- /fill:layout.index -->

<!-- fill:layout.schema -->, task schema<!-- /fill:layout.schema -->

<!-- fill:layout.settings -->, conventions, Todoist policies<!-- /fill:layout.settings -->

<!-- fill:layout.skills -->setup / capture / plan / ingest / query / sync / lint<!-- /fill:layout.skills -->

<!-- fill:layout.seed -->├── _node.template.md<!-- /fill:layout.seed -->

<!-- fill:layout.pms-templates -->
        ├── _task.template.md   # the fixed task shape — never copied, never customized
        ├── area.md             # an area = one Todoist project
        └── project.md          # a project = one section in its area's Todoist project
<!-- /fill:layout.pms-templates -->

<!-- fill:split.exits --> Outside this folder, the agent writes only to Todoist (through the sync skill) and, at setup and on your yes, to the scheduled tasks.<!-- /fill:split.exits -->

<!-- fill:split.yours -->Knowledge and work (`raw/`, `knowledge/`, `tasks/`) are yours<!-- /fill:split.yours -->

<!-- fill:how.title -->**Curator + graph + tracker in one.**<!-- /fill:how.title -->

<!-- fill:how.tasks --> Things you need to do become task nodes in `tasks/`, connected by the same edges.<!-- /fill:how.tasks -->

<!-- fill:how.task-bullets -->
- **`tasks/` is part of the graph, not a sidecar.** The folder split is about lifecycle — tasks complete, knowledge accretes — but a task carries the same typed edges and is traversed with the same scan. That's what makes "what's blocking Project X?" answerable: the tasks point at the project, and the query looks in both folders.
- **Tasks reuse the same predicate vocabulary.** A subtask is `part_of`; a blocked task `depends_on`; a task's subject is `about`; an extracted action item is `introduced_by` its source. No task-specific predicates ship, and most PMS installs never need one.
- **Capture is deliberately cheap.** Say "remind me to email Ana about Acme" and you get one file, one index line, the same task in Todoist, and a one-line confirmation. It resolves links only against names already in the index — it will never invent an empty `[[Acme]]` page just because you mentioned it. Unrecognized mentions stay plain links, and lint offers to promote the ones that keep recurring.
- **Nothing is deleted.** A cancelled task is `status: dropped` with a reason, not a missing file. The record of deciding *not* to do something is worth keeping. Finished tasks get a `closed` date and, after a while, move to `tasks/archive/` — where they keep every edge but drop out of the index, so the index stays small enough to stay cheap.
<!-- /fill:how.task-bullets -->

<!-- fill:how.touches --> and tasks<!-- /fill:how.touches -->

<!-- fill:how.action-items --> Ingest also pulls action items out of meeting notes and transcripts, handing them to capture.<!-- /fill:how.action-items -->

<!-- fill:ops.count -->seven<!-- /fill:ops.count -->

<!-- fill:ops.capture -->
| "remind me to…", "add a task", "mark T-0042 done" | **capture** — one task file, linked to what it already knows, pushed to Todoist; also updates, completes or drops a task |
<!-- /fill:ops.capture -->

<!-- fill:ops.ingest -->nodes, edges, and any action items it finds<!-- /fill:ops.ingest -->

<!-- fill:ops.query-says -->, "what's blocking X", "what's open"<!-- /fill:ops.query-says -->

<!-- fill:ops.query-does -->lookup, traversal, or task triage<!-- /fill:ops.query-does -->

<!-- fill:ops.setup-says -->, "connect Todoist", "schedule the sync"<!-- /fill:ops.setup-says -->

<!-- fill:ops.setup-does -->; also connects Todoist and schedules the sync<!-- /fill:ops.setup-does -->

<!-- fill:ops.plan-sync -->
| "plan X", "break this down", "quebra em tarefas" | **plan** — proposes a task tree with dependencies, writes it on approval, and puts the whole tree in Todoist |
| "sync", or the daily scheduled run | **sync** — pulls what you did on your phone, adopts tasks you added there, and unblocks what can now start |
<!-- /fill:ops.plan-sync -->

<!-- fill:ops.lint -->20 health checks in three cost tiers, including Todoist drift<!-- /fill:ops.lint -->

<!-- fill:ops.composition -->ingest calls capture for action items, plan calls capture for its tree, every Todoist call goes through sync, and lint<!-- /fill:ops.composition -->

<!-- fill:read.task-board -->
Dataview can show a task board without leaving Obsidian: `TABLE status, due FROM "tasks" WHERE status != "done" AND status != "dropped"`. It reads the files, so it reflects Todoist only as of the last sync — Todoist itself is the live board.

<!-- /fill:read.task-board -->

<!-- fill:obsidian.tasks --> and `tasks/`<!-- /fill:obsidian.tasks -->

<!-- fill:obsidian.exclude-tasks --> Do **not** exclude `tasks/` — tasks are real nodes and excluding them hides half your graph.<!-- /fill:obsidian.exclude-tasks -->

<!-- fill:todoist-upgrade -->
## How Todoist is used

| In the PMS | In Todoist |
|---|---|
| the PMS itself (its single **area**) | one project — the PMS's bucket, e.g. "Saúde" |
| a **project** (e.g. "Check-up 2026") | a section of that project |
| a task in the project | a task in the section |
| a task that is part of another task | a subtask |
| a group of steps created by `plan` | a parent you can't tick (completing a Todoist parent would complete every step under it) |
| a step waiting on another | label `pms-blocked` + a "Waiting on:" line — removed by sync when it can start |
| dropped | completed + label `pms-dropped` (nothing is ever deleted) |

**What you can do on your phone:** complete, reopen, reschedule, rename, add reminders and your own labels, and add new tasks inside the bucket. Sync picks all of that up.
**What to do in the PMS instead:** restructure — move a task to another project, change what waits on what, drop a task with a reason. If you move a task on the phone, sync asks you rather than guessing.
**Everything else is yours.** The PMS reads and writes only its bucket. Your Inbox and your other projects are never touched, so one Todoist account can hold several PMSes, each in its own project. If you want a PMS to manage several Todoist projects, say so at setup (`multiple` mode: one project per area). **Plan limits are yours to lift:** on Todoist Free (5 active projects, no deadlines, one week of activity history), the PMS tells you when a limit blocks something and suggests upgrading. It doesn't work around it. On Free, `deadline` stays in the file and appears in the task description.

## Upgrading from v2.1.x (tasks in files only)

1. Copy in this template's `CLAUDE.md`, all of `meta/skills/`, and `meta/templates/` (including `area.md` and `project.md`).
2. Merge `meta/GRAPH_SCHEMA.md`: add the `area` and `project` node types, the four-value `origin` enum, the task fields `deadline` and `todoist_id`, and the § Todoist mapping section. Keep your own types and predicates.
3. Add the § Todoist section to `meta/SETTINGS.md`, and `todoist_synced_at:` to the index frontmatter.
4. Say "configure o Todoist": setup connects Todoist, sets up the bucket project, and offers to schedule the sync. Then say "sync — push all pending" so every existing open task goes to Todoist.

For anything older than v2.1, start from the README at tag `v2.1.0` in the template repository.

<!-- /fill:todoist-upgrade -->

<!-- fill:local.todoist -->, and your tasks (titles and short context) live in Todoist<!-- /fill:local.todoist -->

<!-- fill:ceiling.tasks --> Tasks are cheaper, but archive the terminal ones.<!-- /fill:ceiling.tasks -->
