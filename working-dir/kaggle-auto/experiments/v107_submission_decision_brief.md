# v107 Submission Decision Brief

Updated: 2026-05-19 04:23 UTC

## Candidate

- `v107-rankceiling-perch-guarded`
- Local path: `birdclef-2026/notebooks/v107-rankceiling-perch-guarded`
- Kaggle kernel: `junhaochengadjcjh7u7/bc26-v107-rankceiling-perch`
- Run-mode output: `birdclef-2026/outputs/v107-rankceiling-perch-guarded-v1`

## Evidence

- Kaggle Run-mode status: `COMPLETE`.
- Runtime: about `316.8s` before save and about `327.1s` through nbconvert.
- Metadata: private, CPU-only, internet disabled.
- Unknown-license runtime dependencies: none.
- Output: `submission.csv` shape `(120,235)`, finite, no duplicate row IDs, range `[0.011144416, 0.9997021]`.
- Proxy: `macro_auc=0.97736356`, `micro_auc=0.91282668`, `top1_hit=0.27397260`, `top5_hit=0.50684932`.

## Decision

`HOLD - do not submit now`

Reason: v107 is the best license-clean Perch-only branch, but it still trails v103 by a large macro/top5 margin and is unlikely to beat the current `0.949` anchor without a stronger SED-like signal.

## Next Action

Audit license-clean SED-like sources or build an internal distillation signal before spending another real submission slot.
