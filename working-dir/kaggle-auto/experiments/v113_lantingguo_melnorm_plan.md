# v113 LantingGuo MelNormProbe Plan

Updated: 2026-05-19 05:38 UTC

## Motivation

`backtracking/birdclef2026-clean-sed-b0` failed as both direct clean SED (`v111`) and train-window remap (`v112`). The next clean SED candidate is `lantingguo/birdclef2026-own-sed-b0-v5-onnx`, which has Kaggle metadata license `CC0-1.0` and a compact 128-mel ONNX interface.

## Original Mechanism

`v113-lantingguo-melnorm-ecoproto` adds a new MelNormProbe sidecar:

- load `sed_b0.onnx` from the CC0 LantingGuo dataset;
- convert each 5-second window into 128-bin mel input;
- run two deterministic mel normalization views, `zscore` and `minmax`;
- estimate per-class AUC on train soundscape windows for both views;
- choose the better view per class, then shrink its influence by train-window quality and view margin;
- fall weak classes back toward the Perch-only surrogate instead of allowing a strong clean-SED branch;
- emit `v113_lantingguo_melnorm_diagnostics.csv`.

This is an original diagnostic/control mechanism rather than direct replication of a public preprocessing recipe.

## Compliance

- CPU-only.
- Internet disabled.
- No unknown-license runtime dependency.
- Runtime metadata uses competition data, Perch ONNX, Google Perch, and `lantingguo/birdclef2026-own-sed-b0-v5-onnx` (`CC0-1.0`).
- No real Kaggle submission unless Run-mode proxy and diagnostics justify spending a daily slot.

## Decision Rule

Promote only if v113 materially beats the current best clean fallback v110 and diagnostics do not show a train-window-only artifact. Otherwise reject or hold as a diagnostic artifact.
