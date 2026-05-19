# v140 v134 Guarded State Refresh

Updated: 2026-05-19 13:19:22 UTC

## Inputs

- execute_if_ready: `False`

## Exit Codes

- gate: `0`
- recheck: `0`
- bundle: `0`
- wrapper: `0`

## Outputs

### gate

`python3 scripts/check_v134_next_window_gate.py --write`

```text
utc_day=2026-05-19
last_submission_day=2026-05-19
visible_today=4
top_candidate=v134_stable3_guarded_rescue
kernel_status={"status": "COMPLETE", "failureMessage": ""}
decision=WAIT-SAME-UTC-DAY
status_path=/Users/junhaocheng/working-dir/kaggle-auto/experiments/v136_next_window_gate_status.md
```

### recheck

`python3 scripts/recheck_v134_guarded_candidate.py --write`

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

### bundle

`python3 scripts/check_v134_window_bundle.py --write`

```text
bundle_updated=2026-05-19 13:19:26 UTC
gate_exit=0
recheck_exit=0
goal_exit=3
dryrun_exit=0
status_path=/Users/junhaocheng/working-dir/kaggle-auto/experiments/v138_v134_window_bundle.md
```

### wrapper

`python3 scripts/recheck_and_optionally_submit_v134.py --write`

```text
gate_decision=WAIT-SAME-UTC-DAY
recheck_verdict=WAIT-SAME-UTC-DAY
ready_for_guarded_submit=False
wrapper_verdict=NOT-READY
status_path=/Users/junhaocheng/working-dir/kaggle-auto/experiments/v139_v134_submit_wrapper_status.md
```

