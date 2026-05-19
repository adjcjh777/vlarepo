# Rules Compliance Report: v101

Updated: 2026-05-19 02:47 UTC

## Candidate

`v101-attributed-alexy-cnn-cpu`

## Result

Status: `PASS-for-guarded-submit`

## Checks

- Daily submissions: UTC `2026-05-19` visible count is `1/5` before submit.
- Pending submissions: none visible before submit.
- Final submissions: no final judging selection is changed by this action.
- CPU-only: pass; metadata has `enable_gpu=false`, and code forces `DEVICE = "cpu"`.
- Runtime: pass for Run-mode environment startup and checkpoint loading; hidden-test inference runtime remains unknown until guarded code submission. Public Alexy dry-run evidence was 51.2 s for 16 train-fallback files on CPU.
- Internet: pass; metadata has `enable_internet=false`.
- Output path: pass; Run-mode writes `/kaggle/working/submission.csv`.
- Format: pass in Run-mode sample mode; output shape `(3, 235)`.
- Row order: pass in Run-mode sample mode; final code asserts hidden-row order against `sample_submission.csv` when hidden rows are mounted.
- Class order: pass; final code asserts columns match `sample_submission.csv`.
- NaN/inf: pass; Run-mode output is finite and final code asserts finite probabilities.
- Range: pass; Run-mode output is in `[0, 1]` and final code asserts probability range.
- Artifact provenance: pass; candidate is an attributed derivative of `alexycactus/birdclef-2026-cnn-infer-dataset`, recorded in `ATTRIBUTION.md` and `experiments/v100_sidecar_decision_brief.md`.
- External provenance: pass-with-notes; required checkpoint dataset is public Kaggle dataset `alexycactus/birdclef-2026-cnn-fold-checkpoints`, already recorded in `experiments/external_data_registry.csv`.
- Private sharing: pass; no team-external private artifact sharing.
- Human labeling/test leakage: pass; no manual test listening or hidden-test leakage.

## Decision

Allow a guarded code submission for v101 as UTC `2026-05-19` slot 2. Do not mark it as a final candidate until hidden-test status, public score, runtime, and stability are reviewed.
