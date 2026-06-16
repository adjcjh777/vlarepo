"""Throwaway loop-engineering prototype core.

Question this prototype answers:
Can we make an agent loop explicit enough that the goal, current work,
verification signal, retry policy, and stopping condition are all visible
instead of hidden inside a long prompt?

This module is intentionally pure: no terminal I/O and no filesystem writes.
The TUI imports it and drives actions by hand.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Literal


TaskStatus = Literal["open", "in_progress", "needs_repair", "done", "blocked"]
LoopStatus = Literal["idle", "running", "done", "blocked"]
ActionName = Literal[
    "discover",
    "start",
    "agent_step",
    "verify_pass",
    "verify_fail",
    "block",
    "reset",
]


DEFAULT_GOAL = (
    "每天扫描一个工程项目的待办、失败信号和最近变更；"
    "选择一个可验证的小任务；让 maker 产出修改；"
    "让 checker 用测试或证据验收；把结果写回状态。"
)


SEED_TASKS = [
    (
        "ci-triage",
        "梳理最近一次 CI 失败，判断是否存在可自动修复的小问题",
        "scheduled_discovery",
    ),
    (
        "docs-drift",
        "检查 README/AGENTS 与当前脚本是否出现命令漂移",
        "repo_audit",
    ),
    (
        "smoke-gap",
        "为一个已有功能补一条最小 smoke 验证命令",
        "quality_gate",
    ),
]


@dataclass
class Task:
    id: str
    title: str
    source: str
    status: TaskStatus = "open"
    attempts: int = 0
    max_attempts: int = 2
    observations: list[str] = field(default_factory=list)
    verifier_notes: list[str] = field(default_factory=list)


@dataclass
class LoopState:
    goal: str = DEFAULT_GOAL
    status: LoopStatus = "idle"
    iteration: int = 0
    max_iterations: int = 8
    current_task_id: str | None = None
    tasks: list[Task] = field(default_factory=list)
    events: list[str] = field(default_factory=lambda: ["loop initialized"])


def initial_state() -> LoopState:
    return LoopState()


def dispatch(state: LoopState, action: ActionName) -> LoopState:
    next_state = deepcopy(state)

    if action == "reset":
        return initial_state()

    if action == "discover":
        return _discover(next_state)

    if action == "start":
        return _start_next(next_state)

    if action == "agent_step":
        return _agent_step(next_state)

    if action == "verify_pass":
        return _verify_pass(next_state)

    if action == "verify_fail":
        return _verify_fail(next_state)

    if action == "block":
        return _block_current(next_state)

    next_state.events.append(f"unknown action ignored: {action}")
    return next_state


def current_task(state: LoopState) -> Task | None:
    if state.current_task_id is None:
        return None
    for task in state.tasks:
        if task.id == state.current_task_id:
            return task
    return None


def maker_prompt(state: LoopState) -> str:
    task = current_task(state)
    if task is None:
        return "No active task. Press [s] to start the next open task."

    return "\n".join(
        [
            "你是 maker agent。只处理这个小任务，不顺手重构。",
            "",
            f"Loop goal: {state.goal}",
            f"Task: {task.title}",
            f"Source: {task.source}",
            "",
            "Required loop discipline:",
            "1. 先确认 cwd 与 git status。",
            "2. 找到最小相关文件和验证命令。",
            "3. 只做一个 coherent change。",
            "4. 跑能证明该任务的最小验证。",
            "5. 汇报 diff、验证结果、残余风险。",
        ]
    )


def checker_prompt(state: LoopState) -> str:
    task = current_task(state)
    if task is None:
        return "No active task. Press [s] to start the next open task."

    return "\n".join(
        [
            "你是 checker agent。你的职责是拒绝不充分的完成声明。",
            "",
            f"Task under review: {task.title}",
            f"Attempts: {task.attempts}/{task.max_attempts}",
            "",
            "Check these gates:",
            "- 修改是否只覆盖任务范围？",
            "- 是否有真实验证输出，而不是口头声称？",
            "- 是否把失败、阻塞、未测风险说清楚？",
            "- 如果证据不足，返回 verify_fail，并给出下一轮修复方向。",
        ]
    )


def summary(state: LoopState) -> dict[str, int | str | None]:
    return {
        "status": state.status,
        "iteration": state.iteration,
        "max_iterations": state.max_iterations,
        "current_task_id": state.current_task_id,
        "open": sum(1 for task in state.tasks if task.status == "open"),
        "in_progress": sum(1 for task in state.tasks if task.status == "in_progress"),
        "needs_repair": sum(1 for task in state.tasks if task.status == "needs_repair"),
        "done": sum(1 for task in state.tasks if task.status == "done"),
        "blocked": sum(1 for task in state.tasks if task.status == "blocked"),
    }


def _discover(state: LoopState) -> LoopState:
    existing_ids = {task.id for task in state.tasks}
    added = 0
    for task_id, title, source in SEED_TASKS:
        if task_id not in existing_ids:
            state.tasks.append(Task(id=task_id, title=title, source=source))
            added += 1
    state.status = "idle" if state.current_task_id is None else "running"
    state.events.append(f"discovered {added} task(s)")
    return state


def _start_next(state: LoopState) -> LoopState:
    if state.current_task_id is not None:
        state.events.append("start ignored: a task is already active")
        return state

    if state.iteration >= state.max_iterations:
        state.status = "blocked"
        state.events.append("loop blocked: iteration budget exhausted")
        return state

    for task in state.tasks:
        if task.status in ("open", "needs_repair"):
            task.status = "in_progress"
            state.current_task_id = task.id
            state.iteration += 1
            state.status = "running"
            state.events.append(f"started task {task.id}")
            return state

    state.status = "done"
    state.events.append("no open tasks; loop is done")
    return state


def _agent_step(state: LoopState) -> LoopState:
    task = current_task(state)
    if task is None:
        state.events.append("agent step ignored: no active task")
        return state

    task.attempts += 1
    task.observations.append(
        f"maker attempt {task.attempts}: drafted a minimal change and verification claim"
    )
    state.events.append(f"maker produced attempt {task.attempts} for {task.id}")
    return state


def _verify_pass(state: LoopState) -> LoopState:
    task = current_task(state)
    if task is None:
        state.events.append("verify pass ignored: no active task")
        return state

    if task.attempts == 0:
        state.events.append("verify pass ignored: maker has not produced an attempt")
        return state

    task.status = "done"
    task.verifier_notes.append("checker accepted: evidence is sufficient")
    state.events.append(f"task {task.id} accepted")
    state.current_task_id = None
    state.status = "idle"
    return state


def _verify_fail(state: LoopState) -> LoopState:
    task = current_task(state)
    if task is None:
        state.events.append("verify fail ignored: no active task")
        return state

    if task.attempts >= task.max_attempts:
        task.status = "blocked"
        task.verifier_notes.append("checker rejected: retry budget exhausted")
        state.events.append(f"task {task.id} blocked after failed verification")
        state.current_task_id = None
        state.status = "blocked"
        return state

    task.status = "needs_repair"
    task.verifier_notes.append("checker rejected: evidence or scope is insufficient")
    state.events.append(f"task {task.id} needs repair")
    state.current_task_id = None
    state.status = "idle"
    return state


def _block_current(state: LoopState) -> LoopState:
    task = current_task(state)
    if task is None:
        state.status = "blocked"
        state.events.append("loop manually blocked with no active task")
        return state

    task.status = "blocked"
    task.verifier_notes.append("manual block: needs human decision")
    state.events.append(f"task {task.id} manually blocked")
    state.current_task_id = None
    state.status = "blocked"
    return state
