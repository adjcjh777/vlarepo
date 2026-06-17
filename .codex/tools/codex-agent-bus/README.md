# Codex Agent Bus

Local message bus for independent Codex sessions. It provides:

- a global registry at `~/.codex/agent-bus/registry.json`
- a global message log at `~/.codex/agent-bus/messages.jsonl`
- stable wrappers in `bin/`
- a minimal stdio MCP server
- Codex hooks for automatic session registration
- CLI commands for audit and manual operation
- pending-target queues for agents that will be opened and registered later
- project team manifests with role aliases, launch prompts, late joins, and task redispatch
- Codex App thread delivery (`codex_app.send_message_to_thread`) for visible user turns, with app-server / `codex exec resume` as headless fallback

Install for all project folders:

```bash
python3 scripts/install_agent_bus.py --user
```

See [docs/agent-bus.md](docs/agent-bus.md) for usage and rollback.
