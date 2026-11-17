# ADR-003 — The PMS template is self-contained

- **Status:** Accepted (2026-11-17). Supersedes ADR-002. Introduced in v2.8.0.
- **Decider:** Fernando

## Context

ADR-002 (v2.7.0) built `pms/` from an external knowledge-base core, vendored at a tag, plus a layer of fills in `ext/`, through a Python build. Fernando's assessment four days later:

- Changes to the template are deliberate and made by the builder. A source/build pipeline adds steps to every change without adding safety.
- The knowledge base and the PMS are separate products. A knowledge base can hold knowledge for any project, this one included, but that is a use, not a built-in dependency.
- Once a copy of the template is pulled elsewhere, it has to live by itself, with no builder and no other repository around.

## Decision

- **`pms/` is the template and the only copy.** It is edited directly. There is no `vendor/`, no `ext/`, no `tools/`, and no build or check step.
- **The PMS carries its own knowledge-graph machinery** (ingest, query, lint, the edge rules) in its own files, as it did through v2.6.1.
- **Nothing here depends on, refers to, or is generated from another repository.** A copy of `pms/` needs nothing from this repository or from anywhere else.

## Consequences

- v2.8.0's `pms/` is v2.6.1's text with a new version line. Nothing in `pms/` ever referred to the external core, so the reversal touched only the repository around it.
- **Fixes are not shared.** A knowledge-base template of the same lineage evolves separately; a fix made there reaches this template only if someone ports it by hand, and the reverse. Accepted.
- **Conventions are v2.6.1's again:** bump the version in `pms/README.md` and tag; A/B variants are hand-edited `pms-*/` siblings.
- **Still open, and exposed by ADR-002:** the task schema and the Todoist mapping are "fixed by the rulebook" but live in `meta/GRAPH_SCHEMA.md`, a per-instance mutable file. A rulebook upgrade therefore can't reach an existing PMS by copying static files, and the agent is technically allowed to edit rules it must never change. Moving them into a static file is cheapest before the first real PMS exists.
