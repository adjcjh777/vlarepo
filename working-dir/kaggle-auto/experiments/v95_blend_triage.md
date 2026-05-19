# v95 Blend Triage - v87/v91

Checked at: 2026-05-19 UTC.

Question: should the second UTC-day slot be spent on a small blend between v87 and v91?

## Available Score Evidence

| Candidate | Public LB | Decision Status |
| --- | ---: | --- |
| v87 `nina-eos5-v38plus` | `0.949` | Current visible anchor. |
| v91 `youssef-e1-rare-tail-nobirdnet` | `0.948` | Retired as a standalone route because it scored below v87. |

## Dry-run Output Relationship

The local Run-mode outputs are only 3 sample rows, so they are weak evidence for hidden performance. They still show that v91 is not a pure duplicate:

| Pair | Pearson | MAD |
| --- | ---: | ---: |
| v87 vs v91 | `0.698726` | `0.006061` |
| v87 vs v92 | `0.999061` | `0.000250` |
| v87 vs v88 | `0.274567` | `0.204219` |

Small v91-weight blends remain very close to v87:

| v91 weight | Corr vs v87 | MAD vs v87 |
| ---: | ---: | ---: |
| 0.05 | `0.998858` | `0.000303` |
| 0.10 | `0.995424` | `0.000606` |
| 0.15 | `0.989722` | `0.000909` |
| 0.20 | `0.981820` | `0.001212` |

## Decision

Do not submit a v87/v91 blend now.

Rationale:

- v91 has already scored lower than v87 by 0.001.
- A small blend is likely anchor-maintenance at best and does not have a credible path to the current top-20 cutoff (`0.953`), let alone top-5 (`0.958`).
- The dry-run output is too small to justify spending a real submission slot.
- Combining the two full notebooks into one CPU-only hidden-test kernel is feasible but would require another Run-mode validation and still would not address the top-20 gap.

v95 is therefore held as a design note, not a notebook candidate.
