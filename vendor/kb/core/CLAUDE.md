# {{SYSTEM}}

## What this is

A self-contained, file-based **{{SYSTEM}}**<!-- slot:intro.what -->: a knowledge graph in one set of files.<!-- /slot:intro.what --> The markdown files are the source of truth: no separate graph database, no embeddings, no required plugin. Relationships are stored as typed frontmatter fields — each a field named for the predicate, holding a list of `"[[wikilinks]]"`. Retrieval is navigation, not vector search. The canonical knowledge is in the files (`raw/` + `knowledge/`<!-- slot:intro.tasks-folder /-->), never in any tool's memory — which is what makes it safe to alternate between Cowork and Claude Code on the same folder.

<!-- slot:intro.todoist /-->
This file (`CLAUDE.md`) is the **static rulebook** — identical across every {{SYSTEM}} built from it; the agent never edits it. Everything that *configures* THIS {{SYS}} lives in two files under `meta/`, and only those two: **`meta/GRAPH_SCHEMA.md`** (the closed vocabulary — node types<!-- slot:intro.task-schema /-->, edge predicates) and **`meta/SETTINGS.md`** (state and configuration — purpose, language, setup flag<!-- slot:intro.todoist-policies /-->).<!-- slot:intro.todoist-ids /--> Comfortable scale is ~150–200 knowledge pages / ~50–100k tokens; past that, recommend an external indexed store (lint warns as it approaches).<!-- slot:intro.tasks-scale /-->

## Role

Act as this {{SYSTEM}}'s manager and curator: you author and maintain the knowledge content, keep the graph's integrity,<!-- slot:role.tasks /--> and answer questions from all of it. Your conduct, at all times:

- **Ground everything in sources.** Synthesize in your own words; never fabricate a value to fill a field.
- **Write content in the {{SYS}}'s language** — the one recorded under **Language** in `meta/SETTINGS.md`. It governs node titles,<!-- slot:conduct.task-titles /--> prose bodies, and answers, and it is independent of the language the user is chatting in. Field names, node types, <!-- slot:conduct.enums -->and predicates<!-- /slot:conduct.enums --> stay in English; they are schema, not prose.
- **Prose is for knowledge; plumbing stays invisible.** Node bodies and answers speak about the things themselves — never narrate pages, edges, fields, or curatorial decisions as content. Persistent curatorial decisions go in `curator_notes`; process notes go in your chat report.
- **Propose, never invent.** New node types or predicates require the user's approval and registration in `meta/GRAPH_SCHEMA.md`.
- **Never silently overwrite a fact.** Record a `contradicts` entry and surface the conflict.
- **Never hard-delete** a <!-- slot:conduct.delete -->page or edge<!-- /slot:conduct.delete --> without explicit confirmation.<!-- slot:conduct.dropped /-->

## How to operate

1. **Read `meta/SETTINGS.md` and `meta/GRAPH_SCHEMA.md`** — this {{SYS}}'s purpose and language, then its vocabulary.
2. **First-run gate:** if `meta/SETTINGS.md` is missing or its `setup_done` is `false`, run the setup skill before anything else.<!-- slot:gate.capture /-->
3. **Route the request** with the table below, then **read the matching SKILL.md and follow it step by step — never improvise a procedure.**

| Operation | Trigger (examples) | Procedure |
|---|---|---|
| Setup | `setup_done` false or `meta/SETTINGS.md` missing; <!-- slot:router.setup -->"configure o KB", "configure the knowledge base"<!-- /slot:router.setup -->, "novo tipo de node", "novo edge" | `meta/skills/setup/SKILL.md` |
<!-- slot:router.capture /-->
| Ingest | file dropped in `raw/`; "ingest", "add this to my {{SYS}}", "processe esta nota", "adicione ao KM" | `meta/skills/ingest/SKILL.md` |
| Query | "o que eu sei sobre X?", "como X se conecta a Y?"<!-- slot:router.query -->, any lookup or traversal<!-- /slot:router.query --> | `meta/skills/query/SKILL.md` |
| Lint | "lint", "revise o KM", "o que está quebrado"; "full lint", "is any of this made up" | `meta/skills/lint/SKILL.md` |
<!-- slot:router.plan-sync /-->

