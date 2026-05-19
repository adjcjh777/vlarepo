# v120 Static Audit

Updated: 2026-05-19 07:35 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v120-clean-tsubasa-sidecar/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v120-clean-tsubasa-sidecar`
- Generator: `birdclef-2026/scripts/birdclef_prepare_v120_clean_tsubasa_sidecar.py`

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
- Notebook writes branch summary diagnostic `v120_clean_tsubasa_branch_summary.csv`.

## Originality Boundary

v120 is a clean, self-contained sidecar experiment. The public CC0 Tsubasa model is treated as a small diversity signal, not as a copied solution. The workspace-owned contribution is the two-view execution and constrained blend decision layer: recompute a Perch-only clean anchor, compute the Tsubasa sidecar, and apply a pre-declared `0.85/0.15` probability blend selected from local proxy evidence.

## Decision

Static gate passed. Push Kaggle Run-mode only; no real submission before runtime/schema/proxy/correlation/compliance evidence.
