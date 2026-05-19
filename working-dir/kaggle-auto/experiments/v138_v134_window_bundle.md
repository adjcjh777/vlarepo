# v138 v134 Window Bundle

Updated: 2026-05-19 12:48:54 UTC

## Commands

- `python3 scripts/check_v134_next_window_gate.py --write`
- `python3 scripts/recheck_v134_guarded_candidate.py --write`
- `python3 birdclef-2026/scripts/birdclef_goal_check.py --submissions-limit 20`

## Exit Codes

- gate: `0`
- recheck: `0`
- goal_check: `3`

## Gate Output

```text
utc_day=2026-05-19
last_submission_day=2026-05-19
visible_today=4
top_candidate=v134_stable3_guarded_rescue
kernel_status={"status": "COMPLETE", "failureMessage": ""}
decision=WAIT-SAME-UTC-DAY
status_path=/Users/junhaocheng/working-dir/kaggle-auto/experiments/v136_next_window_gate_status.md
```

## Recheck Output

```text
utc_day=2026-05-19
last_submission_day=2026-05-19
top_candidate=v134_stable3_guarded_rescue
new_utc_window=False
top_candidate_is_v134=True
runmode_complete=True
schema_valid=True
rules_hold_runmode_pass=True
validation_gate_pass=True
decision_guarded_pool=True
verdict=WAIT-SAME-UTC-DAY
status_path=/Users/junhaocheng/working-dir/kaggle-auto/experiments/v137_v134_guarded_recheck_status.md
```

## Goal Check Output

```text
checked_at_utc= 2026-05-19 12:49:05 UTC
leaderboard_rows_returned= 20
top5_cutoff= 0.958
top20_cutoff= 0.954
team_rank_known= False
team_rank=not_in_returned_top20
team_best_visible_submission_score= 0.949
team_best_visible_submission_date= 2026-05-18 06:04:44
team_best_visible_submission_desc= Attributed public-reference derivative of nina2025/birdclef-2026-eos-5; v87 anchors on prior 0.948 public-reference result and uses EoS5 0.04/0.96 Model_2+rank-power-0.949 blend; C
team_best_original_like_submission_score= 0.925
team_best_original_like_submission_date= 2026-05-18 03:45:13.937000
team_best_original_like_submission_desc= Original private mid-support probe-rescue v86; conservative v84 anchor plus controlled v70-style probe signal; CPU-only Run-mode validated; no public notebook code copied
gap_to_top20= 0.005
gap_to_top5= 0.009
original_like_gap_to_top20= 0.029
original_like_gap_to_top5= 0.033
GOAL_GATE=NOT_REACHED
```

