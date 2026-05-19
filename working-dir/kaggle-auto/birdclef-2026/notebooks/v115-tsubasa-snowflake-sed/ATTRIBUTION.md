# Attribution

This candidate continues the private original v86/v102/v103 and clean v110-v114 line.

Original v115 change:
- uses the CC0 `tsubasatech/birdclef-2026-snowflake-sed` ONNX dataset;
- ensembles `sed_convnext-tiny_fold0.onnx` and `sed_tf-efficientnetv2-m_fold0.onnx` inside the notebook;
- keeps the workspace-original train-window column remap and trust-strength calibration from v112;
- rebuilds train Perch features inside the Kaggle notebook instead of using `jaejohn/perch-meta`;
- avoids `tuckerarrants/bc2026-distilled-sed-public`;
- keeps CPU-only/no-internet metadata and emits class-level remap diagnostics.

Run-mode only until v115 runtime, schema, proxy, correlation, and compliance evidence pass.
