---
type: index
title: {{SYSTEM}} Index
updated: <YYYY-MM-DD>
<!-- slot:fm.tasks /-->
---

# Index

Navigation entry point. <!-- slot:readers -->Every query and ingest starts here<!-- /slot:readers --> — most of them read nothing else. Keep it current; lint checks it against the files actually on disk. Group node entries by type as the {{SYS}} grows.

Each node entry carries the page's title **and its aliases**, so resolving a name — dedup on ingest<!-- slot:resolve.capture /-->, lookup on query — costs one read of this file instead of a scan of every page.<!-- slot:task-entries --> An entry missing its aliases silently turns a one-read operation into a folder scan.<!-- /slot:task-entries --> Format:

```
- [[Page Title]] — aliases: Variant Name, Another Name
- [[Page With No Aliases]]
<!-- slot:format.tasks /-->
```

A knowledge page's link is its title, because its filename is its title.<!-- slot:task-links /-->

## Nodes
_(none yet — node pages appear here as they are written by ingest<!-- slot:nodes.writers /-->, grouped by type)_

<!-- slot:tasks /-->
## Sources awaiting ingest
- See the root of `raw/` (processed sources live in `raw/archive/`).
