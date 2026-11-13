---
name: query
description: >-
  Answer a question from the {{SYSTEM}} by reading synthesized node pages<!-- slot:desc.lists --> and traversing typed edges<!-- /slot:desc.lists -->. Use this whenever the user asks something answerable from their own {{SYS}}, asks to trace relationships or do multi-hop reasoning — "what do I know about X?", "o que eu sei sobre X?", "how does X connect to Y?", "what depends on Z?"<!-- slot:desc.work /-->. Trigger it for relationship/traversal questions in particular, since those are exactly what the typed graph exists for.
---

# Query

Answer from the {{SYSTEM}}. <!-- slot:modes -->Two<!-- /slot:modes --> modes; pick based on the question. In all of them: **the answer is natural prose about the things themselves** — never narrate pages, edges, fields, or metadata as the answer ("Page X correlates to Page Y through edge W" is the failure mode). The machinery is plumbing; translate it.

**Prerequisite:** `CLAUDE.md` — operate by it. Start every query at `meta/GRAPH_INDEX.md`. Answer in the language recorded under `meta/SETTINGS.md` § Language, unless the user asks in a different one — then answer in theirs and leave the stored files as they are.

<!-- slot:scope -->
**Scope, for every mode:** the graph is `knowledge/`. Inbound edges are found by scanning its pages' predicate fields; a link into `raw/archive/` is valid.
<!-- /slot:scope -->

## Mode A — lookup / synthesis

For "what do I know about X", "summarize my thinking on Y":

1. From the index, find candidate pages — its entries carry both titles and aliases, so a name the user used resolves there in one read. Only `tags` still require searching frontmatter. If a name you'd expect is missing from the index, scan `knowledge/`<!-- slot:a.fallback /--> as a fallback and mention that the index looks stale.
2. Read those synthesized pages and answer from them.
<!-- slot:a.open-work /-->
<!-- slot:a.n4 -->3<!-- /slot:a.n4 -->. Cite the pages you used: `[[Page]]`.

## Mode B — relationship / multi-hop

For "how does X connect to Z", "what depends on X", "what contradicts Y"<!-- slot:b.blocking /-->:

1. Find the starting page(s) from the index.
2. **Traverse the typed edges.** The predicate frontmatter fields (field names are the predicates in `meta/GRAPH_SCHEMA.md` § Edges) hold the outbound edges. To find *inbound* edges, search other pages' predicate fields for this page's wikilink<!-- slot:b.both -->,<!-- /slot:b.both --> matching its filename stem (the part of a link before any `|`), its `title`, and any `aliases` (the index lists all three).<!-- slot:b.archive /--> Symmetric predicates (marked so in the inverse column) are mirrored onto both pages, so their edges are always readable outbound — never scan for those. Walk as many hops as the question needs, but bound it: outbound hops are cheap, **each inbound hop costs a scan of every page**, so stop once the question is answered, and if a traversal is running long, report what you found and ask whether to keep going rather than silently walking the whole graph.
3. **Compose the answer in prose**, verbalizing each hop via the predicate's *meaning* column in `meta/GRAPH_SCHEMA.md` § Edges (`based_on` → "is built on"; `member_of` → "belongs to"). The reader should get a plain-language explanation of how the things relate, not a recitation of the graph.
4. Only the predicate fields are the graph. **Do not traverse `see_also` or plain prose `[[wikilinks]]` as typed edges** — and never invent an edge not in the files.

<!-- slot:mode-c /-->
## When the answer isn't there

Say so plainly. Offer to check the root of `raw/` for pending sources, or to ingest more material. Do not fabricate <!-- slot:answer.tasks -->facts or edges<!-- /slot:answer.tasks -->.

## Optional: saving an answer

If the user asks to save the answer (or it's durable, reusable knowledge), file it as a new node of an appropriate type registered in `meta/GRAPH_SCHEMA.md` § Nodes (`concept` is the usual default): synthesize it, give it typed-edge fields, add it to the index. Ask before saving anything borderline.
<!-- slot:save.task /-->

## Output

- The answer, in natural prose (edges verbalized, no page/edge narration).
- Citations to the pages used.
- For Mode B only: close with one compact audit line, e.g. `Path: A →based_on→ B →part_of→ C` — the receipt that the connection was traversed, not invented. One line, after the answer, never instead of it.
<!-- slot:output.c /-->
