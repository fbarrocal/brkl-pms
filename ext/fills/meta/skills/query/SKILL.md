<!-- PMS fills for core meta/skills/query/SKILL.md. Only the fill blocks count; text between them is ignored. -->

<!-- fill:desc.lists -->, traversing typed edges, and listing tasks<!-- /fill:desc.lists -->

<!-- fill:desc.work --> — or asks about their own work: "what's on my plate", "what's open", "what's blocked", "o que está pendente", "what's due this week"<!-- /fill:desc.work -->

<!-- fill:modes -->Three<!-- /fill:modes -->

<!-- fill:scope -->
**Scope, for every mode:** the graph is `knowledge/` **∪ the root of `tasks/`**. Any scan for inbound edges covers both — a scan of `knowledge/` alone silently drops every task, which is exactly the half of the answer the user asked for when they said "what's blocking this". Include `tasks/archive/` only when the question is about history ("what did I do last month", "why did we drop that").
<!-- /fill:scope -->

<!-- fill:a.fallback --> and `tasks/`<!-- /fill:a.fallback -->

<!-- fill:a.open-work -->
3. **Mention open work on the subject.** If tasks point at X (`about`, `depends_on`, `part_of`), a summary of X that omits them is incomplete — the user asked what they know, and what they still owe is part of that. One sentence, in prose: "You still owe a follow-up email to Ana on this." Skip terminal tasks unless asked.
<!-- /fill:a.open-work -->

<!-- fill:a.n4 -->4<!-- /fill:a.n4 -->

<!-- fill:b.blocking -->, "what's blocking X"<!-- /fill:b.blocking -->

<!-- fill:b.both --> — **across `knowledge/` and `tasks/` both** —<!-- /fill:b.both -->

<!-- fill:b.archive --> When following an outbound edge whose target is not in `knowledge/` or the root of `tasks/`, check `tasks/archive/` before calling it missing — a link to an archived task is valid.<!-- /fill:b.archive -->

<!-- fill:mode-c -->
## Mode C — task list / triage

For "what's on my plate", "what's open", "what's blocked", "what's due this week", "what's left on Project X":

1. **Ask sync for live state first** (`meta/skills/sync/SKILL.md`, Mode 3, task state). Todoist owns done, due and priority, so a list built from the files alone can be a day stale. Use the files for structure (what's `part_of` what, what waits on what) and for tasks still pending push, and Todoist for the state. Where the two disagree, Todoist's state is the answer — mention that a sync is due. If Todoist is unreachable, carry on from the index and **say the answer is as of** `todoist_synced_at`.
2. **Then read the `## Tasks` section of `meta/GRAPH_INDEX.md`.** It carries id, link, status, and due date — enough to join Todoist's state to the graph, and, when Todoist is unreachable, enough to answer "what's open", "what's due this week", and "what's blocked" in one read. Open individual task files only for the ones you'll report in detail, or when the question needs a field the index doesn't carry (`owner`, `notes`, edges). If a task's due date is missing from the index but present in the file, say so — that is index drift, and lint fixes it.
3. **Filter by the closed enum, not by adjectives.** "Open work" means `status` in `open` / `doing` / `blocked` — say which you included. Terminal tasks (`done`, `dropped`) are excluded unless the user asks for history. **`tasks/archive/` is not in the index at all**, so a history question ("what did I finish last quarter", "why did we drop that") is the one case that costs a folder scan — do it when asked, and say that's what you're doing.
4. **Scoped by a subject?** "What's left on Project X" is an inbound-edge question — scan `tasks/` for tasks whose `about` / `part_of` / `depends_on` fields name that page, then filter by status.
5. **Answer as a short list, ordered by what makes it actionable:** blocked items first (they need a decision), then due date, then capture date. Give the id and title on each line, since the id is how the user will refer back to it. Two or three items can just be prose.
6. **Surface the stuck ones.** A `blocked` task whose `depends_on` target is already `done`, or an `open` task that's been open a long time, is worth one sentence — that is the whole point of tracking them. Don't fix it here; say it, and let capture or lint handle the change.
7. **When the list is empty, say so plainly** — don't pad it with near-misses from other statuses.

Mode C **reads**. It never changes a status, completes, drops, or archives a task — that is capture's Mode B. If the user's next words are "mark the second one done", follow `meta/skills/capture/SKILL.md`.

<!-- /fill:mode-c -->

<!-- fill:answer.tasks -->facts, edges, or tasks<!-- /fill:answer.tasks -->

<!-- fill:save.task -->

If instead the answer surfaced something the user needs to *do*, follow `meta/skills/capture/SKILL.md` with `origin: query` — don't write the task file from here.
<!-- /fill:save.task -->

<!-- fill:output.c -->
- For Mode C only: state the filter you applied, e.g. `Scope: open + doing + blocked, all subjects` — so an empty or short list is readable as a real answer rather than a missed scan.
<!-- /fill:output.c -->
