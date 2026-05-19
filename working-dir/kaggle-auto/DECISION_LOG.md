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

## 2026-05-19 Public Scan and v118 EcoHabitat Negative Result
- Ran the latest public-kernel scan after the user requested more original innovation and less direct reference copying.
- Inspected `aiaiaiooo/birdclef2026`: metadata has GPU enabled, current Kaggle status is `ERROR`, training AUC is `nan`, and inference fails on missing `best_model.pth`; decision `REJECT-as-candidate`.
- Inspected `ommodi07/birdclef2026`: metadata has GPU and internet enabled, the notebook trains on dummy random tensors, and its output `submission.csv` is an all-zero fallback; decision `REJECT-as-candidate`.
- Converted the public "habitat/acoustic context" idea into a workspace-original v118 local probe instead of copying code: class-selective v113 rescue over v110, gated by per-class AUC deltas, support, row entropy, and branch disagreement.
- Added `birdclef-2026/scripts/birdclef_probe_v118_ecohabitat_rescue.py` and ran it successfully, writing `experiments/v118_ecohabitat_selective_probe.csv` with `1083` scored formulas.
- v118 result: no formula beats v114; best original gated formulas tie v110 macro `0.97911204`, while v114 remains `0.97920102`.
- Decision: `REJECT - do not materialize or submit v118 as-is`; preserve the negative result to avoid repeated tuning of v113 gates.
- No new real Kaggle submission was made; UTC `2026-05-19` visible submissions remain `2/5`.

## 2026-05-19 v119 Roniheka HGNet SED Negative Result
- Built `birdclef-2026/notebooks/v119-roniheka-hgnet-sed` from the clean v112/v114 line and pushed Kaggle Run-mode only as `junhaochengadjcjh7u7/bc26-v119-roniheka-hgnet-sed`.
- Original contribution: v119 treats `roniheka/birdclef-2026-a90v2-distilled-hgnet-onnx` as an auditable CC0 SED evidence source, then routes it through the workspace-owned train-window class remap, trust-strength calibration, and EcoProto/rank-launch clean blend instead of copying a public ensemble recipe.
- Static compliance passed: private kernel, CPU-only, internet disabled, BirdCLEF competition source present, Perch/Google model source present, Roniheka CC0 source present, and unknown-license `jaejohn/perch-meta` / `tuckerarrants/bc2026-distilled-sed-public` excluded from runtime inputs.
- Kaggle Run-mode completed and saved output at about `400.8s`; downloaded `submission.csv`, `v119_roniheka_hgnet_sed_remap_diagnostics.csv`, and kernel log under `birdclef-2026/outputs/v119-roniheka-hgnet-sed-v1/`.
- Schema passed for dry-run rows: `120 x 235`, sample column order matched, all finite, no duplicate row IDs, range `[0.013670, 0.999859]`.
- Proxy was weak: `macro=0.86521034`, `micro=0.87197101`, `top5=0.34246575`, below v110/v114 clean baselines.
- Correlation vs v114 was lower than prior clean self-blends (`Pearson=0.718637`, MAD `0.148267`), but the quality loss is too large to justify a real slot.
- Refreshed `birdclef_goal_check.py` at `2026-05-19 07:24:45 UTC`: best visible remains `0.949`, top20/top5 cutoffs `0.954/0.958`, `GOAL_GATE=NOT_REACHED`; today's UTC real submissions remain `2/5`.
- Decision: `REJECT - do not submit v119`; preserve as a clean negative result and stop direct Roniheka HGNet tuning unless new train-window evidence appears.

