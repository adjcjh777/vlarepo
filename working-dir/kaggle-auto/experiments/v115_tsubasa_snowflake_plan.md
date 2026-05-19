# v115 Tsubasa Snowflake SED Plan

Created: 2026-05-19 06:24 UTC

## Motivation

v114 proved that the v113 LantingGuo MelNorm sidecar can be made
self-contained, but its gain over v110 is microscopic and correlation with v110
is too high. A local positive-delta-only rescue probe also failed to beat the
uniform v114 blend. The next useful step is therefore a lower-correlation,
license-clean SED source instead of more tuning on the same branch.

## Source

- Dataset: `tsubasatech/birdclef-2026-snowflake-sed`
- Kaggle metadata license: `CC0-1.0`
- Files:
  - `sed_convnext-tiny_fold0.onnx`
  - `sed_tf-efficientnetv2-m_fold0.onnx`
- Local ONNX I/O audit:
  - input: `audio ['B', 160000] tensor(float)`
  - output: `logits ['B', 234] tensor(float)`

## Original Mechanism

v115 reuses the v112 clean SED remap/EcoProto scaffold but replaces the weak
backtracking SED model with a Tsubasa Snowflake two-model ONNX ensemble:

- run both Snowflake SED models on raw 5-second audio windows;
- average their logits before sigmoid conversion;
- learn a train-window output-column remap against competition train labels;
- apply per-class trust strength only when remapped columns beat same-index
  columns by AUC/correlation margins;
- feed the calibrated SED view into the existing EcoProto/rank-launch clean
  blend.

This is not a public output clone: the external asset is only the CC0 ONNX
source, while the calibration/remap/trust layer and final blend policy are
workspace-original.

## Compliance

- CPU-only metadata.
- Internet disabled.
- No `jaejohn/perch-meta`.
- No `tuckerarrants/bc2026-distilled-sed-public`.
- Uses public Perch ONNX (`CC0-1.0` recorded previously), Google Perch
  (`Apache 2.0` recorded previously), and Tsubasa Snowflake SED (`CC0-1.0`).
- Run-mode first; no real submission unless schema, runtime, proxy, correlation,
  and rules reports justify a daily slot.

## Gate

Reject if Run-mode fails, exceeds 90-minute CPU budget, outputs degenerate
predictions, regresses below the v110/v114 clean fallback level, or remains a
near-duplicate of v110/v114 without stronger proxy evidence.
