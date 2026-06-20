---
name: agent-bus
description: Route Agent Bus multi-agent coordination workflows across registration, delegation, teams, and diagnostics. Use when the user asks generally about Agent Bus, multi-agent coordination, cross-agent communication, planner/executor/tester/reviewer collaboration, or when no narrower Agent Bus skill clearly fits.
---

# Agent Bus

Use this as the lightweight entrypoint for the Agent Bus skill family. Classify the request, then load or follow the narrow skill that owns the work.

## Routing

- Register, identify, join as a role, or claim queued messages: use `$agent-bus-register`.
- Send/delegate a task, ACK or reply to a message, verify visible delivery, or use pending targets: use `$agent-bus-delegate`.
- Create a project team, define role aliases, launch or attach role sessions, or dispatch role-scoped work: use `$agent-bus-team`.
- Debug missing agents, stuck sends, hung triggers, unclaimed pending messages, or queued-but-not-visible delivery: use `$agent-bus-diagnose`.

If a request spans multiple areas, use this order:

1. Register the current session if identity or inbox state matters.
2. Create or attach teams if the user asked for role structure.
3. Delegate work or reply to messages.
4. Diagnose only if a concrete failure appears.

## Global Invariants

- `session_id` is the canonical Agent Bus routing identity.
- `agent_id` is a non-unique role or name hint.
- Durable Bus storage and visible Codex thread delivery are separate proof layers.
- A queued message, pending message, or `last_seen` update does not prove the target saw the task.
- Do not read Codex auth files, API keys, transcripts, or unrelated private state.
- Do not edit `~/.codex/config.toml` unless the user explicitly asks for installation/configuration work.
- Avoid `resume` and `codex_app` triggers unless the user needs visible wake-up and the narrow skill's timeout rules are followed.

## Reporting Standard

Report the concrete identifiers that make the workflow auditable: `session_id`, `agent_id`, `message_id`, `correlation_id`, `team_id`, role alias, cwd, trigger, and delivery status when available.

State uncertainty explicitly. For example: "Bus storage is queued; visible thread delivery is not yet confirmed."
