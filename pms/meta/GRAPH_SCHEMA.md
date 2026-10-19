# Graph Schema

The **closed vocabulary** of this Personal Management System: which kinds of thing may exist, and which kinds of relationship may connect them. Every operation reads this file. Nothing outside these lists may be written — propose an addition here (via the setup skill) rather than inventing one.

This is one of exactly two files the agent may edit. The other is `meta/SETTINGS.md`, which holds this PMS's *state and configuration* (purpose, language, setup flag). The split is deliberate: this file is a vocabulary that grows and is diffed when it changes; the other is configuration, written once and rarely again. The static rules live in `CLAUDE.md` and are never edited.

## Nodes

Node types active in this PMS. Every page in `knowledge/` declares one in its `type:` field. Ships with two generic defaults; first-run setup adds PMS-specific ones. For each type: its name, what it represents, its fields, and its template file (if any).

- **`entity`** — a specific thing (a person, place, work, object, event). Fields: `title`, `aliases`, `tags`, typed-edge fields, `sources`, `see_also`. Template: none (follows the generic seed `meta/templates/_node.template.md` shape).
- **`concept`** — an idea, theme, or topic. Fields: same as `entity`. Template: none (same seed shape).

<!-- Add PMS-specific node types here during setup, e.g.:
- `person` — a human relevant to this PMS. Fields: title, aliases, role, org, edges, sources, see_also. Template: meta/templates/person.md
- `project` — a piece of work. Fields: title, status, edges, sources, see_also. Template: meta/templates/project.md
Each new type: (1) copy meta/templates/_node.template.md to meta/templates/<type>.md, (2) register it here. -->

## Tasks

`task` is a node type like any other for the purposes of the graph — it carries typed edges, it is traversed, it appears in `meta/GRAPH_INDEX.md`. It differs in exactly two ways, and only these two:

1. **It lives in `tasks/`, not `knowledge/`** — because it has a completion lifecycle, while knowledge nodes accrete.
2. **It is not required to have `sources:`** — a task usually originates from a human intent, not from a file in `raw/`. Its `origin:` field records where it came from instead.

Unlike node types under **Nodes**, the task schema is **fixed** — it is not extended per PMS. Adding a field to it changes what every capture writes, so treat it as a rulebook-level change, not a setup-time one.

**Fields.** `type` (always the literal `task`), `id`, `title`, `status`, `origin`, `created`, `updated` are required. `due`, `owner`, `tags`, `notes` are optional and omitted entirely when unknown — never filled with a placeholder. `closed` is required **once and only once the status is terminal**. Template: `meta/templates/_task.template.md`.

`closed` exists because `updated` cannot answer "how long has this been done?" — `updated` bumps on any edit, so a task finished two months ago and touched yesterday looks fresh. Without a separate date, the archive window is unenforceable and lint's archivable check is guesswork. Set `closed` to the date the status became `done` or `dropped`; clear it if the task is ever reopened.

**`status` — closed enum, exactly five values:**

| status | meaning |
|---|---|
| `open` | captured, not started |
| `doing` | actively in progress |
| `blocked` | cannot proceed; what it waits on is a `depends_on` edge or a `notes` line |
| `done` | completed |
| `dropped` | deliberately abandoned — kept, never deleted |

`done` and `dropped` are the two **terminal** states, and the only ones eligible for `tasks/archive/`. There is no sixth value and no free-text status; a state you cannot express with these five is a `notes` line, not a new status.

**Archiving removes the index entry.** A task in `tasks/archive/` is out of `meta/GRAPH_INDEX.md` entirely — exactly like an archived source in `raw/archive/`. This is what keeps the index bounded: tasks are the fastest-growing file type in the system, and an index that accumulates every one of them forever defeats the "one cheap read" that capture and query triage both depend on. Archived tasks keep their frontmatter and their edges; they are found by scanning `tasks/archive/`, which only a history question does.

**`origin` — closed enum, exactly three values:** `capture` (a human said so), `ingest` (an action item extracted from a source in `raw/`), `query` (surfaced while answering). When `origin` is `ingest`, the task also carries `sources:` pointing at the archived source — that is the one case where a task has provenance.

**Ownership.** `owner` is a **plain string field**, not a typed edge, because a PMS with no `person` node type has nowhere to point. If this PMS later registers a `person` type, setup should offer to promote `owner` into an `assigned_to` typed edge and register the predicate below. Until then, do not write `assigned_to`.

## Edges

The predicates (typed-edge field names) active in this PMS. The same vocabulary governs `knowledge/` and `tasks/` — a task does not get its own predicate set. Setup may add PMS-specific ones. Edges are directional; only the forward field is stored on the origin page (inverses are for reading). A predicate marked **(symmetric)** in the inverse column is the exception — it is written on both pages. That marker is load-bearing: it is what makes the mirroring rule in `CLAUDE.md` fire, so mark any new symmetric predicate accordingly. Do not invent predicates outside this list — propose additions here instead.

| predicate (field) | meaning (A → B) | inverse |
|---|---|---|
| `is_a` | A is an instance/subtype of B | `has_instance` |
| `part_of` | A is a component of B | `has_part` |
| `based_on` | A is built on / derived from B | `basis_for` |
| `authored_by` | A was created by person/org B | `authored` |
| `uses` | A makes use of B | `used_by` |
| `depends_on` | A requires B to function | `depended_on_by` |
| `introduced_by` | A was surfaced to me via source or person B | `introduced` |
| `about` | A (a page/note/task) is about topic B | `subject_of` |
| `supports` | A is evidence/argument for B | `supported_by` |
| `contradicts` | A conflicts with B | `contradicts` (symmetric) |
| `contrasts_with` | A is compared against B | `contrasts_with` (symmetric) |
| `precedes` | A comes before B in time/sequence | `follows` |
| `member_of` | A belongs to group/collection B | `has_member` |
| `located_in` | A is situated in B | `contains` |

**Tasks reuse this vocabulary — they do not need additions to work.** The common task relationships already have predicates: a subtask is `part_of` its parent; a blocked task `depends_on` what it waits for; a task is `about` the topic or project it concerns; a task extracted from a source is `introduced_by` that source. Reach for an existing predicate before proposing a new one — the value of a closed vocabulary is that it stays small.

<!-- Add PMS-specific predicates here during setup, e.g. for a book: `ally_of`, `enemy_of`;
for a work PMS: `owns`, `assigned_to`. Keep the list closed and small. -->
