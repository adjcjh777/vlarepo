# v123 Submission Decision Brief

Updated: 2026-05-19 09:21 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v123-rankcal-singlepass-tsubasa/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v123-rankcal-singlepass`
- Output: `birdclef-2026/outputs/v123-rankcal-singlepass-tsubasa-v1/submission.csv`
- Mechanism: rank-calibrate Tsubasa SED sidecar onto the clean Perch surrogate scale, apply a 10-class rank-margin gate, then run one EcoProto/rank-launch final pass.

## Evidence

- Run-mode: `COMPLETE`.
- Runtime before saved output: about `474.4s`.
- Schema: `120 x 235`, sample column order matched, all finite, no duplicate row IDs.
- Proxy: `macro=0.97921107`, `micro=0.91480745`, `top5=0.52054795`.
- Gate cells: `572 / 28080`.
- Correlation vs v110: Pearson `0.999952`, MAD `0.000203`.
- Correlation vs v114: Pearson `0.999546`, MAD `0.001488`.

## Decision

`HOLD - do not submit`

v123 is a technically successful memory-safe refinement: it fixes v122's scale-mismatch gate and keeps one final-layer pass. But the proxy gain over v114 is only about `+0.000010` macro and the output is nearly identical to clean anchors. That is too weak to justify a real Kaggle slot.

## Next Direction

Stop tuning the Tsubasa sidecar at this scale unless a new train-window rationale appears. The useful reusable lesson is that any future sidecar should be single-pass and rank-calibrated, but the current 10-class Tsubasa lane does not provide enough incremental quality.
