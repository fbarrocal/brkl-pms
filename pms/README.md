# Personal Management System template

**v2.6.0** — the PMS (a knowledge graph with a task layer) with **Todoist as the task surface**. The PMS plans: it breaks goals into tasks, tracks what waits on what, and links work to what you know. Todoist is where you see, get reminded about, and tick off the tasks, on every device. The files own structure; Todoist owns execution state. Design record: `docs/adr/001-todoist-task-surface.md` in the template repository.

It needs the **Todoist connector** enabled in Claude; setup asks you to connect it. Without it, the knowledge side works and tasks queue up as *pending push*.

Two things go in — material you want understood, and things you need to do — and both end up as typed, cross-referenced nodes in one graph.

## Quick start (Cowork)

**Project description — paste this when creating the project:**

> This project is a Personal Management System: a self-curated knowledge graph with a task layer. Sources go in, typed and cross-referenced knowledge comes out, goals are planned into tasks that live in Todoist, and questions are answered from all of it. `CLAUDE.md` in this folder is the operating manual — follow it for every request; it defines the curator's role and conduct and routes every operation (setup, capture, plan, ingest, query, sync, lint) to its procedure under `meta/skills/`. This PMS's vocabulary lives in `meta/GRAPH_SCHEMA.md` and its configuration in `meta/SETTINGS.md`.

Then:

1. **Rename & place this folder** to your PMS's name (e.g. `My-PMS`, `Work`, `Book-Notes`) and put it where you keep your files.
2. **Enable file operations.** Claude Desktop → Settings → Capabilities → turn on **Code execution and file creation**.
3. **Create the project starting FROM this folder.** Cowork tab → Projects → **New project → "Use an existing folder"** → select this folder. Start from the folder — don't create an empty project and try to attach the folder afterwards. Paste the blurb above into the project description/instructions. Keep **Memory on**.
4. **Send your first message.** Because `setup_done` is `false`, the agent runs the setup skill:
   - **Connect Todoist.** It checks the Todoist connector first. If it isn't authorized yet, it asks you to connect it and waits. It never asks for a password or token in chat.
   - **A short interview:** purpose, node types, edges, language, which Todoist project this PMS lives in (a new one named after it, by default), and whether to **schedule the daily sync** (plus an optional weekly lint). It creates the scheduled tasks only if you say yes.
   - **One exception:** if your first message is a task ("remind me to call Ana"), it captures the task first and offers setup after. That task reaches Todoist when setup finishes. You should never have to sit through an interview to write down one thing you need to do.
5. **Then just use it.** Drop material in `raw/` and ask to ingest. Say "remind me to…" and it becomes a task. Ask questions of either.
6. **Don't skip the sync schedule.** The sync is what moves completions from your phone into the PMS and unblocks the next steps. If you said "not now" during setup, say "schedule the sync" any time.

## Layout

```
your-pms-folder/
├── README.md                # this file — start here
├── CLAUDE.md                # static rulebook: role, conduct, how to operate, how it works
├── .gitignore               # for the later Claude Code + Git step
├── raw/                     # inbox — root holds pending only; ingest archives
│                            # processed files to raw/archive/
├── knowledge/               # node pages, flat; a node's type is a field, not a folder
├── tasks/                   # one file per task; terminal ones move to tasks/archive/
└── meta/                    # the machinery (visible on purpose)
    ├── GRAPH_INDEX.md       # navigation entry point — nodes + tasks, with aliases and statuses
    ├── GRAPH_SCHEMA.md      # the closed vocabulary: node types, task schema, edge predicates
    ├── SETTINGS.md          # this PMS's purpose, language, conventions, Todoist policies, setup state
    ├── skills/              # setup / capture / plan / ingest / query / sync / lint — single source of truth
    └── templates/
        ├── _node.template.md   # generic seed — copy to meta/templates/<type>.md
        ├── _task.template.md   # the fixed task shape — never copied, never customized
        ├── area.md             # an area = one Todoist project
        └── project.md          # a project = one section in its area's Todoist project
```

