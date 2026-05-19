# Final Submission Checklist

Updated: 2026-05-19 09:21 UTC

## Current State
- No final submission selection has been made.
- v88 scored `0.921` and is not final-selection eligible.
- v89 is not submit-eligible as-is.
- v120 was submitted as ref `52802748` and is not final-selection eligible because hidden-test evaluation exceeded Kaggle RAM.
- v121 completed Run-mode with strong local proxy, but is not submit/final-selection eligible as-is because it inherits v120's double-final-layer memory risk.
- v122 completed Run-mode with a single-pass memory-safe structure, but macro proxy is below clean baselines.
- v123 completed Run-mode with rank-calibrated single-pass sidecar, but the proxy gain is too small and output is near-duplicate of v110/v114.
- Current best visible fallback is v87 `0.949`, but final promotion still requires private-LB robustness reasoning and complete provenance/compliance evidence.

## Required Before Any Final Judging Selection
- [ ] Candidate has scored or otherwise has authoritative Kaggle submission result.
- [ ] Candidate-specific rules compliance report is `PASS`.
- [ ] Daily submission ledger is complete.
- [ ] Final submission count remains at most `2`.
- [ ] CPU-only final inference proof exists.
- [ ] Runtime evidence is below 90 minutes with safety margin.
- [ ] Notebook writes `/kaggle/working/submission.csv`.
- [ ] No-internet execution proof exists.
- [ ] All external datasets/models/kernels/wheels have public accessibility, minimal-cost access, license compatibility, and recorded provenance.
- [ ] Prediction schema is validated against sample submission class order and row order where applicable.
- [ ] No NaN/inf and prediction range is valid.
- [ ] No hidden-test leakage, hand labeling, or private sharing risk.
- [ ] Decision brief explains why this candidate is robust for private leaderboard, not only public leaderboard.

## Current Candidate Gate

| Candidate | Final checklist state | Blocking reason |
|---|---:|---|
| v88 | `REJECT-as-final` | scored `0.921`, below v87 `0.949`, top20 `0.953`, and original-like `0.925` |
| v89 | `REJECT-as-submit` | all-constant staging prior output; weak OOF diagnostics |
| v120 | `REJECT-memory` | ref `52802748`; hidden-test error: requested more RAM than available |
| v121 | `HOLD-memory-risk` | Run-mode proxy strong, but double-final-layer structure is not safe after v120 hidden RAM failure |
| v122 | `REJECT-quality` | single-pass memory fix works, but macro proxy `0.97709863` is below clean baselines |
| v123 | `HOLD-too-small-gain` | rank-calibrated single-pass works, but macro gain over v114 is only about `+0.000010` |

## Next Automatic Action
Do not submit the current Tsubasa sidecar variants. The next real candidate needs a larger proxy improvement or materially different low-correlation evidence while preserving single-pass memory safety.
