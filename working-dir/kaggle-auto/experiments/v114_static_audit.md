# v114 Static Audit

Updated: 2026-05-19 05:56 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v114-v110-v113-selfblend/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v114-clean-selfblend`
- Mechanism: self-contained `0.85*v110_like + 0.15*v113_like` clean blend.

## Metadata

- `enable_gpu`: `false`
- `enable_tpu`: `false`
- `enable_internet`: `false`
- `competition_sources`: `birdclef-2026`
- `dataset_sources`:
  - `rishikeshjani/perch-onnx-for-birdclef-2026`
  - `lantingguo/birdclef2026-own-sed-b0-v5-onnx`
- `model_sources`: `google/bird-vocalization-classifier/TensorFlow2/perch_v2_cpu/1`
- `kernel_sources`: empty

## Dependency Check

Runtime metadata and notebook code do not include:

- `jaejohn/perch-meta`
- `tuckerarrants/bc2026-distilled-sed-public`
- `backtracking/birdclef2026-clean-sed-b0`
- prior local output paths such as `outputs/v110` or `outputs/v113`

## Code Check

- Notebook code cells compile locally.
- Final layer is wrapped and executed twice inside the notebook:
  - `final_probs_v110_like = _compute_v114_branch(...)`
  - `final_probs_v113_like = _compute_v114_branch(...)`
- Final blend is computed as `0.85 * final_probs_v110_like + 0.15 * final_probs_v113_like`.
- Originality check: v114 recomputes both branch views from mounted models/data
  inside the notebook, including the v113 MelNormProbe sidecar diagnostics, and
  does not use stored predictions from earlier notebooks as a runtime input.

## Decision

`PASS static audit`

Kaggle Run-mode later completed successfully. Local checks were recorded in:

- `experiments/v114_schema_report.csv`
- `experiments/v114_proxy_scores.csv`
- `experiments/v114_correlation_vs_branch.csv`
- `experiments/v114_submission_decision_brief.md`

Final promotion decision: `HOLD - do not submit`.
