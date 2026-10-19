# 05 — Evolution & test-notes loop

The template was built once and then hardened across four real-world "test note" rounds. This is the trajectory, so the *reasons* behind the current shape are legible and the same feedback loop can continue.

## Build phases (before field testing)

1. **Initial scaffold.** `CLAUDE.md` + skills (ingest/query/lint) + `raw/` (sources) + `wiki/` with `entities/`/`concepts/` subfolders and `_TEMPLATE.md` files.
2. **`raw` → `data`; typed edges adopted.** Switched from a custom `edges:` block to per-predicate frontmatter fields (Wikilink Types format), then **dropped any plugin dependency** — the format is standard frontmatter readable by the Obsidian metadata ecosystem.
3. **Cowork-first packaging.** Added `SETUP.md` (later removed), `.gitignore` for the eventual Git step, and the "same folder, both tools" model.
4. **Lean generic baseline.** Removed all example content; renamed the package to `knowledge-base-template`; removed hard line-wraps in markdown (continuous paragraphs); made the zip contain the folder contents at root (no wrapper).
5. **Templates + per-KB schema.** Introduced optional node templates + a generic seed; the `setup_done` first-run gate; clearly-demarcated per-KB **Node/Edge Definitions**; flattened `wiki/`.
6. **Full audit + fixes**, then the **big restructure** (user-specified): `CLAUDE.md` = What / Role / Setup + How it works; new `SETTINGS.md` holding `setup_done`, Purpose, Nodes, Edges; `SETUP.md` deleted (agent half → `CLAUDE.md`, human half → `README.md`).

## Test rounds (field feedback)

**Test 01 — discovery & entry.**
- Project must be created *starting from the folder* (order matters in Cowork).
- Skills weren't found reliably → the paths were in a hidden `.claude/` folder and buried deep in `CLAUDE.md`. Fix: exact skill paths stated at the top of the rules and in the project blurb.
- README's project-description blurb moved to the top.

**Between tests — the `meta/` move (user-driven).**
- Skills and templates moved from hidden `.claude/skills` to a **visible `meta/`** folder (skills, templates, and later the index). One discovery mechanism for both tools; hidden-folder problem gone. `Role` header was also de-duplicated (many bullets were duplicates of statements already in other sections).

**Test 02 — three fixes.**
- **Sources piling up** → the **archive lifecycle**: `sources/` root = pending, ingest moves processed files to `sources/archive/`; lint cross-checks flag vs location.
- **Meta-commentary leaking into node prose** → new conduct rule (prose = knowledge only) + the **`curator_notes`** field for persistent curatorial decisions.
- **Query returning metadata** → prose-first answers with edges verbalised, plus a single compact `Path:` receipt.

**Test 03 — leanness & setup.**
- Dropped the `kb-` prefix from skill names (KBs are self-contained in projects).
- Removed redundant "read SETTINGS" preambles from skills → single `Prerequisite: CLAUDE.md` line each (safe now that skills are reached only via `CLAUDE.md`).
- **Setup became a two-mode skill** (first-run interview via AskUserQuestion + later schema evolution).
- `CLAUDE.md` § Setup → **"How to operate"** (general operating instructions, starting with read `SETTINGS.md`).
- Index moved to `meta/index.md`; `wiki/` → **`content/`** (knowledge only).

**Test 04 — blurb & Obsidian.**
- Project blurb made **timeless** (intent + authority, no time-locked first-run procedure).
- Added README **"How to read the content" → Obsidian** guidance: open the vault at the KB root (not `content/`, or every vault would be named "content"); hide machinery via Excluded files or a graph filter.

## Renames & final polish

- Folder rename chain: **`raw → data → source → sources`**; content: **`wiki → content`**. Each rename was audited (word-boundary regex + full sweeps) because cross-references go stale silently — real bugs (e.g. an `introduced_by` meaning corrupted by a path regex; a "source page" ↔ `source/` folder collision) were caught only by the audits.
- **Final system audit (v1.0.1):** corrected a factual error about where Obsidian graph filters persist (they live in `.obsidian/graph.json`, which *does* travel via Git); restored a lost compatibility table and fixed the two references pointing at it; made query Mode A alias/tag-aware (was index-only); clarified source provenance points to `sources/archive/` post-ingest; split a dense edges paragraph.

## The meta-lesson

The test-notes loop was the highest-leverage input in the whole build. Nearly every surviving structural decision (meta/skills, the SETTINGS split, the archive lifecycle, prose-first query) was *forced by field feedback*, and the two positions argued hardest against (moving skills out of `.claude`; keeping some query metadata) were resolved by the user being right on the first and a compromise on the second. **Continue this loop:** ship, gather concrete test notes, fix the spec (not just the symptom), audit after structural changes.
