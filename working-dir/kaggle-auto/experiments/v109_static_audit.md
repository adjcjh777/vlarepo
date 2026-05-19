# v109 Static Audit

Updated: 2026-05-19 04:34 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v109-ecoproto-ranklaunch-perch/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v109-ecoproto-ranklaunch`
- Mechanism: original EcoProto prototype signal used inside guarded rank launch.

## Metadata

- `enable_gpu`: `false`
- `enable_tpu`: `false`
- `enable_internet`: `false`
- `competition_sources`: `birdclef-2026`
- `dataset_sources`: `rishikeshjani/perch-onnx-for-birdclef-2026`
- `model_sources`: `google/bird-vocalization-classifier/TensorFlow2/perch_v2_cpu/1`
- `kernel_sources`: empty

## Dependency Check

Runtime metadata does not include:

- `jaejohn/perch-meta`
- `tuckerarrants/bc2026-distilled-sed-public`

Those names appear only in provenance text documenting removed dependencies. They are not mounted as runtime inputs.

## Decision

`PASS static audit`

Proceed with Kaggle Run-mode execution and local schema/proxy checks after output is available.

