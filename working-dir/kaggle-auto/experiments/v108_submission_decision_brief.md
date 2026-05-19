# v108 Submission Decision Brief

Updated: 2026-05-19 04:31 UTC

## Candidate

- `v108-ecoproto-perch-guarded`
- Local path: `birdclef-2026/notebooks/v108-ecoproto-perch-guarded`
- Kaggle kernel: `junhaochengadjcjh7u7/bc26-v108-ecoproto-perch`
- Run-mode output: `birdclef-2026/outputs/v108-ecoproto-perch-guarded-v1`

## Evidence

- Kaggle Run-mode status: `COMPLETE`.
- Runtime: about `334.3s` before save and about `339.4s` through nbconvert.
- Metadata: private, CPU-only, internet disabled.
- Unknown-license runtime dependencies: none.
- Output: `submission.csv` shape `(120,235)`, finite, no duplicate row IDs, range `[0.011144416, 0.999291660]`.
- Proxy: `macro_auc=0.97881000`, `micro_auc=0.82693410`, `top1_hit=0.00000000`, `top5_hit=0.08219178`.

## Decision

`REJECT - do not submit`

Reason: EcoProto is a genuine original signal and improves macro over v107, but it does not recover row-level top-hit behavior. Its `top5_hit=0.08219178` is far below v107 (`0.50684932`) and v103 (`0.71232877`), so it is unlikely to beat the current `0.949` anchor.

## Next Action

Promote EcoProto from a standalone rescue layer into a rank-launch layer: build v109 to combine EcoProto with v107-style row-rank restoration while keeping license-clean runtime inputs.

