# v123 Run-Mode Status

Updated: 2026-05-19 09:21 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v123-rankcal-singlepass-tsubasa/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v123-rankcal-singlepass`
- Output directory: `birdclef-2026/outputs/v123-rankcal-singlepass-tsubasa-v1`
- Generator: `birdclef-2026/scripts/birdclef_prepare_v123_rankcal_singlepass_tsubasa.py`

## Status

Kaggle Run-mode status: `COMPLETE`.

Downloaded artifacts:

- `submission.csv`
- `v123_rankcal_tsubasa_summary.csv`
- `v123_rankcal_tsubasa_remap_diagnostics.csv`
- `bc26-v123-rankcal-singlepass.log`

## Runtime Evidence

- Output saved at about `474.4s`.
- nbconvert completed at about `486.8s`.
- Runtime is below the 90-minute CPU inference cap.
- CPU-only ONNX Runtime execution succeeded.
- Internet disabled in kernel metadata.
- The final layer ran once after rank-calibrated SED hybridization.

## Quality Evidence

- Proxy: macro `0.97921107`, micro `0.91480745`, top1 `0.23287671`, top5 `0.52054795`.
- Schema: `120 x 235`, finite values, no duplicate row IDs, score range `[0.011144, 0.999470]`.
- Columns match `sample_submission.csv`; dry-run row IDs come from train soundscapes, so row-order match to hidden-test sample is not applicable in this local proxy output.
- Gate cells: `572 / 28080`, compared with v122's `114 / 28080`.
- Correlation vs v110: Pearson `0.999952`, MAD `0.000203`.
- Correlation vs v114: Pearson `0.999546`, MAD `0.001488`.
- Correlation vs v121: Pearson `0.998925`, MAD `0.001256`.

## Decision

`HOLD-too-small-gain`

v123 successfully fixes v122's under-active gate while preserving the single-pass memory profile, but its macro proxy gain over v114 is only about `+0.000010` and its output is nearly identical to v110/v114. Do not spend a real submission slot on this candidate.
