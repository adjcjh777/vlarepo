# DECISION_LOG

## 2026-05-18 Phase 0
- Checked working directory: `/Users/junhaocheng/working-dir/kaggle-auto`.
- Did not run `git pull`.
- Did not push to any remote.
- Confirmed the dedicated skill path exists and is readable: `/Users/junhaocheng/working-dir/kaggle-auto/birdclef-2026/agentic-data-science-competition`.
- Read dedicated skill core files and BirdCLEF extension content.
- Noted that project directory is inside a broader `/Users/junhaocheng` git root and appears untracked from that root; no checkpoint commit was made because staging the full home-level untracked project would be unsafe.
- Initialized local control directories and ledgers for autonomous execution.
- Decision: continue to Phase 1 artifact audit, preserving all existing local files.

## 2026-05-18 Phase 1/1C/2
- Generated low-cost repository and artifact inventories.
- Built full artifact registry and schema reports.
- Found 13 submission/test-prediction CSVs; 12 have sample-compatible class columns and valid numeric range.
- Flagged `birdclef-2026/outputs/v87-attributed-nina-eos5-v38plus/submission.csv` as unsafe due NaN/numeric issues.
- Diagnosed v87 OOF cache: `oof_base` mean AUC `0.79594742`, `oof_prior` mean AUC `0.60316009`, with 70 scorable classes and 164 skipped classes.
- Refreshed Kaggle state at `2026-05-18 10:56 UTC`: v87 is complete with public score `0.949`; today visible submissions are `4/5`; top20/top5 cutoffs are `0.953/0.958`; `GOAL_GATE=NOT_REACHED`.
- Decision: v87 improves the visible anchor by `0.001` but is not top20 progress; do not spend the final slot on EoS5/S106 near-duplicates.

## 2026-05-18 v88 Run-Mode Preparation
- Materialized `v88-attributed-zeyad-eos-parity-t3` from the EOS Parity T3 public reference with explicit attribution.
- Initial Kaggle kernel push failed with `403 Forbidden` because source metadata retained `id_no`.
- Removed `id_no` from v88 metadata and patched `birdclef_prepare_eos_t3.py` to drop it during future materialization.
- Retried Kaggle kernel push successfully; v88 version 1 is running in Kaggle Run-mode.
- Decision: no real submission until v88 Run-mode completes and passes output, runtime, provenance, and material-difference checks.

## 2026-05-18 v88 Waiting Audit
- Refreshed state at `2026-05-18 10:59 UTC`: v88 remains `KernelWorkerStatus.RUNNING`; `GOAL_GATE=NOT_REACHED`; best visible score remains `0.949`; top20/top5 cutoffs remain `0.953/0.958`.
- Added `scripts/audit_v88_runmode.py` to fetch outputs after completion, validate `submission.csv`, parse runtime, and compare v88 with v87 references by overlapping `row_id` and class columns.
- Ran the audit script while v88 was still running; it correctly wrote `experiments/v88_runmode_status.md` with decision `Wait`.
- Added `experiments/v88_static_audit.md`; static checks confirm CPU/no-internet metadata, BirdNET disabled by default, T3 `QUANTILE_MIX_ALPHA=0.5`, `RANK_MODE=\"blend\"`, four EOS variants, final finite/range/row/column assertions, and dry-run sample alignment.
- Decision: keep the fifth real submission locked while v88 is running.

## 2026-05-18 v88 Submission Gate
- v88 Run-mode completed and outputs were fetched.
- `submission.csv` schema is valid: 3 rows, 235 columns, sample column order and row order match, no NaN/inf, range `[0.24237677, 0.4825965]`.
- Run-mode log reaches notebook conversion at about `348.7s`, under the 90-minute CPU cap.
- Local overlap with v87 sample-aligned output is materially different: Pearson `0.27456720`, MAD `0.204218783333`.
- Current UTC-day visible submissions before v88 remain `4/5`; v87 best is `0.949`; top20/top5 cutoffs are `0.953/0.958`.
- Decision: submit v88 as the fifth UTC-day slot after guarded dry-run passes; do not submit anything else today after v88.

## 2026-05-18 v88 Submitted
- Guarded submit dry-run passed for v88: visible today count `4`, kernel status `COMPLETE`, v76 gate row found with score `0.925`, no existing v88 scored row.
- Executed guarded code submission for v88.
- Kaggle response ref: `52773123`.
- Immediate submissions refresh shows v88 at `2026-05-18 11:06:18.053000 UTC`, `SubmissionStatus.PENDING`, score blank.
- Visible UTC-day submissions are now `5/5`.
- Decision: stop all real submissions for UTC `2026-05-18`; monitor v88 result only.

