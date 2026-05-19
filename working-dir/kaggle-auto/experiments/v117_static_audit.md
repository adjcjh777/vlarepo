# v117 Static Audit

Updated: 2026-05-19 06:49 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v117-tsubasa-convnext-noremap/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v117-tsubasa-convnext-noremap`
- Generator: `birdclef-2026/scripts/birdclef_prepare_v117_tsubasa_convnext_noremap.py`

## Metadata

- `enable_gpu`: `false`
- `enable_tpu`: `false`
- `enable_internet`: `false`
- `competition_sources`: `birdclef-2026`
- `dataset_sources`:
  - `rishikeshjani/perch-onnx-for-birdclef-2026`
  - `tsubasatech/birdclef-2026-snowflake-sed`
- `model_sources`: `google/bird-vocalization-classifier/TensorFlow2/perch_v2_cpu/1`
- `kernel_sources`: empty

## Code Check

- Code cells compile locally, excluding the Kaggle notebook magic install cell.
- Runtime code includes `sed_convnext-tiny_fold0.onnx`.
- Runtime code excludes `sed_tf-efficientnetv2-m_fold0.onnx`.
- Runtime code explicitly contains `remap_strength[:] = 0.0`.
- Runtime code excludes:
  - `jaejohn/perch-meta`
  - `tuckerarrants/bc2026-distilled-sed-public`
  - `backtracking/birdclef2026-clean-sed-b0`

## Decision

`PASS static audit`

Proceed to Kaggle Run-mode only. Do not real-submit until output evidence exists.
