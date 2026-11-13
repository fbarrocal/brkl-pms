# {{SYSTEM}} template

<!-- slot:intro -->
**v{{VERSION}}** — a self-curated knowledge graph in plain markdown. Sources go in; typed, cross-referenced knowledge pages come out; questions are answered by navigating the graph, not by vector search.
<!-- /slot:intro -->

## Quick start (Cowork)

**Project description — paste this when creating the project:**

<!-- slot:blurb -->
> This project is a {{SYSTEM}}: a self-curated knowledge graph. Sources go in, typed and cross-referenced knowledge comes out, and questions are answered from it. `CLAUDE.md` in this folder is the operating manual — follow it for every request; it defines the curator's role and conduct and routes every operation (setup, ingest, query, lint) to its procedure under `meta/skills/`. This {{SYS}}'s vocabulary lives in `meta/GRAPH_SCHEMA.md` and its configuration in `meta/SETTINGS.md`.
<!-- /slot:blurb -->

Then:

1. **Rename & place this folder** to your {{SYS}}'s name (e.g. `My-{{SYS}}`, `Work`, `Book-Notes`) and put it where you keep your files.
2. **Enable file operations.** Claude Desktop → Settings → Capabilities → turn on **Code execution and file creation**.
3. **Create the project starting FROM this folder.** Cowork tab → Projects → **New project → "Use an existing folder"** → select this folder. Start from the folder — don't create an empty project and try to attach the folder afterwards. Paste the blurb above into the project description/instructions. Keep **Memory on**.
4. **Send your first message.** Because `setup_done` is `false`, the agent runs the setup skill:
<!-- slot:first-message -->
   - **A short interview:** purpose, node types, edges, and the language the content is written in.
<!-- /slot:first-message -->
5. **Then just use it.** Drop material in `raw/` and ask to ingest.<!-- slot:use.tasks --> Ask it questions.<!-- /slot:use.tasks -->
<!-- slot:use.sync /-->

## Layout

```
your-{{sys}}-folder/
├── README.md                # this file — start here
├── CLAUDE.md                # static rulebook: role, conduct, how to operate, how it works
├── .gitignore               # for the later Claude Code + Git step
├── raw/                     # inbox — root holds pending only; ingest archives
│                            # processed files to raw/archive/
├── knowledge/               # node pages, flat; a node's type is a field, not a folder
<!-- slot:layout.tasks /-->
└── meta/                    # the machinery (visible on purpose)
    ├── GRAPH_INDEX.md       # navigation entry point<!-- slot:layout.index --> — every node, with its aliases<!-- /slot:layout.index -->
    ├── GRAPH_SCHEMA.md      # the closed vocabulary: node types<!-- slot:layout.schema /-->, edge predicates
    ├── SETTINGS.md          # this {{SYS}}'s purpose, language<!-- slot:layout.settings /-->, setup state
    ├── skills/              # <!-- slot:layout.skills -->setup / ingest / query / lint<!-- /slot:layout.skills --> — single source of truth
    └── templates/
        <!-- slot:layout.seed -->└── _node.template.md<!-- /slot:layout.seed -->   # generic seed — copy to meta/templates/<type>.md
<!-- slot:layout.pms-templates /-->
```

The split that matters: `CLAUDE.md` is static and identical across every {{SYS}} you build from it — the agent never edits it.<!-- slot:split.exits --> The agent never writes outside this folder.<!-- /slot:split.exits --> Everything that configures THIS {{SYS}} lives in exactly two files, both under `meta/`: `GRAPH_SCHEMA.md` (what may exist) and `SETTINGS.md` (what this {{SYS}} is). <!-- slot:split.yours -->Knowledge (`raw/`, `knowledge/`) is yours<!-- /slot:split.yours -->; machinery (`meta/`) is the system's. To upgrade the rulebook across many systems later, copy one file.

## How it works

- <!-- slot:how.title -->**Curator + graph in one.**<!-- /slot:how.title --> The agent reads pending items in `raw/` and writes synthesized node pages into `knowledge/`, connecting them with **typed edges**.<!-- slot:how.tasks /-->
- **Nodes are typed.** Every page in the flat `knowledge/` folder has a `type:` (e.g. `entity`, `concept`, or a {{SYS}}-specific type like `person` or `character`). The frontmatter is the structured catalog layer; the prose body is the knowledge layer — both at once.
<!-- slot:how.task-bullets /-->
- **Provenance runs both ways.** Each node carries a `sources:` field listing the source items it was built from, and each source carries `touches:` listing the pages<!-- slot:how.touches /--> it fed. Lint checks the round-trip, so a page nothing supports is visible rather than plausible.
- **Drop anything in `raw/`.** Files don't need to arrive tagged — ingest stamps the bookkeeping frontmatter it needs. Binaries (PDFs, images, audio) get a small `.md` sidecar that carries that frontmatter for them.<!-- slot:how.action-items /-->
- **Edges are typed frontmatter fields** — a relationship is a frontmatter field named for the predicate, holding wikilinks (e.g. `part_of: ["[[A Larger Thing]]"]`, `contradicts: ["[[A Rival Claim]]"]`). Because it's plain frontmatter, the whole Obsidian metadata ecosystem can read the graph — no plugin required (see **How to read the content**).
- **Retrieval is navigation, not vector search.** The agent reads `meta/GRAPH_INDEX.md` and traverses typed edges — no embeddings.

## The <!-- slot:ops.count -->four<!-- /slot:ops.count --> operations

