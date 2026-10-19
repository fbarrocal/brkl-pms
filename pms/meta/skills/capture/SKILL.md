---
name: capture
description: Capture a task, action item, or reminder into tasks/ as a typed node. Use this whenever the user states something they need to do or want remembered — "to do", "todo", "add a task", "remember me to", "remind me to", "action item", "I need to", "don't let me forget", "lembra de", "preciso", "anota aí" — or when another skill (usually ingest) hands you an action item it found. Trigger it for a bare imperative aimed at the user's future self, even when the word "task" is never spoken. This is also the skill that updates a task's status, marks one done, or drops one.
---

# Capture

Turn an intent into a task node. **This skill is authoritative for everything in `tasks/`** — no other skill writes, updates, or archives a task file; they call this one. It is also the skill that must stay *fast*: capture that costs the user a conversation is capture they stop using.

**Prerequisite:** `CLAUDE.md` — operate by it. `meta/GRAPH_SCHEMA.md` § Tasks is the authority for the task schema and the `status` / `origin` enums; § Edges is the authority for predicates. `meta/SETTINGS.md` § Language governs the task title and body.

**Capture runs before setup.** This is the one operation exempt from the first-run gate in `CLAUDE.md`. If `setup_done` is `false`, still write the task — use the language the user is writing in, take the default ID prefix, and expect no edges to resolve (the index is empty). Then say the PMS isn't configured yet and offer setup. Making someone answer a four-question interview before their first "remind me to…" is how a task tracker stops getting used on day one.

## Mode A — new task

1. **Read `meta/GRAPH_INDEX.md` — once.** This single read serves both of the next two steps. Everything capture needs to be correct is in it: the `next_task_id` counter, the link for every task, and the titles and aliases of every node. Do not scan folders unless this read tells you it can't be trusted.
2. **Assign the id.** Take `next_task_id` from the index's frontmatter. Never derive it from the `## Tasks` entries or from a count of files — archiving removes entries, so the highest listed id is not the highest id ever issued, and ids are never reused. If the counter is missing, or is not above every id listed in the index, it is stale: scan `tasks/` **and `tasks/archive/`** for the true maximum, use that plus one, and tell the user to run lint. Lint's duplicate-id and counter checks are the backstop.
3. **Write the file.** Create `tasks/YYYY-MM-DD-short-slug.md` from `meta/templates/_task.template.md`. The date prefix is today's capture date, not the due date. Take the user's words as the title, as an imperative, in the PMS's Language. Do not research, do not restructure the graph, do not ask a clarifying question you could answer from the text.
4. **Set the fields.**
   - `status: open` unless the user clearly said otherwise; `created` and `updated` to today.
   - `origin` per the schema: `capture` when a human asked, `ingest` when ingest handed it over, `query` when it came out of an answer.
   - **`sources:` only when `origin` is `ingest`** — the archived `raw/` path the caller passed you. A task with any other origin has no `sources:` field at all; its provenance *is* its origin.
   - `due` and `owner` only if stated. An unstated optional field is omitted entirely, never filled with a guess or a placeholder. No `closed` — that field appears only when a task goes terminal.
5. **Link what the index already resolved.** For each thing the task mentions, if it matched an entry's **title or alias exactly** in step 1, write the typed edge using the link **exactly as the index lists it** — a knowledge page's `[[Title]]`, or a task's piped `[[<file-stem>|<Title>]]` (a bare task title resolves to no file) — `about` for what the task concerns, `part_of` for a subtask, `depends_on` for what it waits on, `introduced_by` for where it came from. Everything else stays a plain `[[wikilink]]` in the body.
6. **Never create a stub node.** A one-line reminder must not add empty pages to `knowledge/`. If the user names something the PMS has never heard of, that is a plain prose link and a lint finding later — not a page. If the thing clearly deserves a node, *say so in your report* and let the user decide.
7. **Add it to the index.** One line under `## Tasks` in `meta/GRAPH_INDEX.md`: id, piped link (`[[<file-stem>|<Title>]]`), status, and `due` if the task has one — Mode C of the query skill reads this line instead of opening the file, so a missing `due` there costs a full folder scan later. In the **same write**, increment `next_task_id` and bump the index's `updated` date. Writing the task without advancing the counter is how an id gets issued twice.
8. **Report in one line.** `Captured T-0042 — "<title>" (open) → about [[Project X]]`. Add a second line only if you have a flag: an unresolved mention worth promoting to a node, or a duplicate you found.

**What capture must not do:** it does not ingest, it does not dedup beyond the exact index match, it does not propose schema changes, it does not write to `knowledge/`, and it does not ask more than one question. If the request turns out to be material to be understood rather than an intent to act, stop and route to ingest instead.

**Batch captures.** When several action items arrive at once (usually from ingest), read the index once, write them all with consecutive ids starting at `next_task_id`, advance the counter past the last one, then report as one list. Each still gets its own file and its own index line.

## Mode B — update, complete, or drop a task

For "mark T-0042 done", "that one's blocked", "drop the Ana thing", "push this to next week":

1. **Find the task** — by id, by title, or by the index. If more than one plausibly matches, ask which; do not guess.
2. **Change only what was asked.** Set `status` to a value from the closed enum (`open` | `doing` | `blocked` | `done` | `dropped`) — never a free-text state. Bump `updated`.
3. **Going terminal sets `closed`.** When status becomes `done` or `dropped`, add `closed:` with today's date. This is what the archive window is measured from — `updated` can't do it, because any later edit resets it. Reopening a terminal task removes `closed` again.
4. **`blocked` needs a reason.** Either a `depends_on` edge pointing at what it waits for, or a `notes` line. A task that is blocked on nothing recorded is just an open task, and lint will flag it.
5. **`dropped` needs a reason too** — a `notes` line saying why. Dropping is a decision worth keeping; deleting it loses the decision.
6. **Never delete the file.** There is no completion path that removes a task. Terminal tasks stay in `tasks/` until archived.
7. **Update the index** entry's status. Report in one line.

## Mode C — archive

Only when the user asks, or when lint proposed it and the user approved:

1. Select tasks whose `closed` date is older than the window in `meta/SETTINGS.md` § Conventions. Never archive a task in a non-terminal state, and never archive one as a side effect of completing it — a task the user just finished should still be visible to them.
2. Move each to `tasks/archive/` (create the folder if missing). The file is unchanged: it keeps its frontmatter, its edges, and its id forever.
3. **Remove its entry from `meta/GRAPH_INDEX.md`.** This is the point of archiving. The index is what capture and query triage read on every single operation, so it has to stay bounded, and tasks are the fastest-growing thing in the PMS. An archived task is found by scanning `tasks/archive/` — which only a history question does. Bump the index's `updated` date.
4. Report the count and the id range moved.

## Escalating

Capture calls other skills rather than doing their work:

- The task needs a node type or predicate that doesn't exist → propose it and route to `meta/skills/setup/SKILL.md` (Mode 2). Capture never edits `meta/GRAPH_SCHEMA.md` itself.
- The user is actually handing you material, not an intent → `meta/skills/ingest/SKILL.md`.
- The user wants to see their tasks rather than add one → `meta/skills/query/SKILL.md` (Mode C).
