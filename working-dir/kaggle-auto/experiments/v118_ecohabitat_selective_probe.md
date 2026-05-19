# v118 EcoHabitat Selective Rescue Probe

Updated: 2026-05-19 07:04 UTC

## Purpose

User guidance for this iteration was to add original innovation rather than
only reference public work. The public habitat-context notebook inspected in
this turn was not a valid candidate, so v118 tests a lightweight original
variant that can be implemented inside the existing clean branch if it works.

## Mechanism

Baseline branches:

- `v110`: clean EcoProto branch.
- `v113`: LantingGuo MelNorm sidecar branch.
- `v114`: fixed `0.85*v110 + 0.15*v113` self-contained blend.

v118 probe formula family:

```text
clip(v110 + alpha * row_gate * support_gate
     * clip((auc_delta - threshold) / slope, 0, 1)
     * (v113 - v110))
```

Original gates tested:

- `class_gate`: only lets v113 influence classes where internal train-window
  AUC delta is positive enough.
- `support_gate`: reduces trust on extremely sparse classes.
- `row_gate=entropy`: uses v110 row entropy as an acoustic-context uncertainty
  proxy.
- `row_gate=diff`: uses v110/v113 disagreement as a branch-context proxy.
- `row_gate=eco`: combines entropy and disagreement.
- `row_gate=inv_eco`: tests the opposite, preferring confident/low-disagreement
  rows.

## Results

Command:

```bash
python3 birdclef-2026/scripts/birdclef_probe_v118_ecohabitat_rescue.py
```

Output:

- `experiments/v118_ecohabitat_selective_probe.csv`
- `1083` formulas scored.

Top local proxy rows:

| name | macro_auc | micro_auc | top5_hit |
| --- | ---: | ---: | ---: |
| v114 | 0.97920102 | 0.91572402 | 0.52054795 |
| v110 | 0.97911204 | 0.91481637 | 0.52054795 |
| th-0.05_sl0.04_flat_a0.1 | 0.97911204 | 0.91499235 | 0.52054795 |
| th-0.05_sl0.04_flat_a0.15 | 0.97911204 | 0.91506714 | 0.52054795 |
| th-0.05_sl0.04_flat_a0.2 | 0.97911204 | 0.91514665 | 0.52054795 |

## Decision

`REJECT - do not materialize or submit v118 as-is`.

The original gating concept is valid and reusable, but the local proxy did not
beat v114. The best formulas tie v110 on macro AUC while improving micro AUC
slightly; that is not enough to justify a Kaggle submission slot or a new
notebook materialization.

## Next Direction

Do not keep tuning v113 gating weights. Better innovation targets:

- find a clean low-correlation source with real OOF-style evidence;
- create a license-clean rescue branch that preserves v103-like macro/top5
  behavior without unknown-license SED/cache dependencies;
- use habitat/acoustic-context features only if they can be computed from real
  audio in the CPU/no-internet notebook and validated against train-window
  labels, not from dummy or fallback outputs.

