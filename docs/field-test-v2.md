# Field test 05 — first real run of v2 (core behaviours)

> Since v2.4.0 the template includes Todoist. This protocol covers the core: capture, ingest, query, archive and lint. Run it with the Todoist connector **off**, so tasks stay pending push; at setup, decline the connection in Step 0. Then run `field-test-todoist.md` for the Todoist side.

Nothing in v2 has been run against real material. This protocol tests the behaviors v2 depends on that only a live session can confirm. It is a run of the *template*, so do it **outside this repository**, in a scratch copy, and bring the notes back here.

## Setup

1. Copy `pms/` to a scratch location, e.g. `D:\scratch\pms-ft05\`. Do not run it inside this repo — the builder `CLAUDE.md` here deliberately suppresses curator behavior.
2. In Cowork: **New project → Use an existing folder →** the scratch copy. Paste the project blurb from `pms/README.md` § Quick start. Memory on.
3. Have ready: one real meeting note or transcript with at least two action items and one named person, and one article on the same subject.
4. Keep a notes file open (`docs/test-notes/ft05.md` in this repo). For each step record: what you sent, what happened, **pass / fail / partial**, and anything surprising.

## Steps and pass criteria

| # | Send / do | Pass if | Tests |
|---|---|---|---|
| 1 | First message, nothing else: *"remind me to call Ana about the renewal"* | A task file `tasks/YYYY-MM-DD-*.md` with `id: T-0001`; index has the piped-link line; `next_task_id: T-0002`; **no** stub page in `knowledge/`; then an offer to configure, not an interview first | Capture's exemption from the setup gate; counter |
| 2 | Accept setup; decline Todoist at Step 0, then answer the interview (Q5 and Q6 are skipped); pick a content language **different** from the one you chat in | `meta/SETTINGS.md` has Purpose, Language, `setup_done: true`; types land in `GRAPH_SCHEMA.md`; it did not touch `CLAUDE.md` | Setup Mode 1; whether AskUserQuestion renders or falls back |
| 3 | Drop the meeting note in `raw/` and say *"ingest this"* | Source stamped and moved to `raw/archive/`; knowledge pages named for their titles; action items became tasks via capture with `origin: ingest`, `sources:` = the archived path, consecutive ids, counter advanced; report lists them | Ingest → capture composition; archive-path handoff |
| 4 | *"here's an article about X, and remind me to follow up with Ana"* (paste text) | It runs ingest, and ingest hands the follow-up to capture. It does not run the two independently, and it does not ask which you meant | Routing precedence on a mixed message |
| 5 | *"what's blocking <project or person from the note>?"* | Answer finds tasks pointing *at* the page (inbound edges from `tasks/`); prose answer + `Path:` line | Two-folder inbound scan |
| 6 | Mark one task done; edit `closed:` by hand to 40 days ago; ask *"archive old tasks"* | Moved to `tasks/archive/`; index entry removed; **`next_task_id` unchanged** | Archive flow |
| 7 | Capture one more task | Gets the next counter value, **not** a reused id | The v2.0.0 id-reuse bug stays fixed |
| 8 | Make a task `depends_on` the archived one (by hand if needed); say *"lint"* | Pass A runs by default; report states folders scanned and the "not run this pass" line. Ask for *"full lint"*: Pass B does **not** report the edge into `tasks/archive/` as dangling | Lint passes; archive-target resolution |
| 9 | Open the scratch folder as an Obsidian vault | Edges to tasks draw as resolved links (no ghost nodes); Dataview `TABLE status, due FROM "tasks"` works | Piped-link fix |

## Also record

- **Adherence:** in at least one step, ask *"which SKILL.md did you follow?"* Note whether it cites the file and whether what it did matches the steps.
- **Cost:** a rough idea of how long and how heavy each operation felt, capture in particular.
- **Prose leaks:** any node body or answer that talks about pages, edges or fields instead of the subject.

## After the run

Bring the notes back here and continue the usual loop: fix the spec rather than the symptom (in `ext/`, or in brkl-kb for anything that isn't about tasks or Todoist — see `adr/002-kb-core-split.md`), rebuild, record the *why* in `decisions-v2.md`, run a stale-reference sweep, bump the version, tag.
