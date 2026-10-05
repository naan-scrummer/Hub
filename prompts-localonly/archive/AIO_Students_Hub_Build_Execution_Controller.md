# AIO STUDENT'S HUB — BUILD EXECUTION CONTROLLER

> Companion prompt for `@AIO_Students_Hub_Master_Scaffold_Prompt.md` and `@Jira_workItems_48.csv`
>
> This document is an **execution and recovery controller**, not a replacement for the Master Scaffold Prompt.

---

# 0. PURPOSE

You are building the existing **AIO Student's Hub** repository in repeated AI-builder runs.

The user will deliberately use this workflow:

```text
SEND THIS CONTROLLER + MASTER SCAFFOLD + JIRA CSV
        ↓
BUILD FOR AS LONG AS THE CURRENT RUN CAN SAFELY CONTINUE
        ↓
SAVE VERIFIED PROGRESS TO THE REPOSITORY
        ↓
RUN ENDS / TOKEN LIMIT / CONTEXT LIMIT / INTERRUPT
        ↓
SEND THIS CONTROLLER + MASTER SCAFFOLD + JIRA CSV AGAIN
        ↓
READ THE EXISTING REPOSITORY + PERSISTED BUILD STATE
        ↓
VERIFY WHAT ACTUALLY EXISTS
        ↓
CONTINUE FROM THE NEXT HIGHEST-VALUE UNFINISHED WORK
        ↓
SAVE VERIFIED PROGRESS
        ↓
REPEAT
```

Your job is to make that workflow reliable.

The project must **not restart from zero on every run**.

The project must **not depend on conversational memory from a previous run**.

The repository itself must contain enough persistent state for a fresh builder run to determine:

- what has been completed;
- what is partially completed;
- what is currently in progress;
- what was attempted but failed;
- what remains;
- which Jira requirements are satisfied;
- which Jira requirements are partially satisfied;
- which Jira requirements are untouched;
- which tests pass/fail;
- what the next recommended implementation unit is;
- what architectural constraints must remain unchanged.

The controller exists specifically to prevent token-limited or interrupted builder runs from losing project progress.

---

# 1. AUTHORITATIVE INPUTS

Every run MUST treat the following three things as inputs:

```text
1. @AIO_Students_Hub_Master_Scaffold_Prompt.md
2. @Jira_workItems_48.csv
3. The current repository on disk
```

Their roles are different.

## 1.1 Master Scaffold Prompt

`AIO_Students_Hub_Master_Scaffold_Prompt.md` is the primary **architecture and project-foundation specification**.

It defines:

- product identity;
- technology choices;
- architecture;
- module boundaries;
- domain model;
- data ownership;
- API principles;
- authentication foundation;
- UI architecture;
- integrations;
- background jobs;
- seed data;
- testing strategy;
- deployment constraints;
- implementation order;
- definition of successful first build;
- normalized Jira requirements.

Do not replace it with this controller.

Do not weaken it because this controller exists.

Do not silently reinterpret it.

## 1.2 Jira CSV

`Jira_workItems_48.csv` is the **raw functional backlog source** supplied by the user.

Treat it as authoritative for the existence, identity, terminology, and functional intent of Jira work items.

The currently supplied backlog contains:

- 11 Epics;
- 48 non-epic work items;
- the feature requirements for Authentication, Dashboard, Attendance, Academics, Examinations, Announcements, Placements, Study Materials, Assignments, Reminders, and Notifications;
- explicitly documented E2E and testing work items.

Do not silently delete, rename, or merge Jira requirements.

Do not declare a Jira item complete merely because a similarly named file exists.

## 1.3 Existing repository

The repository is the **actual implementation state**.

When repository state conflicts with an old progress note, inspect the repository and tests and reconcile the progress note.

Never assume a progress file is correct without verification.

---

# 2. THE CENTRAL RULE

## NEVER TRUST REPORTED PROGRESS WITHOUT RECONCILIATION

At the beginning of every run, establish:

```text
Declared state
      ↓
Repository inspection
      ↓
Implementation inspection
      ↓
Test execution / targeted validation
      ↓
Reconciled actual state
```

At the end of every run, establish:

```text
Changes made
      ↓
Validation
      ↓
Verified state
      ↓
Persisted checkpoint
```

A progress file is a **checkpoint**, not proof.

The codebase, migrations, tests, and executable behavior are the proof.

---

# 3. PERSISTENT BUILD STATE

Create and maintain the following files in the repository unless an equivalent project-specific location already exists:

```text
docs/
├── build-progress.md
├── build-state.json
├── build-log.md
├── jira-traceability.md
├── architecture.md
└── api.md
```

If the Master Scaffold Prompt already caused some of these files to exist, update the existing files instead of creating duplicates.

The two most important recovery files are:

```text
docs/build-progress.md
docs/build-state.json
```

---

# 4. HUMAN-READABLE PROGRESS FILE

Maintain `docs/build-progress.md` as a concise operational dashboard.

It MUST contain at least:

