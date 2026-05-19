# Attribution

This candidate continues the private original clean v110/v116/v120-v123 line.

Original v124 change:
- runs the clean EcoProto/rank-launch final layer once;
- keeps a lightweight rank-calibrated CC0 Tsubasa sidecar for post-final correction;
- applies the sidecar only to 10 pre-declared train-window-supported classes with rank margin 0.02;
- avoids the v120/v121 double-final memory pattern;
- does not mount prior output CSVs or unknown-license SED/cache dependencies;
- keeps CPU-only/no-internet metadata and writes post-final diagnostics.

Run-mode only until v124 runtime, schema, proxy, correlation, and compliance evidence pass.