## 2026-05-19 v120 Clean Tsubasa Sidecar Guarded Submit
- Built `birdclef-2026/notebooks/v120-clean-tsubasa-sidecar` from the clean v110/v116 line and pushed Kaggle Run-mode only as `junhaochengadjcjh7u7/bc26-v120-clean-tsubasa-sidecar`.
- Original contribution: v120 recomputes a Perch-only clean anchor and a CC0 Tsubasa ConvNeXt SED sidecar inside one CPU/no-internet notebook, then emits a pre-declared `0.85/0.15` probability blend without mounting prior output CSVs.
- Static compliance passed: private kernel, CPU-only, internet disabled, competition source present, Perch CC0 source present, Tsubasa CC0 source present, Google Perch model source present, and unknown-license Perch/SED/cache inputs excluded.
- Kaggle Run-mode completed and saved output at about `683.4s`; nbconvert finished at about `696.8s`, below the 90-minute cap.
- Schema passed for dry-run rows: `120 x 235`, sample column order matched, all finite, no duplicate row IDs, range `[0.013462, 0.999145]`.
- Proxy improved over the clean branch: v120 `macro=0.98139925`, `micro=0.91435250`, `top5=0.47945205`; v114 baseline `macro=0.97920102`.
- Correlation is high but controlled vs clean anchors: vs v110 Pearson `0.994670`, vs v114 Pearson `0.994543`; vs Tsubasa sidecar Pearson `0.827078`.
- Refreshed `birdclef_goal_check.py` at `2026-05-19 07:47:21 UTC`: best visible remains `0.949`, top20/top5 cutoffs `0.954/0.958`, `GOAL_GATE=NOT_REACHED`; today's UTC real submissions were `2/5` before v120.
- Decision: `SUBMIT - guarded slot 3`; v120 is a bold clean macro-proxy candidate, not a final selection until public score is recorded.
- Real submission executed at `2026-05-19 07:49:31 UTC`, Kaggle ref `52802748`; initial status `PENDING`, public score blank. UTC `2026-05-19` visible submissions are now `3/5`.
- Refreshed at `2026-05-19 08:06 UTC`: v120 ref `52802748` is `SubmissionStatus.COMPLETE` but has no public score and reports `Your notebook requested more memory (RAM) than is available.`
- Decision update: `REJECT-memory`; retire v120 as a final/next-submit candidate. The likely issue is the double final-layer execution for sidecar plus clean anchor, so any follow-up must be single-pass or memory-reduced before another real slot.

## 2026-05-19 v121 Class-Selective Tsubasa Innovation Probe
- Built `birdclef-2026/notebooks/v121-class-selective-tsubasa` from the clean v120/v116 line and pushed Kaggle Run-mode only as `junhaochengadjcjh7u7/bc26-v121-class-selective-tsubasa`.
- Original contribution: v121 turns the Tsubasa ConvNeXt SED branch into a sparse class-selective sidecar instead of a global blend. It pre-declares 10 train-window-supported classes and applies `0.40` sidecar mix only when `tsubasa_sidecar > clean_anchor + 0.02`.
- Local probe evidence: best class-selective row `v114_v116_cls_margin-0.02_w0.4_side_gt_anchor` reached macro `0.982755`, micro `0.925888`, top5 `0.534247`, beating v120 macro `0.981399` and v114 top5 `0.520548`.
- Static compliance passed: private kernel, CPU-only, internet disabled, BirdCLEF competition source present, Perch/Google model source present, Tsubasa CC0 source present, and unknown-license Perch/SED/cache inputs excluded.
- Kaggle Run-mode completed and saved output at about `612.9s`; downloaded `submission.csv`, `v121_class_selective_tsubasa_summary.csv`, `v121_tsubasa_sidecar_remap_diagnostics.csv`, and kernel log under `birdclef-2026/outputs/v121-class-selective-tsubasa-v1/`.
- Schema passed for dry-run rows: `120 x 235`, sample column order matched, all finite, no duplicate row IDs, range `[0.011144, 0.999470]`.
- Proxy: macro `0.98275473`, micro `0.92510802`, top5 `0.53424658`.
- Correlation vs v110/v114 is very high (`0.998869` / `0.998467` Pearson), but correlation vs the raw Tsubasa sidecar is lower (`0.769061`), confirming a sparse sidecar intervention rather than a wholesale branch replacement.
- Refreshed `birdclef_goal_check.py` at `2026-05-19 08:29:52 UTC`: best visible remains `0.949`, top20/top5 cutoffs `0.954/0.958`, `GOAL_GATE=NOT_REACHED`; today's UTC real submissions remain `3/5`.
- Decision: `HOLD-memory-risk - do not submit v121 as-is`. The candidate is the best current original clean-sidecar idea, but it still uses v120's double-final-layer structure, which already failed hidden-test RAM. Next real candidate should be a single-pass v122 that injects the class-selective sidecar before the final layer and runs the final decision layer once.

