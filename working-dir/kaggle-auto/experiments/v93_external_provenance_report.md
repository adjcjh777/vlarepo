# v93 External Provenance Report

Updated: 2026-05-19 01:19 UTC

## Source
- Public Kaggle notebook reference: `adkasd/birdclef-2026-sub-v4-5-strong`
- Local derivative: `birdclef-2026/notebooks/v93-attributed-adkasd-strong-nobirdnet`
- Source metadata snapshot: `experiments/provenance/v93/source_kernel_metadata.json`

## Local Changes
- Cleared executed notebook outputs before pushing to Kaggle.
- Removed an empty dataset source entry from metadata.
- Explicitly disabled BirdNET lookup and removed any BirdNET model source.
- Kept CPU-only and no-internet metadata.

## Dependencies
- `tuckerarrants/bc2026-distilled-sed-public`: public Kaggle dataset, license not confirmed locally.
- `tuckerarrants/birdclef-2026-waveform-cache`: public Kaggle dataset, license not confirmed locally.
- `jaejohn/perch-meta`: public Kaggle dataset, license not confirmed locally.
- `tuckerarrants/perch-v2-no-dft-onnx`: public Kaggle dataset, license not confirmed locally.
- `rishikeshjani/perch-onnx-for-birdclef-2026`: public Kaggle dataset, previously recorded as `CC0-1.0`.
- `hideyukizushi/sgkfk-202604041716`: public Kaggle dataset, license not confirmed locally.
- `ashok205/tf-wheels`: Kaggle kernel source, license not confirmed locally.
- `hideyukizushi/bird26-reprod-perch-proto-residualssm-train-s7177`: Kaggle kernel source, license not confirmed locally.
- `google/bird-vocalization-classifier/TensorFlow2/perch_v2_cpu/1`: public Kaggle model, previously recorded as Apache 2.0.
- `adkasd/birdclef-2026-priors-research`: required by a later prior cell but not accessible through the current Kaggle API session (`403 Forbidden`).

## Compliance Status
Status: `REJECT-for-real-submit`.

Reason: v93 cannot complete Run-mode without an inaccessible priors dataset, and its available partial final output is exactly identical to v87. It should not be used for real submission or final judging.

