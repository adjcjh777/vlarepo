# Rules Compliance Report: v93

Updated: 2026-05-19 01:19 UTC

## Candidate
`v93-attributed-adkasd-strong-nobirdnet`

## Result
Status: `REJECT-for-real-submit`

## Checks
- Daily submissions: no real submission was made for v93; UTC `2026-05-19` remains `1/5` used because only v91 was submitted.
- Pending submission guard: pass; v91 is still pending, so v93 was only run as Kaggle Run-mode evidence.
- CPU-only: pass; metadata has `enable_gpu=false`.
- Internet: pass; metadata has `enable_internet=false`.
- Runtime: incomplete; Run-mode errored after about `392s`.
- Output path: partial pass; `submission.csv` was written before the error.
- Format: partial pass; dry-run `submission.csv` shape `(3, 235)` with valid row/class order and finite probabilities.
- BirdNET: pass; explicitly disabled and no BirdNET model source attached.
- External provenance: fail/hold; later prior cell requires `adkasd/birdclef-2026-priors-research`, which is not accessible through the current Kaggle API session.
- Duplicate-risk gate: fail; v93 dry-run final is exactly identical to v87 (`corr=1.000000`, MAD `0.000000`).

## Decision
Do not submit v93. Do not spend more Run-mode attempts on this candidate unless the inaccessible priors dataset becomes available and a new diversity hypothesis is documented first.

