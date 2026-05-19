# v103 Guarded Macro-Risk Rescue Plan

Created: 2026-05-19 03:10 UTC

## Purpose

The user explicitly asked for original innovation rather than only following public work. v103 keeps the private v86/v102 line and adds a more conservative original guard layer:

- keep v102's class-wise macro-risk rescue idea;
- reduce rescue strength for weak mid-support classes;
- require positive per-cell rescue evidence before using the full rescue mix;
- add a row-level top-hit preservation guard for confident v84-like anchor winners;
- preserve high-AUC and rare-class conservative guards.

## Hypothesis

v102 had strong local macro proxy but weak micro/top-hit proxy. v103 should keep the macro-risk rescue signal while reducing damage to confident primary calls.

## Constraints

- Kaggle Run-mode first only.
- No real competition submission while v101 ref `52795021` is `PENDING`.
- CPU-only, no internet, private kernel metadata.
- Final inference must remain below the 90-minute Kaggle limit.

## Candidate

- Prepare script: `birdclef-2026/scripts/birdclef_prepare_v103_guarded_macro_rescue.py`
- Notebook dir: `birdclef-2026/notebooks/v103-guarded-macro-risk-rescue`
- Kaggle kernel: `junhaochengadjcjh7u7/bc26-v103-guarded-macro-rescue`

## Decision Gate

Submit v103 only if:

- Run-mode completes and output passes schema/range/order checks;
- proxy does not regress below v102 in the macro/top-hit tradeoff;
- v101 has scored or failed, leaving a real submission slot decision clear.
