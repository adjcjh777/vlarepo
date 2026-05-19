# v134 Static Audit

Updated: 2026-05-19 11:52 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v134-stable3-guarded-rescue/submission.ipynb`
- Metadata: `birdclef-2026/notebooks/v134-stable3-guarded-rescue/kernel-metadata.json`
- Generator: `birdclef-2026/scripts/birdclef_prepare_v134_stable3_guarded_rescue.py`
- Kernel: `junhaochengadjcjh7u7/bc26-v134-stable3-guarded-rescue`

## Static Checks

- JSON parse: pass, `20` notebook cells.
- Private kernel: pass, `is_private=true`.
- CPU-only: pass, `enable_gpu=false`, `enable_tpu=false`.
- Internet disabled: pass, `enable_internet=false`.
- Competition source: pass, `birdclef-2026`.
- Runtime datasets:
  - `rishikeshjani/perch-onnx-for-birdclef-2026`
  - `backtracking/birdclef2026-clean-sed-b0`
- Model source:
  - `google/bird-vocalization-classifier/TensorFlow2/perch_v2_cpu/1`
- Kernel sources: pass, empty.
- Prior output CSV mounts: pass by static search; no prior `outputs/` mount.
- Runtime dependency reduction: pass; `roniheka` dataset removed relative to v127.

## Originality and Scope

v134 is the guarded stable3 continuation after the v127 public-score collapse:

- starts from the single-final-layer v110 clean EcoProto anchor;
- narrows the route to `47158son13`, `47158son22`, `47158son23`;
- uses only the clean `v112`/Backtracking side signal;
- keeps positive-only rescue;
- adds a row-level top-hit preservation guard inspired by v103;
- avoids broad same-family expansion.

## Decision

`PUSH-RUNMODE-ONLY`

Run-mode is justified because the candidate is materially narrower and cleaner than v127, and it does not consume a real submission slot.

