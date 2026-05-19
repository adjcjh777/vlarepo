# v119 Static Audit and Plan

Updated: 2026-05-19 07:18 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v119-roniheka-hgnet-sed/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v119-roniheka-hgnet-sed`
- Generator: `birdclef-2026/scripts/birdclef_prepare_v119_roniheka_hgnet_sed.py`

## Trigger

v103 has the strongest original proxy but is held for unknown-license runtime dependencies. v112 already tested `backtracking/birdclef2026-clean-sed-b0` and was too weak. Dataset audit found `roniheka/birdclef-2026-a90v2-distilled-hgnet-onnx` with Kaggle metadata license `CC0-1.0` and ONNX interface `spec [batch,1,256,time] -> logits [batch,234]`.

## Original Change

v119 keeps the clean v112/v114 framework but swaps the SED source:

- remove unknown-license `jaejohn/perch-meta` and `tuckerarrants/bc2026-distilled-sed-public` from runtime;
- keep CPU-only/no-internet inference;
- rebuild train Perch features in-notebook;
- use five CC0 Roniheka HGNet ONNX folds as the SED branch;
- preserve the workspace-original train-window remap, trust-strength calibration, and EcoProto/rank-launch clean blend.

## Originality Boundary

This candidate is deliberately not a blind port of another notebook. The public CC0 HGNet folds are treated only as one auditable acoustic evidence source. The workspace-owned contribution is the surrounding decision layer:

- replace the previously weak clean raw-audio SED branch with a stronger mel-Spec HGNet source while keeping the runtime license-clean;
- feed that source through the local train-window column remap rather than trusting the model's native class ordering blindly;
- calibrate branch trust with the existing train-window agreement signal before it enters the final blend;
- combine the SED signal with the local EcoProto/rank-launch path instead of copying a public ensemble recipe;
- require proxy, correlation, schema, and compliance gates before spending a real Kaggle submission slot.

## Static Checks

- Metadata private: pass.
- `enable_gpu=false`, `enable_tpu=false`, `enable_internet=false`: pass.
- `competition_sources=[birdclef-2026]`: pass.
- Runtime datasets:
  - `rishikeshjani/perch-onnx-for-birdclef-2026`: CC0-1.0.
  - `roniheka/birdclef-2026-a90v2-distilled-hgnet-onnx`: CC0-1.0.
- Model source: `google/bird-vocalization-classifier/TensorFlow2/perch_v2_cpu/1`: previously audited Apache 2.0.
- Kernel sources: empty.
- Code syntax: pass via local notebook AST parse excluding Kaggle magic cell.
- Runtime code does not mount prior local output CSVs.
- Unknown-license sources are mentioned only in provenance/attribution text as excluded dependencies, not used as runtime inputs.

## Gate

Run Kaggle Run-mode only. Do not real-submit unless v119 completes, output schema/range pass, proxy/correlation justify a submission slot, and candidate-specific compliance remains clean.