The split that matters: `CLAUDE.md` is static and identical across every PMS you build from it — the agent never edits it. Outside this folder, the agent writes only to Todoist (through the sync skill) and, at setup and on your yes, to the scheduled tasks. Everything that configures THIS PMS lives in exactly two files, both under `meta/`: `GRAPH_SCHEMA.md` (what may exist) and `SETTINGS.md` (what this PMS is). Knowledge and work (`raw/`, `knowledge/`, `tasks/`) are yours; machinery (`meta/`) is the system's. To upgrade the rulebook across many systems later, copy one file.

## How it works

- **Curator + graph + tracker in one.** The agent reads pending items in `raw/` and writes synthesized node pages into `knowledge/`, connecting them with **typed edges**. Things you need to do become task nodes in `tasks/`, connected by the same edges.
- **Nodes are typed.** Every page in the flat `knowledge/` folder has a `type:` (e.g. `entity`, `concept`, or a PMS-specific type like `person` or `character`). The frontmatter is the structured catalog layer; the prose body is the knowledge layer — both at once.
- **`tasks/` is part of the graph, not a sidecar.** The folder split is about lifecycle — tasks complete, knowledge accretes — but a task carries the same typed edges and is traversed with the same scan. That's what makes "what's blocking Project X?" answerable: the tasks point at the project, and the query looks in both folders.
- **Tasks reuse the same predicate vocabulary.** A subtask is `part_of`; a blocked task `depends_on`; a task's subject is `about`; an extracted action item is `introduced_by` its source. No task-specific predicates ship, and most PMS installs never need one.
- **Capture is deliberately cheap.** Say "remind me to email Ana about Acme" and you get one file, one index line, the same task in Todoist, and a one-line confirmation. It resolves links only against names already in the index — it will never invent an empty `[[Acme]]` page just because you mentioned it. Unrecognized mentions stay plain links, and lint offers to promote the ones that keep recurring.
- **Nothing is deleted.** A cancelled task is `status: dropped` with a reason, not a missing file. The record of deciding *not* to do something is worth keeping. Finished tasks get a `closed` date and, after a while, move to `tasks/archive/` — where they keep every edge but drop out of the index, so the index stays small enough to stay cheap.
- **Provenance runs both ways.** Each node carries a `sources:` field listing the source items it was built from, and each source carries `touches:` listing the pages and tasks it fed. Lint checks the round-trip, so a page nothing supports is visible rather than plausible.
- **Drop anything in `raw/`.** Files don't need to arrive tagged — ingest stamps the bookkeeping frontmatter it needs. Binaries (PDFs, images, audio) get a small `.md` sidecar that carries that frontmatter for them. Ingest also pulls action items out of meeting notes and transcripts, handing them to capture.
- **Edges are typed frontmatter fields** — a relationship is a frontmatter field named for the predicate, holding wikilinks (e.g. `part_of: ["[[A Larger Thing]]"]`, `contradicts: ["[[A Rival Claim]]"]`). Because it's plain frontmatter, the whole Obsidian metadata ecosystem can read the graph — no plugin required (see **How to read the content**).
- **Retrieval is navigation, not vector search.** The agent reads `meta/GRAPH_INDEX.md` and traverses typed edges — no embeddings.

## The seven operations

| You say | It runs |
|---|---|
| "remind me to…", "add a task", "mark T-0042 done" | **capture** — one task file, linked to what it already knows, pushed to Todoist; also updates, completes or drops a task |
| drop a file in `raw/`, "ingest this" | **ingest** — nodes, edges, and any action items it finds |
| "what do I know about X", "what's blocking X", "what's open" | **query** — lookup, traversal, or task triage |
| "add a node type", "novo edge", "connect Todoist", "schedule the sync" | **setup** — the only skill that edits the schema; also connects Todoist and schedules the sync |
| "plan X", "break this down", "quebra em tarefas" | **plan** — proposes a task tree with dependencies, writes it on approval, and puts the whole tree in Todoist |
| "sync", or the daily scheduled run | **sync** — pulls what you did on your phone, adopts tasks you added there, and unblocks what can now start |
| "lint", "what's broken" | **lint** — 20 health checks in three cost tiers, including Todoist drift; proposes but never applies unasked |

