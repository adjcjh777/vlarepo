---
name: agent-bus-register
description: Register the current Codex session with the local Codex Agent Bus and claim queued tasks for this session. Use when the user asks to join/register/identify this agent, set this session as planner/executor/tester/reviewer, enable cross-project agent communication, hot-load messages for newly opened agent sessions, or quickly prepare the current Codex session for Agent Bus list_agents/send_message/reply_message workflows.
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

4. Report the registered `agent_id`, `name`, `session_id`, `cwd`, and any `claimed_count` /
   `claimed_messages`. If the script returns `warnings`, include them because registration can
   succeed while the global Agent Bus CLI/hook installation is still missing.
   - `agent_id` must equal the Codex `session_id`. Treat `name` as a human alias only.
   - If `claimed_count > 0`, immediately inspect the inbox before starting unrelated work.

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
- Registration claims pending-target messages addressed to this `name`, `session_id`, `agent_id`, or
  compatible tags/cwd prefix. Claimed messages are updated with this session id and become visible
  through `agent-bus inbox --target <session_id>`.
- If `~/.codex/tools/codex-agent-bus/bin/agent-bus` is missing, explain that the global Agent Bus install has not been completed and show the install command, but do not run it automatically.
- Never read Codex auth files, API keys, or transcripts.
- Never edit `~/.codex/config.toml`; installation is separate and must be explicit.

## Follow-Up Checks

After registration, if the Agent Bus CLI exists, run:

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus list
```

Use this only to confirm visibility; do not expose unrelated secrets or config content.

If registration reports claimed messages, inspect them:

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus inbox --target <session_id> --unread-only --limit 10
```

## Future-Agent Hot Loading

Agent Bus supports queuing work for agent sessions that have not been opened yet. Use this when a
planner wants to publish tasks for an executor/tester/scout before those Codex sessions exist.

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus send executor "Run focused tests and report PASS/BLOCKED" \
  --from-agent planner \
  --trigger queue \
  --allow-pending \
  --correlation-id <uuid>
```

This records a durable `pending_target` message keyed by `target_query=executor`. It does not wake a
Codex UI because there is no session id yet. When a later session runs this skill with
`--name executor`, registration claims the message, fills in `to_agent_id == to_session_id ==
<new session_id>`, and reports `claimed_count`.

Rules:

- Use `--allow-pending` only when the target name is intentional and stable, such as `executor`,
  `tester`, `ui-ux`, `scout`, or a repo-specific role alias.
- Treat pending-target delivery as Bus-side hot loading, not visible Codex-thread delivery. If the
  task must appear as a user-visible prompt, resend visibly after the target session exists while
  preserving the original `message_id` and `correlation_id`.
- After claiming, the target agent should read inbox, do the task, then reply to the original
  message id with `reply_message(message_id=..., result=...)`.

## Reliable Message Delivery

When using Agent Bus for delegation, registration is not enough. A message can be written to the
Bus store while the target Codex thread still does not visibly receive the task. Treat delivery as a
two-layer system:

1. Durable Bus record: the request exists in `~/.codex/agent-bus/messages.jsonl` with a
   `message_id`.
2. Visible Codex thread delivery: the target agent can actually see and act on the prompt.

Do not assume `last_seen` changes or a queued message means the target saw the task.

Recommended safe workflow:

1. Create the canonical Bus message with the CLI and capture its `message_id`.

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus send <target> "<task>" \
  --from-agent <sender> \
  --trigger queue \
  --correlation-id <uuid> \
  --hop-count <n>
```

If the intended target session does not exist yet, add `--allow-pending --trigger queue` instead of
retrying `resume` / `codex_app`. The later agent registration will claim the queued task.

2. If the task must visibly wake or notify another Codex thread, send a matching visible prompt to
   the target `session_id` with the Codex thread tool when available. Include the original
   `message_id`, `correlation_id`, sender/target names, and an explicit reply instruction:

```text
完成后必须调用 Agent Bus:
reply_message(message_id='<original message_id>', result='...')
```

3. Verify delivery:
   - `agent-bus health` confirms the registry/message store is readable and writable.
   - `agent-bus inbox --target <target> --unread-only --limit 5` confirms the Bus-side record.
   - A visible thread send result or an ACK/reply from the target confirms Codex-side delivery.

4. When the target replies, mark processed replies read after handling them:

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus mark-read <reply_message_id>
```

## Send Trigger Cautions

- Avoid sending multiple `agent-bus send --trigger resume` or `--trigger codex_app` commands in
  parallel. These triggers can block while trying to wake Codex or the app bridge.
- If you use `resume` or `codex_app`, always add a small timeout, for example
  `--timeout-sec 15`, and send one message at a time.
- If a send command hangs, interrupt it, then inspect:

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus health
tail -n 20 ~/.codex/agent-bus/messages.jsonl
```

- If the message exists with `status: queued` or `status: prepared` but the user or target agent
  cannot see it, the Bus store worked but visible delivery failed. Use the Codex thread tool to
  visibly resend the same task, preserving the original `message_id` so the target can still
  `reply_message` to the canonical Bus record.
- `last_seen` in `agent-bus list` is only a weak signal. It may update because the session was
  touched, not because the task became visible.

## Incident Note: Queued But Not Visible

Observed failure mode:

- Three delegations sent with `--trigger resume` were persisted to `messages.jsonl`.
- The CLI processes hung in the resume/app transport layer and produced no useful output.
- The target sessions existed and `last_seen` changed, but the user could not see the delegated
  prompts in the target threads.
- Recovery was to interrupt the hung sends, confirm `agent-bus health`, inspect
  `messages.jsonl`, then use visible Codex thread delivery with the original Bus `message_id`.

When a user says they cannot see a delegated Agent Bus task, treat that as a real delivery failure
until proven otherwise. Report the distinction clearly: "Bus storage is healthy, visible thread
delivery failed", then resend visibly and verify an ACK.
