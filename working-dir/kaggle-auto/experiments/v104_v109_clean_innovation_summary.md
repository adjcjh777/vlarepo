# v104-v109 License-Clean Innovation Summary

Updated: 2026-05-19 04:44 UTC

## Context

v103 remains the strongest original Run-mode candidate, but it is not final-clean because it uses two public Kaggle datasets with unknown license metadata:

- `jaejohn/perch-meta`
- `tuckerarrants/bc2026-distilled-sed-public`

v104-v107 tested license-clean Perch-only replacements. v108-v109 added an original EcoProto signal built from competition train labels plus Perch embeddings, rather than only adapting public notebook behavior.

## Results

| candidate | dependency status | mechanism | runtime save | macro | micro | top1 | top5 | decision |
|---|---:|---|---:|---:|---:|---:|---:|---|
| v103 | `HOLD-license-audit` | guarded macro rescue with unknown-license SED/cache | ~239s | 0.98906455 | 0.92885549 | 0.38356164 | 0.71232877 | strongest evidence; not final-clean |
| v104 | `PASS-clean` | Perch-only guarded rescue | ~347s | 0.97751210 | 0.78763929 | 0.00000000 | 0.08219178 | reject submit |
| v105 | `PASS-clean` | timid rank restore | ~336s | 0.97751210 | 0.81765567 | 0.00000000 | 0.08219178 | reject submit |
| v106 | `PASS-clean` | rank-dominant restore | ~314s | 0.97753686 | 0.87641886 | 0.02739726 | 0.35616438 | hold |
| v107 | `PASS-clean` | rank-ceiling restore | ~317s | 0.97736356 | 0.91282668 | 0.27397260 | 0.50684932 | best clean top-k; hold |
| v108 | `PASS-clean` | original EcoProto rescue | ~334s | 0.97881000 | 0.82693410 | 0.00000000 | 0.08219178 | reject submit |
| v109 | `PASS-clean` | original EcoProto rank-launch | ~341s | 0.97963460 | 0.91325592 | 0.23287671 | 0.47945205 | strongest clean macro; hold |
| v110 | `PASS-clean` | original EcoProto clean blend | ~288s | 0.97911204 | 0.91481637 | 0.21917808 | 0.52054795 | best clean top-k; hold |

## Decision

`DO NOT REAL-SUBMIT v104-v110 YET`

Reasons:

- v108-v109 satisfy the user requirement to add original innovation, not just reference public work.
- v109 is the strongest license-clean macro candidate so far; v110 is the best clean top-k fallback, but both are still far behind v103.
- Current evidence does not justify spending a real submission slot against the `0.949` anchor.

## Next Action

Stop squeezing the clean Perch-only family for now. Continue searching for a license-clean SED-like source or build internal distillation from competition-only labels.
