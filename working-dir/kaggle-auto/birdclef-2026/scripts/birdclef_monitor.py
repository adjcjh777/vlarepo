#!/usr/bin/env python3
"""Monitor BirdCLEF 2026 submissions and print quota-aware next actions."""

from __future__ import annotations

import argparse
import re
import time
from datetime import datetime, timezone

from kaggle.api.kaggle_api_extended import KaggleApi


COMPETITION = "birdclef-2026"
TEAM_NAME = "JUNHAO CHENG (adjcjh7u7)"


def utc_day_prefix() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def score_float(value: object) -> float | None:
    try:
        text = str(value)
        if not text:
            return None
        return float(text)
    except (TypeError, ValueError):
        return None


def is_candidate_submission(sub: object, candidate: str) -> bool:
    candidate = candidate.lower()
    haystack = " ".join(
        str(x or "")
        for x in [
            getattr(sub, "description", ""),
            getattr(sub, "url", ""),
            getattr(sub, "file_name", ""),
        ]
    ).lower()
    return bool(
        re.search(rf"\bbc26-{re.escape(candidate)}(?:-|/|\b)", haystack)
        or re.search(rf"\b{re.escape(candidate)}(?:;|,)", haystack)
    )


def print_submissions(subs: list[object], utc_today: str) -> None:
    today_count = sum(str(s.date).startswith(utc_today) for s in subs)
    print(f"utc_today={utc_today}")
    print(f"visible_today_count={today_count}")
    for i, sub in enumerate(subs[:8], 1):
        print(
            i,
            sub.date,
            "|",
            sub.status,
            "| score=",
            repr(sub.public_score),
            "| err=",
            repr(sub.error_description),
            "|",
            (sub.description or "")[:160],
        )


def leaderboard_summary(api: KaggleApi) -> tuple[float | None, float | None]:
    rows = api.competition_leaderboard_view(COMPETITION)
    scores = [score_float(row.score) for row in rows]
    scores = [s for s in scores if s is not None]
    top5 = scores[4] if len(scores) >= 5 else None
    top20 = scores[19] if len(scores) >= 20 else None
    print(f"leaderboard_top5_cutoff={top5}")
    print(f"leaderboard_top20_cutoff={top20}")
    return top5, top20


