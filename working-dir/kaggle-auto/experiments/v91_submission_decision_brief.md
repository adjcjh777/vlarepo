# v91 Submission Decision Brief

Updated: 2026-05-19 00:31 UTC

## Candidate
- `v91-attributed-youssef-e1-rare-tail-nobirdnet`
- Source reference: `cocoaai/bc26-youssef-e1-rare-tail-birdnet`
- Local candidate: `birdclef-2026/notebooks/v91-attributed-youssef-e1-rare-tail-nobirdnet`
- Kaggle kernel: `junhaochengadjcjh7u7/bc26-v91-attributed-youssef-e1-rare-tail-nobirdnet`
- Run-mode output: `birdclef-2026/outputs/v91-attributed-youssef-e1-rare-tail-nobirdnet-v1`

## Evidence
- Kaggle Run-mode status: `COMPLETE`
- Runtime from log: about `508s`, below the 90-minute CPU cap.
- Metadata: CPU-only, internet disabled, competition source `birdclef-2026`.
- BirdNET: explicitly disabled for license compatibility; `submission_birdnet.csv` is all zero.
- Output: `submission.csv` shape `(3, 235)`, class columns and row order match `sample_submission.csv`.
- Numeric checks: no NaN, no inf, range `[0.45683104, 0.52307403]`, `226` rounded-6 unique values.
- Dry-run overlap: v91 vs v87 correlation `0.698726`, MAD `0.006061`; v91 vs v90 correlation `0.967619`, MAD `0.003041`.
- Log evidence: `BirdNET explicitly disabled for v91 license compatibility.`

## Decision
- Submit v91 as the first real submission of UTC `2026-05-19`.
- Rationale: v90's BirdNET signal is blocked by CC BY-NC risk; v91 preserves the source's Proto/SED sonotype and rare-tail gates, passes CPU/no-internet/runtime/schema checks, and uses today's first slot conservatively.
- Risk: dry-run difference from v87 is modest, so this is a cautious structural probe rather than a top20-probability lock.

