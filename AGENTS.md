# AIO Student's Hub — OpenCode Agent Instructions

This file is the **authoritative OpenCode instruction file** for this working directory.

Its purpose is to make repeated coding runs resumable, prevent duplicate work, and keep the repository recoverable if a run stops because of context exhaustion, interruption, crash, or build failure.

\---

## 1\. Run-provided guidance and prompts

Do **not** depend on any fixed or legacy scaffold/controller prompt filenames.

At each run, the user may provide one or more current guidance or prompt files, for example:

```text
guide.md
prompt.md
```

Treat the guidance/prompt files actually supplied for the current run as the **current task specification and planning input**.

The exact filenames are not fixed. Discover and use the files provided for that run rather than expecting obsolete project-specific controller/scaffold filenames.

Use the **current repository as implementation truth**.

Do not repeatedly reread large run-provided guidance/prompt files unless needed to resolve requirements, dependencies, acceptance criteria, or an inconsistency.

CSV files may be supplied for project data, work items, or traceability. When relevant, use the supplied CSV as required input rather than treating it as a continuation-state file.

If:

```text
docs/jira-traceability.md
```

exists, read it during startup. Use it to track Jira/work-item traceability and reconcile which work items are implemented, pending, or otherwise accounted for.

\---

## 2\. Continuation state

The single resumable execution state file is:

```text
.opencode-state.md
```

Create it immediately on the first substantial run if it does not exist.

It replaces the old continuation role previously spread across:

```text
docs/build-progress.md
docs/build-state.json
docs/build-log.md
```

Do not maintain duplicate execution state in those deprecated files.

`docs/jira-traceability.md` may still be maintained when Jira-to-code traceability is useful to the project, but it is **not** the run-resume state.

\---

## 3\. Mandatory startup behavior

At the start of every substantial run, follow this order:

1. Read this `AGENTS.md`.
2. Read `.opencode-state.md` if it exists.
3. Read the **current run's supplied `guide.md`/guidance and prompt files** (or their actual supplied filenames).
4. Read the supplied CSV file(s) when they are relevant to the requested work.
5. Read `docs/jira-traceability.md` if it exists.
6. Inspect the actual repository.
7. Check relevant `git status`, diffs, existing implementation, and tests.
8. Reconcile the recorded state and traceability with the repository.
9. Determine:

   * what is already complete,
   * what is partially complete,
   * what failed,
   * what remains,
   * what must still be verified.
10. Calculate only the work required by the **current run's prompt/guidance**.
11. Resume from the earliest **safe unfinished step**.

The startup sequence is deliberate: **state + current instructions + traceability + repository reality** must be established before implementation begins.

Do not look for or depend on obsolete fixed scaffold/controller filenames.

Never assume the repository is fresh because the same prompt or control files were supplied again.

Never restart completed work without evidence that it is missing, broken, incompatible, or unverified.

\---

## 4\. Legacy-state migration

If `.opencode-state.md` does not exist but any of these old files do:

```text
docs/build-progress.md
docs/build-state.json
docs/build-log.md
```

perform a one-time migration:

1. Read only enough of the legacy state files to recover:

   * current task,
   * completed work,
   * partial work,
   * failures/blockers,
   * verification state,
   * next intended action.
2. Verify those claims against the repository.
3. Create `.opencode-state.md` using the current format below.
4. From that point onward, update only `.opencode-state.md` for continuation state.
5. Do not delete the old files unless the user explicitly asks.

Repository state always overrides stale legacy records.

\---

## 5\. Required state format

Maintain `.opencode-state.md` in this compact form:

```md
# OpenCode Continuation State

## Task
<short description of the current task>

## Prompt
<short normalized description; do not copy a huge prompt>

## Status
IN\_PROGRESS | BLOCKED | COMPLETE

## Last Safe Point
<exact milestone known to be complete>

## Completed
- <completed item>

## In Progress
- <partial item and exact state>

## Remaining
- <unfinished item>

## Files Changed
- `<path>` — <what changed>

## Verification
- Build: PASS | FAIL | NOT\_RUN
- Tests: PASS | FAIL | NOT\_RUN
- Lint/Typecheck: PASS | FAIL | NOT\_RUN
- Other: <relevant check>

## Failures / Blockers
- <failure or blocker>
- None

## Next Action
<ONE concrete next action>

## Recovery Notes
<only information needed to safely continue>
```

Keep this file short and factual.

Replace stale information instead of accumulating a transcript.

Never store secrets, tokens, passwords, credentials, or private data.

\---

## 6\. Checkpoint behavior

Assume a run can stop at any moment.

Update `.opencode-state.md`:

* after a meaningful milestone,
* before a risky or large change,
* after tests/build/typecheck/lint,
* after a failure,
* when the remaining work changes,
* before ending a run.

