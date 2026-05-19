# v102 Run-Mode Status

Updated: 2026-05-19 03:00 UTC

## Candidate

- Local path: `birdclef-2026/notebooks/v102-original-macro-risk-rescue`
- Kaggle kernel: `junhaochengadjcjh7u7/bc26-v102-original-macro-risk-rescue`
- Version: `1`
- Source line: private original `v86-original-midsupport-proberescue`

## Original Change

v102 replaces v86's broad mid-support probe rescue with a class-wise macro-risk rescue policy.

The policy uses:

- local OOF risk (`perch_auc_cal_ref`);
- train support counts;
- taxonomy bucket (`Amphibia` / `Insecta` texture taxa);
- SED-vs-Perch disagreement (`sed_auc_ref - perch_auc_cal_ref`);
- high-AUC anchor protection and rare-class floor guards.

This is a workspace-original meta-layer, not a public notebook copy.

## Current Status

- Kaggle Run-mode version 1: `RUNNING` at first check.
- Real competition submission: not submitted.
- Reason for no real submission: v101 ref `52795021` is still `PENDING`, and v102 lacks Run-mode evidence.

## Next Gate

When Run-mode completes, pull outputs and logs, then check:

- CPU-only/no-internet status;
- runtime under 90 minutes;
- `submission.csv` shape and row/class order;
- NaN/inf/range;
- v102 log count line `V102 original macro-risk rescue counts`;
- correlation versus v86/v87/v91 outputs if output is score-shaped.
