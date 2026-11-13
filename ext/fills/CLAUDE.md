<!-- PMS fills for core CLAUDE.md. Only the fill blocks count; text between them is ignored. -->

<!-- fill:intro.what -->: a knowledge graph and a task layer in one set of files.<!-- /fill:intro.what -->

<!-- fill:intro.tasks-folder --> + `tasks/`<!-- /fill:intro.tasks-folder -->

<!-- fill:intro.todoist -->
**Tasks also live in Todoist, which is where the user sees and ticks them off.** Ownership is split by field: **the files own structure** — how work breaks down, what waits on what, what a task is about, where it is placed, and whether it was dropped. **Todoist owns execution state** — done or not, due date, priority, reminders, and the title as last edited. The files are the source of truth for knowledge and structure; Todoist is the source of truth for execution state. See **Todoist** below.

<!-- /fill:intro.todoist -->

<!-- fill:intro.task-schema -->, task schema<!-- /fill:intro.task-schema -->

<!-- fill:intro.todoist-policies -->, Todoist policies<!-- /fill:intro.todoist-policies -->

<!-- fill:intro.todoist-ids --> The Todoist ids that bind areas and projects are data, kept on those nodes.<!-- /fill:intro.todoist-ids -->

<!-- fill:intro.tasks-scale --> Tasks are cheaper but not free — archive terminal ones.<!-- /fill:intro.tasks-scale -->

<!-- fill:role.tasks --> track the user's tasks,<!-- /fill:role.tasks -->

<!-- fill:conduct.task-titles --> task titles,<!-- /fill:conduct.task-titles -->

<!-- fill:conduct.enums -->predicates, and enum values (`status`, `origin`)<!-- /fill:conduct.enums -->

<!-- fill:conduct.delete -->page, task, or edge<!-- /fill:conduct.delete -->

<!-- fill:conduct.dropped --> A cancelled task is `status: dropped`, not a deleted file.<!-- /fill:conduct.dropped -->

<!-- fill:gate.capture --> **Capture is the one exception** — a first message that is just "remind me to call Ana" gets the task written first, then the offer to configure. Before setup, capture writes the file but does **not** push it to Todoist: no account has been confirmed yet. Setup pushes those pending tasks when it finishes. Everything else waits for setup; capture waiting for setup is how a task tracker dies in its first minute.<!-- /fill:gate.capture -->

<!-- fill:router.setup -->"configure o PMS", "configure o KB", "configure o Todoist", "connect Todoist", "schedule the sync"<!-- /fill:router.setup -->

<!-- fill:router.capture -->
| Capture | "remind me to", "to do", "add a task", "action item", "lembra de", "preciso"; "mark T-0042 done", "drop that one" | `meta/skills/capture/SKILL.md` |
<!-- /fill:router.capture -->

<!-- fill:router.query -->, "what's on my plate", "o que está aberto", any lookup, traversal, or task list<!-- /fill:router.query -->

<!-- fill:router.plan-sync -->
| Plan | "plan", "break this down", "quebra em tarefas", "planeja", "what are the steps to…", re-plan an existing project | `meta/skills/plan/SKILL.md` |
| Sync | "sync", "sincroniza", "what did I finish on my phone", the scheduled daily run; any other skill needing Todoist | `meta/skills/sync/SKILL.md` |
<!-- /fill:router.plan-sync -->

<!-- fill:routing -->
**Plan vs. capture.** One thing to do is capture. A goal that needs several steps — "plan the move", "break this down", "what are the steps to…" — is plan. When unsure, capture it and offer to plan it.

**Routing precedence.** Capture and ingest both react to "add this" — they are told apart by *what* is being added, not by the verb. An **imperative aimed at the user's future self** ("remember to email Ana") is capture. **Material to be understood** — a file, an article, a transcript, pasted text — is ingest. When a request is genuinely both ("here's the meeting transcript, and remind me to follow up"), run ingest, which will call capture for the action items. When it is genuinely ambiguous, ask; do not guess and do not run both independently.

<!-- /fill:routing -->

<!-- fill:composition -->ingest calls capture for action items; capture and lint call setup for schema changes; query calls capture when the user turns an answer into a task; plan calls capture to write the tasks it designed; sync calls capture to apply what changed on the phone. **Every call to Todoist goes through sync** — capture and plan call it to push, query calls it to read, lint routes Todoist fixes through it. No other skill talks to Todoist. A skill never duplicates another's procedure — if you find yourself writing a task file from inside ingest, stop and follow `meta/skills/capture/SKILL.md` instead.<!-- /fill:composition -->

