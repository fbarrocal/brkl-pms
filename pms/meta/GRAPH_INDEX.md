---
type: index
title: Personal Management System Index
updated: <YYYY-MM-DD>
next_task_id: T-0001   # monotonic counter — capture takes this id and increments it; never lowered, never derived from the entries below
todoist_synced_at:     # set by the sync skill at the end of a completed run; empty = never synced
---

# Index

Navigation entry point. Every query, ingest, and capture starts here — most of them read nothing else. Keep it current; lint checks it against the files actually on disk. Group node entries by type as the PMS grows.

Each node entry carries the page's title **and its aliases**, so resolving a name — dedup on ingest, link resolution on capture, lookup on query — costs one read of this file instead of a scan of every page. Each task entry carries its id, its link, its status, and its due date, so task triage is answered without opening a single task file. The next task id is **not** derived from these entries — archiving removes them — but from `next_task_id` in the frontmatter above. An entry missing its aliases, or a task entry missing its due date, silently turns a one-read operation into a folder scan. Format:

```
- [[Page Title]] — aliases: Variant Name, Another Name
- [[Page With No Aliases]]
- T-0042 [[2026-08-15-email-ana|Email Ana about the Acme renewal]] — open, due 2026-08-22
- T-0041 [[2026-08-14-draft-q3-summary|Draft the Q3 summary]] — done
```

A knowledge page's link is its title, because its filename is its title. A task's link is piped — file stem, then title — because task files are date-slugged and links resolve by filename. Copy the task link from here whenever you write an edge to a task.

## Nodes
_(none yet — node pages appear here as you ingest, grouped by type)_

## Tasks
_(none yet — tasks appear here as you capture them; id, piped link, status, due if set)_

**Archived tasks are not listed here.** When a task moves to `tasks/archive/`, its entry is removed — exactly like an archived source. Tasks are the fastest-growing files in the PMS, and an index that kept every one of them forever would stop being cheap to read, which is the only reason this file exists. An archived task is still a real node with real edges; it is found by scanning `tasks/archive/`, which only a question about history does.

## Sources awaiting ingest
- See the root of `raw/` (processed sources live in `raw/archive/`).
