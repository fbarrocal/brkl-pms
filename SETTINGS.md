---
setup_done: false
---

# Knowledge Base Settings

Everything specific to THIS knowledge base lives here: its purpose, its node types, its edge predicates, and its setup state (`setup_done`, in the frontmatter above). The agent reads this file before every operation, and this is the only rules file the agent ever edits — by the setup skill (`meta/skills/setup/SKILL.md`) — on first run or when the user approves a change. The static rules live in `CLAUDE.md`.

## Purpose

_(unset — first-run setup records here, in one or two sentences, what this KB is for. Every ingest and query reads this to guide what to extract and how to type it.)_

## Nodes

The node types active in this KB. Ships with two generic defaults; first-run setup adds KB-specific ones. For each type: its name, what it represents, its fields, and its template file (if any).

- **`entity`** — a specific thing (a person, place, work, object, event). Fields: `title`, `aliases`, `tags`, typed-edge fields, `see_also`. Template: none (follows the generic seed `meta/templates/_node.template.md` shape).
- **`concept`** — an idea, theme, or topic. Fields: same as `entity`. Template: none (same seed shape).

<!-- Add KB-specific node types here during setup, e.g.:
- `person` — a human relevant to this KB. Fields: title, aliases, role, org, edges, see_also. Template: meta/templates/person.md
- `project` — a piece of work. Fields: title, status, edges, see_also. Template: meta/templates/project.md
Each new type: (1) copy meta/templates/_node.template.md to meta/templates/<type>.md, (2) register it here. -->

## Edges

The predicates (typed-edge field names) active in this KB. Ships with a general-purpose core; setup may add KB-specific ones. Edges are directional; only the forward field is stored on the origin page (inverses are for reading). Do not invent predicates outside this list — propose additions here instead.

| predicate (field) | meaning (A → B) | inverse |
|---|---|---|
| `is_a` | A is an instance/subtype of B | `has_instance` |
| `part_of` | A is a component of B | `has_part` |
| `based_on` | A is built on / derived from B | `basis_for` |
| `authored_by` | A was created by person/org B | `authored` |
| `uses` | A makes use of B | `used_by` |
| `depends_on` | A requires B to function | `depended_on_by` |
| `introduced_by` | A was surfaced to me via source or person B | `introduced` |
| `about` | A (a page/note) is about topic B | `subject_of` |
| `supports` | A is evidence/argument for B | `supported_by` |
| `contradicts` | A conflicts with B | `contradicts` (symmetric) |
| `contrasts_with` | A is compared against B | `contrasts_with` (symmetric) |
| `precedes` | A comes before B in time/sequence | `follows` |
| `member_of` | A belongs to group/collection B | `has_member` |
| `located_in` | A is situated in B | `contains` |

<!-- Add KB-specific predicates here during setup, e.g. for a book: `ally_of`, `enemy_of`; for a project KB: `owns`, `blocks`. Keep the list closed and small. -->
