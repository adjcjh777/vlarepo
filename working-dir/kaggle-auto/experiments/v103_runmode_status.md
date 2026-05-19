# v103 Run-Mode Status

Updated: 2026-05-19 03:20 UTC

## Candidate

- Local path: `birdclef-2026/notebooks/v103-guarded-macro-risk-rescue`
- Kaggle kernel: `junhaochengadjcjh7u7/bc26-v103-guarded-macro-rescue`
- Version: `1`
- Source line: private original `v86` plus `v102` macro-risk rescue

## Current Status

- Kaggle Run-mode version 1: `COMPLETE`.
- Output archive: `birdclef-2026/outputs/v103-guarded-macro-risk-rescue-v1`.
- Real competition submission: not submitted.
- Reason for no real submission: v101 ref `52795021` is still `PENDING`.

## Completed Checks

- CPU-only/no-internet status;
- runtime under 90 minutes;
- `submission.csv` shape and row/class order;
- NaN/inf/range;
- v103 log count line `V103 guarded macro-risk rescue counts`;
- proxy score versus v102.

## Key Results

- Runtime: about `239s` before save and about `251s` through nbconvert.
- Output: `(120,235)`, finite, range `[0.011422446, 0.99943465]`.
- Original guard counts: `positive_rescue_cells=2068`, `top_hit_guard_cells=423`, `ctx_cells=22`.
- Proxy: `macro_auc=0.98906455`, `micro_auc=0.92885549`, `top5_hit=0.71232877`.

Decision: hold v103 as the current strongest original Run-mode candidate, but do not submit until v101 resolves and quota/leaderboard gates are rechecked.
