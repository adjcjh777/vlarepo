# v112 Original Clean SED Remap EcoProto Plan

Updated: 2026-05-19 05:20 UTC

## Motivation

v111 proved that `backtracking/birdclef2026-clean-sed-b0` can run in the CPU/no-internet Kaggle path, but direct same-index use of its 234 outputs broke the proxy. The likely failure mode is not runtime; it is class-order, calibration, or training-target mismatch.

## Original Mechanism

`v112-clean-sed-remap-ecoproto` keeps the v110/v111 EcoProto clean branch, but adds an original train-window self-calibration layer:

- run the audited CC0 clean SED model on train and test soundscape windows;
- compute a 234-by-234 train-window output-to-target correlation matrix;
- for each competition class, compare the same-index SED column with the strongest candidate output column;
- accept a remap only when the candidate beats same-index AUC and correlation by conservative margins;
- blend same-index and remapped SED views by a per-class trust strength;
- inject row-rank information only in proportion to that trust strength;
- emit `v112_clean_sed_remap_diagnostics.csv` for class-level audit.

This is deliberately an alignment diagnosis and controlled original sidecar, not another copied public blend.

## Compliance

- CPU-only.
- Internet disabled.
- No unknown-license runtime dependency.
- Runtime metadata uses competition data, Perch ONNX, Google Perch, and `backtracking/birdclef2026-clean-sed-b0` with Kaggle metadata `CC0-1.0`.
- No real Kaggle submission unless Run-mode proxy and diagnostics justify spending a daily slot.

## Decision Rule

Promote only if v112 materially improves over v110 clean fallback and does not show obvious train-window remap overfit. Otherwise reject or hold as a diagnostic artifact.
