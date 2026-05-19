# v117 Submission Decision Brief

Updated: 2026-05-19 06:51 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v117-tsubasa-convnext-noremap/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v117-tsubasa-convnext-noremap`
- Output: `birdclef-2026/outputs/v117-tsubasa-convnext-noremap-v1/submission.csv`

## Run-Mode Evidence

- Kaggle Run-mode status: `COMPLETE`
- Runtime before saved output: about `435.3s`
- Schema: `120 x 235`, finite, no duplicate row IDs
- Range: `[0.013660, 0.999643]`
- Proxy: `macro=0.71214482`, `micro=0.72131755`, `top5=0.32876712`

## Diagnostic Notes

- No-remap isolation worked as intended:
  - remapped classes: `0/234`
  - remap strength: all `0`
- Same-index Tsubasa ConvNeXt SED train-window AUC was only `0.7672`, below
  Perch calibrated AUC `0.8020`.
- Correlation remained materially different from v110/v114 (`~0.77`), but the
  quality collapse is too large.

## Decision

`REJECT - do not submit`

Rationale: turning off the remap made the branch worse rather than better.
Together with v116, this shows the Tsubasa ConvNeXt source is not a useful
drop-in SED replacement for the clean branch. It should not consume a real
submission slot.

## Follow-Up

Stop the Tsubasa ConvNeXt/Snowflake SED lane for now. Future work should move to
a different low-correlation source or a more internally grounded original
mechanism, not further tuning of this SED branch.
