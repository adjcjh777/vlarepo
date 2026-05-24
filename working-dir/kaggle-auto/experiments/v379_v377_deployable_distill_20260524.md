# v379 v377 Deployable Distillation Probe

Updated: 2026-05-24 13:29:20 UTC

Status: `PROMOTE-v379-deployable-v377-distill-NO-PUSH-NO-SUBMIT`.

## Research Question

Can the v377 teacher movement be distilled into hidden-test-computable features from the license-clean v107 branch, train-soundscape priors, and temporal context, so that no v103 output is needed at inference time?

## Inference Feature Policy

- Candidate inference uses v107 scores/ranks, train_soundscape site-hour priors, row_id-derived temporal context, and fixed coefficients.
- v103 is used only in this local probe to define the distillation target; it is not an inference dependency.
- No Kaggle push or real competition submission is authorized by this probe.

## Baselines

- v107 anchor macro: `0.97736356`, top5: `0.50684932`, fold std: `0.15524730`
- v377 oracle macro: `0.98367415`, top5: `0.50684932`, active cells: `282`
- anchor follow-up weak mean AUC: `0.94984332`

## Result

- Candidates screened: `384`
- Promoted local candidates: `72`
- Best candidate: `alpha0.01_delta_bw0.7_d0_pr0`
- Best macro: `0.97832804` / gain `0.00096449`
- Best weak follow-up gain: `0.00303125`
- Best fold std delta: `-0.00022659`
- Best corr vs anchor: `0.99996142`
- Best corr vs v377 oracle: `0.99980820`

## Top Candidates

| candidate | macro_gain | weak_gain | fold_std_delta | top5 | corr_anchor | corr_oracle | decision |
|---|---:|---:|---:|---:|---:|---:|---|
| alpha0.01_delta_bw0.7_d0_pr0 | 0.00096449 | 0.00303125 | -0.00022659 | 0.50684932 | 0.99996142 | 0.99980820 | PROMOTE-deployable-distill-candidate |
| alpha0.01_delta_bw0.7_d0_pr0.25 | 0.00096449 | 0.00303125 | -0.00022659 | 0.50684932 | 0.99996341 | 0.99980720 | PROMOTE-deployable-distill-candidate |
| alpha0.01_delta_bw0.7_d0_pr0.5 | 0.00096449 | 0.00303125 | -0.00022659 | 0.50684932 | 0.99996766 | 0.99979604 | PROMOTE-deployable-distill-candidate |
| alpha0.01_delta_bw0.7_d0.005_pr0 | 0.00093973 | 0.00295344 | -0.00022659 | 0.50684932 | 0.99996149 | 0.99980797 | PROMOTE-deployable-distill-candidate |
| alpha0.01_delta_bw0.7_d0.005_pr0.25 | 0.00093973 | 0.00295344 | -0.00022659 | 0.50684932 | 0.99996348 | 0.99980699 | PROMOTE-deployable-distill-candidate |
| alpha0.01_delta_bw0.7_d0.005_pr0.5 | 0.00093973 | 0.00295344 | -0.00022659 | 0.50684932 | 0.99996772 | 0.99979586 | PROMOTE-deployable-distill-candidate |
| alpha0.1_delta_bw0.7_d0_pr0 | 0.00093181 | 0.00292855 | -0.00022659 | 0.50684932 | 0.99996406 | 0.99980567 | PROMOTE-deployable-distill-candidate |
| alpha0.1_delta_bw0.7_d0_pr0.25 | 0.00093181 | 0.00292855 | -0.00022659 | 0.50684932 | 0.99996594 | 0.99980452 | PROMOTE-deployable-distill-candidate |
| alpha0.1_delta_bw0.7_d0_pr0.5 | 0.00093181 | 0.00292855 | -0.00022659 | 0.50684932 | 0.99996989 | 0.99979358 | PROMOTE-deployable-distill-candidate |
| alpha0.1_delta_bw0.7_d0.005_pr0 | 0.00090705 | 0.00285074 | -0.00022659 | 0.50684932 | 0.99996413 | 0.99980528 | PROMOTE-deployable-distill-candidate |
| alpha0.1_delta_bw0.7_d0.005_pr0.25 | 0.00090705 | 0.00285074 | -0.00022659 | 0.50684932 | 0.99996601 | 0.99980416 | PROMOTE-deployable-distill-candidate |
| alpha0.1_delta_bw0.7_d0.005_pr0.5 | 0.00090705 | 0.00285074 | -0.00022659 | 0.50684932 | 0.99996994 | 0.99979325 | PROMOTE-deployable-distill-candidate |

## Decision

- `PROMOTE-v379-deployable-v377-distill-NO-PUSH-NO-SUBMIT`
- If promoted, next step is a static notebook materializer that embeds fixed coefficients and repeats the same feature policy.
- If held, v377 remains a useful teacher diagnostic only, not a submit-ready route.
