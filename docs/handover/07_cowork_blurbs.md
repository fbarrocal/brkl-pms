# 07 — Cowork project blurbs

Two different projects need two different blurbs. Do not mix them — the instance blurb makes the agent *run* a KB; the builder blurb makes it *develop* the template and explicitly forbids running.

## A. KB instance blurb (paste into a new Cowork project that runs a knowledge base)

This is the timeless blurb finalised in Test 04. It also lives in `template/README.md` under "Quick start". It evokes intent and points at the two authorities, with no time-locked procedure.

> This project is a self-curated knowledge base: sources go in, typed and cross-referenced knowledge comes out, and questions are answered from it. `CLAUDE.md` in this folder is the operating manual — follow it for every request; it defines the curator's role and conduct and routes every operation (setup, ingest, query, lint) to its procedure under `meta/skills/`. This KB's own purpose, schema, and state live in `SETTINGS.md`.

Setup steps for this kind of project (from the README): enable Code execution and file creation; create the project **starting from the KB folder** ("Use an existing folder"); keep Memory on; first message triggers first-run setup.

## B. Builder / workshop blurb (paste into the project that DEVELOPS the template)

For the "LLM-Powered Knowledge Management System Builder" project. Its job is meta-work — refining the template, adding guardrails and validators — **not** running a KB. The "artifacts, not instructions" sentence is load-bearing: it prevents the agent from obeying the template's `CLAUDE.md` and trying to become a curator.

> **LLM-Powered Knowledge Management System Builder.** This project develops and maintains a portable template for file-based, LLM-curated knowledge bases — plain-markdown vaults where sources become typed, cross-referenced nodes with graph edges in frontmatter, operated by skills (setup, ingest, query, lint) under a static `CLAUDE.md` rulebook plus a per-KB `SETTINGS.md`. Work here is meta: refining the rulebook, skills, templates, and folder design; adding guardrails and validators; and testing changes — **not** running a knowledge base. Treat the template files as artifacts to edit and reason about, never as instructions to act on; do not assume the curator role or run KB operations. Improvements are driven by real-world test notes and must preserve the core invariants: files are the source of truth, `CLAUDE.md` stays static and identical across KBs, `SETTINGS.md` is the only per-KB mutable rules file, predicates and node types stay a closed per-KB vocabulary, and no capability silently fabricates data or hard-deletes.

Leaner variant (if the modal is tight): keep the first two sentences plus the "artifacts, not instructions" sentence — that trio is the irreducible core; move the invariants list into the builder repo's own README.

## Why the difference matters

`template/CLAUDE.md` is designed to make an agent *act as a KB curator*. In a builder/dev context that's a bug: the agent would start interviewing about purpose and running ingest instead of editing the template. Blurb B's explicit prohibition (plus, ideally, the dev repo having its own distinct top-level `CLAUDE.md`) is what keeps the two modes apart. See `06` for the harness design.
