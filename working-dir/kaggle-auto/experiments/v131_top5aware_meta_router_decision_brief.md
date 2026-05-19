# v131 Top5-Aware Meta Router Decision Brief

Updated: 2026-05-19 11:08 UTC

## Candidate

- Script: `birdclef-2026/scripts/birdclef_probe_v131_top5aware_meta_router.py`
- Probe output: `experiments/v131_top5aware_meta_router_probe.csv`
- Selection output: `experiments/v131_top5aware_meta_router_selection.csv`
- Scope: local-only grouped meta-router probe; no Kaggle push and no real submission.

## Motivation

v129 and v130 suggested that:

- the stable clean component is `47158son13/22/23` from `v112_backtracking_remap`;
- broad routers can gain macro but hurt top5;
- positive-only narrow routers preserve top5 but need a principled selection rule.

v131 turns that into an explicit search procedure under leave-one-soundscape-out validation. It greedily adds class-source interventions only when the blocked objective improves in this order:

1. `top5_hit`
2. `macro_auc`
3. `micro_auc`

## Results

Baselines:

| candidate | macro | micro | top1 | top5 |
| --- | ---: | ---: | ---: | ---: |
| `v114_clean_selfblend_baseline` | 0.97920102 | 0.91572402 | 0.23287671 | 0.52054795 |
| `v110_clean_baseline` | 0.97911204 | 0.91481637 | 0.21917808 | 0.52054795 |

Best v131 path for `v114_clean_selfblend`:

| step | selected class | source | mode | weight | blocked macro | blocked micro | blocked top5 |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| 1 | `47158son13` | `v112_backtracking_remap` | `positive` | 0.7 | 0.97941185 | 0.91668340 | 0.52054795 |
| 2 | `47158son22` | `v112_backtracking_remap` | `positive` | 0.7 | 0.97960159 | 0.91768880 | 0.52054795 |
| 3 | `47158son23` | `v112_backtracking_remap` | `positive` | 0.7 | 0.97979134 | 0.91861043 | 0.52054795 |

The same three-step path appears for `v110_clean`, ending at:

- macro `0.97970236`
- micro `0.91772625`
- top5 `0.52054795`

## Interpretation

v131 confirms that the best top5-aware grouped meta-router under the current evidence is exactly the stable 3-class positive router already hinted by v129/v130.

That is useful because it makes the component choice less arbitrary, but it does not change the promotion decision:

- v131 preserves top5, which is good;
- v131 improves macro over the clean baselines, which is real progress;
- v131 still remains below v127 proxy macro `0.98008089` and below v126 same-row support>=10 router `0.98021860`.
- A follow-up `gpt-5.3-codex-spark` exploration check over the v129/v130/v131 CSVs found that the remaining support>=10 top5-preserving clean combinations are the `v119_roniheka_hgnet` pairs for `47158son20`, `47158son21`, and `47158son25`, but none displaced the stable `v112` triad under the current blocked objective.

## Decision

`HOLD-confirmed-component - do not submit v131`

v131 is the cleanest confirmation so far that the stable 3-class `v112` component is worth keeping. It is not strong enough to become the fifth-slot candidate while v127 is still pending.

## Next Action

- Keep `47158son13/22/23 + v112_backtracking_remap + positive w0.7` as the current best top5-aware clean component.
- Do not materialize v131 as a Kaggle notebook yet.
- Wait for v127 score/error before any fifth-slot decision.
- Keep submission strategy anchored to the current best visible score `0.949`; do not switch to a different method family until five consecutive real-submit outcomes have failed to improve that anchor.
- If a follow-up is needed after v127 resolves, build around this component rather than reopening a broad unconstrained router search.
- Do not launch a broad `v132` local sweep now; if v127 fails or scores poorly, start with a very small follow-up around the stable3 component and only then reopen search scope.
