# Knowledge Base template

A generic, self-contained skeleton for **any** knowledge base — personal notes, a research topic, a book, a project, anything. Your markdown files are the source of truth; the agent (Cowork or Claude Code) is both the curator and the query engine. No database, no embeddings, no required plugin. It starts empty and configures itself to your purpose on the first message.

## Quick start (Cowork)

**Project description — paste this when creating the project:**

> This project is a self-curated knowledge base: sources go in, typed and cross-referenced knowledge comes out, and questions are answered from it. `CLAUDE.md` in this folder is the operating manual — follow it for every request; it defines the curator's role and conduct and routes every operation (setup, ingest, query, lint) to its procedure under `meta/skills/`. This KB's own purpose, schema, and state live in `SETTINGS.md`.

Then:

1. **Rename & place this folder** to your KB's name (e.g. `My-KB`, `Book-Notes`) and put it where you keep your files.
2. **Enable file operations.** Claude Desktop → Settings → Capabilities → turn on **Code execution and file creation**.
3. **Create the project starting FROM this folder.** Cowork tab → Projects → **New project → "Use an existing folder"** → select this folder. Start from the folder — don't create an empty project and try to attach the folder afterwards. Paste the blurb above into the project description/instructions. Keep **Memory on**.
4. **Send your first message.** Because `setup_done` is `false`, the agent runs the setup skill: a short structured interview — purpose, node types, edges — whose answers it writes into `SETTINGS.md`. After that, normal use: drop sources in `sources/`, then ask to ingest, query, and lint.
5. **(Optional) Automate upkeep.** Add a scheduled task to the project: *"toda segunda, rode o lint e liste as fontes pendentes em sources/."*

## Layout

```
your-kb-folder/
├── README.md             # this file — start here
├── CLAUDE.md             # static rulebook: role, conduct, how to operate, how it works
├── SETTINGS.md           # this KB's purpose, node types, edge predicates, setup state
├── .gitignore            # for the later Claude Code + Git step
├── sources/              # inbox — root holds pending only; ingest archives
│                         # processed files to sources/archive/
├── content/              # knowledge only — all node pages, flat; type is a field
└── meta/                 # the machinery (visible on purpose)
    ├── index.md          # navigation entry point
    ├── skills/           # setup / ingest / query / lint — single source of truth
    └── templates/        # optional node templates
        └── _node.template.md  # generic seed — copy to meta/templates/<type>.md
```

The split that matters: `CLAUDE.md` is static and identical across all your knowledge bases — the agent never edits it. Everything specific to THIS KB lives in `SETTINGS.md`, the only rules file the agent writes. Knowledge (`sources/`, `content/`) is yours; machinery (`meta/`) is the system's. To upgrade the rulebook across many KBs later, copy one file.

## Later — point Claude Code at the same folder for Git

Both tools can share this folder safely: each keeps its session state in its own place, and the canonical knowledge is the files. **One rule: don't run both on the folder at the exact same time.**

1. Open this folder in Claude Code (or a terminal).
2. Start version control. **No-code:** open the folder in **GitHub Desktop** → *Create repository* → commit. **Terminal:** `git init && git add -A && git commit -m "initial KB"`.
3. The included `.gitignore` keeps tool scratch and local overrides out of history.
4. Use Claude Code for occasional heavy jobs — bulk ingest, a full re-lint, git commits — while Cowork stays your day-to-day chat curator. Claude Code reads the same `CLAUDE.md`, which routes it to the same `meta/skills/` procedures.

## How it works