<!-- fill:layers.tasks -->
3. **`tasks/`** — Task nodes: one file per task, action item, or reminder. Also flat; terminal tasks move to `tasks/archive/`. Tasks are **part of the graph** (see below) — the folder split is about lifecycle, not membership.
<!-- /fill:layers.tasks -->

<!-- fill:layers.n4 -->4<!-- /fill:layers.n4 -->

<!-- fill:layers.index-readers -->every query, ingest, and capture starts by reading it<!-- /fill:layers.index-readers -->

<!-- fill:layers.task-template --> — and `_task.template.md` is the fixed task shape<!-- /fill:layers.task-template -->

<!-- fill:layers.n5 -->5<!-- /fill:layers.n5 -->

<!-- fill:layers.exits -->Outside this PMS folder it writes to exactly two places: **Todoist**, only through the sync skill, and the host's **scheduled tasks**, only at setup and only on the user's yes.<!-- /fill:layers.exits -->

<!-- fill:namings -->
**On the two namings.** Folders say what they *hold*: `knowledge/` holds knowledge pages, `tasks/` holds tasks, `raw/` holds inputs. The `meta/GRAPH_*` files say what they *span*: the index and the schema each cover the whole graph, which is `knowledge/` and `tasks/` at once. This is why `knowledge/` is deliberately **not** called `graph/` — the graph is not a folder, and naming one folder after it implies the other one isn't part of it. That implication is precisely the bug that makes an inbound-edge scan miss half the graph.
<!-- /fill:namings -->

<!-- fill:sources.exempt -->, except `area` and `project` nodes, which record an intent rather than something a source said. Tasks are exempt: a task's provenance is its `origin:` field, and only an `origin: ingest` task carries `sources:`.<!-- /fill:sources.exempt -->

<!-- fill:links.capture -->that is how capture leaves unrecognized mentions for lint to promote<!-- /fill:links.capture -->

<!-- fill:links.tasks --> A task is linked in piped form, `[[<file-stem>|<Title>]]` (see **Tasks**). An ingested source, when an `introduced_by` edge points at it, is linked the same way:<!-- /fill:links.tasks -->

<!-- fill:traversal -->
**The traversal set is `knowledge/` ∪ `tasks/`.** Both folders are one graph. "Following an edge" means reading or searching the predicate fields across **both** — a grep in Claude Code, a file scan in Cowork. This is load-bearing and easy to get wrong: outbound edges work either way, but **inbound** edges are found by scanning, so a scan scoped to `knowledge/` alone makes every task invisible to the node it points at. "What is blocking [[Project X]]?" is answered by tasks pointing *at* the project; scan one folder and the answer is silently empty. Scan both, always. By default the scan covers `knowledge/` plus the **root** of `tasks/`; include `tasks/archive/` only when the question is about history. That limit applies to *scanning*, not to *resolving*: an edge whose target is not in `knowledge/` or the root of `tasks/` may point at an archived task — look there before calling it missing. A link into `tasks/archive/` or `raw/archive/` is valid.
<!-- /fill:traversal -->

<!-- fill:tasks-todoist -->
## Tasks

A task is a node that carries state. It lives in `tasks/`, carries typed edges like any node, is traversed like any node, and appears in `meta/GRAPH_INDEX.md` like any node. Its schema — required fields, the closed `status` enum, the closed `origin` enum — is fixed in `meta/GRAPH_SCHEMA.md` § Tasks and is **not** extended per PMS.

**Filenames are date-slugged; identity is in the frontmatter.** A task file is `YYYY-MM-DD-short-slug.md` (`2026-08-15-email-ana.md`) and carries a stable `id:` (`T-0042`). The date prefix makes files sort chronologically and makes two captures on different days impossible to collide. **A link to a task names its file and displays its title:** `[[2026-08-15-email-ana|Email Ana about the Acme renewal]]` — never `[[T-0042]]`, and never the bare title, which resolves to no file. The index carries each task's link in exactly this form, so writers copy it rather than compose it.

