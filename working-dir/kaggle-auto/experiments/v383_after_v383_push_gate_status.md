# v383 After-v383 Push Gate Status

Updated: 2026-05-24 13:52:50 UTC

- Kernel: `junhaochengadjcjh7u7/bc26-v383-v380-dryrun-tolerant`
- Decision: `PUSHED-v383-runmode`
- Reason: v383 Run-mode push accepted through Kaggle API; monitor with audit_v383_runmode
- Execute attempted: `True`
- Notebook dir: `birdclef-2026/notebooks/v383-v380-dryrun-tolerant`

## Evidence

- v383_decision: `READY-v383-dryrun-tolerant-static-audit-NO-PUSH-NO-SUBMIT`
- v383_block_count: `0`
- v383_macro_gain: `0.0016012025357819981`
- v383_top5_anchor: `0.5068493150684932`
- v383_top5_local: `0.5068493150684932`
- notebook_dir: `birdclef-2026/notebooks/v383-v380-dryrun-tolerant`
- missing: `[]`
- metadata_id: `junhaochengadjcjh7u7/bc26-v383-v380-dryrun-tolerant`
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
- v383 Run-mode push is schema/runtime proof only.
- A live pending competition submission blocks this push.
- After push, run `python3 scripts/audit_v383_runmode.py --fetch-if-complete --write`.

## Command Output

```
{"ref": "/code/junhaochengadjcjh7u7/bc26-v383-v380-dryrun-tolerant", "url": "https://www.kaggle.com/code/junhaochengadjcjh7u7/bc26-v383-v380-dryrun-tolerant", "versionNumber": 1, "error": "", "invalidTags": [], "invalidDatasetSources": [], "invalidCompetitionSources": [], "invalidKernelSources": [], "invalidModelSources": []}
```
