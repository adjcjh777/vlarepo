# Codex Agent Bus

Codex Agent Bus is a local MCP server, registry, hook, and CLI that lets independent Codex sessions discover each other and exchange work across any project folder on the same machine.

It does not modify Codex source code, does not open a public port, and does not read `~/.codex/auth.json` or other secret files. Messages are local JSON files.

## Install

From this directory:

```bash
python3 scripts/install_agent_bus.py --user
```

The installer copies the tool to:

```text
~/.codex/tools/codex-agent-bus/
```

It then writes a managed block to:

```text
~/.codex/config.toml
```

Before writing, it creates a timestamped backup of the existing config. The configured commands are absolute paths to:

```text
~/.codex/tools/codex-agent-bus/bin/agent-bus-mcp
~/.codex/tools/codex-agent-bus/bin/agent-bus-hook
~/.codex/tools/codex-agent-bus/bin/agent-bus
```

## Global Data

By default all projects share:

```text
~/.codex/agent-bus/registry.json
~/.codex/agent-bus/messages.jsonl
~/.codex/agent-bus/teams.json
~/.codex/agent-bus/locks/
~/.codex/agent-bus/logs/agent-bus.log
```

Override with:

```bash
export CODEX_AGENT_BUS_HOME=/some/absolute/path
```

Each agent record stores its own `cwd`. When `send_message(..., trigger="resume")` wakes a target session, transport uses the target record's `cwd`, not the caller's cwd.

## Identity Model

The canonical Agent Bus identity is the Codex session id from `/status`.

```text
agent_id == session_id
```

`name` is only a human-readable alias, such as `planner`, `executor`, or `bandofagents-tester`. Older name-derived ids are migrated into `legacy_agent_ids` so existing messages and commands can still resolve them, but new records and `list_agents` display the session id as `agent_id`.

## Typical Flow

In each Codex session, register a useful name:

```text
register_agent(name="planner", role="Plans and delegates work", session_id="<from /status>", cwd="/path/to/project")
```

List peers:

```text
list_agents()
```

Delegate across projects:

```text
send_message(target="executor", message="Run the focused tests and report failures.")
```

Queue work for a session that has not been opened yet:

```text
send_message(target="executor", message="Run the focused tests.", trigger="queue", allow_pending=true)
```

This writes a `pending_target` message keyed by the future agent name. When a later Codex session
registers with `name="executor"`, registration claims the queued message, fills in
`to_agent_id == to_session_id == <new session id>`, and returns `claimed_count` plus
`claimed_messages`. The new agent can then run:

```text
get_inbox(target="<new session id>", unread_only=true)
```

For interactive Codex app sessions, use the default `trigger="codex_app"`:

```text
send_message(target="executor", message="Run the focused tests and report failures.")
```

The tool writes the global log entry and returns:

```text
transport.surface = "codex_app.send_message_to_thread"
transport.threadId = "<target session id>"
transport.prompt = "<user-visible delegated task>"
```

The calling agent must then call the official Codex App tool:

```text
codex_app.send_message_to_thread(threadId=transport.threadId, prompt=transport.prompt)
```

This is the path intended to make the task visible as a user input in the target Codex thread.

For headless CLI automation, use `trigger="resume"`. Agent Bus then tries:

1. `codex app-server proxy` JSON-RPC, using `thread/resume` followed by `turn/start` with text input.
2. `codex exec resume <SESSION_ID>` as non-interactive fallback.

`exec_resume_noninteractive` may not appear in an already-open Codex UI.

Finish delegated work:

```text
reply_message(message_id="<original-message-id>", result="Done. Tests pass.")
```

## CLI

The installed CLI mirrors the MCP tools:

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus health
~/.codex/tools/codex-agent-bus/bin/agent-bus list
~/.codex/tools/codex-agent-bus/bin/agent-bus send executor "Please run tests"
```

Use `--trigger queue` to record a message without waking the target Codex session. Queue mode only proves that the global log/inbox path works; it does not make the target Codex UI show a new user message.

Use `--allow-pending` when the target name is intentional but the target session is not registered
yet:

```bash
agent-bus send executor "Run tests after you open" --trigger queue --allow-pending
agent-bus register --name executor --role "Runs tests" --session-id <new-session-id> --cwd /path/to/project
agent-bus inbox --target <new-session-id> --unread-only
```

Pending-target messages are durable Bus records, not visible Codex turns. If the task must appear as
a user-visible prompt, resend visibly after the target session exists, preserving the original
`message_id` and `correlation_id`.

## Project Teams

Create a role-based project team from one controller conversation:

```bash
agent-bus team create dreamqa \
  --project /path/to/project \
  --goal "Improve Dream QA with implementation, testing, and release review" \
  --role planner:"Plans tasks and maintains the ledger" \
  --role executor:"Implements bounded code changes" \
  --role tester:"Runs read-only verification"
