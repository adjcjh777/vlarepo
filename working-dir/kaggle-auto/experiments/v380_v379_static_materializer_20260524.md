# v380 v379 Static Materializer

            Updated: 2026-05-24 13:38:12 UTC

            Status: `READY-v380-static-materializer-audit-NO-PUSH-NO-SUBMIT`.

            ## Research Question

            Can the v379 deployable-distill candidate be materialized as a
            static, CPU-only, no-internet v107 notebook patch with fixed
            coefficients and no diagnostic teacher runtime dependency?

            ## Implementation Summary

            - Source notebook: `/Users/junhaocheng/working-dir/kaggle-auto/birdclef-2026/notebooks/v107-rankceiling-perch-guarded`
            - Destination notebook: `/Users/junhaocheng/working-dir/kaggle-auto/birdclef-2026/notebooks/v380-v379-static-distill`
            - Kernel id: `junhaochengadjcjh7u7/bc26-v380-v379-static-distill`
            - Patch marker: `CODEX_V380_V379_STATIC_DISTILL_PATCH`
            - Spec: `/Users/junhaocheng/working-dir/kaggle-auto/experiments/v380_v379_static_distill_spec.json`
            - Local materialized submission: `/Users/junhaocheng/working-dir/kaggle-auto/experiments/v380_v379_static_distill_local_submission.csv`
            - Runtime policy: `runtime uses only v107 submission, competition train_soundscapes_labels, sample row ids, and fixed coefficients`

            ## Local Metrics

            - Macro: `0.97736356` -> `0.97896476` (`+0.00160120`)
            - Top1: `0.27397260` -> `0.27397260`
            - Top5: `0.50684932` -> `0.50684932`
            - Fold std delta: `-0.00022659`
            - Weak follow-up gain: `+0.00503235`
            - Corr vs anchor: `0.99994875`

            ## Static Audit

            - `destination_exists`: `True`
- `notebook_exists`: `True`
- `metadata_exists`: `True`
- `attribution_exists`: `True`
- `marker_cell_once`: `True`
- `cpu_disabled_gpu`: `True`
- `cpu_disabled_tpu`: `True`
- `internet_disabled`: `True`
- `competition_source`: `True`
- `keeps_clean_dataset_sources`: `True`
- `keeps_clean_model_sources`: `True`
- `no_unknown_metadata_sources`: `True`
- `no_unknown_patch_runtime_sources`: `True`
- `writes_submission_csv`: `True`
- `writes_diagnostics`: `True`
- `row_order_guard`: `True`
- `range_guard`: `True`
- `spec_has_all_labels`: `True`
- `local_no_top5_regression`: `True`
- `local_fold_std_not_worse`: `True`

            ## Decision

            - `READY-v380-static-materializer-audit-NO-PUSH-NO-SUBMIT`
            - Next: Build a guarded Run-mode push/audit pair only if a fresh submit-window and risk review authorizes it.
