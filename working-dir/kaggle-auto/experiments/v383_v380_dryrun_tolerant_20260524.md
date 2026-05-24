# v383 v380 Dry-run-tolerant Static Materializer

            Updated: 2026-05-24 13:52:30 UTC

            Status: `READY-v383-dryrun-tolerant-static-audit-NO-PUSH-NO-SUBMIT`.

            ## Research Question

            Can the v380 materializer be repaired so Kaggle Run-mode dry-run
            train-row fallback no longer crashes while preserving real
            sample-row guards and the clean v107 runtime policy?

            ## Result

            - Destination notebook: `/Users/junhaocheng/working-dir/kaggle-auto/birdclef-2026/notebooks/v383-v380-dryrun-tolerant`
            - Kernel id: `junhaochengadjcjh7u7/bc26-v383-v380-dryrun-tolerant`
            - Patch marker: `CODEX_V383_V380_DRYRUN_TOLERANT_PATCH`
            - Macro gain retained: `0.00160120`
            - Fold std delta retained: `-0.00022659`
            - Static block count: `0`

            ## Static Audit

            - `destination_exists`: `True`
- `notebook_exists`: `True`
- `metadata_exists`: `True`
- `attribution_exists`: `True`
- `marker_cell_once`: `True`
- `dryrun_tolerant_message`: `True`
- `real_sample_guard_present`: `True`
- `cpu_disabled_gpu`: `True`
- `cpu_disabled_tpu`: `True`
- `internet_disabled`: `True`
- `competition_source`: `True`
- `keeps_clean_dataset_sources`: `True`
- `keeps_clean_model_sources`: `True`
- `no_unknown_patch_runtime_sources`: `True`
- `local_macro_gate`: `True`
- `local_top5_not_worse`: `True`
- `local_fold_std_not_worse`: `True`

            ## Decision

            - `READY-v383-dryrun-tolerant-static-audit-NO-PUSH-NO-SUBMIT`
            - Next: Push v383 for Run-mode proof if live pending count is zero.
