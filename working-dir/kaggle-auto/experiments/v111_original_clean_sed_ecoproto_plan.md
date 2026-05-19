# v111 Original Clean SED EcoProto Plan

Updated: 2026-05-19 05:03 UTC

## Motivation

v104-v110 showed that Perch-only clean branches are compliant but missing a strong SED-like ranking signal. Kaggle metadata audit found `backtracking/birdclef2026-clean-sed-b0` with `CC0-1.0` license and a raw-audio ONNX interface that fits the existing CPU 5-second-window pipeline.

## Mechanism

`v111-clean-sed-ecoproto-blend` adds one new clean input to the v110 branch:

- attach `backtracking/birdclef2026-clean-sed-b0` as a dataset source;
- load `fold0_best_overall.onnx` with ONNX Runtime CPU;
- run the clean SED model over train and test 5-second windows;
- use clean SED train logits to compute a class AUC reference;
- replace the Perch-only SED surrogate with clean SED probabilities;
- keep the v110 EcoProto clean-blend structure.

## Compliance

- CPU-only.
- Internet disabled.
- No unknown-license runtime dependency.
- Runtime metadata uses competition data, Perch ONNX (`CC0-1.0`), clean SED B0 (`CC0-1.0`), and Google Perch (`Apache 2.0`).

## Decision Rule

Do not real-submit unless v111 materially improves the clean-branch proxy and plausibly challenges the current `0.949` anchor.

