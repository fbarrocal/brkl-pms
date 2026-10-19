---
setup_done: false
---

# Settings

This PMS's **state and configuration**: what it is for, what language it is written in, and whether it has been set up (`setup_done`, in the frontmatter above). Written once at first run and rarely again.

This is one of exactly two mutable **rules** files (the agent also maintains the index, templates, and content, but none of those define rules). The other is `meta/GRAPH_SCHEMA.md`, which holds the *vocabulary* — node types, the task schema, and edge predicates. Keep the two apart: settings answer "what is this PMS", schema answers "what may exist in it". The static rules live in `CLAUDE.md` and are never edited.

## Purpose

_(unset — first-run setup records here, in one or two sentences, what this PMS is for. Every ingest, capture, and query reads this to guide what is worth extracting and how to type it.)_

## Language

_(unset — first-run setup records here the language for node titles, task titles, prose bodies, and answers.)_

This governs **content**, not conversation: the user may chat in one language and want the vault in another. Field names, node types, `status`/`origin` values, and edge predicates always stay in English — they are schema, not prose. Changing this after pages exist means retitling nodes, which breaks every wikilink pointing at them, so treat a change as a migration, not an edit.

## Conventions

Operating preferences for this PMS. Defaults shown; setup or the user may change them.

- **Task ID prefix:** `T` — task IDs are `T-0001`, `T-0002`, … Filenames stay date-slugged (`2026-08-15-email-ana.md`); the ID is frontmatter, not filename.
- **Archive completed tasks after:** 30 days in a terminal state (`done` / `dropped`). Lint proposes the move; nothing is archived automatically.
