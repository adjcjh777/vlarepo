# v387 Score Monitor Status

Updated: 2026-05-24 15:44:57 UTC

## Submission

- candidate: `v387-dryrun-tolerant-static-distill`
- ref: `52991496`
- submitted_at: `2026-05-24 15:21:09.597000`
- status: `SubmissionStatus.COMPLETE`
- public_score: `0.881`
- error: ``
- utc_today_visible_submissions: `3`

## Decision

- state: `RETIRE-no-progress`
- reason: score underperformed 0.949 anchor; retire v387 unless a concrete implementation bug is found

## Guard

- Do not submit another candidate while v387 is pending.
- If v387 improves beyond `0.949`, record the new visible best and start protection planning.
- If v387 ties/drops/errors, hold or retire v386 parameter-stressed fixed-coefficient distill before any sibling route.
