---
name: agent-bus-team
description: Create and manage role-based Agent Bus project teams. Use when the user asks to create, join, launch, attach, inspect, or dispatch an Agent Bus team; define planner, executor, tester, reviewer, scout, or role aliases; bootstrap future agents; spawn subagents for roles; or route role-scoped work through Agent Bus.
---

# Agent Bus Team

Use this skill when the user wants organized multi-agent collaboration around a project or goal.

## Default Team Shape

Infer roles from the user's request. When unspecified, start with:

- `planner`: plans tasks and maintains the ledger.
- `executor`: implements bounded changes.
- `tester`: runs focused verification and reports PASS/BLOCKED.
- `reviewer`: audits final claims, scope boundaries, secrets, and release readiness when risk warrants it.

Use stable role aliases so future sessions can claim queued bootstrap work.

## Create a Team

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus team create <team-name> \
  --project /absolute/project/path \
  --goal "<team goal>" \
  --role planner:"Plans tasks and maintains the ledger" \
  --role executor:"Implements bounded changes" \
  --role tester:"Runs focused verification"
```

This creates durable team state, role aliases, pending bootstrap messages, and launch prompts. It does not by itself prove that visible Codex threads were created.

## Launch and Attach

Preferred path for visible Codex App role threads:

1. Run:

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus team launch <team-id-or-name> --mode codex-app
```

2. If the launch result includes `project_resolution.status=project_lookup_required`, call `codex_app.list_projects`, choose the deepest saved project path that contains the team project path, then rerun launch with `--codex-project-id <projectId>` or fill the returned `create_thread_request.target.projectId`.

3. For each returned `create_thread_request`, call `codex_app.create_thread`. This creates the left-sidebar-visible Codex App thread.

4. Immediately call the returned `attach_after_create` command using `create_thread.threadId`.

5. If attach returns `visible_delivery`, call `codex_app.send_message_to_thread` with the created thread id and `visible_delivery.prompt` so the role receives the canonical Agent Bus bootstrap message.

Use subagent launch when the controller wants in-turn worker agents instead of persistent Codex App threads:

1. Run:

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus team launch <team-id-or-name> --mode subagent-tool
```

2. For each returned `spawn_request`, call the available subagent spawn tool from the controller conversation.

3. Attach the returned subagent id as the role thread/session handle:

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus team attach-thread <team-id-or-name> \
  --role <role> \
  --thread-id <spawn_agent.agent_id>
```

Do not ask the spawned agent to guess its own id.

Use prompt mode when a human or controller will open sessions manually:

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus team launch <team-id-or-name> --mode prompt
```

Use attach when a real role conversation already exists:

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus team attach-thread <team-id-or-name> \
  --role tester \
  --thread-id <existing-thread-id-or-session-id>
```

## Dispatch Role Work

Choose the dispatch transport from the role's real target:

- Attached Codex App thread/session: prefer `--trigger codex_app`.
- Spawned subagent controlled by the current conversation: use `--trigger subagent_tool`.
- Future role with no real thread: use `--trigger queue` or pending bootstrap flow.

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus team dispatch <team-id-or-name> \
  --role tester \
  --trigger <codex_app|subagent_tool|queue> \
  "<task>"
```

If the command returns a transport payload for a visible subagent or Codex App thread tool, call that tool with the returned target and prompt. The Bus record is durable, but the target sees the task only after the visible transport succeeds.

## Team Commands

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus team list
~/.codex/tools/codex-agent-bus/bin/agent-bus team show <team-id-or-name>
~/.codex/tools/codex-agent-bus/bin/agent-bus team join <team-id> --role tester --agent <session-id-or-name>
```

## Boundaries

- Use `$agent-bus-register` when a role session needs to register and claim its pending bootstrap message.
- Use `$agent-bus-delegate` for ACK/reply handling and visible delivery verification.
- Use `$agent-bus-diagnose` when team dispatch is queued but not visible.
- Prefer `team launch --mode codex-app` for native Codex App thread creation.
- Treat `team launch --mode app-server-experimental` as legacy experimental fallback. It may create an app-server thread id, but Codex App visibility still needs ACK or visible-delivery proof.
- Until a real session exists, role tasks are pending Bus records only.
