---
name: lint
description: Run a health check on the {{SYSTEM}} and propose fixes. Use this whenever the user says "lint", "check my {{SYS}}", "check my knowledge base", "revise o KM", "what's broken", "o que está quebrado", "clean up the graph", "run maintenance", or wants a periodic (e.g. weekly) health pass. Also use for the deeper passes — "full lint", "deep lint", "check my sources", "is any of this made up", "verifique as fontes". Trigger it proactively if the user mentions the {{SYS}} feels messy, has dead links, or has drifted. It finds unregistered types/predicates, settings drift, duplicate and dangling edges, dependency cycles, untyped links to promote, orphan pages, contradictions, `raw/` inbox mismatches, index drift,<!-- slot:desc.tasks /--> prose that narrates machinery, and pages whose claims their sources don't support.
---

# Lint

The health check that substitutes for the guarantees an external database would give you. It reports and proposes — it does not change or delete files without explicit confirmation.

**Prerequisite:** `CLAUDE.md` — operate by it. `meta/GRAPH_SCHEMA.md` is the authority for valid <!-- slot:prereq.tasks -->node types and edge fields<!-- /slot:prereq.tasks -->; `meta/SETTINGS.md` is the authority for <!-- slot:prereq.conventions -->purpose and language<!-- /slot:prereq.conventions -->.

## Scope

<!-- slot:scope -->
Run the checks across `knowledge/` (`raw/` for #8, #11 and #12; `raw/archive/` as a valid link target for #5). **Say in the report which folders you actually scanned** — a clean result from a half-scan is indistinguishable from a clean result, and that is the worst thing a health check can produce.
<!-- /slot:scope -->

<!-- slot:exemptions /-->
## Three passes

The checks differ enormously in cost, and a health check nobody runs is worth nothing. Pick a pass; each one includes the ones before it.

| Pass | Cost | Cadence | Contains |
|---|---|---|---|
| **A — Quick** | frontmatter only, no cross-file resolution | weekly<!-- slot:pass-a.captures /--> | 1, 2, 3, 8, 9, 10, 12<!-- slot:pass-a -->, 15<!-- /slot:pass-a --> |
| **B — Full** | resolves edges across every file<!-- slot:pass-b.cost /--> | monthly, or after a burst of ingests | A + 4, 5, 6, 7, 11, 13<!-- slot:pass-b.checks -->, 16<!-- /slot:pass-b.checks --> |
| **C — Fidelity** | re-reads source material and judges prose | occasionally, and before you rely on this system for something that matters | B + 17, 18 |

**Pass A is the default.** Run it when the user just says "lint". Offer B if A finds edge or index problems, since those usually travel with the ones only B can see. Offer C when the user asks whether the content is trustworthy, before a hand-off, or when it has been many ingests since the last one. Never run C silently — it is expensive, and the user should know they asked for it.

If a pass is running long, **stop and report what you have**, naming the checks you completed and the ones you skipped. A partial report that says so is useful; a partial report presented as complete is a lie about the system's health.

## Checks

### Pass A — structure and state

1. **Missing or unregistered node types.** Any node with no `type` at all, or whose `type` is not in `meta/GRAPH_SCHEMA.md` § Nodes. Propose registering it (via the setup skill) or reassigning it to an existing type.<!-- slot:c1.misfile /-->
2. **Schema and settings drift.** A registered type whose § Nodes entry names a template file that is missing (types marked "Template: none" are fine), or whose fields disagree with its entry in `meta/GRAPH_SCHEMA.md` § Nodes. Propose aligning them. Also flag orphan templates (a `meta/templates/<type>.md` with no matching entry in § Nodes), and flag if `setup_done` is `true` in `meta/SETTINGS.md` but its Purpose or Language is still unset. Also flag content whose titles or prose are plainly not in the recorded Language — mixed-language vaults are a slow drift that only shows up once they are expensive to fix.
3. **Invalid predicates.** Any edge field whose name is not in `meta/GRAPH_SCHEMA.md` § Edges. Propose mapping it to an allowed predicate, or registering a new one via the setup skill.
8. **Source inbox (`raw/`) state.** Pending sources = files in the root of `raw/`; list them to run ingest on. Cross-check flag vs location: a file in the root with `ingested: true` should be archived (propose the move); a file in `raw/archive/` with `ingested: false` needs investigation.
<!-- slot:c9 -->
9. **Index drift.** Pages on disk missing from `meta/GRAPH_INDEX.md`, index entries pointing to files that don't exist, and **alias drift** (an entry whose listed aliases disagree with the page's own `aliases` field). Alias drift is the quiet one: it makes dedup and name lookup miss, which is how duplicate nodes get created. An index entry pointing at a file that no longer exists is also this system's only detector for a page that was deleted — treat it as that, not as a typo. Sources in `raw/archive/` were never in the index — do not report them as missing.
<!-- /slot:c9 -->
10. **Scale watch.** Rough page/token count; warn if approaching the ~150–200 knowledge-page ceiling where an external index becomes worth adding.<!-- slot:c10.tasks /-->
12. **Unstamped sources.** Files in `raw/` missing the source frontmatter block, and binaries with no `<filename>.md` sidecar. Propose stamping them (via ingest) so they can be processed.
<!-- slot:c14 /-->
15. **Malformed edge lists.** Read each file's own predicate fields; no cross-file work needed:
    - **Duplicate entry.** The same wikilink appearing twice in the same predicate field. Edge fields are **sets**, and `CLAUDE.md` names the cause outright: an ingest that blind-appends instead of unioning. A corrected source re-ingested three times gives you an edge listed three times, which silently triples that relationship's weight in every traversal and every count. The repair is always "collapse to one" — no judgment needed, so propose them all in one go.
    - **Self-referential edge.** A page listing its own filename stem, title, or alias in one of its own edge fields. Always a bug; a page is not `part_of` itself.
    - **Empty or malformed field.** A predicate field present but empty, or holding a bare string instead of a `"[[wikilink]]"`. Both read as "no edge" to a traversal while looking like an edge to a human.

