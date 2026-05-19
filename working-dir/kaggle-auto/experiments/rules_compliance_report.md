# Rules Compliance Report

Updated: 2026-05-19 08:29 UTC

## Authority
- Official Kaggle BirdCLEF+ 2026 rules and platform limits remain the primary authority.
- Local guardrail source: `RULES_COMPLIANCE_GUARDRAILS.md`.
- Goal source: `birdclef-2026/goal.md`.

## Global Status
- UTC `2026-05-19` visible submissions after v120: `3/5`.
- Current visible best remains v87 `0.949`.
- Live goal gate remains `GOAL_GATE=NOT_REACHED`.
- Top20/top5 cutoffs at latest check: `0.954` / `0.958`.

## Candidate Summary

| Candidate | Submission state | Compliance state | Decision |
|---|---:|---:|---|
| v88 attributed EOS Parity T3 | scored `0.921` | `REJECT-as-final` | Retire; below v87 `0.949`, below top20 `0.953`, and below original-like `0.925`. |
| v89 attributed Perch-CNN | Run-mode complete; not submitted | `HOLD-as-source` | Do not submit as-is; output is all-constant staging prior and OOF diagnostics are weak. |
| v120 clean Tsubasa sidecar | submitted; ref `52802748`; hidden RAM error | `REJECT-memory` | Retire; Run-mode passed but hidden-test evaluation exceeded Kaggle RAM. |
| v121 class-selective Tsubasa | Run-mode complete; not submitted | `HOLD-memory-risk` | Original sparse sidecar gate improves local proxy, but still uses v120's double-final-layer structure. Convert to single-pass before real submission. |

## Hard Guardrails
- Final inference must be CPU-only and under 90 minutes.
- Final notebook must write `/kaggle/working/submission.csv`.
- Final notebook must not depend on internet access.
- At most 5 real Kaggle submissions per UTC day.
- At most 2 final submissions for judging.
- No final promotion without artifact lineage, external provenance, runtime proof, schema proof, and candidate-specific compliance report.
- No public-LB-only blend or promotion decision.
- No hand labeling, hidden-test leakage, or private sharing outside the Kaggle team.

## Current Decision
Retire v120 as a submission/final candidate because hidden-test evaluation exceeded Kaggle RAM. Preserve v121 as a promising original Run-mode result, but do not submit it as-is. Continue only with memory-reduced, single-pass evidence before spending another real slot.
