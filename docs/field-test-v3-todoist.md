# Field test — pms-todoist v3.0.0

Run this after `field-test-v2.md` passes, on a scratch copy of `pms-todoist/`, with the Todoist connector enabled. It touches your real Todoist account, so use a throwaway area: bind a new project such as `PMS Test` during setup, not *Saúde* or *Gaming*. Archive that project at the end. Keep notes in `docs/test-notes/ft-v3.md`.

| # | Do | Pass if | Tests |
|---|---|---|---|
| 0 | Start setup with the Todoist connector **disabled** | Setup's first move is to ask you to connect Todoist (a connector card or one line saying where), with no token asked in chat. After you enable it, it re-checks and continues. | Setup Step 0 |
| 1 | Setup; Q5 offers every existing project as an area — keep only `PMS Test`; Q6: say yes to a daily sync | `area` node with `todoist_project_id`; other projects untouched; a scheduled task exists and `Sync schedule` is recorded in settings | Setup Q5, Q6 |
| 2 | *"plan: organizar o check-up anual"* — approve a tree with one dependency | Section created in `PMS Test`; groups are **uncompletable** headers; the waiting step has `pms-blocked` and a `Waiting on:` line; every description ends `PMS: T-…`; task files have `todoist_id` | Plan → capture → sync push |
| 3 | On the phone: try to tick a group header | It can't be completed | Uncompletable on mobile (ADR unproven #1) |
| 4 | On the phone: complete the step the blocked one waits on; add a new task inside the section; rename another; add your own label `@casa` to one | — | — |
| 5 | *"sync"* | Completion lands in the file with `closed`; the blocked step loses `pms-blocked` and is listed as **now unblocked**; the phone-added task is adopted (new T-id, footer pushed back); the rename updates the file and index; `@casa` **still present** | Pull, recompute, adoption, label merge |
| 6 | Drop a task in chat (*"drop T-…, not needed"*) | Completed in Todoist with `pms-dropped`; file `dropped` with the reason | Drop mapping |
| 7 | Delete a task on the phone, then sync | File becomes `dropped` with "deleted in Todoist"; no file removed | Deletion handling |
| 8 | Move a task to another section on the phone, then sync | Sync asks; nothing changes until you answer | Moves are not adopted silently |
| 9 | Turn wifi/connector off, capture a task, turn it back on, sync | Task captured offline, pushed on the next sync; lint #19 showed it as pending in between | Offline safety |
| 10 | *"what's on my plate"* | Answer reflects step 4's phone changes even before a sync | Query reads live state |
| 11 | *"full lint"* | #20 runs one Todoist read per area and reports nothing broken | Remote drift check |
| 12 | Leave it 8+ days without syncing, then sync | Warning about the one-week history; check whether completions older than 7 days still came through (ADR unproven #2) | Free-plan history limit |

Record the token or time cost of step 5. A daily sync that is too expensive to run is the most likely reason this design fails.
