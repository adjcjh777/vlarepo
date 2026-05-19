# Final Submission Checklist: v101

Updated: 2026-05-19 02:47 UTC

- Candidate: `v101-attributed-alexy-cnn-cpu`
- Submit mode: Kaggle code submission from kernel version `1`
- CPU-only metadata: pass
- CPU-only code path: pass, `DEVICE = "cpu"`
- Internet disabled: pass
- Runtime under 90 minutes: pending hidden-test measurement; Run-mode completed and public CPU dry-run evidence was 51.2 s for 16 files
- `submission.csv` exists: pass in Run-mode
- Sample row order: pass in Run-mode
- Hidden row order: guarded by assertion in final code
- Class column order: pass
- No NaN/inf: pass in Run-mode and guarded by assertion
- Prediction range `[0, 1]`: pass in Run-mode and guarded by assertion
- Train fallback removed: pass
- Attribution recorded: pass
- External provenance recorded: pass
- Public-LB-only tuning: not used for promotion; local dry-run proxy and source diversity motivate the guarded probe
- Human-labeling/test-leakage risk: none found
- Decision: allowed as a guarded real submission, not yet a final judging candidate
