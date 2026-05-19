#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments"
STATUS_PATH = EXP / "v138_v134_window_bundle.md"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write combined markdown report")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)

    gate = run(["python3", "scripts/check_v134_next_window_gate.py", "--write"])
    recheck = run(["python3", "scripts/recheck_v134_guarded_candidate.py", "--write"])
    goal = run(["python3", "birdclef-2026/scripts/birdclef_goal_check.py", "--submissions-limit", "20"])
    dryrun = run(
        ["python3", "birdclef-2026/scripts/birdclef_guarded_submit.py", "--candidate", "v134", "--max-today", "4"]
    )

    lines = [
        "# v138 v134 Window Bundle",
        "",
        f"Updated: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "## Commands",
        "",
        "- `python3 scripts/check_v134_next_window_gate.py --write`",
        "- `python3 scripts/recheck_v134_guarded_candidate.py --write`",
        "- `python3 birdclef-2026/scripts/birdclef_goal_check.py --submissions-limit 20`",
        "- `python3 birdclef-2026/scripts/birdclef_guarded_submit.py --candidate v134 --max-today 4`",
        "",
        "## Exit Codes",
        "",
        f"- gate: `{gate.returncode}`",
        f"- recheck: `{recheck.returncode}`",
        f"- goal_check: `{goal.returncode}`",
        f"- guarded_submit_dryrun: `{dryrun.returncode}`",
        "",
        "## Gate Output",
        "",
        "```text",
        gate.stdout.strip(),
        "```",
        "",
        "## Recheck Output",
        "",
        "```text",
        recheck.stdout.strip(),
        "```",
        "",
        "## Goal Check Output",
        "",
        "```text",
        goal.stdout.strip(),
        "```",
        "",
        "## Guarded Submit Dry-Run Output",
        "",
        "```text",
        dryrun.stdout.strip(),
        "```",
        "",
    ]

    if args.write:
        STATUS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"bundle_updated={now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"gate_exit={gate.returncode}")
    print(f"recheck_exit={recheck.returncode}")
    print(f"goal_exit={goal.returncode}")
    print(f"dryrun_exit={dryrun.returncode}")
    if args.write:
        print(f"status_path={STATUS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
