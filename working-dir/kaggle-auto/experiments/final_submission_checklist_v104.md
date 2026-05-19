# Final Submission Checklist: v104

Updated: 2026-05-19 03:58 UTC

- Candidate: `v104-perch-only-guarded-rescue`
- Submit mode: Kaggle code submission from kernel version `1`
- CPU-only metadata: pass
- CPU-only code path: pass, ONNX Runtime CPU providers only
- Internet disabled: pass
- Runtime under 90 minutes: pass, about `347s` before save and about `358s` through nbconvert
- `submission.csv` exists: pass
- Row order: pass in dry-run
- Class column order: pass
- No NaN/inf: pass
- Prediction range `[0, 1]`: pass
- Unknown-license runtime dependencies removed: pass
- Attribution recorded: pass
- External provenance recorded: pass
- Public-LB-only tuning: not used
- Human-labeling/test-leakage risk: none found
- Pending-submission gate: clear
- Quality gate: fail; proxy top1/top5 and micro are too weak
- Decision: not submit, not final candidate
