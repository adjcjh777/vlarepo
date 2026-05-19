# v134 Runmode Decision Brief

Updated: 2026-05-19 12:00 UTC

## Candidate

- Kernel: `junhaochengadjcjh7u7/bc26-v134-stable3-guarded-rescue`
- Output dir: `birdclef-2026/outputs/v134-stable3-guarded-rescue-v1`
- Audit script: `scripts/audit_v134_runmode.py`

## External Runmode Evidence

- Kaggle status: `COMPLETE`
- Fetched files:
  - `submission.csv`
  - `v134_guarded_branch_summary.csv`
- Fetch note: one auxiliary file download hit an SSL EOF, but the primary output file for validation is present.

## Validation Snapshot

- Output shape: `120 x 235`
- Columns match `sample_submission.csv`: `True`
- Duplicate row IDs: `False`
- NaN/inf: `False / False`
- Range: `[0.011144416, 0.9994699]`
- Mean/std: `0.521994338403 / 0.242283004113`
- Correlation vs references:
  - vs `v110`: Pearson `0.99855157`, MAD `0.00086211`
  - vs `v114`: Pearson `0.99814262`, MAD `0.00214727`
  - vs `v127`: Pearson `0.99746160`, MAD `0.00181695`

## Interpretation

`v134` passed the minimum external Run-mode gate:

- notebook executed to completion;
- output file is present and numerically valid;
- route remains close to the clean anchor family while being narrower than `v127`.

At the same time, the similarity numbers show that `v134` is still a near-family continuation, not a radically new path. That means the anti-collapse question is not fully answered by Run-mode alone.

## Decision

`HOLD-RUNMODE-PASS`

Keep `v134` in the guarded candidate pool. It has earned continued consideration because the external Run-mode pass removes one class of operational risk, but it should not be real-submitted yet without a stronger anti-collapse screen than proximity to `v110/v114/v127`.

## Next Action

- Keep today's slot 5 unused.
- Use `v134` as the leading stable3 guarded notebook package for future guarded comparison work.
- If a next real candidate is ever needed, compare it against `v134` with the anti-collapse scorecard before spending a slot.

