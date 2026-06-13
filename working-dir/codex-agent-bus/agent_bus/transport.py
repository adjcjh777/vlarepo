"""Transport implementations for waking Codex sessions."""

from __future__ import annotations

import dataclasses
import os
import subprocess
import threading
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclasses.dataclass
class TransportResult:
    ok: bool
    status: str
    command: List[str]
    cwd: str
    returncode: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        return dataclasses.asdict(self)


class CodexResumeTransport:
    """Resume a Codex session via the public Codex CLI."""

    _capability_lock = threading.Lock()
    _capability_cache: Dict[str, object] = {}

    def __init__(self, codex_cmd: Optional[str] = None) -> None:
        self.codex_cmd = codex_cmd or os.environ.get("CODEX_AGENT_BUS_CODEX", "codex")

    def send(
        self,
        session_id: str,
        cwd: str,
        prompt: str,
        timeout_sec: Optional[float] = None,
    ) -> TransportResult:
        if not session_id:
            return TransportResult(False, "failed", [], cwd, error="session_id is required")
        target_cwd = str(Path(cwd).expanduser())
        if not Path(target_cwd).exists():
            return TransportResult(False, "failed", [], target_cwd, error="target cwd does not exist")
        timeout = timeout_sec or 600
        last_result: Optional[TransportResult] = None
        for command in self._candidate_commands(session_id, target_cwd, prompt):
            uses_stdin = command[-1] == "-"
            try:
                completed = subprocess.run(
                    command,
                    input=prompt if uses_stdin else None,
                    text=True,
                    capture_output=True,
                    cwd=target_cwd,
                    timeout=timeout,
                    shell=False,
                    env=self._safe_env(),
                )
            except FileNotFoundError as exc:
                return TransportResult(
                    False,
                    "failed",
                    command,
                    target_cwd,
                    error="codex command not found: %s" % exc,
                )
            except subprocess.TimeoutExpired as exc:
                return TransportResult(
                    False,
                    "queued",
                    command,
                    target_cwd,
                    error="codex resume timed out after %ss" % timeout,
                    stdout=(exc.stdout or "") if isinstance(exc.stdout, str) else "",
                    stderr=(exc.stderr or "") if isinstance(exc.stderr, str) else "",
                )
            result = TransportResult(
                ok=completed.returncode == 0,
                status="delivered" if completed.returncode == 0 else self._status_from_error(completed.stderr),
                command=command,
                cwd=target_cwd,
                returncode=completed.returncode,
                stdout=self._tail(completed.stdout),
                stderr=self._tail(completed.stderr),
                error=None if completed.returncode == 0 else self._tail(completed.stderr or completed.stdout),
            )
            if result.ok:
                return result
            last_result = result
            if not self._looks_like_cli_shape_error(result.stderr + "\n" + result.stdout):
                return result
        return last_result or TransportResult(False, "failed", [], target_cwd, error="no command candidates")

    def _candidate_commands(self, session_id: str, cwd: str, prompt: str) -> Iterable[List[str]]:
        style = self._detect_cd_style()
        if style == "exec-prefix-cd":
            yield [self.codex_cmd, "exec", "-C", cwd, "resume", session_id, "-"]
        yield [self.codex_cmd, "exec", "resume", session_id, "-C", cwd, "-"]
        yield [self.codex_cmd, "exec", "resume", session_id, "--cd", cwd, "-"]
        yield [self.codex_cmd, "exec", "resume", session_id, "-"]
        if style == "exec-prefix-cd":
            yield [self.codex_cmd, "exec", "-C", cwd, "resume", session_id, prompt]
        yield [self.codex_cmd, "exec", "resume", session_id, prompt]

    def _detect_cd_style(self) -> str:
        cache_key = "cd_style:%s" % self.codex_cmd
        with self._capability_lock:
            cached = self._capability_cache.get(cache_key)
            if isinstance(cached, str):
                return cached
        style = "exec-prefix-cd"
        try:
            completed = subprocess.run(
                [self.codex_cmd, "exec", "--help"],
                text=True,
                capture_output=True,
                timeout=5,
                shell=False,
                env=self._safe_env(),
            )
            help_text = (completed.stdout or "") + "\n" + (completed.stderr or "")
            if "-C, --cd <DIR>" not in help_text and "--cd <DIR>" not in help_text:
                style = "cwd-only"
        except Exception:
            style = "exec-prefix-cd"
        with self._capability_lock:
            self._capability_cache[cache_key] = style
        return style

    def _safe_env(self) -> Dict[str, str]:
        env = os.environ.copy()
        return env

    def _looks_like_cli_shape_error(self, text: str) -> bool:
        lowered = text.lower()
        markers = [
            "unexpected argument",
            "unrecognized option",
            "found argument",
            "usage:",
            "unknown option",
            "invalid value",
        ]
        return any(marker in lowered for marker in markers)

    def _status_from_error(self, stderr: str) -> str:
        lowered = (stderr or "").lower()
        if "lock" in lowered or "already running" in lowered or "busy" in lowered:
            return "queued"
        return "failed"

    def _tail(self, value: str, limit: int = 4000) -> str:
        if not value:
            return ""
        return value[-limit:]
