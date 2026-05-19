# v102 Run-Mode Status

Updated: 2026-05-19 03:04 UTC

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

- Kaggle Run-mode version 1: `COMPLETE`.
- Output archive: `birdclef-2026/outputs/v102-original-macro-risk-rescue-v1`.
- Real competition submission: not submitted.
- Reason for no real submission: v101 ref `52795021` is still `PENDING`; v102 is valid but has mixed proxy evidence.

## Next Gate

Completed checks:

- CPU-only/no-internet status;
- runtime under 90 minutes;
- `submission.csv` shape and row/class order;
- NaN/inf/range;
- v102 log count line `V102 original macro-risk rescue counts`;
- proxy score and side-output correlation.

Key results:

- Runtime: about `249.49s`.
- Output: `(120,235)`, finite, range `[0.011208452, 0.9996138]`.
- Original rescue counts: `active_rescue=16`, `ctx_cells=149`.
- Proxy: `macro_auc=0.98897867`, `micro_auc=0.92916937`, `top5_hit=0.69863014`.

Decision: hold v102 as a valid original Run-mode candidate, but do not submit while v101 is pending and before a more conservative v103 rescue variant is considered.
