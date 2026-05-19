# v93 Submission Decision Brief

Updated: 2026-05-19 01:19 UTC

## Candidate
- `v93-attributed-adkasd-strong-nobirdnet`
- Source reference: `adkasd/birdclef-2026-sub-v4-5-strong`
- Local candidate: `birdclef-2026/notebooks/v93-attributed-adkasd-strong-nobirdnet`
- Kaggle kernel: `junhaochengadjcjh7u7/bc26-v93-attributed-adkasd-strong-nobirdnet`
- Run-mode output: `birdclef-2026/outputs/v93-attributed-adkasd-strong-nobirdnet-v1`

## Evidence
- Kaggle Run-mode status: `ERROR`.
- The main prediction path wrote `submission.csv` and passed basic dry-run diagnostics.
- Final dry-run output shape `(3, 235)`, range `[0.47687027, 0.5553993]`, `221` rounded-6 unique values.
- The notebook failed later with missing `adkasd/birdclef-2026-priors-research`.
- Kaggle API access to `adkasd/birdclef-2026-priors-research` returned `403 Forbidden`.
- Dry-run overlap: v93 vs v87 correlation `1.000000`, MAD `0.000000`.

## Decision
- Reject v93 as a real-submission candidate.
- Rationale: it is not a complete Run-mode candidate and its partial final output adds no diversity over the current v87 anchor.
- Automatic next action: keep waiting for v91 score/error; search for a materially different candidate instead of repairing v93.

