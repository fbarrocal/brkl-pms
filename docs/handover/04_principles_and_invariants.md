# 04 — Principles & invariants

These are the load-bearing constraints. **Any future change to the template must preserve them**, or it is changing the architecture rather than improving it. Use this as a standing checklist when evaluating a proposed edit or a new guardrail/validator.

## Invariants (do not violate)

1. **Files are the source of truth.** No external database, no embeddings. Canonical knowledge lives in `sources/` + `content/`, never in any tool's memory.
2. **`CLAUDE.md` is static and identical across all KBs.** The agent never edits it. All per-KB variation goes in `SETTINGS.md`.
3. **`SETTINGS.md` is the only mutable rules file.** Purpose, Nodes, Edges, `setup_done`. Edited only by the setup skill (or the user).
4. **Node types and edge predicates are a closed, per-KB vocabulary.** Registered in `SETTINGS.md`. The agent **proposes, never invents** — additions need user approval.
5. **No fabrication.** Template/type fields are *optional scaffolding*; fill only what sources support. Never invent a value to fill a field.
6. **No silent overwrites; no hard-deletes.** Conflicts are recorded as `contradicts` and surfaced. Deletions/removals need explicit confirmation (and, for schema, a migration plan).
7. **Prose is for knowledge; plumbing stays invisible.** Node bodies and query answers speak about the *things*, never narrate pages/edges/fields/curatorial process. Persistent curatorial decisions live in `curator_notes`, never in prose.
8. **Edges live only in per-predicate frontmatter fields.** Prose `[[wikilinks]]` and `see_also` are not typed edges and are never traversed. Only the forward field is stored.
9. **`sources/` bodies are immutable.** Ingest may change only bookkeeping frontmatter (`ingested`, `touches`) and file location (→ `sources/archive/`).
10. **Two tools, one folder, never simultaneously.** Cowork and Claude Code share the folder; each keeps its own session state elsewhere; the files are the shared layer.

## Design principles (the "why", to guide judgement)

- **Single source of truth for every concept.** The vocabulary lives in exactly one place (`SETTINGS.md`); procedures in exactly one place (`meta/skills/`); the rulebook in one place (`CLAUDE.md`). Duplication is the enemy — it was removed repeatedly (e.g. skills stopped repeating "read SETTINGS"; the project blurb stopped repeating the gate logic).
- **The bottleneck is maintenance, not storage.** Every feature should reduce upkeep, not add it. Archiving, lint, and the curator-does-the-structuring model all serve this.
- **Type is a field, not a folder.** Both `sources/` and `content/` are flat; classification is metadata. (Lifecycle *is* allowed as a folder — hence `sources/archive/` — a different axis from type.)
- **Discovery/adherence is instruction-strength, not mechanism-strength.** The system relies on the agent reading `CLAUDE.md` and following it. This is the design's ceiling and the source of most residual risk (see `06`). Improvements that make adherence more robust (e.g. lint checks that catch violations mechanically) are high-value.
- **Auditability over convenience where they conflict.** The `Path:` receipt in queries, the `contradicts` edges, the provenance in archived sources — all exist so synthesis can be trusted, not just produced.
- **Genericity is a mechanism, not a catalog.** The template ships the *ability* to define types/edges, plus sensible defaults — not a fixed domain schema.

## The "meta-work vs. run" boundary (critical for anyone editing this)

The template's `CLAUDE.md` tells an agent to *become a KB curator*. When you are **developing** the template (this hand-over context, or a Claude Code dev clone), you must **not** obey that — treat the files as artifacts. A tool that auto-loads the folder's `CLAUDE.md` will otherwise start running the KB. The builder/dev environment must neutralise this (see `06` and the builder blurb in `07`).
