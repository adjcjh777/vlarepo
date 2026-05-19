# v134 Stable3 Guarded Rescue Decision Brief

Updated: 2026-05-19 11:42 UTC

## Candidate

- Script: `birdclef-2026/scripts/birdclef_probe_v134_stable3_guarded_rescue.py`
- Probe output: `experiments/v134_stable3_guarded_rescue_probe.csv`
- Materialize script: `birdclef-2026/scripts/birdclef_prepare_v134_stable3_guarded_rescue.py`
- Materialized notebook dir: `birdclef-2026/notebooks/v134-stable3-guarded-rescue`
- Scope: local-only blocked probe; no Kaggle push and no real submission.

## Motivation

`v131` confirmed the best current top5-aware clean component is the stable `47158son13/22/23 + v112_backtracking_remap + positive w0.7` triad. `v134` adds a `v103`-inspired row-level top-hit preservation guard to test whether that component can gain extra anti-collapse safety without giving up top5.

## Results

Baselines:

| candidate | macro | micro | top1 | top5 |
| --- | ---: | ---: | ---: | ---: |
| `v114_clean_selfblend_baseline` | 0.97920102 | 0.91572402 | 0.23287671 | 0.52054795 |
| `v110_clean_baseline` | 0.97911204 | 0.91481637 | 0.21917808 | 0.52054795 |

Best `v114` row:

| candidate | macro | micro | top1 | top5 | active cells |
| --- | ---: | ---: | ---: | ---: | ---: |
| `v134_v114_clean_selfblend_w0.9_t0.7_m0.08_top50` | 0.97979134 | 0.91924338 | 0.23287671 | 0.52054795 | 176 |

Key pattern:

- the top-hit threshold and margin settings did not change the best row;
- the best row is effectively the stable3 positive rescue with a stronger row-level guard interpretation;
- compared with `v131`, macro and top5 stay unchanged, while micro improves from `0.91861043` to `0.91924338`.

## Interpretation

`v134` does not create a new submit-ready family, but it slightly improves the anti-collapse profile of the stable3 route:

- no top5 regression;
- no macro regression relative to `v131`;
- a small micro gain;
- still far below the confidence needed to spend a real slot after `v127 = 0.883`.

## Decision

`HOLD-guarded-component - do not submit v134`

Use `v134` as the current best local continuation of the stable3 clean family. It is a better starting component than `v131`, but still not strong enough to justify immediate real submission.

## Next Action

- Prefer `v134` over `v131` as the stable3 baseline for future local work.
- Use the materialized `v134-stable3-guarded-rescue` notebook as the next candidate handoff package when a later Run-mode verification is worth doing.
- Keep today's slot 5 unused.
- If a later follow-up is needed, build around `v134` plus stronger grouped anti-collapse screening rather than reopening the broad clean-router family.