## 2026-05-18 v88 Pending + Research Scan
- Refreshed v88 at `2026-05-18 11:08:07 UTC`: still `SubmissionStatus.PENDING`, score blank.
- `birdclef_goal_check.py` at `2026-05-18 11:08:08 UTC`: best visible remains `0.949`, top20/top5 cutoffs `0.953/0.958`, `GOAL_GATE=NOT_REACHED`.
- UTC-day visible submissions remain `5/5`; no more real submissions are allowed today.
- Ran `birdclef_public_scan.py --page-size 20` as non-submission research.
- Public scan confirmed high-score public references remain dominated by EoS/rank families already represented by v87/v88; do not chase S106/S114/EoS5 near-duplicates.
- Initially flagged CPU visual/aux branch (`mtoshidesu/birdclef-2026-visual-cpu-inference`, `beicicc/bc26-mtoshi-vis-may18`) as a possible watchlist, then checked metadata and local history.
- Metadata is CPU/no-internet compatible, but this visual CPU family is already represented by local v44, which prior reports rejected as a v38-family duplicate after Run-mode validation.
- Revised next-day watchlist if v88 underperforms: prioritize CNN/pseudo-label or other non-EoS metadata-gated branches, not v44/mtoshi visual duplicates.
- Wrote `experiments/research_trigger_reason.md`, `experiments/research_findings_actionable.md`, and `experiments/research_experiment_plan.md`.
- Wrote `experiments/watchlist_metadata_visual_cpu.md`.

## 2026-05-18 Metadata Gate: CNN/PL/Low-Vote Routes
- Refreshed v88 at `2026-05-18 11:14:12 UTC`: still `SubmissionStatus.PENDING`, score blank.
- `birdclef_goal_check.py` at `2026-05-18 11:14:12 UTC`: best visible remains `0.949`, top20/top5 cutoffs `0.953/0.958`, `GOAL_GATE=NOT_REACHED`.
- UTC-day visible submissions remain `5/5`; no more real submissions are allowed today.
- Rejected `alexycactus/birdclef-2026-cnn-pl-saver` for the current queue because metadata enables GPU and the notebook is closer to pseudo-label/checkpoint saving than CPU final inference.
- Promoted `alexycactus/birdclef-2026-ensemble-perch-cnn` as the only next-day non-EoS Run-mode candidate if v88 underperforms or ties; metadata is CPU/no-internet compatible, but it still requires Run-mode, runtime, schema, provenance, and correlation validation.
- Rejected `rauffauzanrambe/birdclef-26-real-load-adapter-reasoning` because metadata enables GPU and internet and depends on Gemma/adapter-style assets.
- Deferred `adkasd/birdclef-2026-sub-v4-5-strong` as idea-only backup because metadata has an empty source entry and the notebook appears broad/heavy.
- Wrote `experiments/watchlist_metadata_cnn_pl.md` and updated research plan/result files.
- Decision: keep waiting for v88; if it does not reach top20, the next automatic action after quota reset is Perch-CNN Run-mode validation, not another EoS/rank duplicate.
- Follow-up monitor at `2026-05-18 11:16:15 UTC`: v88 remains `SubmissionStatus.PENDING`; visible submissions remain `5/5`; continue waiting only.

## 2026-05-18 v89 Perch-CNN Preparation
- Follow-up monitor at `2026-05-18 11:17:14 UTC`: v88 remains `SubmissionStatus.PENDING`; visible submissions remain `5/5`; `GOAL_GATE=NOT_REACHED`.
- Pulled `alexycactus/birdclef-2026-ensemble-perch-cnn` source and metadata to `/tmp/bc26_perch_cnn_source` for static audit.
- Metadata gate passed for CPU/no-internet: `enable_gpu=False`, `enable_internet=False`, competition source includes `birdclef-2026`, dataset/model sources are declared.
- Static audit found a train-soundscapes staging fallback when `test_soundscapes` is empty; this violates the final hardening rule against train fallback.
- Added `birdclef-2026/scripts/birdclef_prepare_perch_cnn.py` to materialize an attributed local v89 candidate only; the script does not push and does not submit.
- Materialized `birdclef-2026/notebooks/v89-attributed-alexycactus-perch-cnn` with attribution and safety patches:
  - metadata rewritten to private CPU/no-internet local kernel id,
  - PyPI fallback removed under internet-disabled mode,
  - train fallback replaced by sample-aligned staging prior output,
  - duplicate row, finite value, and range assertions added.
