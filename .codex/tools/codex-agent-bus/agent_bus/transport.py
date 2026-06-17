"""Transport implementations for waking Codex sessions."""

from __future__ import annotations

import dataclasses
import contextlib
import json
import os
import select
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


@dataclasses.dataclass
class TransportResult:
    ok: bool
    status: str
    command: List[str]
    cwd: str
    surface: str
    returncode: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    error: Optional[str] = None
    fallback_from: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        return dataclasses.asdict(self)


class CodexAppServerTransport:
    """Deliver user input through the official Codex app-server protocol."""

    def __init__(self, codex_cmd: Optional[str] = None, auto_start_daemon: bool = True) -> None:
        self.codex_cmd = codex_cmd or os.environ.get("CODEX_AGENT_BUS_CODEX", "codex")
        self.auto_start_daemon = auto_start_daemon

    def send(
        self,
        session_id: str,
        cwd: str,
        prompt: str,
        timeout_sec: Optional[float] = None,
    ) -> TransportResult:
        if not session_id:
            return TransportResult(False, "failed", [], cwd, "app_server", error="session_id is required")
        target_cwd = str(Path(cwd).expanduser())
        if not Path(target_cwd).exists():
            return TransportResult(False, "failed", [], target_cwd, "app_server", error="target cwd does not exist")
        timeout = min(timeout_sec or 60, 120)
        command = [self.codex_cmd, "app-server", "--stdio"]
        first = self._send_via_proxy(command, session_id, target_cwd, prompt, timeout)
        if first.ok or not self.auto_start_daemon:
            return first
        start = self._start_daemon(timeout=15)
        if not start.ok:
            start.fallback_from = first.error or first.stderr or first.status
            return start
        second = self._send_via_proxy(command, session_id, target_cwd, prompt, timeout)
        if not second.ok:
            second.fallback_from = first.error or first.stderr or first.status
        return second

    def _send_via_proxy(
        self,
        command: List[str],
        session_id: str,
        cwd: str,
        prompt: str,
        timeout: float,
    ) -> TransportResult:
        messages = self._build_messages(session_id, cwd, prompt)
        started = time.monotonic()
        try:
            proc = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd,
                env=self._safe_env(),
            )
        except FileNotFoundError as exc:
            return TransportResult(
                False,
                "failed",
                command,
                cwd,
                "app_server_stdio",
                error="codex command not found: %s" % exc,
            )
        assert proc.stdin is not None
        assert proc.stdout is not None
        try:
            for message in messages:
                proc.stdin.write(json.dumps(message, ensure_ascii=False, separators=(",", ":")) + "\n")
            proc.stdin.flush()
            responses: List[Dict[str, Any]] = []
            while time.monotonic() - started < timeout:
                ready, _, _ = select.select([proc.stdout], [], [], 0.1)
                if not ready:
                    if proc.poll() is not None:
                        break
                    continue
                line = proc.stdout.readline()
                if not line:
                    if proc.poll() is not None:
                        break
                    time.sleep(0.05)
                    continue
                try:
                    response = json.loads(line)
                except json.JSONDecodeError:
                    continue
                responses.append(response)
                if response.get("id") == 2:
                    if "error" in response:
                        self._terminate(proc)
                        stderr = self._read_stderr_tail(proc)
                        return TransportResult(
                            False,
                            "failed",
                            command,
                            cwd,
                            "app_server_stdio",
                            returncode=proc.returncode,
                            stdout=self._tail("\n".join(json.dumps(item, ensure_ascii=False) for item in responses)),
                            stderr=stderr,
                            error=str(response.get("error")),
                        )
                    self._terminate(proc)
                    return TransportResult(
                        True,
                        "delivered",
                        command,
                        cwd,
                        "app_server_stdio_turn_start",
                        returncode=proc.returncode,
                        stdout=self._tail("\n".join(json.dumps(item, ensure_ascii=False) for item in responses)),
                        stderr=self._read_stderr_tail(proc),
                    )
            self._terminate(proc)
            stderr = self._read_stderr_tail(proc)
            return TransportResult(
                False,
                "failed",
                command,
                cwd,
                "app_server_stdio",
                returncode=proc.returncode,
                stderr=stderr,
                error=stderr or "app-server --stdio did not acknowledge turn/start",
            )
        except BrokenPipeError as exc:
            self._terminate(proc)
            stderr = self._read_stderr_tail(proc)
            return TransportResult(
                False,
                "failed",
                command,
                cwd,
                "app_server_stdio",
                returncode=proc.returncode,
                stderr=stderr,
                error="app-server --stdio pipe closed: %s" % exc,
            )

    def _build_messages(self, session_id: str, cwd: str, prompt: str) -> List[Dict[str, Any]]:
        return [
            {
                "method": "initialize",
                "id": 0,
                "params": {
                    "clientInfo": {
                        "name": "codex_agent_bus",
                        "title": "Codex Agent Bus",
                        "version": "0.1.0",
                    },
                    "capabilities": {
                        "experimentalApi": True,
                        "requestAttestation": False,
                    },
                },
            },
            {"method": "initialized", "params": {}},
            {
                "method": "thread/resume",
                "id": 1,
                "params": {
                    "threadId": session_id,
                    "cwd": cwd,
                    "runtimeWorkspaceRoots": [cwd],
                    "excludeTurns": True,
                },
            },
            {
                "method": "turn/start",
                "id": 2,
                "params": {
                    "threadId": session_id,
                    "cwd": cwd,
                    "runtimeWorkspaceRoots": [cwd],
                    "input": [{"type": "text", "text": prompt, "text_elements": []}],
                    "responsesapiClientMetadata": {
                        "source": "codex_agent_bus",
                        "target_session_id": session_id,
                    },
                },
            },
        ]

    def _start_daemon(self, timeout: float) -> TransportResult:
        command = [self.codex_cmd, "app-server", "daemon", "start"]
        try:
            completed = subprocess.run(
                command,
                text=True,
                capture_output=True,
                timeout=timeout,
                shell=False,
                env=self._safe_env(),
            )
        except FileNotFoundError as exc:
            return TransportResult(False, "failed", command, os.getcwd(), "app_server_daemon", error=str(exc))
        except subprocess.TimeoutExpired as exc:
            return TransportResult(
                False,
                "failed",
                command,
                os.getcwd(),
                "app_server_daemon",
                stdout=(exc.stdout or "") if isinstance(exc.stdout, str) else "",
                stderr=(exc.stderr or "") if isinstance(exc.stderr, str) else "",
                error="codex app-server daemon start timed out",
            )
        return TransportResult(
            ok=completed.returncode == 0,
            status="started" if completed.returncode == 0 else "failed",
            command=command,
            cwd=os.getcwd(),
            surface="app_server_daemon",
            returncode=completed.returncode,
            stdout=self._tail(completed.stdout),
            stderr=self._tail(completed.stderr),
            error=None if completed.returncode == 0 else self._tail(completed.stderr or completed.stdout),
        )

    def _read_stderr_tail(self, proc: subprocess.Popen[str]) -> str:
        if proc.stderr is None:
            return ""
        try:
            return self._tail(proc.stderr.read() or "")
        except Exception:
            return ""
        finally:
            with contextlib.suppress(Exception):
                proc.stderr.close()

    def _terminate(self, proc: subprocess.Popen[str]) -> None:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
        for stream in (proc.stdin, proc.stdout):
            if stream is not None:
                with contextlib.suppress(Exception):
                    stream.close()

    def _safe_env(self) -> Dict[str, str]:
        return os.environ.copy()

    def _tail(self, value: str, limit: int = 4000) -> str:
        if not value:
            return ""
        return value[-limit:]


