"""Interactive terminal shell for the loop-engineering prototype.

Run from the workspace root:
    python3 outputs/loop_engineering_kit/loop_tui.py
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict

from loop_core import checker_prompt, dispatch, initial_state, maker_prompt, summary


BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


KEYS = {
    "d": ("discover", "发现/补充待办"),
    "s": ("start", "启动下一个任务"),
    "a": ("agent_step", "模拟 maker 一轮产出"),
    "p": ("verify_pass", "checker 通过"),
    "f": ("verify_fail", "checker 驳回"),
    "b": ("block", "人工阻塞"),
    "r": ("reset", "重置原型"),
    "q": ("quit", "退出"),
}


def clear() -> None:
    print("\033[2J\033[H", end="")


def render(state) -> None:
    clear()
    print(f"{BOLD}Loop Engineering Prototype{RESET}")
    print(f"{DIM}Throwaway TUI: state is in memory only.{RESET}\n")

    print(f"{BOLD}Goal{RESET}")
    print(state.goal)
    print()

    print(f"{BOLD}Summary{RESET}")
    print(json.dumps(summary(state), ensure_ascii=False, indent=2))
    print()

    print(f"{BOLD}Tasks{RESET}")
    if not state.tasks:
        print(f"{DIM}No tasks yet. Press [d] to discover seed tasks.{RESET}")
    for task in state.tasks:
        marker = "*" if task.id == state.current_task_id else "-"
        print(
            f"{marker} {task.id}: {task.status} "
            f"(attempts {task.attempts}/{task.max_attempts})"
        )
        print(f"  {task.title}")
        if task.observations:
            print(f"  {DIM}last observation: {task.observations[-1]}{RESET}")
        if task.verifier_notes:
            print(f"  {DIM}last checker note: {task.verifier_notes[-1]}{RESET}")
    print()

    print(f"{BOLD}Active Maker Prompt{RESET}")
    print(_indent(maker_prompt(state), "  "))
    print()

    print(f"{BOLD}Active Checker Prompt{RESET}")
    print(_indent(checker_prompt(state), "  "))
    print()

    print(f"{BOLD}Recent Events{RESET}")
    for event in state.events[-7:]:
        print(f"- {event}")
    print()

    print(f"{BOLD}Raw State Snapshot{RESET}")
    print(json.dumps(asdict(state), ensure_ascii=False, indent=2))
    print()

    shortcuts = "  ".join(
        f"[{BOLD}{key}{RESET}] {DIM}{label}{RESET}" for key, (_, label) in KEYS.items()
    )
    print(shortcuts)


def _indent(text: str, prefix: str) -> str:
    return "\n".join(prefix + line for line in text.splitlines())


def main() -> None:
    state = initial_state()
    while True:
        render(state)
        choice = input("\nAction> ").strip().lower()[:1]
        if not choice:
            continue
        action, _ = KEYS.get(choice, ("unknown", ""))
        if action == "quit":
            clear()
            print("Loop prototype closed.")
            return
        if action == "unknown":
            state.events.append(f"unknown key ignored: {choice}")
            continue
        state = dispatch(state, action)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
