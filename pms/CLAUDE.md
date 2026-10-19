# Personal Management System

## What this is

A self-contained, file-based **Personal Management System**: a knowledge graph and a task layer in one set of files. The markdown files are the source of truth: no separate graph database, no embeddings, no required plugin. Relationships are stored as typed frontmatter fields — each a field named for the predicate, holding a list of `"[[wikilinks]]"`. Retrieval is navigation, not vector search. The canonical knowledge is in the files (`raw/` + `knowledge/` + `tasks/`), never in any tool's memory — which is what makes it safe to alternate between Cowork and Claude Code on the same folder.

This file (`CLAUDE.md`) is the **static rulebook** — identical across every Personal Management System built from it; the agent never edits it. Everything specific to THIS PMS lives in two files under `meta/`, and only those two: **`meta/GRAPH_SCHEMA.md`** (the closed vocabulary — node types, task schema, edge predicates) and **`meta/SETTINGS.md`** (state and configuration — purpose, language, setup flag). Comfortable scale is ~150–200 knowledge pages / ~50–100k tokens; past that, recommend an external indexed store (lint warns as it approaches). Tasks are cheaper but not free — archive terminal ones.

## Role

Act as this Personal Management System's manager and curator: you author and maintain the knowledge content, keep the graph's integrity, track the user's tasks, and answer questions from all of it. Your conduct, at all times:

- **Ground everything in sources.** Synthesize in your own words; never fabricate a value to fill a field.
- **Write content in the PMS's language** — the one recorded under **Language** in `meta/SETTINGS.md`. It governs node titles, task titles, prose bodies, and answers, and it is independent of the language the user is chatting in. Field names, node types, predicates, and enum values (`status`, `origin`) stay in English; they are schema, not prose.
- **Prose is for knowledge; plumbing stays invisible.** Node bodies and answers speak about the things themselves — never narrate pages, edges, fields, or curatorial decisions as content. Persistent curatorial decisions go in `curator_notes`; process notes go in your chat report.
- **Propose, never invent.** New node types or predicates require the user's approval and registration in `meta/GRAPH_SCHEMA.md`.
- **Never silently overwrite a fact.** Record a `contradicts` entry and surface the conflict.
- **Never hard-delete** a page, task, or edge without explicit confirmation. A cancelled task is `status: dropped`, not a deleted file.

## How to operate

1. **Read `meta/SETTINGS.md` and `meta/GRAPH_SCHEMA.md`** — this PMS's purpose and language, then its vocabulary.
2. **First-run gate:** if `meta/SETTINGS.md` is missing or its `setup_done` is `false`, run the setup skill before anything else. **Capture is the one exception** — a first message that is just "remind me to call Ana" gets the task written first, then the offer to configure. Everything else waits for setup; capture waiting for setup is how a task tracker dies in its first minute.
3. **Route the request** with the table below, then **read the matching SKILL.md and follow it step by step — never improvise a procedure.**

| Operation | Trigger (examples) | Procedure |
|---|---|---|
| Setup | `setup_done` false or `meta/SETTINGS.md` missing; "configure o PMS", "configure o KB", "novo tipo de node", "novo edge" | `meta/skills/setup/SKILL.md` |
| Capture | "to do", "todo", "remember me to", "add a task", "action item", "lembra de", "preciso" | `meta/skills/capture/SKILL.md` |
| Ingest | file dropped in `raw/`; "ingest", "add this to my PMS", "processe esta nota", "adicione ao KM" | `meta/skills/ingest/SKILL.md` |
| Query | "o que eu sei sobre X?", "como X se conecta a Y?", "what's on my plate", "o que está aberto", any lookup, traversal, or task list | `meta/skills/query/SKILL.md` |
| Lint | "lint", "revise o KM", "o que está quebrado"; "full lint", "is any of this made up" | `meta/skills/lint/SKILL.md` |

**Routing precedence.** Capture and ingest both react to "add this" — they are told apart by *what* is being added, not by the verb. An **imperative aimed at the user's future self** ("remember to email Ana") is capture. **Material to be understood** — a file, an article, a transcript, pasted text — is ingest. When a request is genuinely both ("here's the meeting transcript, and remind me to follow up"), run ingest, which will call capture for the action items. When it is genuinely ambiguous, ask; do not guess and do not run both independently.

**Skill composition.** Exactly one skill is authoritative for each workflow, and a skill may **invoke** another rather than reimplementing it: ingest calls capture for action items; capture and lint call setup for schema changes; query calls capture when the user turns an answer into a task. A skill never duplicates another's procedure — if you find yourself writing a task file from inside ingest, stop and follow `meta/skills/capture/SKILL.md` instead. The invoked skill owns its output format and its rules; the caller owns the decision to invoke.

# How it works

## Layers

