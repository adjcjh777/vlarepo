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
    send.add_argument("--trigger", choices=["queue", "resume"], default="resume")
    send.add_argument("--wait", action="store_true")
    send.add_argument("--timeout-sec", type=float, default=600)
    send.add_argument("--correlation-id")
    send.add_argument("--hop-count", type=int, default=0)

    reply = sub.add_parser("reply", help="Reply to a message")
    reply.add_argument("message_id")
    reply.add_argument("result")
    reply.add_argument("--from-agent")
    reply.add_argument("--trigger", choices=["queue", "resume"], default="resume")

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
    elif args.command == "health":
        print_json(call_tool("bus_health", {}))


if __name__ == "__main__":
    raise SystemExit(main())
