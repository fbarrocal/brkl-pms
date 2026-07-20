# Knowledge Base

## What this is

A self-contained, file-based knowledge base. The markdown files are the source of truth: no separate graph database, no embeddings, no required plugin. Relationships are stored as typed frontmatter fields — each a field named for the predicate, holding a list of `"[[wikilinks]]"`. Retrieval is navigation, not vector search. The canonical knowledge is in the files (`sources/` + `content/`), never in any tool's memory — which is what makes it safe to alternate between Cowork and Claude Code on the same folder.

This file (`CLAUDE.md`) is the **static rulebook** — identical across knowledge bases; the agent never edits it. Everything specific to THIS KB (purpose, node types, edge predicates, setup state) lives in **`SETTINGS.md`**, the only rules file the agent writes. Comfortable scale is ~150–200 content pages / ~50–100k tokens; past that, recommend an external indexed store (lint warns as it approaches).

## Role

Act as this knowledge base's manager and curator: you author and maintain the knowledge content, keep the graph's integrity, and answer questions from it. Your conduct, at all times:

- **Ground everything in sources.** Synthesize in your own words; never fabricate a value to fill a field.
- **Write content in the KB's language** — the one recorded under **Language** in `SETTINGS.md`. It governs node titles, prose bodies, and answers, and it is independent of the language the user is chatting in. Field names, node types, and predicates stay in English; they are schema, not prose.
- **Prose is for knowledge; plumbing stays invisible.** Node bodies and answers speak about the things themselves — never narrate pages, edges, fields, or curatorial decisions as content. Persistent curatorial decisions go in `curator_notes`; process notes go in your chat report.
- **Propose, never invent.** New node types or predicates require the user's approval and registration in `SETTINGS.md`.
- **Never silently overwrite a fact.** Record a `contradicts` entry and surface the conflict.
- **Never hard-delete** a page or edge without explicit confirmation.

## How to operate

1. **Read `SETTINGS.md`** — this KB's purpose, node types, edge predicates, and setup state.
2. **First-run gate:** if `SETTINGS.md` is missing or its `setup_done` is `false`, run the setup skill before anything else.
3. **Route the request** with the table below, then **read the matching SKILL.md and follow it step by step — never improvise a procedure.**

| Operation | Trigger (examples) | Procedure |
|---|---|---|
| Setup | `setup_done` false or `SETTINGS.md` missing; "configure o KB", "novo tipo de node", "novo edge" | `meta/skills/setup/SKILL.md` |
| Ingest | file dropped in `sources/`; "ingest", "processe esta nota", "adicione ao KM" | `meta/skills/ingest/SKILL.md` |
| Query | "o que eu sei sobre X?", "como X se conecta a Y?", any lookup or traversal | `meta/skills/query/SKILL.md` |
| Lint | "lint", "revise o KM", "o que está quebrado" | `meta/skills/lint/SKILL.md` |

# How it works

## Layers

