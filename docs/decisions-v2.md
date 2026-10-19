# v2 decision log

Why the PMS template (v2.x) is shaped the way it is. This is the v2 continuation of `handover/03_decisions.md` (which covers v1.0.1). It was kept in Claude project memory until 2026-10-19 and moved here so it is versioned with the artifact it explains.

**Rule for future changes:** before proposing a structural change, check this file and `handover/03_decisions.md`. If the point was already argued and resolved, don't relitigate it without new field evidence.

## Carried over from v1 (still load-bearing)

- **Graph-over-vector, entirely on Claude.** No external DB or embeddings; the graph *is* the markdown. Claude is both curator and query engine. Accepted cost: not local (content goes to Anthropic), ceiling ~150–200 pages / ~50–100k tokens.
- **Typed edges as per-predicate frontmatter**, not a custom `edges:` block — matches the Obsidian Wikilink Types storage format, so Dataview / Breadcrumbs / Juggl / Graph Link Types read it with zero plugin dependency.
- **Static `CLAUDE.md` + mutable per-PMS files.** The agent can never corrupt its own rulebook; rulebook upgrades propagate by copying one file.
- **`curator_notes`** exists to stop dedup/lint from merging pages a human deliberately kept separate. Respected by tooling, never restated in prose.
- **Query answers are prose-first plus one `Path:` audit line** — compromise between "no metadata narration" (user) and "a bare-prose answer can't be told apart from confabulation" (agent).
- **Visible `meta/`, not hidden `.claude/`.** Field test 01 showed Cowork failed to discover skills in a dot-folder. Don't revert for discoverability-sensitive files.

## v2.0.0 (2026-08-15) — the PMS layer

The template became a Personal Management System: knowledge graph + task layer, top-level rather than embeddable.