## 2026-05-19 v122-v123 Single-Pass Tsubasa Follow-ups
- Built `birdclef-2026/notebooks/v122-singlepass-class-selective-tsubasa` as the memory-reduced follow-up to v121: inject the 10-class Tsubasa sidecar before the final EcoProto/rank-launch layer, then run the final layer once.
- v122 Run-mode completed at about `471.2s` before output save; schema passed; proxy `macro=0.97709863`, `micro=0.92241158`, `top5=0.58904110`; gate cells `114 / 28080`.
- v122 decision: `REJECT-quality`. It proves the single-pass memory structure can run, but the raw probability gate is too sparse because Tsubasa SED probabilities are lower-scale than the clean Perch surrogate.
- Built `birdclef-2026/notebooks/v123-rankcal-singlepass-tsubasa` to fix v122's scale mismatch: compare column-wise ranks, map Tsubasa rank order onto the clean probability distribution, then apply the same 10-class sidecar gate before one final pass.
- v123 Run-mode completed at about `474.4s` before output save; schema passed; proxy `macro=0.97921107`, `micro=0.91480745`, `top5=0.52054795`; gate cells `572 / 28080`.
- v123 correlation is too high to justify a slot: vs v110 Pearson `0.999952`, vs v114 Pearson `0.999546`; macro gain over v114 is only about `+0.000010`.
- Refreshed `birdclef_goal_check.py` at `2026-05-19 09:21:17 UTC`: best visible remains `0.949`, top20/top5 cutoffs `0.954/0.958`, `GOAL_GATE=NOT_REACHED`; today's UTC real submissions remain `3/5`.
- Decision: `HOLD-too-small-gain - do not submit v123 as-is`. Stop tuning this Tsubasa sidecar lane unless new train-window evidence appears; any future sidecar must remain single-pass and should bring materially larger proxy or diversity evidence.

## 2026-05-19 v124 Post-Final Tsubasa Negative Result
- Built `birdclef-2026/notebooks/v124-postfinal-rankcal-tsubasa` to test a final alternative for the Tsubasa lane: run the clean final layer once, then apply a lightweight post-final rank-calibrated Tsubasa sidecar on the same 10 selected classes.
- Static compliance passed: private kernel, CPU-only, internet disabled, BirdCLEF competition source present, Perch/Google model source present, Tsubasa CC0 source present, no unknown-license Perch/SED/cache inputs, and no prior output CSV mounts.
- Kaggle Run-mode completed at about `462.5s` before output save; schema passed for dry-run rows: `120 x 235`, finite values, no duplicate row IDs, range `[0.011144, 0.999470]`.
- Proxy was weak: `macro=0.97115717`, `micro=0.90281675`, `top5=0.52054795`; post-final sidecar gate cells were `555 / 28080`.
- Refreshed `birdclef_goal_check.py` at `2026-05-19 09:45:14 UTC`: best visible remains `0.949`, top20/top5 cutoffs `0.954/0.958`, `GOAL_GATE=NOT_REACHED`; today's UTC real submissions remain `3/5`.
- Decision: `REJECT-quality - do not submit v124`. The Tsubasa sidecar lane is exhausted for now: v121 was quality-strong but memory-unsafe, v122/v123 were memory-safe but not slot-worthy, and v124 is memory-safe but quality-negative.

## 2026-05-19 v125 Non-Tsubasa Class Router Probe
- Added `birdclef-2026/scripts/birdclef_probe_v125_non_tsubasa_router.py` to satisfy the innovation requirement with a workspace-owned non-Tsubasa sparse class router instead of another public-kernel-style blend.
- The probe excludes all Tsubasa branches and tests only clean non-Tsubasa side sources already run in Kaggle Run-mode: v112 Backtracking remap, v113 LantingGuo MelNorm, and v119 Roniheka HGNet.
- Mechanism: keep v110/v114 clean EcoProto anchors, compute per-class side-source AUC deltas on train soundscape windows, select the best side source per class only when it beats the anchor by a declared margin, shrink by class support, and rank-calibrate side predictions onto the anchor distribution.
- Wrote `experiments/v125_non_tsubasa_router_probe.csv` and `experiments/v125_non_tsubasa_router_class_diagnostics.csv`.
- Best row: `v114_clean_selfblend_router_m0_w0.7_rankcal`, macro `0.98060057`, micro `0.91703497`, top5 `0.52054795`, Pearson vs anchor `0.99706961`, MAD `0.00218707`, routed classes `6`.
- Routed classes: `47158son01`, `47158son13`, `47158son21`, `47158son22`, `47158son23`, `plcjay1`; routed sources are v112 and v119.
- Decision: `HOLD - do not submit`. v125 is a genuine original/non-Tsubasa innovation probe and improves v114 by about `+0.00140` local macro, but the gain is narrow, includes a 1-positive class (`plcjay1`), does not improve top5, and would need separate memory-aware notebook materialization before any real slot.

