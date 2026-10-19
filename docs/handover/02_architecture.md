# 02 — Architecture (v1.0.1)

## Folder layout

```
<kb-root>/                 # renamed to the KB's name at setup; this becomes the Obsidian vault name
├── README.md              # human onboarding (Cowork + Claude Code); "how to read the content"
├── CLAUDE.md              # STATIC rulebook — identical across all KBs; the agent never edits it
├── SETTINGS.md            # per-KB: purpose, node types, edge predicates, setup_done state (agent edits this)
├── .gitignore             # versions vault/tool config; ignores tool scratch + local UI state
├── sources/               # inbox — root = pending only; ingest archives processed files to sources/archive/
├── content/               # flat; all node pages; a node's type is its `type:` field (no type subfolders)
└── meta/                  # the machinery (visible on purpose, so Cowork finds it & Obsidian can exclude it)
    ├── index.md           # navigation entry point; queries & ingests start here
    ├── skills/            # setup / ingest / query / lint — each a SKILL.md, single source of truth
    └── templates/         # optional node templates; _node.template.md is the generic seed
```

## The three content layers

1. **`sources/` (input, immutable body).** Files carry `type: source`, a `source:` kind (`article|meeting|note|…`), `ingested:` and `touches:` bookkeeping. Root holds *pending* only; ingest moves processed files to `sources/archive/`. A source's **body** is immutable — ingest may change only bookkeeping frontmatter and location.
2. **`content/` (output, the knowledge graph).** Flat folder of node pages. Each node = **catalog layer** (typed frontmatter: `type`, fields, edges, optional `curator_notes`, `see_also`) + **knowledge layer** (synthesised prose body). A node is both at once.
3. **`meta/` (machinery).** Index + skills + templates. Kept separate so `content/` is pure knowledge.

## Nodes

- Every node file declares `type:`; the type must be registered under **Nodes** in `SETTINGS.md`.
- Ships with two generic types: **`entity`** (a specific thing) and **`concept`** (an idea/theme). Setup adds KB-specific types (e.g. `person`, `character`, `formula`).
- **Templates are optional.** A node can exist with just `type` + prose. A template (`meta/templates/<type>.md`) is a scaffold; its type-specific fields are *optional* — the agent fills only what sources support and **never fabricates a value to fill a field**.
- **`curator_notes:`** — an optional frontmatter field for persistent curatorial decisions (e.g. "intentionally distinct from [[X]] — two identities of one entity; do not merge"). Machine-readable, respected by dedup and lint, **never restated in prose**.

## Edges (the graph)

- Each typed relationship is a **frontmatter field named for the predicate**, holding a list of `"[[wikilinks]]"`. Directional: the field lives on the **origin** page and points at the target.
- Example: `part_of: ["[[A Broader Topic]]"]`, `authored_by: ["[[A Person]]"]`.
- The active predicate set is exactly the table in **`SETTINGS.md` § Edges**. Its *meaning* column doubles as the **verbalisation dictionary** for query answers (`based_on` → "is built on").
- Ships with a 14-predicate general-purpose core: `is_a, part_of, based_on, authored_by, uses, depends_on, introduced_by, about, supports, contradicts, contrasts_with, precedes, member_of, located_in`. Only the forward field is stored; inverses are for reading.
- A plain prose `[[wikilink]]` with no matching frontmatter field is **not** a typed edge. `see_also:` is an explicit untyped escape valve — never traversed.
- Because edges are plain frontmatter, the graph is readable by Obsidian core graph (unlabeled lines), Dataview, Graph Link Types (labelled), Breadcrumbs, and Juggl — with no plugin required by the template.

## The static/mutable split (the load-bearing idea)

- **`CLAUDE.md` is static** — byte-identical across every KB. It carries: What this is, Role (conduct rules), How to operate (read SETTINGS → first-run gate → route to skill), and How it works (Layers, Nodes & Edges, Sources).
- **`SETTINGS.md` is the only file the agent writes as "rules"** — Purpose, Nodes, Edges, and `setup_done` (frontmatter flag).
- Consequences: (a) the agent can never corrupt its own rulebook while configuring a KB; (b) you can **upgrade every KB's rulebook by copying one file**; (c) all per-KB state lives in one auditable place.

## Operations (skills)

| Skill | Trigger | What it does |
|---|---|---|
| **setup** | first run (`setup_done` false / `SETTINGS.md` missing), or schema-change requests | Mode 1: interview (purpose, node types, edges) via AskUserQuestion (fallback to chat), write to `SETTINGS.md`, set `setup_done: true`. Mode 2: add/amend types & predicates on approval. |
| **ingest** | file in `sources/`; "ingest / processe esta nota" | Read pending source → extract nodes+edges → dedup → write/update content pages (prose + typed fields) → flag contradictions → mark `ingested`, fill `touches`, move to `sources/archive/` → update index. Type/predicate gaps route to setup Mode 2. |
| **query** | "what do I know about X?", "how does X connect to Y?" | Mode A lookup / Mode B multi-hop traversal. Answers in **natural prose** (edges verbalised); Mode B closes with one compact `Path:` audit line. Never narrates pages/edges as the answer; never fabricates edges. |
| **lint** | "lint / revise o KM" | 10 checks: unregistered/missing types, settings drift, invalid predicates, untyped links to promote, dangling edges, orphan pages, contradictions, inbox state (flag vs location), index drift, scale watch. Reports & proposes; never hard-deletes without sign-off. |

Each skill starts with a single line — `Prerequisite: CLAUDE.md — operate by it` — and does not repeat the rules (they're reached only through `CLAUDE.md`'s routing).

## The setup gate (first-run flow)

`SETTINGS.md` ships with `setup_done: false`. On the first interaction, `CLAUDE.md` § How to operate directs the agent to run the **setup** skill before anything else: it interviews the user about the KB's purpose, proposes node types and edge predicates fitting that purpose, writes them into `SETTINGS.md`, and flips `setup_done: true`. Only then does normal operation (ingest/query/lint) begin.
