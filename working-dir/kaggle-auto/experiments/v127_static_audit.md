# v127 Static Audit

Updated: 2026-05-19 10:10 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v127-memorysafe-nontsubasa-router/submission.ipynb`
- Metadata: `birdclef-2026/notebooks/v127-memorysafe-nontsubasa-router/kernel-metadata.json`
- Generator: `birdclef-2026/scripts/birdclef_prepare_v127_memorysafe_nontsubasa_router.py`
- Kernel: `junhaochengadjcjh7u7/bc26-v127-nontsubasa-router`

## Static Checks

- JSON parse: pass, `20` notebook cells.
- Private kernel: pass, `is_private=true`.
- CPU-only: pass, `enable_gpu=false`, `enable_tpu=false`.
- Internet disabled: pass, `enable_internet=false`.
- Competition source: pass, `birdclef-2026`.
- Runtime datasets:
  - `rishikeshjani/perch-onnx-for-birdclef-2026`
  - `backtracking/birdclef2026-clean-sed-b0`
  - `roniheka/birdclef-2026-a90v2-distilled-hgnet-onnx`
- Model source:
  - `google/bird-vocalization-classifier/TensorFlow2/perch_v2_cpu/1`
- Kernel sources: pass, empty.
- Prior output CSV mounts: pass by static search; no local `outputs/` path or prior submission output source.
- Tsubasa branch usage: pass by metadata and code intent; no Tsubasa dataset source.

## Originality and Scope

v127 is the memory-safe materialization path for the v125-v126 non-Tsubasa router lane:

- starts from the single-final-layer v110 clean EcoProto anchor;
- computes raw Backtracking and Roniheka side evidence inside the notebook;
- rank-calibrates only five support>=10 selected classes;
- avoids recomputing v112/v119 side final layers to reduce hidden RAM risk;
- does not use prior output CSVs.

## Decision

`PUSH-RUNMODE-ONLY`

Do not real-submit v127 until Run-mode completion, output schema, local proxy, correlation, and compliance evidence are recorded.
