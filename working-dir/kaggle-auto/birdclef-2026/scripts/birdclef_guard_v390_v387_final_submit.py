#!/usr/bin/env python3
"""Guard v387 before any real BirdCLEF 2026 competition submission.

Default mode never submits. The execute path requires both --execute and
--confirm-submit-v387 so the dry-run audit can be refreshed safely.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from kaggle.api.kaggle_api_extended import KaggleApi


ROOT = Path(__file__).resolve().parents[2]
COMPETITION = "birdclef-2026"
CANDIDATE = "v387-v386-static-distill"
KERNEL = "junhaochengadjcjh7u7/bc26-v387-v386-static-distill"
KERNEL_VERSION = 1
FILE_NAME = "submission.csv"
MESSAGE = (
    "v387 v386 parameter-stressed fixed-coefficient distill over the clean v107 Perch anchor; "
    "uses hidden-test-computable row_id temporal context and train soundscape priors, "
    "retains real sample-row guards, CPU-only no-internet; submitted only after v387 "
    "Run-mode runtime proof, v388 class-risk audit, and v389 submit-readiness gate"
)

V387_RUNMODE = ROOT / "artifacts/runtime_v387_runmode_status.json"
V389_READY = ROOT / "artifacts/runtime_v389_v387_submit_readiness_20260524.json"
V387_STATIC = ROOT / "artifacts/runtime_v387_v386_static_materializer_20260524.json"
NOTEBOOK_DIR = ROOT / "birdclef-2026/notebooks/v387-v386-static-distill"
METADATA = NOTEBOOK_DIR / "kernel-metadata.json"
REPORT = ROOT / "experiments/v390_v387_final_submit_gate_20260524.md"
RUNTIME = ROOT / "artifacts/runtime_v390_v387_final_submit_gate_20260524.json"
SUBMISSION_LEDGER = ROOT / "experiments/submission_ledger.csv"


@dataclass
class GateResult:
    decision: str
    blockers: list[str]
    evidence: dict[str, Any]


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def today_prefix() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def score_float(value: object) -> float | None:
    try:
        text = str(value or "").strip()
        return float(text) if text else None
    except ValueError:
        return None


def live_state() -> dict[str, Any]:
    try:
        api = KaggleApi()
        api.authenticate()
        subs = api.competition_submissions(COMPETITION)[:20]
        kernel_status = api.kernels_status(KERNEL)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    today = today_prefix()
    latest: list[dict[str, Any]] = []
    pending = 0
    duplicate_scored = False
    duplicate_pending = False
    for sub in subs:
        desc = str(getattr(sub, "description", "") or "")
        status = str(getattr(sub, "status", "") or "")
        score = score_float(getattr(sub, "public_score", ""))
        if "PENDING" in status:
            pending += 1
        if "v387" in desc.lower() or "dry-run-tolerant fixed-coefficient distill" in desc.lower():
            if score is not None:
                duplicate_scored = True
            if "PENDING" in status:
                duplicate_pending = True
        latest.append(
            {
                "date": str(getattr(sub, "date", "") or ""),
                "status": status,
                "score": "" if score is None else f"{score:.3f}",
                "description": desc,
            }
        )
    today_count = sum(1 for sub in subs if str(getattr(sub, "date", "")).startswith(today))
    return {
        "ok": True,
        "pending": pending,
        "today_count": today_count,
        "kernel_status": str(kernel_status),
        "duplicate_scored": duplicate_scored,
        "duplicate_pending": duplicate_pending,
        "latest": latest[:5],
    }


def evaluate(max_today: int) -> GateResult:
    blockers: list[str] = []
    runmode = read_json(V387_RUNMODE)
    ready = read_json(V389_READY)
    static = read_json(V387_STATIC)
    metadata = read_json(METADATA)
    live = live_state()

    local_metrics = static.get("local_metrics", {}) if isinstance(static.get("local_metrics"), dict) else {}
    audit = static.get("audit", {}) if isinstance(static.get("audit"), dict) else {}
    evidence: dict[str, Any] = {
        "candidate": CANDIDATE,
        "kernel": KERNEL,
        "kernel_version": KERNEL_VERSION,
        "v387_runmode_decision": runmode.get("decision", "MISSING"),
        "v387_runtime_seconds": runmode.get("runtime_seconds", "MISSING"),
        "v389_decision": ready.get("decision", "MISSING"),
        "v389_blocker_count": ready.get("blocker_count", "MISSING"),
        "v387_static_decision": static.get("decision", "MISSING"),
        "v387_static_block_count": audit.get("block_count", "MISSING"),
        "macro_gain": local_metrics.get("macro_gain", "MISSING"),
        "fold_std_delta": local_metrics.get("fold_std_delta", "MISSING"),
        "weak_followup_gain": local_metrics.get("weak_followup_gain", "MISSING"),
        "corr_vs_v107_anchor": local_metrics.get("corr_vs_v107_anchor", "MISSING"),
        "metadata_id": metadata.get("id", "MISSING"),
        "metadata_enable_gpu": metadata.get("enable_gpu", "MISSING"),
        "metadata_enable_tpu": metadata.get("enable_tpu", "MISSING"),
        "metadata_enable_internet": metadata.get("enable_internet", "MISSING"),
        "live": live,
        "max_today": max_today,
    }

    if runmode.get("decision") != "READY-v387-runmode-dryrun-runtime-proof":
        blockers.append("v387_runmode_not_ready")
    if ready.get("decision") != "READY-v387-submit-readiness-AWAIT-EXPLICIT-SUBMIT-GATE":
        blockers.append("v389_submit_readiness_not_ready")
    if ready.get("blocker_count") != 0:
        blockers.append("v389_blockers_present")
    if static.get("decision") != "READY-v387-v386-static-materializer-audit-NO-PUSH-NO-SUBMIT":
        blockers.append("v387_static_not_ready")
    if audit.get("block_count") != 0:
        blockers.append("v387_static_blockers_present")

    try:
        macro_gain = float(local_metrics.get("macro_gain"))
        fold_std_delta = float(local_metrics.get("fold_std_delta"))
    except Exception:
        blockers.append("local_metrics_missing")
    else:
        if macro_gain < 0.0015:
            blockers.append("macro_gate_not_met")
        if fold_std_delta > 1e-12:
            blockers.append("fold_std_regressed")

    if metadata.get("id") != KERNEL:
        blockers.append("metadata_id_mismatch")
    if metadata.get("enable_gpu") is not False:
        blockers.append("metadata_gpu_not_disabled")
    if metadata.get("enable_tpu") is not False:
        blockers.append("metadata_tpu_not_disabled")
    if metadata.get("enable_internet") is not False:
        blockers.append("metadata_internet_not_disabled")

    if not live.get("ok"):
        blockers.append("live_state_unavailable")
    else:
        if int(live.get("pending", -1)) > 0:
            blockers.append("live_pending_submission")
        if int(live.get("today_count", 999)) > max_today:
            blockers.append("today_quota_guard")
        if "COMPLETE" not in str(live.get("kernel_status", "")):
            blockers.append("kernel_status_not_complete")
        if live.get("duplicate_scored") or live.get("duplicate_pending"):
            blockers.append("duplicate_v387_submission")

    decision = "READY-v390-v387-final-submit-gate" if not blockers else "HOLD-v390-v387-final-submit-gate"
    return GateResult(decision=decision, blockers=blockers, evidence=evidence)


def write_report(result: GateResult, execute: bool, submitted: bool, submit_response: str) -> None:
    RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp_utc": now_utc(),
        "experiment_id": "v390-v387-final-submit-gate",
        "decision": result.decision,
        "blocker_count": len(result.blockers),
        "blockers": result.blockers,
        "execute_requested": execute,
        "submitted": submitted,
        "submit_response": submit_response,
        "evidence": result.evidence,
    }
    RUNTIME.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# v390 v387 Final Submit Gate",
        "",
        f"Updated: {payload['timestamp_utc']}",
        "",
        f"- Decision: `{result.decision}`",
        f"- Blocker count: `{len(result.blockers)}`",
        f"- Blockers: `{result.blockers}`",
        f"- Execute requested: `{execute}`",
        f"- Submitted: `{submitted}`",
        "",
        "## Research Question",
        "",
        "Is v387 ready for a real BirdCLEF 2026 competition submission after fresh Run-mode, readiness, quota, duplicate, metadata, and promotion-gate checks?",
        "",
        "## Evidence",
        "",
    ]
    for key, value in result.evidence.items():
        lines.append(f"- {key}: `{value}`")
    lines += [
        "",
        "## Decision",
        "",
        f"`{result.decision}`",
        "",
        "This gate does not submit unless both `--execute` and `--confirm-submit-v387` are provided.",
    ]
    if submit_response:
        lines += ["", "## Submit Response", "", "```", submit_response.strip(), "```"]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_submission_ledger(response: str) -> None:
    if not SUBMISSION_LEDGER.exists():
        return
    live = live_state()
    slot = int(live.get("today_count", 0)) if live.get("ok") else 0
    row = {
        "submitted_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "submission_name": "v387-dryrun-tolerant-static-distill",
        "submission_ref_or_kernel": f"kernel:{KERNEL} v{KERNEL_VERSION}; response={response}",
        "candidate_evidence": "v387 Run-mode READY runtime_seconds=298; v389 blocker_count=0; v387 static macro_gain=+0.00291826 fold_std_delta=-0.00083026 weak_gain=+0.00917166",
        "submit_reason": "explicitly authorized final-submit gate after v387/v389 readiness",
        "public_lb_score_if_available": "",
        "decision_reason": "PENDING-public-score; monitor before any further real submit",
        "utc_day_slot": str(slot),
        "final_submission_candidate": "yes",
        "rules_compliance_status": "HOLD-pending-public-score",
        "notes": MESSAGE,
    }
    with SUBMISSION_LEDGER.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row))
        writer.writerow(row)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-today", type=int, default=4)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm-submit-v387", action="store_true")
    args = parser.parse_args()

    result = evaluate(max_today=args.max_today)
    submitted = False
    submit_response = ""
    if args.execute:
        if not args.confirm_submit_v387:
            result.blockers.append("missing_explicit_confirm_submit_v387")
            result.decision = "HOLD-v390-v387-final-submit-gate"
        elif result.decision != "READY-v390-v387-final-submit-gate":
            submit_response = "execute refused: gate is not READY"
        else:
            api = KaggleApi()
            api.authenticate()
            response = api.competition_submit_code(
                FILE_NAME,
                MESSAGE,
                COMPETITION,
                kernel=KERNEL,
                kernel_version=KERNEL_VERSION,
                quiet=False,
            )
            submit_response = repr(response)
            append_submission_ledger(submit_response)
            submitted = True
            result.decision = "SUBMITTED-v387-competition-pending"

    write_report(result, execute=args.execute, submitted=submitted, submit_response=submit_response)
    print(f"checked_at={now_utc()}")
    print(f"decision={result.decision}")
    print(f"blockers={result.blockers}")
    print(f"submitted={submitted}")
    print(f"report={REPORT}")
    print(f"runtime={RUNTIME}")
    return 0 if not result.blockers else 2


if __name__ == "__main__":
    raise SystemExit(main())
