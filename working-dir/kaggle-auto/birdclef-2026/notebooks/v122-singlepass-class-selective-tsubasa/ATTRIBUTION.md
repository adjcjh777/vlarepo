# Attribution

This candidate continues the private original clean v110/v116/v120/v121 line.

Original v122 change:
- preserves v121's 10-class Tsubasa sidecar gate;
- moves the sidecar blend before the EcoProto/rank-launch final layer;
- runs the expensive final layer once instead of recomputing clean and sidecar finals;
- uses only CC0 Tsubasa and CC0 Perch ONNX dataset inputs plus the Google Perch model source;
- does not mount prior output CSVs or unknown-license SED/cache dependencies;
- keeps CPU-only/no-internet metadata and writes single-pass diagnostics.

Run-mode only until v122 runtime, schema, proxy, correlation, memory-risk, and compliance evidence pass.
