#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi


ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments"
LEDGER = EXP / "submission_ledger.csv"
STATUS = EXP / "v387_score_monitor_status.md"
RESULT = EXP / "submission_result_v387.md"
COMPETITION = "birdclef-2026"
SUBMISSION_NAME = "v387-dryrun-tolerant-static-distill"
KERNEL = "junhaochengadjcjh7u7/bc26-v387-v386-static-distill"
BEST_VISIBLE = 0.949
TOP20 = 0.955
TOP5 = 0.960


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def score_float(value: object) -> float | None:
    try:
        text = str(value or "").strip()
        return float(text) if text else None
    except ValueError:
        return None


def find_submission(subs: list[object]) -> object | None:
    for sub in subs:
        desc = str(getattr(sub, "description", "") or "").lower()
        if "v387 v386 parameter-stressed fixed-coefficient distill" in desc or "v387" in desc:
            return sub
    return None


def decision_for(status: str, score: float | None, error: str) -> tuple[str, str]:
    if error:
        return "REJECT-error", f"hidden evaluation error: {error}"
    if "PENDING" in status:
        return "WAIT-pending", "v387 is pending; do not submit another candidate until this resolves"
    if score is None:
        return "WAIT-no-score", "submission is not pending but public score is blank; inspect Kaggle table before action"
    if score >= TOP5:
        return "PROMOTE-top5-review", "score reached or exceeded current Top5 cutoff; start final/fallback/bold protection"
    if score >= TOP20:
        return "PROMOTE-top20-review", "score reached current Top20 cutoff; review final/fallback strategy"
    if score > BEST_VISIBLE:
        return "HOLD-improved-anchor", "score improved visible best but did not reach Top20"
    if score == BEST_VISIBLE:
        return "HOLD-tie-anchor", "score tied 0.949; keep v387 evidence but do not repeat this route blindly"
    return "RETIRE-no-progress", "score underperformed 0.949 anchor; retire v387 unless a concrete implementation bug is found"


def update_ledger(status: str, score: float | None, decision: str, reason: str) -> None:
    if not LEDGER.exists():
        return
    with LEDGER.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(rows[0].keys()) if rows else []
    changed = False
    for row in rows:
        if row.get("submission_name") != SUBMISSION_NAME:
            continue
        if score is not None:
            row["public_lb_score_if_available"] = f"{score:.3f}"
        if "PENDING" in status:
            row["decision_reason"] = "PENDING-public-score; v387 dispatched by guarded submit after gate and recheck pass"
            row["rules_compliance_status"] = "HOLD-pending-public-score"
        else:
            row["decision_reason"] = reason
            if decision.startswith("PROMOTE"):
                row["rules_compliance_status"] = "PASS-scored-review-needed"
            elif decision.startswith("HOLD"):
                row["rules_compliance_status"] = "HOLD-scored-not-final"
            elif decision.startswith(("RETIRE", "REJECT")):
                row["rules_compliance_status"] = "PASS-scored-not-final"
            row["final_submission_candidate"] = "no"
        changed = True
    if changed and fieldnames:
        with LEDGER.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


