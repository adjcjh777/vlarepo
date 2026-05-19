# v121 Static Audit

Updated: 2026-05-19 08:29 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v121-class-selective-tsubasa/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v121-class-selective-tsubasa`
- Generator: `birdclef-2026/scripts/birdclef_prepare_v121_class_selective_tsubasa.py`

## Static Checks

- Metadata private: pass.
- `enable_gpu=false`, `enable_tpu=false`, `enable_internet=false`: pass.
- `competition_sources=[birdclef-2026]`: pass.
- Runtime datasets:
  - `rishikeshjani/perch-onnx-for-birdclef-2026`: CC0-1.0.
  - `tsubasatech/birdclef-2026-snowflake-sed`: CC0-1.0.
- Model source: `google/bird-vocalization-classifier/TensorFlow2/perch_v2_cpu/1`: previously audited Apache 2.0.
- Kernel sources: empty.
- Code syntax: pass via local notebook AST parse excluding Kaggle magic cell.
- Runtime code does not mount prior local output CSVs.
- Runtime code does not include `jaejohn/perch-meta` or `tuckerarrants/bc2026-distilled-sed-public`.
- Notebook writes `submission.csv`.
- Notebook writes branch summary diagnostic `v121_class_selective_tsubasa_summary.csv`.

## Decision

Static gate passed, and Kaggle Run-mode later completed. v121 is not eligible for real submission as-is because v120 ref `52802748` completed with hidden-test RAM exceeded, and v121 still uses the same double-final-layer structure.
