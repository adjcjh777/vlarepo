"""Command line interface for Codex Agent Bus."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

from .mcp_server import call_tool


def print_json(value: Dict[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Codex Agent Bus CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    register = sub.add_parser("register", help="Register an agent")
    register.add_argument("--name", required=True)
    register.add_argument("--role", required=True)
    register.add_argument("--session-id", required=True)
    register.add_argument("--cwd")
    register.add_argument("--status", default="idle")
    register.add_argument("--capability", action="append", default=[])
    register.add_argument("--tag", action="append", default=[])

    update = sub.add_parser("update", help="Update an agent")
    update.add_argument("target")
    update.add_argument("--name")
    update.add_argument("--role")
    update.add_argument("--status")
    update.add_argument("--capability", action="append")
    update.add_argument("--tag", action="append")

    list_agents = sub.add_parser("list", help="List agents")
    list_agents.add_argument("--include-disabled", action="store_true")
    list_agents.add_argument("--cwd-prefix")
    list_agents.add_argument("--tag")

    resolve = sub.add_parser("resolve", help="Resolve an agent")
    resolve.add_argument("target")

    send = sub.add_parser("send", help="Send a message")
    send.add_argument("target")
    send.add_argument("message")
    send.add_argument("--from-agent")
    send.add_argument("--trigger", choices=["queue", "codex_app", "resume"], default="codex_app")
    send.add_argument("--wait", action="store_true")
    send.add_argument("--timeout-sec", type=float, default=600)
    send.add_argument("--correlation-id")
    send.add_argument("--hop-count", type=int, default=0)
    send.add_argument("--allow-pending", action="store_true", help="Queue for a future agent name if target is not registered yet")

    reply = sub.add_parser("reply", help="Reply to a message")
    reply.add_argument("message_id")
    reply.add_argument("result")
    reply.add_argument("--from-agent")
    reply.add_argument("--trigger", choices=["queue", "codex_app", "resume"], default="codex_app")

    inbox = sub.add_parser("inbox", help="Read inbox")
    inbox.add_argument("--target")
    inbox.add_argument("--unread-only", action="store_true")
    inbox.add_argument("--limit", type=int)

    mark = sub.add_parser("mark-read", help="Mark a message as read")
    mark.add_argument("message_id")

    status = sub.add_parser("status", help="Update status")
    status.add_argument("target")
    status.add_argument("status")
    status.add_argument("--note")

    team = sub.add_parser("team", help="Manage Agent Bus teams")
    team_sub = team.add_subparsers(dest="team_command", required=True)

    team_create = team_sub.add_parser("create", help="Create a project team")
    team_create.add_argument("name")
    team_create.add_argument("--project", required=True)
    team_create.add_argument("--goal", required=True)
    team_create.add_argument("--role", action="append", default=[], help="Role spec: name:description or name")
    team_create.add_argument("--from-agent")

    team_sub.add_parser("list", help="List teams")

    team_show = team_sub.add_parser("show", help="Show a team")
    team_show.add_argument("team")

    team_join = team_sub.add_parser("join", help="Join an existing agent to a team role")
    team_join.add_argument("team")
    team_join.add_argument("--role", required=True)
    team_join.add_argument("--agent", required=True)

    team_launch = team_sub.add_parser("launch", help="Prepare role launch prompts or experimentally create role threads")
    team_launch.add_argument("team")
    team_launch.add_argument("--role")
    team_launch.add_argument("--mode", choices=["prompt", "app-server-experimental"], default="prompt")
    team_launch.add_argument("--from-agent")
    team_launch.add_argument("--timeout-sec", type=float, default=60)
    team_launch.add_argument("--deliver-bootstrap", action="store_true")

    team_attach = team_sub.add_parser("attach-thread", help="Attach an existing Codex thread/session to a team role")
    team_attach.add_argument("team")
    team_attach.add_argument("--role", required=True)
    team_attach.add_argument("--thread-id")
    team_attach.add_argument("--session-id")
    team_attach.add_argument("--agent-name")
    team_attach.add_argument("--cwd")
    team_attach.add_argument("--from-agent")

    team_dispatch = team_sub.add_parser("dispatch", help="Dispatch or rebalance a task to a team role")
    team_dispatch.add_argument("team")
    team_dispatch.add_argument("--role", required=True)
    team_dispatch.add_argument("message")
    team_dispatch.add_argument("--from-agent")
    team_dispatch.add_argument("--trigger", choices=["queue", "codex_app", "resume"], default="queue")

    sub.add_parser("health", help="Show bus health")

    args = parser.parse_args(argv)
    try:
        dispatch(args)
    except Exception as exc:
        print_json({"error": str(exc)})
        return 1
    return 0


def dispatch(args: argparse.Namespace) -> None:
    payload: Dict[str, Any]
    if args.command == "register":
        payload = {
            "name": args.name,
            "role": args.role,
            "session_id": args.session_id,
            "cwd": args.cwd,
            "status": args.status,
            "capabilities": args.capability,
            "tags": args.tag,
        }
        print_json(call_tool("register_agent", payload))
    elif args.command == "update":
        payload = {
            "target": args.target,
            "name": args.name,
            "role": args.role,
            "status": args.status,
            "capabilities": args.capability,
            "tags": args.tag,
        }
        print_json(call_tool("update_agent", payload))
    elif args.command == "list":
        print_json(
            call_tool(
                "list_agents",
                {
                    "include_disabled": args.include_disabled,
                    "cwd_prefix": args.cwd_prefix,
                    "tag": args.tag,
                },
            )
        )
    elif args.command == "resolve":
        print_json(call_tool("resolve_agent", {"target": args.target}))
    elif args.command == "send":
        print_json(
            call_tool(
                "send_message",
                {
                    "target": args.target,
                    "message": args.message,
                    "from_agent": args.from_agent,
                    "trigger": args.trigger,
                    "wait": args.wait,
                    "timeout_sec": args.timeout_sec,
                    "correlation_id": args.correlation_id,
                    "hop_count": args.hop_count,
                    "allow_pending": args.allow_pending,
                },
            )
        )
    elif args.command == "reply":
        print_json(
            call_tool(
                "reply_message",
                {
                    "message_id": args.message_id,
                    "result": args.result,
                    "from_agent": args.from_agent,
                    "trigger": args.trigger,
                },
            )
        )
    elif args.command == "inbox":
        print_json(
            call_tool(
                "get_inbox",
                {"target": args.target, "unread_only": args.unread_only, "limit": args.limit},
            )
        )
    elif args.command == "mark-read":
        print_json(call_tool("mark_read", {"message_id": args.message_id}))
    elif args.command == "status":
        print_json(call_tool("update_status", {"target": args.target, "status": args.status, "note": args.note}))
    elif args.command == "team":
        dispatch_team(args)
    elif args.command == "health":
        print_json(call_tool("bus_health", {}))


def dispatch_team(args: argparse.Namespace) -> None:
    if args.team_command == "create":
        print_json(
            call_tool(
                "create_team",
                {
                    "name": args.name,
                    "project": args.project,
                    "goal": args.goal,
                    "roles": parse_role_specs(args.role),
                    "from_agent": args.from_agent,
                },
            )
        )
    elif args.team_command == "list":
        print_json(call_tool("list_teams", {}))
    elif args.team_command == "show":
        print_json(call_tool("show_team", {"team": args.team}))
    elif args.team_command == "join":
        print_json(call_tool("join_team", {"team": args.team, "role": args.role, "agent": args.agent}))
    elif args.team_command == "launch":
        print_json(
            call_tool(
                "launch_team",
                {
                    "team": args.team,
                    "role": args.role,
                    "mode": args.mode,
                    "from_agent": args.from_agent,
                    "timeout_sec": args.timeout_sec,
                    "deliver_bootstrap": args.deliver_bootstrap,
                },
            )
        )
    elif args.team_command == "attach-thread":
        print_json(
            call_tool(
                "attach_team_thread",
                {
                    "team": args.team,
                    "role": args.role,
                    "thread_id": args.thread_id,
                    "session_id": args.session_id,
                    "agent_name": args.agent_name,
                    "cwd": args.cwd,
                    "from_agent": args.from_agent,
                },
            )
        )
    elif args.team_command == "dispatch":
        print_json(
            call_tool(
                "dispatch_team_task",
                {
                    "team": args.team,
                    "role": args.role,
                    "message": args.message,
                    "from_agent": args.from_agent,
                    "trigger": args.trigger,
                },
            )
        )


def parse_role_specs(values: List[str]) -> List[Dict[str, str]]:
    roles: List[Dict[str, str]] = []
    for value in values:
        name, separator, description = value.partition(":")
        role: Dict[str, str] = {"name": name.strip()}
        if separator:
            role["description"] = description.strip()
        roles.append(role)
    return roles


if __name__ == "__main__":
    raise SystemExit(main())
