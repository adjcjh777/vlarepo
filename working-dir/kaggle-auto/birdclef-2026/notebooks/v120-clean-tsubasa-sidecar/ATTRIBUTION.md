# Attribution

This candidate continues the private original clean v110/v116 line.

Original v120 change:
- uses the CC0 `tsubasatech/birdclef-2026-snowflake-sed` ConvNeXt ONNX fold as a low-correlation sidecar;
- recomputes a Perch-only clean anchor in the same notebook;
- emits a constrained `0.85 clean_anchor + 0.15 Tsubasa_sidecar` probability blend;
- does not mount prior output CSVs or unknown-license SED/cache dependencies;
- keeps CPU-only/no-internet metadata and writes branch summary diagnostics.

Run-mode only until v120 runtime, schema, proxy, correlation, and compliance evidence pass.
