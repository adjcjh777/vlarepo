# v120 Clean Tsubasa Sidecar Plan

Created: 2026-05-19 07:35 UTC

## Trigger

v116 was rejected as a standalone candidate because its local dry-run proxy collapsed, but it remained compliance-clean and materially different from the clean branch. A controlled local blend probe found that a small Tsubasa probability sidecar can improve macro proxy over the v110/v114 clean anchor family.

## Candidate

- Notebook: `birdclef-2026/notebooks/v120-clean-tsubasa-sidecar/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v120-clean-tsubasa-sidecar`
- Generator: `birdclef-2026/scripts/birdclef_prepare_v120_clean_tsubasa_sidecar.py`

## Original Mechanism

v120 is not a public notebook fork and does not mount previous output CSVs. It executes two internal views inside one CPU/no-internet notebook:

- `clean_anchor`: a v110-like Perch-only clean surrogate with EcoProto/rank-launch.
- `tsubasa_sidecar`: the CC0 Tsubasa ConvNeXt SED branch from v116.

The final score is a constrained probability blend:

`0.85 * clean_anchor + 0.15 * tsubasa_sidecar`

## Local Probe Evidence

The lightweight local blend probe wrote `experiments/v120_clean_diversity_blend_probe.csv`.

Best relevant rows:

- `v110_prob_v116_0.15`: macro `0.981399`, top5 `0.479452`.
- `v114_prob_v116_0.15`: macro `0.981513`, top5 `0.479452`.
- Baseline `v114`: macro `0.979201`, top5 `0.520548`.

Interpretation: v120 trades some top5 proxy for a higher macro-AUC proxy and lower-correlation clean sidecar. This is a bold clean candidate, not a conservative fallback.

## Gate

Run Kaggle Run-mode only first. Do not real-submit unless v120 completes, output schema/range pass, proxy/correlation remain favorable, and candidate-specific compliance remains clean.
