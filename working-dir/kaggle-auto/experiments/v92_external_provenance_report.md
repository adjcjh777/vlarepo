# v92 External Provenance Report

Updated: 2026-05-19 01:03 UTC

## Source
- Public Kaggle notebook reference: `beicicc/bc26-mtoshi-vis-may18`
- Local derivative: `birdclef-2026/notebooks/v92-attributed-mtoshi-vis-nobirdnet`
- Source metadata snapshot: `experiments/provenance/v92/source_kernel_metadata.json`

## Local Changes
- Removed the non-inference `mtoshidesu/birdclef-flow-diagram` dataset dependency and display cell.
- Explicitly disabled BirdNET and removed any BirdNET model source.
- Kept CPU-only and no-internet metadata.
- Added hard final row-order, column-order, finite, duplicate-row, and range checks.

## Dependencies
- `tuckerarrants/bc2026-distilled-sed-public`: public Kaggle dataset, license not confirmed locally.
- `jaejohn/perch-meta`: public Kaggle dataset, license not confirmed locally.
- `tuckerarrants/perch-v2-no-dft-onnx`: public Kaggle dataset, license not confirmed locally.
- `rishikeshjani/perch-onnx-for-birdclef-2026`: public Kaggle dataset, previously recorded as `CC0-1.0`.
- `ashok205/tf-wheels`: Kaggle kernel source, license not confirmed locally.
- `google/bird-vocalization-classifier/TensorFlow2/perch_v2_cpu/1`: public Kaggle model, previously recorded as Apache 2.0.

## Compliance Status
Status: `PASS-for-local-runmode`, `HOLD-for-real-submit`.

Reason: v92 is reproducible as CPU/no-internet Run-mode evidence, but several public Kaggle dataset/kernel-source licenses remain locally unknown, and the final dry-run output is a near-duplicate of the already submitted v87 anchor. It should not consume slot two without a fresh score-driven decision.