## 2026-05-19 v126 Router Robustness Probe
- Added `birdclef-2026/scripts/birdclef_probe_v126_router_robustness.py` to stress-test the v125 router under explicit support floors.
- Wrote `experiments/v126_router_robustness_probe.csv`, `experiments/v126_router_robustness_selection.csv`, and `experiments/v126_router_robustness_decision_brief.md`.
- Baseline v114 macro remains `0.97920102`. v126 best row with all 6 classes matches v125 at `0.98060057`.
- More importantly, excluding the fragile 1-positive `plcjay1` class still leaves `v126_min10_w0.7_rankcal` at macro `0.98021860`, micro `0.91700965`, top5 `0.52054795`, with 5 routed classes.
- Support>=10 routed classes: `47158son01`, `47158son13`, `47158son21`, `47158son22`, `47158son23`; sources are v112 and v119.
- Decision: `PLAN-MATERIALIZE - Run-mode only, no real submission yet`. v126 is robust enough to justify a memory-aware notebook materialization, but not a real submission before Run-mode, schema, proxy, correlation, compliance, and hidden-memory risk review pass.
- Operational note: current shell PATH does not expose `kaggle`, but the installed CLI exists at `/Users/junhaocheng/Library/Python/3.9/bin/kaggle`.

## 2026-05-19 v127 Memory-Safe Non-Tsubasa Router Materialization
- Added `birdclef-2026/scripts/birdclef_prepare_v127_memorysafe_nontsubasa_router.py` and materialized `birdclef-2026/notebooks/v127-memorysafe-nontsubasa-router`.
- v127 is intentionally separated from v126: exact v126 used v112/v119 final-output surfaces, while v127 is the notebook-compliant memory-safe adaptation that computes raw Backtracking/Roniheka side evidence inside the notebook and applies a post-final rank-calibrated router.
- Static audit passed in `experiments/v127_static_audit.md`: private, CPU-only, internet disabled, BirdCLEF competition source present, Perch/Google model source present, Backtracking and Roniheka CC0 side sources present, no Tsubasa source, no kernel sources, no prior output CSV mounts.
- Kaggle Run-mode completed in about `390.8s` through nbconvert and downloaded `submission.csv`, `v127_router_summary.csv`, `v127_router_branch_summary.csv`, and kernel log under `birdclef-2026/outputs/v127-memorysafe-nontsubasa-router-v1/`.
- Schema passed: `120 x 235`, sample column order matched, all finite, no duplicate row IDs, range `[0.01114442, 0.99946990]`.
- Proxy: macro `0.98008089`, micro `0.91595668`, top5 `0.52054795`.
- Correlation: vs v110 Pearson `0.996646`, MAD `0.002296`; vs v114 Pearson `0.996229`, MAD `0.003581`; vs side references v112/v119 Pearson `0.783987` / `0.722441`.
- Added v127 to `birdclef-2026/scripts/birdclef_guarded_submit.py` and wrote `experiments/submission_validation_report_v127.md`, `experiments/rules_compliance_report_v127.md`, and `experiments/v127_submission_decision_brief.md`.
- Refreshed `birdclef_goal_check.py` at `2026-05-19 10:24:41 UTC`: best visible remains `0.949`, top20/top5 cutoffs `0.954/0.958`, `GOAL_GATE=NOT_REACHED`; today's UTC real submissions are `3/5` before v127 and no pending row is visible.
- Decision: `SUBMIT - guarded slot 4`. v127 is not a final selection candidate yet, but it is the best current memory-safe original non-Tsubasa candidate after v120 hidden RAM failure and v122-v124 quality failures.
- Real submission executed at `2026-05-19 10:27:41.813 UTC`, Kaggle ref `52807175`; initial status `PENDING`, public score blank. UTC `2026-05-19` visible submissions are now `4/5`.
- Refreshed at `2026-05-19 10:31:57 UTC`: v127 remains `PENDING`, public score blank. `birdclef_goal_check.py` still reports best visible `0.949`, top20/top5 cutoffs `0.954/0.958`, and `GOAL_GATE=NOT_REACHED`. Do not spend the fifth slot while v127 is pending.