```markdown
# AIO Student's Hub — Build Progress

## Overall Status
- Overall completion: <percentage or justified estimate>
- Foundation status: <not started / in progress / substantially complete / complete>
- Last verified: <timestamp>
- Last verified commit/hash if available: <value or N/A>

## Current Phase
<phase>

## Current Work Package
<work package>

## Current Task
<task>

## Last Verified Achievement
<one concrete statement>

## Last Failed Attempt / Known Issue
<none or concrete issue>

## Next Recommended Task
<one concrete atomic task>

## Jira Progress
- Epics: <x>/11 structurally addressed
- Non-epic work items: <x>/48 verified complete
- Partial: <x>
- Not started: <x>
- Blocked: <x>

## Tests
- Passing: <x>
- Failing: <x>
- Not run / unknown: <x>

## Critical E2E Workflows
- E2E-001: <status>
- E2E-002: <status>
- E2E-003: <status>
- E2E-004: <status>

## Architecture Invariants
<important invariants>

## Recent Checkpoints
- <timestamp>: <what changed + verification>
- <timestamp>: <what changed + verification>

## Safe Resume Instruction
<exactly what the next fresh builder run should inspect and do first>
```

Keep this file readable. Do not turn it into a giant dump of source code.

---

# 5. MACHINE-READABLE BUILD STATE

Maintain `docs/build-state.json` as a small structured state record.

Use a stable schema such as:

```json
{
  "project": "AIO Student's Hub",
  "schema_version": 1,
  "last_checkpoint_at": "...",
  "current_phase": "...",
  "current_work_package": "...",
  "current_task": "...",
  "overall_status": "in_progress",
  "progress_estimate": 0,
  "last_verified_commit": null,
  "requirements": {
    "total_epics": 11,
    "total_non_epic_items": 48,
    "complete": [],
    "partial": [],
    "in_progress": [],
    "blocked": [],
    "not_started": []
  },
  "e2e": {
    "SCRUM03-E2E-001": "not_started",
    "SCRUM03-E2E-002": "not_started",
    "SCRUM03-E2E-003": "not_started",
    "SCRUM03-E2E-004": "not_started"
  },
  "tests": {
    "last_command": null,
    "passing": null,
    "failing": null,
    "status": "unknown"
  },
  "last_completed_task": null,
  "last_failed_task": null,
  "next_task": null,
  "blocked_reason": null,
  "architecture_decisions": [],
  "resume_notes": []
}
```

You may extend the schema, but do not casually rename stable fields between runs.

Keep the file machine-readable JSON. Do not put comments in it.

---

# 6. JIRA REQUIREMENT STATE MODEL

For each Jira work item, track one of these states:

```text
NOT_STARTED
IN_PROGRESS
PARTIAL
COMPLETE
BLOCKED
```

Use `PARTIAL` when some acceptance behavior exists but the item is not actually done.

Use `BLOCKED` only when a concrete blocker prevents progress.

Do not use `COMPLETE` because:

- a folder exists;
- a component exists;
- a function is named correctly;
- an endpoint returns a hardcoded response;
- a test file exists without meaningful assertions;
- the feature looks visually complete;
- a mock was created but the workflow is not connected.

Completion must be grounded in the actual requirement's behavior and the Master Scaffold Prompt's definition of done.

---

# 7. JIRA IDENTIFIER NORMALIZATION

When reading the CSV, preserve the exact Jira IDs.

Examples include:

```text
SCRUM03-F001
SCRUM03-F001-UI-001
SCRUM03-F001-FLOW-001
SCRUM03-F001-SEC-001
SCRUM03-F001-SEC-002
SCRUM03-T-001
SCRUM03-E2E-001
```

Do not invent alternative IDs.

The `Summary` field may contain a bracketed identifier such as `[SCRUM03-F001]`. Extract and use the actual identifier consistently.

The normalized Jira requirements embedded in the Master Scaffold Prompt must remain traceable back to the CSV.

---

# 8. REQUIREMENT RECONCILIATION

At the start of every run:

1. Read the Master Scaffold Prompt.
2. Read the Jira CSV.
3. Inspect `docs/build-progress.md` if present.
4. Inspect `docs/build-state.json` if present.
5. Inspect `docs/jira-traceability.md` if present.
6. Inspect the repository structure.
7. Inspect version-control state if available.
8. Run targeted tests or validation needed to verify the claimed current phase.
9. Reconcile the recorded state against actual repository state.
10. Only then select the next work package.

If the progress file says:

```text
Assignments = COMPLETE
```

but the repository shows missing CRUD paths or failing tests, change the status back to:

```text
PARTIAL
```

or another accurate state.

Never preserve an incorrect progress claim merely to avoid rework.

---

# 9. FRESH RUN / RESUME / RECOVERY MODES

Determine the run mode immediately.

## MODE A — Fresh repository

Use when the project is genuinely new and there is no meaningful implementation.

Follow the Master Scaffold Prompt's implementation order.

Still create persistent build state before substantial implementation begins.

## MODE B — Normal resume

Use when the project already contains substantial implementation and the progress files are present.

Continue from the reconciled next task.

Do not recreate completed architecture.

## MODE C — Recovery / inconsistent state

Use when:

- progress files disagree with the repository;
- tests unexpectedly fail;
- the last run appears to have stopped mid-change;
- generated files are incomplete;
- migrations and ORM models are inconsistent;
- a feature is marked complete but is not functional.

In recovery mode:

1. stop adding new features temporarily;
2. identify the inconsistency;
3. repair the smallest necessary set of files;
4. validate;
5. update progress;
6. resume normal implementation.

Do not launch a large refactor merely because state tracking is imperfect.

---

# 10. WORK IN ATOMIC CHECKPOINTED UNITS

Do not treat a full phase as one uninterrupted task.

Break work into **atomic implementation units**.

A good unit is small enough that it can be:

```text
implemented
→ validated
→ checkpointed
```

within one builder run.

Examples:

```text
Create Assignment ORM model + migration

Implement AssignmentRepository

Implement AssignmentService status classification

Implement Assignment CRUD API

Implement Assignment frontend page

Connect assignment creation to reminder creation

Implement reminder processor

Implement reminder → notification generation
```

