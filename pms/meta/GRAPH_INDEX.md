---
type: index
title: Personal Management System Index
updated: <YYYY-MM-DD>
---

# Index

Navigation entry point. Every query, ingest, and capture starts here — most of them read nothing else. Keep it current; lint checks it against the files actually on disk. Group node entries by type as the PMS grows.

Each node entry carries the page's title **and its aliases**, so resolving a name — dedup on ingest, link resolution on capture, lookup on query — costs one read of this file instead of a scan of every page. Each task entry carries its id, status, and due date, so both task triage *and* next-id assignment are answered without opening a single task file. An entry missing its aliases, or a task entry missing its due date, silently turns a one-read operation into a folder scan. Format:

```
- [[Page Title]] — aliases: Variant Name, Another Name
- [[Page With No Aliases]]
- T-0042 [[Email Ana about the Acme renewal]] — open, due 2026-08-22
- T-0041 [[Draft the Q3 summary]] — done
```

## Nodes
_(none yet — node pages appear here as you ingest, grouped by type)_

## Tasks
_(none yet — tasks appear here as you capture them; id, title, status, due if set)_

**Archived tasks are not listed here.** When a task moves to `tasks/archive/`, its entry is removed — exactly like an archived source. Tasks are the fastest-growing files in the PMS, and an index that kept every one of them forever would stop being cheap to read, which is the only reason this file exists. An archived task is still a real node with real edges; it is found by scanning `tasks/archive/`, which only a question about history does.

## Sources awaiting ingest
- See the root of `raw/` (processed sources live in `raw/archive/`).
