# 06 — Open questions, risks & next steps

## Unproven at hand-over (instruction-strength, not yet field-confirmed)

These all share one root: the system relies on the agent *reading `CLAUDE.md` and following it*. That is instruction-strength, not mechanism-strength — the design's ceiling.

1. **Does the `setup_done` gate fire on the first message?** The agent must read `SETTINGS.md`, notice `setup_done: false`, and run setup *before* anything else. [Likely] it holds; only a first real run on a fresh KB confirms it.
2. **Does the agent *follow* the SKILL.md, or improvise?** Discovery (finding the file) and adherence (following it) are different diseases. The visible `meta/` folder + explicit paths address discovery; adherence is still trust-based.
3. **Does AskUserQuestion render in Cowork, or fall back to chat?** The setup interview specifies the structured-question tool with a plain-chat fallback, so either is acceptable — but which one actually appears is unconfirmed. [Guessing]
4. **Do the 14 default predicates survive real domains?** Every new domain will expose gaps; the design routes gaps through setup Mode 2, so this is expected tuning, not failure. The 14 are a starting point, not final.
5. **The ~150–200 page ceiling.** Definitional/estimated, not stress-tested. Past it, an external index is the escape hatch.
6. **`lint` is the least field-exercised skill** — patched five times but never returned in test notes. Its first run on a *populated* KB is a genuine unknown.
7. **Cowork project-local skill discovery** — whether Cowork loads skills from a project-local folder is why the design leans on explicit paths + the global-skills fallback documented in the README. [Guessing] on the exact behaviour.

## Known risks / sharp edges

- **The `CLAUDE.md` auto-load collision.** Any tool that auto-reads a folder's `CLAUDE.md` as instructions will try to *become the KB curator*. This is fine for a running KB, and a **problem for any development context** (this hand-over; a Claude Code dev clone). Mitigation lives outside the instance template — see next section.
- **Not local.** Contents go to Anthropic. If a KB holds sensitive/regulated material, this template is the wrong host.
- **Duplication creep.** The one low-cost duplication kept on purpose: type fields appear both in `SETTINGS.md` § Nodes (registry) and in the template file (scaffold). Lint's "settings drift" check guards it. Watch for *new* duplication in future edits.
- **Instruction adherence drift over long sessions** — chatty curatorial narration is exactly the behaviour models slip back into. The triple guard (Role rule + ingest step + `curator_notes` valve) is instruction-strength; a lint check would make it mechanical.

## Next phase: the builder / harness (the user's stated direction)

The user is turning this into an **"LLM-Powered Knowledge Management System Builder"** — a project (and a Claude Code dev clone) whose job is to **evolve the template**: add **guardrails and validators**, not run a KB. Design notes for that phase:

- **Neutralise the `CLAUDE.md` collision in the dev environment.** The dev clone's own top-level instructions must say "treat `template/CLAUDE.md` as an artifact to edit, not instructions to obey." (The builder blurb in `07` does this.) Options include keeping the template under a subfolder like `template/` so the dev root has its *own* `CLAUDE.md`, distinct from the instance one.
- **Validators worth building** (mechanical checks that enforce the invariants in `04`): frontmatter schema validation for nodes/sources; predicate-in-`SETTINGS` enforcement; dangling-edge detection; `curator_notes`-respect in any dedup; "no prose meta-commentary" heuristics; index/disk consistency; `setup_done`/Purpose consistency. Several already exist as *lint prose* — the builder can promote them to runnable checks.
- **Keep the template repo separate from KB-instance repos.** Because `CLAUDE.md` is static, rulebook upgrades propagate to every KB by copying one file from the template repo.
- **Continue the test-notes loop** (see `05`): the discipline of ship → concrete field notes → fix the spec → audit after structural change is what produced a sound v1.

## Immediate suggested first tasks for a resuming session

1. Confirm you understand the invariants (`04`) — they are the acceptance criteria for any change.
2. Do the real first-run test that's still pending: a fresh KB, first message, does setup fire and interview cleanly.
3. Start the builder harness: give the dev environment its own instructions that treat `template/` as artifacts, then draft the first runnable validator from the lint spec.