| You say | It runs |
|---|---|
<!-- slot:ops.capture /-->
| drop a file in `raw/`, "ingest this" | **ingest** — <!-- slot:ops.ingest -->nodes and edges, with contradictions flagged<!-- /slot:ops.ingest --> |
| "what do I know about X"<!-- slot:ops.query-says -->, "how does X connect to Y"<!-- /slot:ops.query-says --> | **query** — <!-- slot:ops.query-does -->lookup or traversal<!-- /slot:ops.query-does --> |
| "add a node type", "novo edge"<!-- slot:ops.setup-says /--> | **setup** — the only skill that edits the schema<!-- slot:ops.setup-does /--> |
<!-- slot:ops.plan-sync /-->
| "lint", "what's broken" | **lint** — <!-- slot:ops.lint -->17 health checks in three cost tiers<!-- /slot:ops.lint -->; proposes but never applies unasked |

Each operation is owned by exactly one skill, and skills call each other rather than duplicating work: <!-- slot:ops.composition -->ingest and lint call setup for schema changes, and lint<!-- /slot:ops.composition --> routes its fixes back through the skill that owns them.

## How to read the content

Everything is plain markdown, so any editor works. `meta/GRAPH_INDEX.md` is the reading entry point, and because the edges are plain frontmatter, these tools consume the typed graph directly:

| Tool | Reads the typed edges via |
|---|---|
| Obsidian core graph | frontmatter links render natively (plain, unlabeled lines) |
| Dataview | frontmatter fields directly (`file.part_of`, `file.uses`, …) |
| Graph Link Types | Dataview metadata — draws each predicate as a label on the graph edge |
| Breadcrumbs | frontmatter fields you map as relation types in its settings |
| Juggl | Dataview metadata |

<!-- slot:read.task-board /-->
### Obsidian

**Open the vault at the {{SYS}}'s root folder, not at `knowledge/`.** The vault takes the folder's name — and since you renamed the folder to your {{SYS}}'s name at setup, each system gets a distinct vault name. Pointing Obsidian at `knowledge/` instead would name every vault "knowledge" and cut the vault off from `raw/`<!-- slot:obsidian.tasks /-->.

With the vault at the root, the machinery (`CLAUDE.md`, `meta/`, …) shows up in search and graph. Two ways to hide it:

- **Excluded files (recommended — hides machinery everywhere).** Settings → **Files and links → Excluded files** → add `meta/`, `raw/`, `CLAUDE.md`, `README.md`. This removes them from search, link suggestions, *and* the graph. Drop `raw/` from the list if you want raw inputs visible.<!-- slot:obsidian.exclude-tasks /-->
- **Graph filter (graph-only).** In the graph view's **Filters** panel, type `-path:meta -path:raw`. Only the graph is affected — search and link suggestions still see the machinery.

Both settings are vault config (`.obsidian/app.json` and `.obsidian/graph.json`), and the included `.gitignore` versions vault config while excluding only local UI state (`workspace.json`) — so configure either once, commit, and every clone of the {{SYS}} inherits it.

Two graph notes: links inside frontmatter render in the core graph as plain, unlabeled lines — so your typed edges do appear natively; for *labeled* edges (seeing `part_of` vs `uses` on the line), use the Graph Link Types or Juggl plugins (table above). And if the graph ever looks too sparse, remember prose `[[wikilinks]]` also draw lines — only the frontmatter fields are the real typed graph.

## Later — point Claude Code at the same folder for Git

Both tools can share this folder safely: each keeps its session state in its own place, and the canonical knowledge is the files. **One rule: don't run both on the folder at the exact same time.**

1. Open this folder in Claude Code (or a terminal).
2. Start version control. **No-code:** open the folder in **GitHub Desktop** → *Create repository* → commit. **Terminal:** `git init && git add -A && git commit -m "initial {{SYS}}"`.
3. The included `.gitignore` keeps tool scratch and local overrides out of history.
4. Use Claude Code for occasional heavy jobs — bulk ingest, a full re-lint, git commits — while Cowork stays your day-to-day chat curator. Claude Code reads the same `CLAUDE.md`, which routes it to the same `meta/skills/` procedures.

<!-- slot:todoist-upgrade -->
## Upgrading from v1.1.x

v1.2.0 is the same curator with a new layout and two more rounds of hardening: stamping and sidecars for raw files, links that always resolve to a file, and a three-pass lint. To move a v1.1.x knowledge base:

1. Rename `sources/` to `raw/` (processed sources go in `raw/archive/`) and `content/` to `knowledge/`, and fix the `sources:` and `touches:` paths that pointed into the old folders.
2. Move `meta/index.md` to `meta/GRAPH_INDEX.md`.
3. Split the root `SETTINGS.md`: **Purpose**, **Language** and the `setup_done` flag go to `meta/SETTINGS.md`; **Nodes** and **Edges** go to `meta/GRAPH_SCHEMA.md`.
4. Copy in this template's `CLAUDE.md`, all of `meta/skills/`, and `meta/templates/_node.template.md`. Embedded installs are gone: remove `meta/host-snippet.md` and the pointer block it put in the host's `CLAUDE.md`.
5. Say "full lint". It reports what the move left behind: links that no longer resolve, index drift, missing provenance.

<!-- /slot:todoist-upgrade -->
## Two things to know going in

- **This is not local.** Running on Claude sends the *contents* of your notes to Anthropic<!-- slot:local.todoist /-->. Your *files* stay on your disk. For a true air-gap, use a local-model GraphRAG tool instead.
- **It has a ceiling.** Comfortable to ~150–200 knowledge pages; past that, add an external indexed store.<!-- slot:ceiling.tasks /--> `CLAUDE.md` explains the design in full.
