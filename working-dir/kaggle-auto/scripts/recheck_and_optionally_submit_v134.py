#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments"
STATUS_PATH = EXP / "v139_v134_submit_wrapper_status.md"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def extract_value(text: str, prefix: str) -> str | None:
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.split("=", 1)[1].strip()
    return None


def extract_markdown_decision(path: Path) -> str | None:
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("`") and stripped.endswith("`") and "UTC" not in stripped:
            return stripped.strip("`")
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write markdown summary")
    parser.add_argument("--execute-if-ready", action="store_true", help="actually submit only if the ready gates pass")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)

    gate = run(["python3", "scripts/check_v134_next_window_gate.py", "--write"])
    recheck = run(["python3", "scripts/recheck_v134_guarded_candidate.py", "--write"])
    bundle = run(["python3", "scripts/check_v134_window_bundle.py", "--write"])
    dryrun = run(["python3", "birdclef-2026/scripts/birdclef_guarded_submit.py", "--candidate", "v134", "--max-today", "4"])

    gate_decision = extract_value(gate.stdout, "decision") or extract_markdown_decision(EXP / "v136_next_window_gate_status.md")
    recheck_verdict = extract_value(recheck.stdout, "verdict") or extract_markdown_decision(EXP / "v137_v134_guarded_recheck_status.md")
    bundle_gate_exit = extract_value(bundle.stdout, "gate_exit")
    bundle_recheck_exit = extract_value(bundle.stdout, "recheck_exit")
    bundle_goal_exit = extract_value(bundle.stdout, "goal_exit")
    dryrun_exit = dryrun.returncode

    ready = (
        gate_decision == "READY-FOR-GUARDED-RECHECK"
        and recheck_verdict == "READY-FOR-GUARDED-RECHECK"
        and bundle_gate_exit == "0"
        and bundle_recheck_exit == "0"
        and bundle_goal_exit not in {None, "4"}
        and dryrun_exit == 0
    )

    execute_proc = None
    if args.execute_if_ready and ready:
        execute_proc = run(
            ["python3", "birdclef-2026/scripts/birdclef_guarded_submit.py", "--candidate", "v134", "--max-today", "0", "--execute"]
        )

    verdict = "READY-BUT-DRYRUN-ONLY" if ready and not args.execute_if_ready else "NOT-READY"
    if args.execute_if_ready and ready:
        verdict = "EXECUTED" if execute_proc and execute_proc.returncode == 0 else "EXECUTE-FAILED"

    lines = [
        "# v139 v134 Submit Wrapper Status",
        "",
        f"Updated: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "## Inputs",
        "",
        f"- execute_if_ready: `{args.execute_if_ready}`",
        "",
        "## Gate Summary",
        "",
        f"- gate_decision: `{gate_decision}`",
        f"- recheck_verdict: `{recheck_verdict}`",
        f"- bundle_gate_exit: `{bundle_gate_exit}`",
        f"- bundle_recheck_exit: `{bundle_recheck_exit}`",
        f"- bundle_goal_exit: `{bundle_goal_exit}`",
        f"- guarded_submit_dryrun_exit: `{dryrun_exit}`",
        f"- ready_for_guarded_submit: `{ready}`",
        "",
        "## Wrapper Verdict",
        "",
        f"`{verdict}`",
        "",
    ]

    if args.write:
        lines += [
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
            "## Bundle Output",
            "",
            "```text",
            bundle.stdout.strip(),
            "```",
            "",
            "## Guarded Submit Dry-Run Output",
            "",
            "```text",
            dryrun.stdout.strip(),
            "```",
            "",
        ]
        if execute_proc is not None:
            lines += [
                "## Guarded Submit Execute Output",
                "",
                "```text",
                execute_proc.stdout.strip(),
                "```",
                "",
            ]
        STATUS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"gate_decision={gate_decision}")
    print(f"recheck_verdict={recheck_verdict}")
    print(f"ready_for_guarded_submit={ready}")
    print(f"wrapper_verdict={verdict}")
    if args.write:
        print(f"status_path={STATUS_PATH}")
    return 0 if not args.execute_if_ready or ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