def recommendation(
    candidate: str,
    target: object | None,
    submissions: list[object],
    today_count: int,
    top5: float | None,
    top20: float | None,
    anchor_score: float,
    anchor_maintenance_ceiling: float,
    promising_score: float,
    weak_score: float,
    daily_limit: int,
) -> str:
    if target is None:
        if today_count == 0:
            return "NEXT: submit v76 with birdclef_guarded_submit.py after dry-run passes."
        if today_count >= daily_limit:
            return "NEXT: wait for the next UTC quota reset; current UTC day is already at the daily limit."
        return "NEXT: no target submission found today; do not spend another slot without a fresh decision."

    status = str(getattr(target, "status", ""))
    err = str(getattr(target, "error_description", "") or "")
    score = score_float(getattr(target, "public_score", ""))

    if err:
        if candidate == "v91":
            return (
                "NEXT: v91 errored; inspect hidden-rerun logs before any slot-two action. "
                "Do not fall back to v90 because v90 was held for BirdNET CC BY-NC license risk."
            )
        if candidate == "v87":
            return (
                "NEXT: v87 errored; inspect logs. If the failure is row alignment, NaN, "
                "or final CSV mechanics, validate an S106-style safe-align recovery before "
                "considering the fifth slot."
            )
        return "NEXT: target submission errored; inspect notebook logs before any second slot."
    if score is None or "PENDING" in status or "SCORING" in status:
        return "NEXT: wait; target score is not available yet."
    if top5 is not None and score >= top5:
        return "NEXT: top-5 cutoff reached or tied; verify rank before marking goal complete."
    if top20 is not None and score >= top20:
        if candidate == "v91":
            return (
                "NEXT: v91 reached the live top-20 cutoff; rerun birdclef_goal_check.py, "
                "preserve quota, and enter protection/verification mode before any slot-two action."
            )
        if candidate == "v87":
            return (
                "NEXT: v87 reached the live top-20 cutoff; rerun birdclef_goal_check.py, "
                "compare the current top-5 cutoff, and preserve the final slot until a "
                "specific score-push candidate is validated."
            )
        return "NEXT: top-20 reached; preserve quota and plan final-selection strategy."

    if candidate == "v91":
        slot_note = (
            " Current UTC quota is full, so do not submit today."
            if today_count >= daily_limit
            else " Keep slot two locked until a materially different candidate has Run-mode evidence."
        )
        if score < 0.949:
            return (
                f"NEXT: v91 scored {score:.3f}, below the v87 anchor 0.949; retire the "
                "BirdNET-disabled E1 route as a real-submission path and do not submit v90 "
                "because of the BirdNET CC BY-NC license risk."
                + slot_note
            )
        return (
            f"NEXT: v91 scored {score:.3f}; this is anchor maintenance below the live top-20 "
            "cutoff. Require a fresh, non-near-duplicate Run-mode candidate plus provenance "
            "checks before spending slot two."
            + slot_note
        )

    if candidate == "v87":
        slot_note = (
            " Current UTC quota is full, so do not submit today."
            if today_count >= daily_limit
            else " Keep the final daily slot locked until Run-mode evidence exists."
        )
        if score < anchor_score:
            return (
                f"NEXT: v87 scored {score:.3f}, below the v38 anchor {anchor_score:.3f}; "
                "retire EoS5 near-duplicates for today and prepare current EOS Parity T3 "
                "as a Kaggle Run-mode-only validation candidate."
                + slot_note
            )
        if score <= anchor_maintenance_ceiling:
            return (
                f"NEXT: v87 scored {score:.3f}; this maintains the {anchor_score:.3f} anchor "
                "but is not top-20 progress. Only prepare EOS Parity T3 after validating "
                "that its output is materially different from v87/v38."
                + slot_note
            )
        return (
            f"NEXT: v87 improved over the {anchor_score:.3f} anchor but remains below top-20; "
            "use EOS Parity T3 for Run-mode evidence, and spend the final slot only after "
            "valid submission diagnostics, CPU < 90 minutes, and material output difference."
            + slot_note
        )

    if score >= promising_score:
        return "NEXT: v76 looks promising; consider v83 first, with v84 as conservative alternate."
    v79_done = next((s for s in submissions if is_candidate_submission(s, "v79") and score_float(getattr(s, "public_score", "")) is not None), None)
    if v79_done is not None:
        return "NEXT: v76 and v79 have both scored below target; retire the old v76/v83/v84/v79 queue and require a fresh candidate before spending another slot."
    if score < weak_score:
        return "NEXT: v76 underperformed; prefer v79 fallback or pause for a new idea before spending slot two."
    return "NEXT: borderline score; wait for stabilization and compare v83/v84/v79 risk before slot two."


def run_once(args: argparse.Namespace) -> bool:
    api = KaggleApi()
    api.authenticate()
    utc_today = utc_day_prefix()
    subs = api.competition_submissions(COMPETITION)[:20]
    today_count = sum(str(s.date).startswith(utc_today) for s in subs)
    print("checked_at_utc=", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
    print_submissions(subs, utc_today)
    top5, top20 = leaderboard_summary(api)
    target = next((s for s in subs if is_candidate_submission(s, args.candidate)), None)
    if target is None:
        print(f"target_candidate={args.candidate} not_found")
    else:
        print(
            f"target_candidate={args.candidate}",
            "| date=",
            target.date,
            "| status=",
            target.status,
            "| score=",
            repr(target.public_score),
            "| url=",
            getattr(target, "url", ""),
        )
    print(
        recommendation(
            args.candidate,
            target,
            subs,
            today_count,
            top5,
            top20,
            args.anchor_score,
            args.anchor_maintenance_ceiling,
            args.promising_score,
            args.weak_score,
            args.daily_limit,
        )
    )
    return target is not None and score_float(getattr(target, "public_score", "")) is not None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", default="v76", help="candidate key to find in recent submissions")
    parser.add_argument("--watch", action="store_true", help="poll until target score/error appears")
    parser.add_argument("--interval", type=int, default=300, help="watch polling interval in seconds")
    parser.add_argument("--max-minutes", type=int, default=240, help="watch time budget")
    parser.add_argument("--promising-score", type=float, default=0.948)
    parser.add_argument("--weak-score", type=float, default=0.943)
    parser.add_argument("--anchor-score", type=float, default=0.948)
    parser.add_argument("--anchor-maintenance-ceiling", type=float, default=0.950)
    parser.add_argument("--daily-limit", type=int, default=5)
    args = parser.parse_args()

    if not args.watch:
        run_once(args)
        return 0

    deadline = time.monotonic() + args.max_minutes * 60
    while True:
        done = run_once(args)
        if done:
            return 0
        if time.monotonic() >= deadline:
            print("WATCH_TIMEOUT: target score not available within time budget.")
            return 4
        print(f"sleeping_seconds={args.interval}")
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