- **Renames:** `sources/`→`raw/`, `content/`→`knowledge/`, `meta/index.md`→`meta/GRAPH_INDEX.md`, root `SETTINGS.md`→`meta/SETTINGS.md` + `meta/GRAPH_SCHEMA.md`.
- **Decision 17 (embed as `kb/` in a host project) reversed in full.** `meta/host-snippet.md` removed. No skill writes outside the PMS folder.
- **Folder naming rule.** Folders are named for what they *hold* (`knowledge/`, `tasks/`, `raw/`); `meta/GRAPH_*` files for what they *span*. `content/` was briefly renamed `graph/` and rejected: a folder named after the graph implies its sibling isn't part of it — exactly the assumption that makes an inbound-edge scan miss half the graph. **Do not rename `knowledge/` to `graph/`.**
- **`tasks/` is a lifecycle split, not a membership split.** Traversal set is `knowledge/ ∪ tasks/`, stated three times (CLAUDE.md, query, lint) because a one-folder inbound scan silently returns empty for "what's blocking X" while outbound edges keep working — an invisible bug.
- **Invariant amended, not broken:** "SETTINGS.md is the only mutable rules file" → exactly two mutable *rules* files under `meta/`: `GRAPH_SCHEMA.md` (vocabulary; churns, gets diffed) and `SETTINGS.md` (config; written once).
- **Zero new predicates.** The 14 cover tasks: `part_of`=subtask, `depends_on`=blocked-by, `about`=subject, `introduced_by`=origin. `owner` is a plain string; setup offers promotion to `assigned_to` only if a `person` type is registered.
- **Closed enums:** `status` = open|doing|blocked|done|dropped; `origin` = capture|ingest|query. Rulebook-level, out of scope for setup Mode 2.
- **Capture must stay cheap.** One index read, exact title/alias matches only, never creates stub nodes, never writes to `knowledge/`, one-line report.
- **Skill composition rule (user's):** exactly one skill is authoritative per workflow; skills invoke each other. Ingest calls capture for action items; lint routes every fix through the owning skill. This resolved the capture/ingest router collision.
- **Old trigger phrases kept** ("knowledge base", "KM", "configure o KB") alongside new ones — a rename is not a reason to stop recognizing what the user actually types.
- **Lint exemptions for tasks:** exactly #6 (orphans) and #11 (provenance).

### Self-consistency audit (same day)

Each fix was a rule referencing something that didn't exist:

- **`closed:` date added** — the archive window measured against `updated` was unenforceable (any edit resets it).
- **Archiving removes the index entry** — tasks are the fastest-growing file type; the "one cheap read" depends on a bounded index. Mirrors `raw/archive/`.
- **Capture exempt from the `setup_done` gate** — a 4-question interview before the first "remind me to…" kills a tracker on day one.
- **Next id from the index, not a folder scan** — one read serves id assignment and link resolution. *(Amended in v2.1.0 — see below.)*
- **Ingest passes capture the `raw/archive/` path**, since the source only moves at the last step.

### Lint hardened (2026-08-15..18): 14 → 18 checks, three passes

Driver: lint verified *structure* thoroughly and *truth* not at all.

- Added #15 malformed edge lists, #16 dependency cycles (a `depends_on` ring is a deadlock #14's stale-block can never see), #17 prose narrating machinery, #18 sampled source fidelity (must state sample size).
- **Passes A quick / B full / C fidelity**, each including the prior. A is the default and the only one to schedule — cross-file checks in Cowork mean re-reading every file, so "run weekly" was incompatible with cost.
- **Report ordered by severity** (Broken / Drifting / Housekeeping), not check number.
- **"What this cannot check"** section: process adherence, rulebook integrity, fabrication with a real citation.

## v2.1.0 (2026-10-19) — stabilization

Spec defects found in an evaluation pass; none required new field evidence because each was a contradiction or an arithmetic failure in the text itself.

- **Task ids come from a monotonic counter**, `next_task_id` in `meta/GRAPH_INDEX.md` frontmatter. *Why:* "highest id in the index + 1" combined with "archiving removes the index entry" reissues an id whenever the highest-numbered task is archived, and restarts at T-0001 if every task is archived (the stale-index fallback only fired when `tasks/` was non-empty). The counter only goes up; a folder scan is the fallback only if it is missing or behind.
- **Every wikilink must resolve to a filename.** Knowledge pages are named for their title. Task links are written `[[<file-stem>|<Title>]]`. *Why:* Obsidian resolves links by filename; tasks are date-slugged, so `[[Email Ana about…]]` was an unresolved ghost in Obsidian, Dataview and Graph Link Types — breaking the compatibility the format was chosen for. The piped form keeps date-slugged filenames (sort order, no collisions) and keeps human-readable titles.
  - *Verified against source (2026-10-19), not yet in a live vault:* Obsidian's `LinkCache.link` is the destination and `displayText` the part after `|` (API docs); Dataview splits on the pipe into `path` + `display`; Breadcrumbs 4.22.1 and Juggl 1.5.0 resolve `frontmatterLinks[].link`; Graph Link Types matches Dataview `path` to the core graph's target id. None of them use the display text to resolve. Bare `[[alias]]` links do not resolve in core Obsidian (by design). Live check: `docs/link-format-check/`.
- **Edges into `tasks/archive/` are valid, not dangling.** Lint #5 and #16 resolve targets against the archive; traversal checks the archive before declaring a target missing.
- **`query` skill frontmatter was invalid YAML** (an unquoted `: ` inside the description). Strict parsers reject it, which can drop the skill's trigger description. Now a folded block scalar.
- **`introduced_by` edges to a source** are written `[[<archived-file-stem>|<source title>]]`, and lint #5 resolves against `raw/archive/` — otherwise the new filename-resolution rule would have flagged every ingest-born task.
- **Wording:** "exactly two files the agent may edit" → "exactly two mutable rules files" (the agent edits the index and templates constantly; a literal reading was wrong).

## Still unproven (nothing in v2 has been field-run)

- Whether the `setup_done` gate fires on a fresh PMS's first message, and whether capture's exemption from it works as written.
- Routing precedence between capture and ingest on a genuinely ambiguous message.
- Inbound-scan cost now grows with tasks, mitigated only by the 30-day archive window.
- Whether the agent follows SKILL.md procedures or improvises (discovery is solved; adherence is not).
- Nothing verifies `CLAUDE.md` / `meta/skills/` were not edited. Git is the current answer; a hash marker checked by a validator is the proposed one.

See `field-test-v2.md` for the protocol that closes the first three.

## v3.0.0 (2026-10-19) — Todoist edition

A separate variant, `pms-todoist/`, not a change to `pms/`. Full record: `adr/001-todoist-task-surface.md`. In one line: the files own structure, Todoist owns execution state, the `PMS: T-0042` footer is the join key, `sync` is the only skill that touches Todoist, and `plan` is the new pipeline-manager skill. Field test: `field-test-v3-todoist.md`.
