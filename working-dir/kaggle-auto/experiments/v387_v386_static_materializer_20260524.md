# v387 v386 Static Materializer

            Updated: 2026-05-24 14:58:42 UTC

            Status: `READY-v387-v386-static-materializer-audit-NO-PUSH-NO-SUBMIT`.

            ## Research Question

            Can the v386 parameter-stressed v383 route be materialized as a static CPU-only notebook while preserving the dry-run tolerant real sample-row guard?

            ## Result

            - Destination notebook: `/Users/junhaocheng/working-dir/kaggle-auto/birdclef-2026/notebooks/v387-v386-static-distill`
            - Kernel id: `junhaochengadjcjh7u7/bc26-v387-v386-static-distill`
            - Patch marker: `CODEX_V387_V386_STATIC_DISTILL_PATCH`
            - Macro gain: `0.00291826`
            - Fold std delta retained: `-0.00083026`
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

            - `READY-v387-v386-static-materializer-audit-NO-PUSH-NO-SUBMIT`
            - Next: Build a guarded v387 Run-mode push/audit pair after v383 real-submit decision is resolved.
