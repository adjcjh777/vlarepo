# v128 Pending-Safe Candidate Queue Decision

Updated: 2026-05-19 10:40 UTC

## Situation

- Active real submission: `v127-memorysafe-nontsubasa-router`, Kaggle ref `52807175`.
- Latest refreshed status: `PENDING` at `2026-05-19 10:31 UTC`.
- UTC day usage after v127: `4/5`.
- Goal gate remains not reached: best visible `0.949`, top20 cutoff `0.954`, top5 cutoff `0.958`.

## Queue Evidence

The local-only queue audit is written to `experiments/v128_pending_safe_candidate_queue.csv`.

Top rows by train-window proxy:

| rank | candidate | macro | micro | top5 | status / blocker |
| --- | --- | ---: | ---: | ---: | --- |
| 1 | `v103-guarded-macro-risk-rescue-v1` | 0.98906455 | 0.92885549 | 0.71232877 | strongest original proxy, but unknown-license dependencies remain |
| 2 | `v102-original-macro-risk-rescue-v1` | 0.98897867 | 0.92916937 | 0.69863014 | same high-proxy family; not clean enough as a prize-route candidate |
| 3 | `v121-class-selective-tsubasa-v1` | 0.98275473 | 0.92510802 | 0.53424658 | original sparse sidecar, but inherits v120 hidden-RAM risk |
| 4 | `v120-clean-tsubasa-sidecar-v1` | 0.98139925 | 0.91435250 | 0.47945205 | retired after hidden-test memory failure |
| 5 | `v127-memorysafe-nontsubasa-router-v1` | 0.98008089 | 0.91595668 | 0.52054795 | current guarded submission is still pending |

The archived local `v87` and `v91` outputs are sample-only in this workspace, so this queue does not use them for train-window correlation. Diversity is measured against clean/local train-window branches such as `v110` and `v127`.

## Originality Boundary

Do not spend the fifth real slot on another public-reference-style fork or simple blend.

The next useful work should be a workspace-owned mechanism:

1. Treat `v103/v102` as evidence of a useful guard/rescue behavior, not as a submission artifact to copy.
2. Remove unknown-license runtime dependencies before any prize-route candidate.
3. Reconstruct the high-proxy signal from clean, in-notebook evidence:
   - row-level confidence preservation guard;
   - positive-evidence rescue gate;
   - per-class support floor;
   - rank-calibrated transfer onto the clean EcoProto anchor;
   - single-final-layer or post-final transformation to stay memory-safe.
4. Keep attribution explicit if any public notebook idea motivates a component, but make the executable candidate depend on our own code and allowed datasets.

## Decision

`RESEARCH-NEXT - v128/v129 license-clean v103-mechanism transfer`

- No Kaggle real submission while v127 is `PENDING`.
- Do not submit v103/v102 as-is.
- Build the next candidate only if it introduces a clean original mechanism that transfers the useful v103 guard/rescue behavior without unknown-license runtime inputs.
- Promotion gate for the next real slot: v127 score/error known, no pending row, UTC quota rechecked, static compliance pass, schema pass, CPU/no-internet pass, proxy materially above clean anchors or meaningfully diverse, and decision log updated before submission.

