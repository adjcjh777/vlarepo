# v102 Submission Decision Brief

Updated: 2026-05-19 03:04 UTC

## Candidate

- `v102-original-macro-risk-rescue`
- Local path: `birdclef-2026/notebooks/v102-original-macro-risk-rescue`
- Kaggle kernel: `junhaochengadjcjh7u7/bc26-v102-original-macro-risk-rescue`
- Run-mode output: `birdclef-2026/outputs/v102-original-macro-risk-rescue-v1`

## Evidence

- Kaggle Run-mode status: `COMPLETE`
- Runtime: about `249.49s`, below 90 minutes.
- Metadata: private, CPU-only, internet disabled, competition source `birdclef-2026`.
- Output: `submission.csv` shape `(120,235)`, finite, no duplicate row IDs, range `[0.011208452, 0.9996138]`.
- Original logic confirmed in log:
  - `protect_anchor=35`
  - `rare_floor=176`
  - `macro_weak=12`
  - `macro_mild=4`
  - `texture_prior_rescue=13`
  - `active_rescue=16`
  - `ctx_cells=149`
- Local dry-run proxy: `macro_auc=0.98897867`, `micro_auc=0.92916937`, `top5_hit=0.69863014`.
- Correlation against available 120-row public side outputs is low (`corr` about `0.22..0.39`), so v102 is materially different from the known Proto/SED sidecar family.

## Decision

`HOLD - do not submit v102 now`

Reasons:

- v101 real submission ref `52795021` is still `PENDING`; further real submissions are locked.
- v102 is original and valid in Run-mode, but the proxy profile is mixed: macro is strong while micro/top-hit are weak.
- Quick local rank blends with SED/Proto/subm2 side outputs did not improve over standalone v102 on the local proxy.

## Next Action

Wait for v101 to score. If v101 fails or scores below anchor, use v102 as the base for a more conservative v103 original lane:

- keep v102's class-wise macro-risk mechanism;
- reduce active rescue strength for weak mid-support classes;
- add a top-hit preservation guard so macro rescue does not damage confident primary calls;
- run v103 only in Kaggle Run-mode first.
