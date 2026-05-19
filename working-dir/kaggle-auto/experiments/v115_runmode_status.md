# v115 Run-Mode Status

Updated: 2026-05-19 06:32 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v115-tsubasa-snowflake-sed/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v115-tsubasa-snowflake-sed`
- Source: `tsubasatech/birdclef-2026-snowflake-sed` (`CC0-1.0`)

## Result

- Kaggle Run-mode status: `ERROR`
- Failure message: `Your notebook tried to allocate more memory than is available.`
- Log archive: `birdclef-2026/outputs/v115-tsubasa-snowflake-sed-v1/bc26-v115-tsubasa-snowflake-sed.log`

## Evidence

The log shows both Snowflake SED ONNX sessions loaded:

- `sed_convnext-tiny_fold0.onnx`
- `sed_tf-efficientnetv2-m_fold0.onnx`

The notebook then rebuilt Perch train features successfully:

- `meta=(708, 2)`
- `scores=(708, 234)`
- `emb=(708, 1536)`

The kernel died before completing the Snowflake SED train rebuild. This points
to memory pressure from keeping Perch plus both SED ONNX models resident.

## Decision

`REJECT - runtime memory`

Do not submit v115. Continue as v116 with only the lighter ConvNeXt-tiny SED
model while preserving the original remap/trust/EcoProto calibration layer.
