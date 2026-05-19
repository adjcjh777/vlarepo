# v90 Submission Decision Brief

Updated: 2026-05-19 00:31 UTC

## Candidate
- `v90-attributed-youssef-e1-rare-tail-birdnet`
- Source reference: `cocoaai/bc26-youssef-e1-rare-tail-birdnet`
- Kaggle kernel: `junhaochengadjcjh7u7/bc26-v90-attributed-youssef-e1-rare-tail-birdnet`
- Run-mode version: `1`

## Evidence
- Kaggle Run-mode status: `COMPLETE`
- Runtime from log: about `389s`, well below the 90-minute CPU cap.
- Output: `submission.csv` shape `(3, 235)`, class columns and row order match `sample_submission.csv`.
- Numeric checks: no NaN, no inf, range `[0.4496346, 0.50999576]`, `226` rounded-6 unique values.
- Dry-run overlap: v90 vs v87 correlation `0.522885`, MAD `0.008947`.

## Compliance Finding
- The attached BirdNET model instance is `shadiakiki1/birdnet-analyzer/TfLite/birdnet_global_6k_v2.4_model_fp32-1/3`.
- Kaggle model instance metadata reports license `Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)`.
- This creates a material prize/final-eligibility risk for a Top 5奖金区 objective.

## Decision
- Do not submit v90.
- Mark as `HOLD-license-risk`.
- Use v91, a BirdNET-disabled variant, for the next compliance-safe Run-mode candidate.