Avoid giant units such as:

```text
"Implement all remaining backend functionality"
```

---

# 11. CHECKPOINT FREQUENCY

Create a persistent checkpoint:

- before starting a major work package;
- after completing a meaningful atomic unit;
- after successful migration changes;
- after meaningful test runs;
- before attempting risky architectural changes;
- when an error reveals a new issue;
- when the run is approaching its practical context/token limit;
- before voluntarily ending a run.

A checkpoint means updating the persistent progress files, not merely saying something in the final response.

---

# 12. TOKEN / CONTEXT EXHAUSTION SAFETY

Assume that the current builder run can end unexpectedly.

Therefore:

## NEVER do this

```text
Start a large feature
→ make many edits
→ postpone progress recording
→ run out of context
→ leave repository state ambiguous
```

## Do this instead

```text
Select atomic task
→ record task as IN_PROGRESS
→ implement
→ validate
→ record result
→ checkpoint
→ choose next task
```

When you detect that the current run is becoming constrained, **stop starting new substantial work**.

Finish the smallest safe checkpoint available.

Then update:

- current task;
- last completed task;
- incomplete files/work;
- known failures;
- next task;
- Jira statuses;
- test state;
- resume notes.

The next run must be able to continue without relying on the previous conversation.

---

# 13. DO NOT CHASE COMPLETION PERCENTAGE

A numerical progress percentage is a convenience, not the source of truth.

Do not manipulate the percentage to make progress look better.

Prefer a truthful statement such as:

```text
42 of 48 non-epic items are structurally addressed,
but 3 remain PARTIAL because their end-to-end validation is incomplete.
```

rather than:

```text
90% complete
```

without evidence.

When a percentage is used, derive it from a transparent rule and document the rule.

---

# 14. PRIORITIZATION ALGORITHM

When deciding what to implement next, use this order unless the Master Scaffold Prompt or an explicit dependency requires otherwise:

```text
1. Repair a broken foundation that blocks progress
2. Complete the current partially implemented work package
3. Satisfy prerequisites for high-dependency features
4. Complete missing architecture required by many modules
5. Complete critical cross-module workflows
6. Complete remaining feature functionality
7. Improve tests where a requirement is otherwise unsafe to declare complete
8. Improve UX / polish after functional coverage is solid
9. Optional refinements last
```

Do not prioritize based merely on what looks most impressive in the UI.

The project is an integrated system.

---

# 15. DEPENDENCY-AWARE ORDER

Respect the relationships already defined by the Master Scaffold Prompt.

A representative dependency direction is:

```text
Project/runtime
    ↓
Database + models
    ↓
Repositories
    ↓
Services
    ↓
Authentication foundation
    ↓
Integration interfaces
    ↓
Jobs
    ↓
APIs
    ↓
Frontend shell
    ↓
Feature pages
    ↓
Cross-module workflows
    ↓
System/E2E validation
```

For the central productivity workflow:

```text
Assignments
    ↓
Reminders
    ↓
Notification generation
    ↓
Notification processing boundary
    ↓
Notification center
```

For academic synchronization:

```text
Portal interface
    ↓
Mock adapter
    ↓
Synchronization
    ↓
Domain persistence
    ↓
Feature API
    ↓
Student UI
```

Do not jump ahead in a way that forces later architectural rewrites.

---

# 16. CURRENT TASK CONTRACT

Before doing meaningful implementation, define one current task internally and persist it.

Use this shape:

```text
Task ID:
Title:
Jira IDs affected:
Prerequisites:
Files expected to change:
Acceptance conditions:
Validation command(s):
Risk:
```

Keep the task narrow.

Example:

```text
Task ID: AIO-ASSIGNMENTS-REPO-01
Title: Implement AssignmentRepository
Jira IDs affected:
  SCRUM03-F009-DATA-001
  SCRUM03-F009-UI-001
Prerequisites:
  Assignment ORM model exists
Files expected to change:
  backend/app/modules/assignments/repository.py
Acceptance conditions:
  create/get/update/delete queries exist
  student ownership is respected
  repository tests pass
Validation:
  pytest tests/integration/assignments
Risk:
  low
```

If a task grows materially beyond its original shape, split it and checkpoint.

---

# 17. NO DUPLICATE WORK

Before creating a file, endpoint, model, service, component, test, migration, or integration adapter:

1. search the repository for an existing equivalent;
2. inspect it;
3. reuse or extend it when appropriate;
4. only create a new artifact when it has a legitimate architectural role.

Do not create duplicates such as:

```text
assignment_service.py
assignment_service_v2.py
assignment_service_new.py
```

because a previous run was forgotten.

Do not create duplicate migrations merely because the previous migration was not inspected.

Do not create duplicate React pages because the route was not found.

---

# 18. NO RESTARTING THE ARCHITECTURE

Once the Master Scaffold architecture exists in the repository, preserve it.

Do not repeatedly rebuild:

- the entire folder structure;
- the database model;
- the auth mechanism;
- the repository pattern;
- the API layer;
- the frontend architecture;
- integration boundaries;
- background-job boundaries.

A later run should normally extend the existing architecture.

Only materially change architecture when:

1. the current architecture violates the Master Scaffold Prompt;
2. a real requirement makes it insufficient;
3. the decision gate is satisfied;
4. the change is documented.

---

# 19. GIT / VERSION CONTROL AWARENESS

If the repository uses Git:

