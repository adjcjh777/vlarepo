from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from scripts.install_agent_bus import update_user_config


class InstallTests(unittest.TestCase):
    def test_dry_run_does_not_print_existing_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "config.toml"
            config.write_text('secret = "do-not-print"\n', encoding="utf-8")
            out = io.StringIO()
            with redirect_stdout(out):
                update_user_config(config, root / "tool", root / "bus", dry_run=True)
            rendered = out.getvalue()
            self.assertIn("CODEX_AGENT_BUS", rendered)
            self.assertNotIn("do-not-print", rendered)


if __name__ == "__main__":
    unittest.main()
