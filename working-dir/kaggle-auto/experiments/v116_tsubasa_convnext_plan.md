# v116 Tsubasa ConvNeXt SED Plan

Created: 2026-05-19 06:33 UTC

## Trigger

v115 failed Kaggle Run-mode with an out-of-memory error after loading both
Tsubasa Snowflake SED ONNX models and rebuilding Perch train features.

## Change

v116 keeps the same clean-source and original-calibration idea, but loads only:

- `sed_convnext-tiny_fold0.onnx`

It drops:

- `sed_tf-efficientnetv2-m_fold0.onnx`

## Original Mechanism

The core v115/v116 innovation remains:

- rebuild train Perch features in the Kaggle notebook;
- run a CC0 raw-audio SED model over train/test windows;
- infer a train-window output-column remap;
- apply per-class trust strength only when the remap beats same-index behavior
  by AUC/correlation margins;
- feed the calibrated SED view into the EcoProto/rank-launch clean blend.

## Gate

v116 must pass Kaggle Run-mode, schema, proxy, correlation, and compliance
checks before any real submission can be considered.