- **Curator + graph in one.** The agent reads the pending items in `sources/` and writes synthesized node pages into `content/`, connecting them with **typed edges**.
- **Nodes are typed.** Every page in the flat `content/` folder has a `type:` (e.g. `entity`, `concept`, or a KB-specific type like `person` or `character`). The frontmatter is the structured catalog layer; the prose body is the knowledge layer — both at once.
- **Provenance runs both ways.** Each node carries a `sources:` field listing the source items it was built from, and each source carries `touches:` listing the pages it fed. Lint checks the round-trip, so a page nothing supports is visible rather than plausible.
- **Drop anything in `sources/`.** Files don't need to arrive tagged — ingest stamps the bookkeeping frontmatter it needs. Binaries (PDFs, images, audio) get a small `.md` sidecar that carries that frontmatter for them.
- **Templates are optional.** Define a template per node type in `meta/templates/` (starting from the generic seed) when a kind of thing recurs enough to deserve structure; skip it otherwise.
- **Edges are typed frontmatter fields** — a relationship is a frontmatter field named for the predicate, holding wikilinks (e.g. `part_of: ["[[A Larger Thing]]"]`, `contradicts: ["[[A Rival Claim]]"]`). Because it's plain frontmatter, the whole Obsidian metadata ecosystem can read the graph — no plugin required (see **How to read the content**).
- **Retrieval is navigation, not vector search.** The agent reads `meta/index.md` and traverses typed edges — no embeddings.

## How to read the content

Everything is plain markdown, so any editor works. `meta/index.md` is the reading entry point (nodes grouped by type), and because the edges are plain frontmatter, these tools consume the typed graph directly:

| Tool | Reads the typed edges via |
|---|---|
| Obsidian core graph | frontmatter links render natively (plain, unlabeled lines) |
| Dataview | frontmatter fields directly (`file.part_of`, `file.uses`, …) |
| Graph Link Types | Dataview metadata — draws each predicate as a label on the graph edge |
| Breadcrumbs | frontmatter fields you map as relation types in its settings |
| Juggl | Dataview metadata |

### Obsidian

**Open the vault at the KB's root folder, not at `content/`.** The vault takes the folder's name — and since you renamed the folder to your KB's name at setup, each KB gets a distinct vault name. Pointing Obsidian at `content/` instead would name every vault "content" and cut the vault off from `sources/`.

With the vault at the root, the machinery (`CLAUDE.md`, `meta/`, …) shows up in search and graph. Two ways to hide it:

- **Excluded files (recommended — hides machinery everywhere).** Settings → **Files and links → Excluded files** → add `meta/`, `sources/`, `CLAUDE.md`, `README.md`, `SETTINGS.md`. This removes them from search, link suggestions, *and* the graph. Drop `sources/` from the list if you want raw inputs visible.
- **Graph filter (graph-only).** In the graph view's **Filters** panel, type `path:content` (or `-path:meta`). Only the graph is affected — search and link suggestions still see the machinery.

Both settings are vault config (`.obsidian/app.json` and `.obsidian/graph.json`), and the included `.gitignore` versions vault config while excluding only local UI state (`workspace.json`) — so configure either once, commit, and every clone of the KB inherits it.

Two graph notes: links inside frontmatter render in the core graph as plain, unlabeled lines — so your typed edges do appear natively; for *labeled* edges (seeing `part_of` vs `uses` on the line), use the Graph Link Types or Juggl plugins (table above). And if the graph ever looks too sparse, remember prose `[[wikilinks]]` also draw lines — only the frontmatter fields are the real typed graph.

## If the agent doesn't pick up an operation

Both `CLAUDE.md` and the project blurb route the agent to `meta/skills/` by exact path. If it still ignores one, a heavier fallback is to copy the contents of `meta/skills/` into your global skills folder, which both tools read:

- **Windows:** `%USERPROFILE%\.claude\skills\`
- **macOS/Linux:** `~/.claude/skills/`

(If you do this, the global copies become a second location to keep in sync — and the generic skill names, e.g. `query`, share that global namespace with any other skills you have. Prefer fixing the routing first.)

## Two things to know going in

- **This is not local.** Running on Claude sends the *contents* of your notes to Anthropic. Your *files* stay on your disk. For a true air-gap, use a local-model GraphRAG tool instead.
- **It has a ceiling.** Comfortable to ~150–200 content pages; past that, add an external indexed store. `CLAUDE.md` explains the design in full.
