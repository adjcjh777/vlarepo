# Attribution

This candidate continues the private original clean v110/v116/v120-v122 line.

Original v123 change:
- preserves the single-pass memory-reduced final-layer structure from v122;
- rank-calibrates the CC0 Tsubasa sidecar onto the clean Perch surrogate scale;
- applies the sidecar only to 10 pre-declared train-window-supported classes with rank margin 0.02;
- runs the expensive final layer once;
- does not mount prior output CSVs or unknown-license SED/cache dependencies;
- keeps CPU-only/no-internet metadata and writes rank-calibrated diagnostics.

Run-mode only until v123 runtime, schema, proxy, correlation, and compliance evidence pass.