def write_reports(sub: object | None, today_count: int) -> tuple[str, str]:
    checked = now_utc()
    if sub is None:
        status = "MISSING"
        score = None
        error = ""
        date = ""
        desc = ""
        ref = ""
    else:
        status = str(getattr(sub, "status", "") or "")
        score = score_float(getattr(sub, "public_score", ""))
        error = str(getattr(sub, "error_description", "") or "")
        date = str(getattr(sub, "date", "") or "")
        desc = str(getattr(sub, "description", "") or "")
        ref = str(getattr(sub, "ref", "") or "")
    decision, reason = decision_for(status, score, error)
    if sub is not None:
        update_ledger(status, score, decision, reason)

    STATUS.write_text(
        "\n".join(
            [
                "# v387 Score Monitor Status",
                "",
                f"Updated: {checked}",
                "",
                "## Submission",
                "",
                f"- candidate: `{SUBMISSION_NAME}`",
                f"- ref: `{ref}`",
                f"- submitted_at: `{date}`",
                f"- status: `{status}`",
                f"- public_score: `{'' if score is None else f'{score:.3f}'}`",
                f"- error: `{error}`",
                f"- utc_today_visible_submissions: `{today_count}`",
                "",
                "## Decision",
                "",
                f"- state: `{decision}`",
                f"- reason: {reason}",
                "",
                "## Guard",
                "",
                "- Do not submit another candidate while v387 is pending.",
                "- If v387 improves beyond `0.949`, record the new visible best and start protection planning.",
                "- If v387 ties/drops/errors, hold or retire v386 parameter-stressed fixed-coefficient distill before any sibling route.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Submission Result: v387",
        "",
        f"Updated: {checked}",
        "",
        "## Candidate",
        "",
        f"- Name: `{SUBMISSION_NAME}`",
        f"- Kernel: `{KERNEL}`",
        "- Kernel version: `1`",
        f"- Kaggle ref: `{ref}`",
        f"- UTC-day visible slot: `{today_count}`",
        "",
        "## Current Status",
        "",
        f"`{decision}`",
        "",
        f"- Kaggle status: `{status}`",
        f"- Public score: `{'' if score is None else f'{score:.3f}'}`",
        f"- Error: `{error}`",
        f"- Latest check: `{checked}`",
        "",
        "## Why It Was Submitted",
        "",
        "v387 is the v386 parameter-stressed fixed-coefficient distillation route over the clean v107 Perch anchor. It uses hidden-test-computable row_id temporal context and train soundscape priors, passed v388 class-risk audit, and was submitted after v389/v390 readiness gates.",
        "",
        "Pre-submit evidence:",
        "",
        "- v387 Run-mode decision was `READY-v387-runmode-dryrun-runtime-proof`.",
        "- Kaggle kernel status was `COMPLETE`.",
        "- Dry-run schema/range/log checks passed and runtime was 298 seconds.",
        "- Static metrics: macro_gain `+0.00291826`, fold_std_delta `-0.00083026`, weak_followup_gain `+0.00917166`.",
        "- v388 class-risk audit found no class regression below `-0.001` and no fold regression below `-0.001`.",
        "",
        "## Post-score Rule",
        "",
        "- If public score improves beyond `0.949`, record the new visible best and start protection planning.",
        "- If public score reaches `0.955+`, compare against Top20/Top5 and prepare final/fallback strategy.",
        "- If public score ties/drops/errors, hold or retire v387 before spending a sibling route slot.",
    ]
    if desc:
        lines += ["", "## Kaggle Description", "", desc]
    RESULT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return decision, reason


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    api = KaggleApi()
    api.authenticate()
    subs = api.competition_submissions(COMPETITION)[:20]
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_count = sum(1 for s in subs if str(getattr(s, "date", "")).startswith(today))
    sub = find_submission(subs)
    if args.write:
        decision, reason = write_reports(sub, today_count)
    else:
        status = str(getattr(sub, "status", "") or "MISSING") if sub is not None else "MISSING"
        score = score_float(getattr(sub, "public_score", "")) if sub is not None else None
        error = str(getattr(sub, "error_description", "") or "") if sub is not None else ""
        decision, reason = decision_for(status, score, error)
    print(f"checked_at={now_utc()}")
    print(f"v387_found={sub is not None}")
    if sub is not None:
        print(f"v387_date={getattr(sub, 'date', '')}")
        print(f"v387_status={getattr(sub, 'status', '')}")
        print(f"v387_public_score={getattr(sub, 'public_score', '')}")
        print(f"v387_error={getattr(sub, 'error_description', '')}")
    print(f"decision={decision}")
    print(f"reason={reason}")
    if args.write:
        print(f"status_path={STATUS}")
        print(f"result_path={RESULT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
