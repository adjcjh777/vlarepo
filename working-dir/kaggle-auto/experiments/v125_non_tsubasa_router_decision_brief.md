# v125 Non-Tsubasa Class Router Decision Brief

Updated: 2026-05-19 09:54 UTC

## Candidate

- Probe script: `birdclef-2026/scripts/birdclef_probe_v125_non_tsubasa_router.py`
- Probe output: `experiments/v125_non_tsubasa_router_probe.csv`
- Class diagnostics: `experiments/v125_non_tsubasa_router_class_diagnostics.csv`
- Scope: local-only dry-run probe; no Kaggle submission and no notebook materialization yet.

## Original Contribution

v125 addresses the user requirement to add our own innovation rather than only follow public work.

The idea is a workspace-owned sparse class router:

- keep the clean EcoProto anchor (`v110` / `v114`) as the main prediction surface;
- exclude all Tsubasa branches from this probe;
- audit only the clean non-Tsubasa side sources already run in Kaggle Run-mode:
  - `v112_backtracking_remap`;
  - `v113_lantingguo_melnorm`;
  - `v119_roniheka_hgnet`;
- compute per-class AUC deltas on train soundscape windows;
- route only classes where a side source beats the anchor by a declared margin;
- shrink intervention by class support;
- rank-calibrate side evidence onto the anchor distribution before blending.

This is not a direct public-kernel fork or global blend. It is an original decision layer that asks where each clean side source has class-specific evidence and suppresses the rest.

## Best Local Evidence

Best row:

- `v114_clean_selfblend_router_m0_w0.7_rankcal`
- Formula: per-class best non-Tsubasa side; margin `0.0`; weight `0.7`; mode `rankcal`; support shrink `log1p`
- Macro: `0.98060057`
- Micro: `0.91703497`
- Top1: `0.23287671`
- Top5: `0.52054795`
- Scored classes: `22`
- Correlation vs anchor: `0.99706961`
- MAD vs anchor: `0.00218707`
- Routed classes: `6`
- Sources used: `v112_backtracking_remap`; `v119_roniheka_hgnet`
- Selected classes: `47158son01`, `47158son13`, `47158son21`, `47158son22`, `47158son23`, `plcjay1`

Comparison:

- v114 clean selfblend: macro `0.97920102`
- v125 best local row: macro `0.98060057`
- Local gain vs v114: about `+0.00140`
- v121 class-selective Tsubasa proxy remains higher at `0.98275473`, but v121 is memory-risk and not submit-safe as-is.

## Risk Assessment

Do not real-submit v125 from this evidence alone.

Reasons:

- The best gain is concentrated in only `6` scored classes.
- `plcjay1` has only `1` positive dry-run sample, so its positive delta is fragile.
- Several routed classes already have anchor AUC near `1.0`; small rank movements can look larger than they are.
- Top5 does not improve over v114.
- A submission-safe notebook would need to recompute the clean anchor plus v112/v119 side branches without mounting prior output CSVs; this requires a separate memory/runtime hardening pass.
- Direct v112 and v119 branches were previously rejected on quality, so v125 should be treated as a sparse correction idea, not as proof that either side source is globally reliable.

## Decision

`HOLD - innovation evidence, do not submit`

Preserve v125 as a genuine non-Tsubasa innovation probe. It is useful because it finds a cleaner, lower-copying route to extract signal from otherwise rejected CC0 side branches. It is not yet strong enough to spend a real Kaggle slot or choose as a final candidate.

## Next Action

If continuing this lane, the next step should be a memory-aware `v126` materialization plan:

- recompute v114-like clean anchor once;
- compute only the minimal side evidence needed for the 6 routed classes;
- unload each ONNX session before the next branch;
- apply the rank-calibrated router after the clean final output;
- run Kaggle Run-mode only;
- submit only if runtime, hidden-memory risk, schema, proxy, correlation, and compliance all pass.

Otherwise, search for a new audited side source with broader class-level positive deltas and stronger top-k evidence.
