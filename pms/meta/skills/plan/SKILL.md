---
name: plan
description: >-
  Break a goal or request into a plan of tasks with dependencies, write it to the PMS, and put the whole tree in Todoist. Use this whenever the user says "plan", "break this down", "quebra isso em tarefas", "planeja", "what are the steps to…", "turn this into a project", or hands over a goal that is clearly more than one task. Also use it to re-plan: add steps to an existing plan, split a task that turned out bigger, or re-order when something slips.
---

# Plan

Turn a goal into a tree of tasks — the pipeline-manager part of the PMS. **This skill is authoritative for decomposition**: deciding what the steps are, how they nest, and what waits on what. It does not write task files (capture does) and does not talk to Todoist (sync does); it decides, then calls them.

**Prerequisite:** `CLAUDE.md` — operate by it. `meta/GRAPH_SCHEMA.md` § Nodes (`area`, `project`), § Tasks and § Edges. `meta/SETTINGS.md` § Purpose, § Language and § Todoist.

## Mode A — new plan

1. **Read `meta/GRAPH_INDEX.md`** once. Find the area this belongs to (in single mode, always the bucket) and whether a `project` node for it already exists. If one exists, this is a re-plan — go to Mode B.
2. **Read the context the plan depends on.** Open the knowledge pages the goal is `about` — what the PMS already knows changes what the steps are. Do not research outside the PMS unless the user asks.
3. **Draft the tree.** Shape rules:
   - **Leaves are actions** — one sitting, one verb, obvious when finished. "Email Ana the draft", not "Handle Ana".
   - **Group only when it helps.** A group (phase) is a task with children. Use one level of groups for most plans and two at most. Todoist nests further, but phones don't show it well.
   - **`depends_on` only for real ordering** — B cannot start until A is finished. "It would be nice to do A first" is order within a group, not a dependency. Every unnecessary dependency is a task that shows as blocked on the phone for no reason.
   - **No dependency cycles.** Check before presenting.
   - **Dates only where the user gave one or the goal implies one.** Never invent due dates to make the plan look complete. If the user gave a final date, put it on the last leaf or the group it finishes, not on every task.
   - **Size it honestly.** If a plan runs past about 25 leaves, it is probably two projects; say so and propose the split.
4. **Present it for approval — nothing is written yet.** Show it as an indented list in the PMS's Language:

```
Area: <Area>    Project: <Project> (new section in Todoist)
1. <Group>
   1.1 <Leaf>                       due <date>
   1.2 <Leaf>
2. <Group>                          waits on 1
   2.1 <Leaf>
   2.2 <Leaf>                       waits on 2.1
Open questions: <anything you had to assume>
```

   Ask for approval, edits, or a different cut. Iterate until approved. **Do not write a partial plan** while the user is still deciding.
5. **On approval, write the structure:**
   - **Project node.** If none exists, create `knowledge/<Project>.md` from `meta/templates/project.md`, with `part_of: ["[[<Area>]]"]`. In single mode the area is always the bucket, so plan never creates one. In `multiple` mode a new area (`meta/templates/area.md`) means a new Todoist project: ask first. These two node types are the only knowledge pages this skill writes. They are exempt from the provenance check because they record an intent, not a source. Add each one to the index.
   - **Tasks.** Call capture **once, as a batch**, with every node of the tree in order (parents first):
     - the title;
     - `origin: plan`;
     - `part_of` → its group, or the project node for top-level items;
     - `about` → the project node;
     - `depends_on` between siblings, given as references to other items in the same batch;
     - `due` where agreed.
     Capture assigns consecutive ids, resolves the in-batch references to real links, and writes the index lines.
6. **Push happens inside capture.** Capture hands the whole batch to sync in one call, so do not call sync again here. Read its result: the whole tree goes to Todoist, groups as uncompletable headers, leaves as tasks, waiting items labelled `pms-blocked`.
7. **Report in a few lines:** project, number of tasks, what is actionable right now (the leaves not waiting on anything), and the Todoist location (area project › section).

## Mode B — re-plan an existing project

For "add a step", "this task is bigger than I thought", "move X after Y", "we're dropping the second phase":

1. Read the project's current tree: its index entries, then the task files that are `part_of` it.
2. Propose the change as a diff against the tree — added, moved, re-dependent, dropped — and get approval.
3. Apply it:
   - new tasks → capture batch (Mode A of capture);
   - changes to edges or status → capture Mode B;
   - dropped work → `status: dropped` with a reason, never deleted. **Dropping a group means dropping every open child first**, then the group. In Todoist, completing a parent completes its open subtasks, and sync would then read those subtasks as *done* rather than dropped.
   Capture pushes each change through sync, so there is no separate push step here.
4. **Splitting a task** that already exists: the original becomes the group (same id, same Todoist task, now uncompletable), and the new pieces are its children. Do not drop it and create a new one — that throws away its history and its Todoist id.

## Escalating

- The plan needs a node type or predicate that doesn't exist → setup (Mode 2).
- The user hands over material rather than a goal ("here are the meeting notes, plan the follow-ups") → ingest first. Ingest's extracted action items can then be grouped by this skill if the user asks.
- A single task → capture, not a plan.
