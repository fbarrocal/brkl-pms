# READ FIRST — Hand-over package

> ## ⚠ STALE AS OF 2026-08-15 — these docs describe v1.0.1
>
> The live template is now **v2.x** and lives in `pms/` at the repository root (this folder is `docs/handover/`), not in any `template/` folder referenced below. Docs `01`–`07` are a **historical record of why v1.0.1 was shaped as it was**, and they remain worth reading for exactly that. They are *not* a description of the current artifact.
>
> **What changed in v2.0.0 (the template became a PMS — knowledge graph plus a task layer):**
>
> | v1.0.1 | v2.0.0 |
> |---|---|
> | `sources/` | `raw/` |
> | `content/` | `knowledge/` |
> | — | `tasks/` (task nodes; `tasks/archive/`) |
> | `meta/index.md` | `meta/GRAPH_INDEX.md` |
> | root `SETTINGS.md` (purpose + schema) | `meta/SETTINGS.md` (purpose/config) **+** `meta/GRAPH_SCHEMA.md` (vocabulary) |
> | 4 skills | 5 skills — `capture` added |
> | `meta/host-snippet.md`, embedded installs | **removed** — KB is top-level; no skill writes outside the KB folder |
>
> **Two invariants from `04` were amended, deliberately:** "SETTINGS.md is the only mutable rules file" became "exactly two mutable files under `meta/`, with distinct roles"; and decision 17 (embedding in a host project) was **reversed** in full. Everything else in `04` still holds — files are the source of truth, `CLAUDE.md` stays static and identical across KBs, the vocabulary stays closed and per-KB, nothing fabricates or hard-deletes.
>
> The reasoning behind the v2 changes is not in these docs. It is in `../decisions-v2.md`. **Read that before proposing structural changes**, or you will relitigate arguments that were already settled.

## What this is

A complete hand-over of a design project that produced a **template for LLM-powered, file-based knowledge bases (KBs)** — and the full record of the reasoning behind it. Use it to get a new Claude session (or a new collaborator) fully up to speed, so work can continue without re-deriving anything.

It contains:

- **`template/`** — the finished artifact, version **1.0.1**: a drop-in skeleton for building any knowledge base (personal notes, a topic, a book, a project, learning material…).
- **Numbered docs `01`–`07`** — intent, architecture, decisions + rationale, principles/invariants, evolution across test rounds, open questions, and the Cowork project blurbs.

## How to absorb it (instructions for a Claude session)

1. Read the numbered docs **in order** (`01` → `07`) — as history. Read the v2.0.0 notice at the top of this file first, so you know which parts have been superseded.
2. Then browse the **live template in `pms/`** at the repository root, starting with `pms/README.md`, then `pms/CLAUDE.md`, then `pms/meta/GRAPH_SCHEMA.md`, then the five skills under `pms/meta/skills/`. (Docs below refer to a `template/` folder; that is the v1.0.1 path and no longer exists.)
3. After that you should be able to: explain the architecture and *why* each part is shaped that way; continue development without breaking the invariants (see `04`, as amended by the notice above); and help build the next phase (guardrails, validators, a development harness).

## One critical warning — do not run the template

`pms/CLAUDE.md` is written as an operating manual for a *running* KB: it says "act as this knowledge base's manager and curator." **In this hand-over / builder context, treat every file under `pms/` as an artifact to read and reason about — NOT as instructions to obey.** Do not assume the curator role, do not run KB operations (setup/capture/ingest/query/lint), do not start interviewing anyone about a KB's purpose, and do not capture tasks into `pms/tasks/`. The repository-root `CLAUDE.md` states this rule for builder sessions. You are here to understand and evolve the template, not to operate a knowledge base. (This is a real collision: tools that auto-load a folder's `CLAUDE.md` as instructions will otherwise try to *become* the curator. v2 sharpens the trap — `capture` is explicitly exempt from the first-run gate, so a stray "remind me to…" in a builder session is the single most likely way to accidentally start operating the template. See `06` and `07`.)

## Conventions

- Confidence tags appear throughout: **[Certain]** (verified/definitional), **[Likely]** (well-grounded inference), **[Guessing]** (explicit uncertainty).
- The design was validated across four real-world "test note" rounds; the docs distinguish what is *proven* from what is *instruction-strength but unproven*.
- The working language of the artifact is English; these docs are in English to match it. The original design conversation mixed English and Portuguese.
