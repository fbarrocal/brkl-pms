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

## Todoist

Bindings and policies for the task surface. Setup writes these; the sync skill reads them.

- **Connection:** _(unset — setup Step 0 records `connected (<account>)` or `not connected`)_.
- **Mode:** `single` — the PMS lives in **one** Todoist project, its bucket, and never touches the user's other projects or Inbox. `multiple` (one Todoist project per `area`) only when the user explicitly asks for it at setup.
- **Bucket:** _(unset — setup Q5 records the area that is this PMS's Todoist project; in `multiple` mode, the area where unplaced tasks go)_.
- **PMS id:** _(unset — setup writes a short slug of the PMS's name, e.g. `rpg-campaign`)_. It prefixes every task footer (`PMS: rpg-campaign/T-0042`), so several PMSes can share one Todoist account without matching each other's tasks. Never change it after tasks are pushed.
- **Plan:** _(unset — read from the account at setup: `free` or `pro`)_. Plan limits — on Free: 5 active projects, no deadlines, one week of activity history — belong to the account owner. When Todoist refuses something for a plan limit, sync reports it and suggests upgrading. It never works around the limit by placing tasks somewhere else.
- **Deadlines:** `off` on Free, `on` on Pro. While `off`, a task's `deadline` stays in the file and is shown in its description instead.
- **Unplaced tasks go to:** the bucket, outside any section. The PMS never writes to the Todoist Inbox.
- **Adoption:** tasks added on the phone *inside the bucket* (or any bound project, in `multiple` mode) are always adopted. Nothing outside the bound projects is ever read — the Inbox and the user's other projects stay the user's.
- **Labels:** `pms-blocked`, `pms-dropped` — the only labels sync adds or removes. Every other label is the user's.
- **Sync schedule:** _(unset — setup Q6 records e.g. `daily 07:00 America/Sao_Paulo`, `weekly lint Mon`, or `not scheduled`)_. Whatever the schedule, warn if the last sync is older than **6 days**: Todoist Free keeps one week of activity history.
