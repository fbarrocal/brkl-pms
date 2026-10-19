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

- **Plan:** `free` — on `free`, keep at most **5** active Todoist projects, which means at most 5 areas plus any unmanaged projects you already have. Change to `pro` if the account is upgraded.
- **Deadlines:** `off` — Todoist deadlines are Pro-only. While `off`, a task's `deadline` stays in the file and is shown in its description instead.
- **Unplaced tasks go to:** `inbox` — where a task with no project and no area is pushed.
- **Adopt from the Inbox:** `no` — Inbox items without a `PMS:` footer are offered for triage, never adopted automatically. Tasks added on the phone *inside a managed section or project* are always adopted.
- **Labels:** `pms-blocked`, `pms-dropped` — the only labels sync adds or removes. Every other label is the user's.
- **Sync cadence:** daily, as a Cowork scheduled task. Warn if the last sync is older than **6 days** — Todoist Free keeps one week of activity history.
