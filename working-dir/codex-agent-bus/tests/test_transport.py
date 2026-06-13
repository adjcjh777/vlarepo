from __future__ import annotations

import json
import os
import stat
import tempfile
import textwrap
import unittest
from pathlib import Path

from agent_bus.transport import CodexResumeTransport


class TransportTests(unittest.TestCase):
    def test_app_server_resume_starts_user_turn(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target_cwd = root / "target"
            target_cwd.mkdir()
            capture = root / "app-server.json"
            fake = root / "codex-fake.py"
            fake.write_text(
                textwrap.dedent(
                    """\
                    #!/usr/bin/env python3
                    import json, os, sys
                    if sys.argv[1:] == ["app-server", "proxy"]:
                        messages = []
                        for _ in range(4):
                            messages.append(json.loads(sys.stdin.readline()))
                        with open(os.environ["CAPTURE_PATH"], "w", encoding="utf-8") as handle:
                            json.dump(messages, handle)
                        print(json.dumps({"id": 0, "result": {"userAgent": "fake"}}), flush=True)
                        print(json.dumps({"id": 1, "result": {"thread": {"id": "session-123"}}}), flush=True)
                        print(json.dumps({"id": 2, "result": {"turn": {"id": "turn-1"}}}), flush=True)
                        raise SystemExit(0)
                    raise SystemExit(2)
                    """
                ),
                encoding="utf-8",
            )
            fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
            old_transport = os.environ.get("CODEX_AGENT_BUS_TRANSPORT")
            os.environ["CODEX_AGENT_BUS_TRANSPORT"] = "app-server"
            os.environ["CAPTURE_PATH"] = str(capture)
            try:
                result = CodexResumeTransport(str(fake)).send("session-123", str(target_cwd), "hello prompt")
            finally:
                if old_transport is None:
                    os.environ.pop("CODEX_AGENT_BUS_TRANSPORT", None)
                else:
                    os.environ["CODEX_AGENT_BUS_TRANSPORT"] = old_transport
                os.environ.pop("CAPTURE_PATH", None)
            self.assertTrue(result.ok, result)
            self.assertEqual(result.surface, "app_server_turn_start")
            messages = json.loads(capture.read_text(encoding="utf-8"))
            self.assertEqual(messages[2]["method"], "thread/resume")
            self.assertEqual(messages[2]["params"]["threadId"], "session-123")
            self.assertEqual(messages[2]["params"]["cwd"], str(target_cwd))
            self.assertEqual(messages[3]["method"], "turn/start")
            self.assertEqual(messages[3]["params"]["input"][0]["text"], "hello prompt")

    def test_exec_resume_uses_target_cwd_and_stdin_prompt_when_selected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target_cwd = root / "target"
            target_cwd.mkdir()
            capture = root / "capture.json"
            fake = root / "codex-fake.py"
            fake.write_text(
                textwrap.dedent(
                    """\
                    #!/usr/bin/env python3
                    import json, os, sys
                    if sys.argv[1:] == ["exec", "--help"]:
                        print("  -C, --cd <DIR>")
                        raise SystemExit(0)
                    capture = os.environ["CAPTURE_PATH"]
                    with open(capture, "w", encoding="utf-8") as handle:
                        json.dump({"argv": sys.argv[1:], "cwd": os.getcwd(), "stdin": sys.stdin.read()}, handle)
                    raise SystemExit(0)
                    """
                ),
                encoding="utf-8",
            )
            fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
            old_transport = os.environ.get("CODEX_AGENT_BUS_TRANSPORT")
            os.environ["CODEX_AGENT_BUS_TRANSPORT"] = "exec"
            os.environ["CAPTURE_PATH"] = str(capture)
            try:
                result = CodexResumeTransport(str(fake)).send("session-123", str(target_cwd), "hello prompt")
            finally:
                if old_transport is None:
                    os.environ.pop("CODEX_AGENT_BUS_TRANSPORT", None)
                else:
                    os.environ["CODEX_AGENT_BUS_TRANSPORT"] = old_transport
                os.environ.pop("CAPTURE_PATH", None)
            self.assertTrue(result.ok, result)
            self.assertEqual(result.surface, "exec_resume_noninteractive")
            payload = json.loads(capture.read_text(encoding="utf-8"))
            self.assertEqual(os.path.realpath(payload["cwd"]), os.path.realpath(str(target_cwd)))
            self.assertEqual(payload["stdin"], "hello prompt")
            self.assertEqual(payload["argv"][:3], ["exec", "-C", str(target_cwd)])


if __name__ == "__main__":
    unittest.main()