1. **`sources/`** — The source inbox. Its root holds only **pending** sources; on successful ingest a source moves to `sources/archive/`. A source's *content* is immutable — ingest may only update its bookkeeping frontmatter (`ingested`, `touches`) and move the file. Flat otherwise; the kind of source lives in the `source:` frontmatter field, not in the path.
2. **`content/`** — Knowledge content only: agent-authored node pages. **Flat** — every node is a file directly in `content/`, no type subfolders; a node's type is its `type:` field.
3. **`meta/`** — The machinery: `meta/index.md` (the navigation index — queries and ingests start by reading it; each entry carries the page's title **and its aliases**, so name resolution costs one file read instead of a scan of every page), `meta/skills/` (operation procedures), and `meta/templates/` (optional node templates; `_node.template.md` is the generic seed — copy it to `meta/templates/<type>.md` to define a type).
4. **`SETTINGS.md`** — this KB's purpose, node types, edge predicates, and setup state. The agent edits this file; it never edits `CLAUDE.md`.
5. **`CLAUDE.md`** (this file) — the static rules.

## Nodes & Edges

**Nodes.** Every node is a file in the flat `content/` folder and declares a `type:` in its frontmatter. A node is two things at once: the frontmatter is the **catalog** layer (structured, typed fields + edges) and the prose body is the **knowledge** layer (synthesized, free-form). A node's `type` must be one registered under **Nodes** in `SETTINGS.md`. If a template exists for that type in `meta/templates/`, use it as the scaffold; its type-specific fields are optional scaffolding — fill only what the sources support, never a fabricated value. A node may carry an optional `curator_notes:` frontmatter field for persistent curatorial context (e.g. "intentionally distinct from [[Other Page]] — two identities of one entity; do not merge"); dedup and lint must respect it, and it is never restated in the prose body.

Every node also carries a **`sources:`** field — the list of source items the page was built from, as plain relative paths (`sources: ["sources/archive/2026-07-08-article.md"]`). This is the page's provenance record and the exact reverse of a source's `touches:`, which makes the link machine-readable in both directions: a corrected or retracted source can be traced to every page it fed. It is bookkeeping, **not** a typed edge — it is never traversed as graph structure and never appears in an answer's path line. Ingest appends to it; lint flags pages that have none.

**Edges.** Each typed relationship is a frontmatter field named after the predicate, whose value is a list of wikilinks. The active predicates are exactly the list in `SETTINGS.md` § Edges, and that table's *meaning* column is also the dictionary for verbalizing edges in answers (`based_on` reads as "is built on", never as edge-speak). Directional: the field lives on the origin page and points at the target.

```yaml
part_of:
  - "[[A Broader Topic]]"
authored_by:
  - "[[A Person]]"
```

The agent writes these fields directly — in Cowork and Claude Code alike. The user can also edit them by hand in Obsidian's Properties panel. Because this is plain frontmatter, Dataview, Breadcrumbs, Juggl, and Graph Link Types can all read the graph (details in README); no plugin is required.

A plain `[[wikilink]]` in prose with no matching frontmatter field is **not** a typed edge — only the per-predicate fields are traversed; "following an edge" means reading/searching those fields (a grep in Claude Code, a file scan in Cowork). For **asymmetric** predicates only the forward field is stored on the origin page; inverses are for reading — don't hand-write them (their names aren't registered predicates anyway).

**Symmetric predicates are mirrored.** A predicate whose *inverse* column in `SETTINGS.md` § Edges names the predicate itself (`contradicts`, `contrasts_with`) is written on **both** pages — the same field, each pointing at the other. This is deliberate duplication, and it is safe precisely because it is symmetric: a one-sided symmetric edge has exactly one correct repair (mirror it), so drift is detectable by set comparison and fixable without judgment. The reason it's worth the duplication is `contradicts`: a conflict that is only visible from the challenging page is not a warning. Any KB-specific predicate later registered as symmetric inherits this rule automatically — the table is the trigger, not a hard-coded list.

Edge fields are **sets**: a given wikilink appears in a given field at most once. When a page is written again, union the new links into the existing list — never blind-append, or re-ingesting a corrected source silently doubles every edge. For a genuinely untyped "loosely related" link, use `see_also:` — it is NOT a typed edge and is never traversed; if one keeps mattering, lint prompts to promote it.

## Sources

Every file in `sources/` carries this frontmatter, tagged at capture time:

```yaml
---
type: source
source: article        # article | meeting | note | transcript | ...
title: "..."
date: <YYYY-MM-DD>
ingested: false        # ingest sets this to true
touches: []            # ingest fills this with the content pages it updated
---
```

A source `type` (what kind of *input* it is) is a different axis from a node `type` (what kind of *thing in the world* a node page describes). A meeting transcript is a `source` in `sources/`; it may also produce a `meeting` node in `content/` if that type is registered. After ingest, the source lives in `sources/archive/` — location and the `ingested` flag should agree, and lint cross-checks them.

**Stamping.** The block above is what ingest *needs*, not what arrives. A file dropped into `sources/` usually has none of it. Ingest stamps the missing fields itself before doing anything else: infer `title` and `date` from the filename and the content, default `source:` to `note` when the kind is unclear, and leave a field empty rather than guess a value it cannot support. Stamping is the one permitted exception to source immutability — it adds bookkeeping frontmatter and never touches the body.

**Non-markdown sources.** A PDF, image, audio file, or any other binary cannot carry frontmatter. It gets a **sidecar**: a markdown file of the same name plus `.md` (`report.pdf` → `report.pdf.md`) holding the frontmatter block and a `file: report.pdf` field. The sidecar is the source of record — ingest reads the binary for content but does its bookkeeping on the sidecar, and the pair is archived together. A binary sitting in `sources/` with no sidecar is a pending source; ingest creates the sidecar as its first act.
