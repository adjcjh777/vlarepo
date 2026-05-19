# v104-v107 Perch-Only License-Clean Ablation Summary

Updated: 2026-05-19 04:23 UTC

## Context

v103 is the strongest original Run-mode candidate but is not final-clean because it uses two public Kaggle datasets with `unknown` license metadata:

- `jaejohn/perch-meta`
- `tuckerarrants/bc2026-distilled-sed-public`

v104-v107 tested whether a license-clean Perch-only branch can replace that signal while keeping CPU-only/no-internet/under-90-minute constraints.

## Results

| candidate | dependency status | runtime save | macro | micro | top1 | top5 | decision |
|---|---:|---:|---:|---:|---:|---:|---|
| v103 | `HOLD-license-audit` | ~239s | 0.98906455 | 0.92885549 | 0.38356164 | 0.71232877 | strongest original evidence; not final-clean |
| v104 | `PASS-clean` | ~347s | 0.97751210 | 0.78763929 | 0.00000000 | 0.08219178 | reject submit |
| v105 | `PASS-clean` | ~336s | 0.97751210 | 0.81765567 | 0.00000000 | 0.08219178 | reject submit |
| v106 | `PASS-clean` | ~314s | 0.97753686 | 0.87641886 | 0.02739726 | 0.35616438 | hold, not submit |
| v107 | `PASS-clean` | ~317s | 0.97736356 | 0.91282668 | 0.27397260 | 0.50684932 | best clean branch, still below v103 |

## Decision

`DO NOT REAL-SUBMIT v104-v107 YET`

Reasons:

- v107 proves Perch/probe rank restoration can recover some row-ranking signal, but its macro proxy remains about `0.0117` below v103.
- v107 top5 is still materially below v103 (`0.5068` vs `0.7123`).
- Historical original-like Perch branches scored around `0.925`; without a stronger new signal, a real submission slot is unlikely to challenge the `0.949` anchor.

## Next Action

Search for or create a license-clean SED-like signal source:

- first, audit Kaggle-accessible datasets/models for explicit permissive licenses;
- second, if no clean SED assets exist, consider internal distillation from competition labels only;
- third, keep v107 as a fallback clean candidate but do not submit until a stronger reason exists.
