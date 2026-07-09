---
name: lint
description: Run a health check on the knowledge base and propose fixes. Use this whenever the user says "lint", "check my knowledge base", "revise o KM", "what's broken", "o que está quebrado", "clean up the graph", "run maintenance", or wants a periodic (e.g. weekly) health pass. Trigger it proactively if the user mentions the KB feels messy, has dead links, or has drifted. It finds unregistered types/predicates, settings drift, untyped links to promote, dangling edges, orphan pages, contradictions, inbox mismatches, and index drift.
---

# Lint

The health check that substitutes for the guarantees an external database would give you. It reports and proposes — it does not change or delete files without explicit confirmation.

**Prerequisite:** `CLAUDE.md` — operate by it. The **Nodes** and **Edges** sections in `SETTINGS.md` are the authority for valid node types and edge fields.

## Checks

Run all of these across `content/` (and `sources/` for #8):

1. **Missing or unregistered node types.** Any node with no `type` at all, or whose `type` is not in `SETTINGS.md` § Nodes. Propose registering it (via the setup skill) or reassigning it to an existing type.
2. **Settings drift.** A registered type whose template in `meta/templates/` is missing, or whose fields disagree with its entry in `SETTINGS.md` § Nodes. Propose aligning them. Also flag orphan templates (a `meta/templates/<type>.md` with no matching entry in § Nodes), and flag if `setup_done` is `true` in `SETTINGS.md` but its Purpose is still unset.
3. **Invalid predicates.** Any edge field whose name is not in `SETTINGS.md` § Edges. Propose mapping it to an allowed predicate, or registering a new one via the setup skill.
4. **Untyped links to promote.** Prose `[[wikilinks]]` (or `see_also` entries) that recur but have no matching predicate field. Propose a predicate to promote each — or confirm it stays `see_also`.
5. **Dangling edges.** Predicate-field wikilinks whose target page doesn't exist. Offer to create a stub or fix the target.
6. **Orphan pages.** Pages with no inbound and no outbound typed edges. Surface for linking or archiving. Respect `curator_notes` before proposing any merge or removal.
7. **Contradictions.** `contradicts` edges and any conflicting facts across pages. List for resolution.
8. **Inbox state.** Pending sources = files in the root of `sources/`; list them to run ingest on. Cross-check flag vs location: a file in the root with `ingested: true` should be archived (propose the move); a file in `sources/archive/` with `ingested: false` needs investigation.
9. **Index drift.** Pages on disk missing from `meta/index.md`, and index entries pointing to pages that don't exist.
10. **Scale watch.** Rough page/token count; warn if approaching the ~150–200 page ceiling where an external index becomes worth adding.

## Report format

Group by check, with counts and concrete proposed fixes:

```
KB Lint — <date>

1. Missing/unregistered types (N): [[A]] has type `widget` → register or reassign?
2. Settings drift (N): type `person` has no meta/templates/person.md → create?
3. Invalid predicates (N): `relates_to` in [[C]] → map to `contrasts_with`?
4. Untyped links (N): [[A]] in [[B]] → promote as `uses`?
5. Dangling edges (N): [[C]] uses [[Missing]] → create stub?
6. Orphan pages (N): [[D]] → link or archive?
7. Contradictions (N): [[E]] vs [[F]] on <fact>
8. Inbox (N pending): sources/2026-07-08-note.md · 1 mismatch: sources/old-note.md ingested but not archived
9. Index drift: 2 pages missing from index, 1 stale entry
10. Scale: ~40 pages — healthy
```

## Applying fixes

After the report, ask which fixes to apply. Apply only what's confirmed. **Never hard-delete a page or edge without explicit sign-off** — when in doubt, archive rather than delete.

## Cadence

Suggest running weekly, or after a burst of ingests.
