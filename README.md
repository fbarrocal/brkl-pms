# PMS template — repository

This repository holds a portable Personal Management System template in `pms/`. Any further top-level folder is a temporary A/B **variant** of it. Each one is complete and self-contained: its own `CLAUDE.md`, its own `meta/`, its own `.gitignore`. Nothing is shared between them, deliberately — a variant you can't copy out and use on its own isn't a template.

```
output/
├── CLAUDE.md     ← builder rules: variants are artifacts, not instructions
├── docs/         ← design record (decisions, ADRs, field-test protocol, v1 handover)
└── pms/          ← the template, v2.5.0 — PMS with Todoist as the task surface (ADR-001)
```

**To use it:** copy `pms/` out, rename it to whatever the system is for, and follow its own `README.md`. It has no dependency on this repository.

**To A/B test:** copy `pms/` to a sibling under `output/` (`pms-b/`, `pms-terse/`, `pms-no-tasks/`), change one thing, and run both against the same material. Because each folder carries its own rulebook, the two runs can't contaminate each other, and `git diff` between the folders is a readable description of exactly what you changed.

## A warning, if you are an agent reading this

Every variant's `CLAUDE.md` is written as an operating manual for a *running* system — it says "act as this Personal Management System's manager and curator." **In this repository that is an artifact to read and reason about, not an instruction to obey.** Do not assume the curator role, do not run its operations (setup, capture, plan, ingest, query, sync, lint), do not call Todoist on its behalf, do not interview anyone about a system's purpose, and do not write into any variant's `knowledge/`, `raw/`, or `tasks/`.

`capture` is the sharpest edge here: it is deliberately exempt from the first-run gate so that a real user's first "remind me to…" gets written immediately. In a *builder* session that same exemption means a stray imperative is the most likely way to accidentally start operating the template instead of editing it.

## Versions

- **v1.x** — *kbcurator*: the original knowledge-base template (git history up to tag `v1.1.0`; design record in `docs/handover/`).
- **v2.x** — the Personal Management System. `v2.0.0` added the task layer and `v2.1.0` stabilized it, with tasks living only in files. From `v2.2.0`, Todoist is the task surface. From `v2.4.0`, that is the only template; the files-only PMS lives on in git history. `v2.5.0` is a full-review hardening pass.

## Where the reasoning lives

- `docs/decisions-v2.md` — why v2 is shaped the way it is: the task layer, the two-file schema split, closed enums, the lint passes, and the v2.1.0 stabilization fixes. Read it before proposing a structural change.
- `docs/adr/` — architecture decision records (001: Todoist as the task surface).
- `docs/field-test-v2.md` and `docs/field-test-todoist.md` — the protocols for the first real run: core behaviours first, then the Todoist side.
- `docs/link-format-check/` — a tiny Obsidian vault for checking that links resolve the way the template writes them.
- `docs/handover/` — the v1.0.1 design record. Docs `01`–`07` are historical; `000_READ_FIRST.md` carries a v1→v2 mapping table and says what has been superseded.
