# v94 Run-mode Status

Candidate: `v94-attributed-karnak-advance-ensemble`

Kernel: `junhaochengadjcjh7u7/bc26-v94-attributed-karnak-advance-ensemble`

Source reference: `karnakbaevarthur/birdclef-advance-ensemble`

Run status: `ERROR`

Artifacts copied to:

`birdclef-2026/outputs/v94-attributed-karnak-advance-ensemble-v1/`

## What Worked

- Kaggle metadata accepted the private CPU/no-internet derivative.
- Public dependencies mounted and main Model_2/Model_5 branches executed far enough to create CSV artifacts.
- BirdNET was explicitly disabled for license compatibility.
- Runtime before failure was about 488.8 seconds in the Kaggle log, below the 90-minute CPU ceiling.

## Failure

The notebook failed during final direct ensemble:

`AssertionError: row_id mismatch in subm_5.csv: missing=240, extra=3`

The cause is a Run-mode dry-run mismatch:

- `subm_2.csv` was generated from a dry-run on 20 train soundscapes, giving 240 rows.
- `subm_5.csv` and `submission.csv` were aligned to the 3-row `sample_submission.csv`.
- The final direct blend tried to ensemble the 240-row and 3-row files and correctly stopped on row_id mismatch.

## Output Summary

Detailed schema metrics are in `experiments/v94_schema_report.csv`.

Key observations:

- `submission.csv`: 3 rows x 235 columns, valid finite probabilities, but only sample rows.
- `subm_2.csv`: 240 rows x 235 columns, valid finite probabilities, but train dry-run rows.
- `submission_protossm.csv` and `submission_sed.csv`: valid 240-row dry-run intermediate outputs.

## Decision

Do not competition-submit v94. It did not produce a complete Run-mode final notebook and does not provide material output evidence against the v87 anchor.
