# v101 Run-Mode Status

Updated: 2026-05-19 02:47 UTC

## Candidate

- Local path: `birdclef-2026/notebooks/v101-attributed-alexy-cnn-cpu`
- Kaggle kernel: `junhaochengadjcjh7u7/bc26-v101-attributed-alexy-cnn-cpu`
- Source reference: `alexycactus/birdclef-2026-cnn-infer-dataset`
- Version: `1`

## Status

- Kaggle Run-mode status: `COMPLETE`
- Output archive: `birdclef-2026/outputs/v101-attributed-alexy-cnn-cpu-v1`
- Run-mode output is sample-shaped because hidden test is unavailable in ordinary Kaggle Run mode.

## Log Evidence

- `torch=2.10.0+cpu`
- `device=cpu  GPU=forced-off`
- Loaded checkpoints:
  - `fold1_best.pth`
  - `fold2_best.pth`
  - `fold3_best.pth`
- Ensemble size: `3` folds, fp32.
- Run-mode branch: `test_soundscapes empty -- staging sample-submission prior output`

## Diagnostics

`diagnostics_v101_staging_no_test.json`:

- `notebook`: `v101_alexy_cnn_cpu`
- `mode`: `staging_no_test`
- `rows`: `3`
- `classes`: `234`
- `device`: `cpu`
- `reason`: hidden test unavailable in Kaggle Run mode

## Interpretation

Run-mode proves environment compatibility, dependency mounting, CPU execution, and safe no-test behavior. It does not prove hidden-test runtime or hidden-test score. A guarded code submission is required for the real hidden-test execution evidence.
