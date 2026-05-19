#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments"
STATUS_PATH = EXP / "v137_v134_guarded_recheck_status.md"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def ledger_last_day() -> str:
    ledger = pd.read_csv(EXP / "submission_ledger.csv")
    return str(ledger.iloc[-1]["timestamp"]).split(" ")[0]


def scorecard_top() -> dict[str, str]:
    scorecard = pd.read_csv(EXP / "v133_next_candidate_scorecard.csv")
    row = scorecard.iloc[0]
    return {k: str(v) for k, v in row.items()}


def has_phrase(path: Path, phrase: str) -> bool:
    return phrase in path.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write markdown status")
    args = parser.parse_args()

    now = utc_now()
    today = now.strftime("%Y-%m-%d")
    last_day = ledger_last_day()
    top = scorecard_top()

    runmode = EXP / "v134_runmode_status.md"
    rules = EXP / "rules_compliance_report_v134.md"
    validation = EXP / "submission_validation_report_v134.md"
    decision = EXP / "v134_submission_decision_brief.md"

    checks = {
        "new_utc_window": today != last_day,
        "top_candidate_is_v134": top["candidate"] == "v134_stable3_guarded_rescue",
        "runmode_complete": has_phrase(runmode, 'Kaggle status: `{"status": "COMPLETE", "failureMessage": ""}`'),
        "schema_valid": has_phrase(runmode, "- has_nan: `False`")
        and has_phrase(runmode, "- has_inf: `False`")
        and has_phrase(runmode, "- range_ok: `True`"),
        "rules_hold_runmode_pass": has_phrase(rules, "Status: `HOLD-RUNMODE-PASS`"),
        "validation_gate_pass": has_phrase(validation, "Pass for guarded candidate-pool retention"),
        "decision_guarded_pool": has_phrase(decision, "`HOLD-RUNMODE-PASS - guarded pool #1`"),
    }

    if not checks["new_utc_window"]:
        verdict = "WAIT-SAME-UTC-DAY"
    elif all(checks.values()):
        verdict = "READY-FOR-GUARDED-RECHECK"
    else:
        verdict = "HOLD-MISSING-EVIDENCE"

    lines = [
        "# v137 v134 Guarded Recheck Status",
        "",
        f"Updated: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "## Snapshot",
        "",
        f"- Current UTC day: `{today}`",
        f"- Last real submission day: `{last_day}`",
        f"- Top scorecard candidate: `{top['candidate']}`",
        f"- Top scorecard window: `{top['submit_window']}`",
        f"- Top scorecard risk: `{top['collapse_risk']}`",
        "",
        "## Checks",
        "",
    ]
    for key, value in checks.items():
        lines.append(f"- {key}: `{value}`")
    lines += ["", "## Verdict", "", f"`{verdict}`", ""]

    if verdict == "WAIT-SAME-UTC-DAY":
        lines += [
            "The evidence package is present, but the UTC window has not rolled over yet.",
        ]
    elif verdict == "READY-FOR-GUARDED-RECHECK":
        lines += [
            "The UTC window is new and v134 still satisfies the current guarded-pool requirements.",
            "This does not auto-submit; it only means the guarded recheck step may proceed.",
        ]
    else:
        lines += [
            "At least one required evidence item is missing or stale. Refresh docs before any guarded submit decision.",
        ]

    if args.write:
        STATUS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"utc_day={today}")
    print(f"last_submission_day={last_day}")
    print(f"top_candidate={top['candidate']}")
    for key, value in checks.items():
        print(f"{key}={value}")
    print(f"verdict={verdict}")
    if args.write:
        print(f"status_path={STATUS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
