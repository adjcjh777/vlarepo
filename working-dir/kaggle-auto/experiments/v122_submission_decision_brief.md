# v122 Submission Decision Brief

Updated: 2026-05-19 09:04 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v122-singlepass-class-selective-tsubasa/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v122-singlepass-cls-tsubasa`
- Output: `birdclef-2026/outputs/v122-singlepass-class-selective-tsubasa-v1/submission.csv`
- Mechanism: v121's 10-class Tsubasa sidecar gate moved before the final layer, then one EcoProto/rank-launch final pass.

## Evidence

- Run-mode: `COMPLETE`.
- Runtime before saved output: about `471.2s`.
- Schema: `120 x 235`, sample column order matched, all finite, no duplicate row IDs.
- Proxy: `macro=0.97709863`, `micro=0.92241158`, `top5=0.58904110`.
- Gate cells: `114 / 28080`.

## Decision

`REJECT - do not submit`

v122 fixes the memory structure but loses macro quality. The likely cause is scale mismatch: Tsubasa SED probabilities are much lower than the clean Perch surrogate, so probability-margin gating activates too few cells before the final layer. The next candidate should keep the single-pass structure but compare rank-calibrated sidecar evidence instead of raw probability scale.
