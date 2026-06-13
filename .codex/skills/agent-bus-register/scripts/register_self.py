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
DEFAULT_TOOL_ROOT = Path.home() / ".codex" / "tools" / "codex-agent-bus"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def bus_home(value: Optional[str]) -> Path:
    if value:
        return Path(value).expanduser()
    if os.environ.get("CODEX_AGENT_BUS_HOME"):
        return Path(os.environ["CODEX_AGENT_BUS_HOME"]).expanduser()
    return Path.home() / ".codex" / "agent-bus"


def possible_source_roots() -> List[Path]:
    roots: List[Path] = []
    if os.environ.get("CODEX_AGENT_BUS_SOURCE"):
        roots.append(Path(os.environ["CODEX_AGENT_BUS_SOURCE"]).expanduser())
    roots.extend(
        [
            Path.cwd() / "codex-agent-bus",
            Path.home() / "working-dir" / "codex-agent-bus",
            DEFAULT_TOOL_ROOT,
        ]
    )
    seen = set()
    unique = []
    for root in roots:
        resolved = str(root)
        if resolved not in seen:
            unique.append(root)
            seen.add(resolved)
    return unique


def find_source_installer() -> Optional[Path]:
    for root in possible_source_roots():
        installer = root / "scripts" / "install_agent_bus.py"
        if installer.exists():
            return installer
    return None


def config_mentions_agent_bus(config_path: Path) -> Optional[bool]:
    if not config_path.exists():
        return False
    try:
        return "agent_bus" in config_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def diagnostics(home: Path, registry_path: Path, cwd: str) -> Dict[str, Any]:
    cli = DEFAULT_TOOL_ROOT / "bin" / "agent-bus"
    hook = DEFAULT_TOOL_ROOT / "bin" / "agent-bus-hook"
    mcp = DEFAULT_TOOL_ROOT / "bin" / "agent-bus-mcp"
    config_path = Path.home() / ".codex" / "config.toml"
    registry = load_registry(registry_path)
    agents = list(registry.get("agents", {}).values())
    cwd_matches = [item for item in agents if item.get("cwd") and realpath(str(item.get("cwd"))) == realpath(cwd)]
    installer = find_source_installer()
    install_command = None
    if installer:
        install_command = "cd %s && python3 scripts/install_agent_bus.py --user" % installer.parents[1]
    return {
        "bus_home": str(home),
        "registry": str(registry_path),
        "registry_exists": registry_path.exists(),
        "agent_count": len(agents),
        "cwd": str(Path(cwd).expanduser()),
        "cwd_match_count": len(cwd_matches),
        "installed_cli": str(cli),
        "installed_cli_exists": cli.exists() and os.access(str(cli), os.X_OK),
        "installed_hook_exists": hook.exists() and os.access(str(hook), os.X_OK),
        "installed_mcp_exists": mcp.exists() and os.access(str(mcp), os.X_OK),
        "user_config": str(config_path),
        "user_config_mentions_agent_bus": config_mentions_agent_bus(config_path),
        "source_installer": str(installer) if installer else None,
        "install_command": install_command,
    }


def setup_warnings(diag: Dict[str, Any]) -> List[str]:
    warnings: List[str] = []
    if not diag.get("installed_cli_exists"):
        warnings.append("Agent Bus CLI is missing or not executable: %s" % diag.get("installed_cli"))
    if not diag.get("installed_hook_exists"):
        warnings.append("Agent Bus hook wrapper is missing or not executable under ~/.codex/tools/codex-agent-bus/bin.")
    if not diag.get("installed_mcp_exists"):
        warnings.append("Agent Bus MCP wrapper is missing or not executable under ~/.codex/tools/codex-agent-bus/bin.")
    if not diag.get("user_config_mentions_agent_bus"):
        warnings.append("~/.codex/config.toml does not appear to contain the agent_bus user-level configuration.")
    return warnings


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
    matches = [item for item in agents if item.get("cwd") and realpath(str(item.get("cwd"))) == realpath(cwd)]
    if not matches:
        return None
    unnamed = [item for item in matches if str(item.get("name", "")).startswith("unnamed-")]
    pool = unnamed or matches
    return sorted(pool, key=lambda item: item.get("last_seen", ""), reverse=True)[0]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Register this Codex session with Agent Bus.")
    parser.add_argument("--preflight", action="store_true", help="Print Agent Bus setup diagnostics and exit.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--role", default=DEFAULT_ROLE)
    parser.add_argument("--session-id", default=os.environ.get("CODEX_SESSION_ID"))
    parser.add_argument("--cwd", default=os.getcwd())
    parser.add_argument("--status", default="idle")
    parser.add_argument("--capability", action="append", default=[])
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--bus-home")
    args = sys.argv[1:]
    if "--preflight" in args and "--name" not in args:
        args = ["--name", "preflight"] + args
    return parser.parse_args(args)


def main() -> int:
    args = parse_args()
    home = bus_home(args.bus_home)
    registry_path = home / "registry.json"
    if args.preflight:
        diag = diagnostics(home, registry_path, args.cwd)
        print(json.dumps({"ok": True, "diagnostics": diag, "warnings": setup_warnings(diag)}, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
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
            diag = diagnostics(home, registry_path, args.cwd)
            next_steps = [
                "Provide --session-id from Codex /status and rerun this script.",
            ]
            if diag.get("install_command"):
                next_steps.insert(0, "Install the global Agent Bus tool explicitly, then open a fresh Codex session: %s" % diag["install_command"])
            else:
                next_steps.insert(0, "Install/enable Codex Agent Bus globally, then open a fresh Codex session.")
            print(
                json.dumps(
                    {
                        "ok": False,
                        "error": "No current Agent Bus session record found for cwd.",
                        "cwd": str(Path(args.cwd).expanduser()),
                        "registry": str(registry_path),
                        "diagnostics": diag,
                        "warnings": setup_warnings(diag),
                        "next_steps": next_steps,
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
    diag = diagnostics(home, registry_path, args.cwd)
    print(
        json.dumps(
            {
                "ok": True,
                "agent": record,
                "registry": str(registry_path),
                "warnings": setup_warnings(diag),
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
