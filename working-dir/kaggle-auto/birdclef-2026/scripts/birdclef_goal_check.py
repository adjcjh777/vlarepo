#!/usr/bin/env python3
"""Check BirdCLEF leaderboard position and completion gates."""

from __future__ import annotations

from datetime import datetime, timezone
import time

from kaggle.api.kaggle_api_extended import KaggleApi


COMPETITION = "birdclef-2026"
TEAM_NAME = "JUNHAO CHENG (adjcjh7u7)"
MAX_RETRIES = 3
RETRY_SLEEP_SECONDS = 2.0


def score_float(value: object) -> float | None:
    try:
        text = str(value)
        if not text:
            return None
        return float(text)
    except (TypeError, ValueError):
        return None


def original_like(sub: object) -> bool:
    desc = str(getattr(sub, "description", "") or "").lower()
    blocked = ["public-reference", "not original", "attributed public", "derivative of"]
    return not any(token in desc for token in blocked)


def call_with_retry(fn, label: str):
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            print(f"{label}_attempt_{attempt}=FAILED")
            print(f"{label}_error_{attempt}={type(exc).__name__}: {exc}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_SLEEP_SECONDS)
    raise last_exc


def main() -> int:
    api = KaggleApi()
    api.authenticate()

    try:
        rows = call_with_retry(lambda: api.competition_leaderboard_view(COMPETITION), "leaderboard_view")
    except Exception as exc:  # noqa: BLE001
        print("checked_at_utc=", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
        print("leaderboard_rows_returned=FAILED")
        print(f"leaderboard_final_error={type(exc).__name__}: {exc}")
        print("GOAL_GATE=CHECK_FAILED_TRANSIENT")
        return 4

    top_scores = [score_float(row.score) for row in rows]
    top_scores = [s for s in top_scores if s is not None]
    top5_cutoff = top_scores[4] if len(top_scores) >= 5 else None
    top20_cutoff = top_scores[19] if len(top_scores) >= 20 else None

    print("checked_at_utc=", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
    print("leaderboard_rows_returned=", len(rows))
    print("top5_cutoff=", top5_cutoff)
    print("top20_cutoff=", top20_cutoff)

    team_row = None
    for idx, row in enumerate(rows, 1):
        if row.team_name == TEAM_NAME:
            team_row = (idx, row)
            break

    try:
        subs = call_with_retry(lambda: api.competition_submissions(COMPETITION)[:50], "competition_submissions")
    except Exception as exc:  # noqa: BLE001
        print("competition_submissions_final_error=", f"{type(exc).__name__}: {exc}")
        print("GOAL_GATE=CHECK_FAILED_TRANSIENT")
        return 4
    scored = [(score_float(s.public_score), s) for s in subs if score_float(s.public_score) is not None]
    best = max(scored, key=lambda x: x[0]) if scored else (None, None)
    best_score, best_sub = best
    original_scored = [(score, sub) for score, sub in scored if original_like(sub)]
    best_original = max(original_scored, key=lambda x: x[0]) if original_scored else (None, None)
    best_original_score, best_original_sub = best_original

    if team_row is not None:
        rank, row = team_row
        score = score_float(row.score)
        print("team_rank_known=", True)
        print("team_rank=", rank)
        print("team_score=", score)
        print("team_submission_date=", row.submission_date)
    else:
        print("team_rank_known=", False)
        print("team_rank=not_in_returned_top20")
        print("team_best_visible_submission_score=", best_score)
        if best_sub is not None:
            print("team_best_visible_submission_date=", best_sub.date)
            print("team_best_visible_submission_desc=", (best_sub.description or "")[:180])
        print("team_best_original_like_submission_score=", best_original_score)
        if best_original_sub is not None:
            print("team_best_original_like_submission_date=", best_original_sub.date)
            print("team_best_original_like_submission_desc=", (best_original_sub.description or "")[:180])

    if team_row is not None and team_row[0] <= 5:
        print("GOAL_GATE=TOP5_REACHED_VERIFY_PRIZE_AND_FINAL_SELECTION")
        return 0
    if top5_cutoff is not None and best_score is not None and best_score >= top5_cutoff:
        print("GOAL_GATE=SCORE_AT_TOP5_CUTOFF_BUT_RANK_NOT_CONFIRMED")
        return 1
    if team_row is not None and team_row[0] <= 20:
        print("GOAL_GATE=TOP20_REACHED_NOT_TOP5")
        return 2
    if top20_cutoff is not None and best_score is not None:
        print("gap_to_top20=", round(top20_cutoff - best_score, 6))
        print("gap_to_top5=", round(top5_cutoff - best_score, 6) if top5_cutoff is not None else None)
    if top20_cutoff is not None and best_original_score is not None:
        print("original_like_gap_to_top20=", round(top20_cutoff - best_original_score, 6))
        print(
            "original_like_gap_to_top5=",
            round(top5_cutoff - best_original_score, 6) if top5_cutoff is not None else None,
        )
    print("GOAL_GATE=NOT_REACHED")
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
