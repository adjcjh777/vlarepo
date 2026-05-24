# v391 After-v391 Push Gate Status

Updated: 2026-05-24 15:15:56 UTC

- Kernel: `junhaochengadjcjh7u7/bc26-v391-v386-safe-static-distill`
- Decision: `PUSHED-v391-runmode`
- Reason: v391 Run-mode push accepted through Kaggle API; monitor with audit_v391_runmode
- Execute attempted: `True`
- Notebook dir: `birdclef-2026/notebooks/v391-v386-safe-static-distill`

## Evidence

- v391_decision: `READY-v391-v386-safe-static-materializer-audit-NO-PUSH-NO-SUBMIT`
- v391_block_count: `0`
- v391_macro_gain: `0.0028202241683551454`
- v391_top5_anchor: `0.5068493150684932`
- v391_top5_local: `0.5068493150684932`
- notebook_dir: `birdclef-2026/notebooks/v391-v386-safe-static-distill`
- missing: `[]`
- metadata_id: `junhaochengadjcjh7u7/bc26-v391-v386-safe-static-distill`
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
- v391 Run-mode push is schema/runtime proof only.
- A live pending competition submission blocks this push.
- After push, run `python3 scripts/audit_v391_runmode.py --fetch-if-complete --write`.

## Command Output

```
{"ref": "/code/junhaochengadjcjh7u7/bc26-v391-v386-safe-static-distill", "url": "https://www.kaggle.com/code/junhaochengadjcjh7u7/bc26-v391-v386-safe-static-distill", "versionNumber": 1, "error": "", "invalidTags": [], "invalidDatasetSources": [], "invalidCompetitionSources": [], "invalidKernelSources": [], "invalidModelSources": []}
```
