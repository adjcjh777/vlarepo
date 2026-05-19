# Rules Compliance Report: v91

Updated: 2026-05-19 00:31 UTC

## Candidate
`v91-attributed-youssef-e1-rare-tail-nobirdnet`

## Result
Status: `PASS-for-guarded-submit`

## Checks
- Daily submissions: UTC `2026-05-19` visible count is `0/5` before submit.
- Final submissions: no final judging selection is changed by this action.
- CPU-only: pass; metadata has `enable_gpu=false`.
- Runtime: pass; Run-mode completed in about `508s`, below 90 minutes.
- Internet: pass; metadata has `enable_internet=false`.
- Output path: pass; Run-mode writes `submission.csv`.
- Format: pass; shape `(3, 235)` in dry-run sample mode.
- Row order: pass; matches local `sample_submission.csv`.
- Class order: pass; matches local `sample_submission.csv`.
- NaN/inf: pass; none found.
- Range: pass; probabilities are within `[0, 1]`.
- Artifact provenance: pass for candidate files and Kaggle output paths listed in `experiments/v91_submission_decision_brief.md`.
- External provenance: pass-with-notes; BirdNET CC BY-NC model was removed, Google Perch model is Apache 2.0, and remaining public Kaggle datasets are recorded in the registry with available metadata.
- Private sharing: pass; no team-external private artifact sharing.
- Human labeling/test leakage: pass; no manual test listening or hidden-test leakage.

## Decision
Allow guarded code submission for v91. Do not mark as final candidate until public score, stability, and final hardening are reviewed.

