#!/usr/bin/env python3
"""Submit-readiness audit for v391.

This script never submits. It verifies whether v391 has enough evidence before
a separate explicitly authorized competition-submit command can be considered.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENTS = ROOT / "experiments"
ARTIFACTS = ROOT / "artifacts"
V391_RUNMODE = ARTIFACTS / "runtime_v391_runmode_status.json"
V391_STATIC = ARTIFACTS / "runtime_v391_v386_safe_static_materializer_20260524.json"
V388_CLASS_RISK = ARTIFACTS / "runtime_v388_v387_class_risk_20260524.json"


@dataclass
class CheckRow:
    check: str
    status: str
    evidence: str
    blocker: bool


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-csv", default=str(EXPERIMENTS / "v393_v391_submit_readiness_20260524.csv"))
    ap.add_argument("--report", default=str(EXPERIMENTS / "v393_v391_submit_readiness_20260524.md"))
    ap.add_argument("--runtime-json", default=str(ARTIFACTS / "runtime_v393_v391_submit_readiness_20260524.json"))
    return ap.parse_args()


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {"parse_error": f"{type(exc).__name__}: {exc}"}


def live_submissions() -> dict[str, object]:
    try:
        api = KaggleApi()
        api.authenticate()
        subs = api.competition_submissions("birdclef-2026")[:20]
    except Exception as exc:  # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {exc}", "pending": -1, "today_count": -1}
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    duplicate = False
    latest: list[dict[str, object]] = []
    for sub in subs[:20]:
        desc = str(getattr(sub, "description", "") or "")
        status = str(getattr(sub, "status", "") or "")
        score = str(getattr(sub, "publicScore", "") or getattr(sub, "public_score", "") or "")
        if "v391" in desc.lower() or "v386 static" in desc.lower():
            duplicate = True
        latest.append({"date": str(getattr(sub, "date", "")), "status": status, "score": score, "description": desc})
    return {
        "pending": sum(1 for sub in subs if "PENDING" in str(getattr(sub, "status", "") or "")),
        "today_count": sum(1 for sub in subs if str(getattr(sub, "date", "")).startswith(today)),
        "duplicate_v391": duplicate,
        "latest": latest[:5],
    }


def add(rows: list[CheckRow], check: str, ok: bool, evidence: str, required: bool = True) -> None:
    rows.append(CheckRow(check, "PASS" if ok else "BLOCK", evidence, bool(required and not ok)))


def main() -> int:
    args = parse_args()
    started = time.time()
    runmode = read_json(V391_RUNMODE)
    static = read_json(V391_STATIC)
    risk = read_json(V388_CLASS_RISK)
    live = live_submissions()
    metrics = static.get("local_metrics", {}) if isinstance(static.get("local_metrics"), dict) else {}
    audit = static.get("audit", {}) if isinstance(static.get("audit"), dict) else {}

    rows: list[CheckRow] = []
    run_decision = str(runmode.get("decision", "MISSING"))
    add(
        rows,
        "v391_runmode_ready",
        run_decision in {"READY-v391-runmode-schema-runtime-proof", "READY-v391-runmode-dryrun-runtime-proof"},
        f"decision={run_decision} runtime_seconds={runmode.get('runtime_seconds')}",
    )
    add(rows, "v391_runmode_not_failed", not run_decision.startswith("REJECT"), f"decision={run_decision}")
    add(
        rows,
        "v391_static_ready",
        static.get("decision") == "READY-v391-v386-safe-static-materializer-audit-NO-PUSH-NO-SUBMIT",
        f"decision={static.get('decision')}",
    )
    add(rows, "v391_static_no_blockers", audit.get("block_count") == 0, f"block_count={audit.get('block_count')}")
    add(rows, "macro_gate", float(metrics.get("macro_gain", -999)) >= 0.0015, f"macro_gain={metrics.get('macro_gain')}")
    add(rows, "weak_gate", float(metrics.get("weak_followup_gain", -999)) >= 0.006, f"weak_followup_gain={metrics.get('weak_followup_gain')}")
    add(
        rows,
        "top5_no_regression",
        float(metrics.get("local_top5_hit", -1)) >= float(metrics.get("anchor_top5_hit", 999)),
        f"top5={metrics.get('anchor_top5_hit')}->{metrics.get('local_top5_hit')}",
    )
    add(rows, "fold_std_not_worse", float(metrics.get("fold_std_delta", 999)) <= 0.0, f"fold_std_delta={metrics.get('fold_std_delta')}")
    add(rows, "class_risk_pass", risk.get("decision") == "READY-v388-v387-class-risk-pass-NO-PUSH-NO-SUBMIT", f"decision={risk.get('decision')} block_count={risk.get('block_count')}")
    add(rows, "no_live_pending", live.get("pending") == 0, f"pending={live.get('pending')} today_count={live.get('today_count')}")
    add(rows, "submission_quota_visible", int(live.get("today_count", 99)) < 5 if isinstance(live.get("today_count"), int) else False, f"today_count={live.get('today_count')}")
    add(rows, "no_duplicate_v391_submission", live.get("duplicate_v391") is False, f"duplicate_v391={live.get('duplicate_v391')}")
    add(rows, "explicit_competition_submit_not_made", True, "this audit has no submit call")

    blockers = [r for r in rows if r.blocker]
    if blockers:
        decision = "WAIT-v391-submit-readiness-blocked-NO-SUBMIT"
        next_action = "Resolve blockers before any separate v391 final-submit gate."
    else:
        decision = "READY-v391-submit-readiness-AWAIT-EXPLICIT-SUBMIT-GATE"
        next_action = "A separate guarded competition-submit command can be considered only with explicit authorization and fresh final checks."

    runtime = {
        "timestamp_utc": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "experiment_id": "v393-v391-submit-readiness",
        "decision": decision,
        "blocker_count": len(blockers),
        "blockers": [r.check for r in blockers],
        "runmode_decision": run_decision,
        "static_decision": static.get("decision"),
        "class_risk_decision": risk.get("decision"),
        "live": live,
        "runtime_seconds": round(time.time() - started, 4),
        "next_recommended_action": next_action,
    }

    out_csv = Path(args.output_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(CheckRow.__annotations__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))

    lines = [
        "# v393 v391 Submit-readiness Audit",
        "",
        f"Updated: {runtime['timestamp_utc']}",
        "",
        f"Status: `{decision}`.",
        "",
        "## Research Question",
        "",
        "Does v391 have enough Run-mode, static, promotion, class-risk, quota, duplicate, and pending-submission evidence to even consider a separate real competition-submit gate?",
        "",
        "## Result",
        "",
        f"- Blocker count: `{len(blockers)}`",
        f"- Blockers: `{[r.check for r in blockers]}`",
        f"- Run-mode decision: `{run_decision}`",
        f"- Static decision: `{static.get('decision')}`",
        f"- Class-risk decision: `{risk.get('decision')}`",
        f"- Live pending: `{live.get('pending')}`",
        f"- Visible submissions today: `{live.get('today_count')}`",
        f"- Duplicate v391: `{live.get('duplicate_v391')}`",
        "",
        "## Checks",
        "",
        "| check | status | blocker | evidence |",
        "|---|---|---:|---|",
    ]
    for row in rows:
        lines.append(f"| {row.check} | {row.status} | {row.blocker} | {row.evidence} |")
    lines.extend(["", "## Decision", "", f"- `{decision}`", f"- Next: {next_action}"])
    Path(args.report).write_text("\n".join(lines) + "\n", encoding="utf-8")

    Path(args.runtime_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.runtime_json).write_text(json.dumps(runtime, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"decision={decision}")
    print(f"blocker_count={len(blockers)} blockers={[r.check for r in blockers]}")
    print(f"runmode_decision={run_decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
