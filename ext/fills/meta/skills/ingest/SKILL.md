<!-- PMS fills for core meta/skills/ingest/SKILL.md. Only the fill blocks count; text between them is ignored. -->

<!-- fill:desc.tasks --> and tasks<!-- /fill:desc.tasks -->

<!-- fill:intro.action-items --> extract action items,<!-- /fill:intro.action-items -->

<!-- fill:intro.output --> and `tasks/` are output<!-- /fill:intro.output -->

<!-- fill:prereq.tasks -->**Nodes**, **Tasks**, and **Edges** sections<!-- /fill:prereq.tasks -->

<!-- fill:ref.conflicts -->step 9<!-- /fill:ref.conflicts -->

<!-- fill:action-items -->
8. **Extract action items — then hand them to capture.** Sources full of commitments (meeting notes, transcripts, threads) usually carry things someone has to *do*, and those are the highest-value thing in the file. Identify them; then **follow `meta/skills/capture/SKILL.md` to write them** — do not write task files from here. Capture is authoritative for `tasks/`, and reimplementing it is how the two drift apart. Pass it, for each item: the imperative as the title, `origin: ingest`, the path this source *will have* in `raw/archive/` for `sources:`, and an `introduced_by` edge pointing at the person who committed (if the index has them) or else at the source, linked as `[[<archived-file-stem>|<source title>]]` so it resolves to the file. Capture handles ids, filenames, index entries, and edge resolution. Hand over the whole batch at once so it reads the index once and assigns consecutive ids.
   - **Use the archived path, not the current one.** The source is still in the root of `raw/` at this point and only moves in step 10, so the obvious path is the wrong one — writing it would leave every ingested task pointing at a file that no longer exists the moment ingest finishes.
   - Extract only what the source **states as a commitment or a request** — a topic worth exploring is a node, not a task. When in doubt, list the borderline ones in your report and ask, rather than filling `tasks/` with speculation.
   - If the source contains no action items, say "none" in the report and move on. Not every source produces tasks.
<!-- /fill:action-items -->

<!-- fill:n9 -->9<!-- /fill:n9 -->

<!-- fill:n10 -->10<!-- /fill:n10 -->

<!-- fill:touches.tasks --> — **knowledge pages and task files alike** —<!-- /fill:touches.tasks -->

<!-- fill:n11 -->11<!-- /fill:n11 -->

<!-- fill:index.tasks --> New tasks were already indexed by capture in step 8; don't add them twice.<!-- /fill:index.tasks -->

<!-- fill:report.tasks -->
Tasks captured (N): T-0042 "<title>", T-0043 "<title>"     (or "none")
<!-- /fill:report.tasks -->

<!-- fill:report.ambiguous -->
⚠ Ambiguous action items: "<X>" — task, or just a topic?   (or "none")
<!-- /fill:report.ambiguous -->

<!-- fill:last-step -->10<!-- /fill:last-step -->

<!-- fill:unfinished.tasks --> and tasks<!-- /fill:unfinished.tasks -->

<!-- fill:unfinished.ids --> Tasks already captured are not rolled back — say which ids exist so a re-ingest can recognize them instead of duplicating.<!-- /fill:unfinished.ids -->
