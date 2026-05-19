# v122 Single-Pass Class-Selective Tsubasa Plan

Created: 2026-05-19 08:55 UTC

## Trigger

v120 was rejected after real submission because hidden-test evaluation exceeded Kaggle RAM. v121 then showed that a sparse class-selective Tsubasa sidecar can improve the local dry-run proxy, but v121 still recomputes the expensive final decision layer twice. v122 is the memory-reduced continuation required before any additional real submission.

## Candidate

- Notebook: `birdclef-2026/notebooks/v122-singlepass-class-selective-tsubasa/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v122-singlepass-cls-tsubasa`
- Generator: `birdclef-2026/scripts/birdclef_prepare_v122_singlepass_class_selective_tsubasa.py`

## Original Mechanism

v122 starts from the license-clean v116 Tsubasa ConvNeXt SED branch and injects v121's sparse sidecar logic before the final EcoProto/rank-launch layer:

- compute the Tsubasa remapped SED probability view once;
- compute the Perch-clean surrogate SED probability view once from `scores_test`;
- apply the v121 class gate to 10 pre-declared train-window-supported classes;
- apply sidecar mix `0.40` only where `tsubasa_sed > clean_sed + 0.02`;
- keep the Perch-clean surrogate everywhere else;
- run the existing expensive final decision layer once.

Selected classes:

`47158son13`, `47158son15`, `47158son16`, `47158son21`, `47158son22`, `47158son23`, `516975`, `chacha1`, `grekis`, `plcjay1`.

## Expected Improvement

v121's local proxy showed that sparse class-selective sidecar intervention is better than the global v120 blend:

- v121 proxy: macro `0.98275473`, top5 `0.53424658`.
- v120 proxy: macro `0.98139925`, top5 `0.47945205`.
- v114 clean baseline: macro `0.97920102`, top5 `0.52054795`.

v122 may not exactly reproduce v121 because the sidecar is injected before the final layer rather than after it, but it should preserve the same original signal while reducing hidden-test memory risk.

## Gate

Run Kaggle Run-mode only. Do not real-submit v122 unless runtime, schema, proxy, correlation, memory-risk, and candidate-specific compliance evidence pass.
