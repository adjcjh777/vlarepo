# v113 Static Audit

Updated: 2026-05-19 05:38 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v113-lantingguo-melnorm-ecoproto/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v113-lanting-melnorm`
- Mechanism: CC0 LantingGuo 128-mel SED MelNormProbe plus EcoProto clean blend.

## Source Audit

- Kaggle dataset: `lantingguo/birdclef2026-own-sed-b0-v5-onnx`
- Kaggle metadata license: `CC0-1.0`
- Files: `sed_b0.onnx`, 17,682,409 bytes.
- ONNX Runtime I/O:
  - input: `mel ['batch', 1, 128, 'time'] tensor(float)`
  - output: `logits ['batch', 234] tensor(float)`

## Metadata

- `enable_gpu`: `false`
- `enable_tpu`: `false`
- `enable_internet`: `false`
- `competition_sources`: `birdclef-2026`
- `dataset_sources`:
  - `rishikeshjani/perch-onnx-for-birdclef-2026`
  - `lantingguo/birdclef2026-own-sed-b0-v5-onnx`
- `model_sources`: `google/bird-vocalization-classifier/TensorFlow2/perch_v2_cpu/1`
- `kernel_sources`: empty

## Dependency Check

Runtime metadata does not include:

- `jaejohn/perch-meta`
- `tuckerarrants/bc2026-distilled-sed-public`
- `backtracking/birdclef2026-clean-sed-b0`

Those names appear only in provenance or historical comments if present. They are not mounted as runtime inputs.

## Decision

`PASS static audit`

Proceed with Kaggle Run-mode execution and local schema/proxy checks after output is available.
