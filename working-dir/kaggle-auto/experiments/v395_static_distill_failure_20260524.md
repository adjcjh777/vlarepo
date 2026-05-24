# v395 Static-distill Family Failure Audit

Updated: 2026-05-24 15:46:48 UTC

Status: `RETIRE-static-distill-family-NO-SUBMIT`.

## Research Question

After v387 scored publicly, should any v380/v383/v387/v391/v394 fixed-coefficient static-distill sibling remain submit-eligible?

## Evidence

- v387 public score: `0.881`
- Visible anchor/best to beat: `0.949`
- Delta vs anchor: `-0.068`
- v387 ledger reason: score underperformed 0.949 anchor; retire v387 unless a concrete implementation bug is found
- v387 notes: v387 v386 parameter-stressed fixed-coefficient distill over the clean v107 Perch anchor; uses hidden-test-computable row_id temporal context and train soundscape priors, retains real sample-row guards, CPU-only no-internet; submitted only after v387 Run-mode runtime proof, v388 class-risk audit, and v389 submit-readiness gate

## Family Decision

| member | status | local_macro_gain | fold_std_delta | weak_followup_gain | submit_allowed |
|---|---|---:|---:|---:|---|
| v380 | RETIRE-family-extrapolation-risk | 0.0016012025357819981 | -0.0002265860787013796 | 0.00503235082674347 | False |
| v383 | RETIRE-family-extrapolation-risk | 0.0016012025357819981 | -0.0002265860787013796 | 0.00503235082674347 | False |
| v387 | RETIRE-scored-collapse | 0.0029182569766682542 | -0.0008302581915264617 | 0.009171664783814482 | False |
| v391 | BLOCK-sibling-of-scored-collapse | 0.0028202241683551454 | -0.0018808458385290716 | 0.008863561671973108 | False |
| v394 | BLOCK-blend-of-scored-collapse | 0.0030816449905235466 | -0.0018808458385290716 | 0.009685169970216734 | False |

## Decision

- `RETIRE-static-distill-family-NO-SUBMIT`
- Do not submit v383, v391, or v394 after v387's public collapse.
- Next action: pivot to a non-static-distill route with hidden-test-computable evidence, or protect the 0.949 visible-best fallback.
