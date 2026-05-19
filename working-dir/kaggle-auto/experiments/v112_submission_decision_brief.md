# v112 Submission Decision Brief

Updated: 2026-05-19 05:32 UTC

## Candidate

- `v112-clean-sed-remap-ecoproto`
- Local path: `birdclef-2026/notebooks/v112-clean-sed-remap-ecoproto`
- Kaggle kernel: `junhaochengadjcjh7u7/bc26-v112-clean-sed-remap`
- Run-mode output: `birdclef-2026/outputs/v112-clean-sed-remap-ecoproto-v1`

## Evidence

- Kaggle Run-mode status: `COMPLETE`.
- Runtime: about `363.2s` before save and about `375.0s` through nbconvert.
- Metadata: private, CPU-only, internet disabled.
- Unknown-license runtime dependencies: none.
- Clean SED source: `backtracking/birdclef2026-clean-sed-b0`, Kaggle metadata license `CC0-1.0`.
- Output artifacts:
  - `submission.csv`
  - `v112_clean_sed_remap_diagnostics.csv`
  - `bc26-v112-clean-sed-remap.log`
- Output schema: `(120,235)`, finite, no duplicate row IDs, score range `[0.01261675, 0.99924165]`.
- Remap diagnostics: `46/234` classes remapped; trust strength mean/max `0.1703/0.8800`.
- Clean SED train-window AUC reference after remap: mean `0.9283`, min `0.7058`, active `71`.
- Proxy: `macro_auc=0.87568304`, `micro_auc=0.83667571`, `top1_hit=0.23287671`, `top5_hit=0.53424658`.
- Correlation: vs v110 `0.779747`, vs v111 `0.867748`, vs v103 `0.649594`.

## Interpretation

v112 is a useful original diagnostic but not a submission candidate. The train-window remap substantially improves internal clean-SED alignment, yet dry-run proxy remains far below v110 clean fallback (`0.97911204`). This suggests the remap is overfitting train soundscape windows or correcting a label-order artifact that does not transfer to the proxy/test distribution.

## Decision

`REJECT - do not submit`

Reason: quality is much weaker than v110, v103, and the current visible anchor. Do not spend a real submission slot on v112.

## Next Action

Do not use direct or remapped `backtracking/birdclef2026-clean-sed-b0` as a strong branch. If continuing clean SED, either:

- audit `lantingguo/birdclef2026-own-sed-b0-v5-onnx` with correct mel preprocessing; or
- keep remap only as a weak diagnostic feature with much stricter class/support gating.
