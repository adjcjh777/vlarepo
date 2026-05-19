# v139 v134 Submit Wrapper Status

Updated: 2026-05-19 13:26:57 UTC

## Inputs

- execute_if_ready: `False`

## Gate Summary

- gate_decision: `WAIT-SAME-UTC-DAY`
- recheck_verdict: `WAIT-SAME-UTC-DAY`
- bundle_gate_exit: `0`
- bundle_recheck_exit: `0`
- bundle_goal_exit: `3`
- guarded_submit_dryrun_exit: `0`
- ready_for_guarded_submit: `False`

## Wrapper Verdict

`NOT-READY`

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

## Bundle Output

```text
bundle_updated=2026-05-19 13:27:04 UTC
gate_exit=0
recheck_exit=0
goal_exit=3
dryrun_exit=0
status_path=/Users/junhaocheng/working-dir/kaggle-auto/experiments/v138_v134_window_bundle.md
```

## Guarded Submit Dry-Run Output

```text
utc_today=2026-05-19
visible_today_count=4
1 2026-05-19 10:27:41.813000 | SubmissionStatus.COMPLETE | score= '0.883' | err= '' | Original clean v127: memory-safe non-Tsubasa raw-side router over v110 EcoProto anchor; CPU-only Run-mode COMPLETE ~390s; Backtracking/Roniheka CC0 side evidenc
2 2026-05-19 07:49:31 | SubmissionStatus.COMPLETE | score= '' | err= 'Your notebook requested more memory (RAM) than is available.' | Original clean v120: Perch-only clean anchor plus 0.15 CC0 Tsubasa ConvNeXt SED sidecar; CPU-only Run-mode COMPLETE ~683s; no unknown-license runtime inputs
3 2026-05-19 02:48:14.867000 | SubmissionStatus.COMPLETE | score= '0.898' | err= '' | v101 Alexy CNN CPU-only guarded submit
4 2026-05-19 00:33:39.303000 | SubmissionStatus.COMPLETE | score= '0.948' | err= '' | Attributed public-reference derivative of cocoaai/bc26-youssef-e1-rare-tail-birdnet with BirdNET disabled for license compatibility; v91 keeps Proto/SED rare-ta
5 2026-05-18 11:06:18.053000 | SubmissionStatus.COMPLETE | score= '0.921' | err= '' | Attributed public-reference derivative of zeyadmohamadezzat/birdclef-2026-eos-parity-inference; v88 EOS Parity T3 uses quantile-mix rank blend with four Proto/S
6 2026-05-18 06:04:44 | SubmissionStatus.COMPLETE | score= '0.949' | err= '' | Attributed public-reference derivative of nina2025/birdclef-2026-eos-5; v87 anchors on prior 0.948 public-reference result and uses EoS5 0.04/0.96 Model_2+rank-
7 2026-05-18 03:45:13.937000 | SubmissionStatus.COMPLETE | score= '0.925' | err= '' | Original private mid-support probe-rescue v86; conservative v84 anchor plus controlled v70-style probe signal; CPU-only Run-mode validated; no public notebook c
8 2026-05-18 00:43:47.007000 | SubmissionStatus.COMPLETE | score= '0.925' | err= '' | Original private support-gated dual-probe v79; CPU-safe Run-mode ~247s; safe fallback if v76 underperforms
candidate_key= v134
candidate_kernel= junhaochengadjcjh7u7/bc26-v134-stable3-guarded-rescue
candidate_version= 1
candidate_file= submission.csv
candidate_priority= next guarded-pool candidate after v127 fallout; do not submit without fresh slot and anti-collapse review
candidate_status= {"status": "COMPLETE", "failureMessage": ""}
candidate_message= Original clean v134: stable3 guarded rescue over v110 EcoProto anchor; CPU-only Run-mode COMPLETE; backtracking-only clean side evidence; top-hit preservation guard; no prior CSV mounts
v76_gate_row_found= True
v76_gate_score= 0.925
DRY_RUN: pass --execute after confirming quota reset and candidate choice.
```

