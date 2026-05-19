# Rules Compliance Report: v92

Updated: 2026-05-19 01:03 UTC

## Candidate
`v92-attributed-mtoshi-vis-nobirdnet`

## Result
Status: `PASS-for-runmode-only`, `DO-NOT-SUBMIT-now`

## Checks
- Daily submissions: no real submission was made for v92; UTC `2026-05-19` remains `1/5` used because only v91 was submitted.
- Pending submission guard: pass; v91 is still pending, so v92 was not submitted.
- Final submissions: no final judging selection changed.
- CPU-only: pass; metadata has `enable_gpu=false`.
- Runtime: pass; Run-mode completed in about `520s`, below 90 minutes.
- Internet: pass; metadata has `enable_internet=false`.
- Output path: pass; Run-mode writes `submission.csv`.
- Format: pass; final dry-run `submission.csv` shape `(3, 235)`.
- Row order: pass; final dry-run rows match local `sample_submission.csv`.
- Class order: pass; final dry-run columns match local `sample_submission.csv`.
- NaN/inf: pass; none found.
- Range: pass; probabilities are within `[0, 1]`.
- BirdNET: pass; explicitly disabled and zero branch saved intentionally.
- Artifact provenance: pass for local Run-mode package; source metadata and attribution are recorded.
- External provenance: hold for real submission; some public Kaggle dataset/kernel-source licenses are still locally unknown.
- Duplicate-risk gate: hold for real submission; v92 dry-run final is nearly identical to v87 (`corr=0.999061`, MAD `0.000250`).

## Decision
Do not submit v92 while v91 is pending. Even after v91 resolves, v92 should not be used as slot two unless the active decision policy accepts a near-duplicate v87-style anchor maintenance candidate.

