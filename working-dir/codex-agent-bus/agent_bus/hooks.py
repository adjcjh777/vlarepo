"""Codex hook entrypoint for automatic Agent Bus registration."""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, Optional

from .store import AgentBusError, AgentStore


DEFAULT_ROLE = "Unspecified Codex agent; update with register_agent or update_agent."


def first_value(payload: Dict[str, Any], *names: str) -> Optional[Any]:
    for name in names:
        if name in payload and payload[name] not in (None, ""):
            return payload[name]
    for value in payload.values():
        if isinstance(value, dict):
            found = first_value(value, *names)
            if found not in (None, ""):
                return found
    return None


def hook_event(payload: Dict[str, Any]) -> str:
    value = first_value(payload, "hook_event_name", "event", "hook", "type") or ""
    return str(value)


def handle_hook(payload: Dict[str, Any], store: Optional[AgentStore] = None) -> Dict[str, Any]:
    store = store or AgentStore()
    event = hook_event(payload)
    session_id = first_value(payload, "session_id", "sessionId", "conversation_id", "thread_id")
    cwd = first_value(payload, "cwd", "working_dir", "workingDirectory") or os.environ.get("PWD") or os.getcwd()
    transcript_path = first_value(payload, "transcript_path", "transcriptPath")
    model = first_value(payload, "model")
    if session_id:
        short = str(session_id)[:8]
        if "stop" in event.lower():
            try:
                store.update_status(str(session_id), "idle")
            except AgentBusError:
                store.upsert_agent(
                    name="unnamed-%s" % short,
                    role=DEFAULT_ROLE,
                    session_id=str(session_id),
                    cwd=str(cwd),
                    transcript_path=str(transcript_path) if transcript_path else None,
                    model=str(model) if model else None,
                    status="idle",
                )
        else:
            existing = None
            try:
                existing = store.resolve_agent(str(session_id), include_disabled=True)
            except AgentBusError:
                existing = None
            store.upsert_agent(
                name=(existing or {}).get("name") or "unnamed-%s" % short,
                role=(existing or {}).get("role") or DEFAULT_ROLE,
                session_id=str(session_id),
                cwd=str(cwd),
                transcript_path=str(transcript_path) if transcript_path else None,
                model=str(model) if model else None,
                status=(existing or {}).get("status") or "idle",
                capabilities=(existing or {}).get("capabilities"),
                tags=(existing or {}).get("tags"),
                metadata=(existing or {}).get("metadata"),
            )
    context = (
        "Agent Bus is enabled for this Codex session. Use register_agent to set your "
        "name and role, list_agents to see peers, send_message to contact another "
        "session, and reply_message to return delegated results. Do not put secrets "
        "in Agent Bus messages."
    )
    return {
        "additionalContext": context,
        "suppressOutput": True,
    }


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {}
    store = AgentStore()
    try:
        response = handle_hook(payload, store)
    except Exception as exc:
        store.log_error("Hook failed", {"error": repr(exc)})
        response = {"additionalContext": "Agent Bus hook failed; Codex startup continues.", "suppressOutput": True}
    sys.stdout.write(json.dumps(response, ensure_ascii=False))
    sys.stdout.write("\n")
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