1. **`raw/`** — The source inbox. Its root holds only **pending** sources; on successful ingest a source moves to `raw/archive/`. A source's *content* is immutable — ingest may only update its bookkeeping frontmatter (`ingested`, `touches`) and move the file. Flat otherwise; the kind of source lives in the `source:` frontmatter field, not in the path.
2. **`knowledge/`** — Knowledge content only: agent-authored node pages. **Flat** — every node is a file directly in `knowledge/`, no type subfolders; a node's type is its `type:` field.
3. **`tasks/`** — Task nodes: one file per task, action item, or reminder. Also flat; terminal tasks move to `tasks/archive/`. Tasks are **part of the graph** (see below) — the folder split is about lifecycle, not membership.
4. **`meta/`** — The machinery: `meta/GRAPH_INDEX.md` (the navigation index — every query, ingest, and capture starts by reading it; each entry carries the page's title **and its aliases**, so name resolution costs one file read instead of a scan of every page), `meta/GRAPH_SCHEMA.md` (the closed vocabulary), `meta/SETTINGS.md` (purpose, language, setup state), `meta/skills/` (operation procedures), and `meta/templates/` (node templates; `_node.template.md` is the generic seed — copy it to `meta/templates/<type>.md` to define a type — and `_task.template.md` is the fixed task shape).
5. **`CLAUDE.md`** (this file) — the static rules. The agent edits `meta/GRAPH_SCHEMA.md` and `meta/SETTINGS.md`; it never edits this file, and it never writes outside this PMS folder.

**On the two namings.** Folders say what they *hold*: `knowledge/` holds knowledge pages, `tasks/` holds tasks, `raw/` holds inputs. The `meta/GRAPH_*` files say what they *span*: the index and the schema each cover the whole graph, which is `knowledge/` and `tasks/` at once. This is why `knowledge/` is deliberately **not** called `graph/` — the graph is not a folder, and naming one folder after it implies the other one isn't part of it. That implication is precisely the bug that makes an inbound-edge scan miss half the graph.

## Nodes & Edges

**Nodes.** Every node is a file in the flat `knowledge/` folder and declares a `type:` in its frontmatter. A node is two things at once: the frontmatter is the **catalog** layer (structured, typed fields + edges) and the prose body is the **knowledge** layer (synthesized, free-form). A node's `type` must be one registered under **Nodes** in `meta/GRAPH_SCHEMA.md`. If a template exists for that type in `meta/templates/`, use it as the scaffold; its type-specific fields are optional scaffolding — fill only what the sources support, never a fabricated value. A node may carry an optional `curator_notes:` frontmatter field for persistent curatorial context (e.g. "intentionally distinct from [[Other Page]] — two identities of one entity; do not merge"); dedup and lint must respect it, and it is never restated in the prose body.

Every node also carries a **`sources:`** field — the list of source items the page was built from, as plain relative paths (`sources: ["raw/archive/2026-07-08-article.md"]`). This is the page's provenance record and the exact reverse of a source's `touches:`, which makes the link machine-readable in both directions: a corrected or retracted source can be traced to every page it fed. It is bookkeeping, **not** a typed edge — it is never traversed as graph structure and never appears in an answer's path line. Ingest appends to it; lint flags knowledge pages that have none. Tasks are exempt: a task's provenance is its `origin:` field, and only an `origin: ingest` task carries `sources:`.

**Edges.** Each typed relationship is a frontmatter field named after the predicate, whose value is a list of wikilinks. The active predicates are exactly the list in `meta/GRAPH_SCHEMA.md` § Edges, and that table's *meaning* column is also the dictionary for verbalizing edges in answers (`based_on` reads as "is built on", never as edge-speak). Directional: the field lives on the origin page and points at the target.

```yaml
part_of:
  - "[[A Broader Topic]]"
authored_by:
  - "[[A Person]]"
```

The agent writes these fields directly — in Cowork and Claude Code alike. The user can also edit them by hand in Obsidian's Properties panel. Because this is plain frontmatter, Dataview, Breadcrumbs, Juggl, and Graph Link Types can all read the graph (details in README); no plugin is required.

A plain `[[wikilink]]` in prose with no matching frontmatter field is **not** a typed edge — only the per-predicate fields are traversed. For **asymmetric** predicates only the forward field is stored on the origin page; inverses are for reading — don't hand-write them (their names aren't registered predicates anyway).

**The traversal set is `knowledge/` ∪ `tasks/`.** Both folders are one graph. "Following an edge" means reading or searching the predicate fields across **both** — a grep in Claude Code, a file scan in Cowork. This is load-bearing and easy to get wrong: outbound edges work either way, but **inbound** edges are found by scanning, so a scan scoped to `knowledge/` alone makes every task invisible to the node it points at. "What is blocking [[Project X]]?" is answered by tasks pointing *at* the project; scan one folder and the answer is silently empty. Scan both, always. By default the scan covers `knowledge/` plus the **root** of `tasks/`; include `tasks/archive/` only when the question is about history.

