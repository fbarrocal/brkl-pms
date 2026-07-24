---
name: setup
description: Configure or evolve this knowledge base's schema. Use on first run (setup_done is false or SETTINGS.md is missing) to interview the user and configure the KB, and on later runs whenever the user wants to add or change node types, templates, or edge predicates — "add a node type", "configure o KB", "novo edge", "update the schema" — or when ingest/lint flagged a type/predicate gap the user approved.
---

# Setup

Configures `SETTINGS.md` — the only rules file this skill edits (plus creating templates in `meta/templates/`). Never edits the KB's `CLAUDE.md`. The sole sanctioned write outside the KB folder is the embedded install check at the end of Mode 1 — injecting `meta/host-snippet.md` into a *host* project's `CLAUDE.md`, with explicit confirmation.

**Prerequisite:** `CLAUDE.md` — operate by it.

## Mode 1 — First run (`setup_done` false or `SETTINGS.md` missing)

Interview the user with the AskUserQuestion tool (structured options); fall back to plain chat questions if the tool is unavailable. Ask the questions themselves in whatever language the user is writing to you in. Keep it to four questions:

1. **Purpose.** What is this KB for — a topic, a book, a project, personal notes, learning material, a research area? Offer common options plus free text.
2. **Node types.** Based on the purpose, propose a small set to create. Examples: professional KB → `person`, `project`, `team`, `meeting`; a book → `character`, `place`, `event`; learning material → `formula`, `recipe`, `term`. The user approves, adjusts, or rejects each; the generic `entity` and `concept` always remain available.
3. **Edges.** Ask whether the generic predicate set in `SETTINGS.md` § Edges needs KB-specific additions — a book might want `ally_of` / `enemy_of`; a project KB might want `owns` / `blocks`. Propose; the user approves.
4. **Language.** What language should the *content* be written in — node titles, prose bodies, and answers? Default to the language the user is writing in, and offer the alternatives explicitly, because chat language and content language often differ (a user may write to you in Portuguese but want an English vault, or the reverse). This is the one setting that is expensive to change later: it is baked into every page title, and retitling pages breaks every wikilink pointing at them. Ask it even when the answer seems obvious.

Then write it down: record the purpose under **Purpose** and the chosen language under **Language**; create each approved template in `meta/templates/` by replicating `meta/templates/_node.template.md`; register the types under **Nodes** and any new predicates under **Edges**; set `setup_done: true` in `SETTINGS.md`'s frontmatter. Templates are optional — the user can skip them and add later when a kind of thing recurs enough to deserve structure. Close with a one-line summary of what was configured and how to start (drop a file in `sources/`, ask to ingest).

**Embedded install check (last step of Mode 1).** Detect whether this KB is embedded inside a larger project: the KB folder is not the repository root, or a project `CLAUDE.md` exists above it. If it is standalone, skip this step silently. If embedded, look for the `kb-host-snippet` marker in the host's `CLAUDE.md` and **propose** — never apply unasked — the fix that matches what you find:

- **No marker** (or no host `CLAUDE.md` at all): offer to append the contents of `meta/host-snippet.md` to the host `CLAUDE.md` (creating the file if missing), first adjusting the `kb/` paths in the block to the KB folder's actual name.
- **Marker present but version-lagging** (its `v` number is older than the one in `meta/host-snippet.md`): offer to replace everything between the markers with the current block. Never append a second copy.

This is the **only write outside the KB folder any skill may ever make**, and only with the user's explicit confirmation. If the user declines, move on without it — lint will re-surface the gap.

## Mode 2 — Schema changes (`setup_done` true)

For adding or amending node types, templates, or predicates after first run:

1. Confirm the requested change (or the gap flagged by ingest/lint that the user approved).
2. Propose the full definition — type name, fields, and template for a node type; predicate, meaning, and inverse for an edge.
3. On approval: create or adjust the template in `meta/templates/`; register or update the entry in `SETTINGS.md` § Nodes or § Edges.
4. Report what changed. Renames and removals follow the no-hard-delete rule: never remove a type or predicate still in use without explicit confirmation and a migration plan for the affected pages.

Re-run the full Mode 1 interview only on request (or if the user sets `setup_done: false` again).
