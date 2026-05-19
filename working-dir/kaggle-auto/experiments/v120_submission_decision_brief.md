# v120 Submission Decision Brief

Updated: 2026-05-19 08:06 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v120-clean-tsubasa-sidecar/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v120-clean-tsubasa-sidecar`
- Output: `birdclef-2026/outputs/v120-clean-tsubasa-sidecar-v1/submission.csv`
- Mechanism: `0.85` clean Perch/EcoProto anchor plus `0.15` CC0 Tsubasa ConvNeXt SED sidecar.

## Originality

v120 is a workspace-original clean sidecar experiment, not a public notebook copy. The public CC0 Tsubasa model is treated as a small diversity branch. The candidate recomputes both views inside one CPU/no-internet notebook, avoids prior output CSVs, and excludes unknown-license SED/cache inputs.

## Run-Mode Evidence

- Kaggle Run-mode status: `COMPLETE`.
- Runtime before saved output: about `683.4s`.
- Schema: `120` rows, `235` columns, sample column order matched, all finite, no duplicate row IDs.
- Score range: `[0.013462, 0.999145]`.
- Proxy: `macro=0.98139925`, `micro=0.91435250`, `top5=0.47945205`.

## Correlation

- vs v110 clean anchor: Pearson `0.994670`, MAD `0.019354`.
- vs v114 selfblend: Pearson `0.994543`, MAD `0.019449`.
- vs v116 Tsubasa sidecar: Pearson `0.827078`, MAD `0.109674`.
- vs v103 hold/unknown-license: Pearson `0.795515`, MAD `0.124708`.
- vs v119 Roniheka: Pearson `0.730562`, MAD `0.144539`.

## Decision

`REJECT-memory after guarded slot 3`

Rationale before submission: v120 was the best clean-branch macro proxy so far and was fully CPU/no-internet/provenance-clean. It was submitted as UTC `2026-05-19` slot 3.

Final result: Kaggle ref `52802748` completed with no public score and error `Your notebook requested more memory (RAM) than is available.` Retire v120 as a final/next-submit candidate.

## Risk

The practical risk was hidden-test memory rather than public-LB quality. The likely failure mode is double execution of the expensive final decision layer for both sidecar and clean anchor. Future candidates should use single-pass hybridization before the final layer.
