# Attribution

This candidate continues the private original v86/v102/v103/v104-v109 line.

Original v112 change:
- removes unknown-license runtime dependencies `jaejohn/perch-meta` and `tuckerarrants/bc2026-distilled-sed-public`;
- rebuilds train Perch features inside the Kaggle notebook from competition train soundscapes;
- replaces the unknown-license SED branch with `backtracking/birdclef2026-clean-sed-b0` (CC0-1.0);
- adds an original train-window clean-SED column remap and trust-strength layer;
- keeps the v103-v106 positive-rescue and top-hit guard idea with conservative class rescue strengths;
- adds EcoProto: class embedding prototypes from competition labels, gated by site/hour priors and temporal consistency;
- self-replays a v107-like rank-ceiling branch and a v109-like EcoProto rank-launch branch;
- blends the two clean branches at 0.40/0.60 based on the local v111 probe;
- emits `v112_clean_sed_remap_diagnostics.csv` for class-order/calibration audit;
- keeps CPU-only/no-internet metadata and public, recorded Perch plus clean SED inputs.

Run-mode only until v112 runtime, schema, proxy, and compliance evidence pass.
