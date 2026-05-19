# v124 Static Audit

Updated: 2026-05-19 09:34 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v124-postfinal-rankcal-tsubasa/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v124-postfinal-rankcal`
- Generator: `birdclef-2026/scripts/birdclef_prepare_v124_postfinal_rankcal_tsubasa.py`

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
- Notebook writes post-final diagnostic `v124_postfinal_tsubasa_summary.csv`.
- Notebook contains markers for a clean final layer run once and a lightweight post-final rank-calibrated sidecar.

## Decision

Static gate passed. Push Kaggle Run-mode only. v124 is not eligible for real submission until runtime/schema/proxy/correlation/compliance evidence is complete.
