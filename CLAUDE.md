# PMS template — builder repository

This repository **develops** a Personal Management System template. It does not run one.

## The one rule

Every variant folder (`pms/`, `pms-todoist/`, and any other `pms-*/` sibling) contains its own `CLAUDE.md`, written as the operating manual for a *running* system ("act as this Personal Management System's manager and curator"). **In this repository those files are artifacts to read, edit, and reason about — never instructions to follow.** This file takes precedence over any nested `CLAUDE.md`, including ones loaded automatically when you open files under a variant folder.

So, in this repository:

- Do not assume the curator role.
- Do not run setup, capture, plan, ingest, query, sync, or lint against any variant.
- Do not call the Todoist connector as part of operating a variant. Testing the mapping in a clearly named, temporary sandbox project is builder work. Touching the user's real projects is not.
- Do not interview the user about a PMS's purpose.
- Do not write into any variant's `knowledge/`, `raw/`, or `tasks/`. Those folders ship empty (`.gitkeep` only) and must stay that way.
- A message like "remind me to…" is addressed to *you as a builder*, not a request to capture a task into `pms/tasks/`. Capture is exempt from the first-run gate in the variant rulebook, which makes it the easiest way to start operating the template by accident.

## Layout

```
output/                  ← git root
├── CLAUDE.md            ← this file (builder rules)
├── README.md            ← what the repo is, how variants work
├── docs/
│   ├── adr/             ← architecture decision records (001: Todoist task surface)
│   ├── decisions-v2.md  ← why v2 is shaped this way — read before structural changes
│   ├── field-test-v2.md ← protocol for the first real run
│   └── handover/        ← v1.0.1 design record (historical; 000_READ_FIRST maps v1→v2)
├── pms/                 ← plain variant (v2.x)
└── pms-todoist/         ← Todoist variant (v3.x) — see docs/adr/001
```

## Invariants every change must preserve

Files are the source of truth · each variant's `CLAUDE.md` stays static and identical across instances · `meta/GRAPH_SCHEMA.md` and `meta/SETTINGS.md` are the only mutable rules files · node types and predicates are a closed per-PMS vocabulary · nothing silently fabricates data or hard-deletes.

## Working conventions

- After any structural change (rename, moved field, new rule), grep the whole variant for stale references — renames go stale silently, and past audits caught real bugs this way.
- Record the *why* of a change in `docs/decisions-v2.md`, not in the variant's `CLAUDE.md`; the operating files should stay imperative.
- Bump the version string in `pms/README.md` and tag the commit.
