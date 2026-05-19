#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments"
STATUS_PATH = EXP / "v140_v134_guarded_state_refresh.md"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write markdown summary")
    parser.add_argument(
        "--execute-if-ready",
        action="store_true",
        help="pass through to the wrapper so it may execute if the guarded gates are satisfied",
    )
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    cmds = [
        ["python3", "scripts/check_v134_next_window_gate.py", "--write"],
        ["python3", "scripts/recheck_v134_guarded_candidate.py", "--write"],
        ["python3", "scripts/check_v134_window_bundle.py", "--write"],
        ["python3", "scripts/recheck_and_optionally_submit_v134.py", "--write"],
    ]
    if args.execute_if_ready:
        cmds[-1].append("--execute-if-ready")

    labels = ["gate", "recheck", "bundle", "wrapper"]
    results = [(label, run(cmd), cmd) for label, cmd in zip(labels, cmds)]

    lines = [
        "# v140 v134 Guarded State Refresh",
        "",
        f"Updated: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "## Inputs",
        "",
        f"- execute_if_ready: `{args.execute_if_ready}`",
        "",
        "## Exit Codes",
        "",
    ]
    for label, proc, _cmd in results:
        lines.append(f"- {label}: `{proc.returncode}`")
    lines += ["", "## Outputs", ""]
    for label, proc, cmd in results:
        lines += [
            f"### {label}",
            "",
            f"`{' '.join(cmd)}`",
            "",
            "```text",
            proc.stdout.strip(),
            "```",
            "",
        ]

    if args.write:
        STATUS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"refresh_updated={now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    for label, proc, _ in results:
        print(f"{label}_exit={proc.returncode}")
    if args.write:
        print(f"status_path={STATUS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