## 2026-05-19 v128 Pending-Safe Originality Queue
- Added `birdclef-2026/scripts/birdclef_pending_safe_candidate_queue.py` to rank existing Run-mode output artifacts without touching Kaggle submissions.
- Wrote `experiments/v128_pending_safe_candidate_queue.csv` and `experiments/v128_pending_safe_candidate_queue_decision.md`.
- Queue result: v103/v102 are still the strongest local proxy family (`v103 macro=0.98906455`, `top5=0.71232877`), but they remain blocked for direct prize-route use by unknown-license dependencies already recorded in v103 compliance.
- v121 is the strongest clean-sidecar idea but inherits the v120 hidden-RAM pattern; v120 itself is retired after hidden-test memory failure; v127 is still pending and therefore locks the fifth real slot.
- Originality decision: do not keep copying or direct-blending public work. The next useful research lane is a license-clean transfer of the v103 guard/rescue mechanism onto allowed in-notebook evidence, with row-level confidence preservation, positive-evidence rescue gating, per-class support floors, rank calibration, and memory-safe single-final-layer/post-final execution.
- Decision: `RESEARCH-NEXT - no real submission while v127 is PENDING`; prepare v128/v129 only as an original, clean, memory-safe mechanism candidate after v127 score/error is known.

## 2026-05-19 v128 Clean Rescue Transfer Probe
- Refreshed external state at `2026-05-19 10:41:17 UTC`: v127 kernel is `COMPLETE`, but competition submission ref `52807175` remains `PENDING`; best visible remains `0.949`, top20/top5 cutoffs `0.954/0.958`, `GOAL_GATE=NOT_REACHED`.
- Added `birdclef-2026/scripts/birdclef_probe_v128_clean_rescue_transfer.py` as a local-only originality probe. It transfers the v103 guard/rescue mechanism without using v103/v102 outputs in candidate construction.
- Wrote `experiments/v128_clean_rescue_transfer_probe.csv`, `experiments/v128_clean_rescue_transfer_selection.csv`, and `experiments/v128_clean_rescue_transfer_decision_brief.md`.
- Best row: `v128_v114_clean_selfblend_min5_d0_w0.9_rm0_t0.7`, macro `0.97987635`, micro `0.92085607`, top5 `0.52054795`, 6 classes, 350 active cells, Pearson vs anchor `0.99768118`.
- Interpretation: v128 improves over v114 but is weaker than v126 support>=10 (`0.98021860`) and v127 (`0.98008089`) on macro. The micro gain is interesting, but positive-only cell rescue is too conservative for the macro objective.
- Decision: `HOLD-quality - do not submit v128`; do not spend the fifth slot while v127 is pending. Next originality probe should move toward grouped clean meta-routing, support-aware full-column routing with a top5 term, or a v126/v127 follow-up after v127 score/error is known.

## 2026-05-19 v129 Blocked Clean Router Probe
- Refreshed external state at `2026-05-19 10:48:18 UTC`: v127 kernel remains `COMPLETE`, but competition submission ref `52807175` remains `PENDING`; best visible remains `0.949`, top20/top5 cutoffs `0.954/0.958`, `GOAL_GATE=NOT_REACHED`.
- Added `birdclef-2026/scripts/birdclef_probe_v129_blocked_clean_router.py` to test the clean non-Tsubasa router with leave-one-soundscape-out validation across 10 train soundscape files.
- Wrote `experiments/v129_blocked_clean_router_probe.csv`, `experiments/v129_blocked_clean_router_selection.csv`, and `experiments/v129_blocked_clean_router_decision_brief.md`.
- Best blocked row: `v129_v114_clean_selfblend_min5_d0.002_w0.35_top5guard0`, macro `0.97970207`, micro `0.91617178`, top1 `0.24657534`, top5 `0.52054795`, average selected classes/fold `3.4`, Pearson vs anchor `0.99937804`.
- Stable classes across all 10 held-out folds are `47158son13`, `47158son22`, and `47158son23`, all routed from `v112_backtracking_remap`; other classes are fold-fragile.
- Decision: `HOLD-validated-small-gain - do not submit v129`. The grouped validation supports the clean-router idea but the gain is too small and still weaker than v127/v128; keep the 3-class pattern as evidence for a future stricter router only after v127 score/error is known.