1. inspect `git status`;
2. inspect recent history when useful;
3. understand whether the previous run left uncommitted changes;
4. do not discard user changes;
5. do not reset or force-rewrite history unless explicitly instructed;
6. record the last verified commit hash in the build state when practical.

If there is no Git repository, rely on filesystem inspection and persistent state.

Do not create commits solely for the sake of progress tracking unless the user's environment/project workflow clearly supports that.

---

# 20. USER CHANGES ARE SACRED

The current repository may contain work produced by a previous builder run or by the user.

Before modifying a file that contains unrelated existing work:

- inspect it;
- preserve compatible work;
- modify only what is necessary.

Never assume the entire repository is disposable.

---

# 21. IMPLEMENTATION + VALIDATION LOOP

Use this continuously:

```text
SELECT TASK
    ↓
MARK IN_PROGRESS
    ↓
IMPLEMENT SMALLEST COMPLETE UNIT
    ↓
RUN TARGETED VALIDATION
    ↓
FIX FAILURES
    ↓
RUN TARGETED VALIDATION AGAIN
    ↓
MARK COMPLETE / PARTIAL / BLOCKED
    ↓
UPDATE TRACEABILITY
    ↓
CHECKPOINT
    ↓
SELECT NEXT TASK
```

Never skip the checkpoint step merely because the code appears correct.

---

# 22. VALIDATION LEVELS

Use the least expensive validation that proves the current task, then broader validation when appropriate.

## Level 1 — Static inspection

Examples:

```text
syntax checks
imports
type/lint checks when configured
route discovery
schema discovery
migration inspection
```

## Level 2 — Targeted unit tests

Run the tests for the changed behavior.

## Level 3 — Integration tests

Exercise repository/service/API boundaries with the test database.

## Level 4 — System/E2E tests

Use for cross-module workflows and explicit Jira E2E requirements.

## Level 5 — Application smoke test

Start the actual application where appropriate and exercise critical user behavior.

Do not run the most expensive possible validation after every trivial file edit when a targeted validation is sufficient.

---

# 23. TEST RESULT PERSISTENCE

After every meaningful test run, update the persistent state with:

```text
Command:
Date/time:
Scope:
Passed:
Failed:
Known flaky/ignored tests:
Relevant failure summary:
```

Do not claim that tests pass based on a previous run when code has materially changed without justification.

When a test fails:

```text
FAILURE DISCOVERED
    ↓
record failure
    ↓
repair if within current scope
    ↓
re-run
    ↓
checkpoint
```

If a failure cannot reasonably be fixed in the current task, record it as a known blocker and move only to work that is not invalidated by it.

---

# 24. TRACEABILITY MAINTENANCE

`docs/jira-traceability.md` must remain aligned with actual implementation state.

For every Jira work item, maintain at least:

```text
Requirement ID
Feature
Status
Implementation artifacts
Tests
Last verified
Notes / blocker
```

Use statuses consistent with:

```text
NOT_STARTED
IN_PROGRESS
PARTIAL
COMPLETE
BLOCKED
```

A requirement marked COMPLETE must point to concrete implementation and validation.

---

# 25. ACCEPTANCE-DRIVEN COMPLETION

For every task, read its Jira requirement and the relevant Master Scaffold section before declaring it complete.

Completion means:

```text
Requirement intent understood
        AND
implementation exists
        AND
integration/boundaries are correct
        AND
relevant validation passes
```

Do not use a single superficial artifact as proof.

---

# 26. SCAFFOLD VS FINAL FUNCTIONALITY

The Master Scaffold Prompt intentionally permits some development-only simplifications.

The controller must preserve this distinction.

It is acceptable for:

- college portals to use deterministic mock adapters;
- background scheduling to use a simple local mechanism;
- local material storage to remain development-only;
- production delivery channels to remain absent;
- some external integrations to be represented by interfaces and mocks.

It is not acceptable to leave foundational architecture absent.

The current project goal remains:

```text
strong runnable foundation
→ final functionality later
```

Do not accidentally turn “scaffold” into “empty skeleton.”

Do not accidentally turn “foundation” into “fully production-integrated enterprise platform.”

---

# 27. DEFINITION OF DONE FOR A WORK PACKAGE

A work package is done only when:

1. Its implementation exists in the intended module boundary.
2. Its dependencies are satisfied.
3. It does not duplicate existing responsibility.
4. Its API/UI behavior, where applicable, is connected to the real backend path.
5. Its persistence behavior, where applicable, is real rather than hardcoded.
6. Relevant tests exist.
7. Relevant tests have been executed.
8. Known failures are resolved or explicitly recorded.
9. Jira traceability is updated.
10. Build state is checkpointed.

---

# 28. FEATURE COMPLETION CHECK

Before marking one of the major feature modules complete, verify as applicable:

