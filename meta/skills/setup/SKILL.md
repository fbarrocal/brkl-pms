---
name: setup
description: Configure or evolve this knowledge base's schema. Use on first run (setup_done is false or SETTINGS.md is missing) to interview the user and configure the KB, and on later runs whenever the user wants to add or change node types, templates, or edge predicates — "add a node type", "configure o KB", "novo edge", "update the schema" — or when ingest/lint flagged a type/predicate gap the user approved.
---

# Setup

Configures `SETTINGS.md` — the only rules file this skill edits (plus creating templates in `meta/templates/`). Never edits `CLAUDE.md`.

**Prerequisite:** `CLAUDE.md` — operate by it.

## Mode 1 — First run (`setup_done` false or `SETTINGS.md` missing)

Interview the user with the AskUserQuestion tool (structured options); fall back to plain chat questions if the tool is unavailable. Keep it to three questions:

1. **Purpose.** What is this KB for — a topic, a book, a project, personal notes, learning material, a research area? Offer common options plus free text.
2. **Node types.** Based on the purpose, propose a small set to create. Examples: professional KB → `person`, `project`, `team`, `meeting`; a book → `character`, `place`, `event`; learning material → `formula`, `recipe`, `term`. The user approves, adjusts, or rejects each; the generic `entity` and `concept` always remain available.
3. **Edges.** Ask whether the generic predicate set in `SETTINGS.md` § Edges needs KB-specific additions — a book might want `ally_of` / `enemy_of`; a project KB might want `owns` / `blocks`. Propose; the user approves.

Then write it down: record the purpose under **Purpose**; create each approved template in `meta/templates/` by replicating `meta/templates/_node.template.md`; register the types under **Nodes** and any new predicates under **Edges**; set `setup_done: true` in `SETTINGS.md`'s frontmatter. Templates are optional — the user can skip them and add later when a kind of thing recurs enough to deserve structure. Close with a one-line summary of what was configured and how to start (drop a file in `sources/`, ask to ingest).

## Mode 2 — Schema changes (`setup_done` true)

For adding or amending node types, templates, or predicates after first run:

1. Confirm the requested change (or the gap flagged by ingest/lint that the user approved).
2. Propose the full definition — type name, fields, and template for a node type; predicate, meaning, and inverse for an edge.
3. On approval: create or adjust the template in `meta/templates/`; register or update the entry in `SETTINGS.md` § Nodes or § Edges.
4. Report what changed. Renames and removals follow the no-hard-delete rule: never remove a type or predicate still in use without explicit confirmation and a migration plan for the affected pages.

Re-run the full Mode 1 interview only on request (or if the user sets `setup_done: false` again).
