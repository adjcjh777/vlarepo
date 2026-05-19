# v104 Submission Decision Brief

Updated: 2026-05-19 03:58 UTC

## Candidate

- `v104-perch-only-guarded-rescue`
- Local path: `birdclef-2026/notebooks/v104-perch-only-guarded-rescue`
- Kaggle kernel: `junhaochengadjcjh7u7/bc26-v104-perch-only-guarded`
- Run-mode output: `birdclef-2026/outputs/v104-perch-only-guarded-rescue-v1`

## Original Change

v104 is a license-reduced continuation of the private v86/v102/v103 line:

- removes runtime dependencies on `jaejohn/perch-meta` and `tuckerarrants/bc2026-distilled-sed-public`;
- rebuilds train Perch features inside the Kaggle notebook from competition train soundscapes;
- replaces the external SED branch with a Perch-only surrogate view;
- keeps v103's positive-rescue and top-hit guard concept with more conservative rescue strengths.

## Evidence

- Kaggle Run-mode status: `COMPLETE`.
- Runtime: about `347s` before save and about `358s` through nbconvert, below 90 minutes.
- Metadata: private, CPU-only, internet disabled.
- Runtime dependencies: `rishikeshjani/perch-onnx-for-birdclef-2026` (`CC0-1.0`) and Google Perch model (`Apache 2.0`); unknown-license cache/SED dependencies removed.
- Output: `submission.csv` shape `(120,235)`, finite, no duplicate row IDs, range `[0.011144416, 0.9992916]`.
- Original guard counts from log:
  - `active_rescue=16`
  - `positive_rescue_cells=2749`
  - `top_hit_guard_cells=330`
  - `ctx_cells=2`
- Local dry-run proxy:
  - `macro_auc=0.97751210`
  - `micro_auc=0.78763929`
  - `top1_hit=0.00000000`
  - `top5_hit=0.08219178`
- Compared with v103: correlation `0.79467134`, MAD `0.12589129`.

## Decision

`REJECT - do not submit v104`

Reason: v104 proves a cleaner compliance path is feasible and stays within runtime, but removing the SED/cache dependencies damages ranking quality too much. It should not consume a real submission slot.

## Next Action

Use v104 as a fallback and implementation reference. The next useful branch should recover SED-like ranking signal from license-clean sources or internal Perch/probe distillation, rather than submitting v104 directly.