class CodexThreadStartTransport:
    """Experimentally create a Codex app-server thread and return its thread id."""

    def __init__(self, codex_cmd: Optional[str] = None, auto_start_daemon: bool = True) -> None:
        self.codex_cmd = codex_cmd or os.environ.get("CODEX_AGENT_BUS_CODEX", "codex")
        self.auto_start_daemon = auto_start_daemon

    def start_thread(
        self,
        cwd: str,
        timeout_sec: Optional[float] = None,
    ) -> Dict[str, Any]:
        target_cwd = str(Path(cwd).expanduser())
        if not Path(target_cwd).exists():
            return {
                "ok": False,
                "status": "failed",
                "surface": "app_server_stdio_thread_start",
                "cwd": target_cwd,
                "error": "target cwd does not exist",
            }
        timeout = min(timeout_sec or 60, 120)
        command = [self.codex_cmd, "app-server", "--stdio"]
        first = self._start_via_proxy(command, target_cwd, timeout)
        if first.get("ok") or not self.auto_start_daemon:
            return first
        start = self._start_daemon(timeout=15)
        if not start.get("ok"):
            start["fallback_from"] = first.get("error") or first.get("stderr") or first.get("status")
            return start
        second = self._start_via_proxy(command, target_cwd, timeout)
        if not second.get("ok"):
            second["fallback_from"] = first.get("error") or first.get("stderr") or first.get("status")
        return second

    def _start_via_proxy(self, command: List[str], cwd: str, timeout: float) -> Dict[str, Any]:
        messages = self._build_messages(cwd)
        started = time.monotonic()
        try:
            proc = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd,
                env=self._safe_env(),
            )
        except FileNotFoundError as exc:
            return {
                "ok": False,
                "status": "failed",
                "command": command,
                "cwd": cwd,
                "surface": "app_server_stdio_thread_start",
                "error": "codex command not found: %s" % exc,
            }
        assert proc.stdin is not None
        assert proc.stdout is not None
        try:
            for message in messages:
                proc.stdin.write(json.dumps(message, ensure_ascii=False, separators=(",", ":")) + "\n")
            proc.stdin.flush()
            responses: List[Dict[str, Any]] = []
            while time.monotonic() - started < timeout:
                ready, _, _ = select.select([proc.stdout], [], [], 0.1)
                if not ready:
                    if proc.poll() is not None:
                        break
                    continue
                line = proc.stdout.readline()
                if not line:
                    if proc.poll() is not None:
                        break
                    time.sleep(0.05)
                    continue
                try:
                    response = json.loads(line)
                except json.JSONDecodeError:
                    continue
                responses.append(response)
                if response.get("id") != 1:
                    continue
                if "error" in response:
                    self._terminate(proc)
                    return {
                        "ok": False,
                        "status": "failed",
                        "command": command,
                        "cwd": cwd,
                        "surface": "app_server_stdio_thread_start",
                        "returncode": proc.returncode,
                        "stdout": self._tail(
                            "\n".join(json.dumps(item, ensure_ascii=False) for item in responses)
                        ),
                        "stderr": self._read_stderr_tail(proc),
                        "error": str(response.get("error")),
                    }
                result = response.get("result") or {}
                thread = result.get("thread") or {}
                thread_id = thread.get("id")
                self._terminate(proc)
                return {
                    "ok": bool(thread_id),
                    "status": "thread_created" if thread_id else "failed",
                    "command": command,
                    "cwd": cwd,
                    "surface": "app_server_stdio_thread_start",
                    "thread_id": thread_id,
                    "thread": thread,
                    "returncode": proc.returncode,
                    "stdout": self._tail(
                        "\n".join(json.dumps(item, ensure_ascii=False) for item in responses)
                    ),
                    "stderr": self._read_stderr_tail(proc),
                    "error": None if thread_id else "thread/start response did not include thread.id",
                }
            self._terminate(proc)
            return {
                "ok": False,
                "status": "failed",
                "command": command,
                "cwd": cwd,
                "surface": "app_server_stdio_thread_start",
                "returncode": proc.returncode,
                "stderr": self._read_stderr_tail(proc),
                "error": "app-server --stdio did not acknowledge thread/start",
            }
        except BrokenPipeError as exc:
            self._terminate(proc)
            return {
                "ok": False,
                "status": "failed",
                "command": command,
                "cwd": cwd,
                "surface": "app_server_stdio_thread_start",
                "returncode": proc.returncode,
                "stderr": self._read_stderr_tail(proc),
                "error": "app-server --stdio pipe closed: %s" % exc,
            }

    def _build_messages(self, cwd: str) -> List[Dict[str, Any]]:
        return [
            {
                "method": "initialize",
                "id": 0,
                "params": {
                    "clientInfo": {
                        "name": "codex_agent_bus",
                        "title": "Codex Agent Bus",
                        "version": "0.1.0",
                    },
                    "capabilities": {
                        "experimentalApi": True,
                        "requestAttestation": False,
                    },
                },
            },
            {"method": "initialized", "params": {}},
            {
                "method": "thread/start",
                "id": 1,
                "params": {
                    "cwd": cwd,
                    "serviceName": "codex_agent_bus",
                    "threadSource": "subagent",
                    "sessionStartSource": "startup",
                    "ephemeral": False,
                },
            },
        ]

    def _start_daemon(self, timeout: float) -> Dict[str, Any]:
        command = [self.codex_cmd, "app-server", "daemon", "start"]
        try:
            completed = subprocess.run(
                command,
                text=True,
                capture_output=True,
                timeout=timeout,
                shell=False,
                env=self._safe_env(),
            )
        except FileNotFoundError as exc:
            return {
                "ok": False,
                "status": "failed",
                "command": command,
                "cwd": os.getcwd(),
                "surface": "app_server_daemon",
                "error": str(exc),
            }
        except subprocess.TimeoutExpired as exc:
            return {
                "ok": False,
                "status": "failed",
                "command": command,
                "cwd": os.getcwd(),
                "surface": "app_server_daemon",
                "stdout": (exc.stdout or "") if isinstance(exc.stdout, str) else "",
                "stderr": (exc.stderr or "") if isinstance(exc.stderr, str) else "",
                "error": "codex app-server daemon start timed out",
            }
        return {
            "ok": completed.returncode == 0,
            "status": "started" if completed.returncode == 0 else "failed",
            "command": command,
            "cwd": os.getcwd(),
            "surface": "app_server_daemon",
            "returncode": completed.returncode,
            "stdout": self._tail(completed.stdout),
            "stderr": self._tail(completed.stderr),
            "error": None if completed.returncode == 0 else self._tail(completed.stderr or completed.stdout),
        }

    def _read_stderr_tail(self, proc: subprocess.Popen[str]) -> str:
        if proc.stderr is None:
            return ""
        try:
            return self._tail(proc.stderr.read() or "")
        except Exception:
            return ""
        finally:
            with contextlib.suppress(Exception):
                proc.stderr.close()

    def _terminate(self, proc: subprocess.Popen[str]) -> None:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
        for stream in (proc.stdin, proc.stdout):
            if stream is not None:
                with contextlib.suppress(Exception):
                    stream.close()

    def _safe_env(self) -> Dict[str, str]:
        return os.environ.copy()

    def _tail(self, value: str, limit: int = 4000) -> str:
        if not value:
            return ""
        return value[-limit:]