**Symmetric predicates are mirrored.** A predicate whose *inverse* column in `meta/GRAPH_SCHEMA.md` § Edges names the predicate itself (`contradicts`, `contrasts_with`) is written on **both** pages — the same field, each pointing at the other. This is deliberate duplication, and it is safe precisely because it is symmetric: a one-sided symmetric edge has exactly one correct repair (mirror it), so drift is detectable by set comparison and fixable without judgment. The reason it's worth the duplication is `contradicts`: a conflict that is only visible from the challenging page is not a warning. Any PMS-specific predicate later registered as symmetric inherits this rule automatically — the table is the trigger, not a hard-coded list.

Edge fields are **sets**: a given wikilink appears in a given field at most once. When a page is written again, union the new links into the existing list — never blind-append, or re-ingesting a corrected source silently doubles every edge. For a genuinely untyped "loosely related" link, use `see_also:` — it is NOT a typed edge and is never traversed; if one keeps mattering, lint prompts to promote it.

## Tasks

A task is a node that carries state. It lives in `tasks/`, carries typed edges like any node, is traversed like any node, and appears in `meta/GRAPH_INDEX.md` like any node. Its schema — required fields, the closed `status` enum, the closed `origin` enum — is fixed in `meta/GRAPH_SCHEMA.md` § Tasks and is **not** extended per PMS.

**Filenames are date-slugged; identity is in the frontmatter.** A task file is `YYYY-MM-DD-short-slug.md` (`2026-08-15-email-ana.md`) and carries a stable `id:` (`T-0042`). The date prefix makes files sort chronologically and makes two captures on different days impossible to collide; the slug keeps the wikilink readable. Wikilinks resolve on the **title**, not the id — `[[Email Ana about the Acme renewal]]`, never `[[T-0042]]`. The next id is the highest one listed in `meta/GRAPH_INDEX.md`, plus one; ids are never reused, so a count of files or entries is not a maximum. Only if the index is visibly stale does finding the next id cost a scan of `tasks/` and `tasks/archive/`.

**Tasks are never deleted.** An abandoned task is `status: dropped` with a reason in `notes` — the record of a decision not to do something is worth as much as the record of doing it. Terminal tasks (`done`, `dropped`) carry a `closed:` date and may be moved to `tasks/archive/` once that date is older than the window in `meta/SETTINGS.md`; lint proposes the move, and nothing is archived automatically. Archiving **removes the task's index entry** — the file keeps its edges and its id forever, but the index stays bounded, which is what makes it cheap enough to read on every operation.

**Linking happens at runtime, cheaply.** Capture resolves only what one read of `meta/GRAPH_INDEX.md` can resolve — exact title and alias matches become typed edges. It **never creates stub nodes** for names it doesn't recognize; an unresolved mention stays a plain prose `[[wikilink]]`, which lint's untyped-link check will later offer to promote. This keeps capture fast enough to be worth using, and it keeps the graph free of empty pages invented by a one-line reminder.

## Sources

Every file in `raw/` carries this frontmatter, tagged at capture time:

```yaml
---
type: source
source: article        # article | meeting | note | transcript | ...
title: "..."
date: <YYYY-MM-DD>
ingested: false        # ingest sets this to true
touches: []            # ingest fills this with the knowledge pages and tasks it produced
---
```

A source `type` (what kind of *input* it is) is a different axis from a node `type` (what kind of *thing in the world* a node page describes). A meeting transcript is a `source` in `raw/`; it may also produce a `meeting` node in `knowledge/` if that type is registered, and one or more tasks in `tasks/`. After ingest, the source lives in `raw/archive/` — location and the `ingested` flag should agree, and lint cross-checks them. `touches:` may list paths in both `knowledge/` and `tasks/`.

**Stamping.** The block above is what ingest *needs*, not what arrives. A file dropped into `raw/` usually has none of it. Ingest stamps the missing fields itself before doing anything else: infer `title` and `date` from the filename and the content, default `source:` to `note` when the kind is unclear, and leave a field empty rather than guess a value it cannot support. Stamping is the one permitted exception to source immutability — it adds bookkeeping frontmatter and never touches the body.

**Non-markdown sources.** A PDF, image, audio file, or any other binary cannot carry frontmatter. It gets a **sidecar**: a markdown file of the same name plus `.md` (`report.pdf` → `report.pdf.md`) holding the frontmatter block and a `file: report.pdf` field. The sidecar is the source of record — ingest reads the binary for content but does its bookkeeping on the sidecar, and the pair is archived together. A binary sitting in `raw/` with no sidecar is a pending source; ingest creates the sidecar as its first act.
