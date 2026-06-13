---
name: agent-bus-register
description: Register the current Codex session with the local Codex Agent Bus. Use when the user asks to join/register/identify this agent, set this session as planner/executor/tester/reviewer, enable cross-project agent communication, or quickly prepare the current Codex session for Agent Bus list_agents/send_message/reply_message workflows.
---

# Agent Bus Register

Use this skill to make the current Codex session discoverable on the local Codex Agent Bus.

## Quick Workflow

1. Decide the `name` and `role` from the user's request.
   - If the user says "注册成 executor", use `name=executor`.
   - If no name is given, infer a short name from the current project folder, such as `build-small-agent`.
   - Keep `role` concrete, for example `Executes implementation and tests in this project`.

2. Optional: run preflight when diagnosing setup:

```bash
python3 ~/.codex/skills/agent-bus-register/scripts/register_self.py --preflight
```

3. Run the bundled script:

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

4. Report the registered `agent_id`, `name`, `session_id`, and `cwd`. If the script returns `warnings`, include them because registration can succeed while the global Agent Bus CLI/hook installation is still missing.
   - `agent_id` must equal the Codex `session_id`. Treat `name` as a human alias only.

5. If registration fails because no current session record exists, do not invent a session id. Follow the script's `next_steps`. Usually either install/enable Agent Bus and open a fresh Codex session, or provide the session id from `/status`:

```bash
python3 ~/.codex/skills/agent-bus-register/scripts/register_self.py \
  --name executor \
  --role "Executes implementation and tests" \
  --session-id "<session id from /status>"
```

## Behavior

- Prefer the global bus home `CODEX_AGENT_BUS_HOME` when set.
- Otherwise use `~/.codex/agent-bus`.
- The canonical Agent Bus identity is the Codex session id. The script writes `agent_id == session_id` and keeps any older name-derived ids only in `legacy_agent_ids` for compatibility.
- Match the current session by finding the newest registry record whose `cwd` equals the current working directory.
- Prefer unnamed hook records when multiple records share the same `cwd`.
- If `~/.codex/tools/codex-agent-bus/bin/agent-bus` is missing, explain that the global Agent Bus install has not been completed and show the install command, but do not run it automatically.
- Never read Codex auth files, API keys, or transcripts.
- Never edit `~/.codex/config.toml`; installation is separate and must be explicit.

## Follow-Up Checks

After registration, if the Agent Bus CLI exists, run:

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus list
```

Use this only to confirm visibility; do not expose unrelated secrets or config content.
