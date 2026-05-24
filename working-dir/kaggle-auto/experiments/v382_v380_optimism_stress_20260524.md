# v382 v380 Optimism Stress Audit

Updated: 2026-05-24 13:46:13 UTC

Status: `READY-v380-optimism-stress-pass-RUNMODE-ONLY-NO-SUBMIT`.

## Research Question

Is the v380 full-coefficient materialization's local macro promotion mostly supported by blocked v379 OOF behavior, or is it too optimistic to continue toward Run-mode proof?

## Result

- v379 OOF macro gain: `0.00096449`
- v380 full-coef macro gain: `0.00160120`
- Macro optimism gap: `0.00063671`
- v379 OOF weak gain: `0.00303125`
- v380 full-coef weak gain: `0.00503235`
- Fold std not worse in both views: `True`
- Top5 not worse: `True`

## Metric Table

| metric | v379_oof | v380_fullcoef | delta | decision |
|---|---:|---:|---:|---|
| macro_gain | 0.00096449 | 0.00160120 | 0.00063671 | WATCH-optimism |
| weak_followup_gain | 0.00303125 | 0.00503235 | 0.00200110 | WATCH-optimism |
| fold_std_delta | -0.00022659 | -0.00022659 | 0.00000000 | PASS-no-extra-optimism |
| top5_hit | 0.50684932 | 0.50684932 | 0.00000000 | PASS-no-extra-optimism |
| corr_vs_anchor | 0.99996142 | 0.99994875 | -0.00001267 | PASS-no-extra-optimism |

## Decision

- `READY-v380-optimism-stress-pass-RUNMODE-ONLY-NO-SUBMIT`
- Next: Continue Run-mode proof. Even if Run-mode passes, require a separate competition-submit gate before any real submission.
