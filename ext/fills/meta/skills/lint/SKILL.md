<!-- PMS fills for core meta/skills/lint/SKILL.md. Only the fill blocks count; text between them is ignored. -->

<!-- fill:desc.tasks --> task hygiene problems, Todoist bookkeeping and drift,<!-- /fill:desc.tasks -->

<!-- fill:prereq.tasks -->node types, task fields, enum values, and edge fields<!-- /fill:prereq.tasks -->

<!-- fill:prereq.conventions -->purpose, language, and conventions<!-- /fill:prereq.conventions -->

<!-- fill:scope -->
Run the checks across **`knowledge/` and `tasks/` both** (`raw/` for #8, #11 and #12; `tasks/archive/` for #14, and as a valid link target for #5, #9 and #16; `raw/archive/` as a valid link target for #5; Todoist, through sync's read-only Mode 3, for #20 only). Scoping a check to `knowledge/` alone is the single easiest mistake here: it makes every task edge look like it doesn't exist, so dangling-edge and symmetric-edge checks come back clean while the task layer quietly rots. **Say in the report which folders you actually scanned** — a clean result from a half-scan is indistinguishable from a clean result, and that is the worst thing a health check can produce.
<!-- /fill:scope -->

<!-- fill:exemptions -->
**Tasks are exempt from two checks, and only two.** #6 (orphans) — a task with no edges is a perfectly normal reminder, not a defect. #11 (provenance) — a task's provenance is its `origin` field, and only an `origin: ingest` task carries `sources:`. `area` and `project` nodes are also exempt from #11, because they record an intent rather than something a source said. Tasks are subject to every other check exactly like knowledge pages.

<!-- /fill:exemptions -->

<!-- fill:pass-a.captures -->, and after any burst of captures<!-- /fill:pass-a.captures -->

<!-- fill:pass-a -->, 14, 15, 19<!-- /fill:pass-a -->

<!-- fill:pass-b.cost -->, both folders; one Todoist read per area<!-- /fill:pass-b.cost -->

<!-- fill:pass-b.checks -->, 16, 20<!-- /fill:pass-b.checks -->

<!-- fill:c1.misfile --> A file in `tasks/` whose type is not `task`, or a `type: task` file sitting in `knowledge/`, is a misfile — propose moving it.<!-- /fill:c1.misfile -->

<!-- fill:c9 -->
9. **Index drift.** Pages and tasks on disk missing from `meta/GRAPH_INDEX.md`, index entries pointing to files that don't exist, **alias drift** (an entry whose listed aliases disagree with the page's own `aliases` field), **status drift** and **due drift** (a task entry whose listed status or due date disagrees with the file), and **link drift** (a task entry whose link stem is not the task's actual filename). Alias drift is the quiet one: it makes dedup and name lookup miss, which is how duplicate nodes get created; due drift is the same failure one layer down, turning query's one-read triage into a folder scan. An index entry pointing at a file that no longer exists is also this system's only detector for a page that was deleted rather than dropped — treat it as that, not as a typo. **Two deliberate exemptions, not findings:** tasks in `tasks/archive/` are *supposed* to be absent from the index, and sources in `raw/archive/` were never in it — do not report either as missing.
<!-- /fill:c9 -->

<!-- fill:c10.tasks --> Count tasks separately — a large open-task count is a triage problem, not a scale problem, but a large *terminal* count in the root of `tasks/` is check #14's business.<!-- /fill:c10.tasks -->

<!-- fill:c14 -->
14. **Task hygiene.** Seven sub-checks, all cheap, all reading `tasks/` and `tasks/archive/`:
    - **Invalid enum value.** A `status` outside `open` / `doing` / `blocked` / `done` / `dropped`, or an `origin` outside `capture` / `ingest` / `query` / `plan`. There is no "close enough" here — propose the correct value.
    - **Unexplained blocked.** `status: blocked` with neither a `depends_on` edge nor a `notes` line. A task blocked on nothing recorded is just an open task pretending to be handled.
    - **Stale block.** `status: blocked` whose every `depends_on` target is `done` or no longer exists. This is the finding that earns the check: the thing it waited for finished and nobody noticed.
    - **Duplicate or reused id.** Two tasks sharing an `id` — check `tasks/` and `tasks/archive/` together. Propose reassignment; never renumber silently.
    - **Counter behind.** `next_task_id` in `meta/GRAPH_INDEX.md` missing, or not above the highest `id` in `tasks/` ∪ `tasks/archive/`. The next capture will reissue an id. Propose setting it to that highest id plus one.
    - **`closed` disagrees with `status`.** A terminal task with no `closed` date (it can never be archived — the window has nothing to measure from), or a non-terminal task still carrying one (it was reopened and the date wasn't cleared). Both are one-line fixes and both are invisible until the archive pass silently skips or grabs the wrong task.
    - **Archivable.** Tasks whose `closed` date is older than the window in `meta/SETTINGS.md` § Conventions, still in the root of `tasks/`. Propose moving them to `tasks/archive/` — the fix is capture's Mode C, which also removes their index entries. Never archive a non-terminal task, and never propose deleting one.
<!-- /fill:c14 -->

<!-- fill:c19 -->
19. **Todoist bookkeeping (local).** No Todoist call — files only:
    - **Pending push.** Task files with no `todoist_id`. A few right after an offline capture is normal; anything older than a day means sync isn't running. Fix: sync Mode 1, "all pending".
    - **Duplicate `todoist_id`.** Two files claiming one Todoist task — always a bug, usually from an interrupted push. Report both files; never pick one silently.
    - **Unbound structure.** An `area` with no `todoist_project_id`, or a `project` with no `todoist_section_id` but with pushed tasks under it.
    - **Mode mismatch.** More than one `area` while `Mode` is `single`, `Bucket` naming an area that doesn't exist, or `PMS id` unset while tasks have been pushed. Fix through setup.
    - **Stale sync.** `todoist_synced_at` empty while pushed tasks exist, or older than the warning age in settings. Also report `Sync schedule: not scheduled` once, with the offer to run setup Q6.
    - **Stale display text.** A task link whose text after `|` no longer matches the target's title in the index (the title was edited in Todoist). Housekeeping only — the link still resolves.

<!-- /fill:c19 -->

<!-- fill:c4.tasks --> **Tasks are the biggest source of these by design** — capture deliberately leaves unrecognized mentions as plain links rather than inventing stub nodes, so a recurring one here is usually a node worth creating, not a link worth typing.<!-- /fill:c4.tasks -->

<!-- fill:c5.targets -->`knowledge/`, `tasks/`, **`tasks/archive/`**, and `raw/archive/`<!-- /fill:c5.targets -->

<!-- fill:c5.bare --> A bare task title (no stem) is dangling even though a task has that title: Obsidian and Dataview cannot follow it.<!-- /fill:c5.bare -->

<!-- fill:c5.both --> Check both directions across `knowledge/` and `tasks/`.<!-- /fill:c5.both -->

<!-- fill:c6.only -->**Knowledge pages only** — pages in `knowledge/`<!-- /fill:c6.only -->

<!-- fill:c6.area --> `area` nodes are exempt: a newly bound area with no projects yet is normal.<!-- /fill:c6.area -->

<!-- fill:c6.tasks --> Skip `tasks/` entirely: an unlinked task is normal.<!-- /fill:c6.tasks -->

<!-- fill:c11.touches --> `touches:` may name task files as well as knowledge pages, so resolve it against both folders; a source that produced action items and lists none is an ingest that stopped halfway.<!-- /fill:c11.touches -->

<!-- fill:c16 -->
16. **Dependency cycles.** Walk `depends_on` and `part_of` across both folders, following targets into `tasks/archive/` where they lead, and report any cycle — A depends on B depends on A, or a task that is `part_of` its own descendant. A `depends_on` cycle is a deadlock: every task in the ring is legitimately `blocked`, none can ever move, and **check #14's stale-block will never fire** because no target is `done`. That combination is why this check exists — the cycle is invisible to every other check in the file and looks like normal blocked work in every task list. Report the full ring, not one member, and let the user decide which edge is wrong; never break a cycle by picking an edge yourself. Bound the walk and say so if you stopped early.
<!-- /fill:c16 -->

<!-- fill:c20 -->

20. **Todoist drift (remote).** Ask sync for a per-area snapshot (Mode 3, one call per bound area — nothing outside them) and compare:
    - **Orphans in Todoist.** A task inside a bound project with no `PMS:` footer — sync will adopt it on the next pull; report it here only if it's older than the last sync, because that means adoption is failing.
    - **Orphans in the files.** A `todoist_id` in the root of `tasks/` that Todoist doesn't have, active or completed. Archived tasks are exempt — Todoist may have aged out their completion records.
    - **State disagreement.** Done in one, open in the other; `pms-blocked` present while every dependency is finished, or missing while one isn't; a grouping task that is completable in Todoist (its name lacks the `* ` header marker); a task file whose title starts with `* ` (the marker leaked into the file); a Todoist parent completed while the files still have open children.
    Fixes go through sync. Lint never writes to Todoist itself.
<!-- /fill:c20 -->

<!-- fill:c17.tasks --> and task<!-- /fill:c17.tasks -->

<!-- fill:band.broken -->, #14's invalid-enum, stale-block and counter-behind, #19's duplicate `todoist_id`, #20's state disagreement<!-- /fill:band.broken -->

<!-- fill:band.drift-closed -->, #14's `closed` mismatch<!-- /fill:band.drift-closed -->

<!-- fill:band.drift-todoist -->, #19's pending push, unbound structure, mode mismatch and stale sync, #20's orphans<!-- /fill:band.drift-todoist -->

<!-- fill:band.house -->, #14's archivable, #19's stale display text<!-- /fill:band.house -->

<!-- fill:ex.scanned -->, tasks/ (18). Not scanned: tasks/archive/, source bodies.<!-- /fill:ex.scanned -->

<!-- fill:ex.c14 -->
  #14 Invalid status (1): T-0031 has status `waiting` → not in the enum; which of the five?
<!-- /fill:ex.c14 -->

<!-- fill:ex.c9 -->, 1 task due-date mismatch<!-- /fill:ex.c9 -->

<!-- fill:ex.c4 -->4 tasks<!-- /fill:ex.c4 -->

<!-- fill:ex.c10 -->, 18 open tasks<!-- /fill:ex.c10 -->

<!-- fill:ex.notrun -->, #20<!-- /fill:ex.notrun -->

<!-- fill:fix.capture --> task changes and archival via capture,<!-- /fill:fix.capture -->

<!-- fill:fix.sync -->, anything in Todoist via sync<!-- /fill:fix.sync -->

<!-- fill:delete.what -->a page, task, or edge<!-- /fill:delete.what -->

<!-- fill:delete.dropped -->, and a task is dropped, never deleted<!-- /fill:delete.dropped -->

<!-- fill:cadence.state -->

Two checks specifically reward a regular cadence rather than a thorough one: #14's stale-block and #16's cycles both find *state that changed while nobody was looking*, and both get worse the longer they sit. Everything else finds mess, which waits patiently.
<!-- /fill:cadence.state -->

<!-- fill:cannot.labels -->
- **Whether a sync ever removed one of the user's own Todoist labels.** Lint has no record of what the labels were before. Sync guards this by verifying every label write as it happens.
<!-- /fill:cannot.labels -->
