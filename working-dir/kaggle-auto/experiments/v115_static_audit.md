# v115 Static Audit

Updated: 2026-05-19 06:24 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v115-tsubasa-snowflake-sed/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v115-tsubasa-snowflake-sed`
- Generator: `birdclef-2026/scripts/birdclef_prepare_v115_tsubasa_snowflake_sed.py`

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

## Source Audit

- `tsubasatech/birdclef-2026-snowflake-sed` Kaggle metadata license:
  `CC0-1.0`
- ONNX files:
  - `sed_convnext-tiny_fold0.onnx`, input `audio ['B', 160000]`, output
    `logits ['B', 234]`
  - `sed_tf-efficientnetv2-m_fold0.onnx`, input `audio ['B', 160000]`, output
    `logits ['B', 234]`

## Code Check

- Code cells compile locally, excluding the Kaggle notebook magic install cell.
- Runtime code includes:
  - `clean_sed_sessions`
  - `sed_convnext-tiny_fold0.onnx`
  - `sed_tf-efficientnetv2-m_fold0.onnx`
  - `v115_snowflake_sed_remap_diagnostics.csv`
- Runtime code does not include:
  - `jaejohn/perch-meta`
  - `tuckerarrants/bc2026-distilled-sed-public`
  - `backtracking/birdclef2026-clean-sed-b0`
  - prior local output paths from v110/v113/v114

## Decision

`PASS static audit`

Proceed to Kaggle Run-mode only. Do not make a real competition submission
until v115 output is pulled and checked with schema, proxy, correlation, runtime,
and compliance reports.
