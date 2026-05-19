#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi


ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments"
STATUS_PATH = EXP / "v136_next_window_gate_status.md"
SCORECARD = EXP / "v133_next_candidate_scorecard.csv"
LEDGER = EXP / "submission_ledger.csv"
TOP_CANDIDATE = "v134_stable3_guarded_rescue"
KERNEL = "junhaochengadjcjh7u7/bc26-v134-stable3-guarded-rescue"
COMPETITION = "birdclef-2026"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_day(ts: str) -> str:
    return str(ts).split(" ")[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write status markdown")
    args = parser.parse_args()

    now = utc_now()
    today = now.strftime("%Y-%m-%d")

    ledger = pd.read_csv(LEDGER)
    scorecard = pd.read_csv(SCORECARD)
    api = KaggleApi()
    api.authenticate()
    submissions = api.competition_submissions(COMPETITION)[:20]
    today_visible = [s for s in submissions if str(s.date).startswith(today)]
    kernel_status = api.kernels_status(KERNEL)

    last_submission_day = utc_day(str(ledger.iloc[-1]["timestamp"]))
    anchor_score = 0.949
    top_row = scorecard.iloc[0]
    top_candidate_ok = str(top_row["candidate"]) == TOP_CANDIDATE
    top_candidate_risk = str(top_row["collapse_risk"])
    top_candidate_window = str(top_row["submit_window"])

    if today == last_submission_day:
        decision = "WAIT-SAME-UTC-DAY"
    elif not top_candidate_ok:
        decision = "RECHECK-RANKING"
    elif "COMPLETE" not in str(kernel_status):
        decision = "WAIT-RUNMODE"
    else:
        decision = "READY-FOR-GUARDED-RECHECK"

    lines = [
        "# v136 Next Window Gate Status",
        "",
        f"Updated: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "## Snapshot",
        "",
        f"- Current UTC day: `{today}`",
        f"- Last real submission day in ledger: `{last_submission_day}`",
        f"- Visible submissions on current UTC day: `{len(today_visible)}`",
        f"- Current anchor score: `{anchor_score}`",
        f"- Top scorecard candidate: `{top_row['candidate']}`",
        f"- Top candidate window: `{top_candidate_window}`",
        f"- Top candidate risk: `{top_candidate_risk}`",
        f"- v134 kernel status: `{kernel_status}`",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Meaning",
        "",
    ]

    if decision == "WAIT-SAME-UTC-DAY":
        lines += [
            "- UTC day has not rolled over yet.",
            "- Do not spend the final same-day slot.",
        ]
    elif decision == "RECHECK-RANKING":
        lines += [
            "- v134 is no longer the top guarded candidate.",
            "- Rebuild and inspect the anti-collapse ranking before any submit action.",
        ]
    elif decision == "WAIT-RUNMODE":
        lines += [
            "- v134 is still missing a completed external Run-mode status.",
            "- Do not promote it until that evidence exists.",
        ]
    else:
        lines += [
            "- A new UTC window is open.",
            "- v134 remains the guarded-pool leader and its external Run-mode is complete.",
            "- This does not auto-submit; it only means a guarded human-reviewed recheck is now allowed.",
        ]

    if args.write:
        STATUS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"utc_day={today}")
    print(f"last_submission_day={last_submission_day}")
    print(f"visible_today={len(today_visible)}")
    print(f"top_candidate={top_row['candidate']}")
    print(f"kernel_status={kernel_status}")
    print(f"decision={decision}")
    if args.write:
        print(f"status_path={STATUS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
