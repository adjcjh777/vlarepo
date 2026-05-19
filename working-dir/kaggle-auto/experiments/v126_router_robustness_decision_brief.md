# v126 Router Robustness Decision Brief

Updated: 2026-05-19 10:03 UTC

## Candidate

- Robustness script: `birdclef-2026/scripts/birdclef_probe_v126_router_robustness.py`
- Probe output: `experiments/v126_router_robustness_probe.csv`
- Selection output: `experiments/v126_router_robustness_selection.csv`
- Scope: local-only robustness probe for the v125 non-Tsubasa router; no Kaggle push and no real submission.

## Why This Was Needed

v125 found an original non-Tsubasa sparse class router, but its best formula included `plcjay1`, a class with only `1` dry-run positive. Before spending notebook materialization effort, the router needed a support-floor stress test.

v126 keeps the same original mechanism:

- anchor: v114 clean selfblend;
- side sources: v112 Backtracking remap, v113 LantingGuo MelNorm, v119 Roniheka HGNet;
- selection: side source must beat anchor per-class AUC on train soundscape windows;
- calibration: rank-calibrate the selected side source onto the anchor distribution;
- intervention: support-shrunk sparse class routing.

## Robustness Results

Baseline:

- v114 anchor macro: `0.97920102`
- v114 anchor micro: `0.91572402`
- v114 anchor top5: `0.52054795`

Top v126 rows:

| candidate | support floor | classes | macro | delta vs v114 | micro | top5 |
|---|---:|---:|---:|---:|---:|---:|
| `v126_min1_w0.7_rankcal` | 1 | 6 | `0.98060057` | `+0.00139955` | `0.91703497` | `0.52054795` |
| `v126_min2_w0.7_rankcal` | 2 | 5 | `0.98021860` | `+0.00101758` | `0.91700965` | `0.52054795` |
| `v126_min10_w0.7_rankcal` | 10 | 5 | `0.98021860` | `+0.00101758` | `0.91700965` | `0.52054795` |
| `v126_min15_w0.7_rankcal` | 15 | 4 | `0.98018069` | `+0.00097967` | `0.91689689` | `0.50684932` |

The low-support `plcjay1` class is not required for a positive result. Excluding it leaves the support>=10 5-class router above v114 by about `+0.00102` macro.

Selected robust classes for the support>=10 row:

- `47158son01`, support `11`, source `v119_roniheka_hgnet`, delta `+0.00083403`
- `47158son13`, support `22`, source `v112_backtracking_remap`, delta `+0.00602968`
- `47158son21`, support `20`, source `v119_roniheka_hgnet`, delta `+0.00050000`
- `47158son22`, support `22`, source `v112_backtracking_remap`, delta `+0.00649351`
- `47158son23`, support `22`, source `v112_backtracking_remap`, delta `+0.00649351`

## Decision

`PLAN-MATERIALIZE - Run-mode only, no real submission yet`

v126 upgrades v125 from a fragile idea to a materialization-worthy local candidate. The support>=10 row is the preferred candidate because it removes the 1-positive class while preserving most of the macro gain.

It is still not real-submit eligible because:

- top5 does not improve over v114;
- direct v112 and v119 were rejected globally, so the value comes only from narrow class routing;
- a compliant notebook must recompute the side evidence rather than mount prior output CSVs;
- hidden-test RAM risk remains unknown after v120's memory failure.

## Next Action

Materialize a `v126-nontsubasa-router-runmode` notebook only if it can stay memory-aware:

- recompute the clean v114-like final output once;
- recompute v112/v119 side evidence sequentially, not simultaneously;
- immediately delete ONNX sessions and large arrays after each side branch;
- apply the support>=10 5-class post-final rank-calibrated router;
- write `v126_router_summary.csv` with selected classes, sources, gates, and score ranges;
- run Kaggle Run-mode only first;
- do not real-submit unless Run-mode output, schema, proxy, correlation, compliance, and hidden-memory risk review all pass.

Operational note: in the current shell, `kaggle` is not on PATH, but the installed CLI exists at `/Users/junhaocheng/Library/Python/3.9/bin/kaggle`.