<!-- slot:c19 /-->
### Pass B — the graph itself

4. **Untyped links to promote.** Prose `[[wikilinks]]` (or `see_also` entries) that recur but have no matching predicate field. Propose a predicate to promote each — or confirm it stays `see_also`.<!-- slot:c4.tasks /--> This check produces the most volume and the least urgency of any in the file: report it as a count with the top few examples, never as a full list.
5. **Dangling edges.** Predicate-field wikilinks that resolve to no file. Resolve by **filename** — the part of the link before any `|` — against <!-- slot:c5.targets -->`knowledge/` and `raw/archive/`<!-- /slot:c5.targets --> (an `introduced_by` edge may point at an ingested source); a link to an archived file is valid, not dangling.<!-- slot:c5.bare --> A bare source title (no stem) is dangling: Obsidian and Dataview cannot follow it.<!-- /slot:c5.bare --> Offer to create a stub, or rewrite the link to the form the index lists.<!-- slot:c5.both /-->
6. **Orphan pages.** <!-- slot:c6.only -->Pages in `knowledge/`<!-- /slot:c6.only --> with no inbound and no outbound typed edges.<!-- slot:c6.area /--> Surface for linking or archiving. Respect `curator_notes` before proposing any merge or removal.<!-- slot:c6.tasks /-->
7. **Contradictions.** `contradicts` edges and any conflicting facts across pages. List for resolution.
11. **Provenance gaps.** **Knowledge pages** with an empty or missing `sources:` field, `sources:` entries pointing at a file that isn't in `raw/`, and **broken round-trips** — a page listing a source that doesn't list it back in `touches:`, or vice versa.<!-- slot:c11.touches /--> An unsourced page is the *shape* a fabricated one takes — but only the shape. This check cannot see a fabricated page that cites a real source; that is #18's job, and #11 passing is not evidence of truth.
13. **One-sided symmetric edges.** For each predicate marked **(symmetric)** in `meta/GRAPH_SCHEMA.md` § Edges, a page carrying it must appear in the same field on the page it points at. Report any that don't. This is the one check whose fix needs no judgment — the repair is always "mirror it" — so propose applying all of them in one go rather than asking page by page. It matters most for `contradicts`: an unmirrored conflict is invisible from the page being challenged.
<!-- slot:c16 -->
16. **Dependency cycles.** Walk `depends_on` and `part_of` across `knowledge/` and report any cycle — A depends on B depends on A, or a page that is `part_of` one of its own parts. A cycle is almost always an extraction error, and it sends multi-hop answers in circles. Report the full ring, not one member, and let the user decide which edge is wrong; never break a cycle by picking an edge yourself. Bound the walk and say so if you stopped early.
<!-- /slot:c16 -->
<!-- slot:c20 /-->

### Pass C — is the content true

These two read material rather than metadata. They are the only checks that can catch the failure this whole system is most exposed to: an agent that wrote something plausible and unsupported. Everything in passes A and B verifies that the filing is tidy; nothing there opens a folder to see whether the contents are right.

