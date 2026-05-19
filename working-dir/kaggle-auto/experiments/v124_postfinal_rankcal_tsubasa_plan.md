# v124 Post-Final Rank-Calibrated Tsubasa Plan

Created: 2026-05-19 09:34 UTC

## Trigger

v121 showed a strong sparse Tsubasa sidecar proxy but inherited v120's hidden RAM risk because it recomputed the final decision layer twice. v122 and v123 proved that single-pass sidecar injection can run under Run-mode, but pre-final injection was either too sparse or too muted. v124 keeps a single clean final pass and applies a lightweight post-final sidecar correction.

## Candidate

- Notebook: `birdclef-2026/notebooks/v124-postfinal-rankcal-tsubasa/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v124-postfinal-rankcal`
- Generator: `birdclef-2026/scripts/birdclef_prepare_v124_postfinal_rankcal_tsubasa.py`

## Original Mechanism

v124 starts from the license-clean v116 Tsubasa branch but changes the final use of SED evidence:

- compute Tsubasa remapped SED probabilities once;
- rank-calibrate Tsubasa sidecar onto the clean Perch surrogate probability scale;
- feed the clean Perch surrogate into the existing EcoProto/rank-launch final layer;
- run the expensive final layer exactly once;
- after the clean final output exists, apply a lightweight post-final sidecar blend on selected classes only when Tsubasa rank is ahead of clean final rank by `0.02`;
- use sidecar mix `0.30` on gated cells.

Selected classes:

`47158son13`, `47158son15`, `47158son16`, `47158son21`, `47158son22`, `47158son23`, `516975`, `chacha1`, `grekis`, `plcjay1`.

## Gate

Run Kaggle Run-mode only. Do not real-submit v124 unless runtime, schema, proxy, correlation, memory-risk, and candidate-specific compliance evidence pass.
