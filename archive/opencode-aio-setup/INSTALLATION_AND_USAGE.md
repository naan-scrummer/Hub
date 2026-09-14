# AIO Student's Hub — Installation and Usage

## 1. Copy the project instructions

Copy this file into the root of the AIO Student's Hub repository:

```text
AGENTS.md
```

This gives OpenCode persistent project guidance. Current OpenCode documentation recommends `AGENTS.md` for project-specific build commands, architecture, and verification requirements. 

## 2. Copy the agents

Copy:

```text
.opencode/agents/build.md
.opencode/agents/explorer.md
.opencode/agents/planner.md
.opencode/agents/reviewer.md
.opencode/agents/tester.md
```

into:

```text
<your-project>/.opencode/agents/
```

OpenCode discovers project agents from `.opencode/agents/`. 

## 3. Start OpenCode from the repository root

```bash
cd /path/to/AIO-Students-Hub
opencode
```

## 4. Start with the primary Build agent

The custom `build` agent is the primary integration owner.

Depending on the OpenCode version/UI, it may be selectable as the `build` primary agent.

## 5. On every run, attach the three existing control/specification files

Use exactly the existing workflow:

```text
@AIO_Students_Hub_Build_Execution_Controller.md
@AIO_Students_Hub_Master_Scaffold_Prompt.md
@Jira_workItems_48(1).csv
```

You do not need a separate prompt for every run.

A useful opening message is:

```text
Continue AIO Student's Hub from the existing repository state.

Use the attached:
@AIO_Students_Hub_Build_Execution_Controller.md
@AIO_Students_Hub_Master_Scaffold_Prompt.md
@Jira_workItems_48(1).csv

First reconcile the persistent build state with the actual repository.
Then use the available specialist subagents when useful.
Do not restart completed work.
Build the highest-priority unblocked atomic work package and checkpoint before ending the run.
```

## 6. How to invoke specialists

Use the OpenCode agent mention mechanism available in your version.

Typical examples:

```text
@explorer inspect current repository state for Assignments
```

```text
@planner create the next atomic implementation package
```

```text
@tester validate the current Assignment → Reminder → Notification path
```

```text
@reviewer audit the latest implementation against the specification
```

The exact UI/mention behavior may vary by OpenCode version; the agent IDs come from the filenames. 

## 7. Recommended cadence inside a run

For a meaningful feature:

```text
Explorer
  ↓
Planner
  ↓
Build
  ↓
Tester
  ↓
Reviewer
  ↓
Build fixes
  ↓
Tester again
  ↓
Checkpoint
```

For a tiny, obvious task:

```text
Build
  ↓
Tester
  ↓
Checkpoint
```

Do not use all agents mechanically for every small edit.

## 8. If OpenCode reports an agent/config syntax error

OpenCode has changed configuration syntax between documentation generations. The current V2 documentation uses `permissions` with action/resource/effect rules, while older examples use the older `permission` object syntax. The files in this package follow the current V2-oriented agent/permission format. 

If your installed OpenCode version rejects that frontmatter, run:

```bash
opencode --version
```

and adjust the agent frontmatter to the syntax supported by that installed version rather than weakening the agent roles.

## 9. Do not add worktrees yet

Start with one repository checkout.

Use subagents for analysis and review.

Only introduce parallel coding/worktrees after the architecture has stable interfaces and you have a concrete reason to parallelize implementation.