- Verified both preparation script and v89 source with `python3 -m py_compile`.
- Reran artifact registry and phase1 inventory; v89 appears in `ARTIFACT_REGISTRY.csv`, `experiments/artifact_registry_full.csv`, and `experiments/ledger_minimal.csv`.
- Wrote `experiments/v89_static_audit.md`.
- Decision: promote v89 to Run-mode validation only; no real submission is allowed on UTC `2026-05-18`.

## 2026-05-18 Rules Compliance Guardrail Update
- Active goal was updated with explicit Rules Compliance Guardrails.
- Froze any new Run-mode/push/submission action until the guardrails were written into local controls and candidate reports.
- Refreshed v88 at `2026-05-18 11:21:17 UTC`: still `SubmissionStatus.PENDING`; visible submissions remain `5/5`; `GOAL_GATE=NOT_REACHED`.
- Kaggle CLI in this environment has no `competitions rules` subcommand; official rules page is tracked as `https://www.kaggle.com/competitions/birdclef-2026/rules`.
- Added `RULES_COMPLIANCE_GUARDRAILS.md`.
- Updated `CODEX_BUDGET_RULES.md`, `BIRDCLEF_TOP5_OBJECTIVE.md`, and `RUNBOOK_AUTONOMOUS.md` to require candidate-level rules compliance reports before real submission/final promotion.
- Wrote `experiments/rules_compliance_report_v88.md`: v88 is `HOLD` for final selection until score and external license/provenance audit complete.
- Wrote `experiments/rules_compliance_report_v89.md`: v89 is `HOLD` for real submission and may only proceed to Run-mode validation.
- Decision: continue v88 monitoring; v89 Run-mode is allowed only as validation evidence, not as a real submission, and any later real submission requires all compliance gates to become `PASS`.
- Pushed v89 to Kaggle Run-mode as kernel version 1; URL: `https://www.kaggle.com/code/junhaochengadjcjh7u7/bc26-v89-attributed-alexycactus-perch-cnn`.
- Checked status after push: v89 is `RUNNING`; v88 kernel remains `COMPLETE`, but v88 real submission remains `PENDING`.
- Added `scripts/audit_v89_runmode.py` for fetch/schema/runtime validation after v89 Run-mode completes.
- Ran `scripts/audit_v89_runmode.py` while v89 is still running; it wrote `experiments/v89_runmode_status.md` with decision `Wait`.
- Updated heartbeat automation `birdclef-v88-run-mode-monitor` to monitor both v88 submission score and v89 Run-mode completion under the new rules compliance guardrails.

## 2026-05-18 v88/v89 Wait-State Refresh
- Checked local git status before continuing; `kaggle-auto` remains inside a broader home-level git root and appears as an untracked project directory, so no broad checkpoint commit is safe.
- Refreshed v88 at `2026-05-18 11:27:07 UTC`: still `SubmissionStatus.PENDING`, score blank, visible submissions remain `5/5`.
- Refreshed v89 with `scripts/audit_v89_runmode.py`: Kaggle Run-mode still `RUNNING`; no output fetch attempted; report remains `Wait`.
- Ran `birdclef_goal_check.py` at `2026-05-18 11:27:30 UTC`: best visible remains `0.949`, top20/top5 cutoffs `0.953/0.958`, `GOAL_GATE=NOT_REACHED`.
- Decision: continue waiting only. Do not submit anything on UTC `2026-05-18`; once v89 completes, fetch outputs and update schema/runtime/compliance gates before any next-day submission decision.

## 2026-05-18 v89 External Provenance Audit
- Pulled Kaggle dataset metadata for `alexycactus/birdclef-2026-cnn-fold-checkpoints`: public Kaggle dataset metadata fetched; license `CC0-1.0`.
- Pulled Kaggle dataset metadata for `rishikeshjani/perch-onnx-for-birdclef-2026`: public Kaggle dataset metadata fetched; license `CC0-1.0`.
- Kaggle CLI `models get` hit a datetime JSON serialization bug for `google/bird-vocalization-classifier`, then Python API fallback captured the model metadata successfully.
- Verified Google Perch model metadata includes public model card, `perch_v2_cpu` CPU variant, and license `Apache 2.0`.
- Persisted provenance metadata under `experiments/provenance/v89/`.
- Wrote `experiments/v89_external_provenance_report.md`.
- Updated `experiments/rules_compliance_report_v89.md`: external data provenance gate is now `PASS-provenance`; overall v89 remains `HOLD` because Run-mode runtime/schema gates are still pending.

