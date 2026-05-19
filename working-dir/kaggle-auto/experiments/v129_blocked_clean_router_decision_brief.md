# v129 Blocked Clean Router Decision Brief

Updated: 2026-05-19 10:55 UTC

## Candidate

- Script: `birdclef-2026/scripts/birdclef_probe_v129_blocked_clean_router.py`
- Probe output: `experiments/v129_blocked_clean_router_probe.csv`
- Selection output: `experiments/v129_blocked_clean_router_selection.csv`
- Scope: local-only blocked validation; no Kaggle push and no real submission.

## Motivation

v125/v126/v128 selected clean router classes on the same 120 train-window rows used for scoring. v129 makes this originality lane stricter by using 10 train soundscape files as groups:

- hold out one soundscape file;
- select per-class clean side source on the other 9 files only;
- rank-calibrate clean side predictions to the train anchor distribution;
- apply the learned router to the held-out file;
- assemble out-of-fold predictions across all 10 held-out files.

This tests whether the clean non-Tsubasa router signal is stable across files instead of only fitting the visible proxy rows.

## Results

Baselines:

| candidate | macro | micro | top1 | top5 |
| --- | ---: | ---: | ---: | ---: |
| `v114_clean_selfblend_baseline` | 0.97920102 | 0.91572402 | 0.23287671 | 0.52054795 |
| `v110_clean_baseline` | 0.97911204 | 0.91481574 | 0.21917808 | 0.52054795 |

Best blocked row:

| candidate | macro | delta vs v114 | micro | top1 | top5 | avg classes/fold | corr vs anchor |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `v129_v114_clean_selfblend_min5_d0.002_w0.35_top5guard0` | 0.97970207 | +0.00050105 | 0.91617178 | 0.24657534 | 0.52054795 | 3.4 | 0.99937804 |

The same score appears with `min_support=10`, so the weak gain does not depend on very low-support classes.

Stable selected classes in the best row:

| class | source | folds selected | mean train support | mean train delta | held-out active rows |
| --- | --- | ---: | ---: | ---: | ---: |
| `47158son22` | `v112_backtracking_remap` | 10 | 19.8 | +0.006669 | 120 |
| `47158son23` | `v112_backtracking_remap` | 10 | 19.8 | +0.006576 | 120 |
| `47158son13` | `v112_backtracking_remap` | 10 | 19.8 | +0.006153 | 120 |
| `47158son21` | `v119_roniheka_hgnet` | 2 | 10.0 | +0.004592 | 24 |
| `47158son25` | `v119_roniheka_hgnet` | 1 | 44.0 | +0.007457 | 12 |
| `47158son20` | `v119_roniheka_hgnet` | 1 | 11.0 | +0.002812 | 12 |

## Interpretation

The clean router signal is real but small under grouped validation:

- v129 improves v114 by about `+0.00050` macro and top1 by about `+0.01370`.
- v129 preserves top5 but does not improve it.
- v129 is weaker than v128 same-row cell rescue (`0.97987635`), v127 memory-safe materialization (`0.98008089`), and v126 same-row support>=10 router (`0.98021860`).
- The robust signal is concentrated in three `47158son` classes from `v112_backtracking_remap`; the remaining selected classes are fold-fragile.

## Decision

`HOLD-validated-small-gain - do not submit v129`

v129 is valuable because it validates that part of the clean router survives leave-one-soundscape-out evaluation. It is not strong enough to consume a real submission slot, especially while v127 is still pending.

## Next Action

- Keep the stable 3-class pattern (`47158son13`, `47158son22`, `47158son23`) as evidence for future clean meta-routing.
- Do not materialize v129 as a Kaggle notebook.
- Wait for v127 score/error before any fifth-slot decision.
- If v127 fails or scores poorly, the next original probe should test a stricter 3-class memory-safe router or a grouped meta-router with a real top5-aware objective, not another broad same-row router.