17. **Prose that narrates machinery.** Read node<!-- slot:c17.tasks /--> bodies. `CLAUDE.md` requires the prose to speak about the things themselves — "Page X relates to Page Y through edge W" is the named failure mode. Flag bodies that narrate pages, edges, fields, ingests, or curatorial decisions; flag curatorial reasoning that belongs in `curator_notes`; flag process commentary that belongs in a chat report. Quote the offending sentence and propose the rewrite — this is one where showing beats describing. It is also the check most likely to find drift after a long run of ingests, because meta-commentary creeps in one sentence at a time.
18. **Source fidelity (sampled).** For a sample of knowledge pages, re-read the sources in their `sources:` field and check that the page's claims are actually supported. Flag: claims present in the page and absent from every cited source; figures, dates, and names that disagree with the source; and confident phrasing where the source hedged.
    - **Sample, and say so.** Take five pages, or 10% of `knowledge/`, whichever is larger. Prioritise the most recently written, the ones with the most edges (a wrong page with many edges poisons the most traversals), and any page whose sources were re-ingested. **State the sample size and which pages you checked** — "sampled 8 of 62 pages" is a finding; "sources look fine" is a false clean bill of health.
    - **A miss here is the most serious thing lint can find.** It means the system produced knowledge that no material supports, which is the one failure that makes everything downstream untrustworthy. Report it first, above everything else, regardless of count.
    - Do not rewrite the page yourself. Report the unsupported claim, cite the source, and let the user decide — the correct repair is sometimes "the page is wrong", sometimes "the source list is incomplete", and you cannot tell which.

## Report format

**Order by severity, not by check number.** A report that opens with rare structural nits and buries an unsupported claim on line 40 trains the user to skim it, and a skimmed health check is a decorative one. Three bands, always in this order, and omit any band that is empty:

- **Broken** — produces wrong answers right now: #18, #16, #5, #13, #15<!-- slot:band.broken /-->, #3, #7.
- **Drifting** — will produce wrong answers soon: #9, #11, #2, #1, #12, #8<!-- slot:band.drift-closed /-->, #17<!-- slot:band.drift-todoist /-->.
- **Housekeeping** — taste and volume: #4, #6, #10<!-- slot:band.house /-->.

```
{{SYS}} Lint — <date> — Pass A (quick)
Scanned: knowledge/ (62)<!-- slot:ex.scanned -->. Not scanned: source bodies.<!-- /slot:ex.scanned -->

BROKEN (4)
  #15 Duplicate edges (3): [[A]] lists [[B]] twice under `uses` → collapse all?
<!-- slot:ex.c14 -->
  #5  Dangling edge (1): [[C]] is `based_on` [[Missing Page]], which doesn't exist → create a stub?
<!-- /slot:ex.c14 -->

DRIFTING (5)
  #9  Index drift: 2 pages missing, 1 alias mismatch<!-- slot:ex.c9 /-->
  #2  Settings drift: type `person` has no meta/templates/person.md → create?

HOUSEKEEPING (2)
  #4  Untyped links (14): most common — [[Acme]] in <!-- slot:ex.c4 -->4 pages<!-- /slot:ex.c4 --> → create a node?
  #10 Scale: ~62 knowledge pages<!-- slot:ex.c10 /--> — healthy

Not run this pass: #4–#7, #11, #13, #16<!-- slot:ex.notrun /--> (Pass B) · #17, #18 (Pass C).
```

The closing line is not optional. It is what stops a quick pass from reading as a full one.

## Applying fixes

After the report, ask which fixes to apply. Apply only what's confirmed, and **apply each through its owning skill** — schema changes via setup,<!-- slot:fix.capture /--> source processing via ingest<!-- slot:fix.sync /-->. Lint finds and proposes; it does not reimplement the procedures that fix things.

Three findings have exactly one correct repair and should be offered as a single batch rather than one confirmation each: #13 (mirror it), #15's duplicates (collapse to one), and #15's self-edges (remove). Everything else needs judgment and gets asked individually.

**Never hard-delete <!-- slot:delete.what -->a page or edge<!-- /slot:delete.what --> without explicit sign-off** — when in doubt, archive rather than delete<!-- slot:delete.dropped /-->.

## Cadence

Pass A weekly. Pass B monthly or after a burst of ingests. Pass C occasionally, and always before you start relying on this system for something that matters.
<!-- slot:cadence.state /-->

## What this cannot check

Say so when it's relevant, rather than letting a clean report imply more than it earned:

- **Whether the agent followed a procedure.** Lint reads artifacts, not process. An improvised ingest that happened to produce well-formed files passes everything here.
- **Whether `CLAUDE.md` or the skills were altered.** The rulebook's integrity is the invariant the whole design rests on, and nothing in this file verifies it. Version control is the real answer.
- **Whether a fabricated claim cites a real source.** #18 samples; it does not prove. A clean Pass C means the sample was clean.
<!-- slot:cannot.labels /-->
