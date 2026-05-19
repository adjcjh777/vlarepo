# Final Submission Checklist: v120

Updated: 2026-05-19 08:06 UTC

## Candidate

`v120-clean-tsubasa-sidecar`

## Pre-Submission Checklist

- [x] Candidate has Kaggle Run-mode result.
- [x] Candidate-specific rules compliance report is `PASS-for-guarded-submit`.
- [x] CPU-only final inference proof exists.
- [x] Runtime evidence is below 90 minutes with safety margin.
- [x] Notebook writes `submission.csv`.
- [x] No-internet execution proof exists.
- [x] External datasets/models have provenance and compatible licenses.
- [x] Prediction schema is validated against sample submission class order.
- [x] No NaN/inf and prediction range is valid.
- [x] No hidden-test leakage, hand labeling, or private sharing risk.
- [x] Daily submission count before submit is `2/5`, so slot 3 is allowed.
- [x] Candidate has authoritative Kaggle result. Ref `52802748` completed with hidden-test RAM error and no public score.
- [ ] Candidate is selected as final judging submission. Blocked by memory error.

## Decision

Rejected as final candidate. Hidden-test evaluation exceeded Kaggle RAM.