```text
Authentication
  [ ] Login
  [ ] Auth state
  [ ] Logout
  [ ] Protected resources
  [ ] Authorization
  [ ] Secure credential handling
  [ ] Required tests

Dashboard
  [ ] Student overview
  [ ] Aggregation service
  [ ] Aggregates real feature services
  [ ] Representative data
  [ ] Attention-oriented content

Attendance
  [ ] Subject view
  [ ] attended/total/percentage
  [ ] application processing
  [ ] mock synchronization
  [ ] unavailable state

Academics
  [ ] subject information
  [ ] academic/internal marks
  [ ] processing service
  [ ] integration boundary

Examinations
  [ ] schedule/date view
  [ ] processing service
  [ ] synchronization boundary
  [ ] unavailable state

Announcements
  [ ] unified feed
  [ ] source traceability
  [ ] timestamp traceability
  [ ] aggregation/normalization
  [ ] integration boundary

Placements
  [ ] opportunities
  [ ] company/eligibility information
  [ ] recruitment updates/dates
  [ ] preparation resources/experiences
  [ ] source synchronization boundary
  [ ] permitted senior-student contributions

Study Materials
  [ ] browse/access
  [ ] search/filter
  [ ] subject context
  [ ] contribution/upload boundary
  [ ] assignment context relationship

Assignments
  [ ] create/read/update/delete
  [ ] due date
  [ ] subject
  [ ] description
  [ ] completion status
  [ ] upcoming/overdue classification
  [ ] reminder relationship
  [ ] materials relationship

Reminders
  [ ] create/view
  [ ] supported associations
  [ ] trigger time
  [ ] independent processing
  [ ] failure handling

Notifications
  [ ] notification records
  [ ] center
  [ ] empty state
  [ ] generation workflow
  [ ] reminder-to-notification relationship
  [ ] processing boundary
```

This checklist is not a replacement for the Jira requirements; it is a practical verification aid.

---

# 29. E2E CHECKPOINT MODEL

Track each explicit E2E workflow separately.

## E2E-001 — Assignment → Reminder → Notification

Track:

```text
[ ] Assignment can be created
[ ] Due date persists
[ ] Reminder relationship/scheduling is created
[ ] Controlled time can reach trigger
[ ] Reminder processor runs independently
[ ] Notification generation occurs
[ ] Notification is stored
[ ] Notification processing boundary exists
[ ] Student can retrieve notification
[ ] Completion before trigger prevents stale attention
```

## E2E-002 — Assignment → Materials context

Track:

```text
[ ] Assignment carries subject/academic context
[ ] Related materials query exists
[ ] Materials service is used
[ ] Relevant materials appear
[ ] Empty result is clear
```

## E2E-003 — Portal → Attendance → Student

Track:

```text
[ ] Mock portal provides data
[ ] Synchronization fetches it
[ ] Data validates/normalizes
[ ] Data persists
[ ] Attendance API returns it
[ ] UI renders it
[ ] Portal failure is represented as unavailable
```

## E2E-004 — Portal → Examination view

Track:

```text
[ ] Mock portal provides data
[ ] Synchronization fetches it
[ ] Data persists
[ ] Examination API returns it
[ ] UI renders schedule/date data
[ ] Failure is represented as unavailable
```

---

# 30. ARCHITECTURAL INVARIANTS

The following are protected invariants unless a documented decision gate changes them:

```text
Modular monolith

Frontend
  ↓
API
  ↓
Application Service
  ↓
Repository
  ↓
SQLAlchemy
  ↓
Database

External source access
  ↓
Integration boundary
  ↓
Synchronization
  ↓
Domain service
  ↓
Persistence

Background processing
  ↓
Job boundary
  ↓
Application service

Dashboard
  = aggregation layer
  ≠ owner of other feature data

Assignments
  = owns assignment state

Reminders
  = owns time-based reminder behavior

Notifications
  = owns notification records/generation/retrieval
```

Do not collapse these boundaries to save time.

---

# 31. ARCHITECTURAL DRIFT DETECTION

At the start of each run, look for warning signs:

```text
hardcoded feature data in frontend
SQL inside route handlers
portal-specific code in domain modules
background processing inside HTTP handlers
cross-module circular imports
multiple competing service implementations
large generic repositories
one giant route file
one giant models file
new unrelated infrastructure
microservices introduced without requirement
new frontend state-management framework without need
```

If drift is found:

1. assess whether it materially violates the Master Scaffold;
2. repair only what is necessary;
3. document the correction;
4. continue.

Do not perform broad beautification refactors during unrelated feature work.

---

# 32. DEPENDENCY / BLOCKER RECORDING

Never write only:

```text
Blocked.
```

Record:

```text
Blocker:
Why it blocks:
Affected Jira IDs:
What is still possible:
Required decision/input:
Recommended next action:
```

A blocker should be specific enough for a future fresh run to understand it immediately.

---

# 33. DECISION GATES

Use the Master Scaffold Prompt's decision gate for consequential changes.

Do not stop for ordinary implementation details.

A decision gate is appropriate when considering:

- changing frontend technology;
- changing authentication architecture;
- changing database strategy;
- introducing distributed infrastructure;
- changing major data relationships;
- changing module boundaries;
- adding a substantial external dependency;
- replacing the established architecture.

When a decision is needed, record it in build state and in an architecture decision record or `docs/architecture.md`.

Use:

```text
Decision required

Context:
...

Option A:
...

Option B:
...

Recommendation:
...

Why this matters:
...
```

Do not invent an irreversible architecture just because it appears convenient for the current task.

---

# 34. STOP CONDITIONS FOR THE CURRENT RUN

A builder run may stop safely when:

- the current atomic work package is complete and checkpointed;
- a genuine decision gate has been reached;
- a blocking failure cannot be responsibly resolved in the current scope;
- the practical context/token budget is becoming constrained;
- continuing would require beginning a large task that cannot be checkpointed reliably.

When stopping, do NOT merely say “continued next time.”

Persist the exact state needed for continuation.

---

# 35. MANDATORY END-OF-RUN CHECKPOINT

Before ending any run for any reason, perform this sequence:

```text
1. Determine what actually changed.
2. Run the most relevant validation available.
3. Record test results.
4. Reconcile Jira statuses affected by this run.
5. Update build-progress.md.
6. Update build-state.json.
7. Update jira-traceability.md.
8. Record unresolved failures/blockers.
9. Record the exact next recommended task.
10. Record any partial file/task state.
11. Record architecture decisions if any.
12. Ensure the repository is left in a coherent state.
```

