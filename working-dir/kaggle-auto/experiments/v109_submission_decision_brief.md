# v109 Submission Decision Brief

Updated: 2026-05-19 04:43 UTC

## Candidate

- `v109-ecoproto-ranklaunch-perch`
- Local path: `birdclef-2026/notebooks/v109-ecoproto-ranklaunch-perch`
- Kaggle kernel: `junhaochengadjcjh7u7/bc26-v109-ecoproto-ranklaunch`
- Run-mode output: `birdclef-2026/outputs/v109-ecoproto-ranklaunch-perch-v1`

## Evidence

- Kaggle Run-mode status: `COMPLETE`.
- Runtime: about `340.6s` before save and about `345.8s` through nbconvert.
- Metadata: private, CPU-only, internet disabled.
- Unknown-license runtime dependencies: none.
- Output: `submission.csv` shape `(120,235)`, finite, no duplicate row IDs, range `[0.011144416, 0.999315100]`.
- Proxy: `macro_auc=0.97963460`, `micro_auc=0.91325592`, `top1_hit=0.23287671`, `top5_hit=0.47945205`.

## Decision

`HOLD - do not submit now`

Reason: v109 is the strongest license-clean branch by macro proxy and proves that the original EcoProto signal can be combined with row-rank restoration. However, its top-hit proxy remains below v107 (`top5=0.47945205` vs `0.50684932`) and far below v103 (`0.71232877`), so it is still unlikely to beat the current `0.949` anchor.

## Follow-Up

Local blend probing suggests `0.4*v107 + 0.6*v109` by probability blend improves top5 to `0.52054795` while keeping macro `0.97911204`. This is a plausible v110 direction, but it still lacks enough evidence to spend a real submission slot without further validation.

