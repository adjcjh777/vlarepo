# v121 Run-Mode Status

Updated: 2026-05-19 08:29 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v121-class-selective-tsubasa/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v121-class-selective-tsubasa`
- Output directory: `birdclef-2026/outputs/v121-class-selective-tsubasa-v1`
- Generator: `birdclef-2026/scripts/birdclef_prepare_v121_class_selective_tsubasa.py`

## Status

Kaggle Run-mode status: `COMPLETE`.

Downloaded artifacts:

- `submission.csv`
- `v121_class_selective_tsubasa_summary.csv`
- `v121_tsubasa_sidecar_remap_diagnostics.csv`
- `bc26-v121-class-selective-tsubasa.log`

## Runtime Evidence

- Output saved at about `612.9s`.
- nbconvert completed at about `625.5s`.
- Runtime is below the 90-minute CPU inference cap in Run-mode.
- CPU-only ONNX Runtime execution succeeded.
- Internet disabled in kernel metadata.

## Branch Evidence

- Clean anchor range/mean/std: `[0.011144, 0.999470] / 0.521132 / 0.242345`.
- Tsubasa sidecar range/mean/std: `[0.012571, 0.999812] / 0.520771 / 0.251924`.
- Final class-selective blend range/mean/std: `[0.011144, 0.999470] / 0.522376 / 0.242254`.
- Selected classes: `47158son13`, `47158son15`, `47158son16`, `47158son21`, `47158son22`, `47158son23`, `516975`, `chacha1`, `grekis`, `plcjay1`.
- Sidecar gate cells: `523 / 28080`.
- Final gate: selected class and `tsubasa_sidecar > clean_anchor + 0.02`.
- Final mix: `0.40` Tsubasa sidecar only on gated cells; clean anchor elsewhere.

## Quality Evidence

- Proxy: macro `0.98275473`, micro `0.92510802`, top1 `0.23287671`, top5 `0.53424658`.
- Schema: `120 x 235`, finite values, no duplicate row IDs, score range `[0.011144, 0.999470]`.
- Columns match `sample_submission.csv`; dry-run row IDs come from train soundscapes, so row-order match to hidden-test sample is not applicable in this local proxy output.
- Correlation vs v110: Pearson `0.998869`, MAD `0.001244`.
- Correlation vs v114: Pearson `0.998467`, MAD `0.002480`.
- Correlation vs v120: Pearson `0.994379`, MAD `0.019665`.
- Correlation vs v116 Tsubasa sidecar: Pearson `0.769061`, MAD `0.127784`.

## Decision

Run-mode passed, but v121 is `HOLD-memory-risk`.

The candidate is a better original sidecar design than v120 on local proxy metrics, but it still uses the same double-final-layer structure that caused v120 to exceed hidden-test RAM. Do not real-submit v121 as-is. Convert the idea into a single-pass memory-reduced follow-up before spending another real slot.
