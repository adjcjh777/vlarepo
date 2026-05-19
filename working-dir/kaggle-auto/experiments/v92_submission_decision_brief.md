# v92 Submission Decision Brief

Updated: 2026-05-19 01:03 UTC

## Candidate
- `v92-attributed-mtoshi-vis-nobirdnet`
- Source reference: `beicicc/bc26-mtoshi-vis-may18`
- Local candidate: `birdclef-2026/notebooks/v92-attributed-mtoshi-vis-nobirdnet`
- Kaggle kernel: `junhaochengadjcjh7u7/bc26-v92-attributed-mtoshi-vis-nobirdnet`
- Run-mode output: `birdclef-2026/outputs/v92-attributed-mtoshi-vis-nobirdnet-v2`

## Evidence
- Kaggle Run-mode status: `COMPLETE`
- Runtime from log: about `520s`, below the 90-minute CPU cap.
- Metadata: CPU-only, internet disabled, competition source `birdclef-2026`.
- BirdNET: explicitly disabled for license compatibility; `submission_birdnet.csv` is all zero.
- Output: final dry-run `submission.csv` shape `(3, 235)`, row and class order match local `sample_submission.csv`.
- Numeric checks: no NaN, no inf, range `[0.47800776, 0.55945575]`, `221` rounded-6 unique values.
- Intermediate dry-run outputs: ProtoSSM and SED each produced `(240, 235)` train-file predictions; BirdNET branch is zero by design.
- Dry-run overlap: v92 vs v87 correlation `0.999061`, MAD `0.000250`; v92 vs v91 correlation `0.688480`, MAD `0.006172`.

## Decision
- Do not submit v92 now.
- Rationale: v91 is still pending, and v92 is effectively a near-duplicate of the v87 anchor on dry-run final output. It is useful as a verified fallback/provenance artifact, but it is not a materially fresh slot-two candidate.
- Automatic next action: wait for v91 score/error. If v91 scores below anchor, prefer finding a new non-near-duplicate candidate rather than submitting v92.

