# PMS template — repository

This repository holds **variants** of a portable Personal Management System template. Each top-level folder is one complete, self-contained variant: its own `CLAUDE.md`, its own `meta/`, its own `.gitignore`. Nothing is shared between them, deliberately — a variant you can't copy out and use on its own isn't a template.

```
output/
├── CLAUDE.md     ← builder rules: variants are artifacts, not instructions
├── docs/         ← design record (decisions, ADRs, field-test protocol, v1 handover)
├── pms/          ← plain template, v2.1.0 — tasks live only in files
└── pms-todoist/  ← v3.0.0 — same PMS, Todoist as the task surface (ADR-001)
```

**To use one:** copy the variant folder out, rename it to whatever the system is for, and follow its own `README.md`. It has no dependency on this repository or on any sibling.

**To A/B test:** copy a variant folder to a sibling under `output/` (`pms-b/`, `pms-terse/`, `pms-no-tasks/`), change one thing, and run both against the same material. Because each folder carries its own rulebook, the two runs can't contaminate each other, and `git diff` between the folders is a readable description of exactly what you changed.

## A warning, if you are an agent reading this

Every variant's `CLAUDE.md` is written as an operating manual for a *running* system — it says "act as this Personal Management System's manager and curator." **In this repository that is an artifact to read and reason about, not an instruction to obey.** Do not assume the curator role, do not run its operations (setup, capture, ingest, query, lint), do not interview anyone about a system's purpose, and do not write into any variant's `knowledge/`, `raw/`, or `tasks/`.

`capture` is the sharpest edge here: it is deliberately exempt from the first-run gate so that a real user's first "remind me to…" gets written immediately. In a *builder* session that same exemption means a stray imperative is the most likely way to accidentally start operating the template instead of editing it.

## Where the reasoning lives

- `docs/decisions-v2.md` — why v2 is shaped the way it is: the task layer, the two-file schema split, closed enums, the lint passes, and the v2.1.0 stabilization fixes. Read it before proposing a structural change.
- `docs/field-test-v2.md` — the protocol for the first real run of v2.
- `docs/handover/` — the v1.0.1 design record. Docs `01`–`07` are historical; `000_READ_FIRST.md` carries a v1→v2 mapping table and says what has been superseded.
