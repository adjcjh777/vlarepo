# v124 Run-Mode Status

Updated: 2026-05-19 09:45 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v124-postfinal-rankcal-tsubasa/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v124-postfinal-rankcal`
- Output directory: `birdclef-2026/outputs/v124-postfinal-rankcal-tsubasa-v1`
- Generator: `birdclef-2026/scripts/birdclef_prepare_v124_postfinal_rankcal_tsubasa.py`

## Status

Kaggle Run-mode status: `COMPLETE`.

Downloaded artifacts:

- `submission.csv`
- `v124_postfinal_tsubasa_summary.csv`
- `v124_postfinal_tsubasa_remap_diagnostics.csv`
- `bc26-v124-postfinal-rankcal.log`

## Runtime Evidence

- Output saved at about `462.5s`.
- nbconvert completed at about `474.0s`.
- Runtime is below the 90-minute CPU inference cap.
- CPU-only ONNX Runtime execution succeeded.
- Internet disabled in kernel metadata.
- Clean final layer ran once; Tsubasa was used only as a lightweight post-final rank-calibrated sidecar.

## Quality Evidence

- Proxy: macro `0.97115717`, micro `0.90281675`, top1 `0.24657534`, top5 `0.52054795`.
- Schema: `120 x 235`, finite values, no duplicate row IDs, score range `[0.011144, 0.999470]`.
- Columns match `sample_submission.csv`; dry-run row IDs come from train soundscapes, so row-order match to hidden-test sample is not applicable in this local proxy output.
- Gate cells: `555 / 28080`.
- Correlation vs v110: Pearson `0.998549`, MAD `0.001412`.
- Correlation vs v114: Pearson `0.998147`, MAD `0.002647`.
- Correlation vs v121: Pearson `0.998167`, MAD `0.001843`.

## Decision

`REJECT-quality`

v124 proves the post-final lightweight sidecar can run with the single-final-layer memory profile, but it hurts macro badly. Stop this direct Tsubasa post-final sidecar lane.