## 2026-05-19 v130 Stable-3 Router Probe
- Refreshed external state at `2026-05-19 10:55:30 UTC`: v127 kernel remains `COMPLETE`, but competition submission ref `52807175` remains `PENDING`; best visible remains `0.949`, top20/top5 cutoffs `0.954/0.958`, `GOAL_GATE=NOT_REACHED`.
- Added `birdclef-2026/scripts/birdclef_probe_v130_stable3_router.py` to isolate the stable v129 classes `47158son13/47158son22/47158son23` with clean `v112_backtracking_remap` evidence.
- Wrote `experiments/v130_stable3_router_probe.csv` and `experiments/v130_stable3_router_decision_brief.md`.
- Same-row best: `v130_v114_clean_selfblend_same_full_w0.9`, macro `0.98008650`, micro `0.91663030`, top5 `0.50684932`.
- Blocked best full-column row: `v130_v114_clean_selfblend_blocked_full_w0.35`, macro `0.97987567`, micro `0.91638119`, top5 `0.50684932`.
- Blocked top5-preserving row: `v130_v114_clean_selfblend_blocked_positive_w0.9`, macro `0.97979134`, micro `0.91924338`, top5 `0.52054795`.
- Decision: `HOLD-component - do not submit v130`. The stable 3-class structure is a useful clean component, but it is not a standalone fifth-slot candidate while v127 is pending; any follow-up should combine it with a top5-aware grouped meta-router after v127 score/error is known.

## 2026-05-19 v131 Top5-Aware Meta Router Probe
- Refreshed external state at `2026-05-19 11:02:32 UTC`: v127 kernel remains `COMPLETE`, but competition submission ref `52807175` remains `PENDING`; best visible remains `0.949`, top20/top5 cutoffs `0.954/0.958`, `GOAL_GATE=NOT_REACHED`.
- Added `birdclef-2026/scripts/birdclef_probe_v131_top5aware_meta_router.py` to search for a compact grouped clean router under a lexicographic blocked objective: preserve/improve top5 first, then macro, then micro.
- Wrote `experiments/v131_top5aware_meta_router_probe.csv`, `experiments/v131_top5aware_meta_router_selection.csv`, and `experiments/v131_top5aware_meta_router_decision_brief.md`.
- The greedy blocked search for both `v110` and `v114` converged to the same stable 3-class positive component: `47158son13`, `47158son22`, `47158son23`, all from `v112_backtracking_remap`, all at weight `0.7`.
- Best `v114` row after 3 steps: macro `0.97979134`, micro `0.91861043`, top5 `0.52054795`. Best `v110` row after 3 steps: macro `0.97970236`, micro `0.91772625`, top5 `0.52054795`.
- A `gpt-5.3-codex-spark` explorer quick-check over the current CSV/brief set found no stronger omitted support>=10 top5-preserving clean set. The only remaining such combinations are `v119_roniheka_hgnet` on `47158son20`, `47158son21`, and `47158son25`, but they do not beat the stable `v112` triad under the current blocked objective.
- Decision: `HOLD-confirmed-component - do not submit v131`. v131 confirms the stable 3-class component is the best current top5-aware clean grouped router, but it is still weaker than v127/v126 on macro and therefore not a fifth-slot candidate while v127 remains pending.
- Follow-up decision: do not start a broad `v132` sweep now; wait for v127 score/error, and only reopen this lane with a narrow stable3-centric follow-up if v127 fails or scores poorly.

