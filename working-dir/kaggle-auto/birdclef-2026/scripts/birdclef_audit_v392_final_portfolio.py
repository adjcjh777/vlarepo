#!/usr/bin/env python3
"""Audit safe/bold final candidate portfolio for the current BirdCLEF lane."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENTS = ROOT / "experiments"
ARTIFACTS = ROOT / "artifacts"
V387_STATIC = ARTIFACTS / "runtime_v387_v386_static_materializer_20260524.json"
V387_RUNMODE = ARTIFACTS / "runtime_v387_runmode_status.json"
V389_READY = ARTIFACTS / "runtime_v389_v387_submit_readiness_20260524.json"
V390_FINAL = ARTIFACTS / "runtime_v390_v387_final_submit_gate_20260524.json"
V391_STATIC = ARTIFACTS / "runtime_v391_v386_safe_static_materializer_20260524.json"
V391_RUNMODE = ARTIFACTS / "runtime_v391_runmode_status.json"
REPORT = EXPERIMENTS / "v392_final_portfolio_20260524.md"
RUNTIME = ARTIFACTS / "runtime_v392_final_portfolio_20260524.json"


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default=str(REPORT))
    ap.add_argument("--runtime-json", default=str(RUNTIME))
    return ap.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def read_json(path: Path) -> dict[str, object]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def metrics(payload: dict[str, object]) -> dict[str, object]:
    return payload.get("local_metrics", {}) if isinstance(payload.get("local_metrics"), dict) else {}


def main() -> int:
    args = parse_args()
    started = time.time()
    v387_static = read_json(V387_STATIC)
    v387_runmode = read_json(V387_RUNMODE)
    v389 = read_json(V389_READY)
    v390 = read_json(V390_FINAL)
    v391_static = read_json(V391_STATIC)
    v391_runmode = read_json(V391_RUNMODE)
    m387 = metrics(v387_static)
    m391 = metrics(v391_static)

    safe_ready = v391_runmode.get("decision") in {
        "READY-v391-runmode-dryrun-runtime-proof",
        "READY-v391-runmode-schema-runtime-proof",
    }
    bold_gate_state = str(v390.get("decision", ""))
    bold_ready = (
        v387_runmode.get("decision") in {"READY-v387-runmode-dryrun-runtime-proof", "READY-v387-runmode-schema-runtime-proof"}
        and v389.get("decision") == "READY-v387-submit-readiness-AWAIT-EXPLICIT-SUBMIT-GATE"
        and bold_gate_state in {"READY-v390-v387-final-submit-gate", "SUBMITTED-v387-competition-pending"}
    )
    checks = {
        "bold_v387_submit_ready": bold_ready,
        "safe_v391_static_ready": v391_static.get("decision") == "READY-v391-v386-safe-static-materializer-audit-NO-PUSH-NO-SUBMIT",
        "safe_v391_runmode_ready_or_pending": safe_ready or v391_runmode.get("decision") == "WAIT-running",
        "safe_has_lower_fold_std_delta_than_bold": float(m391.get("fold_std_delta", 999)) < float(m387.get("fold_std_delta", -999)),
        "safe_has_fewer_active_cells_than_bold": int(m391.get("active_cells", 999999)) < int(m387.get("active_cells", -1)),
        "both_pass_macro_gate": float(m387.get("macro_gain", -999)) >= 0.0015 and float(m391.get("macro_gain", -999)) >= 0.0015,
        "both_pass_weak_gate": float(m387.get("weak_followup_gain", -999)) >= 0.006 and float(m391.get("weak_followup_gain", -999)) >= 0.006,
    }
    block_count = sum(not v for v in checks.values())
    if bold_ready and safe_ready and block_count == 0:
        decision = "READY-final-portfolio-safe-v391-bold-v387"
        next_action = "Use v387 as bold_final and v391 as safe_final; require explicit authorization for any real submit."
    elif bold_ready and checks["safe_v391_static_ready"]:
        decision = "WAIT-safe-final-runmode-v391-bold-v387-ready"
        next_action = "Poll v391 Run-mode; keep v387 as current real-submit-ready bold candidate."
    else:
        decision = "HOLD-final-portfolio-incomplete"
        next_action = "Resolve portfolio blockers before final candidate freeze."

    runtime = {
        "timestamp_utc": utc_now(),
        "experiment_id": "v392-final-portfolio",
        "decision": decision,
        "elapsed_seconds": round(time.time() - started, 4),
        "checks": checks,
        "block_count": block_count,
        "safe_final": {
            "candidate": "v391-v386-safe-static-distill",
            "static_decision": v391_static.get("decision"),
            "runmode_decision": v391_runmode.get("decision", "MISSING"),
            "metrics": m391,
        },
        "bold_final": {
            "candidate": "v387-v386-static-distill",
            "static_decision": v387_static.get("decision"),
            "runmode_decision": v387_runmode.get("decision"),
            "submit_readiness": v389.get("decision"),
            "final_submit_gate": v390.get("decision"),
            "metrics": m387,
        },
        "next_recommended_action": next_action,
    }
    Path(args.runtime_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.runtime_json).write_text(json.dumps(runtime, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# v392 Final Portfolio Audit",
        "",
        f"Updated: {runtime['timestamp_utc']}",
        "",
        f"Status: `{decision}`.",
        "",
        "## Research Question",
        "",
        "Do we currently have a safe_final and bold_final pair that satisfies the final-candidate rule without making a real competition submission?",
        "",
        "## Candidate Roles",
        "",
        f"- `bold_final`: `v387-v386-static-distill`, macro_gain `{float(m387.get('macro_gain', 0)):+.8f}`, fold_std_delta `{float(m387.get('fold_std_delta', 0)):+.8f}`, weak_gain `{float(m387.get('weak_followup_gain', 0)):+.8f}`, status `{bold_gate_state}`",
        f"- `safe_final`: `v391-v386-safe-static-distill`, macro_gain `{float(m391.get('macro_gain', 0)):+.8f}`, fold_std_delta `{float(m391.get('fold_std_delta', 0)):+.8f}`, weak_gain `{float(m391.get('weak_followup_gain', 0)):+.8f}`, runmode `{v391_runmode.get('decision', 'MISSING')}`",
        "",
        "## Checks",
        "",
    ]
    lines += [f"- `{k}`: `{v}`" for k, v in checks.items()]
    lines += ["", "## Decision", "", f"- `{decision}`", f"- Next: {next_action}"]
    Path(args.report).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"decision={decision}")
    print(f"block_count={block_count}")
    print(f"bold_ready={bold_ready} safe_ready={safe_ready}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
