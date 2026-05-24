# v387 Score Monitor Status

Updated: 2026-05-24 15:37:07 UTC

## Submission

- candidate: `v387-dryrun-tolerant-static-distill`
- ref: `52991496`
- submitted_at: `2026-05-24 15:21:09.597000`
- status: `SubmissionStatus.PENDING`
- public_score: ``
- error: ``
- utc_today_visible_submissions: `3`

## Decision

- state: `WAIT-pending`
- reason: v387 is pending; do not submit another candidate until this resolves

## Guard

- Do not submit another candidate while v387 is pending.
- If v387 improves beyond `0.949`, record the new visible best and start protection planning.
- If v387 ties/drops/errors, hold or retire v386 parameter-stressed fixed-coefficient distill before any sibling route.
