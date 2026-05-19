# v105 Submission Decision Brief

Updated: 2026-05-19 04:03 UTC

## Candidate

- `v105-rankrestored-perch-guarded`
- Local path: `birdclef-2026/notebooks/v105-rankrestored-perch-guarded`
- Kaggle kernel: `junhaochengadjcjh7u7/bc26-v105-rankrestored-perch`
- Run-mode output: `birdclef-2026/outputs/v105-rankrestored-perch-guarded-v1`

## Original Change

v105 keeps v104's license-clean runtime dependency set and adds a bounded row-rank restoration layer from Perch/probe views:

- no runtime dependency on `jaejohn/perch-meta`;
- no runtime dependency on `tuckerarrants/bc2026-distilled-sed-public`;
- rebuilds train Perch features in-notebook;
- restores some high row-rank Perch/probe cells after the guarded macro rescue.

## Evidence

- Kaggle Run-mode status: `COMPLETE`.
- Runtime: about `335.8s` before save and about `346.7s` through nbconvert, below 90 minutes.
- Output: `submission.csv` shape `(120,235)`, finite, no duplicate row IDs, range `[0.011144416, 0.9992916]`.
- Rank restore log: `restore=1417`, `top_guard=138`.
- Local dry-run proxy:
  - `macro_auc=0.97751210`
  - `micro_auc=0.81765567`
  - `top1_hit=0.00000000`
  - `top5_hit=0.08219178`
- Compared with v104:
  - macro unchanged at `0.97751210`;
  - micro improves from `0.78763929` to `0.81765567`;
  - top1/top5 remain unchanged and too weak;
  - flattened correlation `0.99934247`, MAD `0.00180369`.

## Decision

`REJECT - do not submit v105`

Reason: v105 shows the row-rank restoration direction can improve micro without breaking macro, but it does not recover top-hit/top5. A real submission slot is not justified.

## Next Action

Run a more aggressive v106 rank-dominant Perch/probe restoration to test the ceiling of license-clean row ranking. If v106 still cannot recover top-hit/top5, abandon this Perch-only branch and return to either v103 risk acceptance or a genuinely new license-clean signal source.
