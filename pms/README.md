# Personal Management System template

**v2.1.0** — a generic, self-contained skeleton for a **Personal Management System**: a knowledge graph with a task layer, for anything you need to both understand and act on — personal notes, a research topic, a book, a project, a work stream. Your markdown files are the source of truth; the agent (Cowork or Claude Code) is curator, query engine, and task tracker. No database, no embeddings, no required plugin. It starts empty and configures itself to your purpose on the first message.

Two things go in — material you want understood, and things you need to do — and both end up as typed, cross-referenced nodes in one graph.

## Quick start (Cowork)

**Project description — paste this when creating the project:**

> This project is a Personal Management System: a self-curated knowledge graph with a task layer. Sources go in, typed and cross-referenced knowledge comes out, tasks are captured alongside it, and questions are answered from all of it. `CLAUDE.md` in this folder is the operating manual — follow it for every request; it defines the curator's role and conduct and routes every operation (setup, capture, ingest, query, lint) to its procedure under `meta/skills/`. This PMS's vocabulary lives in `meta/GRAPH_SCHEMA.md` and its configuration in `meta/SETTINGS.md`.

Then:

1. **Rename & place this folder** to your PMS's name (e.g. `My-PMS`, `Work`, `Book-Notes`) and put it where you keep your files.
2. **Enable file operations.** Claude Desktop → Settings → Capabilities → turn on **Code execution and file creation**.
3. **Create the project starting FROM this folder.** Cowork tab → Projects → **New project → "Use an existing folder"** → select this folder. Start from the folder — don't create an empty project and try to attach the folder afterwards. Paste the blurb above into the project description/instructions. Keep **Memory on**.
4. **Send your first message.** Because `setup_done` is `false`, the agent runs the setup skill: a short structured interview — purpose, node types, edges, language — whose answers it writes into `meta/SETTINGS.md` and `meta/GRAPH_SCHEMA.md`. **One exception:** if your first message is a task ("remind me to call Ana"), it captures the task first and offers setup after. You should never have to sit through an interview to write down one thing you need to do.
5. **Then just use it.** Drop material in `raw/` and ask to ingest. Say "remind me to…" and it becomes a task. Ask questions of either.
6. **(Optional) Automate upkeep.** Add a scheduled task to the project: *"toda segunda, rode o lint rápido (Pass A) e liste as fontes pendentes em raw/ e as tasks abertas."* Schedule the quick pass only — the deeper ones are expensive and worth asking for deliberately.

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
    ├── SETTINGS.md          # this PMS's purpose, language, conventions, setup state
    ├── skills/              # setup / capture / ingest / query / lint — single source of truth
    └── templates/
        ├── _node.template.md   # generic seed — copy to meta/templates/<type>.md
        └── _task.template.md   # the fixed task shape — never copied, never customized
