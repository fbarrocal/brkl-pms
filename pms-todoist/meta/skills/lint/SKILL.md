---
name: lint
description: Run a health check on the Personal Management System and propose fixes. Use this whenever the user says "lint", "check my PMS", "check my knowledge base", "revise o KM", "what's broken", "o que está quebrado", "clean up the graph", "run maintenance", or wants a periodic (e.g. weekly) health pass. Also use for the deeper passes — "full lint", "deep lint", "check my sources", "is any of this made up", "verifique as fontes". Trigger it proactively if the user mentions the PMS feels messy, has dead links, or has drifted. It finds unregistered types/predicates, settings drift, duplicate and dangling edges, dependency cycles, untyped links to promote, orphan pages, contradictions, inbox mismatches, index drift, task hygiene problems, prose that narrates machinery, and pages whose claims their sources don't support.
---

# Lint

The health check that substitutes for the guarantees an external database would give you. It reports and proposes — it does not change or delete files without explicit confirmation.

**Prerequisite:** `CLAUDE.md` — operate by it. `meta/GRAPH_SCHEMA.md` is the authority for valid node types, task fields, enum values, and edge fields; `meta/SETTINGS.md` is the authority for purpose, language, and conventions.

## Scope

Run the checks across **`knowledge/` and `tasks/` both** (`raw/` for #8 and #12; `tasks/archive/` for #14, and as a valid link target for #5, #9 and #16). Scoping a check to `knowledge/` alone is the single easiest mistake here: it makes every task edge look like it doesn't exist, so dangling-edge and symmetric-edge checks come back clean while the task layer quietly rots. **Say in the report which folders you actually scanned** — a clean result from a half-scan is indistinguishable from a clean result, and that is the worst thing a health check can produce.

**Tasks are exempt from two checks, and only two.** #6 (orphans) — a task with no edges is a perfectly normal reminder, not a defect. #11 (provenance) — a task's provenance is its `origin` field, and only an `origin: ingest` task carries `sources:`. `area` and `project` nodes are also exempt from #11, because they record an intent rather than something a source said. Tasks are subject to every other check exactly like knowledge pages.

## Three passes

The checks differ enormously in cost, and a health check nobody runs is worth nothing. Pick a pass; each one includes the ones before it.

| Pass | Cost | Cadence | Contains |
|---|---|---|---|
| **A — Quick** | frontmatter only, no cross-file resolution | weekly, and after any burst of captures | 1, 2, 3, 8, 9, 10, 12, 14, 15, 19 |
| **B — Full** | resolves edges across every file, both folders; one Todoist read per area | monthly, or after a burst of ingests | A + 4, 5, 6, 7, 11, 13, 16, 20 |
| **C — Fidelity** | re-reads source material and judges prose | occasionally, and before you rely on this system for something that matters | B + 17, 18 |

**Pass A is the default.** Run it when the user just says "lint". Offer B if A finds edge or index problems, since those usually travel with the ones only B can see. Offer C when the user asks whether the content is trustworthy, before a hand-off, or when it has been many ingests since the last one. Never run C silently — it is expensive, and the user should know they asked for it.

If a pass is running long, **stop and report what you have**, naming the checks you completed and the ones you skipped. A partial report that says so is useful; a partial report presented as complete is a lie about the system's health.

## Checks

### Pass A — structure and state

1. **Missing or unregistered node types.** Any node with no `type` at all, or whose `type` is not in `meta/GRAPH_SCHEMA.md` § Nodes. Propose registering it (via the setup skill) or reassigning it to an existing type. A file in `tasks/` whose type is not `task`, or a `type: task` file sitting in `knowledge/`, is a misfile — propose moving it.
2. **Schema and settings drift.** A registered type whose template in `meta/templates/` is missing, or whose fields disagree with its entry in `meta/GRAPH_SCHEMA.md` § Nodes. Propose aligning them. Also flag orphan templates (a `meta/templates/<type>.md` with no matching entry in § Nodes), and flag if `setup_done` is `true` in `meta/SETTINGS.md` but its Purpose or Language is still unset. Also flag content whose titles or prose are plainly not in the recorded Language — mixed-language vaults are a slow drift that only shows up once they are expensive to fix.
3. **Invalid predicates.** Any edge field whose name is not in `meta/GRAPH_SCHEMA.md` § Edges. Propose mapping it to an allowed predicate, or registering a new one via the setup skill.
8. **Inbox state.** Pending sources = files in the root of `raw/`; list them to run ingest on. Cross-check flag vs location: a file in the root with `ingested: true` should be archived (propose the move); a file in `raw/archive/` with `ingested: false` needs investigation.
9. **Index drift.** Pages and tasks on disk missing from `meta/GRAPH_INDEX.md`, index entries pointing to files that don't exist, **alias drift** (an entry whose listed aliases disagree with the page's own `aliases` field), **status drift** and **due drift** (a task entry whose listed status or due date disagrees with the file), and **link drift** (a task entry whose link stem is not the task's actual filename). Alias drift is the quiet one: it makes dedup and name lookup miss, which is how duplicate nodes get created; due drift is the same failure one layer down, turning query's one-read triage into a folder scan. An index entry pointing at a file that no longer exists is also this system's only detector for a page that was deleted rather than dropped — treat it as that, not as a typo. **Two deliberate exemptions, not findings:** tasks in `tasks/archive/` are *supposed* to be absent from the index, and sources in `raw/archive/` were never in it — do not report either as missing.
10. **Scale watch.** Rough page/token count; warn if approaching the ~150–200 knowledge-page ceiling where an external index becomes worth adding. Count tasks separately — a large open-task count is a triage problem, not a scale problem, but a large *terminal* count in the root of `tasks/` is check #14's business.
12. **Unstamped sources.** Files in `raw/` missing the source frontmatter block, and binaries with no `<filename>.md` sidecar. Propose stamping them (via ingest) so they can be processed.
14. **Task hygiene.** Six sub-checks, all cheap, all reading `tasks/` and `tasks/archive/`:
    - **Invalid enum value.** A `status` outside `open` / `doing` / `blocked` / `done` / `dropped`, or an `origin` outside `capture` / `ingest` / `query` / `plan`. There is no "close enough" here — propose the correct value.
    - **Unexplained blocked.** `status: blocked` with neither a `depends_on` edge nor a `notes` line. A task blocked on nothing recorded is just an open task pretending to be handled.
    - **Stale block.** `status: blocked` whose every `depends_on` target is `done` or no longer exists. This is the finding that earns the check: the thing it waited for finished and nobody noticed.
    - **Duplicate or reused id.** Two tasks sharing an `id` — check `tasks/` and `tasks/archive/` together. Propose reassignment; never renumber silently.
    - **Counter behind.** `next_task_id` in `meta/GRAPH_INDEX.md` missing, or not above the highest `id` in `tasks/` ∪ `tasks/archive/`. The next capture will reissue an id. Propose setting it to that highest id plus one.
    - **`closed` disagrees with `status`.** A terminal task with no `closed` date (it can never be archived — the window has nothing to measure from), or a non-terminal task still carrying one (it was reopened and the date wasn't cleared). Both are one-line fixes and both are invisible until the archive pass silently skips or grabs the wrong task.
    - **Archivable.** Tasks whose `closed` date is older than the window in `meta/SETTINGS.md` § Conventions, still in the root of `tasks/`. Propose moving them to `tasks/archive/` — the fix is capture's Mode C, which also removes their index entries. Never archive a non-terminal task, and never propose deleting one.
15. **Malformed edge lists.** Read each file's own predicate fields; no cross-file work needed:
    - **Duplicate entry.** The same wikilink appearing twice in the same predicate field. Edge fields are **sets**, and `CLAUDE.md` names the cause outright: an ingest that blind-appends instead of unioning. A corrected source re-ingested three times gives you an edge listed three times, which silently triples that relationship's weight in every traversal and every count. The repair is always "collapse to one" — no judgment needed, so propose them all in one go.
    - **Self-referential edge.** A page listing its own filename stem, title, or alias in one of its own edge fields. Always a bug; a page is not `part_of` itself.
    - **Empty or malformed field.** A predicate field present but empty, or holding a bare string instead of a `"[[wikilink]]"`. Both read as "no edge" to a traversal while looking like an edge to a human.

19. **Todoist bookkeeping (local).** No Todoist call — files only:
    - **Pending push.** Task files with no `todoist_id`. A few right after an offline capture is normal; anything older than a day means sync isn't running. Fix: sync Mode 1, "all pending".
    - **Duplicate `todoist_id`.** Two files claiming one Todoist task — always a bug, usually from an interrupted push. Report both files; never pick one silently.
    - **Unbound structure.** An `area` with no `todoist_project_id`, or a `project` with no `todoist_section_id` but with pushed tasks under it.
    - **Area count over the plan.** More `area` nodes than `meta/SETTINGS.md` § Todoist allows Todoist projects.
    - **Stale sync.** `todoist_synced_at` empty while pushed tasks exist, or older than the warning age in settings.
    - **Stale display text.** A task link whose text after `|` no longer matches the target's title in the index (the title was edited in Todoist). Housekeeping only — the link still resolves.

### Pass B — the graph itself

4. **Untyped links to promote.** Prose `[[wikilinks]]` (or `see_also` entries) that recur but have no matching predicate field. Propose a predicate to promote each — or confirm it stays `see_also`. **Tasks are the biggest source of these by design** — capture deliberately leaves unrecognized mentions as plain links rather than inventing stub nodes, so a recurring one here is usually a node worth creating, not a link worth typing. This check produces the most volume and the least urgency of any in the file: report it as a count with the top few examples, never as a full list.
5. **Dangling edges.** Predicate-field wikilinks that resolve to no file. Resolve by **filename** — the part of the link before any `|` — against `knowledge/`, `tasks/`, **`tasks/archive/`**, and `raw/archive/` (an `introduced_by` edge may point at an ingested source); a link to an archived file is valid, not dangling. A bare task title (no stem) is dangling even though a task has that title: Obsidian and Dataview cannot follow it. Offer to create a stub, or rewrite the link to the form the index lists. Check both directions across `knowledge/` and `tasks/`.
6. **Orphan pages.** **Knowledge pages only** — pages in `knowledge/` with no inbound and no outbound typed edges. Surface for linking or archiving. Respect `curator_notes` before proposing any merge or removal. Skip `tasks/` entirely: an unlinked task is normal.
7. **Contradictions.** `contradicts` edges and any conflicting facts across pages. List for resolution.
11. **Provenance gaps.** **Knowledge pages** with an empty or missing `sources:` field, `sources:` entries pointing at a file that isn't in `raw/`, and **broken round-trips** — a page listing a source that doesn't list it back in `touches:`, or vice versa. `touches:` may name task files as well as knowledge pages, so resolve it against both folders; a source that produced action items and lists none is an ingest that stopped halfway. An unsourced page is the *shape* a fabricated one takes — but only the shape. This check cannot see a fabricated page that cites a real source; that is #18's job, and #11 passing is not evidence of truth.
13. **One-sided symmetric edges.** For each predicate marked **(symmetric)** in `meta/GRAPH_SCHEMA.md` § Edges, a page carrying it must appear in the same field on the page it points at. Report any that don't. This is the one check whose fix needs no judgment — the repair is always "mirror it" — so propose applying all of them in one go rather than asking page by page. It matters most for `contradicts`: an unmirrored conflict is invisible from the page being challenged.
16. **Dependency cycles.** Walk `depends_on` and `part_of` across both folders, following targets into `tasks/archive/` where they lead, and report any cycle — A depends on B depends on A, or a task that is `part_of` its own descendant. A `depends_on` cycle is a deadlock: every task in the ring is legitimately `blocked`, none can ever move, and **check #14's stale-block will never fire** because no target is `done`. That combination is why this check exists — the cycle is invisible to every other check in the file and looks like normal blocked work in every task list. Report the full ring, not one member, and let the user decide which edge is wrong; never break a cycle by picking an edge yourself. Bound the walk and say so if you stopped early.

20. **Todoist drift (remote).** Ask sync for a read of each managed area (Mode 3, one call per area) and compare:
    - **Orphans in Todoist.** A task inside a managed section or project with no `PMS:` footer — sync will adopt it on the next pull; report it here only if it's older than the last sync, because that means adoption is failing.
    - **Orphans in the files.** A `todoist_id` in the root of `tasks/` that Todoist doesn't have, active or completed. Archived tasks are exempt — Todoist may have aged out their completion records.
    - **State disagreement.** Done in one, open in the other; `pms-blocked` present while every dependency is finished, or missing while one isn't; a grouping task that is completable in Todoist.
    - **Foreign label damage.** A task that lost user labels it had before a sync — evidence that a label write replaced instead of merging. Report it first; it destroys user data.
    Fixes go through sync. Lint never writes to Todoist itself.

### Pass C — is the content true

These two read material rather than metadata. They are the only checks that can catch the failure this whole system is most exposed to: an agent that wrote something plausible and unsupported. Everything in passes A and B verifies that the filing is tidy; nothing there opens a folder to see whether the contents are right.

17. **Prose that narrates machinery.** Read node and task bodies. `CLAUDE.md` requires the prose to speak about the things themselves — "Page X relates to Page Y through edge W" is the named failure mode. Flag bodies that narrate pages, edges, fields, ingests, or curatorial decisions; flag curatorial reasoning that belongs in `curator_notes`; flag process commentary that belongs in a chat report. Quote the offending sentence and propose the rewrite — this is one where showing beats describing. It is also the check most likely to find drift after a long run of ingests, because meta-commentary creeps in one sentence at a time.
18. **Source fidelity (sampled).** For a sample of knowledge pages, re-read the sources in their `sources:` field and check that the page's claims are actually supported. Flag: claims present in the page and absent from every cited source; figures, dates, and names that disagree with the source; and confident phrasing where the source hedged.
    - **Sample, and say so.** Take five pages, or 10% of `knowledge/`, whichever is larger. Prioritise the most recently written, the ones with the most edges (a wrong page with many edges poisons the most traversals), and any page whose sources were re-ingested. **State the sample size and which pages you checked** — "sampled 8 of 62 pages" is a finding; "sources look fine" is a false clean bill of health.
    - **A miss here is the most serious thing lint can find.** It means the system produced knowledge that no material supports, which is the one failure that makes everything downstream untrustworthy. Report it first, above everything else, regardless of count.
    - Do not rewrite the page yourself. Report the unsupported claim, cite the source, and let the user decide — the correct repair is sometimes "the page is wrong", sometimes "the source list is incomplete", and you cannot tell which.

## Report format

**Order by severity, not by check number.** A report that opens with rare structural nits and buries an unsupported claim on line 40 trains the user to skim it, and a skimmed health check is a decorative one. Three bands, always in this order, and omit any band that is empty:

- **Broken** — produces wrong answers right now: #18, #20's foreign label damage, #16, #5, #13, #15, #14's invalid-enum, stale-block and counter-behind, #19's duplicate `todoist_id`, #20's state disagreement, #3, #7.
- **Drifting** — will produce wrong answers soon: #9, #11, #2, #1, #12, #8, #14's `closed` mismatch, #17, #19's pending push, unbound structure, area count and stale sync, #20's orphans.
- **Housekeeping** — taste and volume: #4, #6, #10, #14's archivable, #19's stale display text.

```
PMS Lint — <date> — Pass A (quick)
Scanned: knowledge/ (62), tasks/ (18). Not scanned: tasks/archive/, source bodies.

BROKEN (4)
  #15 Duplicate edges (3): [[A]] lists [[B]] twice under `uses` → collapse all?
  #14 Invalid status (1): T-0031 has status `waiting` → not in the enum; which of the five?

DRIFTING (5)
  #9  Index drift: 2 pages missing, 1 alias mismatch, 1 task due-date mismatch
  #2  Settings drift: type `person` has no meta/templates/person.md → create?

HOUSEKEEPING (2)
  #4  Untyped links (14): most common — [[Acme]] in 4 tasks → create a node?
  #10 Scale: ~62 knowledge pages, 18 open tasks — healthy

Not run this pass: #4–#7, #11, #13, #16 (Pass B) · #17, #18 (Pass C).
```

The closing line is not optional. It is what stops a quick pass from reading as a full one.

## Applying fixes

After the report, ask which fixes to apply. Apply only what's confirmed, and **apply each through its owning skill** — schema changes via setup, task changes and archival via capture, source processing via ingest. Lint finds and proposes; it does not reimplement the procedures that fix things.

Three findings have exactly one correct repair and should be offered as a single batch rather than one confirmation each: #13 (mirror it), #15's duplicates (collapse to one), and #15's self-edges (remove). Everything else needs judgment and gets asked individually.

**Never hard-delete a page, task, or edge without explicit sign-off** — when in doubt, archive rather than delete, and a task is dropped, never deleted.

## Cadence

Pass A weekly. Pass B monthly or after a burst of ingests. Pass C occasionally, and always before you start relying on this system for something that matters.

Two checks specifically reward a regular cadence rather than a thorough one: #14's stale-block and #16's cycles both find *state that changed while nobody was looking*, and both get worse the longer they sit. Everything else finds mess, which waits patiently.

## What this cannot check

Say so when it's relevant, rather than letting a clean report imply more than it earned:

- **Whether the agent followed a procedure.** Lint reads artifacts, not process. An improvised ingest that happened to produce well-formed files passes everything here.
- **Whether `CLAUDE.md` or the skills were altered.** The rulebook's integrity is the invariant the whole design rests on, and nothing in this file verifies it. Version control is the real answer.
- **Whether a fabricated claim cites a real source.** #18 samples; it does not prove. A clean Pass C means the sample was clean.
