---
name: ingest
description: Ingest a pending item from the sources/ inbox into the content pages. Use this whenever the user drops a new file into sources/, or says "ingest", "process this note", "add this to my knowledge base", "processe esta nota", "I read this article, capture it", or otherwise wants raw material turned into curated, cross-referenced node pages with typed edges. Trigger it even when the user just points at a sources/ file and says "process it" without naming the operation.
---

# Ingest

Turn a pending source into curated knowledge: update or create typed node pages, add typed edges, flag contradictions, and update the index. The source is input; `content/` is output.

**Prerequisite:** `CLAUDE.md` — operate by it. `SETTINGS.md`'s **Purpose** guides what is worth extracting and how to type it; its **Nodes** and **Edges** sections are the single source of truth for types and predicates.

## Steps

1. **Prepare the source.** Take the pending file from the root of `sources/`.
   - **If it is a binary** (PDF, image, audio, …), create its sidecar `<filename>.md` carrying the source frontmatter block plus `file: <filename>`; the sidecar is the source of record from here on, and the pair travels together.
   - **If its frontmatter is missing or incomplete**, stamp the missing bookkeeping fields (`type`, `source`, `title`, `date`, `ingested`, `touches`): infer `title` and `date` from the filename and content, default `source:` to `note` when the kind is unclear, and leave a field empty rather than fabricate a value. Stamping is the only edit permitted to a source besides bookkeeping and location.
   - **Check `sources/archive/` for a prior version** of this same source (same basename, same `title`, or obviously the same material). If there is one, this is a **re-ingest**, not a new source — say so and confirm with the user before proceeding, then treat it as a correction pass: union edges rather than adding them again, and route changed facts through step 8 (conflicts) instead of overwriting.
2. **Read the source.** Its content is immutable — extract from it, never rewrite the body.
3. **Load context.** Read `meta/index.md`, then the existing node pages the source is likely to touch (by title, alias, tag). You are weaving into an existing structure.
4. **Extract** the things (nodes) and relationships the source contains.
5. **Type every node.** Assign each node a `type` from `SETTINGS.md` § Nodes. If a source describes a kind of thing that fits no registered type, propose a new type — route it through the setup skill (Mode 2) on the user's approval. Never invent a type silently.
6. **Type every relationship.** Map each to an allowed predicate from `SETTINGS.md` § Edges. If none fits, propose an addition via the setup skill — never invent a predicate silently.
7. **Write the pages.** For each affected node, in the flat `content/` folder:
   - **dedup first:** check `meta/index.md` — its entries carry titles *and* aliases, so one read resolves variant names (people and things often appear under several). Prefer updating the existing node, and ask the user when unsure. If the index looks stale, fall back to scanning `content/` frontmatter and tell the user to run lint. Respect `curator_notes` — if pages are marked intentionally distinct, never propose merging them;
   - update or create the page, using the type's template from `meta/templates/` as scaffold if one exists;
   - write synthesis in your own words (never paste source text), **in the language recorded under `SETTINGS.md` § Language** — which may differ from the source's language and from the chat's; using `[[wikilinks]]` inline for readability. The body contains knowledge about the subject only — no process commentary, no curatorial narration; persistent curatorial decisions go in the `curator_notes` frontmatter field, process notes in your chat report;
   - add each typed edge as a per-predicate frontmatter field (`"[[wikilink]]"` in its list). **Edge fields are sets** — union the new links into whatever is already there; if a link is already present in that field, leave it alone. Never blind-append;
   - **mirror symmetric predicates.** If the predicate's inverse column in `SETTINGS.md` § Edges names the predicate itself, write the same field on the *other* page too, pointing back. Both pages must end up carrying the edge; writing one side is a bug lint will flag;
   - **record provenance:** add this source's archived path to the page's `sources:` list (also a set — a re-ingest of the same source must not duplicate the entry);
   - fill type-specific fields only where the source supports them — never fabricate a value to fill a field;
   - bump `updated`.
8. **Handle conflicts, don't bury them.** If the source contradicts an existing page, add a `contradicts` entry **on both pages** (it is symmetric — see the mirroring rule) and flag it in your report. Never silently overwrite. A contradiction recorded on only one page is invisible to anyone reading the other, which defeats the point of recording it.
9. **Close the loop on the source.** Set `ingested: true`, fill `touches:` with the pages you updated, then **move the file to `sources/archive/`** (create the folder if missing) — binary and sidecar move together as a pair. Never alter the source's body content — only its bookkeeping frontmatter and its location.
10. **Update `meta/index.md`** with any new pages (grouped by type), **including each page's aliases on its entry** — the index is what makes dedup and name lookup cheap, so an entry without its aliases defeats the purpose. Bump the index's `updated` date.

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

## If you can't finish

Step 9 is deliberately last: until it runs, the source is still pending and nothing is lost. If you have to stop partway, **leave the source in the root of `sources/` with `ingested: false`**, and report exactly which pages you already wrote. A half-ingested source that still looks pending is recoverable; one that was archived early is not.
