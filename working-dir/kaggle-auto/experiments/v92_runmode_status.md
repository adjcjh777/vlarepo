# v92 Run-mode Status

Updated: 2026-05-19 01:03 UTC

## Candidate
- Candidate: `v92-attributed-mtoshi-vis-nobirdnet`
- Source reference: `beicicc/bc26-mtoshi-vis-may18`
- Kaggle kernel: `junhaochengadjcjh7u7/bc26-v92-attributed-mtoshi-vis-nobirdnet`
- Local notebook: `birdclef-2026/notebooks/v92-attributed-mtoshi-vis-nobirdnet`
- Output path: `birdclef-2026/outputs/v92-attributed-mtoshi-vis-nobirdnet-v2`

## Result
- Kaggle Run-mode status: `COMPLETE`
- Runtime evidence: log completed around `520s`; final submission diagnostics passed at about `506s`.
- Mode: Run-mode evidence only. This was not submitted to the competition.
- CPU-only: `enable_gpu=false`, `enable_tpu=false`.
- Internet: `enable_internet=false`.
- BirdNET: explicitly disabled; `submission_birdnet.csv` is all zero.
- Final dry-run output: `submission.csv` shape `(3, 235)`.
- Intermediate outputs: `submission_protossm.csv`, `submission_sed.csv`, and `submission_birdnet.csv` shape `(240, 235)` in train-file dry-run mode.

## Log Evidence
- `v92 safety patch: removed non-inference flow diagram dependency.`
- `v92 safety patch: skipped original flow diagram display cell.`
- `BirdNET explicitly disabled for v92 license compatibility.`
- `BirdNET unavailable - zero submission saved`
- `Dry-run detected: Aligning rows with sample_submission.csv`
- `Ready for submission!`
- `submission.csv passed basic diagnostics.`

## Decision
Keep as local Run-mode evidence only. Do not submit v92 while v91 is pending, and do not use v92 as slot two unless a later decision explicitly accepts its near-duplicate risk versus v87.