## 2026-05-18 v89 Run-Mode Completion and Rejection-as-Submit
- Refreshed v88 at `2026-05-18 11:32:10 UTC`: real submission remains `SubmissionStatus.PENDING`, score blank; UTC-day visible submissions remain `5/5`.
- Ran `birdclef_goal_check.py` at `2026-05-18 11:32:10 UTC`: best visible remains `0.949`, top20/top5 cutoffs remain `0.953/0.958`, `GOAL_GATE=NOT_REACHED`.
- Reran `scripts/audit_v89_runmode.py`: v89 Run-mode is `COMPLETE`, outputs are fetched, parsed runtime is `363.6s`, and `submission.csv` / `submission_no_postproc.csv` both match sample schema with no NaN/inf.
- v89 output is not competitive evidence as-is: both CSVs are all-constant staging prior predictions (`min=max=mean 0.0042735042735`) because hidden test is unavailable in Run-mode and the patched notebook correctly avoided train-soundscape fallback.
- v89 diagnostics are weak for promotion: Perch-only OOF macro-AUC `0.747827`, logit-off `0.449898`, logit-on `0.462314`; this is not a top-20-oriented signal.
- Updated artifact registry and Phase 1 inventory after v89 outputs; v89 now appears as a teacher/reference/unknown-test-pred record with runtime/schema artifacts.
- Corrected `experiments/skill_usage_report.md` to record that a generic skill was briefly opened before `goal.md` was fully read, but the dedicated BirdCLEF+ 2026 skill is the active execution authority and no generic workflow overrides were used.
- Decision: do not submit v89 as-is, even after quota reset. Keep it only as a clean CPU/no-internet/provenance base for possible future modeling changes. Continue waiting for v88 score; no more real submissions are allowed on UTC `2026-05-18`.

## 2026-05-18 v88 Final Check Before Pause
- Refreshed v88 at `2026-05-18 11:35:25 UTC`: real submission remains `SubmissionStatus.PENDING`, score blank; UTC-day visible submissions remain `5/5`.
- Ran `birdclef_goal_check.py` at `2026-05-18 11:35:26 UTC`: best visible remains `0.949`, top20/top5 cutoffs remain `0.953/0.958`, `GOAL_GATE=NOT_REACHED`.
- Updated `experiments/submission_result_v88.md` with the latest wait state and the v89 demotion rule.
- Updated heartbeat automation `birdclef-v88-run-mode-monitor` to continue every 30 minutes in the current thread and to use `experiments/v89_submission_decision_brief.md` as the v89 decision reference.
- Decision: pause active work on the external scoring blocker. The next automatic action is heartbeat-driven v88 score refresh; do not spend any real submission until UTC quota resets and a new candidate has a non-trivial prediction signal plus fresh compliance pass.

## 2026-05-18 Phase 0 Control File Completion
- Completion audit found three missing Phase 0 control files required by `goal.md`: `experiments/external_data_registry.csv`, `experiments/rules_compliance_report.md`, and `experiments/final_submission_checklist.md`.
- Created `experiments/external_data_registry.csv` with v88/v89 declared external datasets, models, and kernel sources. v89 sources with captured metadata are marked `PASS-provenance`; v88 unresolved sources are marked `HOLD-license-audit`.
- Created `experiments/rules_compliance_report.md` as the global rules compliance summary: UTC `2026-05-18` submissions are `5/5`, v88 is `HOLD`, v89 is `HOLD-as-source`, and no further real submissions are allowed today.
- Created `experiments/final_submission_checklist.md` with final-selection gates and current candidate statuses.
- Refreshed v88 at `2026-05-18 11:37:41 UTC`: real submission remains `SubmissionStatus.PENDING`, score blank; UTC-day visible submissions remain `5/5`.
- Ran `birdclef_goal_check.py` at `2026-05-18 11:37:41 UTC`: best visible remains `0.949`, top20/top5 cutoffs remain `0.953/0.958`, `GOAL_GATE=NOT_REACHED`.
- Updated `experiments/submission_result_v88.md` and `experiments/rules_compliance_report_v88.md` with the current wait/provenance state.
- Decision: Phase 0/ledger/compliance deliverables are now present; the only current blocker is the external v88 scoring queue.

## 2026-05-18 v88 External Provenance Audit
- Added `scripts/audit_v88_provenance.py` to fetch source metadata for v88 declared datasets, models, and kernel source into `experiments/provenance/v88/`.
- Ran the v88 provenance audit successfully: 11 sources audited, 5 `PASS-provenance`, 6 `HOLD-license-audit`.
- Wrote `experiments/v88_external_provenance_report.md` and normalized `experiments/external_data_registry.csv` so v88 and v89 provenance rows are tracked separately.
- Updated global and candidate compliance files: `experiments/rules_compliance_report.md`, `experiments/final_submission_checklist.md`, and `experiments/rules_compliance_report_v88.md`.
- Decision: v88 remains valid as an already-submitted pending candidate, but cannot be promoted to final judged submission until score appears and the six remaining license-audit holds are resolved.

