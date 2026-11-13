<!-- PMS fills for core meta/skills/setup/SKILL.md. Only the fill blocks count; text between them is ignored. -->

<!-- fill:desc.connect -->to connect the services this PMS needs, interview<!-- /fill:desc.connect -->

<!-- fill:desc.pms -->"configure o PMS", <!-- /fill:desc.pms -->

<!-- fill:desc.todoist --> — to connect or re-bind Todoist ("connect Todoist", "configure o Todoist"), to schedule the sync ("schedule the sync"), or when capture/ingest/plan/lint<!-- /fill:desc.todoist -->

<!-- fill:intro.conventions --> conventions,<!-- /fill:intro.conventions -->

<!-- fill:intro.exits --> Outside this PMS folder it writes only the host's scheduled tasks (Q6, on a yes). It reads Todoist through sync and never writes to Todoist directly.<!-- /fill:intro.exits -->

<!-- fill:step0 -->
### Step 0 — Connect what this PMS needs (before the interview)

This PMS needs one connector: **Todoist**. One PMS serves one Todoist account. Check the connection before asking anything else: the Todoist answers in Q5 and Q6 depend on it, and a user who connects at the end has to be interviewed twice.

1. **Probe.** Ask sync for the account read (Mode 3: account, plan, projects and sections). If it answers, note the account name and plan and go to the interview.
2. **If it can't reach Todoist, ask the user to authorize it.** If the host can present a connector card (for example, a connector-suggestion tool), use it to offer Todoist. Otherwise, tell the user in one line where to enable it: the Todoist connector in Claude's connector settings, for this project. Wait for them to say it's done, then probe again.
3. **Never ask for a password or API token in chat.** Authorization happens in the connector's own sign-in flow, not in this conversation.
4. **If the user declines or can't connect now,** carry on with the interview. Record `Connection: not connected` in `meta/SETTINGS.md` § Todoist and skip Q5 and Q6. Tasks are still captured; they wait as *pending push*. The next time any skill needs Todoist, sync will say so and offer this step again.

<!-- /fill:step0 -->

<!-- fill:count -->six<!-- /fill:count -->

<!-- fill:q2.always -->`entity`, `concept`, `area` and `project` always remain available, and `task` always exists (its schema is fixed — it is never proposed, extended, or removed).<!-- /fill:q2.always -->

<!-- fill:q3.tasks --> **Cover task relationships in this same question**, and start from the position that nothing needs adding: subtasks are `part_of`, blocked tasks `depends_on`, a task's subject is `about`, an extracted action item is `introduced_by`. Only propose a task predicate the shipped set genuinely cannot express. If the user approved a `person` node type in Q2, this is also the moment to offer promoting the task `owner` string field into an `assigned_to` typed edge.<!-- /fill:q3.tasks -->

<!-- fill:q4.task-titles --> task titles,<!-- /fill:q4.task-titles -->

<!-- fill:q5-q6 -->
5. **Todoist bucket.** A PMS is usually about one subject, so it lives in **one** Todoist project, and the user's other projects and Inbox stay untouched. Ask where it should live, offering:
   - **A new project named after this PMS** — recommended. It starts empty and nothing of the user's is adopted.
   - **An existing project** — list them by name from the Step 0 read. Before the user picks, say what that implies: its existing **sections** become `project` nodes, and its existing **tasks** (give the count) are adopted by the first sync.
   - **Several projects** — only if the user explicitly wants this PMS to manage more than one. Then each chosen project becomes an `area`, the same implications apply to each, and one of them is named the bucket for unplaced tasks. Record `Mode: multiple`.

   The chosen project becomes the single `area` node (one per project in `multiple` mode). Record it as `Bucket`, record `Mode: single` unless the user chose several, and write a short slug of the PMS's name as `PMS id`. Take the plan (Free / Pro) from the account rather than asking: it sets `Plan` and `Deadlines` in `meta/SETTINGS.md` § Todoist. For a new project, ask sync to create it now (Mode 1, binding without tasks) so it appears in Todoist right away.
6. **Schedule the sync.** Explain in one sentence why it matters: the sync is what brings phone completions into the PMS and unblocks the next steps, and Todoist Free keeps only one week of history. Then ask:
   - **Daily sync** — recommended; ask what time, in the user's timezone.
   - **Weekly quick lint** — optional.
   - **Not now.**
   If the user agrees and the host can create scheduled tasks, create them now, with prompts like *"Run the PMS sync (meta/skills/sync, Mode 2) and show me what got unblocked."* and *"Run the PMS lint, Pass A."* If the host can't schedule, give the user that exact text to add themselves. Record the outcome under `Sync schedule` in `meta/SETTINGS.md` § Todoist. Never schedule without a yes.
<!-- /fill:q5-q6 -->

<!-- fill:write.settings -->, any convention the user changed, the § Todoist values from Step 0, Q5 and Q6<!-- /fill:write.settings -->

<!-- fill:write.knowledge -->
- **`knowledge/`** — the bucket's `area` node (one per chosen project in `multiple` mode), from `meta/templates/area.md`. Title it with the project's name; if the name has a character filenames reject, replace it and keep the original as an alias. Fill `todoist_project_id`. For each existing section in an existing project, add one `project` node, from `meta/templates/project.md`, with `todoist_section_id` filled and `part_of` that area. Add them all to the index.
<!-- /fill:write.knowledge -->

<!-- fill:write.task-template --> Never create or edit `_task.template.md` — the task shape is fixed.<!-- /fill:write.task-template -->

<!-- fill:after-todoist -->
Then, if Todoist is connected:

- **Push anything captured before setup** — sync Mode 1, "all pending".
- **If an existing project was chosen, offer a first sync** (Mode 2) to adopt its tasks. Tell the user how many there are; adopting them now saves the first scheduled run from a surprise.

<!-- /fill:after-todoist -->

<!-- fill:close -->, say what you need to do and it gets captured as a task, or ask to plan a goal<!-- /fill:close -->

<!-- fill:m2.flaggers -->capture/ingest/lint<!-- /fill:m2.flaggers -->

<!-- fill:m2.pms -->
**Out of scope for Mode 2:** the task schema. `status` and `origin` are closed enums and the task field list is fixed in `meta/GRAPH_SCHEMA.md` § Tasks — changing them changes what every capture writes in every PMS, which makes it a rulebook decision, not a per-PMS one. If the user wants a sixth status, tell them plainly that the answer is a `notes` line or a `tags` entry, and that changing the enum means changing the template itself.

**Connectors and schedules** are also handled here after first run:

- "Connect Todoist" / "configure o Todoist" runs Step 0, then Q5 if no bucket is bound yet, then the push-pending step.
- "Schedule the sync" runs Q6.
- Neither re-runs the whole interview.

**Todoist bindings** are also a Mode 2 change. Binding a second Todoist project switches the PMS to `multiple` mode — confirm the user wants that before doing it. Moving the bucket to another project is also a binding change, as is unbinding a project. Unbinding never touches Todoist. The area node keeps its history and its `todoist_project_id` is cleared. Its tasks' Todoist copies stay where they are but are no longer synced, and their files become *unplaced* until re-homed.

<!-- /fill:m2.pms -->