class CodexExecResumeTransport:
    """Resume a Codex session through non-interactive codex exec."""

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
            return TransportResult(False, "failed", [], cwd, "exec_resume", error="session_id is required")
        target_cwd = str(Path(cwd).expanduser())
        if not Path(target_cwd).exists():
            return TransportResult(False, "failed", [], target_cwd, "exec_resume", error="target cwd does not exist")
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
                    "exec_resume",
                    error="codex command not found: %s" % exc,
                )
            except subprocess.TimeoutExpired as exc:
                return TransportResult(
                    False,
                    "queued",
                    command,
                    target_cwd,
                    "exec_resume",
                    error="codex resume timed out after %ss" % timeout,
                    stdout=(exc.stdout or "") if isinstance(exc.stdout, str) else "",
                    stderr=(exc.stderr or "") if isinstance(exc.stderr, str) else "",
                )
            result = TransportResult(
                ok=completed.returncode == 0,
                status="delivered" if completed.returncode == 0 else self._status_from_error(completed.stderr),
                command=command,
                cwd=target_cwd,
                surface="exec_resume_noninteractive",
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
        return last_result or TransportResult(
            False,
            "failed",
            [],
            target_cwd,
            "exec_resume",
            error="no command candidates",
        )

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


class CodexResumeTransport:
    """Deliver a prompt to a Codex session using official Codex transports."""

    def __init__(self, codex_cmd: Optional[str] = None) -> None:
        self.codex_cmd = codex_cmd or os.environ.get("CODEX_AGENT_BUS_CODEX", "codex")
        self.app_server = CodexAppServerTransport(self.codex_cmd)
        self.exec_resume = CodexExecResumeTransport(self.codex_cmd)

    def send(
        self,
        session_id: str,
        cwd: str,
        prompt: str,
        timeout_sec: Optional[float] = None,
    ) -> TransportResult:
        mode = os.environ.get("CODEX_AGENT_BUS_TRANSPORT", "auto").strip().lower()
        if mode in ("exec", "exec_resume", "codex_exec"):
            return self.exec_resume.send(session_id, cwd, prompt, timeout_sec)
        app_result = self.app_server.send(session_id, cwd, prompt, timeout_sec)
        if app_result.ok or mode in ("app", "app_server", "app-server"):
            return app_result
        exec_result = self.exec_resume.send(session_id, cwd, prompt, timeout_sec)
        exec_result.fallback_from = app_result.error or app_result.stderr or app_result.status
        return exec_result
