---
type: index
title: Knowledge Base Index
updated: <YYYY-MM-DD>
---

# Index

Navigation entry point. Every query and ingest starts here. Keep it current — lint checks it against the pages actually on disk. Group entries by node type as the KB grows.

Each entry carries the page's title **and its aliases**, so resolving a name — dedup on ingest, lookup on query — costs one read of this file instead of a scan of every page. Format:

```
- [[Page Title]] — aliases: Variant Name, Another Name
- [[Page With No Aliases]]
```

## Nodes
_(none yet — node pages appear here as you ingest, grouped by type)_

## Sources awaiting ingest
- See the root of `sources/` (processed sources live in `sources/archive/`).
