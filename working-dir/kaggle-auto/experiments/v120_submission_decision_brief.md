# v120 Submission Decision Brief

Updated: 2026-05-19 07:47 UTC

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

`SUBMIT - guarded slot 3`

Rationale: v120 is the best clean-branch macro proxy so far and is fully CPU/no-internet/provenance-clean. It is correlated with v110/v114, but the Tsubasa sidecar provides a measured low-weight diversity signal and a local macro improvement large enough to justify one real slot while UTC `2026-05-19` remains at `2/5` visible submissions.

## Risk

The top5 proxy drops from v114 `0.520548` to v120 `0.479452`, so this is a bold macro-oriented clean candidate rather than the conservative fallback. If public LB drops below the v87 `0.949` anchor, retire this exact blend and do not keep increasing Tsubasa weight.
