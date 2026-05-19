# Attribution

This candidate continues the private original clean v110/v116/v120 line.

Original v121 change:
- uses the CC0 `tsubasatech/birdclef-2026-snowflake-sed` ConvNeXt ONNX fold as a class-selective sidecar;
- recomputes a Perch-only clean anchor in the same notebook;
- applies the sidecar only to 10 pre-declared train-window-supported classes and only when the sidecar exceeds the anchor by 0.02;
- does not mount prior output CSVs or unknown-license SED/cache dependencies;
- keeps CPU-only/no-internet metadata and writes class-selective branch diagnostics.

Run-mode only while v120 real submission is pending.
