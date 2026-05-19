# v103 Submission Decision Brief

Updated: 2026-05-19 03:20 UTC

## Candidate

- `v103-guarded-macro-risk-rescue`
- Local path: `birdclef-2026/notebooks/v103-guarded-macro-risk-rescue`
- Kaggle kernel: `junhaochengadjcjh7u7/bc26-v103-guarded-macro-rescue`
- Run-mode output: `birdclef-2026/outputs/v103-guarded-macro-risk-rescue-v1`

## Original Change

v103 is not a public notebook copy. It continues the private v86/v102 line and adds an original guard layer:

- reduce v102 rescue strengths;
- require positive per-cell rescue evidence before full rescue mixing;
- add a row-level top-hit preservation guard for confident v84-like anchor winners;
- preserve high-AUC and rare-class conservative guards.

## Evidence

- Kaggle Run-mode status: `COMPLETE`.
- Runtime: about `239s` before save and about `251s` through nbconvert, below 90 minutes.
- Metadata: private, CPU-only, internet disabled, competition source `birdclef-2026`.
- Output: `submission.csv` shape `(120,235)`, finite, no duplicate row IDs, range `[0.011422446, 0.99943465]`.
- Original guard counts from log:
  - `active_rescue=16`
  - `positive_rescue_cells=2068`
  - `top_hit_guard_cells=423`
  - `ctx_cells=22`
- Local dry-run proxy:
  - `macro_auc=0.98906455`
  - `micro_auc=0.92885549`
  - `top1_hit=0.38356164`
  - `top5_hit=0.71232877`
- Compared with v102 proxy:
  - macro improved from `0.98897867` to `0.98906455`;
  - top5 improved from `0.69863014` to `0.71232877`;
  - micro decreased slightly from `0.92916937` to `0.92885549`;
  - top1 remained unchanged at `0.38356164`.
- v103 is a close conservative refinement of v102: flattened output correlation `0.99991883`, mean absolute difference `0.00059379`, max absolute difference `0.08139174`.

## Decision

`HOLD - do not submit v103 while v101 is still pending`

Reason:

- v103 is the best current original Run-mode candidate on the local proxy tradeoff, but v101 ref `52795021` is still `PENDING`.
- The goal gate is still not reached: latest known best visible score is `0.949`, top20 cutoff is `0.953`, and top5 cutoff is `0.958`.

## Next Action

When v101 scores:

- if v101 reaches or clearly improves the anchor, reassess whether an original v103 slot is worth the risk;
- if v101 fails or underperforms, consider v103 as the next original real-submission candidate after a final quota check.