## 2026-05-18 v88 Scored and Retired
- Refreshed v88 at `2026-05-18 12:01:17 UTC`: real submission is `SubmissionStatus.COMPLETE` with public score `0.921`; UTC-day visible submissions remain `5/5`.
- Ran `birdclef_goal_check.py` at `2026-05-18 12:01:17 UTC`: best visible remains v87 `0.949`, top20/top5 cutoffs remain `0.953/0.958`, `GOAL_GATE=NOT_REACHED`.
- Updated `experiments/submission_result_v88.md`, `experiments/submission_ledger.csv`, `experiments/rules_compliance_report.md`, `experiments/final_submission_checklist.md`, and `experiments/rules_compliance_report_v88.md`.
- Decision: retire v88/EOS Parity T3 as a submission and final-selection candidate. It is below v87 `0.949`, below top20 `0.953`, below top5 `0.958`, and even below the original-like `0.925` line. Preserve v87 as visible-best fallback; do not submit anything else on UTC `2026-05-18`; v89 remains source-only.

## 2026-05-19 v114 Self-Contained Clean Blend
- Built `birdclef-2026/notebooks/v114-v110-v113-selfblend` from the v113 clean branch and pushed Kaggle Run-mode only as `junhaochengadjcjh7u7/bc26-v114-clean-selfblend`.
- Original contribution: v114 recomputes a `v110_like` Perch-only clean fallback branch and a `v113_like` LantingGuo MelNormProbe branch inside one CPU/no-internet notebook, then blends `0.85/0.15` without mounting prior output CSVs.
- Static audit passed: private kernel, CPU-only, internet disabled, competition source present, Perch/Google model source present, LantingGuo CC0 source present, no local v110/v113 output paths in runtime code.
- Kaggle Run-mode completed at about `535.5s` before saved output and produced `submission.csv`, `v113_lantingguo_melnorm_diagnostics.csv`, `v114_branch_auc_diagnostics.csv`, and `v114_branch_summary.csv`.
- Schema passed: `120 x 235`, all finite, no duplicate row IDs, range `[0.011144, 0.999466]`.
- Proxy: `macro=0.97920102`, `micro=0.91572402`, `top1=0.23287671`, `top5=0.52054795`.
- Correlation vs v110: Pearson/Spearman `0.999594`; branch AUC delta diagnostics show `8` positive classes and `63` negative classes for the v113-like sidecar.
- Refreshed `birdclef_goal_check.py` at `2026-05-19 06:05:54 UTC`: best visible remains `0.949`, top20/top5 cutoffs `0.953/0.958`, `GOAL_GATE=NOT_REACHED`; today's UTC real submissions remain `2/5`.
- Decision: `HOLD - do not submit`. v114 is clean, self-contained, and more original than a public fork or CSV blend, but the proxy gain over v110 is microscopic and the output is too correlated with v110 to justify spending a real submission slot.

## 2026-05-19 v115-v117 Tsubasa SED Negative Result
- Audited `tsubasatech/birdclef-2026-snowflake-sed`: Kaggle metadata license `CC0-1.0`; ONNX files expose `audio [B,160000] -> logits [B,234]`.
- Built v115 as a two-model Snowflake SED ensemble plus the workspace-original train-window remap/trust/EcoProto layer. Kaggle Run-mode failed with memory exceeded after loading both SED ONNX sessions and rebuilding Perch train features.
- Built v116 as a memory-reduced single `sed_convnext-tiny_fold0.onnx` branch with the same remap/trust layer. Run-mode completed in about `489.9s`; schema passed; proxy `macro=0.85930903`, `micro=0.83251880`, `top5=0.39726027`; correlation vs v110 `0.764711`; decision `REJECT - do not submit`.
- Built v117 to isolate same-index Tsubasa ConvNeXt SED by disabling column remap. Run-mode completed in about `435.3s`; schema passed; proxy `macro=0.71214482`, `micro=0.72131755`, `top5=0.32876712`; correlation vs v110 `0.772860`; decision `REJECT - do not submit`.
- Conclusion: Tsubasa SED is compliance-clean and low-correlation but does not transfer into the current clean EcoProto final layer. Stop tuning this lane unless a new OOF-style rationale appears.
