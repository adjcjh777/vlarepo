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

1. `v134_stable3_guarded_rescue`
   Evidence: macro `0.97979134`, micro `0.91924338`, top1 `0.23287671`, top5 `0.52054795`, `blocked stable3 with positive rescue and top-hit guard`.
   Status: `next_day_or_later`, evidence `blocked_top5aware_guarded`, same-family recent fails `0`, risk `low_to_medium`, `same macro as v131 with slightly stronger anti-collapse guard and higher micro`.

2. `v131_stable3_top5aware`
   Evidence: macro `0.97979134`, micro `0.91861043`, top1 `0.23287671`, top5 `0.52054795`, `blocked top5-aware stable3 on v110/v114`.
   Status: `next_day_or_later`, evidence `blocked_top5aware`, same-family recent fails `0`, risk `low_to_medium`, `stable3 component confirmed after v127 fallout`.

3. `v129_blocked_clean_router`
   Evidence: macro `0.97970207`, micro `0.91617178`, top1 `0.24657534`, top5 `0.52054795`, `leave-one-soundscape-out gain with stable v112 triad`.
   Status: `next_day_or_later`, evidence `blocked_grouped`, same-family recent fails `0`, risk `low_to_medium`, `grouped validation positive but weaker than v131`.

4. `v103_guarded_macro_rescue`
   Evidence: macro `0.98906455`, micro `0.92885549`, top1 `0.38356164`, top5 `0.71232877`, `strongest proxy but no real-score proof`.
   Status: `local_only_until_compliance_clear`, evidence `same_row_high_proxy`, same-family recent fails `0`, risk `high`, `mechanism-rich evidence not today's slot5`.

5. `v102_original_macro_rescue`
   Evidence: macro `0.98897867`, micro `0.92916937`, top1 `0.38356164`, top5 `0.69863014`, `strong proxy but weaker guard than v103`.
   Status: `local_only_until_compliance_clear`, evidence `same_row_high_proxy`, same-family recent fails `0`, risk `high`, `mechanism base not immediate submit`.

6. `v126_min10_w0.7_rankcal`
   Evidence: macro `0.98021860`, micro `0.91700965`, top1 `0.23287671`, top5 `0.52054795`, `support>=10 macro gain without grouped proof`.
   Status: `local_only_until_extra_screen`, evidence `same_row_support10`, same-family recent fails `2`, risk `medium_to_high`, `same family as v127; do not submit without stronger anti-collapse screen`.

7. `v127_memorysafe_nontsubasa_router`
   Evidence: macro `0.98008089`, micro `0.91595668`, top1 `0.20547945`, top5 `0.52054795`, `real score invalidated same-family trust`.
   Status: `retired`, evidence `real_submit`, same-family recent fails `2`, risk `very_high`, `real-score collapse; do not retry near-neighbor blindly`.

8. `v105_rankrestored_perch`
   Evidence: macro `0.97751210`, micro `0.81765567`, top1 `0.00000000`, top5 `0.08219178`, `small micro recovery but top5 still collapsed`.
   Status: `do_not_submit`, evidence `same_row_clean_fallback`, same-family recent fails `0`, risk `very_high`, `retired`.

9. `v104_perch_only_guarded`
   Evidence: macro `0.97751210`, micro `0.78763929`, top1 `0.00000000`, top5 `0.08219178`, `license-clean but ranking collapse`.
   Status: `do_not_submit`, evidence `same_row_clean_fallback`, same-family recent fails `0`, risk `very_high`, `retired`.

## Current Guard

- Anchor remains `v87 = 0.949`.
- Completed non-positive streak after the anchor is `5`.
- Decision remains `NO-SLOT5-TODAY`; for the next real candidate window, start from the stable3 component rather than a broad near-neighbor of `v127`.
