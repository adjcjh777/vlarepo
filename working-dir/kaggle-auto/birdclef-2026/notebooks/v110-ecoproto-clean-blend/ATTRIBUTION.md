# Attribution

This candidate continues the private original v86/v102/v103/v104-v109 line.

Original v110 change:
- removes unknown-license runtime dependencies `jaejohn/perch-meta` and `tuckerarrants/bc2026-distilled-sed-public`;
- rebuilds train Perch features inside the Kaggle notebook from competition train soundscapes;
- replaces the SED branch with a Perch-only surrogate view;
- keeps the v103-v106 positive-rescue and top-hit guard idea with conservative class rescue strengths;
- adds EcoProto: class embedding prototypes from competition labels, gated by site/hour priors and temporal consistency;
- self-replays a v107-like rank-ceiling branch and a v109-like EcoProto rank-launch branch;
- blends the two clean branches at 0.40/0.60 based on the local v110 probe;
- keeps CPU-only/no-internet metadata and public, recorded Perch inputs.

Run-mode only until v110 runtime, schema, proxy, and compliance evidence pass.
