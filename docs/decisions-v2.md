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

## v2.2.0–v2.4.0 (2026-10-19) — Todoist as the task surface

v2.2.0 introduced it as a separate variant. v2.3.0 moved connector authorization and sync scheduling into setup. v2.4.0 (Fernando's decision) made it the **only** template at `pms/`, so the files-only PMS survives only in git history (tag `v2.1.0`). Full record: `adr/001-todoist-task-surface.md`. In one line: the files own structure, Todoist owns execution state, the `PMS: T-0042` footer is the join key, `sync` is the only skill that touches Todoist, and `plan` is the new pipeline-manager skill. Field test: `field-test-todoist.md`.
- **2026-10-19:** Mapping re-examined once the Free-plan cap stopped being a constraint. Fernando kept area → project / project → section; the costs he accepted and the triggers for revisiting are in ADR-001's amendment.
- **2026-10-19:** Versioning fixed. kbcurator = v1.x (tag `v1.1.0`); everything PMS = v2.x. The earlier v3.0.0 / v3.1.0 tags were never pushed; they became v2.2.0 / v2.3.0. The Todoist edition became the only template in v2.4.0.

## v2.5.0 (2026-10-19) — full-review hardening

A file-by-file review of the template, then a second pass for system-level gaps. Contradictions fixed:

- "Never writes outside this folder" was false once Todoist and scheduled tasks existed. It now names exactly those two exits.
- Setup examples suggested registering a `project` type, which already ships.
- Lint #14 said six sub-checks but had seven.
- Lint #2 would have flagged `entity` and `concept` for having no template.
- Lint #20's "foreign label damage" was uncheckable, because lint has no record of earlier labels. It is now a write-time guard in sync, and is listed under what lint cannot check.
- Sync Mode 3 didn't cover the account read that setup depends on.
- `priority` was synced but missing from the task schema.
- A Pull read only the area projects, so completions of tasks pushed to the Inbox were never seen.

Behaviour added:

- No Todoist push before setup confirms the account; setup pushes those pending tasks when it finishes.
- Placement falls back to an `about` edge pointing at a project or area.
- A task that reaches an area but no project goes in the area's project with no section.
- Terminal states are pushed bottom-up, and dropping a group drops its children first. Completing a Todoist parent cascades, so the wrong order would turn dropped children into `done`.
- Groups close as `dropped` when every child was dropped.
- Deletion is detected by fetching the task id, not inferred from absence.
- Sections created on the phone are adopted as `project` nodes.
- Setup Q5 states what binding implies (existing sections and tasks get adopted) and offers a first sync.
- A chat edit to a Todoist-owned field (due date, title, priority) is pushed; Todoist's value wins only on a pull.
- The index is re-read immediately before every write, because a scheduled sync and a chat session can run at once.

## v2.6.0 (2026-10-20) — one Todoist bucket per PMS

Fernando's decision. A PMS is usually about one subject, so by default it lives in one Todoist project — a new one named after it, unless the user picks an existing one. Everything else in the account is left alone. Managing several projects (`multiple` mode) happens only on an explicit ask at setup. Footer `PMS: <pms-id>/T-0042` so several PMSes can share an account. Inbox triage removed. Full record: ADR-001, Amendment 2.
- **2026-10-20:** A mock bucket ("PMS Demo", since archived) showed that Todoist returns an uncompletable header's name with a `* ` prefix. Sync now ignores that prefix when comparing titles; otherwise every pull would report each phase as renamed. Lint checks the marker in both directions.
- **2026-10-20:** Repository moved out of the old `kbcurator/output/` folder to its own root (`brkl-pms/`), and the GitHub repo was renamed `kbcurator` → `brkl-pms` (GitHub redirects the old URL). No template change.

## v2.7.0 (2026-11-13) — built on the brkl-kb core

Fernando's decision: the knowledge base becomes its own template again, in its own repository (**brkl-kb**, v1.2.0), and the PMS depends on it instead of containing it. The driver: projects that need only a knowledge base had nowhere to start one, because since v2.4.0 the only template required Todoist. Full record: `adr/002-kb-core-split.md`; the KB side is in brkl-kb `docs/decisions-kb.md`.

- **Split at the source, combined at build time.** brkl-kb's `core/` carries slots. This repository vendors it at a tag (`vendor/kb/`, hash-pinned), fills the slots from `ext/fills/`, adds `ext/files/`, and `tools/build.py` writes `pms/`. The built template is one self-contained folder, as before, so the agent never deals with composition. That matters most for the traversal-set rule (`knowledge/` ∪ `tasks/`), which fails silently if it's wrong.
- **A pure refactor.** Every PMS-only passage of v2.6.1 was cut verbatim into a fill. The v2.7.0 `pms/` is byte-identical to v2.6.1's apart from the version line, which is now generated from `ext/extension.json`. This was the acceptance test, and it passed.
- **Two repositories, not one** (Fernando's call over a monorepo recommendation): the KB gets its own identity and releases. The accepted cost is that a new slot means a brkl-kb release, then a vendor bump here.
- **Conventions changed.** The version lives in `ext/extension.json`, not `pms/README.md`. `pms/` and `vendor/kb/` are never edited by hand (`tools/build.py --check`). A/B siblings are still hand-edited copies of `pms/`; the winner gets ported into `ext/`.
- **Left as it was, on purpose, to keep the build identical:** the fixed task schema and Todoist mapping still live in the mutable `meta/GRAPH_SCHEMA.md`, which means a rulebook upgrade can't propagate by copying static files. And 180 fine-grained slots. Both are next-pass work (ADR-002 § Consequences).

## v2.8.0 (2026-11-17) — self-contained again

Fernando's decision, reversing v2.7.0: the PMS and the knowledge base are independent projects, so `pms/` is no longer built from an external core. Full record: `adr/003-self-contained-template.md`.

- `vendor/`, `ext/` and `tools/` removed. `pms/` is the template and the only copy, edited directly: no build, no check, no pin.
- `pms/` is unchanged apart from its version line, so its text is still v2.6.1's. Nothing in it ever referred to the external core.
- Conventions restored: bump the version in `pms/README.md` and tag. A/B variants are hand-edited `pms-*/` siblings.
- The builder docs (`CLAUDE.md`, `README.md`, `field-test-v2.md`, `handover/000_READ_FIRST.md`) are back to their v2.6.1 wording, plus ADR-003 and a self-containment invariant.
- Why the reversal is right on its own terms: the build existed only so two templates could share text. With sharing ruled out it had no job left, and it added a step to every change.

## v2.8.1 (2026-11-17) — fixes ported from brkl-kb v1.3.1

All five graph-rule fixes from brkl-kb's stale-reference audit applied here too; PMS had every one of the bugs.

- **Ingest now updates the index before archiving the source (steps 10 and 11 swapped).** The "if you can't finish" section rested on archiving being the last act, but the index update ran after it. An interruption between the two left a source archived, so it looked done, while its knowledge pages were missing from the index. Now a source that still looks pending is the only sign of an unfinished ingest, which is the state the recovery rule already assumes. Step 8's "use the archived path" note now points at step 11.
- **Lint check numbers are written into the text, not as Markdown list markers.** Out-of-sequence markers (1, 2, 3, 8, … 19; 4, … 20) are renumbered by any CommonMark renderer, so in Obsidian or on GitHub the numbers stopped matching the pass table and severity bands. The agent reads raw text and wasn't affected; humans were.
- **Lint #17 cites the right source.** It credited `CLAUDE.md` with naming the "Page X … through edge W" failure mode; that example lives in the query skill, and `CLAUDE.md` states the rule (§ Role).
- **Lint scope and example report match the rules.** Scope now names `raw/archive/` for #18's source re-reads; the Pass A example lists `raw/` as scanned, since #8 and #12 scan it.
- **Default `entity`/`concept` types list the seed's bookkeeping fields** (`created`, `updated`, `curator_notes`). Lint #2 compares fields against § Nodes, so the shorter list invited false drift reports.
