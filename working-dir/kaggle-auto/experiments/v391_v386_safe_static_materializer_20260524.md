# v391 v386 Safe Static Materializer

            Updated: 2026-05-24 15:15:19 UTC

            Status: `READY-v391-v386-safe-static-materializer-audit-NO-PUSH-NO-SUBMIT`.

            ## Research Question

            Can the safe-final v386 parameter set be materialized as a static CPU-only notebook while preserving the dry-run tolerant real sample-row guard?

            ## Result

            - Destination notebook: `/Users/junhaocheng/working-dir/kaggle-auto/birdclef-2026/notebooks/v391-v386-safe-static-distill`
            - Kernel id: `junhaochengadjcjh7u7/bc26-v391-v386-safe-static-distill`
            - Patch marker: `CODEX_V391_V386_SAFE_STATIC_DISTILL_PATCH`
            - Macro gain: `0.00282022`
            - Fold std delta retained: `-0.00188085`
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

            - `READY-v391-v386-safe-static-materializer-audit-NO-PUSH-NO-SUBMIT`
            - Next: Build a guarded v391 Run-mode push/audit pair only if a safe_final slot is needed after v387/v390.
