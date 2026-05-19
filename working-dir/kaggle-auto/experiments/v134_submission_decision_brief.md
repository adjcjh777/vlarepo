# v134 Submission Decision Brief

Updated: 2026-05-19 12:30 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v134-stable3-guarded-rescue/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v134-stable3-guarded-rescue`
- Output: `birdclef-2026/outputs/v134-stable3-guarded-rescue-v1/submission.csv`
- Mechanism: single-final-layer v110 clean EcoProto anchor plus stable `47158son13/22/23` clean `v112` rescue with a row-level top-hit preservation guard.

## Originality

v134 is a workspace-original continuation of the clean non-Tsubasa line. It is not a public notebook copy and not a broad rerun of v127:

- it narrows the route to the stable three-class clean component found by grouped validation;
- it keeps positive-only rescue updates;
- it adds a `v103`-style row-level top-hit preservation guard;
- it removes the broader five-class raw-side expansion and the `roniheka` runtime dependency.

## Evidence

- Kaggle Run-mode status: `COMPLETE`.
- Schema: `120 x 235`, sample column order matched, finite, no duplicate row IDs.
- Score range: `[0.011144416, 0.9994699]`.
- Blocked local proxy: `macro=0.97979134`, `micro=0.91924338`, `top5=0.52054795`.
- Correlation:
  - vs v110: Pearson `0.99855157`, MAD `0.00086211`
  - vs v114: Pearson `0.99814262`, MAD `0.00214727`
  - vs v127: Pearson `0.99746160`, MAD `0.00181695`

## Decision

`HOLD-RUNMODE-PASS - guarded pool #1`

v134 has the best current anti-collapse profile inside the stable clean family and is the leading guarded candidate for the next window. It is still not ready for an immediate real submission because its external Run-mode evidence shows that it remains close to the v110/v114/v127 family and has not yet crossed a stronger anti-collapse threshold.

## Risk

The main remaining risk is not operational failure but family proximity: despite the narrower stable3 guard design, v134 still behaves like a near-family continuation rather than a new robust frontier. That makes same-day impulsive submission exactly the wrong move.

## Next Action

- Keep `v134` at guarded-pool rank `#1`.
- Do not spend today's remaining real slot.
- At the next UTC window, rerun the gate and anti-collapse scorecard before deciding whether v134 should graduate from guarded pool to real-submit candidate.

