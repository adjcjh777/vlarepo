# Rules Compliance Report: v103

Updated: 2026-05-19 03:38 UTC

## Candidate

`v103-guarded-macro-risk-rescue`

## Result

Status: `HOLD-for-real-submit`

v103 is a valid original Run-mode candidate, but it is not yet a fully clean real-submit/final candidate because two attached public Kaggle datasets expose `unknown` license metadata through the Kaggle API.

## Checks

- Daily submissions: UTC `2026-05-19` visible real submissions are `2/5`; v101 ref `52795021` completed with public score `0.898`.
- Pending submissions: none visible after v101 completion.
- Final submissions: no final judging selection is changed by v103.
- CPU-only: pass; metadata has `enable_gpu=false` and `enable_tpu=false`.
- Runtime: pass for Run-mode; v103 model log reaches save at about `239s`, nbconvert ends about `251s`, below 90 minutes.
- Internet: pass; metadata has `enable_internet=false`.
- Output path: pass; Run-mode writes `/kaggle/working/submission.csv`.
- Format: pass in Run-mode; output shape `(120,235)`.
- Row order: pass for dry-run train-like rows; hidden code follows `sample_submission.csv` order through the notebook's output construction.
- Class order: pass; columns match `sample_submission.csv`.
- NaN/inf: pass; archived output is finite.
- Range: pass; archived output range is `[0.011422446, 0.99943465]`.
- Artifact provenance: pass; candidate is a workspace-original v86/v102/v103 line with attribution recorded in `ATTRIBUTION.md`, `v103_runmode_status.md`, and `v103_submission_decision_brief.md`.
- External provenance: partial. `rishikeshjani/perch-onnx-for-birdclef-2026` is CC0-1.0 and Google Perch model is Apache 2.0, but `jaejohn/perch-meta` and `tuckerarrants/bc2026-distilled-sed-public` return license `unknown` in Kaggle metadata.
- Private sharing: pass; no team-external private artifact sharing.
- Human labeling/test leakage: pass; no manual test listening, no human labels, no hidden-test leakage.
- Public-LB-only tuning: pass; v103 was chosen from local Run-mode/proxy evidence and original mechanism, not public LB weight fitting.

## Decision

Do not submit v103 as-is. v101 no longer blocks submission, but v103 still requires a final license-risk decision or a license-clean variant before it can be treated as a final/prize-route candidate.

## Next Automatic Action

Keep v103 as the strongest original Run-mode evidence. Since v101 underperformed, either:

- submit v103 only as a guarded non-final probe after explicitly accepting the unknown-license risk; or
- preferably build a v104/v105 license-reduced original branch that removes or replaces the unknown-license cache/SED dependencies before real submission.
