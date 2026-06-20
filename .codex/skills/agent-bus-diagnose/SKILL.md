---
name: agent-bus-diagnose
description: Diagnose Agent Bus setup, registry, inbox, trigger, and delivery failures. Use when Agent Bus registration, list, inbox, send, resume, codex_app, pending-target claiming, ACK, reply, team dispatch, or visible delivery appears stuck, missing, ambiguous, or inconsistent.
---

# Agent Bus Diagnose

Use this skill for read-mostly diagnosis of Agent Bus state and delivery failures.

## Safety

- Do not read Codex auth files, API keys, transcripts, or unrelated private state.
- Do not edit `~/.codex/config.toml` during diagnosis.
- Do not expose unrelated message contents. Report only the identifiers and snippets needed for the issue.
- Prefer read-only checks first.

## Diagnostic Workflow

1. Establish scope.
   - Confirm current `cwd`.
   - Identify `CODEX_AGENT_BUS_HOME` or default to `~/.codex/agent-bus`.
   - Check whether `~/.codex/tools/codex-agent-bus/bin/agent-bus` exists.

2. Run preflight when registration setup is suspect:

```bash
python3 ~/.codex/skills/agent-bus-register/scripts/register_self.py --preflight
```

3. Check Bus health and registry:

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus health
~/.codex/tools/codex-agent-bus/bin/agent-bus list
```

4. Check the relevant inbox when a target is known:

```bash
~/.codex/tools/codex-agent-bus/bin/agent-bus inbox --target <session_id_or_alias> --unread-only --limit 10
```

5. Inspect only recent relevant message metadata when a send or ACK is missing:

```bash
tail -n 20 ~/.codex/agent-bus/messages.jsonl
```

Filter the result mentally or with safe text tools to the relevant `message_id`, `correlation_id`, `from_agent`, `to_session_id`, `target_query`, `pending_target`, `status`, and timestamps.

## Common Findings

- CLI missing: global Agent Bus install is incomplete. Show the install command if the tool or preflight suggests one, but do not run it automatically.
- No current session record: rerun `$agent-bus-register` with a real `/status` session id or open a fresh Codex session after enabling hooks.
- Pending target not claimed: ensure the later session registers with the intended role alias, tag, or compatible cwd.
- Message queued but not visible: Bus storage worked, but Codex-side visible delivery is unconfirmed.
- `codex_app` missing or returned only a transport payload: call the available Codex App thread tool with the returned thread id and prompt, then require ACK/reply for proof.
- `resume` or `codex_app` hung: stop parallel retries, preserve the canonical `message_id`, and route recovery through `$agent-bus-delegate`.
- Ambiguous agent name: resolve by `session_id`; treat `agent_id` as a role hint only.

## Recovery Guidance

- For registration fixes, route to `$agent-bus-register`.
- For resend, ACK, or reply, route to `$agent-bus-delegate`.
- For role/team state, route to `$agent-bus-team`.
- If the user says they cannot see a delegated task, treat it as a real visible-delivery failure until a target ACK or visible send result proves otherwise.

Use precise wording:

```text
Bus storage is healthy, visible thread delivery failed or is unconfirmed.
```
