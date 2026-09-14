# AIO Student's Hub — Multi-Agent OpenCode Implementation Guide

## What this setup is

This setup creates a small team of specialized OpenCode agents around the existing AIO Student's Hub build system.

```text
                         PRIMARY BUILD AGENT
                                  │
             ┌────────────────────┼────────────────────┐
             ↓                    ↓                    ↓
         EXPLORER              PLANNER              TESTER
       read-only map        read-only plan       validation
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  ↓
                              BUILD CODE
                                  │
                                  ↓
                              REVIEWER
                            read-only audit
                                  │
                                  ↓
                         BUILD AGENT FIXES
                                  │
                                  ↓
                              CHECKPOINT
```

OpenCode supports project-specific agents in `.opencode/agents/`, with `primary` and `subagent` modes. Read-only agents can be restricted with permissions. See the current OpenCode agent and permission documentation for the installed syntax. 

## Files

```text
AGENTS.md
.opencode/
└── agents/
    ├── build.md
    ├── explorer.md
    ├── planner.md
    ├── reviewer.md
    └── tester.md
```

## Why the main builder owns integration

The project has many shared architectural surfaces:

- database models;
- migrations;
- authentication;
- service contracts;
- cross-module workflows;
- shared API schemas;
- job boundaries.

Allowing several coding agents to change these simultaneously would increase merge and architecture risk.

Therefore:

```text
Subagents = analysis / validation by default
Build agent = implementation + integration owner
```

Parallel coding is reserved for rare cases where interfaces are already stable and file ownership is explicit.

## How the agents work together

### Explorer
Use when the builder needs to understand the existing state before editing.

Example request:

```text
Use @explorer to inspect the current Assignment module and tell me exactly what exists, what is partial, and which files are relevant to SCRUM03-F009.*.
```

### Planner
Use after exploration/reconciliation.

Example request:

```text
Use @planner to produce the smallest safe next work package for the current repository state, respecting the Master Scaffold and Jira CSV.
```

### Tester
Use after implementation or when a failure needs independent diagnosis.

Example request:

```text
Use @tester to run the relevant Assignment/Reminder/Notification validation and classify any failures. Do not edit files.
```

### Reviewer
Use after meaningful implementation changes.

Example request:

```text
Use @reviewer to audit the current changes against the Master Scaffold and affected Jira items. Do not edit files.
```

## Recommended build cycle

```text
READ
 ↓
RECONCILE
 ↓
EXPLORE
 ↓
PLAN
 ↓
CHECKPOINT IN_PROGRESS
 ↓
BUILD
 ↓
TEST
 ↓
REVIEW
 ↓
FIX
 ↓
TEST AGAIN
 ↓
UPDATE JIRA TRACEABILITY
 ↓
CHECKPOINT
```

The build agent may skip an unnecessary subagent call when the task is obvious and well-bounded. More agents is not automatically better.

## Persistent memory

The most important state remains:

```text
docs/build-progress.md
docs/build-state.json
docs/build-log.md
docs/jira-traceability.md
```

Subagents do not replace these files.

A fresh OpenCode session must be able to continue using only:

```text
Master Scaffold
Jira CSV
Build Controller
Repository
Persistent build state
```

## Existing three-file loop remains valid

You should still use:

```text
@AIO_Students_Hub_Build_Execution_Controller.md
@AIO_Students_Hub_Master_Scaffold_Prompt.md
@Jira_workItems_48(1).csv
```

on every new run.

The agents simply make the execution within each run more disciplined.

## If a run is interrupted

Do not attempt to reconstruct the previous conversation.

Start the next run by:

```text
read specifications
→ read build state
→ inspect repository
→ reconcile
→ resume
```

## What not to do

Do not:

```text
open 5 terminals
→ let 5 agents edit the same checkout
```

unless you deliberately create isolated worktrees and define merge ownership.

The recommended initial setup does not require multiple worktrees.
