# v122 Run-Mode Status

Updated: 2026-05-19 09:04 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v122-singlepass-class-selective-tsubasa/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v122-singlepass-cls-tsubasa`
- Output directory: `birdclef-2026/outputs/v122-singlepass-class-selective-tsubasa-v1`
- Generator: `birdclef-2026/scripts/birdclef_prepare_v122_singlepass_class_selective_tsubasa.py`

## Status

Kaggle Run-mode status: `COMPLETE`.

Downloaded artifacts:

- `submission.csv`
- `v122_singlepass_tsubasa_summary.csv`
- `v122_singlepass_tsubasa_remap_diagnostics.csv`
- `bc26-v122-singlepass-cls-tsubasa.log`

## Runtime Evidence

- Output saved at about `471.2s`.
- nbconvert completed at about `484.3s`.
- Runtime is below the 90-minute CPU inference cap.
- CPU-only ONNX Runtime execution succeeded.
- Internet disabled in kernel metadata.
- The final layer ran once after SED-level hybridization.

## Quality Evidence

- Proxy: macro `0.97709863`, micro `0.92241158`, top1 `0.26027397`, top5 `0.58904110`.
- Schema: `120 x 235`, finite values, no duplicate row IDs, score range `[0.011144, 0.999812]`.
- Columns match `sample_submission.csv`; dry-run row IDs come from train soundscapes, so row-order match to hidden-test sample is not applicable in this local proxy output.
- Correlation vs v110: Pearson `0.999107`, MAD `0.001008`.
- Correlation vs v114: Pearson `0.998738`, MAD `0.002165`.
- Correlation vs v121: Pearson `0.998531`, MAD `0.001797`.

## Decision

`REJECT-quality`

v122 successfully repaired the v120/v121 double-final-layer memory pattern, but its probability-scale pre-final gate was too sparse: only `114 / 28080` cells were gated. Macro proxy fell below the clean v110/v114 baselines, so v122 is not submit-eligible. Preserve it as a memory-fix proof and continue with rank-calibrated gating.