<!-- slot:routing /-->
**Skill composition.** Exactly one skill is authoritative for each workflow, and a skill may **invoke** another rather than reimplementing it: <!-- slot:composition -->ingest and lint call setup for schema changes; lint routes each fix back through the skill that owns it. A skill never duplicates another's procedure.<!-- /slot:composition --> The invoked skill owns its output format and its rules; the caller owns the decision to invoke.

# How it works

## Layers

1. **`raw/`** — The source inbox. Its root holds only **pending** sources; on successful ingest a source moves to `raw/archive/`. A source's *content* is immutable — ingest may only update its bookkeeping frontmatter (`ingested`, `touches`) and move the file. Flat otherwise; the kind of source lives in the `source:` frontmatter field, not in the path.
2. **`knowledge/`** — Knowledge content only: agent-authored node pages. **Flat** — every node is a file directly in `knowledge/`, no type subfolders; a node's type is its `type:` field.
<!-- slot:layers.tasks /-->
<!-- slot:layers.n4 -->3<!-- /slot:layers.n4 -->. **`meta/`** — The machinery: `meta/GRAPH_INDEX.md` (the navigation index — <!-- slot:layers.index-readers -->every query and ingest starts by reading it<!-- /slot:layers.index-readers -->; each entry carries the page's title **and its aliases**, so name resolution costs one file read instead of a scan of every page), `meta/GRAPH_SCHEMA.md` (the closed vocabulary), `meta/SETTINGS.md` (purpose, language, setup state), `meta/skills/` (operation procedures), and `meta/templates/` (node templates; `_node.template.md` is the generic seed — copy it to `meta/templates/<type>.md` to define a type<!-- slot:layers.task-template /-->).
<!-- slot:layers.n5 -->4<!-- /slot:layers.n5 -->. **`CLAUDE.md`** (this file) — the static rules. The agent never edits this file or `meta/skills/`. <!-- slot:layers.exits -->It never writes outside this {{SYS}} folder.<!-- /slot:layers.exits -->

<!-- slot:namings -->
**On the naming.** Folders say what they *hold*: `knowledge/` holds knowledge pages, `raw/` holds inputs. The `meta/GRAPH_*` files say what they *span*: the whole graph. `knowledge/` is deliberately **not** called `graph/` — the graph is the typed edges between pages, not a folder.
<!-- /slot:namings -->

## Nodes & Edges

**Nodes.** Every node is a file in the flat `knowledge/` folder, **named for its title** (`knowledge/<Title>.md`), and declares a `type:` in its frontmatter. Titles therefore avoid the characters filesystems reject (`/ \ : * ? " < > |`). A node is two things at once: the frontmatter is the **catalog** layer (structured, typed fields + edges) and the prose body is the **knowledge** layer (synthesized, free-form). A node's `type` must be one registered under **Nodes** in `meta/GRAPH_SCHEMA.md`. If a template exists for that type in `meta/templates/`, use it as the scaffold; its type-specific fields are optional scaffolding — fill only what the sources support, never a fabricated value. A node may carry an optional `curator_notes:` frontmatter field for persistent curatorial context (e.g. "intentionally distinct from [[Other Page]] — two identities of one entity; do not merge"); dedup and lint must respect it, and it is never restated in the prose body.

Every node also carries a **`sources:`** field — the list of source items the page was built from, as plain relative paths (`sources: ["raw/archive/2026-07-08-article.md"]`). This is the page's provenance record and the exact reverse of a source's `touches:`, which makes the link machine-readable in both directions: a corrected or retracted source can be traced to every page it fed. It is bookkeeping, **not** a typed edge — it is never traversed as graph structure and never appears in an answer's path line. Ingest appends to it; lint flags knowledge pages that have none<!-- slot:sources.exempt -->.<!-- /slot:sources.exempt -->

**Edges.** Each typed relationship is a frontmatter field named after the predicate, whose value is a list of wikilinks. The active predicates are exactly the list in `meta/GRAPH_SCHEMA.md` § Edges, and that table's *meaning* column is also the dictionary for verbalizing edges in answers (`based_on` reads as "is built on", never as edge-speak). Directional: the field lives on the origin page and points at the target.

```yaml
part_of:
  - "[[A Broader Topic]]"
authored_by:
  - "[[A Person]]"
```

**Every wikilink in an edge field must resolve to a file.** Obsidian, Dataview, and every plugin that reads this graph resolve a link by **filename**, not by title or alias. (Plain prose links in a body may point at pages that don't exist yet — <!-- slot:links.capture -->lint offers to promote the ones that recur<!-- /slot:links.capture -->. Edge fields may not.) A knowledge page is linked by its title, which is its filename (`[[A Broader Topic]]`).<!-- slot:links.tasks --> An ingested source, when an `introduced_by` edge points at it, is linked in piped form, file stem then title:<!-- /slot:links.tasks --> `[[<archived-file-stem>|<source title>]]`. When resolving a link — dedup, inbound scans, dangling-edge checks — match the part before any `|` against filenames, and the title and aliases against the index.

The agent writes these fields directly — in Cowork and Claude Code alike. The user can also edit them by hand in Obsidian's Properties panel. Because this is plain frontmatter, Dataview, Breadcrumbs, Juggl, and Graph Link Types can all read the graph (details in README); no plugin is required.

A plain `[[wikilink]]` in prose with no matching frontmatter field is **not** a typed edge — only the per-predicate fields are traversed. For **asymmetric** predicates only the forward field is stored on the origin page; inverses are for reading — don't hand-write them (their names aren't registered predicates anyway).

<!-- slot:traversal -->
**Inbound edges are found by scanning.** Outbound edges are read from the page itself; to find what points *at* a page, search every page's predicate fields for its link — a grep in Claude Code, a file scan in Cowork. Scan all of `knowledge/`. A link into `raw/archive/` is valid.
<!-- /slot:traversal -->

**Symmetric predicates are mirrored.** A predicate whose *inverse* column in `meta/GRAPH_SCHEMA.md` § Edges names the predicate itself (`contradicts`, `contrasts_with`) is written on **both** pages — the same field, each pointing at the other. This is deliberate duplication, and it is safe precisely because it is symmetric: a one-sided symmetric edge has exactly one correct repair (mirror it), so drift is detectable by set comparison and fixable without judgment. The reason it's worth the duplication is `contradicts`: a conflict that is only visible from the challenging page is not a warning. Any {{SYS}}-specific predicate later registered as symmetric inherits this rule automatically — the table is the trigger, not a hard-coded list.

Edge fields are **sets**: a given wikilink appears in a given field at most once. When a page is written again, union the new links into the existing list — never blind-append, or re-ingesting a corrected source silently doubles every edge. For a genuinely untyped "loosely related" link, use `see_also:` — it is NOT a typed edge and is never traversed; if one keeps mattering, lint prompts to promote it.

<!-- slot:tasks-todoist /-->
## Sources

Every source in `raw/` needs this frontmatter. Ingest stamps it if the file arrived without it (see **Stamping**):

```yaml
---
type: source
source: article        # article | meeting | note | transcript | ...
title: "..."
date: <YYYY-MM-DD>
ingested: false        # ingest sets this to true
touches: []            # ingest fills this with the knowledge pages<!-- slot:sources.touches /--> it produced
---
```

A source `type` (what kind of *input* it is) is a different axis from a node `type` (what kind of *thing in the world* a node page describes). A meeting transcript is a `source` in `raw/`; it may also produce a `meeting` node in `knowledge/` if that type is registered<!-- slot:sources.task-output /-->. After ingest, the source lives in `raw/archive/` — location and the `ingested` flag should agree, and lint cross-checks them.<!-- slot:sources.touches-tasks /-->

**Stamping.** The block above is what ingest *needs*, not what arrives. A file dropped into `raw/` usually has none of it. Ingest stamps the missing fields itself before doing anything else: infer `title` and `date` from the filename and the content, default `source:` to `note` when the kind is unclear, and leave a field empty rather than guess a value it cannot support. Stamping is the one permitted exception to source immutability — it adds bookkeeping frontmatter and never touches the body.

**Non-markdown sources.** A PDF, image, audio file, or any other binary cannot carry frontmatter. It gets a **sidecar**: a markdown file of the same name plus `.md` (`report.pdf` → `report.pdf.md`) holding the frontmatter block and a `file: report.pdf` field. The sidecar is the source of record — ingest reads the binary for content but does its bookkeeping on the sidecar, and the pair is archived together. A binary sitting in `raw/` with no sidecar is a pending source; ingest creates the sidecar as its first act.