The checkpoint is mandatory even when the run ended unexpectedly as long as the environment still permits filesystem edits.

---

# 36. SAFE RESUME INSTRUCTION

At the end of `docs/build-progress.md`, always maintain a section called:

```text
## Safe Resume Instruction
```

It should contain an actionable instruction for a completely fresh AI builder.

Example:

```text
Read the Master Scaffold Prompt and Jira CSV, then inspect the repository and this progress file.
Reconcile the Assignment module state.
Run the assignment repository tests.
If the repository matches the recorded state, continue by implementing AssignmentService.create_assignment().
Do not rebuild authentication, database setup, or completed modules.
```

This is deliberately specific.

Do not write vague instructions such as:

```text
Continue project.
```

---

# 37. RESTART-RESISTANCE RULE

A fresh run must behave approximately like this:

```text
OPEN INPUTS
    ↓
READ MASTER SCAFFOLD
    ↓
READ JIRA CSV
    ↓
READ BUILD STATE
    ↓
INSPECT REPOSITORY
    ↓
VERIFY CLAIMED COMPLETIONS
    ↓
SELECT NEXT TASK
    ↓
IMPLEMENT
    ↓
VALIDATE
    ↓
CHECKPOINT
```

It must NOT behave like this:

```text
Read prompt
    ↓
Assume project is empty
    ↓
Recreate folder structure
    ↓
Recreate models
    ↓
Recreate auth
```

unless repository inspection proves that those things are actually absent or broken.

---

# 38. PARTIAL IMPLEMENTATION HANDLING

AI builders frequently stop halfway through a task.

When an existing task is partially implemented:

1. identify which pieces exist;
2. identify which pieces work;
3. identify missing pieces;
4. preserve working pieces;
5. complete the smallest missing set;
6. validate;
7. update status.

Example:

```text
Assignment CRUD

Model: COMPLETE
Migration: COMPLETE
Repository: COMPLETE
Service: PARTIAL
API: PARTIAL
UI: NOT_STARTED
Tests: PARTIAL
```

Do NOT classify the entire feature as untouched.

Continue from the first genuinely incomplete dependency.

---

# 39. FAILURE RECOVERY

When a prior run left an error:

```text
1. Reproduce or inspect the error.
2. Identify its scope.
3. Decide whether it is local or architectural.
4. Fix the smallest responsible layer.
5. Re-run the relevant test.
6. Re-run broader validation when justified.
7. Checkpoint the repaired state.
```

Never hide known failures merely to move the progress percentage forward.

---

# 40. MIGRATION SAFETY

Database changes deserve special caution.

Before creating a new migration:

- inspect current models;
- inspect current migration history;
- understand the current schema;
- avoid duplicate migration intent;
- use Alembic as specified by the Master Scaffold.

After migration changes:

```text
migration generation
    ↓
inspect migration
    ↓
apply migration
    ↓
validate database
    ↓
run relevant tests
    ↓
checkpoint
```

Do not use migration generation as proof that the runtime schema is correct.

---

# 41. SEED DATA SAFETY

Seed data must remain deterministic.

If modifying seed data:

- preserve the ability to reproduce the same development state;
- preserve cross-module relationships;
- avoid random startup mutations;
- update tests if required;
- record meaningful seed changes in the build log.

Do not repeatedly regenerate the database with incompatible seed assumptions merely because a fresh UI screenshot is desired.

---

# 42. FRONTEND VERIFICATION

A page is not complete because its route renders.

Verify, as applicable:

```text
route exists
→ API is connected
→ authenticated state is respected
→ loading state exists
→ success state exists
→ empty state exists
→ error state exists
→ unavailable state exists where required
→ real persisted data is rendered
→ user action reaches the intended backend path
```

Do not leave a polished mock screen disconnected from the backend and mark it COMPLETE.

---

# 43. BACKEND VERIFICATION

An endpoint is not complete because it returns HTTP 200.

Verify, as applicable:

```text
route
→ validation
→ auth/authorization
→ service
→ repository
→ database
→ response schema
```

Do not use hardcoded sample responses for a requirement that is supposed to be database-backed.

Mocked external data is acceptable only at the external integration boundary defined by the Master Scaffold.

---

# 44. INTEGRATION VERIFICATION

For portal-backed features, verify the actual boundary:

```text
Mock/source adapter
→ synchronization
→ validation/normalization
→ persistence
→ domain service
→ API
→ UI
```

A mock adapter returning good data directly to the frontend does not satisfy the architecture.

---

# 45. JOB VERIFICATION

For background work, verify that the job is independently invokable.

The job should call application services rather than duplicating business logic.

At minimum verify the logical existence and testability of:

```text
process_due_reminders()
process_pending_notifications()
```

Do not satisfy background-job requirements by hiding everything inside an API request handler.

---

# 46. DASHBOARD VERIFICATION

When validating the dashboard, confirm that it aggregates real feature services.

Do not create a parallel dashboard-only copy of:

- assignment data;
- examination data;
- announcement data;
- attendance data;
- academic data;
- reminder data;
- notification data;
- placement data.

If the dashboard needs a value, prefer the existing feature application service or a clearly defined aggregation abstraction.

---

# 47. PROGRESS REPORTING LANGUAGE

Use precise language.

Prefer:

```text
Implemented and verified
Implemented but not fully tested
Structurally present, behavior incomplete
Blocked by X
Not started
```

Avoid:

```text
Basically done
Almost done
Should work
Looks good
Completed
```

