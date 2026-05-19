# v111 Static Audit

Updated: 2026-05-19 05:03 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v111-clean-sed-ecoproto-blend/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v111-clean-sed-ecoproto`
- Mechanism: clean SED B0 plus EcoProto clean blend.

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

## Decision

`PASS static audit`

Proceed with Kaggle Run-mode execution and local schema/proxy checks after output is available.

