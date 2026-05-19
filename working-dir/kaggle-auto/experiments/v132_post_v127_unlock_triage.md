# v132 Post-v127 Unlock Triage

Updated: 2026-05-19 11:28 UTC

## Situation

- Current visible anchor: `v87 = 0.949`
- Latest guarded original submit: `v127 = 0.883`
- Non-positive streak since the anchor has reached `5`
- Updated rule now allows method-family change, but the next move must explicitly avoid another collapse like `0.883`

## What Changed

The gate is now unlocked, but that does **not** mean the last daily slot should be spent immediately.

The main reason is local risk concentration:

- `v127` is a real-score failure from the current clean-router family;
- `v126` has better local proxy than `v127`, but it is still the same broad family and has not yet earned a stronger anti-collapse screen than `v127` had;
- `v103` has the strongest proxy, but it still carries unknown-license runtime dependencies;
- `v104/v105` are cleaner, but were already rejected for catastrophic top1/top5 weakness.

## Triage

### `HOLD-TODAY` today slot 5 should stay unused unless new evidence appears

Do **not** spend today slot 5 on:

- another near-neighbor of the `v126/v127` clean-router family;
- a blind public-reference-style jump;
- a license-risk `v103` real submit without a separate explicit risk acceptance;
- a weak clean fallback like `v104/v105`.

### `NEXT-HIGH-CONFIDENCE` best current direction after the unlock

If a next real submit becomes necessary, the highest-signal direction is:

- start from the stable `47158son13/22/23 + v112_backtracking_remap + positive w0.7` component confirmed by `v129/v130/v131`;
- combine it with a stricter anti-collapse screen before any real slot:
  - blocked validation preserved top5;
  - no broad same-family gamble;
  - memory-safe notebook path is explicit.

### `LOCAL-ONLY` branches still worth offline evidence work

- `v103/v102` mechanism clean-up path:
  strongest proxy evidence, but still compliance-blocked
- stable3 top5-aware grouped router:
  safer and cleaner, but not yet strong enough for immediate real submit

## Decision

`NO-SLOT5-TODAY unless materially new evidence appears`

The unlock changes what we are *allowed* to explore, not what is *wise* to submit right now. After a `0.883` collapse, preserving the last slot is higher value than forcing one more speculative move from insufficient evidence.

