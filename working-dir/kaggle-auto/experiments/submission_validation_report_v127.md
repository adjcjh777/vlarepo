# Submission Validation Report: v127

Updated: 2026-05-19 10:24 UTC

## Artifact

`birdclef-2026/outputs/v127-memorysafe-nontsubasa-router-v1/submission.csv`

## Validation

- Kaggle Run-mode status: `COMPLETE`.
- Runtime: output saved at about `378.4s`; nbconvert finished at about `390.8s`, below the 90-minute cap.
- Columns match `sample_submission.csv`: pass.
- Row IDs: dry-run train-like rows, no duplicates.
- Rows/columns: `120 x 235`.
- Numeric values finite: pass.
- Prediction range: `[0.01114442, 0.99946990]`.
- Prediction mean/std: `0.52113223 / 0.24167349`.
- Local dry-run proxy: macro `0.98008089`, micro `0.91595668`, top5 `0.52054795`.
- Correlation:
  - vs v110: Pearson `0.996646`, MAD `0.002296`.
  - vs v114: Pearson `0.996229`, MAD `0.003581`.
  - vs v112: Pearson `0.783987`, MAD `0.123417`.
  - vs v119: Pearson `0.722441`, MAD `0.147190`.

## Submission Gate

Pass for guarded code submission through Kaggle kernel `junhaochengadjcjh7u7/bc26-v127-nontsubasa-router` version `1`.

Use only a guarded slot; do not mark as final before public/private evidence exists.
