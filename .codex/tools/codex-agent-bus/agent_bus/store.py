"""Persistent global registry and message store for Codex Agent Bus."""

from __future__ import annotations

import contextlib
import json
import os
import shutil
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

from . import __version__

try:
    import fcntl  # type: ignore
except ImportError:  # pragma: no cover
    fcntl = None  # type: ignore


MAX_HOP_COUNT = 6
STALE_AFTER_SECONDS = 24 * 60 * 60
VALID_STATUSES = {
    "idle",
    "running",
    "needs_input",
    "done",
    "error",
    "unknown",
}


class AgentBusError(Exception):
    """Base error for Agent Bus operations."""


class NotFoundError(AgentBusError):
    """Raised when a target cannot be found."""


class AmbiguousTargetError(AgentBusError):
    """Raised when a target matches more than one agent."""

    def __init__(self, target: str, candidates: List[Dict[str, Any]]) -> None:
        super().__init__("Target %r matched multiple agents" % target)
        self.target = target
        self.candidates = candidates


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_time(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def default_bus_home() -> Path:
    override = os.environ.get("CODEX_AGENT_BUS_HOME")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".codex" / "agent-bus"


def as_list(value: Optional[Iterable[Any]]) -> List[str]:
    if not value:
        return []
    if isinstance(value, str):
        return [value] if value else []
    return [str(item) for item in value if str(item)]


def make_agent_id(name: str, session_id: str) -> str:
    del name
    return session_id


def safe_json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class AgentStore:
    def __init__(self, home: Optional[Path] = None) -> None:
        self.home = Path(home).expanduser() if home else default_bus_home()
        self.registry_path = self.home / "registry.json"
        self.messages_path = self.home / "messages.jsonl"
        self.locks_dir = self.home / "locks"
        self.logs_dir = self.home / "logs"
        self.log_path = self.logs_dir / "agent-bus.log"
        self.ensure_layout()

    def ensure_layout(self) -> None:
        self.home.mkdir(parents=True, exist_ok=True)
        self.locks_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        if not self.registry_path.exists():
            self._write_json_atomic(
                self.registry_path,
                {"version": __version__, "updated_at": utc_now(), "agents": {}},
            )
        if not self.messages_path.exists():
            self.messages_path.touch()

    def log_error(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        entry = {"created_at": utc_now(), "level": "error", "message": message}
        if data:
            entry["data"] = data
        try:
            self.logs_dir.mkdir(parents=True, exist_ok=True)
            with self.log_path.open("a", encoding="utf-8") as handle:
                handle.write(safe_json_dumps(entry) + "\n")
        except OSError:
            pass

    @contextlib.contextmanager
    def _locked(self, name: str) -> Iterator[None]:
        self.ensure_layout()
        lock_path = self.locks_dir / ("%s.lock" % name)
        with lock_path.open("a+", encoding="utf-8") as handle:
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                if fcntl is not None:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def _read_json(self, path: Path, default: Any) -> Any:
        try:
            with path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except FileNotFoundError:
            return default
        except json.JSONDecodeError as exc:
            self.log_error("Invalid JSON file", {"path": str(path), "error": str(exc)})
            return default

    def _write_json_atomic(self, path: Path, value: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(str(tmp), str(path))

    def _read_registry_unlocked(self) -> Dict[str, Any]:
        registry = self._read_json(
            self.registry_path,
            {"version": __version__, "updated_at": utc_now(), "agents": {}},
        )
        agents = registry.get("agents", {})
        if isinstance(agents, list):
            agents = {str(agent.get("agent_id")): agent for agent in agents if agent.get("agent_id")}
        if not isinstance(agents, dict):
            agents = {}
        agents = self._normalize_agents(agents)
        registry["agents"] = agents
        registry.setdefault("version", __version__)
        registry.setdefault("updated_at", utc_now())
        return registry

    def _normalize_agents(self, agents: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        normalized: Dict[str, Dict[str, Any]] = {}
        for key, value in agents.items():
            if not isinstance(value, dict):
                continue
            record = dict(value)
            session_id = str(record.get("session_id") or "")
            if not session_id:
                agent_id = str(record.get("agent_id") or key)
                record["agent_id"] = agent_id
                normalized[agent_id] = record
                continue
            canonical_id = session_id
            legacy_ids = set(as_list(record.get("legacy_agent_ids")))
            for candidate in [str(key), str(record.get("agent_id") or "")]:
                if candidate and candidate != canonical_id:
                    legacy_ids.add(candidate)
            record["agent_id"] = canonical_id
            if legacy_ids:
                record["legacy_agent_ids"] = sorted(legacy_ids)
            existing = normalized.get(canonical_id)
            if existing and str(existing.get("last_seen", "")) > str(record.get("last_seen", "")):
                existing_legacy = set(as_list(existing.get("legacy_agent_ids")))
                existing_legacy.update(legacy_ids)
                if existing_legacy:
                    existing["legacy_agent_ids"] = sorted(existing_legacy)
                normalized[canonical_id] = existing
            else:
                if existing:
                    legacy_ids.update(as_list(existing.get("legacy_agent_ids")))
                    if legacy_ids:
                        record["legacy_agent_ids"] = sorted(legacy_ids)
                normalized[canonical_id] = record
        return normalized

    def _write_registry_unlocked(self, registry: Dict[str, Any]) -> None:
        registry["updated_at"] = utc_now()
        self._write_json_atomic(self.registry_path, registry)

    def list_agents(
        self,
        include_disabled: bool = False,
        cwd_prefix: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        with self._locked("registry"):
            agents = list(self._read_registry_unlocked()["agents"].values())
        if not include_disabled:
            agents = [agent for agent in agents if agent.get("enabled", True)]
        if cwd_prefix:
            prefix = str(Path(cwd_prefix).expanduser())
            agents = [agent for agent in agents if str(agent.get("cwd", "")).startswith(prefix)]
        if tag:
            agents = [agent for agent in agents if tag in agent.get("tags", [])]
        now = datetime.now(timezone.utc)
        for agent in agents:
            last_seen = parse_time(agent.get("last_seen"))
            agent["stale"] = True if not last_seen else (now - last_seen).total_seconds() > STALE_AFTER_SECONDS
        return sorted(agents, key=lambda item: item.get("last_seen", ""), reverse=True)

    def resolve_agent(self, target: str, include_disabled: bool = False) -> Dict[str, Any]:
        return self._resolve_agent_from_list(target, self.list_agents(include_disabled=include_disabled))

    def _resolve_agent_from_list(self, target: str, agents: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not target:
            raise NotFoundError("Target is required")
        exact = [agent for agent in agents if agent.get("agent_id") == target]
        if exact:
            return exact[0]
        by_legacy = [agent for agent in agents if target in agent.get("legacy_agent_ids", [])]
        if len(by_legacy) == 1:
            return by_legacy[0]
        if len(by_legacy) > 1:
            raise AmbiguousTargetError(target, by_legacy)
        by_session = [agent for agent in agents if agent.get("session_id") == target]
        if len(by_session) == 1:
            return by_session[0]
        if len(by_session) > 1:
            raise AmbiguousTargetError(target, by_session)
        by_name = [agent for agent in agents if agent.get("name") == target]
        if len(by_name) == 1:
            return by_name[0]
        if len(by_name) > 1:
            raise AmbiguousTargetError(target, by_name)
        raise NotFoundError("No agent found for target %r" % target)

    def upsert_agent(
        self,
        name: str,
        role: str,
        session_id: str,
        cwd: Optional[str] = None,
        transcript_path: Optional[str] = None,
        model: Optional[str] = None,
        status: Optional[str] = None,
        capabilities: Optional[Iterable[Any]] = None,
        tags: Optional[Iterable[Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        enabled: Optional[bool] = None,
        agent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not session_id:
            raise AgentBusError(
                "session_id is required. Use Codex /status or SessionStart hook auto-registration."
            )
        now = utc_now()
        status = status or "unknown"
        if status not in VALID_STATUSES:
            raise AgentBusError("Invalid status %r" % status)
        with self._locked("registry"):
            registry = self._read_registry_unlocked()
            agents = registry["agents"]
            existing_id = session_id
            existing = agents.get(existing_id, {})
            legacy_ids = set(as_list(existing.get("legacy_agent_ids")))
            if agent_id and agent_id != session_id:
                legacy_ids.add(agent_id)
            record = dict(existing)
            record.update(
                {
                    "agent_id": existing_id,
                    "name": name or existing.get("name") or ("unnamed-%s" % session_id[:8]),
                    "role": role or existing.get("role") or "",
                    "session_id": session_id,
                    "cwd": str(Path(cwd).expanduser()) if cwd else existing.get("cwd") or os.getcwd(),
                    "transcript_path": transcript_path
                    if transcript_path is not None
                    else existing.get("transcript_path"),
                    "model": model if model is not None else existing.get("model"),
                    "status": status,
                    "created_at": existing.get("created_at") or now,
                    "last_seen": now,
                    "capabilities": as_list(capabilities)
                    if capabilities is not None
                    else existing.get("capabilities", []),
                    "tags": as_list(tags) if tags is not None else existing.get("tags", []),
                    "metadata": metadata if metadata is not None else existing.get("metadata", {}),
                    "enabled": bool(enabled) if enabled is not None else existing.get("enabled", True),
                }
            )
            if legacy_ids:
                record["legacy_agent_ids"] = sorted(legacy_ids)
            agents[existing_id] = record
            self._write_registry_unlocked(registry)
            return dict(record)

    def update_agent(self, target: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        allowed = {"name", "role", "status", "capabilities", "tags", "metadata", "enabled"}
        filtered = {key: value for key, value in updates.items() if key in allowed and value is not None}
        if "status" in filtered and filtered["status"] not in VALID_STATUSES:
            raise AgentBusError("Invalid status %r" % filtered["status"])
        with self._locked("registry"):
            registry = self._read_registry_unlocked()
            agent = self._resolve_agent_from_list(target, list(registry["agents"].values()))
            record = dict(registry["agents"][agent["agent_id"]])
            if "capabilities" in filtered:
                filtered["capabilities"] = as_list(filtered["capabilities"])
            if "tags" in filtered:
                filtered["tags"] = as_list(filtered["tags"])
            record.update(filtered)
            record["last_seen"] = utc_now()
            registry["agents"][record["agent_id"]] = record
            self._write_registry_unlocked(registry)
            return dict(record)

    def update_status(self, target: str, status: str, note: Optional[str] = None) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {}
        try:
            current = self.resolve_agent(target, include_disabled=True)
            metadata = dict(current.get("metadata", {}))
        except AgentBusError:
            metadata = {}
        if note:
            metadata["status_note"] = note
        return self.update_agent(target, {"status": status, "metadata": metadata})

    def append_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        record = dict(message)
        if not record.get("message_id"):
            record["message_id"] = str(uuid.uuid4())
        if not record.get("correlation_id"):
            record["correlation_id"] = str(uuid.uuid4())
        if not record.get("created_at"):
            record["created_at"] = utc_now()
        if not record.get("status"):
            record["status"] = "queued"
        if record.get("hop_count") is None:
            record["hop_count"] = 0
        with self._locked("messages"):
            with self.messages_path.open("a", encoding="utf-8") as handle:
                handle.write(safe_json_dumps(record) + "\n")
        return record

    def _message_matches_agent(self, message: Dict[str, Any], agent: Dict[str, Any]) -> bool:
        if message.get("to_agent_id") and message.get("to_agent_id") == agent.get("agent_id"):
            return True
        if message.get("to_session_id") and message.get("to_session_id") == agent.get("session_id"):
            return True
        identity_values = {
            str(value)
            for value in [
                agent.get("agent_id"),
                agent.get("session_id"),
                agent.get("name"),
            ]
            if value
        }
        identity_values.update(as_list(agent.get("legacy_agent_ids")))
        for key in ("target_query", "to_name"):
            value = str(message.get(key) or "")
            if value and value in identity_values:
                return True
        target_tags = as_list(message.get("target_tags"))
        if target_tags:
            agent_tags = set(as_list(agent.get("tags")))
            if not set(target_tags).issubset(agent_tags):
                return False
        cwd_prefix = message.get("target_cwd_prefix")
        if cwd_prefix:
            try:
                agent_cwd = str(Path(str(agent.get("cwd") or "")).expanduser())
                prefix = str(Path(str(cwd_prefix)).expanduser())
            except TypeError:
                return False
            if not agent_cwd.startswith(prefix):
                return False
        return bool(message.get("pending_target") and (target_tags or cwd_prefix))

    def claim_pending_messages(self, agent: Dict[str, Any]) -> List[Dict[str, Any]]:
        claimed: List[Dict[str, Any]] = []
        with self._locked("messages"):
            messages = self._read_messages_unlocked()
            changed = False
            for index, message in enumerate(messages):
                if message.get("to_agent_id") or message.get("to_session_id"):
                    continue
                if not message.get("pending_target"):
                    continue
                if not self._message_matches_agent(message, agent):
                    continue
                updated = dict(message)
                updated.update(
                    {
                        "to_agent_id": agent.get("agent_id"),
                        "to_session_id": agent.get("session_id"),
                        "to_name": agent.get("name") or message.get("to_name"),
                        "pending_target": False,
                        "claimed_at": utc_now(),
                        "claimed_by_agent_id": agent.get("agent_id"),
                        "claimed_by_session_id": agent.get("session_id"),
                    }
                )
                if updated.get("status") == "pending_target":
                    updated["status"] = "queued"
                messages[index] = updated
                claimed.append(updated)
                changed = True
            if changed:
                self._write_messages_unlocked(messages)
        return claimed

    def read_messages(self) -> List[Dict[str, Any]]:
        with self._locked("messages"):
            return self._read_messages_unlocked()

    def _read_messages_unlocked(self) -> List[Dict[str, Any]]:
        messages: List[Dict[str, Any]] = []
        if not self.messages_path.exists():
            return messages
        with self.messages_path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError as exc:
                    self.log_error(
                        "Invalid message JSONL row",
                        {"line": line_number, "error": str(exc)},
                    )
                    continue
                if isinstance(value, dict):
                    messages.append(value)
        return messages

    def _write_messages_unlocked(self, messages: List[Dict[str, Any]]) -> None:
        tmp = self.messages_path.with_suffix(".jsonl.tmp")
        with tmp.open("w", encoding="utf-8") as handle:
            for message in messages:
                handle.write(safe_json_dumps(message) + "\n")
        os.replace(str(tmp), str(self.messages_path))

    def update_message(self, message_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        with self._locked("messages"):
            messages = self._read_messages_unlocked()
            for index, message in enumerate(messages):
                if message.get("message_id") == message_id:
                    updated = dict(message)
                    updated.update({key: value for key, value in updates.items() if value is not None})
                    messages[index] = updated
                    self._write_messages_unlocked(messages)
                    return updated
        raise NotFoundError("No message found for id %r" % message_id)

    def find_message(self, message_id: str) -> Dict[str, Any]:
        for message in self.read_messages():
            if message.get("message_id") == message_id:
                return message
        raise NotFoundError("No message found for id %r" % message_id)

    def get_inbox(
        self,
        target: Optional[str] = None,
        unread_only: bool = False,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        messages = self.read_messages()
        if target:
            agent = self.resolve_agent(target, include_disabled=True)
            messages = [
                message
                for message in messages
                if self._message_matches_agent(message, agent)
            ]
        if unread_only:
            messages = [message for message in messages if not message.get("read_at")]
        messages = sorted(messages, key=lambda item: item.get("created_at", ""), reverse=True)
        if limit:
            messages = messages[: int(limit)]
        return messages

    def mark_read(self, message_id: str) -> Dict[str, Any]:
        return self.update_message(message_id, {"read_at": utc_now()})

    def wait_for_reply(
        self,
        correlation_id: str,
        parent_message_id: Optional[str],
        timeout_sec: float,
    ) -> Optional[Dict[str, Any]]:
        deadline = time.time() + timeout_sec
        while time.time() < deadline:
            messages = self.read_messages()
            for message in reversed(messages):
                if parent_message_id and message.get("parent_message_id") == parent_message_id:
                    return message
                if (
                    message.get("correlation_id") == correlation_id
                    and message.get("message_type") == "reply"
                ):
                    return message
            time.sleep(0.5)
        return None

    def health(self) -> Dict[str, Any]:
        self.ensure_layout()
        checks = {
            "home": str(self.home),
            "registry_path": str(self.registry_path),
            "messages_path": str(self.messages_path),
            "log_path": str(self.log_path),
            "version": __version__,
            "codex_command": shutil.which("codex"),
            "registry_readable": os.access(str(self.registry_path), os.R_OK),
            "registry_writable": os.access(str(self.registry_path), os.W_OK),
            "messages_readable": os.access(str(self.messages_path), os.R_OK),
            "messages_writable": os.access(str(self.messages_path), os.W_OK),
            "recent_errors": self._recent_errors(),
        }
        checks["ok"] = all(
            [
                checks["registry_readable"],
                checks["registry_writable"],
                checks["messages_readable"],
                checks["messages_writable"],
            ]
        )
        return checks

    def _recent_errors(self, limit: int = 5) -> List[Dict[str, Any]]:
        if not self.log_path.exists():
            return []
        try:
            lines = self.log_path.read_text(encoding="utf-8").splitlines()[-limit:]
        except OSError:
            return []
        errors: List[Dict[str, Any]] = []
        for line in lines:
            try:
                errors.append(json.loads(line))
            except json.JSONDecodeError:
                errors.append({"message": line})
        return errors
