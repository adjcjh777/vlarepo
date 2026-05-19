# v101 Submission Decision Brief

Updated: 2026-05-19 02:47 UTC

## Candidate

- `v101-attributed-alexy-cnn-cpu`
- Source reference: `alexycactus/birdclef-2026-cnn-infer-dataset`
- Local candidate: `birdclef-2026/notebooks/v101-attributed-alexy-cnn-cpu`
- Kaggle kernel: `junhaochengadjcjh7u7/bc26-v101-attributed-alexy-cnn-cpu`
- Run-mode output: `birdclef-2026/outputs/v101-attributed-alexy-cnn-cpu-v1`

## Evidence

- Kaggle Run-mode status: `COMPLETE`
- Metadata: private, CPU-only, internet disabled, competition source `birdclef-2026`.
- Code hardening: forced CPU, train fallback removed, final duplicate-row/finite/range/row-order assertions added.
- Run-mode output: sample-shaped prior `submission.csv` with shape `(3,235)`, finite values, no duplicate row IDs, checksum `4920b7c5f4a3b3ab30a54ee2858b2bfe4de06991a695c30608d9c22d5554d1bd`.
- Run-mode log confirms checkpoint dataset mounting and 3 fold checkpoints loaded on CPU.
- Local proxy from public Alexy CPU dry-run output: `macro_auc=0.98988271`, `micro_auc=0.99909419`, `top5_hit=1.0`.
- Public Alexy CPU dry-run runtime evidence: 51.2 s for 16 train-fallback files.

## Decision

Submit v101 as the second real submission of UTC `2026-05-19`.

Rationale: after v91 scored below the v87 anchor, v101 is a materially different CNN route rather than another near-EoS/Proto-SED replay. It is CPU-only, no-internet, provenance-recorded, and has strong dry-run proxy evidence. The guarded submission is necessary to measure hidden-test runtime and score because Kaggle Run mode does not mount hidden test files.

Risk: this is an attributed public-reference derivative and its Run-mode output is sample prior only; hidden-test behavior is not proven until the code submission completes.

## Result Update

Updated: 2026-05-19 03:25 UTC

- Status: `COMPLETE`
- Public score: `0.898`
- Outcome: retire v101. It is below the `0.949` anchor, below v91 `0.948`, below v88 `0.921`, and below the original-like `0.925` floor.
- Next action: do not submit further Alexy CNN derivatives from this lane; continue with original/compliance-clean candidates.
