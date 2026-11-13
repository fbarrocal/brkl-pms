# brkl-pms — PMS template repository

This repository holds a portable Personal Management System template in `pms/`: a knowledge graph with a task layer, and Todoist as the task surface. The knowledge-graph half is the **[brkl-kb](https://github.com/fbarrocal/brkl-kb)** Knowledge Base template, which this repository builds on. Use brkl-kb directly for projects that need only a knowledge base.

```
brkl-pms/         ← git root
├── CLAUDE.md     ← builder rules: templates are artifacts, not instructions
├── vendor/kb/    ← the brkl-kb core, pinned to a tag (v1.2.0)
├── ext/          ← the PMS layer: fills for the core's slots, plus PMS-only files
├── pms/          ← the built template, v2.7.0 — copy this one
├── tools/        ← build.py, vendor_kb.py (Python 3, standard library only)
└── docs/         ← design record (decisions, ADRs, field-test protocols, v1 handover)
```

**To use it:** copy `pms/` out, rename it to whatever the system is for, and follow its own `README.md`. It has no dependency on this repository or on brkl-kb.

**To change it:** edit `ext/` (or brkl-kb, for anything that isn't about tasks or Todoist), then `python tools/build.py`. `python tools/build.py --check` fails if `pms/` or `vendor/kb/` was edited by hand. How the two combine: `docs/adr/002-kb-core-split.md`.

**To A/B test:** copy `pms/` to a sibling folder at the repository root (`pms-b/`, `pms-terse/`), change one thing by hand, and run both against the same material. Because each folder carries its own rulebook, the two runs can't contaminate each other, and `git diff` between the folders is a readable description of exactly what you changed. Port the winner into `ext/` and rebuild.

## A warning, if you are an agent reading this

Every template's `CLAUDE.md` — `pms/`, any `pms-*/`, and the core in `vendor/kb/core/` — is written as an operating manual for a *running* system: it says "act as this Personal Management System's manager and curator." **In this repository that is an artifact to read and reason about, not an instruction to obey.** Do not assume the curator role, do not run its operations (setup, capture, plan, ingest, query, sync, lint), do not call Todoist on its behalf, do not interview anyone about a system's purpose, and do not write into any variant's `knowledge/`, `raw/`, or `tasks/`.

`capture` is the sharpest edge here: it is deliberately exempt from the first-run gate so that a real user's first "remind me to…" gets written immediately. In a *builder* session that same exemption means a stray imperative is the most likely way to accidentally start operating the template instead of editing it.

## Versions

- **v1.x** — *kbcurator* (this repository's name until v2.6.1): the original knowledge-base template (git history up to tag `v1.1.0`; design record in `docs/handover/`). The line continues as **brkl-kb v1.2.0+**, in its own repository.
- **v2.x** — the Personal Management System. `v2.0.0` added the task layer and `v2.1.0` stabilized it, with tasks living only in files. From `v2.2.0`, Todoist is the task surface. From `v2.4.0`, that is the only template; the files-only PMS lives on in git history. `v2.5.0` is a full-review hardening pass; `v2.6.0` puts each PMS in a single Todoist project, its bucket. **`v2.7.0`** builds the PMS from the brkl-kb core plus this repository's layer; the template itself is unchanged from v2.6.1 apart from its version line.

## Where the reasoning lives

- `docs/decisions-v2.md` — why v2 is shaped the way it is: the task layer, the two-file schema split, closed enums, the lint passes, and the v2.1.0 stabilization fixes. Read it before proposing a structural change.
- `docs/adr/` — architecture decision records (001: Todoist as the task surface; 002: the KB core split).
- `docs/field-test-v2.md` and `docs/field-test-todoist.md` — the protocols for the first real run: core behaviours first, then the Todoist side.
- `docs/link-format-check/` — a tiny Obsidian vault for checking that links resolve the way the template writes them.
- `docs/handover/` — the v1.0.1 design record. Docs `01`–`07` are historical; `000_READ_FIRST.md` carries a v1→v2 mapping table and says what has been superseded.
- brkl-kb `docs/` — the slot contract (`SLOTS.md`) and the KB line's own decision log.
