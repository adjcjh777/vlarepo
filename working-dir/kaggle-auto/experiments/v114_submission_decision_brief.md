# v114 Submission Decision Brief

Updated: 2026-05-19 06:12 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v114-v110-v113-selfblend/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v114-clean-selfblend`
- Output: `birdclef-2026/outputs/v114-v110-v113-selfblend-v1/submission.csv`
- Mechanism: self-contained `0.85*v110_like + 0.15*v113_like` blend.

## Originality

v114 is not a direct public-notebook fork or post-hoc CSV blend. It recomputes
two internal SED views inside one CPU/no-internet Kaggle notebook:

- `v110_like`: Perch-only clean fallback SED surrogate.
- `v113_like`: LantingGuo CC0 ONNX model passed through our MelNormProbe view
  selection and class-level trust shrinkage.
- The final decision layer is executed for both branches and blended inside the
  notebook; no prior local output CSV is mounted at runtime.

## Run-Mode Evidence

- Kaggle Run-mode status: `COMPLETE`
- Runtime before saved output: about `535.5s`
- Schema: `120` rows, `235` columns, all finite, no duplicate row IDs.
- Score range: `[0.011144, 0.999466]`
- Proxy: `macro=0.97920102`, `micro=0.91572402`, `top1=0.23287671`,
  `top5=0.52054795`

## Branch Diagnostics

- v110_like mean/std: `0.521132/0.242345`
- v113_like mean/std: `0.521022/0.243240`
- v114_blend mean/std: `0.521116/0.241920`
- Branch delta mean/std/min/max: `-0.000110/0.046091/-0.796220/0.738279`
- Per-class train-window AUC deltas: `8` positive, `63` negative,
  `67` classes with absolute delta above `0.05`.

## Correlation

- vs v110: Pearson `0.999594`, Spearman `0.999594`
- vs v113: Pearson `0.986973`, Spearman `0.986552`
- vs v103: Pearson `0.787564`, Spearman `0.783990`
- vs v112: Pearson `0.780190`, Spearman `0.775591`
- vs v111: Pearson `0.764050`, Spearman `0.759230`

## Decision

`HOLD - do not submit`

Rationale: v114 is compliance-clean and self-contained, and it exactly
materializes the small local blend gain over v110. However, the gain is tiny
(`macro 0.97920102` vs v110 `0.97911204`) and the output is almost identical to
v110 (`Pearson 0.999594`). This is useful as a documented original diagnostic,
but not strong enough to spend one of the daily real-submission slots.

## Next Direction

The next useful attempt should not simply increase the v113 branch weight. The
evidence says the LantingGuo MelNorm branch is weaker for most train-window
classes. Prefer a lower-correlation original mechanism, for example:

- a class-selective rescue that only applies the v113 branch to positive-delta
  classes; or
- a new audited CC0 SED/source branch with lower correlation to v110 and a
  stronger per-class diagnostic profile.
