from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_bus.mcp_server import call_tool
from agent_bus.store import AgentStore


class FakeTransport:
    def __init__(self) -> None:
        self.calls = []

    def send(self, session_id, cwd, prompt, timeout_sec=None):
        self.calls.append(
            {
                "session_id": session_id,
                "cwd": cwd,
                "prompt": prompt,
                "timeout_sec": timeout_sec,
            }
        )

        class Result:
            ok = True
            status = "delivered"
            error = None

            def to_dict(self):
                return {"ok": True, "status": "delivered", "cwd": cwd}

        return Result()


class McpToolTests(unittest.TestCase):
    def test_register_list_send_queue_and_reply_queue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = AgentStore(Path(tmp))
            planner = call_tool(
                "register_agent",
                {
                    "name": "planner",
                    "role": "Plans",
                    "session_id": "planner-session",
                    "cwd": "/tmp/planner",
                },
                store=store,
            )["agent"]
            executor = call_tool(
                "register_agent",
                {
                    "name": "executor",
                    "role": "Executes",
                    "session_id": "executor-session",
                    "cwd": "/tmp/executor",
                },
                store=store,
            )["agent"]
            listed = call_tool("list_agents", {}, store=store)["agents"]
            self.assertEqual({item["name"] for item in listed}, {"planner", "executor"})
            sent = call_tool(
                "send_message",
                {
                    "target": "executor",
                    "message": "do work",
                    "from_agent": "planner",
                    "trigger": "queue",
                },
                store=store,
            )
            self.assertEqual(sent["transport"]["status"], "queued")
            self.assertEqual(sent["target"]["cwd"], "/tmp/executor")
            reply = call_tool(
                "reply_message",
                {
                    "message_id": sent["message_id"],
                    "result": "done",
                    "from_agent": "executor",
                    "trigger": "queue",
                },
                store=store,
            )
            self.assertEqual(reply["source"]["agent_id"], planner["agent_id"])
            original = store.find_message(sent["message_id"])
            self.assertEqual(original["status"], "replied")
            self.assertEqual(executor["cwd"], "/tmp/executor")

    def test_send_resume_uses_target_agent_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = AgentStore(Path(tmp))
            transport = FakeTransport()
            call_tool(
                "register_agent",
                {
                    "name": "planner",
                    "role": "Plans",
                    "session_id": "planner-session",
                    "cwd": "/tmp/planner",
                },
                store=store,
            )
            call_tool(
                "register_agent",
                {
                    "name": "executor",
                    "role": "Executes",
                    "session_id": "executor-session",
                    "cwd": "/tmp/executor-project",
                },
                store=store,
            )
            result = call_tool(
                "send_message",
                {
                    "target": "executor",
                    "message": "do work",
                    "from_agent": "planner",
                    "trigger": "resume",
                },
                store=store,
                transport=transport,
            )
            self.assertEqual(result["transport"]["cwd"], "/tmp/executor-project")
            self.assertEqual(transport.calls[0]["cwd"], "/tmp/executor-project")
            self.assertIn("reply_message", transport.calls[0]["prompt"])


if __name__ == "__main__":
    unittest.main()
