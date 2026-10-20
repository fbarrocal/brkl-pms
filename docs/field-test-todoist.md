# Field test — Todoist side (v2.6.0)

Run this after `field-test-v2.md` passes, on a scratch copy of `pms/`, with the Todoist connector enabled. It touches a real Todoist account, but only the one project the PMS lives in, so your own account is fine. Archive the test project at the end. Keep notes in `docs/test-notes/ft-todoist.md`.

| # | Do | Pass if | Tests |
|---|---|---|---|
| 0 | Start setup with the Todoist connector **disabled** | Setup's first move is to ask you to connect Todoist (a connector card or one line saying where), with no token asked in chat. After you enable it, it re-checks and continues. | Setup Step 0 |
| 1 | Setup; at Q5 choose **a new project named after the PMS**; Q6: say yes to a daily sync | One new Todoist project exists, with nothing else in the account touched; one `area` node bound to it; `Mode: single`, `Bucket` and `PMS id` recorded; a scheduled task exists and `Sync schedule` is recorded | Setup Q5, Q6 |
| 1b | Optional: in a second scratch copy, choose **an existing project** with one section and one task at Q5 | Setup states what will be adopted (one section, one task) before you confirm; the section becomes a `project` node; the offered first sync adopts the task | Existing-bucket adoption |
| 2 | *"plan: organizar o check-up anual"* — approve a tree with one dependency | Section created in the bucket; groups are **uncompletable** headers; the waiting step has `pms-blocked` and a `Waiting on:` line; every description ends `PMS: <pms-id>/T-…`; task files have `todoist_id` | Plan → capture → sync push |
| 3 | On the phone: try to tick a group header | It can't be completed | Uncompletable on mobile (ADR unproven #1) |
| 4 | On the phone: complete the step the blocked one waits on; add a new task inside the section; rename another; add your own label `@casa` to one; add a task to your **Inbox** and to another project | — | — |
| 5 | *"sync"* | Completion lands in the file with `closed`; the blocked step loses `pms-blocked` and is listed as **now unblocked**; the phone-added task is adopted (new T-id, footer pushed back); the rename updates the file and index; `@casa` **still present**; the Inbox and other-project tasks are **not** read, adopted or mentioned | Pull, recompute, adoption, label merge, bucket isolation |
| 6 | Drop a task in chat (*"drop T-…, not needed"*); then re-plan to drop a whole group | Completed in Todoist with `pms-dropped`; file `dropped` with the reason. For the group: the children are dropped first, and none of them comes back as `done` on the next sync | Drop mapping; bottom-up terminal order |
| 7 | Delete a task on the phone, then sync | File becomes `dropped` with "deleted in Todoist"; no file removed | Deletion handling |
| 8 | Move a task to another section on the phone, then sync | Sync asks; nothing changes until you answer | Moves are not adopted silently |
| 9 | Turn wifi/connector off, capture a task, turn it back on, sync | Task captured offline, pushed on the next sync; lint #19 showed it as pending in between | Offline safety |
| 10 | *"what's on my plate"* | Answer reflects step 4's phone changes even before a sync | Query reads live state |
| 11 | *"full lint"* | #20 runs one Todoist read per area and reports nothing broken | Remote drift check |
| 12 | Leave it 8+ days without syncing, then sync | Warning about the one-week history; check whether completions older than 7 days still came through (ADR unproven #2) | Free-plan history limit |

Record the token or time cost of step 5. A daily sync that is too expensive to run is the most likely reason this design fails.