## 2026-05-19 v134 Stable3 Guarded Rescue Probe
- Added `birdclef-2026/scripts/birdclef_probe_v134_stable3_guarded_rescue.py` to test the stable3 `v112` component with a `v103`-style row-level top-hit guard.
- Wrote `experiments/v134_stable3_guarded_rescue_probe.csv` and `experiments/v134_stable3_guarded_rescue_decision_brief.md`.
- Best `v114` row: `macro=0.97979134`, `micro=0.91924338`, `top1=0.23287671`, `top5=0.52054795`, `active_cells=176`.
- Interpretation: `v134` does not beat `v131` on macro/top5, but it preserves both while slightly improving micro and gives a cleaner guarded interpretation of the stable3 route.
- Decision: `HOLD-guarded-component - do not submit v134`; treat it as the preferred local continuation over raw `v131`, while keeping today's slot 5 unused.
- Materialized `birdclef-2026/notebooks/v134-stable3-guarded-rescue` via `birdclef-2026/scripts/birdclef_prepare_v134_stable3_guarded_rescue.py`.
- Static local package check passed: notebook exists, router cell is inserted, metadata is private CPU-only/no-internet, dataset sources were reduced to Perch + Backtracking only, and `ATTRIBUTION.md` records the stable3 guarded change.
- Added `experiments/v134_static_audit.md` and `experiments/v134_runmode_status.md`.
- Decision update: `PUSH-RUNMODE-ONLY`; Run-mode is the next evidence step because v134 is a narrower, lower-risk stable3 continuation and does not consume a real submission slot.
- Pushed `birdclef-2026/notebooks/v134-stable3-guarded-rescue` to Kaggle successfully as kernel version `1`.
- Refreshed kernel status immediately after push: `junhaochengadjcjh7u7/bc26-v134-stable3-guarded-rescue` is `KernelWorkerStatus.RUNNING`.
- Decision: keep waiting for Run-mode completion; no real competition submission is attached to v134 at this stage.
- Added `scripts/audit_v134_runmode.py` and ran it after kernel completion.
- Refreshed external state: `junhaochengadjcjh7u7/bc26-v134-stable3-guarded-rescue` is now `COMPLETE`.
- Retrieved `submission.csv` and `v134_guarded_branch_summary.csv`; one auxiliary fetch hit SSL EOF, but primary output validation succeeded.
- Recorded `experiments/v134_schema_report.csv`, `experiments/v134_correlation_vs_references.csv`, `experiments/v134_runmode_status.md`, and `experiments/v134_runmode_decision_brief.md`.
- Current read: `v134` passes the external Run-mode gate and stays numerically valid, but remains very close to the `v110/v114/v127` family; keep it in the guarded pool rather than promoting it straight to a real slot.
- A `gpt-5.3-codex-spark` explorer follow-up confirmed that `v134` should be treated as `guarded pool`, not `local-only`, and that if a new slot opens it ranks ahead of `v131` because it keeps the same macro/top5 with slightly better micro and an external Run-mode pass.

## 2026-05-19 Anchor-Streak Guard
- Adopt the updated objective rule explicitly: stay on the current highest-score basis and avoid broad method-family changes until there are `5` consecutive real-submit outcomes without positive feedback over the best visible anchor.
- Current visible anchor is `v87 = 0.949`.
- Completed non-positive outcomes after that anchor: `v88=0.921`, `v91=0.948`, `v101=0.898`, `v120=ERROR-memory` -> streak count `4`.
- `v127` is the next gate result. While its Kaggle row remains `PENDING`, do not spend slot 5 on a different method family and do not reopen a broad alternative sweep.
- Practical implication: avoid another low-confidence off-family submission like the prior `0.898` Alexy CPU lane unless the streak actually reaches `5` or new evidence materially changes the guard.

## 2026-05-19 v127 Score Resolution
- Refreshed external state at `2026-05-19 11:19:58 UTC`: v127 competition row changed from `PENDING` to `SubmissionStatus.COMPLETE` with public score `0.883`; kernel status remains `COMPLETE`.
- This is a strongly negative result relative to the visible anchor `0.949`, the original-like `0.925` line, and even the prior Alexy CPU miss `0.898`.
- Update the anchor-streak guard: completed non-positive outcomes after `v87=0.949` are now `v88`, `v91`, `v101`, `v120`, `v127`, so streak count reaches `5`.
- Decision: the method-family-change gate is now unlocked, but do not spend slot 5 on a blind broad gamble. The next candidate must be high-confidence and specifically filtered to avoid another `0.883`-style collapse.