```

The command writes a `teams.json` record and creates one pending bootstrap message per role. Role
targets are team-scoped aliases such as `dreamqa-planner`, `dreamqa-executor`, and
`dreamqa-tester`, so roles do not collide with generic agent names in other projects.

The response includes `launch_prompts`. Paste one launch prompt into a new Codex App conversation,
or otherwise open a new Codex session and register with the specified alias. When that new session
registers, it claims the pending role message and the team role becomes `active`.

For a one-dialogue Codex controller flow:

1. Create the team.
2. Run `agent-bus team launch <team> --mode subagent-tool`.
3. Call `multi_agent_v1.spawn_agent` once per returned `spawn_request`.
4. Attach each returned `agent_id` with `agent-bus team attach-thread`.
5. Use `team dispatch` for subsequent role tasks and rebalancing.

The spawned agent does not need to know its own id; the controller records the mapping.

Useful commands:

```bash
agent-bus team list
agent-bus team show dreamqa
agent-bus team launch dreamqa --mode subagent-tool
agent-bus team launch dreamqa --role tester
agent-bus team attach-thread dreamqa --role tester --thread-id <existing-thread-id>
agent-bus team join <team-id> --role tester --agent <existing-session-id-or-name>
agent-bus team dispatch <team-id> --role tester "Run the smoke suite and report PASS/BLOCKED"
```

`team launch --mode subagent-tool` is the preferred one-dialogue controller path when Codex has the
`multi_agent_v1.spawn_agent` tool. It returns one `spawn_request` per role. The controller should
call `multi_agent_v1.spawn_agent` with that request, then immediately attach the returned
`agent_id`:

```bash
agent-bus team launch dreamqa --role tester --mode subagent-tool
agent-bus team attach-thread dreamqa --role tester --thread-id <spawn_agent.agent_id>
```

This keeps the role name (`tester`) separate from the spawned thread/session id and records the
mapping in `teams.json`.

For later visible tasks to a spawned subagent, dispatch with the subagent trigger and then call the
returned tool payload:

```bash
agent-bus team dispatch dreamqa --role tester --trigger subagent_tool "Run focused tests"
```

The response contains:

```text
transport.surface = "multi_agent_v1.send_input"
transport.target = "<spawn_agent.agent_id>"
transport.prompt = "<delegated task prompt>"
```

The controller must call `multi_agent_v1.send_input(target=transport.target,
message=transport.prompt)` for visible delivery to the spawned agent.

`team launch` updates each role's launch state and returns the current launch prompt. It is safe to
run repeatedly:

```bash
agent-bus team launch dreamqa
agent-bus team launch dreamqa --role executor --mode prompt
```

If a Codex App conversation already exists, attach it to the role:

```bash
agent-bus team attach-thread dreamqa --role executor --thread-id <thread-or-session-id>
```

This registers the role alias against that `thread_id`, claims the pending bootstrap message, marks
the role `active`, and returns a `codex_app.send_message_to_thread` payload so the controller can
make the bootstrap task visible in that conversation.

There is also an experimental app-server thread launcher:

```bash
agent-bus team launch dreamqa --role tester --mode app-server-experimental
```

This calls the internal app-server `thread/start` protocol and, when it returns a thread id, attaches
that id to the role. The role status becomes `thread_created_unverified_visibility`, because the Bus
can verify that app-server returned a thread id but cannot by itself prove the thread appeared in the
Codex App UI. Add `--deliver-bootstrap` to also try `thread/resume` + `turn/start` delivery to the
new thread.

Thread creation boundary:

- Team creation does not claim that Codex App visible conversations were automatically created.
- `team launch --mode subagent-tool` is the preferred Codex-controller path: Agent Bus returns
  spawn payloads, the controller calls `multi_agent_v1.spawn_agent`, then attaches the returned id.
- `team launch --mode prompt` is a durable launch plan, not automatic UI creation.
- `team attach-thread` is the reliable path when a real `threadId`/session already exists.
- `team launch --mode app-server-experimental` can return a thread id from internal app-server
  `thread/start`, but visibility still needs a separate App-side ACK or successful visible delivery.
- Until a real `threadId` exists, team work is represented as pending Bus records plus launch
  prompts. Once a session exists, use the normal visible-delivery path and preserve `message_id`,
  `correlation_id`, `team_id`, and role alias.

You can force a transport while testing:

```bash
agent-bus send executor "Visible user-turn test"
agent-bus send --trigger resume executor "Headless fallback test"
CODEX_AGENT_BUS_TRANSPORT=exec agent-bus send --trigger resume executor "Non-interactive fallback test"
```

## Loop Guard

Messages carry `correlation_id` and `hop_count`. Resume triggering is refused when `hop_count` exceeds 6.

## Rollback

Restore the backup printed by the installer, or remove the managed block between:

```text
# BEGIN CODEX_AGENT_BUS
# END CODEX_AGENT_BUS
```

The installed tool directory and data directory can then be removed manually.
