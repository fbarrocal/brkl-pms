# ADR-002 — The knowledge base is its own template; the PMS builds on it

- **Status:** Accepted (2026-11-13). Introduced in v2.7.0, on brkl-kb v1.2.0.
- **Decider:** Fernando

## Context

Since v2.4.0 the only template was the PMS with Todoist, and the knowledge base existed only inside it. Some of Fernando's projects need a knowledge base and nothing else, so there was nowhere to start one: setup asked for a Todoist connection, a bucket and a sync schedule, and every rulebook file carried the task layer.

The coupling was not in one folder but in almost every file. In v2.6.1, the template's `CLAUDE.md` mentioned Todoist about 40 times and tasks about 70 times in 129 lines; lint, about 70 task mentions in 140 lines. Only `ingest` and the node template never mentioned Todoist. The task layer is woven into the shared rules, and one of those rules fails silently if it's cut wrong: the traversal set is `knowledge/` ∪ `tasks/`, and an inbound scan of one folder returns an empty "what's blocking X" that looks correct.

## Decision

**Two repositories, split at the source, combined at build time.**

- **brkl-kb** holds the knowledge base. Its `core/` is the template source with **slots**, marked places where an extension adds or replaces text. Built alone, it gives the KB-only template `kb/`.
- **brkl-pms** (this repository) vendors brkl-kb's `core/`, `core.json` and `tools/` at a tag into `vendor/kb/`. Its `ext/` holds fills for the slots plus the PMS-only files (capture, plan, sync, the task/area/project templates, `tasks/`). `tools/build.py` assembles the two into `pms/`, which stays the folder people copy.
- **The built template is one plain set of files**, exactly as explicit as before. The agent that runs it reads one `CLAUDE.md` with every rule inline, and never works out what's installed.
- **The pin is mechanical.** `vendor/kb/VENDOR.json` records the tag, the commit and a sha256 per file; the build refuses to run on an edited copy.

The split was cut as a pure refactor: the v2.7.0 build is byte-identical to v2.6.1's `pms/` apart from the version line.

## Alternatives considered

1. **Runtime plugin** (the core's skills check for installed extensions). It would let a PMS be added to an existing KB folder in place. Rejected: every hook becomes one more instruction the agent must remember on every operation, adherence is the least proven part of this design, and the traversal-set rule would sit behind that indirection.
2. **Two vaults, with the PMS calling the KB.** Rejected: tasks leave the graph (ADR-001 already rejected that), Obsidian links don't resolve across vaults, and two rulebooks in one session repeats decision 17's open risk.
3. **One template with a "tasks off" setting.** Cheapest, but it lets nothing evolve apart. Every KB edit would still happen inside files full of Todoist text.
4. **One repository holding both** (the recommendation at the time: slot changes would be atomic, one decision log, one tag). Fernando chose two repositories so the KB has its own identity and releases. The accepted cost: a change that needs a new slot is a brkl-kb release, then a vendor bump here.
5. **Vendoring mechanism:** a git submodule or a git subtree were alternatives to a pinned copy. A pinned copy was chosen. End users never need it (`pms/` is committed), there is no git plumbing to get wrong on Windows, and the hash check catches hand edits.

## Consequences

- **A change has to be put in the right repository first.** Anything true of every knowledge base goes to brkl-kb; anything about tasks, planning or Todoist goes to `ext/`.
- **180 slots, many of them a few words long.** That is the price of a byte-identical first cut: the PMS text was woven through the shared paragraphs, and this version doesn't restructure them. Fewer, larger seams are the next structural pass on both sides.
- **The build catches renamed and removed slots, not changed meaning.** After every vendor bump, read `git diff pms/`.
- **A latent breach is now visible, not yet fixed.** The task schema and the Todoist mapping are "fixed by the rulebook" but live in `meta/GRAPH_SCHEMA.md`, a per-instance mutable file. So a rulebook upgrade can't reach an existing PMS by copying static files, and the agent is technically allowed to edit rules it must never change. The split kept them there to stay byte-identical. Moving them into a static PMS file is a deliberate change for a later version.
- **The KB build gives up what only tasks needed:** scheduled tasks, the `Conventions` settings, and lint checks #14, #19 and #20 (the KB's check numbers have those gaps).

## Unproven

- The KB-only build has never been run (brkl-kb `docs/field-test-kb.md`).
- Whether fills written against one core version stay correct across core bumps in practice.