## 2026-05-19 Post-v127 Unlock Triage
- A `gpt-5.3-codex-spark` explorer quick-check after the unlock suggested three buckets: `v126`-family memory-safe follow-up as the highest current clean-family candidate, `v129` stable3 upgrades as next-day/local work, and `v103/v102` clean-up as mechanism-rich but compliance-blocked work.
- After reviewing that suggestion against the actual `v127=0.883` score, do **not** promote a same-family `v126` near-neighbor into today's fifth slot. The real-score collapse from `v127` is too severe to justify another adjacent clean-router gamble on the same UTC day.
- Added `experiments/v132_post_v127_unlock_triage.md` to freeze the current policy: unlock acknowledged, but `NO-SLOT5-TODAY unless materially new evidence appears`.
- Practical decision: preserve the remaining daily slot for now; use local-only work to separate `stable3`-centric top5-aware components from broader risky families and keep `v103/v102` as compliance-cleanup evidence, not immediate submit candidates.

## 2026-05-19 v133 Next Candidate Scorecard
- Added `experiments/v133_next_candidate_scorecard.csv` and `experiments/v133_next_candidate_scorecard.md` to turn the post-`v127` situation into a reusable anti-collapse ranking.
- Ranking logic: filter known collapse branches first, then rank by `macro` lift, top5 preservation, grouped stability, compliance debt, and recent same-family collapse risk.
- Current order:
  - `v131_stable3_top5aware` as the highest-priority local continuation;
  - `v129_blocked_clean_router` as backup local continuation;
  - `v126_min10_w0.7_rankcal` as proxy-strong but same-family-risky;
  - `v103/v102` as high-value mechanism evidence but compliance-blocked;
  - `v104/v105` retired.
- Decision remains `NO-SLOT5-TODAY`; next real-candidate window should start from the stable3 component, not another broad near-neighbor of `v127`.

## 2026-05-19 v135 Next Window Runbook
- Current external state still shows UTC `2026-05-19`, visible real submissions today remain `4`, and best visible anchor remains `0.949`.
- Added `experiments/v135_next_window_runbook.md` to freeze the exact next-window procedure instead of reopening more same-day exploration.
- Key policy: wait for the UTC reset, rebuild the anti-collapse scorecard, re-confirm `v134` guarded-pool rank `#1`, and only then decide whether it should be promoted to a real-submit candidate.
- Fallback order is fixed as `v134 -> v131 -> v129 -> (only after compliance cleanup) v103/v102`; `v126` stays below that line until it earns a stronger anti-collapse screen than the current same-family evidence.

## 2026-05-19 v136 Next Window Gate
- Added `scripts/check_v134_next_window_gate.py` to make the next-window promotion rule executable instead of manual.
- Wrote `experiments/v136_next_window_gate_status.md` from the current state.
- Current gate output:
  - UTC day: `2026-05-19`
  - visible submissions today: `4`
  - top guarded candidate: `v134_stable3_guarded_rescue`
  - `v134` kernel status: `COMPLETE`
  - decision: `WAIT-SAME-UTC-DAY`
- Practical implication: even though `v134` is now the guarded-pool leader with completed Run-mode evidence, the correct move before UTC rollover is still to preserve the final same-day slot.
- Refreshed again at `2026-05-19 12:17:49 UTC`: gate decision is still `WAIT-SAME-UTC-DAY`; leaderboard gate remains `NOT_REACHED` with visible best `0.949` and top20/top5 cutoffs `0.954/0.958`.
- A `gpt-5.3-codex-spark` explorer rechecked the current guarded pool and found no candidate that should be inserted ahead of `v134`. Current guidance remains: keep waiting for the next UTC window rather than spending slot 5 today.
- Refreshed again at `2026-05-19 12:20:32 UTC`: gate is still `WAIT-SAME-UTC-DAY`, visible submissions today remain `4`, and `v134` remains the top guarded candidate. `birdclef_goal_check.py` still reports best visible `0.949`, top20/top5 cutoffs `0.954/0.958`, `GOAL_GATE=NOT_REACHED`.
- Practical implication unchanged: stay idle on real submissions until the UTC day changes.
