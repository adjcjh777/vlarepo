# Final Submission Checklist: v103

Updated: 2026-05-19 03:38 UTC

- Candidate: `v103-guarded-macro-risk-rescue`
- Submit mode: Kaggle code submission from kernel version `1`
- CPU-only metadata: pass
- CPU-only code path: pass, ONNX Runtime CPU providers only
- Internet disabled: pass
- Runtime under 90 minutes: pass in Run-mode, about `239s` before save and about `251s` through nbconvert
- `submission.csv` exists: pass in Run-mode
- Row order: pass in dry-run; hidden row-order logic still requires real submission validation
- Class column order: pass
- No NaN/inf: pass
- Prediction range `[0, 1]`: pass
- Original innovation recorded: pass, v103 adds positive-rescue and top-hit guard logic over v102
- Attribution recorded: pass
- External provenance recorded: partial
- License status: hold, `jaejohn/perch-meta` and `tuckerarrants/bc2026-distilled-sed-public` have Kaggle metadata license `unknown`
- Public-LB-only tuning: not used
- Human-labeling/test-leakage risk: none found
- Pending-submission gate: clear, v101 ref `52795021` completed with public score `0.898`
- Decision: hold as strongest original Run-mode candidate, not final-clean yet
