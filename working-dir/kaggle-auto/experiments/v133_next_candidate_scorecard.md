# v133 Next Candidate Scorecard

Updated: 2026-05-19 11:34 UTC

## Purpose

After `v127 = 0.883`, the method-family gate is unlocked, but the next move must avoid another collapse. This scorecard turns the current evidence into a practical ranking for the next candidate window.

## Ranking Logic

Filter first:

- reject branches with known collapse patterns such as `top1=0` or `top5` collapse;
- reject unresolved `PENDING` or `ERROR-memory` candidates as immediate follow-ons;
- reject broad same-family retries that do not add a stronger anti-collapse screen than `v127`.

Rank second:

- `macro` improvement matters;
- `top5` must be preserved;
- grouped / blocked stability is a strong positive;
- compliance debt is a strong negative;
- recent real-score collapse from the same family is a strong negative.

## Current Ranking

1. `v131_stable3_top5aware`
   Evidence: blocked top5-aware stable3 on `v110/v114`, `macro=0.97979134`, `top5=0.52054795`, stable classes `47158son13/22/23 + v112_backtracking_remap + positive w0.7`.
   Status: highest-priority local continuation, not a same-day slot5 candidate.

2. `v129_blocked_clean_router`
   Evidence: grouped validation `macro=0.97970207`, `top1=0.24657534`, `top5=0.52054795`, stable `v112` triad.
   Status: backup local continuation; weaker than `v131`.

3. `v126_min10_w0.7_rankcal`
   Evidence: strongest clean-router broad proxy `macro=0.98021860`, `top5=0.52054795`.
   Risk: same broad family neighborhood as `v127=0.883`, so it should not be promoted without a stronger anti-collapse screen.
   Status: local-only until further guarded validation.

4. `v103/v102`
   Evidence: strongest proxy family (`v103 macro=0.98906455`, `top5=0.71232877`; `v102 macro=0.98897867`, `top5=0.69863014`).
   Risk: unknown-license runtime dependencies still block real submission.
   Status: mechanism-rich evidence pool, not immediate submit candidates.

5. `v104/v105`
   Evidence: license-clean but `top5=0.08219178`, `top1=0`.
   Status: retired for real submission.

## Decision

`NO-SLOT5-TODAY`

The highest-value move is to preserve today's final slot and carry forward a narrower anti-collapse path. For the next real candidate window, start from the `v131` stable3 component, not from a broad near-neighbor of `v127`.

