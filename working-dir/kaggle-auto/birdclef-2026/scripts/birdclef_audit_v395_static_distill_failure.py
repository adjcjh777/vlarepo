#!/usr/bin/env python3
"""Audit the v380/v383/v387/v391/v394 static-distill family after v387 scored."""

from __future__ import annotations

import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SUBMISSION_LEDGER = ROOT / "experiments/submission_ledger.csv"
REPORT = ROOT / "experiments/v395_static_distill_failure_20260524.md"
CSV = ROOT / "experiments/v395_static_distill_failure_20260524.csv"
RUNTIME = ROOT / "artifacts/runtime_v395_static_distill_failure_20260524.json"
FAMILY = ["v380", "v383", "v387", "v391", "v394"]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def find_v387_score() -> tuple[str, str, str]:
    with SUBMISSION_LEDGER.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    matches = [r for r in rows if r.get("submission_name") == "v387-dryrun-tolerant-static-distill"]
    if not matches:
        return "MISSING", "", "v387 submission ledger row is missing"
    row = matches[-1]
    return row.get("public_lb_score_if_available", ""), row.get("decision_reason", ""), row.get("notes", "")


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def metric(path: Path, key: str) -> object:
    data = read_json(path)
    metrics = data.get("local_metrics", {}) if isinstance(data.get("local_metrics"), dict) else {}
    return metrics.get(key, "MISSING")


def main() -> int:
    started = time.time()
    score_text, decision_reason, notes = find_v387_score()
    try:
        score = float(score_text)
    except Exception:
        score = float("nan")
    anchor = 0.949
    score_delta = score - anchor if score == score else float("nan")
    family_failure = score == score and score < anchor
    rows = [
        {
            "family_member": "v380",
            "status": "RETIRE-family-extrapolation-risk" if family_failure else "HOLD-score-unverified",
            "reason": "same fixed-coefficient static-distill lineage as v387; v387 public score invalidates proxy trust",
            "local_macro_gain": metric(ROOT / "artifacts/runtime_v380_v379_static_materializer_20260524.json", "macro_gain"),
            "fold_std_delta": metric(ROOT / "artifacts/runtime_v380_v379_static_materializer_20260524.json", "fold_std_delta"),
            "weak_followup_gain": metric(ROOT / "artifacts/runtime_v380_v379_static_materializer_20260524.json", "weak_followup_gain"),
            "submit_allowed": False,
        },
        {
            "family_member": "v383",
            "status": "RETIRE-family-extrapolation-risk" if family_failure else "HOLD-score-unverified",
            "reason": "dry-run tolerant v380 repair; same public-score failure risk as v387",
            "local_macro_gain": metric(ROOT / "artifacts/runtime_v383_v380_dryrun_tolerant_20260524.json", "macro_gain"),
            "fold_std_delta": metric(ROOT / "artifacts/runtime_v383_v380_dryrun_tolerant_20260524.json", "fold_std_delta"),
            "weak_followup_gain": metric(ROOT / "artifacts/runtime_v383_v380_dryrun_tolerant_20260524.json", "weak_followup_gain"),
            "submit_allowed": False,
        },
        {
            "family_member": "v387",
            "status": "RETIRE-scored-collapse" if family_failure else "HOLD-score-unverified",
            "reason": f"public score {score_text} vs anchor {anchor:.3f}; {decision_reason}",
            "local_macro_gain": metric(ROOT / "artifacts/runtime_v387_v386_static_materializer_20260524.json", "macro_gain"),
            "fold_std_delta": metric(ROOT / "artifacts/runtime_v387_v386_static_materializer_20260524.json", "fold_std_delta"),
            "weak_followup_gain": metric(ROOT / "artifacts/runtime_v387_v386_static_materializer_20260524.json", "weak_followup_gain"),
            "submit_allowed": False,
        },
        {
            "family_member": "v391",
            "status": "BLOCK-sibling-of-scored-collapse" if family_failure else "HOLD-score-unverified",
            "reason": "safe_final changes gates/active cells but inherits v387's failed fixed-coefficient static-distill mechanism",
            "local_macro_gain": metric(ROOT / "artifacts/runtime_v391_v386_safe_static_materializer_20260524.json", "macro_gain"),
            "fold_std_delta": metric(ROOT / "artifacts/runtime_v391_v386_safe_static_materializer_20260524.json", "fold_std_delta"),
            "weak_followup_gain": metric(ROOT / "artifacts/runtime_v391_v386_safe_static_materializer_20260524.json", "weak_followup_gain"),
            "submit_allowed": False,
        },
        {
            "family_member": "v394",
            "status": "BLOCK-blend-of-scored-collapse" if family_failure else "HOLD-score-unverified",
            "reason": "blend of v391 and v387 endpoints; local dominance no longer counts as submit evidence after v387 public collapse",
            "local_macro_gain": read_json(ROOT / "artifacts/runtime_v394_safe_bold_blend_20260524.json").get("best", {}).get("macro_gain", "MISSING"),
            "fold_std_delta": read_json(ROOT / "artifacts/runtime_v394_safe_bold_blend_20260524.json").get("best", {}).get("fold_std_delta", "MISSING"),
            "weak_followup_gain": read_json(ROOT / "artifacts/runtime_v394_safe_bold_blend_20260524.json").get("best", {}).get("weak_followup_gain", "MISSING"),
            "submit_allowed": False,
        },
    ]
    CSV.parent.mkdir(parents=True, exist_ok=True)
    with CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    decision = "RETIRE-static-distill-family-NO-SUBMIT" if family_failure else "HOLD-static-distill-score-unverified-NO-SUBMIT"
    updated = utc_now()
    runtime = {
        "timestamp_utc": updated,
        "experiment_id": "v395-static-distill-failure",
        "decision": decision,
        "elapsed_seconds": round(time.time() - started, 4),
        "v387_public_score": score_text,
        "anchor_score": anchor,
        "score_delta_vs_anchor": score_delta,
        "family": FAMILY,
        "rows": rows,
        "next_recommended_action": "Do not submit v383/v391/v394. Move to a non-static-distill, hidden-test-computable route with real public evidence or explicit fresh submit gate.",
    }
    RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    RUNTIME.write_text(json.dumps(runtime, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    table = "\n".join(
        f"| {r['family_member']} | {r['status']} | {r['local_macro_gain']} | {r['fold_std_delta']} | {r['weak_followup_gain']} | {r['submit_allowed']} |"
        for r in rows
    )
    REPORT.write_text(
        f"""# v395 Static-distill Family Failure Audit

Updated: {updated}

Status: `{decision}`.

## Research Question

After v387 scored publicly, should any v380/v383/v387/v391/v394 fixed-coefficient static-distill sibling remain submit-eligible?

## Evidence

- v387 public score: `{score_text}`
- Visible anchor/best to beat: `{anchor:.3f}`
- Delta vs anchor: `{score_delta:+.3f}`
- v387 ledger reason: {decision_reason}
- v387 notes: {notes}

## Family Decision

| member | status | local_macro_gain | fold_std_delta | weak_followup_gain | submit_allowed |
|---|---|---:|---:|---:|---|
{table}

## Decision

- `{decision}`
- Do not submit v383, v391, or v394 after v387's public collapse.
- Next action: pivot to a non-static-distill route with hidden-test-computable evidence, or protect the 0.949 visible-best fallback.
""",
        encoding="utf-8",
    )
    print(f"decision={decision}")
    print(f"v387_public_score={score_text}")
    print(f"score_delta_vs_anchor={score_delta:+.3f}")
    print(f"report={REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
