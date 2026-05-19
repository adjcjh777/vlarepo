# Attribution

This candidate continues the private original and clean v112/v114 line.

Original v119 change:
- uses the CC0 `roniheka/birdclef-2026-a90v2-distilled-hgnet-onnx` five-fold ONNX dataset;
- replaces the weaker `backtracking/birdclef2026-clean-sed-b0` raw-audio branch;
- keeps the workspace-original train-window remap and trust-strength calibration;
- rebuilds train Perch features inside the Kaggle notebook;
- avoids `jaejohn/perch-meta` and `tuckerarrants/bc2026-distilled-sed-public`;
- keeps CPU-only/no-internet metadata and emits class-level remap diagnostics.

Run-mode only until v119 runtime, schema, proxy, correlation, and compliance evidence pass.
