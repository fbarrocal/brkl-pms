---
name: query
description: >-
  Answer a question from the Personal Management System by reading synthesized node pages, traversing typed edges, and listing tasks. Use this whenever the user asks something answerable from their own PMS, asks to trace relationships or do multi-hop reasoning — "what do I know about X?", "o que eu sei sobre X?", "how does X connect to Y?", "what depends on Z?" — or asks about their own work: "what's on my plate", "what's open", "what's blocked", "o que está pendente", "what's due this week". Trigger it for relationship/traversal questions in particular, since those are exactly what the typed graph exists for.
---

# Query

Answer from the Personal Management System. Three modes; pick based on the question. In all of them: **the answer is natural prose about the things themselves** — never narrate pages, edges, fields, or metadata as the answer ("Page X correlates to Page Y through edge W" is the failure mode). The machinery is plumbing; translate it.

**Prerequisite:** `CLAUDE.md` — operate by it. Start every query at `meta/GRAPH_INDEX.md`. Answer in the language recorded under `meta/SETTINGS.md` § Language, unless the user asks in a different one — then answer in theirs and leave the stored files as they are.

**Scope, for every mode:** the graph is `knowledge/` **∪ the root of `tasks/`**. Any scan for inbound edges covers both — a scan of `knowledge/` alone silently drops every task, which is exactly the half of the answer the user asked for when they said "what's blocking this". Include `tasks/archive/` only when the question is about history ("what did I do last month", "why did we drop that").

## Mode A — lookup / synthesis

For "what do I know about X", "summarize my thinking on Y":

1. From the index, find candidate pages — its entries carry both titles and aliases, so a name the user used resolves there in one read. Only `tags` still require searching frontmatter. If a name you'd expect is missing from the index, scan `knowledge/` and `tasks/` as a fallback and mention that the index looks stale.
2. Read those synthesized pages and answer from them.
3. **Mention open work on the subject.** If tasks point at X (`about`, `depends_on`, `part_of`), a summary of X that omits them is incomplete — the user asked what they know, and what they still owe is part of that. One sentence, in prose: "You still owe a follow-up email to Ana on this." Skip terminal tasks unless asked.
4. Cite the pages you used: `[[Page]]`.

## Mode B — relationship / multi-hop

For "how does X connect to Z", "what depends on X", "what contradicts Y", "what's blocking X":

1. Find the starting page(s) from the index.
2. **Traverse the typed edges.** The predicate frontmatter fields (field names are the predicates in `meta/GRAPH_SCHEMA.md` § Edges) hold the outbound edges. To find *inbound* edges, search other pages' predicate fields for this page's wikilink — **across `knowledge/` and `tasks/` both** — matching its filename stem (the part of a link before any `|`), its `title`, and any `aliases` (the index lists all three). When following an outbound edge whose target is not in `knowledge/` or the root of `tasks/`, check `tasks/archive/` before calling it missing — a link to an archived task is valid. Symmetric predicates (marked so in the inverse column) are mirrored onto both pages, so their edges are always readable outbound — never scan for those. Walk as many hops as the question needs, but bound it: outbound hops are cheap, **each inbound hop costs a scan of every page**, so stop once the question is answered, and if a traversal is running long, report what you found and ask whether to keep going rather than silently walking the whole graph.
3. **Compose the answer in prose**, verbalizing each hop via the predicate's *meaning* column in `meta/GRAPH_SCHEMA.md` § Edges (`based_on` → "is built on"; `member_of` → "belongs to"). The reader should get a plain-language explanation of how the things relate, not a recitation of the graph.
4. Only the predicate fields are the graph. **Do not traverse `see_also` or plain prose `[[wikilinks]]` as typed edges** — and never invent an edge not in the files.

## Mode C — task list / triage

For "what's on my plate", "what's open", "what's blocked", "what's due this week", "what's left on Project X":

1. **Ask sync for live state first** (`meta/skills/sync/SKILL.md`, Mode 3). Todoist owns done/due, so a list built from the files alone can be a day stale. Use the files for the structure (what's `part_of` what, what waits on what), and Todoist for the state. If Todoist is unreachable, carry on from the index and **say the answer is as of** `todoist_synced_at`.
2. **Then read the `## Tasks` section of `meta/GRAPH_INDEX.md`.** It carries id, title, status, and due date — which is every field ordinary triage needs, so "what's open", "what's due this week", and "what's blocked" are all answered in one read. Open individual task files only for the ones you'll report in detail, or when the question needs a field the index doesn't carry (`owner`, `notes`, edges). If a task's due date is missing from the index but present in the file, say so — that is index drift, and lint fixes it.
3. **Filter by the closed enum, not by adjectives.** "Open work" means `status` in `open` / `doing` / `blocked` — say which you included. Terminal tasks (`done`, `dropped`) are excluded unless the user asks for history. **`tasks/archive/` is not in the index at all**, so a history question ("what did I finish last quarter", "why did we drop that") is the one case that costs a folder scan — do it when asked, and say that's what you're doing.
4. **Scoped by a subject?** "What's left on Project X" is an inbound-edge question — scan `tasks/` for tasks whose `about` / `part_of` / `depends_on` fields name that page, then filter by status.
5. **Answer as a short list, ordered by what makes it actionable:** blocked items first (they need a decision), then due date, then capture date. Give the id and title on each line, since the id is how the user will refer back to it. Two or three items can just be prose.
6. **Surface the stuck ones.** A `blocked` task whose `depends_on` target is already `done`, or an `open` task that's been open a long time, is worth one sentence — that is the whole point of tracking them. Don't fix it here; say it, and let capture or lint handle the change.
7. **When the list is empty, say so plainly** — don't pad it with near-misses from other statuses.

Mode C **reads**. It never changes a status, completes, drops, or archives a task — that is capture's Mode B. If the user's next words are "mark the second one done", follow `meta/skills/capture/SKILL.md`.

## When the answer isn't there

Say so plainly. Offer to check the root of `raw/` for pending sources, or to ingest more material. Do not fabricate facts, edges, or tasks.

## Optional: saving an answer

If the user asks to save the answer (or it's durable, reusable knowledge), file it as a new node of an appropriate type registered in `meta/GRAPH_SCHEMA.md` § Nodes (`concept` is the usual default): synthesize it, give it typed-edge fields, add it to the index. Ask before saving anything borderline.

If instead the answer surfaced something the user needs to *do*, follow `meta/skills/capture/SKILL.md` with `origin: query` — don't write the task file from here.

## Output

- The answer, in natural prose (edges verbalized, no page/edge narration).
- Citations to the pages used.
- For Mode B only: close with one compact audit line, e.g. `Path: A →based_on→ B →part_of→ C` — the receipt that the connection was traversed, not invented. One line, after the answer, never instead of it.
- For Mode C only: state the filter you applied, e.g. `Scope: open + doing + blocked, all subjects` — so an empty or short list is readable as a real answer rather than a missed scan.
