---
name: query
description: Answer a question from the knowledge base by reading synthesized node pages and traversing typed edges. Use this whenever the user asks something answerable from their own KB, or asks to trace relationships, find connections, or do multi-hop reasoning — "what do I know about X?", "o que eu sei sobre X?", "how does X connect to Y?", "what depends on Z?", "trace the path from A to B". Trigger it for relationship/traversal questions in particular, since those are exactly what the typed graph exists for.
---

# Query

Answer from the knowledge base. Two modes; pick based on the question. In both: **the answer is natural prose about the things themselves** — never narrate pages, edges, fields, or metadata as the answer ("Page X correlates to Page Y through edge W" is the failure mode). The machinery is plumbing; translate it.

**Prerequisite:** `CLAUDE.md` — operate by it. Start every query at `meta/index.md`.

## Mode A — lookup / synthesis

For "what do I know about X", "summarize my thinking on Y":

1. From the index, find candidate pages by title, alias, tag.
2. Read those synthesized pages and answer from them.
3. Cite the pages you used: `[[Page]]`.

## Mode B — relationship / multi-hop

For "how does X connect to Z", "what depends on X", "what contradicts Y":

1. Find the starting page(s) from the index.
2. **Traverse the typed edges.** The predicate frontmatter fields (field names are the predicates in `SETTINGS.md` § Edges) hold the outbound edges. To find *inbound* edges, search other pages' predicate fields for this page's wikilink — matching its `title` and any `aliases`, since edges may point at either. Walk as many hops as the question needs.
3. **Compose the answer in prose**, verbalizing each hop via the predicate's *meaning* column in `SETTINGS.md` § Edges (`based_on` → "is built on"; `member_of` → "belongs to"). The reader should get a plain-language explanation of how the things relate, not a recitation of the graph.
4. Only the predicate fields are the graph. **Do not traverse `see_also` or plain prose `[[wikilinks]]` as typed edges** — and never invent an edge not in the files.

## When the answer isn't there

Say so plainly. Offer to check the root of `sources/` for pending sources, or to ingest more material. Do not fabricate facts or edges.

## Optional: saving an answer

If the user asks to save the answer (or it's durable, reusable knowledge), file it as a new node of an appropriate type registered in `SETTINGS.md` § Nodes (`concept` is the usual default): synthesize it, give it typed-edge fields, add it to the index. Ask before saving anything borderline.

## Output

- The answer, in natural prose (edges verbalized, no page/edge narration).
- Citations to the pages used.
- For Mode B only: close with one compact audit line, e.g. `Path: A →based_on→ B →part_of→ C` — the receipt that the connection was traversed, not invented. One line, after the answer, never instead of it.
