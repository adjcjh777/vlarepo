# v124 Submission Decision Brief

Updated: 2026-05-19 09:45 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v124-postfinal-rankcal-tsubasa/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v124-postfinal-rankcal`
- Output: `birdclef-2026/outputs/v124-postfinal-rankcal-tsubasa-v1/submission.csv`
- Mechanism: run clean EcoProto/rank-launch final layer once, then apply a lightweight post-final rank-calibrated Tsubasa sidecar on 10 selected classes.

## Evidence

- Run-mode: `COMPLETE`.
- Runtime before saved output: about `462.5s`.
- Schema: `120 x 235`, sample column order matched, all finite, no duplicate row IDs.
- Proxy: `macro=0.97115717`, `micro=0.90281675`, `top5=0.52054795`.
- Gate cells: `555 / 28080`.
- Correlation vs v110: Pearson `0.998549`, MAD `0.001412`.
- Correlation vs v114: Pearson `0.998147`, MAD `0.002647`.

## Decision

`REJECT - do not submit`

v124 confirms that a post-final lightweight sidecar is memory-safe, but it damages macro proxy more than v122/v123. The current Tsubasa sidecar lane should stop: v121 is quality-strong but memory-unsafe, v122/v123 are memory-safe but not worth a slot, and v124 is memory-safe but quality-negative.
