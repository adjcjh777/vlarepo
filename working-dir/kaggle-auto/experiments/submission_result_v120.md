# v120 Submission Result

Updated: 2026-05-19 08:06 UTC

## Candidate

- Candidate: `v120-clean-tsubasa-sidecar`
- Kaggle ref: `52802748`
- Submitted at: `2026-05-19 07:49:31 UTC`
- Message: `Original clean v120: Perch-only clean anchor plus 0.15 CC0 Tsubasa ConvNeXt SED sidecar; CPU-only Run-mode COMPLETE ~683s; no unknown-license runtime inputs`

## Final Status

- Status: `SubmissionStatus.COMPLETE`
- Public score: blank
- Error: `Your notebook requested more memory (RAM) than is available.`
- UTC `2026-05-19` visible submissions after v120: `3/5`

## Pre-Submit Evidence

- Run-mode: `COMPLETE`
- Runtime: output saved at about `683.4s`
- Schema: `120 x 235`, sample columns matched, finite values, no duplicate row IDs
- Proxy: macro `0.98139925`, micro `0.91435250`, top5 `0.47945205`
- Compliance: `PASS-for-guarded-submit`

## Decision

`REJECT - hidden-test memory exceeded`

v120 remains useful as Run-mode/proxy evidence, but it is not a valid final or next-submit candidate because hidden-test evaluation exceeded Kaggle RAM. The likely failure mode is the double execution of the expensive final decision layer: first for the Tsubasa sidecar and then again for the clean anchor. Future follow-up must be single-pass or otherwise memory-reduced before any real submission.
