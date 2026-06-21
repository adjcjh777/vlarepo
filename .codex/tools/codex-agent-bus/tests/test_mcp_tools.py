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


class FakeThreadLauncher:
    def __init__(self) -> None:
        self.calls = []
        self.count = 0

    def start_thread(self, cwd, timeout_sec=None):
        self.count += 1
        thread_id = "launched-thread-%s" % self.count
        self.calls.append({"cwd": cwd, "timeout_sec": timeout_sec, "thread_id": thread_id})
        return {
            "ok": True,
            "status": "thread_created",
            "surface": "fake_thread_start",
            "cwd": cwd,
            "thread_id": thread_id,
        }


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
            self.assertEqual(planner["agent_id"], "planner")
            self.assertEqual(planner["session_id"], "planner-session")
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
            self.assertEqual(executor["agent_id"], "executor")
            self.assertEqual(executor["session_id"], "executor-session")
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
            self.assertIn("CLI fallback", transport.calls[0]["prompt"])
            self.assertIn("agent-bus reply", transport.calls[0]["prompt"])
            self.assertIn("--from-agent executor-session --trigger queue", transport.calls[0]["prompt"])

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

    def test_send_subagent_tool_prepares_send_input_payload(self) -> None:
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
            call_tool(
                "register_agent",
                {
                    "name": "tester",
                    "role": "Tests",
                    "session_id": "spawned-agent-1",
                    "cwd": "/tmp/project",
                },
                store=store,
            )
            sent = call_tool(
                "send_message",
                {
                    "target": "tester",
                    "message": "run subagent smoke",
                    "from_agent": "planner",
                    "trigger": "subagent_tool",
                },
                store=store,
            )
            self.assertEqual(sent["transport"]["surface"], "multi_agent_v1.send_input")
            self.assertEqual(sent["transport"]["target"], "spawned-agent-1")
            self.assertIn("run subagent smoke", sent["transport"]["prompt"])
            self.assertEqual(store.find_message(sent["message_id"])["status"], "prepared")

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

    def test_team_dispatch_subagent_tool_targets_attached_role(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = AgentStore(Path(tmp))
            team_result = call_tool(
                "create_team",
                {
                    "name": "Dream QA",
                    "project": "/tmp/dreamqa",
                    "goal": "Improve demo quality",
                    "roles": [{"name": "tester", "description": "Runs QA"}],
                },
                store=store,
            )
            call_tool(
                "attach_team_thread",
                {
                    "team": team_result["team"]["team_id"],
                    "role": "tester",
                    "thread_id": "spawned-agent-1",
                },
                store=store,
            )
            dispatched = call_tool(
                "dispatch_team_task",
                {
                    "team": team_result["team"]["team_id"],
                    "role": "tester",
                    "message": "Run smoke tests",
                    "trigger": "subagent_tool",
                },
                store=store,
            )
            transport = dispatched["dispatch"]["transport"]
            self.assertEqual(transport["surface"], "multi_agent_v1.send_input")
            self.assertEqual(transport["target"], "spawned-agent-1")
            self.assertIn("Run smoke tests", transport["prompt"])
            role = dispatched["team"]["roles"]["tester"]
            self.assertEqual(role["agent_id"], team_result["team"]["roles"]["tester"]["alias"])
            self.assertEqual(role["session_id"], "spawned-agent-1")

    def test_team_launch_prompt_records_launch_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = AgentStore(Path(tmp))
            team_result = call_tool(
                "create_team",
                {
                    "name": "Dream QA",
                    "project": "/tmp/dreamqa",
                    "goal": "Improve demo quality",
                    "roles": [{"name": "tester", "description": "Runs QA"}],
                },
                store=store,
            )
            launched = call_tool(
                "launch_team",
                {"team": team_result["team"]["team_id"], "role": "tester", "mode": "prompt"},
                store=store,
            )
            self.assertEqual(launched["launches"][0]["status"], "prompt_ready")
            self.assertIn("register_self.py", launched["launches"][0]["launch_prompt"]["prompt"])
            role = launched["team"]["roles"]["tester"]
            self.assertEqual(role["launch_status"], "pending_manual_launch")
            self.assertEqual(role["launch_mode"], "prompt")
            self.assertIn("launch_prompt", role)

    def test_attach_team_thread_claims_bootstrap_and_prepares_visible_delivery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = AgentStore(Path(tmp))
            team_result = call_tool(
                "create_team",
                {
                    "name": "Dream QA",
                    "project": "/tmp/dreamqa",
                    "goal": "Improve demo quality",
                    "roles": [{"name": "tester", "description": "Runs QA"}],
                },
                store=store,
            )
            attached = call_tool(
                "attach_team_thread",
                {
                    "team": team_result["team"]["team_id"],
                    "role": "tester",
                    "thread_id": "existing-thread-1",
                },
                store=store,
            )
            self.assertEqual(attached["agent"]["session_id"], "existing-thread-1")
            self.assertEqual(attached["claimed_message"]["to_session_id"], "existing-thread-1")
            self.assertEqual(attached["claimed_message"]["status"], "prepared")
            self.assertEqual(attached["visible_delivery"]["threadId"], "existing-thread-1")
            role = attached["team"]["roles"]["tester"]
            self.assertEqual(role["status"], "active")
            self.assertEqual(role["launch_status"], "attached_existing_thread")
            self.assertEqual(role["thread_id"], "existing-thread-1")

    def test_team_launch_subagent_tool_returns_spawn_request(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = AgentStore(Path(tmp))
            team_result = call_tool(
                "create_team",
                {
                    "name": "Dream QA",
                    "project": "/tmp/dreamqa",
                    "goal": "Improve demo quality",
                    "roles": [{"name": "tester", "description": "Runs QA"}],
                },
                store=store,
            )
            launched = call_tool(
                "launch_team",
                {
                    "team": team_result["team"]["team_id"],
                    "role": "tester",
                    "mode": "subagent-tool",
                },
                store=store,
            )
            launch = launched["launches"][0]
            self.assertEqual(launch["status"], "spawn_tool_required")
            self.assertEqual(launch["spawn_request"]["tool"], "multi_agent_v1.spawn_agent")
            self.assertEqual(launch["spawn_request"]["agent_type"], "worker")
            self.assertEqual(
                launch["spawn_request"]["attach_after_spawn"]["thread_id_source"],
                "spawn_agent.agent_id",
            )
            self.assertIn("不要臆造自己的 id", launch["spawn_request"]["message"])
            self.assertIn("reply_message", launch["spawn_request"]["message"])
            self.assertIn("agent-bus reply", launch["spawn_request"]["message"])
            self.assertIn("--from-agent dream-qa-tester --trigger queue", launch["spawn_request"]["message"])
            role = launched["team"]["roles"]["tester"]
            self.assertEqual(role["launch_status"], "spawn_tool_required")
            self.assertEqual(role["launch_mode"], "subagent-tool")
            self.assertEqual(role["spawn_request"]["tool"], "multi_agent_v1.spawn_agent")

    def test_team_launch_codex_app_returns_create_thread_request(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = AgentStore(Path(tmp))
            team_result = call_tool(
                "create_team",
                {
                    "name": "Dream QA",
                    "project": "/tmp/dreamqa",
                    "goal": "Improve demo quality",
                    "roles": [{"name": "tester", "description": "Runs QA"}],
                },
                store=store,
            )
            launched = call_tool(
                "launch_team",
                {
                    "team": team_result["team"]["team_id"],
                    "role": "tester",
                    "mode": "codex-app",
                    "codex_projects": [
                        {"projectId": "/tmp", "path": "/tmp", "label": "tmp"},
                        {"projectId": "/tmp/other", "path": "/tmp/other", "label": "other"},
                    ],
                },
                store=store,
            )
            launch = launched["launches"][0]
            self.assertEqual(launch["status"], "codex_app_create_thread_required")
            self.assertEqual(launch["create_thread_request"]["tool"], "codex_app.create_thread")
            self.assertEqual(launch["create_thread_request"]["target"]["projectId"], "/tmp")
            self.assertEqual(
                launch["create_thread_request"]["target"]["environment"],
                {"type": "local"},
            )
            self.assertEqual(launch["project_resolution"]["status"], "deepest_parent")
            self.assertEqual(launch["project_resolution"]["matched_project_path"], "/tmp")
            self.assertIn("ACK_CODEX_APP_THREAD_CREATED_VISIBLE", launch["create_thread_request"]["prompt"])
            self.assertEqual(launch["attach_after_create"]["thread_id_source"], "create_thread.threadId")
            self.assertIn("team attach-thread", launch["attach_after_create"]["command"])
            self.assertEqual(launch["deliver_after_attach"]["tool"], "codex_app.send_message_to_thread")
            self.assertEqual(
                launch["deliver_after_attach"]["prompt_source"],
                "attach_team_thread.visible_delivery.prompt",
            )
            role = launched["team"]["roles"]["tester"]
            self.assertEqual(role["launch_status"], "codex_app_create_thread_required")
            self.assertEqual(role["launch_mode"], "codex-app")
            self.assertEqual(role["codex_app_create_thread"]["target"]["projectId"], "/tmp")

    def test_experimental_team_launch_starts_thread_and_attaches_role(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = AgentStore(Path(tmp))
            launcher = FakeThreadLauncher()
            team_result = call_tool(
                "create_team",
                {
                    "name": "Dream QA",
                    "project": "/tmp/dreamqa",
                    "goal": "Improve demo quality",
                    "roles": [{"name": "tester", "description": "Runs QA"}],
                },
                store=store,
            )
            launched = call_tool(
                "launch_team",
                {
                    "team": team_result["team"]["team_id"],
                    "role": "tester",
                    "mode": "app-server-experimental",
                },
                store=store,
                thread_launcher=launcher,
            )
            self.assertEqual(launcher.calls[0]["cwd"], "/tmp/dreamqa")
            self.assertEqual(launched["launches"][0]["thread_start"]["thread_id"], "launched-thread-1")
            role = launched["team"]["roles"]["tester"]
            self.assertEqual(role["status"], "active")
            self.assertEqual(role["session_id"], "launched-thread-1")
            self.assertEqual(role["launch_status"], "thread_created_unverified_visibility")
            self.assertEqual(launched["thread_creation"]["visibility"], "unverified")


if __name__ == "__main__":
    unittest.main()
