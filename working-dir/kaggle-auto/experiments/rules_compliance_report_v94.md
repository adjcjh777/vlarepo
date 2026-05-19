# Rules Compliance Report - v94

Candidate: `v94-attributed-karnak-advance-ensemble`

Status: `REJECTED`

## Checks

| Check | Result | Notes |
| --- | --- | --- |
| CPU-only metadata | PASS | `enable_gpu=false`, `enable_tpu=false`. |
| Internet disabled | PASS | `enable_internet=false`. |
| Competition source | PASS | `birdclef-2026` present. |
| BirdNET usage | PASS after patch | BirdNET lookup was explicitly disabled; BirdNET model sources are removed if present. |
| Runtime <= 90 minutes | PASS | Failure occurred around 488.8 seconds, well under 90 minutes. |
| Run-mode complete | FAIL | Kaggle status `ERROR`. |
| Final schema | FAIL | Final notebook did not complete; sample-only `submission.csv` is not valid evidence for submission. |
| Daily quota | PASS | No competition submission was made for v94. |
| Attribution | PASS | `ATTRIBUTION.md` added in the candidate notebook directory. |

## Compliance Decision

v94 must not be submitted. The rules-compatible parts of the candidate are preserved for audit, but the failed Run-mode finalization prevents any competition slot use.
