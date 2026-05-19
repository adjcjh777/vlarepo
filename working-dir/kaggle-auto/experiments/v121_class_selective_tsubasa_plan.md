# v121 Class-Selective Tsubasa Plan

Created: 2026-05-19 08:03 UTC
Updated: 2026-05-19 08:29 UTC

## Trigger

v120 was still pending when this plan was created. While waiting, a local class-selective probe found that the Tsubasa sidecar can improve both macro proxy and top5 proxy if it is applied only to a small supported class set and only when the sidecar score is clearly above the clean anchor.

Post-update: v120 later completed with hidden-test RAM exceeded. This plan remains useful as an originality/quality probe, but v121 is no longer a direct real-submission plan because it still uses the same double-final-layer memory pattern.

## Candidate

- Notebook: `birdclef-2026/notebooks/v121-class-selective-tsubasa/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v121-class-selective-tsubasa`
- Generator: `birdclef-2026/scripts/birdclef_prepare_v121_class_selective_tsubasa.py`

## Original Mechanism

v121 is a self-contained clean notebook. It computes:

- `clean_anchor`: the Perch-only clean EcoProto/rank-launch anchor.
- `tsubasa_sidecar`: the CC0 Tsubasa ConvNeXt SED sidecar.

Then it applies the sidecar only when all gates pass:

- class is in the pre-declared train-window-supported class list;
- `tsubasa_sidecar > clean_anchor + 0.02`;
- sidecar mix is exactly `0.40` on gated cells and `0.00` elsewhere.

Selected classes:

`47158son13`, `47158son15`, `47158son16`, `47158son21`, `47158son22`, `47158son23`, `516975`, `chacha1`, `grekis`, `plcjay1`.

## Local Probe Evidence

The local probe wrote `experiments/v121_class_selective_sidecar_probe.csv`.

Best relevant row:

- `v114_v116_cls_margin-0.02_w0.4_side_gt_anchor`: macro `0.982755`, micro `0.925888`, top1 `0.246575`, top5 `0.534247`.

Baselines:

- v120 global sidecar: macro `0.981399`, top5 `0.479452`.
- v114 clean baseline: macro `0.979201`, top5 `0.520548`.
- v110 clean baseline: macro `0.979112`, top5 `0.520548`.

Interpretation: v121 is a better clean-sidecar design than v120 on the local dry-run proxy because it improves macro while preserving or improving top5.

## Gate

Kaggle Run-mode completed, and v121 has runtime/schema/proxy/correlation/compliance evidence. Do not real-submit v121 as-is because it still uses the double-final-layer structure implicated by the v120 hidden-test RAM error. Convert the idea into a single-pass memory-reduced follow-up first.
