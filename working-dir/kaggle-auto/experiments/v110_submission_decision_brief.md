# v110 Submission Decision Brief

Updated: 2026-05-19 05:00 UTC

## Candidate

- `v110-ecoproto-clean-blend`
- Local path: `birdclef-2026/notebooks/v110-ecoproto-clean-blend`
- Kaggle kernel: `junhaochengadjcjh7u7/bc26-v110-ecoproto-cleanblend`
- Run-mode output: `birdclef-2026/outputs/v110-ecoproto-clean-blend-v1`

## Evidence

- Kaggle Run-mode status: `COMPLETE`.
- Runtime: about `287.8s` before save and about `292.6s` through nbconvert.
- Metadata: private, CPU-only, internet disabled.
- Unknown-license runtime dependencies: none.
- Output: `submission.csv` shape `(120,235)`, finite, no duplicate row IDs, range `[0.011144416, 0.999469900]`.
- Proxy: `macro_auc=0.97911204`, `micro_auc=0.91481637`, `top1_hit=0.21917808`, `top5_hit=0.52054795`.
- Correlation: vs v107 `0.99372017`, vs v109 `0.99718071`, vs v103 `0.78728573`.

## Decision

`HOLD - do not submit now`

Reason: v110 is the best license-clean top-k fallback so far and improves over v107 top5, but it remains too close to v107/v109 and far behind v103 on macro/top-hit evidence. It is not strong enough to justify spending a real submission slot against the current `0.949` anchor.

## Next Action

Stop squeezing the clean Perch-only family for now. The next high-value direction is a license-clean SED-like source or an internal distillation signal built from competition labels and allowed public models.

