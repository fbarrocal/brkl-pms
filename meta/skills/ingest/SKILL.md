---
name: ingest
description: Ingest a pending item from the sources/ inbox into the content pages. Use this whenever the user drops a new file into sources/, or says "ingest", "process this note", "add this to my knowledge base", "processe esta nota", "I read this article, capture it", or otherwise wants raw material turned into curated, cross-referenced node pages with typed edges. Trigger it even when the user just points at a sources/ file and says "process it" without naming the operation.
---

# Ingest

Turn a pending source into curated knowledge: update or create typed node pages, add typed edges, flag contradictions, and update the index. The source is input; `content/` is output.

**Prerequisite:** `CLAUDE.md` — operate by it. `SETTINGS.md`'s **Purpose** guides what is worth extracting and how to type it; its **Nodes** and **Edges** sections are the single source of truth for types and predicates.

## Steps

1. **Read the source** in the root of `sources/`. Its content is immutable — extract from it, never rewrite the body.
2. **Load context.** Read `meta/index.md`, then the existing node pages the source is likely to touch (by title, alias, tag). You are weaving into an existing structure.
3. **Extract** the things (nodes) and relationships the source contains.
4. **Type every node.** Assign each node a `type` from `SETTINGS.md` § Nodes. If a source describes a kind of thing that fits no registered type, propose a new type — route it through the setup skill (Mode 2) on the user's approval. Never invent a type silently.
5. **Type every relationship.** Map each to an allowed predicate from `SETTINGS.md` § Edges. If none fits, propose an addition via the setup skill — never invent a predicate silently.
6. **Write the pages.** For each affected node, in the flat `content/` folder:
   - **dedup first:** check existing pages' `title` and `aliases` for a match (people and things often appear under variant names); prefer updating the existing node, and ask the user when unsure. Respect `curator_notes` — if pages are marked intentionally distinct, never propose merging them;
   - update or create the page, using the type's template from `meta/templates/` as scaffold if one exists;
   - write synthesis in your own words (never paste source text), using `[[wikilinks]]` inline for readability. The body contains knowledge about the subject only — no process commentary, no curatorial narration; persistent curatorial decisions go in the `curator_notes` frontmatter field, process notes in your chat report;
   - add each typed edge as a per-predicate frontmatter field (`"[[wikilink]]"` in its list);
   - fill type-specific fields only where the source supports them — never fabricate a value to fill a field;
   - bump `updated`.
7. **Handle conflicts, don't bury them.** If the source contradicts an existing page, add a `contradicts` field entry and flag it — never silently overwrite.
8. **Close the loop on the source.** Set `ingested: true`, fill `touches:` with the pages you updated, then **move the file to `sources/archive/`** (create the folder if missing). Never alter the source's body content — only its bookkeeping frontmatter and its location.
9. **Update `meta/index.md`** with any new pages (grouped by type) and bump its `updated` date.

## Report format

```
Ingested: <source title> → moved to sources/archive/
Pages touched (N): [[Page A]], [[Page B]], …
New nodes (N): [[Page C]] (type: person)
New typed edges (N): A --based_on--> B, C --member_of--> D, …
⚠ Contradictions: <page> — <what conflicts>          (or "none")
⚠ Type gaps: source describes "<X>" — propose new type `<name>`?   (or "none")
⚠ Predicate gaps: relationship "<X>" fit no predicate — propose `<name>`?   (or "none")
```

The flags at the bottom are the point — they're what stops the graph from rotting silently.
