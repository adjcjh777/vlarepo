# v135 Next Window Runbook

Updated: 2026-05-19 12:12 UTC

## Current State

- UTC date is still `2026-05-19`
- Visible submissions today: `4`
- Best visible anchor remains `0.949`
- `v127` scored `0.883`
- `v134` has now passed Kaggle Run-mode and sits at guarded-pool rank `#1`

## What Not To Do

Before the UTC day rolls over, do **not**:

- spend slot 5 on a broad clean-router near-neighbor of `v127`;
- spend slot 5 on `v103` without a separate license-risk decision;
- burn the last slot on a weak clean fallback like `v104/v105`;
- open a broad parameter sweep just because method-family change is technically unlocked.

## First Action After UTC Reset

1. Refresh the submission table and confirm the new UTC date.
2. Rebuild `experiments/v133_next_candidate_scorecard.csv` with the latest local state.
3. Re-check that `v134` is still guarded-pool rank `#1`.
4. Only then decide whether `v134` should be promoted from guarded pool to real-submit candidate.

## Promotion Gate For v134

`v134` should only move forward if all of the following still hold:

- external Run-mode remains `COMPLETE`;
- `submission.csv` stays schema-valid;
- no new evidence contradicts the stable3 route;
- the anti-collapse scorecard still ranks `v134` above every alternative;
- there is no stronger clean or compliance-safe branch that has appeared since the last refresh.

## Fallback Order

If `v134` is not promoted after the next refresh, use this order:

1. `v134_stable3_guarded_rescue`
2. `v131_stable3_top5aware`
3. `v129_blocked_clean_router`
4. `v103/v102` only after explicit compliance-cleanup work

Keep `v126` below those options until it has a stronger anti-collapse screen than the same-family evidence available now.

## Decision

`WAIT-FOR-NEXT-UTC-WINDOW`

The highest-value move right now is not another probe and not the final daily slot. It is preserving a clean decision boundary so the next window starts from the best guarded candidate with the least chance of another `0.883`-style failure.

