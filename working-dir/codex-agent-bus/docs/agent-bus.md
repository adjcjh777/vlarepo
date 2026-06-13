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
~/.codex/agent-bus/locks/
~/.codex/agent-bus/logs/agent-bus.log
```

Override with:

```bash
export CODEX_AGENT_BUS_HOME=/some/absolute/path
```

Each agent record stores its own `cwd`. When `send_message(..., trigger="resume")` wakes a target session, transport uses the target record's `cwd`, not the caller's cwd.

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
send_message(target="executor", message="Run the focused tests and report failures.", trigger="resume")
```

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

Use `--trigger queue` to record a message without waking the target Codex session.

## Loop Guard

Messages carry `correlation_id` and `hop_count`. Resume triggering is refused when `hop_count` exceeds 6.

## Rollback

Restore the backup printed by the installer, or remove the managed block between:

```text
# BEGIN CODEX_AGENT_BUS
# END CODEX_AGENT_BUS
```

The installed tool directory and data directory can then be removed manually.
