# v112 Static Audit

Updated: 2026-05-19 05:20 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v112-clean-sed-remap-ecoproto/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v112-clean-sed-remap`
- Mechanism: CC0 clean SED train-window column remap plus EcoProto clean blend.

## Metadata

- `enable_gpu`: `false`
- `enable_tpu`: `false`
- `enable_internet`: `false`
- `competition_sources`: `birdclef-2026`
- `dataset_sources`:
  - `rishikeshjani/perch-onnx-for-birdclef-2026`
  - `backtracking/birdclef2026-clean-sed-b0`
- `model_sources`: `google/bird-vocalization-classifier/TensorFlow2/perch_v2_cpu/1`
- `kernel_sources`: empty

## Dependency Check

Runtime metadata does not include:

- `jaejohn/perch-meta`
- `tuckerarrants/bc2026-distilled-sed-public`

Those names appear only in provenance text documenting removed dependencies. They are not mounted as runtime inputs.

## Innovation Check

`PASS`: v112 includes a new class-output remap and trust-strength layer learned from train soundscape windows. This is an original diagnostic/control mechanism, not a direct public-notebook replication.

## Decision

`PASS static audit`

Proceed with Kaggle Run-mode execution and local schema/proxy checks after output is available.
