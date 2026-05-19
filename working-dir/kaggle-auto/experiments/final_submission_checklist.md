# Final Submission Checklist

Updated: 2026-05-19 07:50 UTC

## Current State
- No final submission selection has been made.
- v88 scored `0.921` and is not final-selection eligible.
- v89 is not submit-eligible as-is.
- v120 has been submitted as ref `52802748` and is not final-selection eligible until its public score and post-submit stability are recorded.
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
| v120 | `PENDING-score` | ref `52802748`; clean macro proxy `0.98139925`; awaiting public score |

## Next Automatic Action
Wait for v120 public score, then update final/fallback status and decide whether another UTC `2026-05-19` slot is justified.
