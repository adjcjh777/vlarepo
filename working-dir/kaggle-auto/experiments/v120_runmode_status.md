# v120 Run-Mode Status

Updated: 2026-05-19 07:47 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v120-clean-tsubasa-sidecar/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v120-clean-tsubasa-sidecar`
- Output directory: `birdclef-2026/outputs/v120-clean-tsubasa-sidecar-v1`

## Status

Kaggle Run-mode status: `COMPLETE`.

Downloaded artifacts:

- `submission.csv`
- `v120_clean_tsubasa_branch_summary.csv`
- `v120_tsubasa_sidecar_remap_diagnostics.csv`
- `bc26-v120-clean-tsubasa-sidecar.log`

## Runtime Evidence

- Output saved at about `683.4s`.
- nbconvert completed at about `696.8s`.
- Runtime is below the 90-minute CPU inference cap with a large safety margin.
- CPU-only ONNX Runtime execution succeeded.
- Internet disabled in kernel metadata.

## Branch Evidence

- Tsubasa sidecar range/mean/std: `[0.012571, 0.999812] / 0.520771 / 0.251924`.
- Clean anchor range/mean/std: `[0.011144, 0.999470] / 0.521132 / 0.242345`.
- Final blend range/mean/std: `[0.013462, 0.999145] / 0.521078 / 0.236149`.
- Final weights: `clean_anchor=0.85`, `tsubasa_sidecar=0.15`.

## Decision

Run-mode passed and the candidate proceeded to guarded real submission.

Post-submission update at `2026-05-19 08:06 UTC`: Kaggle ref `52802748` completed with no public score and error `Your notebook requested more memory (RAM) than is available.` Retire v120 as a final/next-submit candidate; future sidecar candidates must avoid the double-final-layer memory pattern.
