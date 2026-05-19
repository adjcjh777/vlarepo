# v127 Submission Decision Brief

Updated: 2026-05-19 11:22 UTC

## Candidate

- Notebook: `birdclef-2026/notebooks/v127-memorysafe-nontsubasa-router/submission.ipynb`
- Kernel: `junhaochengadjcjh7u7/bc26-v127-nontsubasa-router`
- Output: `birdclef-2026/outputs/v127-memorysafe-nontsubasa-router-v1/submission.csv`
- Mechanism: single-final-layer v110 clean EcoProto anchor plus post-final rank-calibrated raw-side router on five support>=10 non-Tsubasa classes.

## Evidence

- Run-mode: `COMPLETE`.
- Runtime: about `390.8s` through nbconvert.
- Schema: pass, `120 x 235`, finite, no duplicate row IDs, sample column order matched.
- Proxy: macro `0.98008089`, micro `0.91595668`, top5 `0.52054795`.
- Correlation vs v110: Pearson `0.996646`, MAD `0.002296`.
- Correlation vs v114: Pearson `0.996229`, MAD `0.003581`.
- Correlation vs raw side-family references: v112 Pearson `0.783987`; v119 Pearson `0.722441`.
- Real competition outcome: ref `52807175` is now `SubmissionStatus.COMPLETE` with public score `0.883`.

## Rationale

v127 is weaker than the exact v126 final-surface router but is much safer operationally:

- no Tsubasa dependency;
- no prior output CSV mount;
- no side final-layer recomputation;
- one clean final layer plus sequential raw side sessions;
- runtime far below 90 minutes;
- positive macro proxy over v110/v114.

The top5 proxy does not improve and the local gain is narrow, so v127 should not be treated as a final candidate. However, after v120's hidden RAM failure and v122-v124 quality failures, v127 is the best available memory-safe original candidate for a guarded real-feedback slot.

## Decision

`REJECT-score - retire v127 as a submit/final candidate`

The real score `0.883` is a hard negative result. Even though the notebook was compliant, CPU-safe, and strong on the local proxy, it collapses too far below the `0.949` anchor to justify further near-neighbor submissions from this exact clean-router family.

## Next Action

Treat v127 as the fifth consecutive non-positive outcome after the `0.949` anchor and unlock method-family exploration under the updated goal rule. Even so, do not spend the next slot on another low-confidence branch; any follow-up should first clear a stronger anti-collapse screen than the v127 proxy did.
