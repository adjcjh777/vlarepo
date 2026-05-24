# Submission Result: v387

Updated: 2026-05-24 15:37:07 UTC

## Candidate

- Name: `v387-dryrun-tolerant-static-distill`
- Kernel: `junhaochengadjcjh7u7/bc26-v387-v386-static-distill`
- Kernel version: `1`
- Kaggle ref: `52991496`
- UTC-day visible slot: `3`

## Current Status

`WAIT-pending`

- Kaggle status: `SubmissionStatus.PENDING`
- Public score: ``
- Error: ``
- Latest check: `2026-05-24 15:37:07 UTC`

## Why It Was Submitted

v387 is the v386 parameter-stressed fixed-coefficient distillation route over the clean v107 Perch anchor. It uses hidden-test-computable row_id temporal context and train soundscape priors, passed v388 class-risk audit, and was submitted after v389/v390 readiness gates.

Pre-submit evidence:

- v387 Run-mode decision was `READY-v387-runmode-dryrun-runtime-proof`.
- Kaggle kernel status was `COMPLETE`.
- Dry-run schema/range/log checks passed and runtime was 298 seconds.
- Static metrics: macro_gain `+0.00291826`, fold_std_delta `-0.00083026`, weak_followup_gain `+0.00917166`.
- v388 class-risk audit found no class regression below `-0.001` and no fold regression below `-0.001`.

## Post-score Rule

- If public score improves beyond `0.949`, record the new visible best and start protection planning.
- If public score reaches `0.955+`, compare against Top20/Top5 and prepare final/fallback strategy.
- If public score ties/drops/errors, hold or retire v387 before spending a sibling route slot.

## Kaggle Description

v387 v386 parameter-stressed fixed-coefficient distill over the clean v107 Perch anchor; uses hidden-test-computable row_id temporal context and train soundscape priors, retains real sample-row guards, CPU-only no-internet; submitted only after v387 Run-mode runtime proof, v388 class-risk audit, and v389 submit-readiness gate