unless supported by actual validation.

---

# 48. BUILD LOG

Maintain `docs/build-log.md` as a chronological concise record.

Each checkpoint entry should contain:

```text
### <timestamp> — <task>

Status: COMPLETE / PARTIAL / BLOCKED
Jira: <IDs>

Changed:
- <files / high-level changes>

Validated:
- <commands / checks>

Result:
- <pass/fail summary>

Next:
- <next task>
```

Do not put every trivial command into the build log.

The purpose is to make the evolution of the build understandable.

---

# 49. BUILD STATE IS NOT CHAT MEMORY

The user may resend the same two or three files in a new builder session with no previous conversational context.

Therefore:

```text
Conversation memory = unreliable
Persistent repository state = required
```

Never assume the next run can see your previous final answer.

The next run should need only:

```text
Master Scaffold
Jira CSV
Repository
Persistent build state
```

to continue intelligently.

---

# 50. USING THE TWO SPECIFICATIONS TOGETHER

The intended relationship is:

```text
Jira CSV
   │
   │ raw functional source
   ▼
Master Scaffold Prompt
   │
   │ architecture + normalized requirements
   ▼
Execution Controller
   │
   │ stateful execution / recovery
   ▼
Repository
```

The controller does not redefine the product.

The Master Scaffold does not define current progress.

The Jira CSV does not prove implementation state.

The repository plus validation proves implementation state.

---

# 51. HANDLING SPECIFICATION DRIFT

If the Jira CSV, Master Scaffold Prompt, and repository disagree:

1. identify the exact disagreement;
2. determine whether it is only an implementation detail or a material product/architecture conflict;
3. preserve the user's stated source hierarchy;
4. do not silently rewrite requirements;
5. use the Master Scaffold's decision gate if a material architectural choice is necessary;
6. record the resolution in build state.

For ordinary implementation ambiguity, choose the simplest behavior consistent with the source requirements.

---

# 52. DO NOT INVENT WORK JUST TO FILL A RUN

When a run still has capacity but all high-priority work requires a decision or external dependency, do not fabricate unrelated features.

Instead:

- complete tests;
- improve traceability;
- validate existing workflows;
- repair known defects;
- improve documentation required by the scaffold;
- strengthen deterministic seed data;
- perform safe cleanup directly supporting current requirements.

Do not add:

- social features;
- chat;
- generic analytics;
- admin dashboards;
- unrelated settings;
- unnecessary infrastructure;
- speculative integrations.

---

# 53. NO PREMATURE POLISH

Visual polish is valuable, but during foundation construction it must not consume the run while foundational work remains incomplete.

Prioritize:

```text
correct data
correct boundaries
correct workflows
correct APIs
correct persistence
correct tests
then polish
```

A modest UI with real data is preferable to a beautiful disconnected mock.

---

# 54. NO PREMATURE INFRASTRUCTURE

Respect the Master Scaffold Prompt's minimal infrastructure policy.

Do not introduce infrastructure merely to make the progress tracker appear sophisticated.

In particular, do not add:

```text
Redis
Celery
Kafka
RabbitMQ
Kubernetes
Terraform
service mesh
microservices
cloud infrastructure
observability platforms
```

unless an actual project requirement and decision gate justify it.

---

# 55. FIRST-RUN INITIALIZATION

If `docs/build-state.json` and `docs/build-progress.md` do not exist, initialize them before substantial implementation.

Perform a repository audit first.

The first audit should identify:

```text
Backend present?
Frontend present?
Database configuration present?
Models present?
Migrations present?
Repositories present?
Services present?
Authentication present?
Integrations present?
Jobs present?
APIs present?
Frontend shell present?
Feature pages present?
Tests present?
Jira traceability present?
README present?
```

Then create an evidence-based baseline.

Do not assume every item is absent merely because a progress file is absent.

---

# 56. REPOSITORY AUDIT OUTPUT

When performing a baseline audit, produce concise findings such as:

```text
FOUNDATION AUDIT

Runtime: present
Backend: present
Frontend: present
Database: present
Migrations: partial
Authentication: partial
Assignments: present
Reminders: partial
Notifications: not started
Portal adapters: present/mock
Tests: partial
Traceability: present

Highest-priority gap:
Assignment → Reminder → Notification workflow is incomplete.
```

Persist the meaningful result.

---

# 57. SAFE CONTINUATION ACROSS MANY RUNS

The project should evolve like this:

```text
RUN 1
  inspect
  scaffold foundation
  checkpoint

RUN 2
  read state
  verify
  continue
  checkpoint

RUN 3
  read state
  verify
  continue
  checkpoint

...

RUN N
  read state
  verify
  finish remaining functionality
  checkpoint
  full validation
```

The number of runs is not important.

The invariant is:

```text
Every run starts from verified repository state.
Every run leaves verified persistent state.
```

---

# 58. COMPLETION OF THE WHOLE SCAFFOLD

Do not mark the overall scaffold COMPLETE until the Master Scaffold Prompt's successful first-build definition has been satisfied and verified.

At minimum, verify:

```text
[ ] backend starts
[ ] frontend starts
[ ] database initializes
[ ] Alembic migrations execute
[ ] deterministic seed works
[ ] login works
[ ] protected resources are protected
[ ] logout works
[ ] authenticated shell loads
[ ] navigation reaches major feature areas
[ ] feature APIs return database-backed data
[ ] dashboard aggregates real services
[ ] Assignment CRUD works
[ ] assignment status classification works
[ ] assignment → reminder relationship works
[ ] reminder processor is independently invokable
[ ] reminder → notification flow works
[ ] notifications are retrievable in-app
[ ] assignment → materials context works
[ ] mock portal → attendance works
[ ] mock portal → examination works
[ ] announcement traceability exists
[ ] placement contribution boundary exists
[ ] required test work items pass
[ ] four required E2E workflows are demonstrable
[ ] structured logs work
[ ] secrets are not logged
[ ] README is usable
[ ] Jira traceability is current
[ ] no accidental premature infrastructure has been added
```

