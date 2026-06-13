"""Minimal stdio MCP server for Codex Agent Bus."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from . import __version__
from .store import (
    AgentBusError,
    AgentStore,
    AmbiguousTargetError,
    MAX_HOP_COUNT,
    NotFoundError,
    utc_now,
)
from .transport import CodexResumeTransport


SERVER_INSTRUCTIONS = (
    "This is a local Codex Agent Bus. Use list_agents to discover peers, "
    "send_message(target, message, trigger='resume') to delegate work to another "
    "Codex session, and reply_message after delegated work is complete. Do not put "
    "secrets in messages. Do not create infinite ping-pong loops; correlation hop "
    "count is capped."
)


def json_schema(
    properties: Dict[str, Any],
    required: Optional[List[str]] = None,
) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required or [],
        "additionalProperties": False,
    }


TOOLS: List[Dict[str, Any]] = [
    {
        "name": "register_agent",
        "description": "Register or update the current Codex session in the global Agent Bus registry.",
        "inputSchema": json_schema(
            {
                "name": {"type": "string"},
                "role": {"type": "string"},
                "session_id": {"type": "string"},
                "cwd": {"type": "string"},
                "capabilities": {"type": "array", "items": {"type": "string"}},
                "tags": {"type": "array", "items": {"type": "string"}},
                "status": {"type": "string"},
            },
            ["name", "role"],
        ),
    },
    {
        "name": "update_agent",
        "description": "Update an agent by agent_id, name, or session_id.",
        "inputSchema": json_schema(
            {
                "target": {"type": "string"},
                "name": {"type": "string"},
                "role": {"type": "string"},
                "status": {"type": "string"},
                "capabilities": {"type": "array", "items": {"type": "string"}},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            ["target"],
        ),
    },
    {
        "name": "list_agents",
        "description": "List registered agents sorted by last_seen descending.",
        "inputSchema": json_schema(
            {
                "include_disabled": {"type": "boolean"},
                "cwd_prefix": {"type": "string"},
                "tag": {"type": "string"},
            }
        ),
    },
    {
        "name": "resolve_agent",
        "description": "Resolve agent_id, name, or session_id to one agent. Returns candidates when ambiguous.",
        "inputSchema": json_schema({"target": {"type": "string"}}, ["target"]),
    },
    {
        "name": "send_message",
        "description": "Write a message and optionally resume the target Codex session.",
        "inputSchema": json_schema(
            {
                "target": {"type": "string"},
                "message": {"type": "string"},
                "from_agent": {"type": "string"},
                "trigger": {"type": "string", "enum": ["queue", "resume"]},
                "wait": {"type": "boolean"},
                "timeout_sec": {"type": "number"},
                "correlation_id": {"type": "string"},
                "hop_count": {"type": "number"},
            },
            ["target", "message"],
        ),
    },
    {
        "name": "reply_message",
        "description": "Reply to an Agent Bus message by message_id.",
        "inputSchema": json_schema(
            {
                "message_id": {"type": "string"},
                "result": {"type": "string"},
                "from_agent": {"type": "string"},
                "trigger": {"type": "string", "enum": ["queue", "resume"]},
            },
            ["message_id", "result"],
        ),
    },
    {
        "name": "get_inbox",
        "description": "Read messages addressed to an agent/session without triggering resume.",
        "inputSchema": json_schema(
            {
                "target": {"type": "string"},
                "unread_only": {"type": "boolean"},
                "limit": {"type": "number"},
            }
        ),
    },
    {
        "name": "mark_read",
        "description": "Mark a message as read.",
        "inputSchema": json_schema({"message_id": {"type": "string"}}, ["message_id"]),
    },
    {
        "name": "update_status",
        "description": "Update an agent status and last_seen timestamp.",
        "inputSchema": json_schema(
            {
                "target": {"type": "string"},
                "status": {"type": "string"},
                "note": {"type": "string"},
            },
            ["target", "status"],
        ),
    },
    {
        "name": "bus_health",
        "description": "Check Agent Bus files, Codex command, version, and recent errors.",
        "inputSchema": json_schema({}),
    },
]


def call_tool(
    name: str,
    arguments: Optional[Dict[str, Any]] = None,
    store: Optional[AgentStore] = None,
    transport: Optional[CodexResumeTransport] = None,
) -> Dict[str, Any]:
    args = arguments or {}
    store = store or AgentStore()
    transport = transport or CodexResumeTransport()
    if name == "register_agent":
        session_id = args.get("session_id") or os.environ.get("CODEX_SESSION_ID")
        if not session_id:
            raise AgentBusError(
                "session_id is required. Use Codex /status or SessionStart hook auto-registration."
            )
        return {
            "agent": store.upsert_agent(
                name=args.get("name") or "",
                role=args.get("role") or "",
                session_id=session_id,
                cwd=args.get("cwd") or os.environ.get("PWD") or os.getcwd(),
                status=args.get("status") or "idle",
                capabilities=args.get("capabilities"),
                tags=args.get("tags"),
            )
        }
    if name == "update_agent":
        return {"agent": store.update_agent(args["target"], args)}
    if name == "list_agents":
        return {
            "agents": store.list_agents(
                include_disabled=bool(args.get("include_disabled", False)),
                cwd_prefix=args.get("cwd_prefix"),
                tag=args.get("tag"),
            )
        }
    if name == "resolve_agent":
        try:
            return {"agent": store.resolve_agent(args["target"], include_disabled=True)}
        except AmbiguousTargetError as exc:
            return {"ambiguous": True, "candidates": exc.candidates}
    if name == "send_message":
        return send_message(store, transport, args)
    if name == "reply_message":
        return reply_message(store, transport, args)
    if name == "get_inbox":
        return {
            "messages": store.get_inbox(
                target=args.get("target"),
                unread_only=bool(args.get("unread_only", False)),
                limit=int(args["limit"]) if args.get("limit") else None,
            )
        }
    if name == "mark_read":
        return {"message": store.mark_read(args["message_id"])}
    if name == "update_status":
        return {
            "agent": store.update_status(
                target=args["target"],
                status=args["status"],
                note=args.get("note"),
            )
        }
    if name == "bus_health":
        return store.health()
    raise AgentBusError("Unknown tool %r" % name)


def send_message(
    store: AgentStore,
    transport: CodexResumeTransport,
    args: Dict[str, Any],
) -> Dict[str, Any]:
    target = store.resolve_agent(args["target"])
    from_agent = resolve_from_agent(store, args.get("from_agent"))
    hop_count = int(args.get("hop_count") or 0)
    if hop_count > MAX_HOP_COUNT:
        raise AgentBusError("Refusing to trigger resume: hop_count %s exceeds %s" % (hop_count, MAX_HOP_COUNT))
    trigger = args.get("trigger") or "resume"
    correlation_id = args.get("correlation_id")
    message = store.append_message(
        {
            "correlation_id": correlation_id,
            "from_agent_id": from_agent.get("agent_id"),
            "from_session_id": from_agent.get("session_id"),
            "to_agent_id": target.get("agent_id"),
            "to_session_id": target.get("session_id"),
            "trigger": trigger,
            "hop_count": hop_count,
            "body": args["message"],
            "status": "queued",
            "message_type": "request",
        }
    )
    transport_result = None
    if trigger == "resume":
        prompt = build_request_prompt(from_agent, target, message)
        transport_result = transport.send(
            session_id=target["session_id"],
            cwd=target["cwd"],
            prompt=prompt,
            timeout_sec=float(args.get("timeout_sec") or 600),
        )
        if transport_result.ok:
            message = store.update_message(
                message["message_id"],
                {"status": "delivered", "delivered_at": utc_now()},
            )
        else:
            message = store.update_message(
                message["message_id"],
                {"status": transport_result.status, "error": transport_result.error},
            )
    reply = None
    if bool(args.get("wait", False)):
        reply = store.wait_for_reply(
            correlation_id=message["correlation_id"],
            parent_message_id=message["message_id"],
            timeout_sec=float(args.get("timeout_sec") or 600),
        )
    return {
        "message_id": message["message_id"],
        "correlation_id": message["correlation_id"],
        "target": target,
        "message": message,
        "transport": transport_result.to_dict() if transport_result else {"status": "queued"},
        "reply": reply,
    }


def reply_message(
    store: AgentStore,
    transport: CodexResumeTransport,
    args: Dict[str, Any],
) -> Dict[str, Any]:
    original = store.find_message(args["message_id"])
    source_target = original.get("from_agent_id") or original.get("from_session_id")
    if not source_target:
        raise AgentBusError("Original message has no source agent/session to reply to")
    source = store.resolve_agent(source_target, include_disabled=True)
    from_agent = resolve_from_agent(store, args.get("from_agent"))
    trigger = args.get("trigger") or "resume"
    reply = store.append_message(
        {
            "correlation_id": original.get("correlation_id"),
            "parent_message_id": original.get("message_id"),
            "from_agent_id": from_agent.get("agent_id"),
            "from_session_id": from_agent.get("session_id"),
            "to_agent_id": source.get("agent_id"),
            "to_session_id": source.get("session_id"),
            "trigger": trigger,
            "hop_count": int(original.get("hop_count") or 0) + 1,
            "body": args["result"],
            "result_summary": summarize(args["result"]),
            "status": "queued",
            "message_type": "reply",
        }
    )
    store.update_message(original["message_id"], {"status": "replied"})
    transport_result = None
    if trigger == "resume":
        if int(reply.get("hop_count") or 0) > MAX_HOP_COUNT:
            raise AgentBusError("Refusing to resume reply: hop_count exceeds %s" % MAX_HOP_COUNT)
        prompt = build_reply_prompt(source, from_agent, original, reply)
        transport_result = transport.send(
            session_id=source["session_id"],
            cwd=source["cwd"],
            prompt=prompt,
            timeout_sec=600,
        )
        if transport_result.ok:
            reply = store.update_message(
                reply["message_id"],
                {"status": "delivered", "delivered_at": utc_now()},
            )
        else:
            reply = store.update_message(
                reply["message_id"],
                {"status": transport_result.status, "error": transport_result.error},
            )
    return {
        "message_id": reply["message_id"],
        "correlation_id": reply["correlation_id"],
        "reply": reply,
        "source": source,
        "transport": transport_result.to_dict() if transport_result else {"status": "queued"},
    }


def resolve_from_agent(store: AgentStore, from_agent: Optional[str]) -> Dict[str, Any]:
    if from_agent:
        return store.resolve_agent(from_agent, include_disabled=True)
    env_agent = os.environ.get("CODEX_AGENT_ID") or os.environ.get("CODEX_SESSION_ID")
    if env_agent:
        try:
            return store.resolve_agent(env_agent, include_disabled=True)
        except AgentBusError:
            pass
    return {
        "agent_id": None,
        "name": os.environ.get("CODEX_AGENT_NAME") or "unknown",
        "session_id": os.environ.get("CODEX_SESSION_ID"),
        "cwd": os.environ.get("PWD") or os.getcwd(),
    }


def build_request_prompt(
    from_agent: Dict[str, Any],
    target: Dict[str, Any],
    message: Dict[str, Any],
) -> str:
    return "\n".join(
        [
            "[Codex Agent Bus delegated task]",
            "from_agent_id: %s" % (from_agent.get("agent_id") or "unknown"),
            "from_agent_name: %s" % (from_agent.get("name") or "unknown"),
            "from_session_id: %s" % (from_agent.get("session_id") or "unknown"),
            "to_agent_id: %s" % target.get("agent_id"),
            "to_agent_name: %s" % target.get("name"),
            "message_id: %s" % message.get("message_id"),
            "correlation_id: %s" % message.get("correlation_id"),
            "hop_count: %s" % message.get("hop_count"),
            "",
            "Task:",
            str(message.get("body") or ""),
            "",
            "When complete, call Agent Bus reply_message with message_id=%r and your result. "
            "Do not include secrets. If you delegate further, preserve correlation_id and increment hop_count."
            % message.get("message_id"),
        ]
    )


def build_reply_prompt(
    source: Dict[str, Any],
    from_agent: Dict[str, Any],
    original: Dict[str, Any],
    reply: Dict[str, Any],
) -> str:
    del source
    return "\n".join(
        [
            "[Codex Agent Bus reply]",
            "from_agent_id: %s" % (from_agent.get("agent_id") or "unknown"),
            "from_agent_name: %s" % (from_agent.get("name") or "unknown"),
            "original_message_id: %s" % original.get("message_id"),
            "reply_message_id: %s" % reply.get("message_id"),
            "correlation_id: %s" % reply.get("correlation_id"),
            "",
            "Result:",
            str(reply.get("body") or ""),
        ]
    )


def summarize(value: str, limit: int = 500) -> str:
    value = " ".join(str(value).split())
    return value[:limit]


class MCPServer:
    def __init__(self) -> None:
        self.store = AgentStore()
        self.transport = CodexResumeTransport()

    def handle(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        method = request.get("method")
        request_id = request.get("id")
        try:
            if method == "initialize":
                return self._response(
                    request_id,
                    {
                        "protocolVersion": request.get("params", {}).get("protocolVersion", "2024-11-05"),
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "codex-agent-bus", "version": __version__},
                        "instructions": SERVER_INSTRUCTIONS,
                    },
                )
            if method == "tools/list":
                return self._response(request_id, {"tools": TOOLS})
            if method == "tools/call":
                params = request.get("params") or {}
                tool_name = params.get("name")
                args = params.get("arguments") or {}
                result = call_tool(tool_name, args, self.store, self.transport)
                return self._response(request_id, tool_result(result))
            if method == "notifications/initialized":
                return None
            return self._error(request_id, -32601, "Method not found: %s" % method)
        except AmbiguousTargetError as exc:
            return self._response(
                request_id,
                tool_result({"ambiguous": True, "candidates": exc.candidates}, is_error=True),
            )
        except (AgentBusError, NotFoundError, KeyError, ValueError) as exc:
            return self._response(request_id, tool_result({"error": str(exc)}, is_error=True))
        except Exception as exc:
            self.store.log_error("Unhandled MCP error", {"error": repr(exc)})
            return self._response(request_id, tool_result({"error": repr(exc)}, is_error=True))

    def _response(self, request_id: Any, result: Any) -> Dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    def _error(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def tool_result(value: Dict[str, Any], is_error: bool = False) -> Dict[str, Any]:
    return {
        "content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)}],
        "structuredContent": value,
        "isError": is_error,
    }


def read_message(stream: Any) -> Optional[Dict[str, Any]]:
    first = stream.readline()
    if not first:
        return None
    if isinstance(first, bytes):
        first_text = first.decode("utf-8", "replace")
    else:
        first_text = first
    if first_text.lower().startswith("content-length:"):
        headers = [first_text]
        while True:
            line = stream.readline()
            if isinstance(line, bytes):
                line_text = line.decode("utf-8", "replace")
            else:
                line_text = line
            if line_text in ("\r\n", "\n", ""):
                break
            headers.append(line_text)
        length = 0
        for header in headers:
            if header.lower().startswith("content-length:"):
                length = int(header.split(":", 1)[1].strip())
        body = stream.read(length)
        if isinstance(body, bytes):
            body = body.decode("utf-8", "replace")
        return json.loads(body)
    return json.loads(first_text)


def write_message(message: Dict[str, Any], stream: Any) -> None:
    body = json.dumps(message, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    header = ("Content-Length: %d\r\n\r\n" % len(body)).encode("ascii")
    stream.write(header + body)
    stream.flush()


def serve() -> None:
    server = MCPServer()
    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer
    while True:
        try:
            request = read_message(stdin)
        except Exception as exc:
            server.store.log_error("Failed to read MCP message", {"error": repr(exc)})
            break
        if request is None:
            break
        response = server.handle(request)
        if response is not None:
            write_message(response, stdout)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Codex Agent Bus MCP stdio server.")
    parser.parse_args(argv)
    serve()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
