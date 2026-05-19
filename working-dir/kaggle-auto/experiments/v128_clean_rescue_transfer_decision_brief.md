# v128 Clean Rescue Transfer Decision Brief

Updated: 2026-05-19 10:48 UTC

## Candidate

- Script: `birdclef-2026/scripts/birdclef_probe_v128_clean_rescue_transfer.py`
- Probe output: `experiments/v128_clean_rescue_transfer_probe.csv`
- Selection output: `experiments/v128_clean_rescue_transfer_selection.csv`
- Scope: local-only originality probe; no Kaggle push and no real submission.

## Motivation

The user requested more original work instead of continuing to copy public references. v103/v102 are the strongest local proxy family, but they remain blocked for direct prize-route use by unknown-license runtime dependencies. v128 therefore transfers the *mechanism* rather than the artifact:

- clean EcoProto anchor;
- clean side-source evidence from v112/v113/v119;
- per-class support floor;
- side source must beat anchor on train-window per-class AUC;
- rank-calibrated side evidence;
- positive-evidence-only rescue cells;
- row-level confidence preservation guard.

The v103 output is used only as a diagnostic correlation reference in the CSV. It is not used to construct any v128 candidate score.

## Results

Baselines:

| candidate | macro | micro | top1 | top5 |
| --- | ---: | ---: | ---: | ---: |
| `v114_clean_selfblend_baseline` | 0.97920102 | 0.91572402 | 0.23287671 | 0.52054795 |
| `v110_clean_baseline` | 0.97911204 | 0.91481574 | 0.21917808 | 0.52054795 |

Best v128 row:

| candidate | macro | delta vs v114 | micro | top5 | classes | active cells | corr vs anchor |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `v128_v114_clean_selfblend_min5_d0_w0.9_rm0_t0.7` | 0.97987635 | +0.00067533 | 0.92085607 | 0.52054795 | 6 | 350 | 0.99768118 |

Selected classes for the best row:

| class | support | source | anchor auc | side auc | delta | active cells |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| `47158son01` | 11 | `v119_roniheka_hgnet` | 0.999166 | 1.000000 | +0.000834 | 60 |
| `47158son13` | 22 | `v112_backtracking_remap` | 0.993506 | 0.999536 | +0.006030 | 58 |
| `47158son18` | 11 | `v112_backtracking_remap` | 0.999166 | 0.999166 | +0.000000 | 53 |
| `47158son21` | 20 | `v119_roniheka_hgnet` | 0.991000 | 0.991500 | +0.000500 | 58 |
| `47158son22` | 22 | `v112_backtracking_remap` | 0.993043 | 0.999536 | +0.006494 | 62 |
| `47158son23` | 22 | `v112_backtracking_remap` | 0.993506 | 1.000000 | +0.006494 | 59 |

## Comparison

v128 is original and clean, but it is not stronger than the current best original non-Tsubasa line:

- v126 support>=10 full-column router: macro `0.98021860`, micro `0.91700965`, top5 `0.52054795`.
- v127 memory-safe materialization: macro `0.98008089`, micro `0.91595668`, top5 `0.52054795`.
- v128 cell-level positive rescue: macro `0.97987635`, micro `0.92085607`, top5 `0.52054795`.

The micro gain is useful evidence, but the macro loss vs v126/v127 means v128 should not consume the fifth real submission slot.

## Decision

`HOLD-quality - do not submit v128`

The originality direction is valid, but the current cell-level positive rescue gate is too conservative for the macro objective. It improves over v114 but fails to beat v126/v127.

## Next Action

Do not materialize v128 as a Kaggle notebook. The next originality probe should not be another positive-only cell rescue. Prefer one of:

- a clean grouped meta-router with blocked validation across train soundscape files;
- a support-aware full-column router with an explicit top5 objective term;
- a memory-safe v126/v127 follow-up only after v127's real score or error is known.

