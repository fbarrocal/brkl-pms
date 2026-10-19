# Link-format check (v2.1.0)

A throwaway vault to confirm the piped task-link format `[[file-stem|Title]]` works in Obsidian and the plugins the PMS README lists. Open **this folder** as a vault (Open folder as vault). Don't save results here; record them in `../field-test-v2.md` notes.

| Check | Expected |
|---|---|
| **Core graph** (turn on *Existing files only* off) | `Send the signed contract` → `Email Ana…` is a real edge. `Control - bare title link` points at a grey **unresolved** node named "Email Ana about the Acme renewal". |
| **Properties panel** on `2026-08-16-send-contract` | `depends_on` shows "Email Ana about the Acme renewal" as a clickable link that opens the task file. |
| **Dataview** — paste the block below into a new note | `blocker` column shows the title and links to the file for T-0002; for T-0003 the link is unresolved. |
| **Graph Link Types** (needs Dataview) | Edge labels `depends_on` and `about` appear on the lines. |
| **Breadcrumbs** — add `depends_on` and `about` as edge fields | Both tasks' edges appear; T-0002's points at the real task file. |
| **Juggl** | Same as core graph. Note: Juggl's last release was Feb 2025. |

```dataview
TABLE status, depends_on AS blocker, about
FROM "tasks"
```
