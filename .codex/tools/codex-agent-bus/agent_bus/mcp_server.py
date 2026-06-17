"""Minimal stdio MCP server for Codex Agent Bus."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

from . import __version__
from .store import (
    AgentBusError,
    AgentStore,
    AmbiguousTargetError,
    MAX_HOP_COUNT,
    NotFoundError,
    utc_now,
)
from .transport import CodexResumeTransport, CodexThreadStartTransport


SERVER_INSTRUCTIONS = (
    "This is a local Codex Agent Bus. Use list_agents to discover peers, "
    "create_team(project, goal, roles) to bootstrap a role-based project team, "
    "launch_team(team, role, mode='subagent-tool') to prepare subagent spawn "
    "requests, launch_team(..., mode='prompt') for manual launch prompts, or "
    "launch_team(..., mode='app-server-experimental') for experimental app-server "
    "threads. After spawning, attach_team_thread(team, role, thread_id) binds the "
    "returned Codex agent/thread id to a role, "
    "send_message(target, message, trigger='codex_app') to prepare a visible "
    "Codex App user turn, then immediately call codex_app.send_message_to_thread "
    "with the returned threadId and prompt. Use trigger='subagent_tool' for "
    "spawned multi_agent_v1 agents and then call multi_agent_v1.send_input. "
    "Use trigger='resume' only for headless fallback. Use allow_pending=true "
    "to queue work for a future agent name before that session has registered; "
    "it will be claimed on registration. "
    "Do not put secrets in messages. agent_id is the Codex "
    "session_id; name is only a human alias. Do not create infinite ping-pong loops; "
    "correlation hop count is capped."
)


DEFAULT_TEAM_ROLES: List[Dict[str, str]] = [
    {"name": "planner", "description": "Reads project context, maintains the task ledger, and coordinates role assignments."},
    {"name": "executor", "description": "Implements bounded code changes inside explicit file locks and reports changed paths."},
    {"name": "tester", "description": "Runs read-only verification, tests, browser/live smoke when applicable, and reports PASS/FAIL/BLOCKED."},
    {"name": "reviewer", "description": "Audits final claims, scope boundaries, secrets, and release readiness before integration."},
]


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
        "description": "Update an agent by agent_id/session_id or human-readable name.",
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
        "description": "Resolve session_id/agent_id or human-readable name to one agent. Returns candidates when ambiguous.",
        "inputSchema": json_schema({"target": {"type": "string"}}, ["target"]),
    },
    {
        "name": "send_message",
        "description": "Write a message and prepare delivery to the target Codex session.",
        "inputSchema": json_schema(
            {
                "target": {"type": "string"},
                "message": {"type": "string"},
                "from_agent": {"type": "string"},
                "trigger": {"type": "string", "enum": ["queue", "codex_app", "resume", "subagent_tool"]},
                "wait": {"type": "boolean"},
                "timeout_sec": {"type": "number"},
                "correlation_id": {"type": "string"},
                "hop_count": {"type": "number"},
                "allow_pending": {"type": "boolean"},
            },
            ["target", "message"],
        ),
    },
    {
        "name": "create_team",
        "description": "Create a project Agent Bus team with role aliases and pending bootstrap tasks for current or future Codex sessions.",
        "inputSchema": json_schema(
            {
                "name": {"type": "string"},
                "project": {"type": "string"},
                "goal": {"type": "string"},
                "roles": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "alias": {"type": "string"},
                            "capabilities": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["name"],
                        "additionalProperties": False,
                    },
                },
                "from_agent": {"type": "string"},
            },
            ["name", "project", "goal"],
        ),
    },
    {
        "name": "list_teams",
        "description": "List Agent Bus teams.",
        "inputSchema": json_schema({}),
    },
    {
        "name": "show_team",
        "description": "Show one Agent Bus team by id, name, or slug.",
        "inputSchema": json_schema({"team": {"type": "string"}}, ["team"]),
    },
    {
        "name": "join_team",
        "description": "Attach an existing registered agent to a team role and claim that role's pending bootstrap message if present.",
        "inputSchema": json_schema(
            {
                "team": {"type": "string"},
                "role": {"type": "string"},
                "agent": {"type": "string"},
            },
            ["team", "role", "agent"],
        ),
    },
    {
        "name": "launch_team",
        "description": "Prepare subagent spawn requests or launch prompts for team roles, or experimentally create app-server threads for roles and attach them to the team.",
        "inputSchema": json_schema(
            {
                "team": {"type": "string"},
                "role": {"type": "string"},
                "mode": {"type": "string", "enum": ["subagent-tool", "prompt", "app-server-experimental"]},
                "from_agent": {"type": "string"},
                "timeout_sec": {"type": "number"},
                "deliver_bootstrap": {"type": "boolean"},
            },
            ["team"],
        ),
    },
    {
        "name": "attach_team_thread",
        "description": "Bind an existing Codex thread/session id to a team role and prepare visible delivery of the role bootstrap prompt.",
        "inputSchema": json_schema(
            {
                "team": {"type": "string"},
                "role": {"type": "string"},
                "thread_id": {"type": "string"},
                "session_id": {"type": "string"},
                "agent_name": {"type": "string"},
                "cwd": {"type": "string"},
                "from_agent": {"type": "string"},
            },
            ["team", "role"],
        ),
    },
    {
        "name": "dispatch_team_task",
        "description": "Dispatch or rebalance a task to a team role. Uses the assigned agent when present, otherwise queues for the role alias.",
        "inputSchema": json_schema(
            {
                "team": {"type": "string"},
                "role": {"type": "string"},
                "message": {"type": "string"},
                "from_agent": {"type": "string"},
                "trigger": {"type": "string", "enum": ["queue", "codex_app", "resume", "subagent_tool"]},
            },
            ["team", "role", "message"],
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
                "trigger": {"type": "string", "enum": ["queue", "codex_app", "resume", "subagent_tool"]},
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
    thread_launcher: Optional[CodexThreadStartTransport] = None,
) -> Dict[str, Any]:
    args = arguments or {}
    store = store or AgentStore()
    transport = transport or CodexResumeTransport()
    thread_launcher = thread_launcher or CodexThreadStartTransport()
    if name == "register_agent":
        session_id = args.get("session_id") or os.environ.get("CODEX_SESSION_ID")
        if not session_id:
            raise AgentBusError(
                "session_id is required. Use Codex /status or SessionStart hook auto-registration."
            )
        agent = store.upsert_agent(
            name=args.get("name") or "",
            role=args.get("role") or "",
            session_id=session_id,
            cwd=args.get("cwd") or os.environ.get("PWD") or os.getcwd(),
            status=args.get("status") or "idle",
            capabilities=args.get("capabilities"),
            tags=args.get("tags"),
        )
        claimed = store.claim_pending_messages(agent)
        return {"agent": agent, "claimed_messages": claimed, "claimed_count": len(claimed)}
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
    if name == "create_team":
        return create_team(store, args)
    if name == "list_teams":
        return {"teams": store.list_teams()}
    if name == "show_team":
        return {"team": store.resolve_team(args["team"])}
    if name == "join_team":
        return join_team(store, args)
    if name == "launch_team":
        return launch_team(store, transport, thread_launcher, args)
    if name == "attach_team_thread":
        return attach_team_thread(store, args)
    if name == "dispatch_team_task":
        return dispatch_team_task(store, transport, args)
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
    pending_target = False
    try:
        target = store.resolve_agent(args["target"])
    except NotFoundError:
        if not bool(args.get("allow_pending", False)):
            raise
        pending_target = True
        target = {
            "agent_id": None,
            "session_id": None,
            "name": args["target"],
            "cwd": None,
            "pending_target": True,
        }
    from_agent = resolve_from_agent(store, args.get("from_agent"))
    hop_count = int(args.get("hop_count") or 0)
    if hop_count > MAX_HOP_COUNT:
        raise AgentBusError("Refusing to trigger resume: hop_count %s exceeds %s" % (hop_count, MAX_HOP_COUNT))
    trigger = args.get("trigger") or "codex_app"
    correlation_id = args.get("correlation_id")
    message = store.append_message(
        {
            "correlation_id": correlation_id,
            "from_agent_id": from_agent.get("agent_id"),
            "from_session_id": from_agent.get("session_id"),
            "to_agent_id": target.get("agent_id"),
            "to_session_id": target.get("session_id"),
            "to_name": target.get("name") or args["target"],
            "target_query": args["target"],
            "pending_target": pending_target,
            "trigger": trigger,
            "hop_count": hop_count,
            "body": args["message"],
            "status": "pending_target" if pending_target else "queued",
            "message_type": "request",
        }
    )
    transport_result = None
    if pending_target:
        return {
            "message_id": message["message_id"],
            "correlation_id": message["correlation_id"],
            "target": target,
            "message": message,
            "transport": pending_target_transport(args["target"], trigger),
            "reply": None,
        }
    prompt = build_request_prompt(from_agent, target, message)
    if trigger == "codex_app":
        transport_result = codex_app_delivery(target, prompt)
        message = store.update_message(
            message["message_id"],
            {"status": "prepared", "prepared_at": utc_now()},
        )
    elif trigger == "subagent_tool":
        transport_result = subagent_tool_delivery(target, prompt)
        message = store.update_message(
            message["message_id"],
            {"status": "prepared", "prepared_at": utc_now()},
        )
    elif trigger == "resume":
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
    if bool(args.get("wait", False)) and trigger != "codex_app":
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
        "transport": transport_to_dict(transport_result),
        "reply": reply,
    }


def create_team(store: AgentStore, args: Dict[str, Any]) -> Dict[str, Any]:
    from_agent = resolve_from_agent(store, args.get("from_agent"))
    roles = normalize_team_roles(args.get("roles"))
    team = store.create_team(
        name=args["name"],
        project=args["project"],
        goal=args["goal"],
        roles=roles,
        created_by=from_agent,
    )
    messages: List[Dict[str, Any]] = []
    launch_prompts: List[Dict[str, Any]] = []
    for role_name, role in team["roles"].items():
        target = maybe_resolve_agent(store, role["alias"])
        prompt = build_team_role_prompt(team, role, from_agent)
        message = store.append_message(
            {
                "correlation_id": team["team_id"],
                "from_agent_id": from_agent.get("agent_id"),
                "from_session_id": from_agent.get("session_id"),
                "to_agent_id": target.get("agent_id"),
                "to_session_id": target.get("session_id"),
                "to_name": target.get("name") or role["alias"],
                "target_query": role["alias"],
                "pending_target": not bool(target.get("session_id")),
                "trigger": "queue",
                "hop_count": 0,
                "body": prompt,
                "status": "queued" if target.get("session_id") else "pending_target",
                "message_type": "request",
                "team_id": team["team_id"],
                "team_role": role_name,
                "team_role_alias": role["alias"],
            }
        )
        team = store.attach_team_role_message(team["team_id"], role_name, message["message_id"])
        if target.get("session_id"):
            team = store.assign_agent_to_team_role(team["team_id"], role_name, target, message_id=message["message_id"])
        messages.append(message)
        launch_prompts.append(build_launch_prompt(team, role, message))
    team["launch_prompts"] = launch_prompts
    team = store.update_team(team)
    return {
        "team": team,
        "messages": messages,
        "launch_prompts": launch_prompts,
        "thread_creation": manual_thread_creation_boundary(),
    }


def join_team(store: AgentStore, args: Dict[str, Any]) -> Dict[str, Any]:
    team = store.resolve_team(args["team"])
    role_name = normalize_role_name(args["role"])
    role = team.get("roles", {}).get(role_name)
    if not role:
        raise NotFoundError("No role %r in team %r" % (role_name, team.get("team_id")))
    agent = store.resolve_agent(args["agent"], include_disabled=True)
    claimed_message = None
    if role.get("pending_message_id"):
        claimed_message = store.assign_message_to_agent(str(role["pending_message_id"]), agent)
    team = store.assign_agent_to_team_role(team["team_id"], role_name, agent, message_id=role.get("pending_message_id"))
    return {"team": team, "agent": agent, "claimed_message": claimed_message}


def launch_team(
    store: AgentStore,
    transport: CodexResumeTransport,
    thread_launcher: CodexThreadStartTransport,
    args: Dict[str, Any],
) -> Dict[str, Any]:
    team = store.resolve_team(args["team"])
    mode = args.get("mode") or "prompt"
    from_agent = resolve_from_agent(store, args.get("from_agent"))
    role_items = selected_team_roles(team, args.get("role"))
    launches: List[Dict[str, Any]] = []
    if mode == "prompt":
        for role_name, role in role_items:
            message = role_message_or_empty(role)
            prompt = build_launch_prompt(team, role, message)
            launch_status = "joined" if role.get("status") == "active" else "pending_manual_launch"
            team = store.update_team_role_launch(
                team["team_id"],
                role_name,
                {
                    "launch_status": launch_status,
                    "launch_mode": "prompt",
                    "launch_prompt": prompt["prompt"],
                    "last_launch_at": utc_now(),
                },
                event={"mode": "prompt", "status": launch_status},
            )
            launches.append(
                {
                    "role": role_name,
                    "alias": role.get("alias"),
                    "status": "prompt_ready",
                    "launch_status": launch_status,
                    "launch_prompt": prompt,
                }
            )
        return {
            "team": store.resolve_team(team["team_id"]),
            "launches": launches,
            "thread_creation": manual_thread_creation_boundary(),
        }
    if mode == "subagent-tool":
        for role_name, role in role_items:
            prompt = build_subagent_spawn_prompt(team, role)
            spawn_request = build_subagent_spawn_request(team, role, prompt)
            team = store.update_team_role_launch(
                team["team_id"],
                role_name,
                {
                    "launch_status": "spawn_tool_required",
                    "launch_mode": "subagent-tool",
                    "launch_prompt": prompt,
                    "last_launch_at": utc_now(),
                    "spawn_request": spawn_request,
                },
                event={"mode": "subagent-tool", "status": "spawn_tool_required"},
            )
            launches.append(
                {
                    "role": role_name,
                    "alias": role.get("alias"),
                    "status": "spawn_tool_required",
                    "spawn_request": spawn_request,
                    "next_step": (
                        "Call multi_agent_v1.spawn_agent with spawn_request, then call "
                        "attach_team_thread using the returned agent_id as thread_id."
                    ),
                }
            )
        return {
            "team": store.resolve_team(team["team_id"]),
            "launches": launches,
            "thread_creation": {
                "status": "subagent_tool_required",
                "visibility": "created_after_spawn_agent",
                "reason": (
                    "The local Agent Bus CLI cannot call Codex tools by itself. A Codex controller "
                    "should execute each returned multi_agent_v1.spawn_agent request and attach "
                    "the returned agent_id to the role."
                ),
            },
        }
    if mode != "app-server-experimental":
        raise AgentBusError("Unsupported launch mode %r" % mode)
    for role_name, role in role_items:
        if role.get("status") == "active" and (role.get("thread_id") or role.get("session_id")):
            launches.append(
                {
                    "role": role_name,
                    "alias": role.get("alias"),
                    "status": "already_active",
                    "thread_id": role.get("thread_id") or role.get("session_id"),
                }
            )
            continue
        start_result = thread_launcher.start_thread(
            cwd=str(team.get("project") or os.getcwd()),
            timeout_sec=float(args.get("timeout_sec") or 60),
        )
        if not start_result.get("ok") or not start_result.get("thread_id"):
            team = store.update_team_role_launch(
                team["team_id"],
                role_name,
                {
                    "launch_status": "thread_creation_failed",
                    "launch_mode": mode,
                    "last_launch_at": utc_now(),
                    "last_launch_error": start_result.get("error") or start_result.get("status"),
                },
                event={"mode": mode, "status": "thread_creation_failed", "result": scrub_transport_result(start_result)},
            )
            launches.append(
                {
                    "role": role_name,
                    "alias": role.get("alias"),
                    "status": "thread_creation_failed",
                    "thread_start": start_result,
                }
            )
            continue
        attach = attach_role_to_thread(
            store,
            team,
            role_name,
            str(start_result["thread_id"]),
            from_agent=from_agent,
            launch_mode=mode,
            launch_status="thread_created_unverified_visibility",
            prepare_visible_delivery=not bool(args.get("deliver_bootstrap", False)),
        )
        delivery_result = None
        if bool(args.get("deliver_bootstrap", False)) and attach.get("claimed_message"):
            claimed_message = attach["claimed_message"]
            prompt = build_request_prompt(from_agent, attach["agent"], claimed_message)
            delivery_result = transport.send(
                session_id=str(start_result["thread_id"]),
                cwd=attach["agent"].get("cwd") or str(team.get("project") or os.getcwd()),
                prompt=prompt,
                timeout_sec=float(args.get("timeout_sec") or 60),
            )
            message_updates = (
                {"status": "delivered", "delivered_at": utc_now()}
                if delivery_result.ok
                else {"status": delivery_result.status, "error": delivery_result.error}
            )
            attach["claimed_message"] = store.update_message(claimed_message["message_id"], message_updates)
            launch_status = (
                "bootstrap_delivered_unverified_visibility"
                if delivery_result.ok
                else "bootstrap_delivery_failed"
            )
            team = store.update_team_role_launch(
                team["team_id"],
                role_name,
                {
                    "launch_status": launch_status,
                    "visible_delivery_status": delivery_result.status,
                    "last_launch_at": utc_now(),
                },
                event={
                    "mode": mode,
                    "status": launch_status,
                    "result": delivery_result.to_dict(),
                },
            )
        launches.append(
            {
                "role": role_name,
                "alias": role.get("alias"),
                "status": "thread_created_unverified_visibility",
                "thread_start": start_result,
                "attach": attach,
                "bootstrap_delivery": transport_to_dict(delivery_result),
            }
        )
        team = store.resolve_team(team["team_id"])
    return {
        "team": store.resolve_team(team["team_id"]),
        "launches": launches,
        "thread_creation": {
            "status": "experimental_thread_start_used",
            "visibility": "unverified",
            "reason": (
                "app-server thread/start returned a thread id, but this tool cannot prove "
                "the thread is visible in the Codex App without a separate visible-thread ACK."
            ),
        },
    }


def attach_team_thread(store: AgentStore, args: Dict[str, Any]) -> Dict[str, Any]:
    team = store.resolve_team(args["team"])
    role_name = normalize_role_name(args["role"])
    thread_id = args.get("thread_id") or args.get("session_id")
    if not thread_id:
        raise AgentBusError("thread_id or session_id is required")
    return attach_role_to_thread(
        store,
        team,
        role_name,
        str(thread_id),
        agent_name=args.get("agent_name"),
        cwd=args.get("cwd"),
        from_agent=resolve_from_agent(store, args.get("from_agent")),
        launch_mode="attach-thread",
        launch_status="attached_existing_thread",
        prepare_visible_delivery=True,
    )


def attach_role_to_thread(
    store: AgentStore,
    team: Dict[str, Any],
    role_name: str,
    thread_id: str,
    agent_name: Optional[str] = None,
    cwd: Optional[str] = None,
    from_agent: Optional[Dict[str, Any]] = None,
    launch_mode: str = "attach-thread",
    launch_status: str = "attached_existing_thread",
    prepare_visible_delivery: bool = True,
) -> Dict[str, Any]:
    role = team.get("roles", {}).get(role_name)
    if not role:
        raise NotFoundError("No role %r in team %r" % (role_name, team.get("team_id")))
    agent = store.upsert_agent(
        name=agent_name or role.get("alias") or role_name,
        role=role.get("description") or ("Team role %s" % role_name),
        session_id=thread_id,
        cwd=cwd or team.get("project") or os.getcwd(),
        status="idle",
        capabilities=role.get("capabilities"),
        tags=["agent-bus-team", str(team.get("team_id")), role_name],
        metadata={
            "team_id": team.get("team_id"),
            "team_role": role_name,
            "team_role_alias": role.get("alias"),
            "thread_attached_by": "agent_bus",
        },
    )
    claimed_message = None
    delivery = None
    if role.get("pending_message_id"):
        claimed_message = store.assign_message_to_agent(str(role["pending_message_id"]), agent)
    team = store.assign_agent_to_team_role(
        str(team["team_id"]),
        role_name,
        agent,
        message_id=role.get("pending_message_id"),
    )
    if prepare_visible_delivery and claimed_message:
        prompt = build_request_prompt(from_agent or resolve_from_agent(store, None), agent, claimed_message)
        delivery = codex_app_delivery(agent, prompt)
        claimed_message = store.update_message(
            claimed_message["message_id"],
            {"status": "prepared", "prepared_at": utc_now()},
        )
    team = store.update_team_role_launch(
        str(team["team_id"]),
        role_name,
        {
            "launch_status": launch_status,
            "launch_mode": launch_mode,
            "thread_id": thread_id,
            "last_launch_at": utc_now(),
            "visible_delivery_status": (delivery or {}).get("status"),
        },
        event={
            "mode": launch_mode,
            "status": launch_status,
            "thread_id": thread_id,
            "visible_delivery_status": (delivery or {}).get("status"),
        },
    )
    return {
        "team": team,
        "agent": agent,
        "claimed_message": claimed_message,
        "visible_delivery": delivery,
        "thread_creation": (
            manual_thread_creation_boundary()
            if launch_mode == "attach-thread"
            else {
                "status": "experimental_thread_start_used",
                "visibility": "unverified",
            }
        ),
    }


def dispatch_team_task(
    store: AgentStore,
    transport: CodexResumeTransport,
    args: Dict[str, Any],
) -> Dict[str, Any]:
    team = store.resolve_team(args["team"])
    role_name = normalize_role_name(args["role"])
    role = team.get("roles", {}).get(role_name)
    if not role:
        raise NotFoundError("No role %r in team %r" % (role_name, team.get("team_id")))
    target = role.get("session_id") or role.get("agent_id") or role.get("alias")
    result = send_message(
        store,
        transport,
        {
            "target": target,
            "message": build_team_task_prompt(team, role, args["message"]),
            "from_agent": args.get("from_agent"),
            "trigger": args.get("trigger") or "queue",
            "allow_pending": True,
            "correlation_id": team["team_id"],
        },
    )
    result["message"] = store.update_message(
        result["message_id"],
        {
            "team_id": team["team_id"],
            "team_role": role_name,
            "team_role_alias": role.get("alias"),
        },
    )
    store.attach_team_role_message(team["team_id"], role_name, result["message_id"], assignment_type="dispatch")
    return {"team": store.resolve_team(team["team_id"]), "dispatch": result}


def normalize_team_roles(value: Any) -> List[Dict[str, Any]]:
    roles = value or DEFAULT_TEAM_ROLES
    normalized: List[Dict[str, Any]] = []
    for role in roles:
        if isinstance(role, str):
            name, _, description = role.partition(":")
            normalized.append({"name": name.strip(), "description": description.strip()})
        elif isinstance(role, dict):
            normalized.append(dict(role))
        else:
            raise AgentBusError("Invalid team role %r" % (role,))
    return normalized


def normalize_role_name(value: str) -> str:
    normalized = "-".join(str(value).lower().replace("_", "-").split())
    return normalized


def selected_team_roles(
    team: Dict[str, Any],
    role_filter: Optional[str],
) -> List[Tuple[str, Dict[str, Any]]]:
    roles = team.get("roles") or {}
    if role_filter:
        role_name = normalize_role_name(role_filter)
        role = roles.get(role_name)
        if not role:
            raise NotFoundError("No role %r in team %r" % (role_name, team.get("team_id")))
        return [(role_name, role)]
    return [(str(role_name), role) for role_name, role in roles.items()]


def role_message_or_empty(role: Dict[str, Any]) -> Dict[str, Any]:
    return {"message_id": role.get("pending_message_id")}


def manual_thread_creation_boundary() -> Dict[str, Any]:
    return {
        "status": "manual_or_external_api_required",
        "visibility": "not_created_by_agent_bus",
        "reason": (
            "Use the returned launch prompt in a new Codex App conversation, or provide an "
            "existing thread/session id with attach_team_thread."
        ),
    }


def scrub_transport_result(value: Dict[str, Any]) -> Dict[str, Any]:
    scrubbed = dict(value)
    if "stdout" in scrubbed and isinstance(scrubbed["stdout"], str):
        scrubbed["stdout"] = scrubbed["stdout"][-1000:]
    if "stderr" in scrubbed and isinstance(scrubbed["stderr"], str):
        scrubbed["stderr"] = scrubbed["stderr"][-1000:]
    return scrubbed


def maybe_resolve_agent(store: AgentStore, target: str) -> Dict[str, Any]:
    try:
        return store.resolve_agent(target, include_disabled=True)
    except AgentBusError:
        return {"agent_id": None, "session_id": None, "name": target, "cwd": None}


def build_team_role_prompt(team: Dict[str, Any], role: Dict[str, Any], from_agent: Dict[str, Any]) -> str:
    del from_agent
    return "\n".join(
        [
            "你是 Agent Bus 团队成员：%s" % role.get("alias"),
            "",
            "团队信息：",
            "- team_id: %s" % team.get("team_id"),
            "- project: %s" % team.get("project"),
            "- goal: %s" % team.get("goal"),
            "- role: %s" % role.get("name"),
            "- role_description: %s" % (role.get("description") or ""),
            "",
            "启动步骤：",
            "1. 确认 cwd 与 git status，不要覆盖其它人的改动。",
            "2. 读取项目 AGENTS.md / README / docs 中和任务相关的规则。",
            "3. 只在你的角色边界内工作；需要跨边界时通过 Agent Bus 回报 NEEDS_CONTEXT。",
            "4. 完成后 reply_message(message_id=<原消息>, result=<JSON/摘要>)。",
            "",
            "团队目标：",
            str(team.get("goal") or ""),
        ]
    )


def build_team_task_prompt(team: Dict[str, Any], role: Dict[str, Any], body: str) -> str:
    return "\n".join(
        [
            "Agent Bus team task",
            "",
            "team_id: %s" % team.get("team_id"),
            "project: %s" % team.get("project"),
            "role: %s" % role.get("name"),
            "role_alias: %s" % role.get("alias"),
            "",
            "任务：",
            str(body),
            "",
            "完成后用 reply_message 回传 status / files_changed / checks / risks。",
        ]
    )


def build_subagent_spawn_prompt(team: Dict[str, Any], role: Dict[str, Any]) -> str:
    return "\n".join(
        [
            "你是 Agent Bus 团队里的 %s。" % role.get("name"),
            "",
            "团队绑定信息：",
            "- team_id: %s" % team.get("team_id"),
            "- project: %s" % team.get("project"),
            "- role: %s" % role.get("name"),
            "- role_alias: %s" % role.get("alias"),
            "- role_description: %s" % (role.get("description") or ""),
            "",
            "启动规则：",
            "1. 你不是单独行动；父对话会把 spawn_agent 返回的 agent_id 作为 thread/session id 写入 Agent Bus。",
            "2. 如果你要读 Bus 任务，等待父对话 attach-thread 后再查 inbox；不要臆造自己的 id。",
            "3. 先确认 cwd / git status / AGENTS.md，再按角色边界工作。",
            "4. 完成任务时用 Agent Bus reply_message 回传 status / files_changed / checks / risks。",
            "",
            "团队目标：",
            str(team.get("goal") or ""),
        ]
    )


def build_subagent_spawn_request(
    team: Dict[str, Any],
    role: Dict[str, Any],
    prompt: str,
) -> Dict[str, Any]:
    role_name = str(role.get("name") or "")
    agent_type = "worker" if role_name in {"executor", "tester", "reviewer"} else "default"
    return {
        "tool": "multi_agent_v1.spawn_agent",
        "agent_type": agent_type,
        "fork_context": False,
        "message": prompt,
        "attach_after_spawn": {
            "team": team.get("team_id"),
            "role": role_name,
            "thread_id_source": "spawn_agent.agent_id",
            "command": (
                "agent-bus team attach-thread %s --role %s --thread-id <spawn_agent.agent_id>"
                % (team.get("team_id"), role_name)
            ),
        },
    }


def build_launch_prompt(team: Dict[str, Any], role: Dict[str, Any], message: Dict[str, Any]) -> Dict[str, Any]:
    text = "\n".join(
        [
            "请在这个 Codex 会话中加入 Agent Bus 团队。",
            "",
            "执行：",
            "python3 ~/.codex/skills/agent-bus-register/scripts/register_self.py \\",
            "  --name %s \\" % role.get("alias"),
            "  --role %r \\" % (role.get("description") or ("Team role %s" % role.get("name"))),
            "  --tag agent-bus-team \\",
            "  --tag %s" % team.get("team_id"),
            "",
            "然后读取：",
            "~/.codex/tools/codex-agent-bus/bin/agent-bus inbox --target <你的 session_id> --unread-only --limit 10",
            "",
            "你应该会领取 message_id: %s" % message.get("message_id"),
            "team_id: %s" % team.get("team_id"),
            "role_alias: %s" % role.get("alias"),
        ]
    )
    return {
        "role": role.get("name"),
        "alias": role.get("alias"),
        "message_id": message.get("message_id"),
        "prompt": text,
    }


def pending_target_transport(target: str, trigger: str) -> Dict[str, Any]:
    return {
        "ok": False,
        "status": "pending_target",
        "surface": "agent_bus_pending_target",
        "target": target,
        "trigger": trigger,
        "next_step": (
            "Open or register a Codex session with this Agent Bus name. "
            "Registration will claim the queued message; then run inbox --target %r."
        )
        % target,
    }


def reply_message(
    store: AgentStore,
    transport: CodexResumeTransport,
    args: Dict[str, Any],
) -> Dict[str, Any]:
    original = store.find_message(args["message_id"])
    source_target = original.get("from_session_id") or original.get("from_agent_id")
    if not source_target:
        raise AgentBusError("Original message has no source agent/session to reply to")
    source = store.resolve_agent(source_target, include_disabled=True)
    from_agent = resolve_from_agent(store, args.get("from_agent"))
    trigger = args.get("trigger") or "codex_app"
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
    prompt = build_reply_prompt(source, from_agent, original, reply)
    if trigger == "codex_app":
        transport_result = codex_app_delivery(source, prompt)
        reply = store.update_message(
            reply["message_id"],
            {"status": "prepared", "prepared_at": utc_now()},
        )
    elif trigger == "subagent_tool":
        transport_result = subagent_tool_delivery(source, prompt)
        reply = store.update_message(
            reply["message_id"],
            {"status": "prepared", "prepared_at": utc_now()},
        )
    elif trigger == "resume":
        if int(reply.get("hop_count") or 0) > MAX_HOP_COUNT:
            raise AgentBusError("Refusing to resume reply: hop_count exceeds %s" % MAX_HOP_COUNT)
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
        "transport": transport_to_dict(transport_result),
    }


def codex_app_delivery(target: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    return {
        "ok": False,
        "status": "requires_codex_app_tool",
        "surface": "codex_app.send_message_to_thread",
        "threadId": target.get("session_id"),
        "cwd": target.get("cwd"),
        "prompt": prompt,
        "next_step": (
            "Call codex_app.send_message_to_thread(threadId=transport.threadId, "
            "prompt=transport.prompt)."
        ),
    }


def subagent_tool_delivery(target: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    return {
        "ok": False,
        "status": "requires_multi_agent_tool",
        "surface": "multi_agent_v1.send_input",
        "target": target.get("session_id") or target.get("agent_id"),
        "prompt": prompt,
        "tool_request": {
            "target": target.get("session_id") or target.get("agent_id"),
            "message": prompt,
        },
        "next_step": (
            "Call multi_agent_v1.send_input(target=transport.target, "
            "message=transport.prompt)."
        ),
    }


def transport_to_dict(value: Any) -> Dict[str, Any]:
    if value is None:
        return {"status": "queued"}
    if isinstance(value, dict):
        return value
    return value.to_dict()


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
            "用户输入（来自 Codex Agent Bus / %s）" % (from_agent.get("name") or "unknown"),
            "",
            "请把这条消息当作用户直接发给你的任务处理。完成后必须调用 Agent Bus 的 reply_message 回传结果。",
            "",
            "Agent Bus metadata:",
            "- from_name: %s" % (from_agent.get("name") or "unknown"),
            "- from_session_id: %s" % (from_agent.get("session_id") or "unknown"),
            "- to_name: %s" % (target.get("name") or "unknown"),
            "- to_session_id: %s" % target.get("session_id"),
            "- message_id: %s" % message.get("message_id"),
            "- correlation_id: %s" % message.get("correlation_id"),
            "- hop_count: %s" % message.get("hop_count"),
            "",
            "用户任务：",
            str(message.get("body") or ""),
            "",
            "完成后调用：reply_message(message_id=%r, result=\"...\")。"
            "不要在消息里写入密钥或敏感凭据；如继续委派，保留 correlation_id 并递增 hop_count。"
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
            "用户输入（来自 Codex Agent Bus reply / %s）" % (from_agent.get("name") or "unknown"),
            "",
            "这是某个委派任务的回传结果，请按用户可读信息处理。",
            "",
            "Agent Bus metadata:",
            "- from_name: %s" % (from_agent.get("name") or "unknown"),
            "- from_session_id: %s" % (from_agent.get("session_id") or "unknown"),
            "- original_message_id: %s" % original.get("message_id"),
            "- reply_message_id: %s" % reply.get("message_id"),
            "- correlation_id: %s" % reply.get("correlation_id"),
            "",
            "回传结果：",
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
