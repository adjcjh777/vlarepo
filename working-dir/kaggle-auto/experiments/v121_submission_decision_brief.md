# v121 Submission Decision Brief

Updated: 2026-05-19 08:29 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v121-class-selective-tsubasa/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v121-class-selective-tsubasa`
- Output: `birdclef-2026/outputs/v121-class-selective-tsubasa-v1/submission.csv`
- Mechanism: clean Perch/EcoProto anchor plus class-selective `0.40` CC0 Tsubasa ConvNeXt SED sidecar only when `tsubasa_sidecar > clean_anchor + 0.02`.

## Originality

v121 is not a public notebook copy. It uses the public CC0 Tsubasa ConvNeXt ONNX model only as an auditable signal source, then adds a workspace-original class-selection and cell-level margin gate derived from local proxy evidence. The intervention is deliberately sparse: 10 selected classes and `523 / 28080` gated cells.

## Run-Mode Evidence

- Kaggle Run-mode status: `COMPLETE`.
- Runtime before saved output: about `612.9s`.
- Schema: `120` rows, `235` columns, sample column order matched, all finite, no duplicate row IDs.
- Score range: `[0.011144, 0.999470]`.
- Proxy: `macro=0.98275473`, `micro=0.92510802`, `top5=0.53424658`.

## Correlation

- vs v110 clean anchor: Pearson `0.998869`, MAD `0.001244`.
- vs v114 selfblend: Pearson `0.998467`, MAD `0.002480`.
- vs v120 global sidecar: Pearson `0.994379`, MAD `0.019665`.
- vs v116 Tsubasa sidecar: Pearson `0.769061`, MAD `0.127784`.
- vs v119 Roniheka: Pearson `0.718611`, MAD `0.148265`.

## Decision

`HOLD - do not submit as-is`

Rationale: v121 is the strongest local clean-sidecar proxy so far and directly addresses the user's request for original innovation. However, v120's real submission failed with hidden-test RAM exceeded, and v121 still recomputes both the sidecar branch and the clean-anchor final layer. That makes the hidden-test memory risk too high for another real slot.

## Next Candidate Direction

Build a single-pass memory-reduced v122 that injects the class-selective Tsubasa evidence before the final decision layer, then runs the expensive final layer once. The intended design is:

- capture Tsubasa remapped SED probabilities once;
- compute the clean Perch surrogate SED view once;
- apply the 10-class `sidecar > clean + 0.02` gate at the SED-probability level;
- replace `sed_probs` with the hybrid view;
- run the existing EcoProto/rank-launch final layer once.

Only consider a real submission after v122 passes Run-mode, schema, proxy, correlation, and candidate-specific compliance checks.