Only then may the scaffold be declared structurally complete.

---

# 59. AFTER SCAFFOLD COMPLETION

Once the scaffold is structurally complete, the controller can continue to be used for the later implementation phase.

The persistent state should then shift from:

```text
Foundation construction
```

toward:

```text
Final functionality
Real integrations
Behavior refinement
UX refinement
Production hardening
```

But the same checkpointing model continues to apply.

---

# 60. RESPONSE DISCIPLINE

The builder's user-facing final response after a run should be concise and factual.

Report:

```text
What was completed
What was validated
What failed
What remains
Exact next task
```

Do not spend the response on a long narrative when persistent state has already been updated.

The repository checkpoint is the important artifact.

---

# 61. IMPORTANT: DO NOT CLAIM TO HAVE DONE WHAT WAS NOT VERIFIED

Never say:

```text
Done
```

when the code was not tested or inspected sufficiently.

Never say:

```text
All requirements implemented
```

unless the traceability matrix and relevant validation support it.

Never say:

```text
The next run can continue
```

unless the persistent checkpoint actually makes continuation possible.

---

# 62. FINAL RUN ALGORITHM

On every invocation of this controller, execute this algorithm mentally and operationally:

```text
A. READ
   - Master Scaffold Prompt
   - Jira CSV
   - build-progress.md
   - build-state.json
   - jira-traceability.md
   - repository

B. RECONCILE
   - declared state vs actual state
   - requirements vs implementation
   - tests vs claims
   - architecture vs scaffold

C. SELECT
   - highest-value unblocked atomic task
   - respecting dependencies

D. RECORD
   - mark task IN_PROGRESS
   - record affected Jira IDs

E. IMPLEMENT
   - preserve architecture
   - modify the smallest responsible scope

F. VALIDATE
   - targeted tests/checks
   - broader validation when justified

G. RECONCILE AGAIN
   - what really works?
   - what remains?

H. CHECKPOINT
   - build-progress.md
   - build-state.json
   - build-log.md
   - jira-traceability.md

I. CONTINUE OR STOP SAFELY
   - continue with another atomic unit only if it can be safely checkpointed
   - otherwise leave a precise next-task instruction
```

---

# 63. THE EXACT USER WORKFLOW THIS CONTROLLER MUST SUPPORT

The user will repeatedly send:

```text
@AIO_Students_Hub_Build_Execution_Controller.md
@AIO_Students_Hub_Master_Scaffold_Prompt.md
@Jira_workItems_48.csv
```

Then the builder runs.

Later, the user will send the same three inputs again.

The builder MUST interpret the second and subsequent runs as **continuations of the same existing project**, not new projects.

The intended loop is:

```text
┌─────────────────────────────────────────────────────────┐
│ USER SENDS CONTROLLER + MASTER + JIRA CSV               │
└──────────────────────────┬──────────────────────────────┘
                           ↓
                 INSPECT EXISTING REPO
                           ↓
                 READ PERSISTED STATE
                           ↓
                 VERIFY ACTUAL PROGRESS
                           ↓
                    SELECT NEXT TASK
                           ↓
                      IMPLEMENT
                           ↓
                      VALIDATE
                           ↓
                    CHECKPOINT STATE
                           ↓
              ┌────────────┴────────────┐
              │                         │
       More safe capacity         Stop safely
              │                         │
              └──────────────┬──────────┘
                             ↓
               USER SENDS SAME INPUTS AGAIN
                             ↓
                           RESUME
```

This is the core purpose of this controller.

---

# 64. DO NOT BREAK THE LOOP

The following behaviors break the intended workflow and are prohibited:

```text
Assuming a fresh repository on every run

Ignoring build-progress.md

Ignoring build-state.json

Ignoring Jira traceability

Rebuilding completed modules from scratch

Repeating already-completed tasks because previous work was not inspected

Making many changes without checkpointing

Leaving the repository in an incoherent half-finished state when a safe checkpoint is possible

Marking work complete without validation

Prioritizing visual polish over foundational blockers

Changing architecture without the decision gate

Treating the current run's conversation as the only memory
```

---

# 65. FINAL DIRECTIVE

Treat this controller as the project's **persistent execution protocol**.

Treat `AIO_Students_Hub_Master_Scaffold_Prompt.md` as the project's **architecture and foundation specification**.

Treat `Jira_workItems_48.csv` as the project's **raw functional backlog source**.

Treat the existing repository and executed validation as the **source of truth for actual implementation state**.

The objective is not merely to make progress during one AI-builder run.

The objective is to make progress **recoverable, measurable, verifiable, and continuable across arbitrarily many AI-builder runs**.

Build in small verified units.

Checkpoint aggressively enough to survive token limits.

Never lose track of where the project is.

Never make the next run guess what happened.

Never restart completed work without evidence that it needs rebuilding.

Never let progress tracking replace engineering validation.

Always leave the repository in the best coherent state you can achieve within the current run.

And always leave a precise answer to this question inside the persistent build state:

> **“Exactly where is AIO Student's Hub right now, what has been verified, what is incomplete, and what should the next builder run do first?”**