```

The split that matters: `CLAUDE.md` is static and identical across every PMS you build from it — the agent never edits it, and never writes outside this folder at all. Everything specific to THIS PMS lives in exactly two files, both under `meta/`: `GRAPH_SCHEMA.md` (what may exist) and `SETTINGS.md` (what this PMS is). Knowledge and work (`raw/`, `knowledge/`, `tasks/`) are yours; machinery (`meta/`) is the system's. To upgrade the rulebook across many systems later, copy one file.

## How it works

- **Curator + graph + tracker in one.** The agent reads pending items in `raw/` and writes synthesized node pages into `knowledge/`, connecting them with **typed edges**. Things you need to do become task nodes in `tasks/`, connected by the same edges.
- **Nodes are typed.** Every page in the flat `knowledge/` folder has a `type:` (e.g. `entity`, `concept`, or a PMS-specific type like `person` or `character`). The frontmatter is the structured catalog layer; the prose body is the knowledge layer — both at once.
- **`tasks/` is part of the graph, not a sidecar.** The folder split is about lifecycle — tasks complete, knowledge accretes — but a task carries the same typed edges and is traversed with the same scan. That's what makes "what's blocking Project X?" answerable: the tasks point at the project, and the query looks in both folders.
- **Tasks reuse the same predicate vocabulary.** A subtask is `part_of`; a blocked task `depends_on`; a task's subject is `about`; an extracted action item is `introduced_by` its source. No task-specific predicates ship, and most PMS installs never need one.
- **Capture is deliberately cheap.** Say "remind me to email Ana about Acme" and you get one file, one index line, one confirmation. It resolves links only against names already in the index — it will never invent an empty `[[Acme]]` page just because you mentioned it. Unrecognized mentions stay plain links, and lint offers to promote the ones that keep recurring.
- **Nothing is deleted.** A cancelled task is `status: dropped` with a reason, not a missing file. The record of deciding *not* to do something is worth keeping. Finished tasks get a `closed` date and, after a while, move to `tasks/archive/` — where they keep every edge but drop out of the index, so the index stays small enough to stay cheap.
- **Provenance runs both ways.** Each node carries a `sources:` field listing the source items it was built from, and each source carries `touches:` listing the pages and tasks it fed. Lint checks the round-trip, so a page nothing supports is visible rather than plausible.
- **Drop anything in `raw/`.** Files don't need to arrive tagged — ingest stamps the bookkeeping frontmatter it needs. Binaries (PDFs, images, audio) get a small `.md` sidecar that carries that frontmatter for them. Ingest also pulls action items out of meeting notes and transcripts, handing them to capture.
- **Edges are typed frontmatter fields** — a relationship is a frontmatter field named for the predicate, holding wikilinks (e.g. `part_of: ["[[A Larger Thing]]"]`, `contradicts: ["[[A Rival Claim]]"]`). Because it's plain frontmatter, the whole Obsidian metadata ecosystem can read the graph — no plugin required (see **How to read the content**).
- **Retrieval is navigation, not vector search.** The agent reads `meta/GRAPH_INDEX.md` and traverses typed edges — no embeddings.

## The five operations

| You say | It runs |
|---|---|
| "remind me to…", "add a task", "to do" | **capture** — one task file, linked to what it already knows |
| drop a file in `raw/`, "ingest this" | **ingest** — nodes, edges, and any action items it finds |
| "what do I know about X", "what's blocking X", "what's open" | **query** — lookup, traversal, or task triage |
| "add a node type", "novo edge" | **setup** — the only skill that edits the schema |
| "lint", "what's broken" | **lint** — 18 health checks in three cost tiers, proposes but never applies unasked |

Each operation is owned by exactly one skill, and skills call each other rather than duplicating work: ingest calls capture for action items, lint routes its fixes back through the skill that owns them.

## How to read the content

Everything is plain markdown, so any editor works. `meta/GRAPH_INDEX.md` is the reading entry point, and because the edges are plain frontmatter, these tools consume the typed graph directly:

| Tool | Reads the typed edges via |
|---|---|
| Obsidian core graph | frontmatter links render natively (plain, unlabeled lines) |
| Dataview | frontmatter fields directly (`file.part_of`, `file.uses`, …) |
| Graph Link Types | Dataview metadata — draws each predicate as a label on the graph edge |
| Breadcrumbs | frontmatter fields you map as relation types in its settings |
| Juggl | Dataview metadata |

Dataview is also the easiest way to get a live task board without leaving Obsidian — `TABLE status, due FROM "tasks" WHERE status != "done"` gives you the same view the query skill produces in chat.

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

## Upgrading an existing PMS from v2.0.0

v2.1.0 fixes two v2.0.0 defects: task ids could be reissued after archiving, and links to tasks did not resolve in Obsidian. Two edits:

1. **Add the counter.** In `meta/GRAPH_INDEX.md` frontmatter, add `next_task_id:` set to the highest id in `tasks/` and `tasks/archive/`, plus one.
2. **Rewrite task links to piped form.** Every link to a task — in the index's `## Tasks` lines and in any edge field — becomes `[[<file-stem>|<Title>]]`. Then copy in the new `CLAUDE.md`, `meta/skills/`, and both templates, and run a full lint (Pass B); #5 reports any bare task link you missed.

## Upgrading an existing PMS from v1.x

v2.0.0 renames folders and splits the settings file, so an existing PMS needs a migration pass. It is mechanical, but do it in one sitting — a half-migrated PMS has the agent reading paths that no longer exist.

1. **Rename the folders.** `sources/` → `raw/`, `content/` → `knowledge/`. Create empty `tasks/`.
2. **Rewrite provenance paths.** Every knowledge page's `sources:` entries still say `sources/archive/…`; they must say `raw/archive/…`. Find-and-replace across `knowledge/` handles it. This is the one step that silently breaks lint's round-trip check if skipped.
3. **Split the settings file.** Move `SETTINGS.md` to `meta/SETTINGS.md`, keeping Purpose and Language; move its **Nodes** and **Edges** sections into the new `meta/GRAPH_SCHEMA.md`, and add the **Tasks** section from this template.
4. **Rename the index.** `meta/index.md` → `meta/GRAPH_INDEX.md`, and add a `## Tasks` section. Nothing goes in it yet — v1 had no tasks.
5. **Copy in the new machinery.** `CLAUDE.md`, all of `meta/skills/`, and `meta/templates/_task.template.md` from this template. Add `next_task_id: T-0001` to the index frontmatter.
   - **Check filenames.** v2.1+ requires each knowledge page's filename to be its title. Rename any that differ, or their links will not resolve.
6. **Drop the host-embed pieces.** Delete `meta/host-snippet.md`. If a host project's `CLAUDE.md` carries a `kb-host-snippet` block, remove it by hand — v2 systems are top-level and no skill writes outside the PMS folder anymore.
7. **Run a full lint (Pass B).** It will find whatever step 2 missed — the broken provenance round-trips only show up in the pass that resolves edges across files.

## Two things to know going in

- **This is not local.** Running on Claude sends the *contents* of your notes to Anthropic. Your *files* stay on your disk. For a true air-gap, use a local-model GraphRAG tool instead.
- **It has a ceiling.** Comfortable to ~150–200 knowledge pages; past that, add an external indexed store. Tasks are cheaper, but archive the terminal ones. `CLAUDE.md` explains the design in full.