Each operation is owned by exactly one skill, and skills call each other rather than duplicating work: ingest calls capture for action items, plan calls capture for its tree, every Todoist call goes through sync, and lint routes its fixes back through the skill that owns them.

## How to read the content

Everything is plain markdown, so any editor works. `meta/GRAPH_INDEX.md` is the reading entry point, and because the edges are plain frontmatter, these tools consume the typed graph directly:

| Tool | Reads the typed edges via |
|---|---|
| Obsidian core graph | frontmatter links render natively (plain, unlabeled lines) |
| Dataview | frontmatter fields directly (`file.part_of`, `file.uses`, …) |
| Graph Link Types | Dataview metadata — draws each predicate as a label on the graph edge |
| Breadcrumbs | frontmatter fields you map as relation types in its settings |
| Juggl | Dataview metadata |

Dataview can show a task board without leaving Obsidian: `TABLE status, due FROM "tasks" WHERE status != "done" AND status != "dropped"`. It reads the files, so it reflects Todoist only as of the last sync — Todoist itself is the live board.

### Obsidian

**Open the vault at the PMS's root folder, not at `knowledge/`.** The vault takes the folder's name — and since you renamed the folder to your PMS's name at setup, each system gets a distinct vault name. Pointing Obsidian at `knowledge/` instead would name every vault "knowledge" and cut the vault off from `raw/` and `tasks/`.

With the vault at the root, the machinery (`CLAUDE.md`, `meta/`, …) shows up in search and graph. Two ways to hide it:

- **Excluded files (recommended — hides machinery everywhere).** Settings → **Files and links → Excluded files** → add `meta/`, `raw/`, `CLAUDE.md`, `README.md`. This removes them from search, link suggestions, *and* the graph. Drop `raw/` from the list if you want raw inputs visible. Do **not** exclude `tasks/` — tasks are real nodes and excluding them hides half your graph.
- **Graph filter (graph-only).** In the graph view's **Filters** panel, type `-path:meta -path:raw`. Only the graph is affected — search and link suggestions still see the machinery.

Both settings are vault config (`.obsidian/app.json` and `.obsidian/graph.json`), and the included `.gitignore` versions vault config while excluding only local UI state (`workspace.json`) — so configure either once, commit, and every clone of the PMS inherits it.

Two graph notes: links inside frontmatter render in the core graph as plain, unlabeled lines — so your typed edges do appear natively; for *labeled* edges (seeing `part_of` vs `uses` on the line), use the Graph Link Types or Juggl plugins (table above). And if the graph ever looks too sparse, remember prose `[[wikilinks]]` also draw lines — only the frontmatter fields are the real typed graph.

## Later — point Claude Code at the same folder for Git

Both tools can share this folder safely: each keeps its session state in its own place, and the canonical knowledge is the files. **One rule: don't run both on the folder at the exact same time.**

1. Open this folder in Claude Code (or a terminal).
2. Start version control. **No-code:** open the folder in **GitHub Desktop** → *Create repository* → commit. **Terminal:** `git init && git add -A && git commit -m "initial PMS"`.
3. The included `.gitignore` keeps tool scratch and local overrides out of history.
4. Use Claude Code for occasional heavy jobs — bulk ingest, a full re-lint, git commits — while Cowork stays your day-to-day chat curator. Claude Code reads the same `CLAUDE.md`, which routes it to the same `meta/skills/` procedures.

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

## Two things to know going in

- **This is not local.** Running on Claude sends the *contents* of your notes to Anthropic, and your tasks (titles and short context) live in Todoist. Your *files* stay on your disk. For a true air-gap, use a local-model GraphRAG tool instead.
- **It has a ceiling.** Comfortable to ~150–200 knowledge pages; past that, add an external indexed store. Tasks are cheaper, but archive the terminal ones. `CLAUDE.md` explains the design in full.
