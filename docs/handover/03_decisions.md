# 03 — Decision log (with rationale)

Each entry: the decision, why, and — where relevant — the tension or the position that was argued against and overruled. This is the "why", so future changes don't silently undo hard-won choices.

## Core architecture

1. **Graph over vector retrieval.** User's choice. Trade-off understood: graph wins multi-hop/"how does it connect", vector wins single-hop lookups. The design ended up **navigation-based with no embeddings at all** — "graph" here means *typed traversable relationships*, not GraphRAG-with-vectors.

2. **Entirely on Claude; files are the source of truth.** No external app, DB, or embeddings. Claude is curator + query engine. Rationale: collapses curator and graph into one artifact, removes the second pipeline and the drift between prose and a separate graph store. **Cost, stated plainly:** this is *not local* — contents go to Anthropic; and it has a scale ceiling (~150–200 pages).

3. **Typed edges as per-predicate frontmatter fields.** Chosen over a custom `edges:` block after the user referenced Obsidian's Wikilink Types plugin. Key realisation: that plugin's *storage* format is per-predicate frontmatter, which is also what Dataview/Breadcrumbs/Juggl/Graph Link Types read — so adopting it gives ecosystem compatibility for free, and **no plugin dependency** (the template writes the frontmatter directly; the plugin is only optional inline-authoring sugar).

4. **Static `CLAUDE.md` + mutable `SETTINGS.md` split.** User-proposed structure; accepted with two modifications (below). Rationale that earned agreement: it stops the agent from editing its own rulebook during setup, makes `CLAUDE.md` identical across KBs (upgrade-by-copy), and centralises per-KB state.

## Pushbacks made, and how they resolved

5. **"Karpathy LLM Wiki is not the typed graph you asked for."** Its connections are untyped `[[wikilinks]]`. It's the stronger *curator* pattern but fails the typed-graph requirement. Outcome: we took its *shape* (raw/ + authored wiki + ingest/query/lint + a schema file) and added real typed edges.

6. **"You can't get a powerful curator AND a real graph from one download — it's an architecture."** Led to the entirely-on-Claude, edges-in-markdown design (decision 2).

7. **`meta/skills/` — I initially resisted moving skills out of `.claude/skills/`** (that path is Claude Code's auto-discovery mechanism). **The user overruled** on the grounds that Cowork is the primary interface and needs a visible, findable folder. **I was wrong and conceded:** the move *improved* coherence — both tools now use one discovery mechanism (explicit paths in a visible folder), and the hidden-folder caveat disappeared. Cost accepted: Claude Code no longer auto-invokes the skills (it reaches them via `CLAUDE.md` routing), which is fine because Code is used explicitly for Git/batch.

8. **Deleting `SETUP.md` — redirected rather than accepted wholesale.** The agent-facing first-run procedure moved into `CLAUDE.md`; the *human* onboarding moved into `README.md` (it can't live in `CLAUDE.md` — it would be permanent context noise, and there's a bootstrap problem). Same file-count reduction, nothing lost.

9. **Typed inbox subfolders — declined.** User floated `inbox/meetings`, `inbox/notes`. Argued: type is a *field*, not a *folder*; folders force single membership and a capture-time decision. Resolution: flat inbox + `source:` frontmatter. (Consistent with the later "flat `content/`, type is a field" rule.)

10. **Data deletion — redirected to archiving.** Piling sources are the rebuild/audit/provenance substrate; deleting them makes the wiki unverifiable. Fix: `sources/` root = pending; ingest moves processed files to `sources/archive/`. Also resolved a latent contradiction ("`sources/` is immutable" vs "ingest sets `ingested: true`") — now precise: *body* immutable; bookkeeping frontmatter + location are sanctioned changes.

11. **Query returning metadata — challenged the framing, kept the receipt.** User: "stop answering with 'Page X correlates to Page Y through edge W'." Agreed the *narration* is wrong (it's a spec bug — the old skill mandated "show the path"). But killing the audit trail entirely loses the ability to tell a real traversal from a confabulated one. Resolution: answer in **prose** (edges verbalised via the meaning column), then **one compact `Path:` line** as the receipt.

## Choices that shaped the model

12. **Templates are optional; a generic seed is replicated per type.** Keeps the baseline generic (a mechanism, not a fixed catalog). New types are created on approval during setup.

13. **First-run gate via `setup_done`.** Ensures a new KB is configured to its purpose before any operation. Setup became a **two-mode skill** (first-run interview + later schema evolution) using AskUserQuestion with a chat fallback.

14. **`curator_notes` frontmatter field.** Solves a trap: the dedup step would eventually propose merging pages a human *deliberately* kept separate. Persistent curatorial decisions need a machine-readable home that's respected by dedup/lint but invisible in prose — precisely because "meta-commentary in prose" was a real test complaint.

15. **Conduct rules (in `CLAUDE.md` Role):** ground everything in sources (no fabrication); prose is for knowledge, plumbing stays invisible; propose-never-invent (new types/predicates need approval); never silently overwrite (use `contradicts`); never hard-delete without confirmation.

16. **Naming/structure evolution** (see `05` for the full chain): folders `raw → data → source → sources`; `wiki → content`; skills/templates/index consolidated under `meta/`. Each rename was audited because a cross-referenced system accrues stale references fast — several real bugs were only caught by post-rename audits.

## Deliberate non-decisions (things intentionally left out)

- No CHANGELOG/version file inside the template — Git covers that better.
- No guard inside the template against the "`CLAUDE.md` gets auto-read in the dev clone" collision — that belongs to the *builder* harness (see `06`/`07`), not the instance template.
- No forced templates for `entity`/`concept` — they use the generic shape to avoid looking like a fixed catalog.

## Addendum — 2026-07-24

17. **Embedded installs: self-contained `kb/` + host-pointer snippet.** Decided the KB embeds in host AI projects as one fully self-contained subfolder (conventionally `kb/`), `sources/` and `CLAUDE.md` included. **Rejected** the floated alternative of a top-level `sources/` outside the KB folder: it breaks the static-`CLAUDE.md` invariant (skills reference `sources/` relative to the KB root), severs relative-path provenance (`sources:`/`touches:` round-trips), and has KB machinery mutating host-owned files. Host integration is a marker-wrapped pointer block (`meta/host-snippet.md`, versioned `v1`) injected into the host's `CLAUDE.md`. The "don't forget it" guarantee rides the existing first-run gate: setup's Mode 1 gained an embedded-install check (propose-only; the single sanctioned write outside the KB folder), and lint gained check #14 (missing or version-lagging block). Open risk, no field evidence yet: nested-rulebook leakage — the curator role loading when a host agent merely reads `kb/content/`; a read-only scoping line in `CLAUDE.md` is the planned fix if it bites.
