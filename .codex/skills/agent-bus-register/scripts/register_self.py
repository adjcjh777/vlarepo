#!/usr/bin/env python3
"""Register the current Codex session in the global Codex Agent Bus registry."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:
    import fcntl  # type: ignore
except ImportError:  # pragma: no cover
    fcntl = None  # type: ignore


DEFAULT_ROLE = "Registered through the agent-bus-register skill."


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def bus_home(value: Optional[str]) -> Path:
    if value:
        return Path(value).expanduser()
    if os.environ.get("CODEX_AGENT_BUS_HOME"):
        return Path(os.environ["CODEX_AGENT_BUS_HOME"]).expanduser()
    return Path.home() / ".codex" / "agent-bus"


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "agent"


def agent_id_for(name: str, session_id: str) -> str:
    digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:8]
    return "%s-%s" % (slugify(name), digest)


def load_registry(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"version": "0.1.0", "updated_at": utc_now(), "agents": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit("Invalid Agent Bus registry JSON: %s" % exc)
    agents = data.get("agents", {})
    if isinstance(agents, list):
        agents = {item["agent_id"]: item for item in agents if item.get("agent_id")}
    if not isinstance(agents, dict):
        agents = {}
    data["agents"] = agents
    return data


def write_registry(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = utc_now()
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(str(tmp), str(path))


def realpath(value: str) -> str:
    return os.path.realpath(str(Path(value).expanduser()))


def choose_current_record(agents: Iterable[Dict[str, Any]], cwd: str) -> Optional[Dict[str, Any]]:
    matches = [item for item in agents if realpath(str(item.get("cwd", ""))) == realpath(cwd)]
    if not matches:
        return None
    unnamed = [item for item in matches if str(item.get("name", "")).startswith("unnamed-")]
    pool = unnamed or matches
    return sorted(pool, key=lambda item: item.get("last_seen", ""), reverse=True)[0]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Register this Codex session with Agent Bus.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--role", default=DEFAULT_ROLE)
    parser.add_argument("--session-id", default=os.environ.get("CODEX_SESSION_ID"))
    parser.add_argument("--cwd", default=os.getcwd())
    parser.add_argument("--status", default="idle")
    parser.add_argument("--capability", action="append", default=[])
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--bus-home")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    home = bus_home(args.bus_home)
    registry_path = home / "registry.json"
    lock_dir = home / "locks"
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_path = lock_dir / "registry.lock"
    with lock_path.open("a+", encoding="utf-8") as lock:
        if fcntl is not None:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        registry = load_registry(registry_path)
        agents = registry["agents"]
        current = None
        session_id = args.session_id
        if session_id:
            current = next((item for item in agents.values() if item.get("session_id") == session_id), None)
        else:
            current = choose_current_record(agents.values(), args.cwd)
            session_id = current.get("session_id") if current else None
        if not session_id:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "error": "No current Agent Bus session record found for cwd.",
                        "cwd": str(Path(args.cwd).expanduser()),
                        "registry": str(registry_path),
                        "next_steps": [
                            "Install/enable Codex Agent Bus and open a fresh Codex session.",
                            "Or rerun with --session-id from Codex /status.",
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
            )
            return 2
        old_id = current.get("agent_id") if current else None
        new_id = old_id or agent_id_for(args.name, session_id)
        record = dict(current or {})
        record.update(
            {
                "agent_id": new_id,
                "name": args.name,
                "role": args.role,
                "session_id": session_id,
                "cwd": str(Path(args.cwd).expanduser()),
                "status": args.status,
                "last_seen": utc_now(),
                "created_at": record.get("created_at") or utc_now(),
                "capabilities": args.capability,
                "tags": args.tag,
                "metadata": record.get("metadata") or {},
                "enabled": record.get("enabled", True),
            }
        )
        if old_id and old_id != new_id:
            agents.pop(old_id, None)
        agents[new_id] = record
        write_registry(registry_path, registry)
        if fcntl is not None:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    print(json.dumps({"ok": True, "agent": record, "registry": str(registry_path)}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
