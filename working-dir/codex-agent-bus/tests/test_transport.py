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
    def test_resume_uses_target_cwd_and_stdin_prompt(self) -> None:
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
            os.environ["CAPTURE_PATH"] = str(capture)
            try:
                result = CodexResumeTransport(str(fake)).send("session-123", str(target_cwd), "hello prompt")
            finally:
                os.environ.pop("CAPTURE_PATH", None)
            self.assertTrue(result.ok, result)
            payload = json.loads(capture.read_text(encoding="utf-8"))
            self.assertEqual(os.path.realpath(payload["cwd"]), os.path.realpath(str(target_cwd)))
            self.assertEqual(payload["stdin"], "hello prompt")
            self.assertEqual(payload["argv"][:3], ["exec", "-C", str(target_cwd)])


if __name__ == "__main__":
    unittest.main()
