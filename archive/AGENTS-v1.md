# AIO Student's Hub — OpenCode Project Instructions

## Mission

This repository is AIO Student's Hub. The repository is built through repeated OpenCode runs.

The authoritative project specification is supplied at run time through:

- `@AIO_Students_Hub_Master_Scaffold_Prompt.md`
- `@Jira_workItems_48(1).csv` (or the original `@Jira_workItems_48.csv` filename when that is the supplied file)
- `@AIO_Students_Hub_Build_Execution_Controller.md`

Treat those three artifacts as the external specification/control layer and the current repository as the implementation truth.

## Mandatory startup behavior

At the start of every substantial run:

1. Read the Master Scaffold Prompt.
2. Read the Jira CSV.
3. Read the Build Execution Controller.
4. Read `docs/build-progress.md` if it exists.
5. Read `docs/build-state.json` if it exists.
6. Read `docs/jira-traceability.md` if it exists.
7. Inspect the actual repository.
8. Reconcile recorded progress with actual code and tests before making changes.

Never assume the repository is fresh because the prompt was freshly attached.

## Mandatory continuation behavior

This project uses repeated runs:

```text
Controller + Scaffold + Jira CSV
        ↓
       BUILD
        ↓
    CHECKPOINT
        ↓
Controller + Scaffold + Jira CSV
        ↓
       BUILD
        ↓
      REPEAT
```

Never restart completed work without evidence that it is missing or broken.

## Build state

The repository is the durable memory of the build.

Use and maintain:

```text
docs/build-progress.md
docs/build-state.json
docs/build-log.md
docs/jira-traceability.md
```

Update these at meaningful checkpoints and before ending a run.

## Architecture invariants

Preserve the architecture established by the Master Scaffold Prompt:

```text
Frontend
  ↓
API
  ↓
Application Service
  ↓
Repository
  ↓
SQLAlchemy ORM
  ↓
Database
```

External systems must go through integration boundaries.

Background work must go through job boundaries.

Dashboard is an aggregation layer, not the owner of other feature data.

Assignments own assignment state.

Reminders own time-based reminder behavior.

Notifications own notification records/generation/retrieval.

The application is a modular monolith unless the user explicitly approves a different architecture.

## Multi-agent rules

The primary `build` agent is the integration owner and the only default agent permitted to perform repository-changing implementation work.

Subagents are specialists:

- `explorer`: read-only repository understanding.
- `planner`: read-only task decomposition and sequencing.
- `reviewer`: read-only architecture/code review.
- `tester`: validation and failure analysis; do not modify application code.

Do not delegate competing edits to multiple agents for the same files.

Prefer the following loop:

```text
Explore → Plan → Build → Test → Review → Fix → Checkpoint
```

Use parallel subagents only for independent read-only analysis unless the build agent has explicitly established stable boundaries for parallel implementation.

## Definition of done

Never mark a task or Jira item complete merely because files exist. Completion requires implementation, correct boundaries, and relevant validation.

## Safety

Never:

- commit secrets;
- log credentials/tokens/passwords;
- reset or discard user work;
- rewrite the project architecture without the decision gate;
- add premature infrastructure merely because it is familiar;
- create duplicate files/services because an earlier run was forgotten.

## Current run priority

Prefer:

1. Repair blockers.
2. Finish the current partial task.
3. Satisfy prerequisites.
4. Complete high-dependency foundation.
5. Complete integrated workflows.
6. Complete remaining feature work.
7. Strengthen tests.
8. Polish UI.

Always leave the repository in a coherent, recoverable state.
