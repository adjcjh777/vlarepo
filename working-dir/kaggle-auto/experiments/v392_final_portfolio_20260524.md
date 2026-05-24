# v392 Final Portfolio Audit

Updated: 2026-05-24 15:31:50 UTC

Status: `READY-final-portfolio-safe-v391-bold-v387`.

## Research Question

Do we currently have a safe_final and bold_final pair that satisfies the final-candidate rule without making a real competition submission?

## Candidate Roles

- `bold_final`: `v387-v386-static-distill`, macro_gain `+0.00291826`, fold_std_delta `-0.00083026`, weak_gain `+0.00917166`, status `SUBMITTED-v387-competition-pending`
- `safe_final`: `v391-v386-safe-static-distill`, macro_gain `+0.00282022`, fold_std_delta `-0.00188085`, weak_gain `+0.00886356`, runmode `READY-v391-runmode-dryrun-runtime-proof`

## Checks

- `bold_v387_submit_ready`: `True`
- `safe_v391_static_ready`: `True`
- `safe_v391_runmode_ready_or_pending`: `True`
- `safe_has_lower_fold_std_delta_than_bold`: `True`
- `safe_has_fewer_active_cells_than_bold`: `True`
- `both_pass_macro_gate`: `True`
- `both_pass_weak_gate`: `True`

## Decision

- `READY-final-portfolio-safe-v391-bold-v387`
- Next: Use v387 as bold_final and v391 as safe_final; require explicit authorization for any real submit.
