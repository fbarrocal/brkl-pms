---
# PROJECT — a finite outcome. Maps to ONE section inside its area's Todoist project.
# Filename = title: knowledge/<Project name>.md
type: project
title: <Project name>
aliases: []
tags: []
part_of:
  - "[[<Area name>]]"       # exactly one area — this decides which Todoist project the section lives in
todoist_section_id: ""     # written by sync when the section is created; never typed by hand
# outcome: ""              # optional — what "done" looks like, if the user said
# typed edges, if any — predicates from meta/GRAPH_SCHEMA.md § Edges
see_also: []
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
---

# <Project name>

The goal and why it matters, in the user's terms. The steps are tasks in `tasks/` that are `part_of` this page; don't restate them here.
