# v94 Submission Decision Brief

Candidate: `v94-attributed-karnak-advance-ensemble`

Decision: `REJECT - do not submit`

## Evidence

- Kaggle Run-mode status: `ERROR`.
- Failure mode: final direct ensemble row_id mismatch between 240-row train dry-run output and 3-row sample-aligned output.
- No valid full final Run-mode `submission.csv` was produced.
- The only final `submission.csv` artifact has 3 sample rows and is not useful for correlation or diversity evidence against v87.
- Current visible anchor remains v87 at 0.949; v91 scored 0.948 and was retired.

## Why Not Patch And Submit

A dry-run-only guard could make the notebook complete by skipping or synthetic-aligning mismatched dry-run rows, but that would not provide real final-output evidence. Because v94 is an attributed public derivative and not a clear score-push beyond 0.949, spending a daily competition submission slot would be unjustified.

## Follow-up

- Keep v94 as a recorded rejected source/reference.
- Do not revisit Karnak direct-blend variants unless a future public run shows materially stronger leaderboard evidence or accessible hidden-test-compatible output evidence.
- Continue looking for accessible, CPU/no-internet, non-near-duplicate candidates that can pass Run-mode without synthetic dry-run completion.
