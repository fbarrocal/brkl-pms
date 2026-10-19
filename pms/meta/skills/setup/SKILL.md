---
name: setup
description: Configure or evolve this Personal Management System's schema. Use on first run (setup_done is false or meta/SETTINGS.md is missing) to interview the user and configure the PMS, and on later runs whenever the user wants to add or change node types, templates, or edge predicates — "add a node type", "configure o PMS", "configure o KB", "novo edge", "update the schema" — or when capture/ingest/lint flagged a type/predicate gap the user approved.
---

# Setup

Configures the two mutable rules files: `meta/SETTINGS.md` (purpose, language, conventions, `setup_done`) and `meta/GRAPH_SCHEMA.md` (node types, edge predicates) — plus templates in `meta/templates/`. **This skill is authoritative for both files**; no other skill edits them, and every schema change routes here. It never edits `CLAUDE.md`, and it never writes outside this PMS folder.

**Prerequisite:** `CLAUDE.md` — operate by it.

## Mode 1 — First run (`setup_done` false or `meta/SETTINGS.md` missing)

Interview the user with the AskUserQuestion tool (structured options); fall back to plain chat questions if the tool is unavailable. Ask the questions themselves in whatever language the user is writing to you in. Keep it to four questions:

1. **Purpose.** What is this PMS for — a topic, a book, a project, personal notes, a work stream, a research area? Offer common options plus free text.
2. **Node types.** Based on the purpose, propose a small set to create. Examples: work PMS → `person`, `project`, `team`, `meeting`; a book → `character`, `place`, `event`; learning material → `formula`, `recipe`, `term`. The user approves, adjusts, or rejects each; the generic `entity` and `concept` always remain available, and `task` always exists (its schema is fixed — it is never proposed, extended, or removed).
3. **Edges.** Ask whether the shipped predicate set in `meta/GRAPH_SCHEMA.md` § Edges needs PMS-specific additions — a book might want `ally_of` / `enemy_of`; a work PMS might want `owns` or `blocks`. Propose; the user approves. **Cover task relationships in this same question**, and start from the position that nothing needs adding: subtasks are `part_of`, blocked tasks `depends_on`, a task's subject is `about`, an extracted action item is `introduced_by`. Only propose a task predicate the shipped set genuinely cannot express. If the user approved a `person` node type in Q2, this is also the moment to offer promoting the task `owner` string field into an `assigned_to` typed edge.
4. **Language.** What language should the *content* be written in — node titles, task titles, prose bodies, and answers? Default to the language the user is writing in, and offer the alternatives explicitly, because chat language and content language often differ (a user may write to you in Portuguese but want an English vault, or the reverse). This is the one setting that is expensive to change later: it is baked into every page title, and retitling pages breaks every wikilink pointing at them. Ask it even when the answer seems obvious.

Then write it down, to the right file:

- **`meta/SETTINGS.md`** — the purpose under **Purpose**, the chosen language under **Language**, any convention the user changed, and `setup_done: true` in the frontmatter.
- **`meta/GRAPH_SCHEMA.md`** — the approved types under **Nodes** and any new predicates under **Edges**.
- **`meta/templates/`** — one file per approved type, replicated from `meta/templates/_node.template.md`. Templates are optional; the user can skip them and add later when a kind of thing recurs enough to deserve structure. Never create or edit `_task.template.md` — the task shape is fixed.

Close with a one-line summary of what was configured and how to start: drop a file in `raw/` and ask to ingest, or just say what you need to do and it gets captured as a task.

## Mode 2 — Schema changes (`setup_done` true)

For adding or amending node types, templates, or predicates after first run:

1. Confirm the requested change (or the gap flagged by capture/ingest/lint that the user approved).
2. Propose the full definition — type name, fields, and template for a node type; predicate, meaning, and inverse for an edge. For a symmetric predicate, mark it **(symmetric)** in the inverse column — that marker is what makes the mirroring rule fire.
3. On approval: create or adjust the template in `meta/templates/`; register or update the entry in `meta/GRAPH_SCHEMA.md` § Nodes or § Edges.
4. Report what changed. Renames and removals follow the no-hard-delete rule: never remove a type or predicate still in use without explicit confirmation and a migration plan for the affected pages.

**Out of scope for Mode 2:** the task schema. `status` and `origin` are closed enums and the task field list is fixed in `meta/GRAPH_SCHEMA.md` § Tasks — changing them changes what every capture writes in every PMS, which makes it a rulebook decision, not a per-PMS one. If the user wants a sixth status, tell them plainly that the answer is a `notes` line or a `tags` entry, and that changing the enum means changing the template itself.

Re-run the full Mode 1 interview only on request (or if the user sets `setup_done: false` again).
