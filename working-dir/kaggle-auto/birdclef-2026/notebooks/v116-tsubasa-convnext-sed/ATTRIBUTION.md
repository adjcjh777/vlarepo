# Attribution

This candidate continues the private original v86/v102/v103 and clean v110-v115 line.

Original v116 change:
- keeps the CC0 `tsubasatech/birdclef-2026-snowflake-sed` source;
- uses only `sed_convnext-tiny_fold0.onnx` after v115's two-model ensemble exceeded Kaggle memory;
- preserves the workspace-original train-window remap and trust-strength calibration;
- rebuilds train Perch features inside the notebook and avoids unknown-license Perch/SED caches;
- keeps CPU-only/no-internet metadata.

Run-mode only until v116 runtime, schema, proxy, correlation, and compliance evidence pass.
