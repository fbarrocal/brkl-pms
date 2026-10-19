---
# TASK TEMPLATE — the fixed shape of every file in tasks/.
# Unlike node templates, this one is NOT copied or customized per PMS.
# Filename: YYYY-MM-DD-short-slug.md  (the date is capture date, not due date)

type: task
id: T-0000                    # stable, never reused; taken from next_task_id in meta/GRAPH_INDEX.md
title: <What needs to happen — an imperative, in the PMS's Language>
status: open                  # open | doing | blocked | done | dropped  — no other value
origin: capture               # capture | ingest | query

# --- optional: omit the line entirely rather than writing a placeholder ---
# due: <YYYY-MM-DD>
# owner: ""                   # plain string, NOT a typed edge (see GRAPH_SCHEMA § Tasks)
# tags: []
# notes: ""                   # why it's blocked, why it was dropped, any context that isn't a link
# closed: <YYYY-MM-DD>        # ADDED when status becomes done/dropped; removed if reopened.
                              # The archive window is measured from this, never from `updated`
                              # — any later edit would reset `updated` and hide the task forever.

# --- typed edges (predicates from "Edges" in meta/GRAPH_SCHEMA.md) ---
# Same vocabulary as knowledge nodes — tasks need no predicates of their own:
#   about:       - "[[The Topic Or Project]]"     # what this task concerns
#   part_of:     - "[[2026-08-10-parent-slug|The Parent Task]]"   # subtask — tasks are linked by file stem|title
#   depends_on:  - "[[What It Waits On]]"         # pairs with status: blocked
#   introduced_by: - "[[The Source Or Person]]"   # where it came from
# Only exact title/alias matches from meta/GRAPH_INDEX.md become edges at capture time, written as
# the index lists them: knowledge pages as [[Title]], tasks as [[file-stem|Title]].
# An unrecognized name stays a plain [[wikilink]] in the body — never invent a stub node for it.

# sources: []                 # ONLY when origin is ingest — the archived raw/ path
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
---

# <Task title>

One or two lines of context, in the user's own terms — what this is and why it matters. Keep it short: a task that needs three paragraphs is a project, and probably wants a node in `knowledge/` with the task pointing `about` it.

Mention related things as `[[wikilinks]]` inline. The ones that matched the index are already typed edges above; the ones that didn't are plain links here, waiting for lint to offer promoting them.
