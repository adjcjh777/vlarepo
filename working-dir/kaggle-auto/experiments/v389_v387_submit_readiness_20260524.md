# v389 v387 Submit-readiness Audit

Updated: 2026-05-24 15:06:23 UTC

Status: `READY-v387-submit-readiness-AWAIT-EXPLICIT-SUBMIT-GATE`.

## Research Question

Does v387 have enough Run-mode, static, promotion, class-risk, quota, duplicate, and pending-submission evidence to even consider a separate real competition-submit gate?

## Result

- Blocker count: `0`
- Blockers: `[]`
- Run-mode decision: `READY-v387-runmode-dryrun-runtime-proof`
- Static decision: `READY-v387-v386-static-materializer-audit-NO-PUSH-NO-SUBMIT`
- Class-risk decision: `READY-v388-v387-class-risk-pass-NO-PUSH-NO-SUBMIT`
- Live pending: `0`
- Visible submissions today: `2`
- Duplicate v387: `False`

## Checks

| check | status | blocker | evidence |
|---|---|---:|---|
| v387_runmode_ready | PASS | False | decision=READY-v387-runmode-dryrun-runtime-proof runtime_seconds=298 |
| v387_runmode_not_failed | PASS | False | decision=READY-v387-runmode-dryrun-runtime-proof |
| v387_static_ready | PASS | False | decision=READY-v387-v386-static-materializer-audit-NO-PUSH-NO-SUBMIT |
| v387_static_no_blockers | PASS | False | block_count=0 |
| macro_gate | PASS | False | macro_gain=0.0029182569766682542 |
| weak_gate | PASS | False | weak_followup_gain=0.009171664783814482 |
| top5_no_regression | PASS | False | top5=0.5068493150684932->0.5068493150684932 |
| fold_std_not_worse | PASS | False | fold_std_delta=-0.0008302581915264617 |
| class_risk_pass | PASS | False | decision=READY-v388-v387-class-risk-pass-NO-PUSH-NO-SUBMIT block_count=0 |
| no_live_pending | PASS | False | pending=0 today_count=2 |
| submission_quota_visible | PASS | False | today_count=2 |
| no_duplicate_v387_submission | PASS | False | duplicate_v387=False |
| explicit_competition_submit_not_made | PASS | False | this audit has no submit call |

## Decision

- `READY-v387-submit-readiness-AWAIT-EXPLICIT-SUBMIT-GATE`
- Next: A separate guarded competition-submit command can be considered only with explicit authorization and fresh final checks.
