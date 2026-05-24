# v380 After-v380 Push Gate Status

Updated: 2026-05-24 13:42:10 UTC

- Kernel: `junhaochengadjcjh7u7/bc26-v380-v379-static-distill`
- Decision: `PUSHED-v380-runmode`
- Reason: v380 Run-mode push accepted through Kaggle API; monitor with audit_v380_runmode
- Execute attempted: `True`
- Notebook dir: `birdclef-2026/notebooks/v380-v379-static-distill`

## Evidence

- v380_decision: `READY-v380-static-materializer-audit-NO-PUSH-NO-SUBMIT`
- v380_block_count: `0`
- v380_macro_gain: `0.0016012025357819981`
- v380_top5_anchor: `0.5068493150684932`
- v380_top5_local: `0.5068493150684932`
- notebook_dir: `birdclef-2026/notebooks/v380-v379-static-distill`
- missing: `[]`
- metadata_id: `junhaochengadjcjh7u7/bc26-v380-v379-static-distill`
- metadata_cpu: `True`
- metadata_no_tpu: `True`
- metadata_no_internet: `True`
- dataset_sources: `['rishikeshjani/perch-onnx-for-birdclef-2026']`
- model_sources: `['google/bird-vocalization-classifier/TensorFlow2/perch_v2_cpu/1']`
- live_pending_count: `0`
- utc_today_visible_kaggle_count: `2`
- live_error: ``

## Guard

- This script never makes a competition submission.
- v380 Run-mode push is schema/runtime proof only.
- A live pending competition submission blocks this push.
- After push, run `python3 scripts/audit_v380_runmode.py --fetch-if-complete --write`.

## Command Output

```
{"ref": "/code/junhaochengadjcjh7u7/bc26-v380-v379-static-distill", "url": "https://www.kaggle.com/code/junhaochengadjcjh7u7/bc26-v380-v379-static-distill", "versionNumber": 1, "error": "", "invalidTags": [], "invalidDatasetSources": [], "invalidCompetitionSources": [], "invalidKernelSources": [], "invalidModelSources": []}
```
