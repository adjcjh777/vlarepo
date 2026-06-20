---
name: agent-bus-register
description: Register the current Codex session with the local Codex Agent Bus and claim queued or pending tasks for this session. Use when the user asks to join, register, identify, or name this agent; set the current session as planner, executor, tester, reviewer, or another role; hot-load queued work for a newly opened session; or prepare this session for Agent Bus list and inbox workflows.
---

# Agent Bus Register

Use this skill to make the current Codex session discoverable on the local Codex Agent Bus and to claim work that was queued for this session or role.

For broader Agent Bus workflows:

- Use `$agent-bus-delegate` for sending tasks, ACKs, replies, and visible delivery.
- Use `$agent-bus-team` for team creation, role aliases, launch, attach, and dispatch.
- Use `$agent-bus-diagnose` for stuck registration, inbox, trigger, or delivery failures.

## Quick Workflow

1. Decide `name` and `role` from the user's request.
   - If the user says "register as executor", use `name=executor`.
   - If no name is given, infer a short name from the current project folder.
   - Keep `role` concrete, for example `Executes implementation and tests in this project`.

2. Optionally run preflight only when checking setup:

```bash
python3 ~/.codex/skills/agent-bus-register/scripts/register_self.py --preflight
```

3. Register with the bundled script:

```bash
python3 ~/.codex/skills/agent-bus-register/scripts/register_self.py \
  --name executor \
  --role "Executes implementation and tests in this project"
```

Add repeated `--capability` or `--tag` flags when useful:

```bash
python3 ~/.codex/skills/agent-bus-register/scripts/register_self.py \
  --name tester \
  --role "Runs focused tests and reports failures" \
  --capability test \
  --tag qa
```

4. Report `agent_id`, `name`, `session_id`, `cwd`, `claimed_count`, and any `claimed_messages`.
   - Treat `session_id` as the unique routing identity.
   - Treat `agent_id` as a non-unique hint such as `planner`, `executor`, or `tester`.
   - Include `warnings`; registration can succeed while global CLI or hook setup is incomplete.

5. If `claimed_count > 0`, inspect the inbox before unrelated work:

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus inbox --target <session_id> --unread-only --limit 10
```

6. If registration fails because no current session record exists, do not invent a session id. Follow the script's `next_steps`. Usually either enable Agent Bus and open a fresh Codex session, or provide the session id from `/status`:

```bash
python3 ~/.codex/skills/agent-bus-register/scripts/register_self.py \
  --name executor \
  --role "Executes implementation and tests" \
  --session-id "<session id from /status>"
```

## Identity Rules

- Prefer `CODEX_AGENT_BUS_HOME` when set; otherwise use `~/.codex/agent-bus`.
- Registry records are keyed by Codex `session_id`.
- The script writes `agent_id` as a role/name hint and preserves older hints in `legacy_agent_ids`.
- Match the current session by the newest registry record whose `cwd` equals the current working directory.
- Prefer unnamed hook records when multiple records share the same `cwd`.
- Registration claims pending-target messages addressed to this `name`, `session_id`, `agent_id`, compatible tags, or compatible cwd prefix.
- Claimed messages become visible through `agent-bus inbox --target <session_id>`.

## Follow-Up Checks

After registration, if the Agent Bus CLI exists, run:

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus list
```

Use this only to confirm visibility. Do not expose unrelated config or message content.

If a claimed task requires a reply or ACK, switch to `$agent-bus-delegate` and reply to the original `message_id`.

## Safety

- Never read Codex auth files, API keys, transcripts, or unrelated private state.
- Never edit `~/.codex/config.toml`; installation is separate and must be explicit.
- If `~/.codex/tools/codex-agent-bus/bin/agent-bus` is missing, explain that the global Agent Bus install is incomplete and show the install command suggested by the script, but do not run it automatically.
- Do not use this skill to send work, create teams, wake threads, or debug stuck delivery. Route those workflows to the narrower Agent Bus skill.