**The next id comes from a counter, not from the entries.** `meta/GRAPH_INDEX.md` carries `next_task_id` in its frontmatter; capture takes that id and increments the counter in the same write. The counter only goes up. It cannot be derived from the listed entries, because archiving removes entries — the highest-numbered task may be the one archived, and "highest listed + 1" would hand its id out again. Only if the counter is missing, or is not above every id on disk, does finding the next id cost a scan of `tasks/` and `tasks/archive/`.

**Two sessions can run at once** — a scheduled sync can fire while the user is chatting. So **re-read `meta/GRAPH_INDEX.md` immediately before every write to it**, and never write it back from a copy read earlier in a long operation. Otherwise the other session's counter bump or new entries are silently undone. Lint's duplicate-id check is the backstop.

**Tasks are never deleted.** An abandoned task is `status: dropped` with a reason in `notes` — the record of a decision not to do something is worth as much as the record of doing it. Terminal tasks (`done`, `dropped`) carry a `closed:` date and may be moved to `tasks/archive/` once that date is older than the window in `meta/SETTINGS.md`; lint proposes the move, and nothing is archived automatically. Archiving **removes the task's index entry** — the file keeps its edges and its id forever, but the index stays bounded, which is what makes it cheap enough to read on every operation.

**Linking happens at runtime, cheaply.** Capture resolves only what one read of `meta/GRAPH_INDEX.md` can resolve — exact title and alias matches become typed edges. It **never creates stub nodes** for names it doesn't recognize; an unresolved mention stays a plain prose `[[wikilink]]`, which lint's untyped-link check will later offer to promote. This keeps capture fast enough to be worth using, and it keeps the graph free of empty pages invented by a one-line reminder.

## Todoist

The task surface. Everything here is enforced by the sync skill; the full mapping is in `meta/GRAPH_SCHEMA.md` § Todoist mapping.

- **One bucket by default.** A PMS is usually about one subject, so it lives in **one Todoist project** — its *bucket*, represented by the single `area` node. Every other Todoist project, and the Inbox, belong to the user: the PMS never reads or writes them. It manages more than one Todoist project only when the user explicitly asks at setup (`Mode: multiple` in `meta/SETTINGS.md` § Todoist). Several PMSes can share one Todoist account, each in its own bucket.
- **Areas and projects.** An `area` node maps to a Todoist **project** (in single mode there is exactly one: the bucket); a `project` node (`part_of` an area) maps to a **section** in that area's project; tasks map to tasks in the section; `part_of` another task maps to a subtask. The bindings (`todoist_project_id`, `todoist_section_id`) live in those nodes' frontmatter.
- **Who wins.** "Owned by Todoist" means that on a pull, Todoist's value overwrites the file. A change the user asks for *in chat* — a new due date, a rename — is written to the file and pushed at once, so the two agree without a conflict.
- **The join key is the task id, not Todoist's.** Every managed Todoist task ends its description with `PMS: <pms-id>/T-0042`, where `<pms-id>` comes from `meta/SETTINGS.md` § Todoist. The prefix is what tells two PMSes sharing one account apart. The file's `todoist_id` is a cache, refreshed when it stops resolving. Todoist has reissued every id before (its 2025 API migration), so identity must not depend on it.
- **Dependencies are the PMS's job.** Todoist has none. A task waiting on another carries the `pms-blocked` label and a `Waiting on:` line. Sync removes both when every `depends_on` target is finished. That recompute is the pipeline: it is what makes the next step appear.
- **Grouping tasks are uncompletable headers in Todoist**, because completing a Todoist parent completes all its open subtasks. Todoist shows a header with a `* ` prefix on its name; that prefix is Todoist's marker, never part of the title in the files. The PMS closes a group only when its children are all terminal, and pushes children before parents. A Todoist parent is never completed while it has open subtasks.
- **Never delete in Todoist.** `dropped` is completed + `pms-dropped`. A task deleted on the phone becomes `dropped` in the files, never a missing file.
- **Offline is safe.** Without Todoist reachable, capture still writes the file; a task with no `todoist_id` is simply *pending push*, and the next sync sends it.

<!-- /fill:tasks-todoist -->

<!-- fill:sources.touches --> and tasks<!-- /fill:sources.touches -->

<!-- fill:sources.task-output -->, and one or more tasks in `tasks/`<!-- /fill:sources.task-output -->

<!-- fill:sources.touches-tasks --> `touches:` may list paths in both `knowledge/` and `tasks/`.<!-- /fill:sources.touches-tasks -->
