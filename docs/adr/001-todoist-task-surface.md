# ADR-001 — Todoist as the task surface; the PMS as the planner

- **Status:** Accepted (2026-10-19). Introduced in v2.2.0 as a separate variant, and made the only template (`pms/`) in v2.4.0. The files-only task layer remains in git history (v2.1.0).
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

- **Invariant amended:** "files are the source of truth" now reads "files are the source of truth for knowledge and structure; Todoist is the source of truth for execution state." It shipped first as a separate variant (v2.2.0) and became the only template in v2.4.0.
- **The template requires a connector.** Without Todoist reachable, capture still writes the file and marks it pending push. Sync catches up later. Nothing is lost, but phone state is stale until then.
- **Sync is instruction-strength for now** (Claude through the connector). The plan is to move it into a script once the mapping is proven in the field — see the next-phase notes in `../decisions-v2.md`.
- **Label writes must merge.** Because `labels` replaces the list, sync reads the current labels and adds or removes only `pms-*` ones. Clobbering your own labels is the failure this rule prevents.
- **Titles can be edited on the phone.** Sync adopts the new title. Links stay valid because task links resolve by file stem (v2.1.0). Only the display text goes stale, and lint reports it as housekeeping.
- **Recurring tasks are out of scope.** A recurring task never reaches "done", so it can't carry graph state. Sync leaves them alone and lists them once.
- **The Inbox is not auto-adopted.** Tasks added on the phone inside a managed section are adopted automatically. Inbox items are offered for triage, because the Inbox holds years of unrelated items.

## Amendment — 2026-10-19: deployment model

**One PMS instance per Todoist account.** Plan limits are the account owner's to lift (upgrade), not a design constraint. Consequences applied in the template:

- **Connector authorization moved into setup** (Step 0, before the interview). The probe goes through sync. Credentials are never requested in chat. If the user declines, the knowledge side still works and tasks wait as pending push.
- **Every existing Todoist project is offered as an area by default.** It is the user's account, so opt-out replaces opt-in.
- **Scheduling the daily sync is a setup question (Q6),** created only on a yes.
- **The Free-plan cap check is removed** from sync and lint. A plan-limit refusal is reported, with an upgrade suggestion, and never worked around.

**Question this reopened (now closed — see below):** the area → project / project → section mapping was justified partly by the 5-project cap, and that justification no longer holds. The mapping still has independent merits: a short, stable Todoist sidebar and one place per area. But the alternative — **PMS project → Todoist project (sub-project of its area), phases → sections** — now competes on merit:
- sections give phases a native group that can't be ticked, so far fewer uncompletable headers;
- Todoist shares and archives per project, so a project can be shared with a collaborator or archived when finished;
- board view per project shows phases as columns;
- the cost is more projects and sidebar churn, and nested projects to manage.
**Decided 2026-10-19 (Fernando): keep the original mapping — area → Todoist project, project → section, phase → parent task that can't be ticked.** This time it is chosen on its merits: a short, stable sidebar, and good handling of small projects.

Costs accepted with it:
- **Phases rely on a workaround.** A phase is a parent task that can't be ticked, and only `plan` creates those. A parent you create yourself on the phone can still be ticked, and ticking it completes every step under it. Sync then records all of those steps as done.
- **A project can't be shared, archived or shown as a board on its own.** A finished project's section stays in its area. Sync offers to archive it rather than doing it, because the connector has no tool to archive a section — so far it has only been seen to update sections.

**Revisit triggers:**
- the first time a project has to be shared with someone;
- areas carrying more than about 10 live sections;
- phase-heavy plans producing many headers that can't be ticked.
If any of these happens, switch a project to its own Todoist project with phases as sections.

## Amendment 2 — 2026-10-20: one bucket per PMS

**A PMS is usually about one subject, so by default it lives in one Todoist project — its bucket.** The user's other projects and the Inbox are never read or written. This supersedes the 2026-10-19 rule "one PMS per Todoist account; every existing project offered as an area" (Fernando's decision).

- **Default `Mode: single`.** Exactly one `area` node, bound to the bucket. PMS projects are sections in it; phases are parent tasks that can't be ticked, as before. The mapping table above still applies, with one area.
- **`Mode: multiple`** keeps the original one-project-per-area mapping, but only when the user explicitly asks for it at setup (Q5) or later through setup Mode 2.
- **Setup Q5 offers:** a new project named after the PMS (recommended, nothing adopted), an existing project (its sections and tasks are adopted, with counts stated before the user confirms), or several projects (`multiple`).
- **Unplaced tasks go to the bucket, outside any section — never the Inbox.** Inbox triage is removed; the sync reads only bound projects.
- **The task footer becomes `PMS: <pms-id>/T-0042`.** Several PMSes can now share one account, each with its own `T-0001…`, so the footer must say which PMS a task belongs to. Footer searches are scoped to bound projects and matched exactly. No PMS from v2.5 or earlier has been used yet, so nothing needs migrating.

Consequences:
- A PMS has room for 20 live sections, i.e. 20 live projects, in its bucket (Todoist's per-project section limit) [Likely].
- On Todoist Free, one bucket per PMS means up to five PMSes, or fewer if the user's own projects take slots.
- The area/project → project/section revisit triggers above now apply per bucket.

## Unproven (field test before relying on it)

- Uncompletable parents behave as headers on mobile and block accidental completion. [Likely, not yet tested]
- Whether `find-completed-tasks` on Free returns completions older than a week. [Guessing]
- Whether the account can add a saved filter beyond the Free 3-view cap (it already shows 6 legacy filters). [Guessing]
- Whether the per-run token cost of a daily full reconcile is acceptable.
