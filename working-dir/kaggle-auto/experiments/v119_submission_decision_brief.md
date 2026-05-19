# v119 Submission Decision Brief

Updated: 2026-05-19 07:24 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v119-roniheka-hgnet-sed/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v119-roniheka-hgnet-sed`
- Output: `birdclef-2026/outputs/v119-roniheka-hgnet-sed-v1/submission.csv`
- Mechanism: CC0 Roniheka HGNet SED evidence source plus local remap/trust/EcoProto/rank-launch clean blend.

## Originality

v119 was built in response to the requirement to add our own innovation rather than only follow public work. The model source is public and CC0, but the candidate-specific contribution is the decision layer around it:

- audited replacement of weak clean raw-audio SED with a mel-Spec HGNet source;
- workspace-local class remap from train-window evidence;
- branch trust shrinkage before blending;
- EcoProto/rank-launch fusion from the clean local branch;
- no direct public output CSV, public kernel fork, or unknown-license SED/cache dependency at runtime.

## Run-Mode Evidence

- Kaggle Run-mode status: `COMPLETE`.
- Runtime before saved output: about `400.8s`.
- Schema: `120` rows, `235` columns, sample column order matched, all finite, no duplicate row IDs.
- Score range: `[0.013670, 0.999859]`.
- Proxy: `macro=0.86521034`, `micro=0.87197101`, `top5=0.34246575`.

## Correlation

- vs v103 hold/unknown-license: Pearson `0.677892`, MAD `0.158460`.
- vs v110 clean branch: Pearson `0.716760`, MAD `0.148745`.
- vs v112 clean SED B0: Pearson `0.636338`, MAD `0.164620`.
- vs v113 LantingGuo MelNorm: Pearson `0.718223`, MAD `0.148134`.
- vs v114 selfblend: Pearson `0.718637`, MAD `0.148267`.
- vs v116 Tsubasa remap: Pearson `0.658242`, MAD `0.161024`.
- vs v117 Tsubasa no-remap: Pearson `0.642985`, MAD `0.164857`.

## Decision

`REJECT - do not submit`

Rationale: v119 is valuable as a clean and original negative experiment because it is less correlated with v110/v114 than earlier clean variants, but its local proxy collapses to `0.86521034`, far below v114 `0.97920102` and v110 `0.97911204`. Spending one of the remaining real submission slots would be unjustified.

## Next Direction

Stop tuning Roniheka HGNet SED as a direct final branch unless new evidence explains the proxy collapse. The next original attempt should focus on a mechanism that raises top5/local macro simultaneously, for example class-selective rescue driven by positive per-class deltas or a different audited source with stronger train-window alignment.
