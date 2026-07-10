---
# GENERIC NODE TEMPLATE — copy this to meta/templates/<type>.md and customize.
# Whatever type you define here must be registered under "Nodes" in SETTINGS.md.
# Templates are OPTIONAL: a node can exist with just `type` + prose and no template.
type: <type-name>
title: <Node name>
aliases: []
tags: []

# --- type-specific plain fields (optional) ---
# Add metadata this type usually carries. Examples for a `person`:
#   role: ""
#   org: ""
# Leave a field out entirely rather than inventing a value for it.

# --- typed edges (predicates from "Edges" in SETTINGS.md) ---
# Each is a field named for the predicate, holding a list of wikilinks:
#   part_of:
#     - "[[A Larger Thing]]"

see_also: []            # untyped soft links — NOT traversed as graph edges
# curator_notes: ""     # optional persistent curatorial context (e.g. intentionally distinct from [[X]]); respected by dedup/lint, never restated in prose
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
---

# <Node name>

Synthesized prose in the agent's own words. The frontmatter fields above are optional scaffolding — fill only what the sources actually support, and never invent a value just to fill a field. The prose is the knowledge layer; the typed fields are the graph layer. A node is both at once.

## <Optional section — e.g. Key facts / Summary / Role>
- …

## Sources
- Which source items contributed to this page (after ingest they live in `sources/archive/`).
