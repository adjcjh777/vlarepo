# v119 Run-Mode Status

Updated: 2026-05-19 07:24 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v119-roniheka-hgnet-sed/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v119-roniheka-hgnet-sed`
- Output directory: `birdclef-2026/outputs/v119-roniheka-hgnet-sed-v1`

## Status

Kaggle Run-mode status: `COMPLETE`.

Downloaded artifacts:

- `submission.csv`
- `v119_roniheka_hgnet_sed_remap_diagnostics.csv`
- `bc26-v119-roniheka-hgnet-sed.log`

## Runtime Notes

- Notebook completed and saved output at about `400.8s`.
- CPU-only ONNX Runtime execution succeeded.
- Five Roniheka HGNet ONNX folds loaded with interface `spec [batch,1,256,time] -> logits [batch,234]`.
- Train Perch features were rebuilt inside the notebook: `meta=(708,2)`, `scores=(708,234)`, `emb=(708,1536)`.
- Roniheka HGNet train logits were rebuilt inside the notebook: `meta=(708,2)`, `logits=(708,234)`.
- Dry-run used train soundscapes because hidden test files are unavailable in Run-mode.

## Key Diagnostics

- Perch raw OOF AUC: `0.6812`.
- Perch calibrated OOF AUC: `0.8020`.
- Roniheka HGNet SED train AUC reference: mean `0.8870`, active classes `71`.
- Accepted remaps: `28/234`.
- SED weights: `sedfirst=0.578`, `adaptive=0.575`, `safety=0.480`.
- Output range after clean blend: `[0.013670, 0.999859]`.

## Decision

Run-mode passed technically, but proxy quality is weak. Do not real-submit v119.
