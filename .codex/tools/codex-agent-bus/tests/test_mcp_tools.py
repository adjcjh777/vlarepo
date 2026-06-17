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
            self.assertEqual(planner["agent_id"], "planner-session")
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
            self.assertEqual(executor["agent_id"], "executor-session")
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
            self.assertEqual(transport.calls[0]["session_id"], "executor-session")
            self.assertIn("用户输入（来自 Codex Agent Bus / planner）", transport.calls[0]["prompt"])
            self.assertIn("用户任务：\ndo work", transport.calls[0]["prompt"])
            self.assertIn("reply_message", transport.calls[0]["prompt"])

    def test_default_send_prepares_codex_app_thread_message(self) -> None:
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
                    "message": "visible work",
                    "from_agent": "planner",
                },
                store=store,
                transport=transport,
            )
            self.assertEqual(result["transport"]["surface"], "codex_app.send_message_to_thread")
            self.assertEqual(result["transport"]["threadId"], "executor-session")
            self.assertIn("用户任务：\nvisible work", result["transport"]["prompt"])
            self.assertEqual(transport.calls, [])
            message = store.find_message(result["message_id"])
            self.assertEqual(message["status"], "prepared")

    def test_send_allow_pending_is_claimed_by_later_registration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = AgentStore(Path(tmp))
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
            sent = call_tool(
                "send_message",
                {
                    "target": "executor",
                    "message": "do future work",
                    "from_agent": "planner",
                    "trigger": "queue",
                    "allow_pending": True,
                },
                store=store,
            )
            self.assertEqual(sent["transport"]["status"], "pending_target")
            self.assertTrue(sent["message"]["pending_target"])
            registered = call_tool(
                "register_agent",
                {
                    "name": "executor",
                    "role": "Executes",
                    "session_id": "executor-session",
                    "cwd": "/tmp/executor-project",
                },
                store=store,
            )
            self.assertEqual(registered["claimed_count"], 1)
            self.assertEqual(registered["claimed_messages"][0]["message_id"], sent["message_id"])
            inbox = call_tool(
                "get_inbox",
                {"target": "executor-session", "unread_only": True},
                store=store,
            )["messages"]
            self.assertEqual([item["message_id"] for item in inbox], [sent["message_id"]])
            self.assertEqual(inbox[0]["to_session_id"], "executor-session")

    def test_create_team_hot_join_and_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = AgentStore(Path(tmp))
            team_result = call_tool(
                "create_team",
                {
                    "name": "Dream QA",
                    "project": "/tmp/dreamqa",
                    "goal": "Improve demo quality",
                    "roles": [
                        {"name": "planner", "description": "Plans work"},
                        {"name": "tester", "description": "Runs QA"},
                    ],
                },
                store=store,
            )
            team = team_result["team"]
            self.assertEqual(team["project"], "/tmp/dreamqa")
            self.assertIn("planner", team["roles"])
            self.assertIn("tester", team["roles"])
            self.assertEqual(len(team_result["messages"]), 2)
            self.assertEqual(len(team_result["launch_prompts"]), 2)
            tester_alias = team["roles"]["tester"]["alias"]
            registered = call_tool(
                "register_agent",
                {
                    "name": tester_alias,
                    "role": "Runs QA",
                    "session_id": "tester-session",
                    "cwd": "/tmp/dreamqa",
                },
                store=store,
            )
            self.assertEqual(registered["claimed_count"], 1)
            joined_team = call_tool("show_team", {"team": team["team_id"]}, store=store)["team"]
            self.assertEqual(joined_team["roles"]["tester"]["status"], "active")
            self.assertEqual(joined_team["roles"]["tester"]["session_id"], "tester-session")
            dispatched = call_tool(
                "dispatch_team_task",
                {
                    "team": team["team_id"],
                    "role": "tester",
                    "message": "Run smoke tests",
                    "trigger": "queue",
                },
                store=store,
            )
            self.assertEqual(dispatched["dispatch"]["target"]["session_id"], "tester-session")
            self.assertIn("Run smoke tests", dispatched["dispatch"]["message"]["body"])
            self.assertEqual(dispatched["dispatch"]["message"]["team_id"], team["team_id"])
            self.assertEqual(dispatched["dispatch"]["message"]["team_role"], "tester")


if __name__ == "__main__":
    unittest.main()
