# v116 Submission Decision Brief

Updated: 2026-05-19 06:47 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v116-tsubasa-convnext-sed/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v116-tsubasa-convnext-sed`
- Output: `birdclef-2026/outputs/v116-tsubasa-convnext-sed-v1/submission.csv`

## Run-Mode Evidence

- Kaggle Run-mode status: `COMPLETE`
- Runtime before saved output: about `489.9s`
- Schema: `120 x 235`, finite, no duplicate row IDs
- Range: `[0.012571, 0.999812]`
- Proxy: `macro=0.85930903`, `micro=0.83251880`, `top5=0.39726027`

## Diagnostic Notes

- Tsubasa ConvNeXt SED loaded successfully from CC0 dataset.
- Train-window SED AUC diagnostic was high: mean `0.9213`, active `71` classes.
- Remap accepted `44/234` classes with max strength `0.88`.
- Correlation vs clean branch outputs dropped materially:
  - vs v110 Pearson `0.764711`
  - vs v114 Pearson `0.766135`
  - vs v103 Pearson `0.679694`

## Decision

`REJECT - do not submit`

Rationale: v116 is compliance-clean and materially different, but the local
dry-run proxy collapses far below v110/v114 and v103. The likely failure mode is
over-aggressive train-window output-column remapping: it creates a lower-corr
signal but damages macro ranking too much for a real submission slot.

## Follow-Up

Create a more conservative v117 using the same CC0 ConvNeXt SED source but
turning off column remap. The next test should isolate whether the raw same-index
Tsubasa SED signal is useful before any remap/trust layer is reintroduced.
