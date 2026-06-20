---
name: agent-bus-delegate
description: Send Agent Bus messages, delegate tasks, verify visible delivery, and reply or ACK to Bus messages. Use when the user asks to send, delegate, dispatch, notify, wake, acknowledge, or reply to another agent or thread; handle pending targets; use reply_message or agent-bus reply; or distinguish durable Bus storage from visible Codex thread delivery.
---

# Agent Bus Delegate

Use this skill to move work between agents after the sender and target identity are clear.

## Core Rule

Treat delivery as two layers:

1. Durable Bus record: a message exists in the Agent Bus store with a `message_id`.
2. Visible Codex delivery: the target session or subagent actually sees and can act on the prompt.

Never claim visible delivery from Bus storage alone.

## Send Workflow

1. Resolve the target.
   - Existing Codex App thread/session: target the `session_id` and plan to use Codex App visible delivery.
   - Existing spawned subagent: use the returned subagent id and the subagent transport.
   - Future agent/role alias: use a stable alias such as `executor`, `tester`, `scout`, or a team role alias.

2. Create the canonical Bus message and capture `message_id`.

For existing Codex App threads that should see the task now, prefer one `codex_app` send. This creates the Bus record and prepares or performs visible delivery:

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus send <target> "<task>" \
  --from-agent <sender_session_id_or_name> \
  --trigger codex_app \
  --timeout-sec 15 \
  --correlation-id <uuid>
```

If this returns a `codex_app.send_message_to_thread` payload instead of delivering by itself, immediately call that Codex App tool with the returned thread id and prompt.

If using a direct Codex App thread tool without the Agent Bus `codex_app` transport, first create a queue record, then send the visible prompt with the same `message_id` and `correlation_id`:

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus send <target_session_id> "<task>" \
  --from-agent <sender_session_id_or_name> \
  --trigger queue \
  --correlation-id <uuid>
```

For future sessions without a real thread, add `--allow-pending`:

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus send executor "<task>" \
  --from-agent planner \
  --trigger queue \
  --allow-pending \
  --correlation-id <uuid>
```

3. For every visible prompt, include:
   - original `message_id`
   - `correlation_id`
   - sender and target names
   - exact reply instruction

Direct visible prompt shape:

```text
After finishing, reply through Agent Bus:
reply_message(message_id='<original message_id>', result='...')
Fallback if MCP is unavailable:
~/.codex/tools/codex-agent-bus/bin/agent-bus reply <original message_id> '<result>' --from-agent <your_session_id> --trigger queue
```

4. Verify both layers when visible delivery matters.

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus health
~/.codex/tools/codex-agent-bus/bin/agent-bus inbox --target <target_session_id> --unread-only --limit 5
```

A visible thread send result or target ACK confirms the Codex-side layer.

## Reply or ACK Workflow

Prefer the MCP `reply_message` tool when it is available. If not, use the CLI immediately:

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus reply <message_id> '<json_or_result>' \
  --from-agent <session_id> \
  --trigger queue
```

Use the exact JSON body requested by the user or sender when they ask for a receipt such as `ACK_DELIVERY_RECEIVED`.

After processing a reply message, mark it read:

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus mark-read <reply_message_id>
```

## Trigger Cautions

- Prefer `--trigger queue` for durable records and pending targets.
- Prefer `--trigger codex_app` or the direct Codex App thread tool for existing Codex App threads that should see the task now.
- Prefer `--trigger subagent_tool` for spawned subagents.
- Use `--allow-pending` only for intentional stable names or role aliases.
- Avoid sending multiple `--trigger resume` or `--trigger codex_app` commands in parallel.
- If using `resume` or `codex_app`, send one message at a time and add a small timeout such as `--timeout-sec 15`.
- If a send hangs, stop retrying the wake trigger and use `$agent-bus-diagnose`.

## Failure Wording

When Bus storage works but the user or target cannot see the task, say:

```text
Bus storage is healthy, visible thread delivery is not confirmed.
```

Then visibly resend the same task if the user needs the target thread to see it, preserving the original `message_id` and `correlation_id`.
