# v130 Stable-3 Router Decision Brief

Updated: 2026-05-19 11:02 UTC

## Candidate

- Script: `birdclef-2026/scripts/birdclef_probe_v130_stable3_router.py`
- Probe output: `experiments/v130_stable3_router_probe.csv`
- Scope: local-only narrow stable-class router probe; no Kaggle push and no real submission.

## Motivation

v129 found that the only clean router classes selected across all 10 leave-one-soundscape-out folds were:

- `47158son13`
- `47158son22`
- `47158son23`

All three used `v112_backtracking_remap` as the clean side source. v130 tests whether this stable 3-class structure is a stronger and more materialization-ready target than the broader v126/v129 routers.

## Results

Baselines:

| candidate | macro | micro | top1 | top5 |
| --- | ---: | ---: | ---: | ---: |
| `v114_clean_selfblend_baseline` | 0.97920102 | 0.91572402 | 0.23287671 | 0.52054795 |
| `v110_clean_baseline` | 0.97911204 | 0.91481574 | 0.21917808 | 0.52054795 |

Best same-row row:

| candidate | macro | micro | top5 | active cells |
| --- | ---: | ---: | ---: | ---: |
| `v130_v114_clean_selfblend_same_full_w0.9` | 0.98008650 | 0.91663030 | 0.50684932 | 360 |

Best blocked full-column row:

| candidate | macro | micro | top5 | active cells |
| --- | ---: | ---: | ---: | ---: |
| `v130_v114_clean_selfblend_blocked_full_w0.35` | 0.97987567 | 0.91638119 | 0.50684932 | 360 |

Best blocked top5-preserving row:

| candidate | macro | micro | top5 | active cells |
| --- | ---: | ---: | ---: | ---: |
| `v130_v114_clean_selfblend_blocked_positive_w0.9` | 0.97979134 | 0.91924338 | 0.52054795 | 176 |

## Interpretation

- The stable 3-class router is real but not strong enough yet.
- Same-row full-column mixing reaches macro `0.98008650`, close to v127's proxy `0.98008089`, but it drops top5 to `0.50684932`.
- Blocked full-column mixing is weaker at `0.97987567` and still drops top5.
- Blocked positive-only mixing preserves top5 and improves micro to `0.91924338`, but macro remains below v127/v128.
- This confirms that the stable 3-class pattern is a useful component, not a standalone fifth-slot candidate.

## Decision

`HOLD-component - do not submit v130`

Do not materialize v130 as a real Kaggle notebook while v127 is pending. If v127 fails or scores poorly, v130's stable 3-class component can be reused inside a broader grouped meta-router, but not as a direct next submission.

## Next Action

- Keep `47158son13/22/23 + v112_backtracking_remap` as a stable, clean component.
- Do not spend the fifth real submission slot until v127 score/error is known.
- If a follow-up is needed, combine this stable component with a top5-aware objective and blocked validation, rather than using same-row macro as the promotion gate.

