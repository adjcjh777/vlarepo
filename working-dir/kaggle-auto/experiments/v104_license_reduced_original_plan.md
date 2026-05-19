# v104 License-Reduced Original Plan

Created: 2026-05-19 03:43 UTC

## Trigger

v101 completed at public score `0.898` and is retired. v103 is the strongest original Run-mode candidate by local proxy, but it is `HOLD-for-real-submit` because two attached public Kaggle datasets have `unknown` license metadata:

- `jaejohn/perch-meta`
- `tuckerarrants/bc2026-distilled-sed-public`

## Objective

Build a v104/v105 original candidate that preserves the useful v103 idea while reducing prize-route compliance risk:

- keep CPU-only and no-internet inference;
- keep runtime under 90 minutes;
- keep v103's class-wise macro-risk and top-hit guard concept;
- remove or replace unknown-license runtime dependencies;
- run Kaggle Run-mode first;
- do not real-submit until schema, runtime, proxy, provenance, and compliance reports pass.

## Candidate Design

### v104A: Perch-Only Guarded Macro Rescue

Remove:

- `jaejohn/perch-meta` cached train features;
- `tuckerarrants/bc2026-distilled-sed-public` SED folds.

Keep:

- competition train/test soundscapes;
- `rishikeshjani/perch-onnx-for-birdclef-2026` (`CC0-1.0`);
- Google Perch model labels/assets (`Apache 2.0`);
- original v103 positive-rescue and top-hit guard logic.

Implementation idea:

- rebuild the small 59-file train soundscape Perch feature cache inside the notebook using Perch ONNX;
- use Perch-calibrated OOF plus embedding/spatial ridge probes as the only model views;
- replace SED-vs-Perch disagreement features with probe-vs-Perch disagreement features;
- keep rare/high-AUC conservative guards;
- reduce active rescue more than v103 unless the probe view gives strong positive evidence.

Expected tradeoff:

- lower macro proxy than v103 is likely because the SED view is removed;
- compliance is cleaner and may be preferable for final/prize-route robustness;
- runtime should remain far below 90 minutes because v103 Run-mode was about 251s with SED and cache, and rebuilding 59 train soundscapes with ONNX should still be within budget.

### v104B: Cache-Free But SED-Retained Probe

Remove only `jaejohn/perch-meta` and rebuild Perch train features in-notebook, but keep SED.

Decision: lower priority. It still has the `tuckerarrants/bc2026-distilled-sed-public` unknown-license blocker, so it does not solve final-clean compliance.

## Required Reports

- `experiments/v104_schema_report.csv`
- `experiments/v104_proxy_scores.csv`
- `experiments/rules_compliance_report_v104.md`
- `experiments/final_submission_checklist_v104.md`
- `experiments/v104_submission_decision_brief.md`

## Gate

Do not submit v104 unless:

- v104 Run-mode completes;
- output schema/range/order checks pass;
- proxy is not obviously worse than the original-like `0.925` historical floor;
- external data registry has no unresolved required dependency for the submitted notebook;
- candidate-specific compliance is `PASS-for-guarded-submit`;
- daily submission count remains below 5.
