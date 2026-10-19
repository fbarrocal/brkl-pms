# ADR-001 — Todoist as the task surface; the PMS as the planner

- **Status:** Accepted (2026-10-19). Applies to the `pms-todoist/` variant (v3.0.0). The plain `pms/` variant is unchanged.
- **Decider:** Fernando

## Context

The v2 task layer lives only in markdown files. It has no notifications, no presence on phone or watch, and no quick capture away from a computer. The goal is to keep what the PMS does well — breaking work down, tracking dependencies, linking tasks to knowledge — and let Todoist handle what it does well: devices, reminders, dates, and checking things off.

Constraints verified against the account on 2026-10-19 (read-only inspection plus a temporary sandbox project, since archived):

| Fact | Evidence |
|---|---|
| Plan is **Todoist Free** | `user-info` |
| Free plan: 5 active personal projects, 20 sections per project, 300 active tasks per project, 3 filter views, 1 week of activity history, task reminders only | Third-party pricing summaries; project count not hit-tested |
| **Deadlines are Pro-only** | API returned `403 PREMIUM_ONLY` on the sandbox |
| **Completing a parent completes all its open subtasks** | Sandbox: an open subtask was completed ~0.1 s before its parent |
| Task descriptions survive completion and are searchable (substring match) | Sandbox: `find-completed-tasks` and `find-tasks searchText` |
| Updating `labels` **replaces** the whole list | Tool contract; sandbox |
| No native task dependencies | Todoist docs; not present in the API surface |
| Writes made through the connector show `client: "Claude"` in the activity log | Sandbox `find-activity` |
| Todoist IDs are not permanent: the 2025 API v1 migration replaced every ID | Todoist / Airbyte migration notes |

Existing account content: Inbox (9 old items), projects *Saúde*, *Gaming*, *Vida Digital*, no sections, no labels before this work. `pms-blocked` and `pms-dropped` labels were created during the sandbox test and kept for real use.

## Decision

**Split ownership by field.**

- **Todoist is authoritative for execution state:** done or not, due date, priority, reminders, and the task title as you last edited it.
- **The PMS files are authoritative for structure:** decomposition (`part_of`), dependencies (`depends_on`), subject (`about`), placement (area/project → Todoist project/section), `dropped` status, and the reasons behind them.

**Mapping (Free-plan aware):**

| PMS | Todoist | Why |
|---|---|---|
| `area` node | project | Few, long-lived — fits the 5-project cap. Existing projects (*Saúde*, *Gaming*, *Vida Digital*) become areas. |
| `project` node (`part_of` an area) | section in the area's project | Many, short-lived — 20 per area. Uses both sections and projects as requested. |
| task directly under a project | task in that section | — |
| task `part_of` another task | subtask | Todoist nesting, so phones show the tree. |
| grouping task (has children, created by `plan`) | **uncompletable** parent | Completing a parent cascades to open subtasks (verified). An uncompletable header can't be ticked by accident. The PMS closes it when every child is terminal. |
| `depends_on` | `pms-blocked` label + `Waiting on:` line in the description | No native dependencies. **The whole tree is pushed**; blocked items are visible but labelled. |
| `done` | completed | — |
| `dropped` | completed + `pms-dropped` | Todoist has no "abandoned" state; never delete. |
| `due` | due date | `deadline` stays PMS-only until the account is on Pro. |
| task id `T-0042` | description footer `PMS: T-0042` | The join key. Todoist ids are stored as `todoist_id`, but never used as identity. |

**One skill owns every Todoist call:** a new `sync` skill. `capture` and `plan` write files and then call `sync` to push. Query reads Todoist through `sync` for fresh state. This follows the existing skill-composition rule.

**Reconciliation runs on a schedule** (daily Cowork scheduled task) and on request. On Free, activity history is one week, so a gap of more than six days is reported as a risk.

## Alternatives considered

1. **One-way projection (files own everything).** Rejected: anything checked off or added on the phone is lost or overwritten.
2. **Todoist owns tasks entirely; the PMS keeps only plans.** Simplest, with no sync. Rejected: tasks leave the graph, dependencies become fragile description text, and "what's blocking X" stops being a graph question.
3. **Push only actionable steps.** Rejected by Fernando in favour of the whole tree: visibility on the phone matters more than a clean list.
4. **PMS project ↔ Todoist project, phases ↔ sections.** Cleaner, but blows through the Free 5-project cap after two projects. Revisit if the account goes Pro (the mapping table above is the only thing that changes).

## Consequences

- **Invariant amended:** "files are the source of truth" now reads "files are the source of truth for knowledge and structure; Todoist is the source of truth for execution state." This is a v3 change, hence a separate variant.
- **The variant requires a connector.** Without Todoist reachable, capture still writes the file and marks it pending push. Sync catches up later. Nothing is lost, but phone state is stale until then.
- **Sync is instruction-strength for now** (Claude through the connector). The plan is to move it into a script once the mapping is proven in the field — see the next-phase notes in `../decisions-v2.md`.
- **Label writes must merge.** Because `labels` replaces the list, sync reads the current labels and adds or removes only `pms-*` ones. Clobbering your own labels is the failure this rule prevents.
- **Titles can be edited on the phone.** Sync adopts the new title. Links stay valid because task links resolve by file stem (v2.1.0). Only the display text goes stale, and lint reports it as housekeeping.
- **Recurring tasks are out of scope.** A recurring task never reaches "done", so it can't carry graph state. Sync leaves them alone and lists them once.
- **The Inbox is not auto-adopted.** Tasks added on the phone inside a managed section are adopted automatically. Inbox items are offered for triage, because the Inbox holds years of unrelated items.

## Unproven (field test before relying on it)

- Uncompletable parents behave as headers on mobile and block accidental completion. [Likely, not yet tested]
- Whether `find-completed-tasks` on Free returns completions older than a week. [Guessing]
- Whether the account can add a saved filter beyond the Free 3-view cap (it already shows 6 legacy filters). [Guessing]
- Whether the per-run token cost of a daily full reconcile is acceptable.
