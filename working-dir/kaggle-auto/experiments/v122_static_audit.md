# v122 Static Audit

Updated: 2026-05-19 08:55 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v122-singlepass-class-selective-tsubasa/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v122-singlepass-cls-tsubasa`
- Generator: `birdclef-2026/scripts/birdclef_prepare_v122_singlepass_class_selective_tsubasa.py`

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
- Runtime code does not include `jaejohn/perch-meta`, `tuckerarrants/bc2026-distilled-sed-public`, `tuckerarrants/perch-v2-no-dft-onnx`, or `tuckerarrants/birdclef-2026-waveform-cache`.
- Notebook writes `submission.csv`.
- Notebook writes single-pass diagnostic `v122_singlepass_tsubasa_summary.csv`.

## Decision

Static gate passed. Push Kaggle Run-mode only. v122 is not eligible for real submission until runtime/schema/proxy/correlation/compliance evidence is complete and the v120 memory failure risk is addressed by the single-pass run evidence.