Before a risky operation, record the intended recovery action.

After success, update:

```text
Last Safe Point
Completed
Verification
Next Action
```

After failure, record:

```text
Failures / Blockers
Verification
Next Action
```

Never claim a step is complete before it actually is.



At the end of every run, update `docs/jira-traceability.md` as needed to accurately reflect the work completed, partially completed, blocked, or still pending during that run; reconcile it with the actual repository and `.opencode-state.md`, and do not mark any Jira item complete unless its required implementation and verification are complete.

\---

## 7\. Resume algorithm

Every resumed run follows:

```text
Read AGENTS.md
      ↓
Read .opencode-state.md
      ↓
Inspect repository + git
      ↓
Reconcile recorded state with reality
      ↓
Read only required spec/Jira/controller context
      ↓
Find earliest safe unfinished step
      ↓
Implement only remaining work
      ↓
Verify
      ↓
Checkpoint .opencode-state.md
```

If the log says something is complete but the repository does not contain it, the repository wins.

If valid partial code exists:

* preserve it,
* inspect it,
* finish or repair it,
* do not rewrite it merely to start clean.

If a build or test was interrupted, rerun the relevant verification before assuming success.

\---

## 8\. Repeated-prompt behavior

If the same prompt is sent again, treat it as a **continuation request**, not automatically as a new task.

First:

1. read `.opencode-state.md`,
2. inspect the repository,
3. compare implementation with the prompt,
4. calculate only the unfinished or unverified work.

If the prompt is already fully satisfied:

* make no unnecessary changes,
* run the relevant verification,
* mark the state `COMPLETE`.

If the new prompt changes the requested scope, preserve valid completed work and calculate a new minimal plan from the existing repository state.

\---

## 9\. Architecture invariants

Preserve the project architecture unless the user explicitly changes it.

Primary flow:

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

Rules:

* External systems go through integration boundaries.
* Background work goes through job boundaries.
* Dashboard is an aggregation layer, not the owner of other feature data.
* Assignments own assignment state.
* Reminders own time-based reminder behavior.
* Notifications own notification records, generation, and retrieval.
* The application remains a modular monolith unless a different architecture is explicitly approved.
* Do not duplicate services/files merely because an earlier run was forgotten.

\---

## 10\. Multi-agent rules

The primary `build` agent is the integration owner and default repository-changing agent.

Specialists:

```text
explorer  → read-only repository understanding
planner   → read-only decomposition/sequencing
reviewer  → read-only architecture/code review
tester    → validation and failure analysis
```

Do not give competing write access to multiple agents for the same files.

Preferred loop:

```text
Explore → Plan → Build → Test → Review → Fix → Checkpoint
```

Parallel agents should normally perform independent read-only analysis unless stable write boundaries have already been established.

All agents must respect `.opencode-state.md`; specialist output must not silently redefine the recorded build state.

\---

## 11\. Work priority

Unless the current prompt requires a different order, prefer:

1. Repair blockers.
2. Finish the current partial task.
3. Satisfy missing prerequisites.
4. Complete high-dependency foundations.
5. Complete integrated workflows.
6. Complete remaining feature work.
7. Strengthen tests and validation.
8. Polish UI and non-critical details.

The current partial task normally takes priority over starting unrelated work.

\---

## 12\. Definition of done

Never mark a task, feature, or Jira item complete merely because files exist.

Mark it complete only when:

1. Required behavior is implemented.
2. Architectural boundaries remain valid.
3. Relevant integrations are connected.
4. Relevant build/tests/typecheck/lint have been run where available.
5. Known failures are resolved or explicitly recorded.
6. No known required implementation remains.

For the current prompt, `.opencode-state.md` must finish with:

```md
## Status
COMPLETE

## Next Action
None — task complete.
```

\---

## 13\. Safety rules

Never:

* commit secrets;
* log credentials, tokens, or passwords;
* reset or discard user work without explicit approval;
* overwrite valid partial work just to restart cleanly;
* rewrite project architecture without an explicit decision;
* add premature infrastructure merely because it is familiar;
* create duplicate modules/services/files because previous progress was not checked;
* mark interrupted verification as passing;
* trust stale state over the actual repository.

Always leave the repository in a coherent and recoverable state.

\---

## 14\. Context-efficiency rule

The continuation system exists to reduce repeated context usage.

Therefore:

* do not reread every large specification file on every run;
* read only the portions needed for the current task;
* keep `.opencode-state.md` compact;
* store current state rather than conversation history;
* prefer repository inspection over repeating earlier reasoning;
* retain only recovery-critical notes.

The goal is:

```text
minimum repeated context
        +
maximum reliable continuation
        +
no broken or duplicated implementation
```

