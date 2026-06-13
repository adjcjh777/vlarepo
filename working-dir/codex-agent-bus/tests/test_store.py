from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_bus.store import AgentStore, AmbiguousTargetError


class StoreTests(unittest.TestCase):
    def test_upsert_resolve_and_global_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = AgentStore(Path(tmp))
            agent = store.upsert_agent(
                name="executor",
                role="Runs tests",
                session_id="session-a",
                cwd="/tmp/project-a",
                capabilities=["test"],
                tags=["ci"],
                status="idle",
            )
            self.assertEqual(agent["cwd"], "/tmp/project-a")
            self.assertEqual(agent["agent_id"], "session-a")
            self.assertTrue((Path(tmp) / "registry.json").exists())
            self.assertTrue((Path(tmp) / "messages.jsonl").exists())
            self.assertEqual(store.resolve_agent("executor")["session_id"], "session-a")
            updated = store.upsert_agent(
                name="executor",
                role="Runs focused tests",
                session_id="session-a",
                cwd="/tmp/project-b",
                status="running",
            )
            self.assertEqual(updated["agent_id"], agent["agent_id"])
            self.assertEqual(updated["cwd"], "/tmp/project-b")

    def test_legacy_name_derived_agent_id_migrates_to_session_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "registry.json"
            registry.write_text(
                """
{
  "version": "0.1.0",
  "updated_at": "2026-06-13T00:00:00Z",
  "agents": {
    "bandofagents-planner-52fbc9fd": {
      "agent_id": "bandofagents-planner-52fbc9fd",
      "name": "bandofagents-planner",
      "role": "Plans",
      "session_id": "019ec041-0e14-7e23-9f27-be6890b12288",
      "cwd": "/tmp/planner",
      "last_seen": "2026-06-13T00:00:00Z",
      "enabled": true
    }
  }
}
""",
                encoding="utf-8",
            )
            store = AgentStore(root)
            agents = store.list_agents()
            self.assertEqual(len(agents), 1)
            self.assertEqual(agents[0]["agent_id"], "019ec041-0e14-7e23-9f27-be6890b12288")
            self.assertIn("bandofagents-planner-52fbc9fd", agents[0]["legacy_agent_ids"])
            self.assertEqual(
                store.resolve_agent("bandofagents-planner-52fbc9fd")["agent_id"],
                "019ec041-0e14-7e23-9f27-be6890b12288",
            )

    def test_ambiguous_name_returns_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = AgentStore(Path(tmp))
            store.upsert_agent("executor", "A", "session-a", cwd="/tmp/a")
            store.upsert_agent("executor", "B", "session-b", cwd="/tmp/b")
            with self.assertRaises(AmbiguousTargetError) as ctx:
                store.resolve_agent("executor")
            self.assertEqual(len(ctx.exception.candidates), 2)

    def test_message_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = AgentStore(Path(tmp))
            message = store.append_message({"body": "hello", "to_session_id": "s1", "correlation_id": None})
            self.assertTrue(message["correlation_id"])
            marked = store.mark_read(message["message_id"])
            self.assertIn("read_at", marked)
            inbox = store.get_inbox(limit=10)
            self.assertEqual(inbox[0]["message_id"], message["message_id"])


if __name__ == "__main__":
    unittest.main()
