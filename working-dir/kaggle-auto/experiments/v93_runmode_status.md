# v93 Run-mode Status

Updated: 2026-05-19 01:19 UTC

## Candidate
- Candidate: `v93-attributed-adkasd-strong-nobirdnet`
- Source reference: `adkasd/birdclef-2026-sub-v4-5-strong`
- Kaggle kernel: `junhaochengadjcjh7u7/bc26-v93-attributed-adkasd-strong-nobirdnet`
- Kaggle version: `1`
- Local notebook: `birdclef-2026/notebooks/v93-attributed-adkasd-strong-nobirdnet`
- Output path: `birdclef-2026/outputs/v93-attributed-adkasd-strong-nobirdnet-v1`

## Result
- Kaggle Run-mode status: `ERROR`
- Real competition submission: none
- CPU-only: `enable_gpu=false`, `enable_tpu=false`.
- Internet: `enable_internet=false`.
- BirdNET: explicitly disabled in the local derivative and no BirdNET model source is attached.

## Error
The notebook wrote `submission.csv`, but later failed in an optional prior/postprocess cell:

`AssertionError: Attach adkasd/birdclef-2026-priors-research (version >=2 with labeled priors)`

The missing dataset `adkasd/birdclef-2026-priors-research` returned `403 Forbidden` through the Kaggle API, so this candidate cannot be completed with available public/local inputs.

## Partial Output Evidence
- `submission.csv`: shape `(3, 235)`, valid dry-run sample rows/columns, finite probabilities.
- `subm_karnakbayev_power_optimization.csv`: shape `(3, 235)`, same values as `submission.csv`.
- `submission_protossm.csv`: shape `(240, 235)`.
- `submission_sed.csv`: shape `(240, 235)`.

## Decision
Reject v93 as a real-submission candidate. It is both incomplete under Run-mode and identical to the v87 dry-run final output, so it should not consume slot two after v91 resolves.

