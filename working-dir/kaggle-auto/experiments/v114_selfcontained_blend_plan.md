# v114 Self-Contained v110/v113 Blend Plan

Updated: 2026-05-19 05:56 UTC

## Motivation

The local v113 probe found a tiny improvement from `0.85*v110 + 0.15*v113`:

- v110 standalone: `macro=0.97911204`
- v113 standalone: `macro=0.97755927`
- local blend probe: `macro=0.979201`

That gain cannot justify a real submission as a local CSV blend. v114 materializes the same idea as a self-contained Kaggle notebook.

## Mechanism

`v114-v110-v113-selfblend` starts from the v113 notebook but keeps two branch views:

- `v110_like`: Perch-only clean fallback SED surrogate;
- `v113_like`: LantingGuo MelNormProbe sidecar;
- the final layer is wrapped into `_compute_v114_branch(...)` and run twice;
- final predictions are `0.85*v110_like + 0.15*v113_like`;
- diagnostics are emitted as `v114_branch_summary.csv` and `v114_branch_auc_diagnostics.csv`.

The notebook does not mount or read local prior output CSVs.

## Original Contribution Boundary

This is intended as a small, auditable original step rather than another direct
public-notebook reference:

- the branch pair is recomputed inside one Kaggle notebook, so the blend is not a
  post-hoc CSV merge of earlier submissions;
- the second branch uses our own MelNormProbe view selection and class-level
  trust shrinkage from v113, not a raw borrowed prediction file;
- the final weight stays deliberately conservative because v113 only improved
  the local probe by a tiny amount and remains highly correlated with v110;
- `v114_branch_auc_diagnostics.csv` records per-class support, branch AUCs, and
  branch deltas so later promotion/rejection has evidence beyond public LB.

## Compliance

- CPU-only.
- Internet disabled.
- No unknown-license runtime dependency.
- Runtime metadata uses competition data, Perch ONNX, Google Perch, and `lantingguo/birdclef2026-own-sed-b0-v5-onnx` (`CC0-1.0`).
- No real Kaggle submission unless Run-mode proxy and diagnostics justify spending a daily slot.

## Decision Rule

Promote only if v114 Run-mode output reproduces or improves the local blend proxy and remains within runtime limits. If the gain is still only microscopic or correlation remains too high, keep it as HOLD instead of spending a real submission slot.

## Run-Mode Result

- Status: `COMPLETE`
- Runtime before saved output: about `535.5s`
- Proxy: `macro=0.97920102`, `micro=0.91572402`, `top1=0.23287671`, `top5=0.52054795`
- Correlation vs v110: Pearson `0.999594`
- Decision: `HOLD - do not submit`; the notebook is clean and self-contained, but the gain over v110 is microscopic and too highly correlated for a real slot.
