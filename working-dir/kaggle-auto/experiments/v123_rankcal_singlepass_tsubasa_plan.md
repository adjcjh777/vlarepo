# v123 Rank-Calibrated Single-Pass Tsubasa Plan

Created: 2026-05-19 09:07 UTC

## Trigger

v122 completed Run-mode and proved that single-pass sidecar injection can avoid the v120/v121 double-final-layer pattern, but its raw-probability gate was too sparse and macro proxy dropped. v123 keeps the single-pass structure and fixes the gate scale mismatch.

## Candidate

- Notebook: `birdclef-2026/notebooks/v123-rankcal-singlepass-tsubasa/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v123-rankcal-singlepass`
- Generator: `birdclef-2026/scripts/birdclef_prepare_v123_rankcal_singlepass_tsubasa.py`

## Original Mechanism

v123 compares clean and Tsubasa sidecar evidence by column-wise ranks rather than raw probabilities:

- compute Tsubasa remapped SED probabilities once;
- compute clean Perch surrogate SED probabilities once;
- rank both views per class over the current rows;
- map Tsubasa rank order onto the clean probability distribution per class;
- apply the same 10-class sidecar list with rank margin `0.02`;
- mix `0.40` rank-calibrated sidecar only on gated cells;
- run the final EcoProto/rank-launch layer once.

Selected classes:

`47158son13`, `47158son15`, `47158son16`, `47158son21`, `47158son22`, `47158son23`, `516975`, `chacha1`, `grekis`, `plcjay1`.

## Gate

Run Kaggle Run-mode only. Do not real-submit v123 unless runtime, schema, proxy, correlation, memory-risk, and candidate-specific compliance evidence pass.
