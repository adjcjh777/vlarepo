# BirdCLEF+ 2026 Goal Tracker

Updated: 2026-05-24 10:46 UTC

## Current Target

- Objective: move from the visible `0.949` anchor toward a private-robust Top-5 candidate.
- Current visible best: `0.949` (`v298`, tied with earlier high-anchor routes).
- Current Top20 cutoff: `0.956`.
- Current Top5 cutoff: `0.960`.
- Current gap to Top20: `0.007`.
- Current gap to Top5: `0.011`.
- Latest goal check: `2026-05-24 11:31:31 UTC`; `GOAL_GATE=NOT_REACHED`.

## v357 Exact-row Branch Candidate Triage

- Experiment: `v357-exactrow-branch-candidate-triage`
- Status: `HOLD-no-usable-exactrow-branch-sidecar / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v357_exactrow_branch_candidate_triage.py`
- Report: `experiments/v357_exactrow_branch_candidate_triage_20260524.md`
- Structured log: `artifacts/runtime_v357_exactrow_branch_candidate_triage_20260524.json`
- Output: `experiments/v357_exactrow_branch_candidate_triage_20260524.csv`
- Research question: after v351/v356 ruled out exact-variant and top-OOF reuse routes, do any existing v87-v94/v347/v351 exact-row output families still contain a non-identical current sample/test-row branch sidecar whose parent route is not already rejected as a visible-score collapse?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v357_exactrow_branch_candidate_triage.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v357_exactrow_branch_candidate_triage.py`
- Result: 12 output families and 29 sidecars audited in `0.59s`; decisions were `BLOCK-not-current-sample-rows=25` and `HOLD-identical-to-final=4`. No sidecar reached `FOLLOWUP-exactrow-diverse-branch`.
- Evidence: all ProtoSSM/SED/BirdNET sidecars in v87/v88/v90/v91/v92/v93/v94/v347/v351 are train-window diagnostic rows; the only current sample/test-row branch files are v351's `submission_v87_eos5.csv`, `submission_v87_karnak_power.csv`, `submission_v87_final.csv`, and v89's `submission_no_postproc.csv`, all with MAD `0.0` and `top5_changed_rows=0` versus their final submissions.
- Decision: stop mining old exact-row sidecars. Do not push or submit. The next useful route must actively recompute a CPU/no-internet SED/Proto-like source on hidden/test rows before another source-agreement candidate is considered.

## v358 Active Recompute Patch-point Audit

- Experiment: `v358-active-recompute-patchpoints`
- Status: `READY-v91-active-source-export-materialization / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v358_active_recompute_patchpoints.py`
- Report: `experiments/v358_active_recompute_patchpoints_20260524.md`
- Structured log: `artifacts/runtime_v358_active_recompute_patchpoints_20260524.json`
- Output: `experiments/v358_active_recompute_patchpoints_20260524.csv`
- Research question: after old sidecars proved unusable, which active CPU/no-internet notebook is the safest next target for an exact-row SED/Proto source exporter that recomputes on current test rows?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v358_active_recompute_patchpoints.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v358_active_recompute_patchpoints.py`
- Result: 6 active notebooks audited in `0.06s`. Decision counts: `READY-preferred-v91-active-source-export-patch-NO-PUSH-NO-SUBMIT=1`, `READY-secondary-v90-active-source-export-patch-NO-PUSH-NO-SUBMIT=1`, `HOLD-feasible-but-less-preferred=1`, `HOLD-not-ready-for-exact-source-export-patch=3`.
- Preferred target: `v91-attributed-youssef-e1-rare-tail-nobirdnet` with feasibility score `131`, CPU/no-internet metadata, active `test_soundscapes` inference, ProtoSSM and SED test arrays, final sample-row alignment/guard, and no v90 BirdNET runtime dependency. Patch anchor line is `2100` in the joined notebook source.
- Risk: v91 still contains dry-run `train_soundscapes` fallback. Any v359 materializer must write exact-row `submission_protossm_exact.csv` and `submission_sed_exact.csv` only when row ids match `sample_submission.csv` and the source arrays came from non-fallback `test_paths`; otherwise it must fail closed and write no source sidecar.
- Decision: prepare v91 local materializer and static audit next. Do not push or submit until exact-row guards, source-array provenance, runtime, and Run-mode schema proof are verified.

## v359 v91 Exact Source Export Materialization

- Experiment: `v359-v91-exact-source-export-materialization`
- Status: `PREPARED-local-v91-exact-source-export / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_prepare_v359_v91_exact_source_export.py`
- Notebook dir: `birdclef-2026/notebooks/v359-v91-exact-source-export`
- Report: `experiments/v359_v91_exact_source_export_materialization_20260524.md`
- Structured log: `artifacts/runtime_v359_v91_exact_source_export_materialization_20260524.json`
- Lineage log: `artifacts/lineage_v359_v91_exact_source_export_materialization_20260524.json`
- Output: `experiments/v359_v91_exact_source_export_materialization_20260524.csv`
- Research question: can the v91 CPU/no-internet active notebook be materialized into a fail-closed exact-row ProtoSSM/SED source exporter, without ever exporting train-window fallback rows as hidden-test sources?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_prepare_v359_v91_exact_source_export.py && python3 birdclef-2026/scripts/birdclef_prepare_v359_v91_exact_source_export.py && python3 birdclef-2026/scripts/birdclef_prepare_v359_v91_exact_source_export.py --execute --overwrite`
- Result: local notebook materialized with kernel id `junhaochengadjcjh7u7/bc26-v359-v91-exact-source-export`; metadata is CPU/no-internet/no-TPU; patch marker is present; intended exact source exports are `submission_protossm_exact.csv` and `submission_sed_exact.csv`.
- Guard: the patch writes no exact source sidecars when `test_soundscapes` is absent, refuses any `_Train_` row id, requires final `submission.csv` and source branch rows to match `sample_submission.csv`, and checks finite `[0,1]` probabilities.
- Decision: local materializer prepared only. No Kaggle push or competition submission is authorized until static and Run-mode source/schema gates pass.

## v360 v359 Static Source Export Audit

- Experiment: `v360-v359-static-source-export`
- Status: `READY-v359-runmode-source-export-audit / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v360_v359_static_source_export.py`
- Report: `experiments/v360_v359_static_source_export_20260524.md`
- Structured log: `artifacts/runtime_v360_v359_static_source_export_20260524.json`
- Output: `experiments/v360_v359_static_source_export_20260524.csv`
- Research question: does the v359 v91 materializer contain the required fail-closed exact-row source-export guards before any Kaggle Run-mode push?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v360_v359_static_source_export.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v360_v359_static_source_export.py`
- Result: 16 static checks passed with `block_count=0`. Checks include CPU/no-internet metadata, competition source, new kernel id, patch after final write, exact source export filenames, dry-run fail-closed branch, `_Train_` row refusal, sample-row guard, final-submission guard, finite/range guard, source dataframe export from live notebook state, summary JSON, and no push/submit calls.
- Decision: v359 is ready for Kaggle Run-mode source/schema proof only. It is not a scoring candidate and must not be real-submitted.

## v361 v359 Run-mode Push and Waiting Gate

- Experiment: `v361-v359-runmode-push-and-wait`
- Status: `READY-v359-runmode-failclosed-source-export-proof / NO-COMPETITION-SUBMIT`
- Push gate: `scripts/push_v359_after_v360_gate.py`
- Run-mode audit: `scripts/audit_v359_runmode.py`
- Push status: `experiments/v359_after_v360_push_gate_status.md`
- Run-mode status: `experiments/v359_runmode_status.md`
- Structured logs: `artifacts/runtime_v359_runmode_status.json`, `artifacts/lineage_v359_runmode_status.json`
- Research question: after v360 static readiness, can v359 be safely pushed to Kaggle Run-mode for source/schema proof without making a real competition submission?
- Validation: `python3 -m py_compile scripts/push_v359_after_v360_gate.py scripts/audit_v359_runmode.py && python3 scripts/push_v359_after_v360_gate.py --write && python3 scripts/push_v359_after_v360_gate.py --write --execute && python3 scripts/audit_v359_runmode.py --fetch-if-complete --write`
- Result: dry gate returned `READY-push-v359-runmode` with `live_pending_count=0`, `utc_today_visible_kaggle_count=2`, CPU/no-internet/no-TPU metadata, and v360 decision `READY-v359-runmode-source-export-audit-NO-SUBMIT`. Execute then pushed kernel version 1 for `junhaochengadjcjh7u7/bc26-v359-v91-exact-source-export`. Final audit at `2026-05-24 12:04:56 UTC` reports Kaggle status `COMPLETE`, fetched output `True`, runtime `264s`, schema-valid `submission.csv`, no traceback, and summary reason `fail_closed_no_test_soundscapes`.
- Decision: no real competition submission was made. v359 proves the fail-closed guard is safe and runtime-safe, but it did not produce active exact-row source sidecars, so it is not a candidate source.

## v362 v92 Backup Source Export Readiness

- Experiment: `v362-v92-backup-source-export-readiness`
- Status: `READY-v92-backup-source-export-materialization / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v362_v92_backup_source_export_readiness.py`
- Report: `experiments/v362_v92_backup_source_export_readiness_20260524.md`
- Structured log: `artifacts/runtime_v362_v92_backup_source_export_readiness_20260524.json`
- Output: `experiments/v362_v92_backup_source_export_readiness_20260524.csv`
- Research question: if v359 completes without usable active exact-row source sidecars, is v92 ready to become the backup fail-closed exact ProtoSSM/SED source-export materializer?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v362_v92_backup_source_export_readiness.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v362_v92_backup_source_export_readiness.py`
- Result: 13 readiness checks passed with `block_count=0`. v92 has CPU/no-internet metadata, active test discovery with dry-run fallback, ProtoSSM and SED branch writes before blend, branch dataframes available for a v359-style final export patch, final `submission.csv` write at joined-source line `2405`, and final sample-row guard at line `2456`.
- Decision: keep v92 as backup materializer only. Do not materialize or push it while v359 Run-mode proof is still running; if v359 completes without active exact-row sidecars, v92 can be materialized with the same fail-closed exact source export patch and then statically audited before any Run-mode push.

## v363 v359 Source Gate Consumer

- Experiment: `v363-v359-source-gate`
- Status: `HOLD-v359-failclosed-no-active-source-sidecars / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v363_v359_source_gate.py`
- Report: `experiments/v363_v359_source_gate_20260524.md`
- Structured log: `artifacts/runtime_v363_v359_source_gate_20260524.json`
- Output: `experiments/v363_v359_source_gate_20260524.csv`
- Research question: once v359 Run-mode outputs are fetched, do its exact-row ProtoSSM/SED source sidecars provide non-identical, schema-safe source diversity worth a downstream local source-agreement experiment?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v363_v359_source_gate.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v363_v359_source_gate.py`
- Result: v359 output has schema-valid `submission.csv` and summary `fail_closed_no_test_soundscapes`, but no `submission_protossm_exact.csv` or `submission_sed_exact.csv`; decision counts are `WAIT-missing-source-sidecar=2`.
- Decision: do not keep polling v359 for exact sidecars. v359 is a safe fail-closed proof only; materialize the v92 backup source-export route next.

## Active Experiment

| Field | Value |
| --- | --- |
| experiment_id | `v299-context-frontier-swap` |
| research_question | Can a tiny context-frontier top5 boundary flip escape the 0.949 plateau after tail-only context movement tied? |
| files_changed | `birdclef-2026/scripts/birdclef_guarded_submit.py`, `scripts/monitor_v299_submission.py`, `birdclef-2026/GOAL_TRACKER.md`, `birdclef-2026/ledgers/experiment_ledger.jsonl` |
| validation_command | `python3 birdclef-2026/scripts/birdclef_guarded_submit.py --candidate v299 --max-today 0` |
| OOF Macro AUC | `not_available_for_hidden_submit_gate` |
| fold std | `not_available_for_hidden_submit_gate` |
| weak-class AUC | `not_available_for_hidden_submit_gate` |
| runtime | Run-mode summary seconds `0.023`; final Kaggle code submission runtime pending if submitted |
| expert correlation | `not_available`; route is movement-constrained by top5 frontier rather than correlation-selected |
| decision | `WAIT-pending-public-score` |
| next recommended action | Monitor Kaggle ref `52973724`; do not submit another candidate while v299 is pending. |

## Submission State

- Submitted candidate: `v299-context-frontier-swap`
- Kaggle ref: `52973724`
- Submitted at: `2026-05-24 04:01:13 UTC`
- Latest monitor decision: `WAIT-pending`
- Latest monitor time: `2026-05-24 04:34:28 UTC`
- Today UTC visible submission count after submit: `1`

## Lessons Carried Forward

- Do not repeat same-anchor micro-repairs that leave public score tied at `0.949`.
- Treat public0952 window-subsampling as negative evidence after `v269=0.855` and `v270=0.875`.
- Prefer a new evaluated error structure over another zero-top5-drift tail nudge.
- Do not claim goal completion after a single audit, submit, or report.

## Pending-Only Next Candidate Prep

- Candidate: `v300-hgnet-context-frontier-veto`
- Status: `MATERIALIZED-LOCAL-ONLY / NO-PUSH / NO-SUBMIT`
- Created at: `2026-05-24 04:05:41 UTC`
- Notebook dir: `birdclef-2026/notebooks/v300-hgnet-context-frontier-veto`
- Role: HGNet-calibrated support/veto layer over the v299 context-frontier idea.
- Guard: no Kaggle push or real submission while v299 ref `52973724` is pending.
- Push gate: `WAIT-live-pending-submission` at `2026-05-24 04:28:23 UTC`; no Kaggle push allowed while pending.

## Pending-safe Offline Screening

- Experiment: `v302-pending-safe-candidate-queue`
- Status: `SCREENED-LOCAL-ONLY / NO-PUSH / NO-SUBMIT`
- Command: `python3 birdclef-2026/scripts/birdclef_pending_safe_candidate_queue.py --output-csv experiments/v302_pending_safe_candidate_queue_20260524.csv`
- Output CSV: `experiments/v302_pending_safe_candidate_queue_20260524.csv`
- Report: `experiments/v302_pending_safe_candidate_queue_20260524.md`
- Result: `24` historical/local candidates ranked while v299 remains pending.
- Best local proxy: `v103-guarded-macro-risk-rescue-v1` (`macro_auc=0.98906455`, `top5_hit=0.71232877`, `corr_v110=0.78728573`, `corr_v127=0.78461338`).
- Decision: use `v103`/`v102` only as a mechanism source for a clean macro-rescue reimplementation; do not submit queued artifacts as-is.
- Rejected direct routes: `v120`/`v121` hidden RAM or inherited Tsubasa risk; `v127`/`v134` true public LB collapse; `v110`/`v114` clean references but not aggressive enough for the Top-5 gap.
- Next recommended action: design a clean `v302` macro-rescue candidate locally, with no Kaggle push or competition submission until v299 ref `52973724` resolves.

## Pending-safe v302 Design

- Experiment: `v302-clean-macro-rescue-design`
- Status: `DESIGN-LOCAL-ONLY / NO-PUSH / NO-SUBMIT`
- Report: `experiments/v302_clean_macro_rescue_design_20260524.md`
- Mechanism to transfer: `v103`/`v102` class-wise macro-risk rescue, positive-rescue gate, row-level top-hit guard, and protected-class guards.
- Design constraint: do not inherit `v103` uncertain-license runtime dependencies; do not repeat the weak v104-v107 Perch-only simplification as a real route.
- Promotion gate: a local probe must be clean, preserve top5 materially above v107's `0.50684932`, avoid v127/v134 collapse-family behavior, and remain blocked from Kaggle actions while v299 is pending.

## Pending-safe v302 Probe

- Experiment: `v302-clean-macro-rescue-probe`
- Status: `HOLD-LOCAL-PROBE-NOT-PROMOTED / NO-PUSH / NO-SUBMIT`
- Report: `experiments/v302_clean_macro_rescue_probe_20260524.md`
- Structured log: `artifacts/runtime_v302_clean_macro_rescue_probe_20260524.json`
- Output CSVs: `experiments/v302_clean_macro_rescue_probe_20260524.csv`, `experiments/v302_clean_macro_rescue_selection_20260524.csv`, `experiments/v302_grouped_clean_macro_rescue_probe_20260524.csv`, `experiments/v302_grouped_clean_macro_rescue_selection_20260524.csv`
- v128-style best: macro `0.97987635`, micro `0.92085607`, top5 `0.52054795`, corr vs anchor `0.99768118`, runtime `16.03s`.
- v143 grouped best: macro `0.97977025`, micro `0.91906734`, top5 `0.52054795`, corr vs anchor `0.99914035`, runtime `19.41s`.
- Decision: improves clean v114 locally but fails promotion gate (`macro_gain<0.0015`, diversity correlation not `<0.97`, fold std not emitted, v299 still pending).
- Next recommended action: keep the grouped triad (`47158son13`, `47158son22`, `47158son23`) as a clean research seed and require a stricter blocked probe with per-group metrics before any materialization gate.

## Pending-safe v302 Strict Group Probe

- Experiment: `v302-strict-group-metrics`
- Status: `REJECT-PROMOTION-KEEP-AS-SEED / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v302_strict_group_metrics.py`
- Report: `experiments/v302_strict_group_metrics_20260524.md`
- Structured log: `artifacts/runtime_v302_strict_group_metrics_20260524.json`
- Outputs: `experiments/v302_strict_group_metrics_20260524.csv`, `experiments/v302_strict_group_summary_20260524.csv`
- Best anchor comparison: `v114_clean_selfblend` baseline macro `0.97920102`, top5 `0.52054795`, macro_fold_std `0.14890666`; v302 triad macro `0.97977025`, top5 `0.52054795`, macro_fold_std `0.15549943`.
- Decision: global macro/micro improve, but fold variance worsens and top5 does not move; do not materialize or submit.
- Next recommended action: only continue with a group-risk veto or a different mechanism targeting low-top5 groups.

## Pending-safe v302 Group-risk Veto

- Experiment: `v302-group-risk-veto`
- Status: `REJECT-TRIAD-FAMILY-FOR-PROMOTION / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v302_group_risk_veto.py`
- Report: `experiments/v302_group_risk_veto_20260524.md`
- Structured log: `artifacts/runtime_v302_group_risk_veto_20260524.json`
- Outputs: `experiments/v302_group_risk_veto_probe_20260524.csv`, `experiments/v302_group_risk_veto_group_metrics_20260524.csv`
- Subsets tested: `14`; promotion candidates found: `0`.
- Best macro-gain subset: full triad on `v114_clean_selfblend`, macro gain `+0.00056923`, macro fold std worsened `0.14890666 -> 0.15549943`.
- Decision: stop promotion effort on this triad family; keep only as research evidence.
- Next recommended action: switch local-only screening toward a different low-top5-group mechanism instead of further tuning the same macro-rescue triad.

## Pending-safe v303 Low-top5 Source Scan

- Experiment: `v303-low-top5-source-scan`
- Status: `MECHANISM-FOUND-NO-DIRECT-CANDIDATE / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v303_low_top5_source_scan.py`
- Report: `experiments/v303_low_top5_source_scan_20260524.md`
- Structured log: `artifacts/runtime_v303_low_top5_source_scan_20260524.json`
- Outputs: `experiments/v303_low_top5_source_scan_20260524.csv`, `experiments/v303_low_top5_source_group_metrics_20260524.csv`
- Low-top5 groups found under v114 anchor: `6`.
- Best diagnostic source: `v103-guarded-macro-risk-rescue-v1`, low_top5_delta `+0.41379310`, low_macro_delta `+0.04389379`, overall_macro_delta `+0.00986353`, corr vs anchor `0.78756350`.
- Direct promotion: rejected; v103/v102 remain mechanism teachers only due uncertain dependency/licensing path.
- Next recommended action: design a clean bounded v304 low-top5 distillation from v103/v102 behavior, targeting only the improving low groups and guarding macro on non-improving groups.

## Pending-safe v304 Low-top5 Bounded Distill

- Experiment: `v304-low-top5-bounded-distill`
- Status: `PROMISING-LOCAL-PROBE-NOT-MATERIALIZED / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v304_low_top5_bounded_distill.py`
- Report: `experiments/v304_low_top5_bounded_distill_20260524.md`
- Structured log: `artifacts/runtime_v304_low_top5_bounded_distill_20260524.json`
- Outputs: `experiments/v304_low_top5_bounded_distill_probe_20260524.csv`, `experiments/v304_low_top5_bounded_distill_group_metrics_20260524.csv`
- Best local probe: `v304_w0.7_m0_top5`, overall_macro_delta `+0.00563164`, overall_top5_delta `+0.01369863`, low_top5_delta `+0.03448276`, active_cells `90`, corr vs anchor `0.99948206`.
- Gate: clears macro and low-top5 local thresholds, but does not clear diversity, final runtime, materialization, or v299-pending gates.
- Next recommended action: prepare a clean v304 materialization plan that hard-codes the bounded low-group rule without shipping v103 as a runtime dependency.

## Pending-safe v304 Materialization Gate

- Experiment: `v304-materialization-gate`
- Status: `WAIT-v299-pending-REJECT-current-v304-materialization / NO-PUSH / NO-SUBMIT`
- Gate script: `scripts/decide_v304_materialization.py`
- Gate status: `experiments/v304_materialization_gate_status.md`
- Structured log: `artifacts/runtime_v304_materialization_gate.json`
- Plan: `experiments/v304_clean_materialization_plan_20260524.md`
- Decision: do not materialize the current v304 rule because it depends on local train soundscape group names and is not yet a deployable hidden-test inference rule.
- Next recommended action: convert the low-top5 behavior into deployable inference-time features before any notebook materialization.

## Pending-safe v305 Deployable Low-top5 Proxy

- Experiment: `v305-deployable-low-top5-proxy`
- Status: `PROMISING-DEPLOYABLE-PROXY-NOT-MATERIALIZED / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v305_deployable_low_top5_proxy.py`
- Report: `experiments/v305_deployable_low_top5_proxy_20260524.md`
- Structured log: `artifacts/runtime_v305_deployable_low_top5_proxy_20260524.json`
- Outputs: `experiments/v305_deployable_low_top5_proxy_probe_20260524.csv`, `experiments/v305_deployable_low_top5_proxy_group_metrics_20260524.csv`
- Best local proxy: `v305_S09_hour00_or_S08_hour07_w0.7_m0.03_top5`, overall_macro_delta `+0.00584333`, overall_top5_delta `+0.02739726`, low_top5_delta `+0.06896552`, corr vs anchor `0.99882109`.
- Gate: row-id site/hour rule is deployable, but clean notebook still must remove v103 runtime dependency and v299 remains pending.
- Next recommended action: design v305 clean notebook rule using v114 internal signals or bounded learned constants, then run materialization gate.

## Pending-safe v306 Clean Constant Rule

- Experiment: `v306-clean-constant-low-top5-rule`
- Status: `REJECT-CLEAN-CONSTANT-RULE / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v306_clean_constant_low_top5_rule.py`
- Report: `experiments/v306_clean_constant_low_top5_rule_20260524.md`
- Structured log: `artifacts/runtime_v306_clean_constant_low_top5_rule_20260524.json`
- Outputs: `experiments/v306_clean_constant_low_top5_rule_probe_20260524.csv`, `experiments/v306_clean_constant_low_top5_rule_group_metrics_20260524.csv`
- Best constant rule: low_top5_delta `+0.20689655`, overall_top5_delta `+0.09589041`, but overall_macro_delta `+0.00000000`; promotion candidates found `0`.
- Decision: static row-id + class-set + anchor-rank constants remove v103 runtime dependency but lose the macro gain; do not materialize.
- Next recommended action: probe v114 internal signals such as branch disagreement, row uncertainty, rank margin, and SED trust diagnostics.

## Pending-safe v307 Internal Signal Low-top5 Probe

- Experiment: `v307-internal-signal-low-top5`
- Status: `REJECT-INTERNAL-SIGNAL-PROBE / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v307_internal_signal_low_top5.py`
- Report: `experiments/v307_internal_signal_low_top5_20260524.md`
- Structured log: `artifacts/runtime_v307_internal_signal_low_top5_20260524.json`
- Outputs: `experiments/v307_internal_signal_low_top5_probe_20260524.csv`, `experiments/v307_internal_signal_low_top5_group_metrics_20260524.csv`
- Candidates tested: `720`; promotion candidates found: `0`.
- Best macro-preserving candidate: `v307_S09_hour00_or_S08_hour07_max_v110_v113_k80_w0.35_m0.03`, overall_macro_delta `+0.00000000`, low_top5_delta `+0.00000000`, corr_vs_anchor `0.99950246`.
- Best low-top5 candidate: `v307_S09_hour00_or_S08_hour07_max_v110_v113_k40_w0.9_m0.01`, low_top5_delta `+0.06896552`, overall_top5_delta `+0.01369863`, but overall_macro_delta `-0.00042862`.
- Decision: clean v114 internal branch signals do not reproduce v305's macro gain; do not materialize or submit.
- Next recommended action: keep v305 as mechanism evidence and v306/v307 as negative controls; continue only with local-only deployable calibration or wait for v299 resolution.

## Pending-safe v308 Class Branch Router Probe

- Experiment: `v308-class-branch-router`
- Status: `REJECT-CLASS-BRANCH-ROUTER / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v308_class_branch_router.py`
- Report: `experiments/v308_class_branch_router_20260524.md`
- Structured log: `artifacts/runtime_v308_class_branch_router_20260524.json`
- Outputs: `experiments/v308_class_branch_router_probe_20260524.csv`, `experiments/v308_class_branch_router_selection_20260524.csv`, `experiments/v308_class_branch_router_group_metrics_20260524.csv`
- Candidates tested: `875`; promotion candidates found: `0`.
- Best candidate: `v308_s3_dd0_ed0_n13`, selected classes `13`, overall_macro_delta `+0.00002475`, overall_top5_delta `+0.00000000`, macro_fold_std_delta `+0.00000000`, corr_vs_anchor `0.99999987`.
- Decision: v114 already absorbs nearly all useful v110/v113 class-level branch signal; do not materialize or submit.
- Next recommended action: stop pure v114 internal-branch routing; continue only with a different deployable signal family or wait for v299 resolution.

## v299 Score Resolution

- Experiment: `v299-context-frontier-swap`
- Status: `HOLD-tie-anchor / NO-FURTHER-SIBLING-REPEAT`
- Submission ref: `52973724`
- Monitor: `experiments/v299_score_monitor_status.md`
- Result: `experiments/submission_result_v299.md`
- Latest check: `2026-05-24 05:25:03 UTC`
- Kaggle status: `SubmissionStatus.COMPLETE`
- Public score: `0.949`
- Decision: tied the visible anchor; preserve as evidence but do not repeat this context-frontier route blindly.

## v300 After-v299 Run-mode Proof

- Experiment: `v300-hgnet-context-frontier-veto`
- Status: `REJECT-v300-openvino-scoring-risk / RUNMODE-COMPLETE / NO-REAL-SUBMIT`
- Push gate: `experiments/v300_after_v299_push_gate_status.md`
- Run-mode audit: `experiments/v300_runmode_status.md`
- Latest push gate decision: `PUSHED-v300-runmode` at `2026-05-24 05:25:29 UTC`
- Latest audit decision: `REJECT-v300-openvino-scoring-risk` at `2026-05-24 05:43:16 UTC`
- Evidence: Run-mode completed with schema pass, but `mode=hidden_no_hgnet_supported_frontier`, `sidecar_active=False`, `swap_rows=0`, `changed_cells=0`, `top5_changed_rows=0`, and log flag `openvino_import=True`.
- Guarded-submit dry-run: refused at `2026-05-24 05:45:53 UTC` with failed fields `decision_ready`, `no_openvino_scoring`, `top5_frontier_active`, `tiny_rows`, `active_cells`.
- Decision: retire v300 as a scoring candidate; no competition submission has been made.

## v298 Taxonomy-context Submission Monitor

- Experiment: `v298-taxonomy-context-swap`
- Status: `WAIT-pending-public-score / REAL-SUBMIT-DISPATCHED / NO-SECOND-SUBMIT-WHILE-PENDING`
- Materialization gate: `experiments/v298_materialization_gate_status.md`
- Prepare status: `experiments/v298_prepare_gate_status.md`
- Push gate: `experiments/v298_after_v289_push_gate_status.md`
- Run-mode audit: `experiments/v298_runmode_status.md`
- Score monitor: `experiments/v298_score_monitor_status.md`
- Submission result: `experiments/submission_result_v298.md`
- Materialization: `MATERIALIZED-v298-local-only` at `2026-05-24 05:29:13 UTC`
- Push gate decision: `PUSHED-v298-runmode` at `2026-05-24 05:29:42 UTC`
- Latest audit decision: `READY-v298-runmode-taxonomy-context-review` at `2026-05-24 05:47:18 UTC`
- Latest push gate refresh: `WAIT-v298-runmode-audit` at `2026-05-24 05:45:53 UTC`; repeated Run-mode push is blocked.
- Guarded-submit ref: `52976043` at `2026-05-24 05:48:20 UTC`.
- Latest monitor: `WAIT-pending` at `2026-05-24 05:56:06 UTC`; public score is still blank.
- Guard: do not submit another candidate while v298 is pending. Use the wait window for local-only screening and design only.

## v298/v300 Guarded-submit Preflight Hardening

- Experiment: `v298-v300-guarded-submit-preflight`
- Status: `HARDENED-WAIT-RUNNING / NO-REAL-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_guarded_submit.py`
- Change: added vetted candidate entries and candidate-specific preflight checks for `v298` and `v300`.
- Validation:
  - `python3 -m py_compile birdclef-2026/scripts/birdclef_guarded_submit.py`
  - `python3 birdclef-2026/scripts/birdclef_guarded_submit.py --candidate v298 --max-today 5`
  - `python3 birdclef-2026/scripts/birdclef_guarded_submit.py --candidate v300 --max-today 5`
- Result: both dry-runs refused before any submission because Kaggle reports candidate status `{"status": "RUNNING", "failureMessage": ""}`.
- Guard: when Run-mode later completes, v298/v300 still require READY audit decisions, clean schema, no pending submissions, and candidate-specific movement/risk checks before any guarded submit.

## v298 Run-mode Push Gate Repeat-guard

- Experiment: `v298-runmode-push-repeat-guard`
- Status: `HARDENED-WAIT-AUDIT / NO-PUSH / NO-SUBMIT`
- Script: `scripts/push_v298_after_v289_gate.py`
- Change: added `previous_push_decision` and `WAIT-running` handling so an already-pushed v298 Run-mode proof cannot be pushed again while audit status is pending.
- Validation: `python3 -m py_compile scripts/push_v298_after_v289_gate.py && python3 scripts/push_v298_after_v289_gate.py --write`
- Result: gate now reports `WAIT-v298-runmode-audit` with reason `v298 Run-mode is already running`.

## v301 OpenVINO Runtime-smoke Validation Refresh

- Experiment: `v301-openvino-runtime-smoke-validation-refresh`
- Status: `ALLOW-VALIDATION-ONLY-DESIGN-REFRESHED / NO-PUSH / NO-SUBMIT`
- Gate: `experiments/v301_validation_gate_status.md`
- Design report: `experiments/v301_openvino_runtime_smoke_design_20260522.md`
- Gates CSV: `experiments/v301_openvino_runtime_smoke_gates_20260522.csv`
- Runtime log: `artifacts/runtime_v301_openvino_runtime_smoke_design.json`
- Lineage log: `artifacts/lineage_v301_openvino_runtime_smoke_design.json`
- Gate decision: `ALLOW-v301-validation-only` at `2026-05-24 05:40:46 UTC`
- Design refresh command: `python3 birdclef-2026/scripts/birdclef_design_v301_openvino_runtime_smoke.py`
- Decision: keep as validation-only design. It may answer future OpenVINO CPU feasibility but must not become a scoring route or real submission candidate.

## Pending-safe v309 Clean Site/hour Low-top5 Probe

- Experiment: `v309-clean-sitehour-lowtop5`
- Status: `HOLD-local-lift-too-small / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v309_clean_sitehour_lowtop5.py`
- Report: `experiments/v309_clean_sitehour_lowtop5_20260524.md`
- Structured log: `artifacts/runtime_v309_clean_sitehour_lowtop5_20260524.json`
- Outputs: `experiments/v309_clean_sitehour_lowtop5_probe_20260524.csv`, `experiments/v309_clean_sitehour_lowtop5_group_metrics_20260524.csv`
- Research question: can the deployable `S09 hour00 OR S08 hour07` slice from v305 be repaired with clean blocked-fold site/hour priors instead of v103 diagnostic-teacher output?
- Validation: `/usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v309_clean_sitehour_lowtop5.py --output-csv experiments/v309_clean_sitehour_lowtop5_probe_20260524.csv --group-csv experiments/v309_clean_sitehour_lowtop5_group_metrics_20260524.csv --report experiments/v309_clean_sitehour_lowtop5_20260524.md`
- Best candidate: `v309_a0.1_b0.05_h0.9_c0.003_ov5`, macro delta `+0.00009596`, target top5 delta `+0.00000000`, top5 overlap `1.00000000`, runtime `3.31s`.
- Decision: clean site/hour prior does not reproduce v305's promotion-level effect; do not materialize. Treat v305's gain as teacher-behavior evidence until a clean non-v103 signal is found.

## Pending-safe v310 Anti-collapse Consensus Portfolio

- Experiment: `v310-anticollapse-consensus-portfolio`
- Status: `HOLD-site-micro-negative / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v310_anticollapse_consensus_portfolio.py`
- Report: `experiments/v310_anticollapse_consensus_portfolio_20260524.md`
- Structured log: `artifacts/runtime_v310_anticollapse_consensus_portfolio_20260524.json`
- Outputs: `experiments/v310_anticollapse_consensus_portfolio_probe_20260524.csv`, `experiments/v310_anticollapse_consensus_portfolio_selection_20260524.csv`
- Research question: can previous anti-collapse/adaptive evidence sources (`v181`, `v192`, `v193`, `v198`, `v206`) form a stronger held-out-fold source-selection portfolio than a single route?
- Validation: `/usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v310_anticollapse_consensus_portfolio.py --output-csv experiments/v310_anticollapse_consensus_portfolio_probe_20260524.csv --selection-csv experiments/v310_anticollapse_consensus_portfolio_selection_20260524.csv --report experiments/v310_anticollapse_consensus_portfolio_20260524.md`
- Source status: `v181`, `v192`, `v193`, `v198` loaded; `v206` row alignment failed because its parquet lacks the later `S09` train-window rows, so it was excluded from scoring.
- Best candidate: `v310_d0_p2_w0.75_c0.035_ov4`, blocked macro delta `+0.00066477`, blocked micro delta `+0.00104159`, leave-site macro delta `+0.00000000`, leave-site micro delta `-0.00000373`, top5 delta `+0.00000000`, runtime `31.21s`.
- Decision: useful same-distribution anti-collapse signal, but cross-site stress is too weak/negative; do not materialize. Future local work should require positive leave-site movement or a hidden-test-computable independent acoustic source.

## Pending-safe v311 OOF Source Census

- Experiment: `v311-oof-source-census`
- Status: `FOLLOWUP-SOURCES-FOUND / DIAGNOSTIC-ONLY / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v311_oof_source_census.py`
- Report: `experiments/v311_oof_source_census_20260524.md`
- Structured log: `artifacts/runtime_v311_oof_source_census_20260524.json`
- Outputs: `experiments/v311_oof_source_census_20260524.csv`, `experiments/v311_oof_source_census_site_metrics_20260524.csv`
- Research question: which existing OOF artifacts remain useful under overall, low-top5, and site-stress readouts while v298 is pending?
- Validation: `/usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v311_oof_source_census.py --output-csv experiments/v311_oof_source_census_20260524.csv --site-csv experiments/v311_oof_source_census_site_metrics_20260524.csv --report experiments/v311_oof_source_census_20260524.md`
- Result: 58 sources scanned, 54 loaded, 3 low-top5 anchor groups identified, runtime `3.52s`; decision counts: `FOLLOWUP-overall-source=3`, `FOLLOWUP-site-robust-source=34`, `HOLD-anchor-identical=8`, `HOLD-no-promotion-signal=9`, `SKIP-not-loaded=4`.
- Best follow-up sources: `v150b_sparse_class_gate`, `v214_bounded_adaptive_verifier`, and `v216_spectrogram_interaction_verifier` each show overall macro delta `+0.00207367`, micro delta `+0.007169`, site min macro delta `+0.00000000`, low-top5 delta `+0.00000000`, correlation `0.99648184`, and top5 overlap `0.991667`.
- Decision: use v311 only as a source-screen. Do not materialize directly; next local experiment should isolate the mechanism shared by `v150b/v214/v216` and require top5-continuity/hidden-test-computable proof before any Run-mode path.

## Pending-safe v312 v150b Strict Revival Gate

- Experiment: `v312-v150b-strict-revival-gate`
- Status: `REJECT-STRICT-REVIVAL / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v312_v150b_strict_revival_gate.py`
- Report: `experiments/v312_v150b_strict_revival_gate_20260524.md`
- Structured log: `artifacts/runtime_v312_v150b_strict_revival_gate_20260524.json`
- Output: `experiments/v312_v150b_strict_revival_gate_20260524.csv`
- Research question: can any already-computed `v150b` sparse donor variant retain promotion-size lift after requiring top1 guard and strict top5 continuity?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v312_v150b_strict_revival_gate.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v312_v150b_strict_revival_gate.py --output-csv experiments/v312_v150b_strict_revival_gate_20260524.csv --report experiments/v312_v150b_strict_revival_gate_20260524.md`
- Result: 217 existing v150b variants audited; `ANCHOR=1`, `REJECT-top1-guard-off=72`, `HOLD-lift-too-small-under-strict-guards=144`, `PROMOTE=0`, runtime `0.52s`.
- Best strict row: `v150b_sparse_v134_stable2_w0.6_pf0_t10.7_lift0`, macro delta `+0.00032782`, micro delta `+0.00025975`, top5 overlap `1.00000000`, top1 guard enabled.
- Decision: no strict `v150b` variant clears promotion gates. Treat v150b/v214/v216 as mechanism evidence only; the visible lift depends on top1-guard-off donor movement and should not be revived as a materialization candidate without a new independently computable signal.

## Pending-safe v313 Site-robust Consensus Probe

- Experiment: `v313-site-robust-consensus`
- Status: `HOLD-watchlist-source-consensus / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v313_site_robust_consensus.py`
- Report: `experiments/v313_site_robust_consensus_20260524.md`
- Structured log: `artifacts/runtime_v313_site_robust_consensus_20260524.json`
- Output: `experiments/v313_site_robust_consensus_20260524.csv`
- Research question: can non-v150b, site-robust OOF sources identified by v311 be combined under strict top5 continuity into a promotion-sized local candidate?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v313_site_robust_consensus.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v313_site_robust_consensus.py --output-csv experiments/v313_site_robust_consensus_20260524.csv --report experiments/v313_site_robust_consensus_20260524.md`
- Result: 16 non-v150b site-robust sources loaded, 560 consensus variants scored, runtime `21.54s`; decisions: `HOLD-local-lift-too-small=556`, `HOLD-site-macro-negative=2`, `HOLD-watchlist-source-consensus=2`, `PROMOTE=0`.
- Best candidate: `v313_n4_w1_c0.02_ov5_mean_delta`, macro delta `+0.00070436`, micro delta `+0.00102163`, low-group macro delta `+0.02500000`, low-group top5 delta `+0.00000000`, site min macro delta `+0.00106753`, top5 overlap `1.00000000`, correlation `0.99999066`.
- Decision: useful weak-slice/source-consensus evidence, but it does not meet OOF macro/weak-class/diversity promotion gates. Keep as watchlist only; do not materialize or submit.

## Pending-safe v314 Acoustic Prototype Retrieval

- Experiment: `v314-acoustic-prototype-retrieval`
- Status: `HOLD-site-risk / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v314_acoustic_prototype_retrieval.py`
- Report: `experiments/v314_acoustic_prototype_retrieval_20260524.md`
- Structured log: `artifacts/runtime_v314_acoustic_prototype_retrieval_20260524.json`
- Output: `experiments/v314_acoustic_prototype_retrieval_20260524.csv`
- Research question: can a hidden-test-computable acoustic prototype signal from v216 raw spectrogram-interaction features improve the current common-row anchor under file-blocked OOF validation and strict top5 continuity?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v314_acoustic_prototype_retrieval.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v314_acoustic_prototype_retrieval.py --output-csv experiments/v314_acoustic_prototype_retrieval_20260524.csv --report experiments/v314_acoustic_prototype_retrieval_20260524.md`
- Result: 120 rows, 97 raw-audio feature dimensions, 960 prototype variants scored, runtime `53.02s`; decisions: `REJECT-top5-continuity=360`, `REJECT-overall-macro-negative=344`, `HOLD-local-lift-too-small=232`, `HOLD-site-risk=24`, `PROMOTE=0`.
- Best candidate: `v314_centroid_mp3_s0.5_w0.5_c0.02_ov5`, macro delta `+0.00027400`, micro delta `+0.00151150`, weak mean AUC delta `+0.00000000`, low-group macro delta `+0.01111112`, low-group top5 delta `+0.00000000`, site min macro delta `-0.00148990`, top5 overlap `1.00000000`, correlation `0.99770712`.
- Decision: raw handcrafted acoustic prototype retrieval is hidden-test-computable and independent, but current signal is too weak and has site risk. Do not materialize; it is evidence to prefer stronger learned/acoustic sources rather than hand-feature prototypes.

## Pending-safe v315 Learned Acoustic Source Gate

- Experiment: `v315-learned-acoustic-source-gate`
- Status: `HOLD-local-lift-too-small / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v315_learned_acoustic_source_gate.py`
- Report: `experiments/v315_learned_acoustic_source_gate_20260524.md`
- Structured log: `artifacts/runtime_v315_learned_acoustic_source_gate_20260524.json`
- Output: `experiments/v315_learned_acoustic_source_gate_20260524.csv`
- Research question: can already-audited learned acoustic sources (`BirdAves` cache head and `EffB0` sentinel) produce a promotion-sized, strict-top5, site-safe local candidate on the common-row anchor?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v315_learned_acoustic_source_gate.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v315_learned_acoustic_source_gate.py --output-csv experiments/v315_learned_acoustic_source_gate_20260524.csv --report experiments/v315_learned_acoustic_source_gate_20260524.md`
- Source status: `EffB0` loaded; `BirdAves` partially aligned with current common rows (`79/120` aligned, `41` anchor-fallback rows), with class sets of `5`, `6`, `22`, and `75` classes.
- Result: 5 learned acoustic sources/variants, 456 gated candidates, runtime `16.83s`; decisions: `HOLD-local-lift-too-small=288`, `HOLD-site-risk=3`, `REJECT-overall-macro-negative=43`, `REJECT-top5-continuity=122`, `PROMOTE=0`.
- Best unconstrained macro row: `v315_birdaves_site_auc_ge_060_plus_eff_b0.35_e0.35_c0.02_ov4`, macro delta `+0.00061425`, micro delta `+0.00031176`, but top5 overlap `0.99666667`, so it is rejected for top5 continuity.
- Best strict row: `v315_birdaves_site_auc_ge_060_plus_eff_b0.35_e0.35_c0.02_ov5`, macro delta `+0.00056890`, micro delta `+0.00027010`, weak mean AUC delta `+0.00000000`, low-group macro delta `+0.00000000`, site min macro delta `+0.00000000`, top5 overlap `1.00000000`, correlation about `0.999951`.
- Decision: learned acoustic sources add small, site-safe macro lift when strictly guarded, but remain below the OOF macro/weak-class/diversity promotion gates. Do not materialize.

## Current Blocker

- External blocker resolved: v298 ref `52976043` completed at public score `0.949`, tying the anchor but not improving toward Top5.
- Latest monitor: `HOLD-tie-anchor` at `2026-05-24 07:23:44 UTC`; public score `0.949`.
- Goal gate refresh: `GOAL_GATE=NOT_REACHED` at `2026-05-24 08:08:57 UTC`; best visible `0.949`, Top20 cutoff `0.956`, Top5 cutoff `0.960`, gap to Top5 `0.011`.
- Local state: v299 tied `0.949`, v298 tied `0.949`, v300 is terminally rejected, v309 did not produce a clean promotion candidate, v310 did not clear leave-site stress, v311 identified source-screen follow-ups but no direct materialization candidate, v312 rejects strict v150b revival, v313 leaves non-v150b site-robust consensus as watchlist only, v314 rejects handcrafted acoustic prototype retrieval, v315 keeps learned acoustic sources as below-gate evidence only, v316 creates `class_coverage.csv`, v317 has one local-review promotion row that is not yet materialized/submittable, v318 blocks direct v317 materialization from existing artifacts, v319 is now the preferred six-class local-review materializer target, v320 prepares a fail-closed local notebook shell for that exact route, v321 static audit clears v320 for Kaggle Run-mode dry-run audit, v322 pushes v320 for Run-mode proof only, v323 selects a no-context backup queue, v324 holds v320 because dry-run output made no active sidecar changes, v325 identifies v134 donor row mismatch as the source blocker, and v326 rejects v305 teacher-distilled clean branch as macro-flat.
- Action boundary: do not submit v320 or any v319-family backup that depends on v134/v193 source movement. Its Kaggle Run-mode dry-run completed with `HOLD-v320-no-active-sidecar`, and v325 shows `v134_donor` has 120 Train rows with zero overlap against current sample rows while v193 fail-closes to the anchor. Any real competition submission still requires completed output with active source-aligned movement, runtime, guard behavior, no pending submission, quota check, and guarded-submit compliance.

## Pending-safe v316 Class Coverage Audit

- Experiment: `v316-class-coverage-audit`
- Status: `LOCAL-DIAGNOSTIC-COMPLETE / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v316_class_coverage_audit.py`
- Coverage file: `birdclef-2026/class_coverage.csv`
- Report: `experiments/v316_class_coverage_audit_20260524.md`
- Structured log: `artifacts/runtime_v316_class_coverage_audit_20260524.json`
- Output: `experiments/v316_class_coverage_audit_20260524.csv`
- Research question: which weak/missing competition classes lack reliable train-soundscape, OOF-anchor, and existing-source coverage, and therefore should drive the next local candidate search while v298 is pending?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v316_class_coverage_audit.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v316_class_coverage_audit.py --coverage-csv birdclef-2026/class_coverage.csv --output-csv experiments/v316_class_coverage_audit_20260524.csv --report experiments/v316_class_coverage_audit_20260524.md --runtime-json artifacts/runtime_v316_class_coverage_audit_20260524.json`
- Result: 234 classes audited, 120 common OOF rows, 54 existing OOF sources loaded, runtime `0.87s`; decision counts: `GAP-missing-common-row-oof=212`, `GAP-low-anchor-no-source-lift=8`, `GAP-weak-oof-no-source-lift=3`, `GAP-site-fragile=1`, `FOLLOWUP-strong-existing-source=3`, `FOLLOWUP-moderate-existing-source=4`, `COVERED-no-priority-gap=3`.
- Key coverage finding: current common-row validation covers only 22 classes with positives, so many official soundscape-heavy classes such as `65380`, `517063`, `22973`, `555146`, `23158`, `24279`, `24321`, `22967`, `66971`, and `1491113` are not directly measurable by the current common-row OOF anchor.
- Existing-source follow-up classes: `47158son17`, `516975`, and `116570` have strong per-class source deltas (`>=0.006`); `47158son25`, `chacha1`, `47158son10`, and `47158son21` have moderate per-class source deltas (`>=0.0015`).
- Decision: diagnostic only; no promotion or submission. Use `class_coverage.csv` to bias the next pending-safe experiment toward one explicit mechanism: either a soundscape-label coverage expansion, or a strict per-class source gate over the 7 follow-up classes.
- Next recommended action: while v298 remains pending, run a single-mechanism v317 probe over the 7 existing-source follow-up classes with strict top5 continuity and site/file blocked stress; do not address the 212 missing-common-row classes with public-LB heuristics until a validation surface exists.

## Pending-safe v317 Coverage-guided Source Gate

- Experiment: `v317-coverage-guided-source-gate`
- Status: `PROMOTE-local-review-only / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v317_coverage_guided_source_gate.py`
- Report: `experiments/v317_coverage_guided_source_gate_20260524.md`
- Structured log: `artifacts/runtime_v317_coverage_guided_source_gate_20260524.json`
- Output: `experiments/v317_coverage_guided_source_gate_20260524.csv`
- Research question: can the seven v316 per-class follow-up signals be turned into a strict-top5, site-safe candidate without touching classes that lack a current validation surface?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v317_coverage_guided_source_gate.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v317_coverage_guided_source_gate.py --coverage-csv birdclef-2026/class_coverage.csv --source-census experiments/v311_oof_source_census_20260524.csv --output-csv experiments/v317_coverage_guided_source_gate_20260524.csv --report experiments/v317_coverage_guided_source_gate_20260524.md --runtime-json artifacts/runtime_v317_coverage_guided_source_gate_20260524.json`
- Result: 240 guarded candidates scored over 7 v316 follow-up classes, runtime `9.34s`; decisions: `PROMOTE-local-review-only=1`, `HOLD-watchlist-coverage-gate=37`, `HOLD-local-lift-too-small=194`, `REJECT-top5-continuity=8`.
- Best row: `v317_all_full_delta_w0.7_c0.04_ov5`, overall macro delta `+0.00151383`, micro delta `+0.00405186`, follow-up mean AUC delta `+0.00475774`, low-group macro delta `+0.00833334`, low-group micro delta `+0.02192722`, site min macro delta `+0.00310966`, top5 overlap `1.00000000`, 2 rows reverted by strict top5 guard, correlation `0.99991956`.
- Used classes/sources: `47158son17:v150b_sparse_class_gate`, `516975:v193_structural_anticollapse_router`, `116570:v150b_sparse_class_gate`, `47158son25:v150b_sparse_class_gate`, `chacha1:v157_bounded_context_fusion`, `47158son10:v150b_sparse_class_gate`, `47158son21:v197_source_consensus_teacher_projection`.
- Decision: promote for local review only because the OOF macro gate is met and site/top5 stress is clean, but do not submit or materialize yet. The candidate still needs hidden-test-computable implementation proof, especially for the v150b-derived class signals that were rejected as a broad family in v312.
- Next recommended action: after v298 resolves, decide whether to build a v318 materializer for this exact 7-class route. Required proof before any Kaggle push: source provenance/rule audit, CPU/no-internet feasibility, strict top5 guard in notebook code, and guarded submit preflight.

## Pending-safe v318 v317 Materializer Readiness Audit

- Experiment: `v318-v317-materializer-readiness`
- Status: `BLOCK-v317-materializer-not-ready / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v318_v317_materializer_readiness.py`
- Report: `experiments/v318_v317_materializer_readiness_20260524.md`
- Structured log: `artifacts/runtime_v318_v317_materializer_readiness_20260524.json`
- Output: `experiments/v318_v317_materializer_readiness_20260524.csv`
- Research question: is the v317 seven-class local-review signal ready to be materialized as a hidden-test CPU notebook, or should it remain local-only?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v318_v317_materializer_readiness.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v318_v317_materializer_readiness.py --v317-csv experiments/v317_coverage_guided_source_gate_20260524.csv --output-csv experiments/v318_v317_materializer_readiness_20260524.csv --report experiments/v318_v317_materializer_readiness_20260524.md --runtime-json artifacts/runtime_v318_v317_materializer_readiness_20260524.json`
- Result: 4 used source families audited; all 4 are blocked for hidden-test materializer readiness. `v150b_sparse_class_gate`, `v157_bounded_context_fusion`, and `v193_structural_anticollapse_router` have `pred_test_*` parquet files that are actually 120 train-window rows; `v197_source_consensus_teacher_projection` has no `pred_test` artifact. v150b and v193 have local notebook materializer shells, but neither has verified hidden-test prediction artifacts for the exact v317 route, and v193 runtime says `runmode_pushed=false`.
- Decision: do not materialize or submit v317 from existing artifacts. v317 remains useful local evidence, but it is not a safe submission route until a self-contained CPU/no-internet notebook computes the exact seven-class mechanism on hidden-test rows.
- Next recommended action: if v298 resolves without reaching the goal, build a new exact-route materializer that recomputes the v317 signals inside a notebook; do not read the OOF-shaped `pred_test_*` artifacts as test predictions.

## Pending-safe v319 Deployability-constrained v317 Subsets

- Experiment: `v319-deployability-constrained-v317`
- Status: `PROMOTE-local-review-only / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v319_deployability_constrained_v317.py`
- Report: `experiments/v319_deployability_constrained_v317_20260524.md`
- Structured log: `artifacts/runtime_v319_deployability_constrained_v317_20260524.json`
- Output: `experiments/v319_deployability_constrained_v317_20260524.csv`
- Research question: after v318 blocks direct v317 materialization, can a more deployability-constrained subset of the seven v317 class/source signals retain promotion-sized local lift under strict top5 and site stress?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v319_deployability_constrained_v317.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v319_deployability_constrained_v317.py --coverage-csv birdclef-2026/class_coverage.csv --source-census experiments/v311_oof_source_census_20260524.csv --output-csv experiments/v319_deployability_constrained_v317_20260524.csv --report experiments/v319_deployability_constrained_v317_20260524.md --runtime-json artifacts/runtime_v319_deployability_constrained_v317_20260524.json`
- Result: 640 constrained candidates scored, runtime `22.47s`; decisions: `PROMOTE-local-review-only=15`, `HOLD-near-promotion-deployability-subset=59`, `HOLD-watchlist-deployability-subset=92`, `HOLD-local-lift-too-small=426`, `REJECT-top5-continuity=48`.
- Best strict row: `v319_shell_plus_context_full_delta_w0.9_c0.06_ov5`, using only `v150b_sparse_class_gate`, `v193_structural_anticollapse_router`, and `v157_bounded_context_fusion`; used classes are `47158son17`, `516975`, `116570`, `47158son25`, `chacha1`, and `47158son10`. Overall macro delta `+0.00196779`, micro delta `+0.00528549`, follow-up mean AUC delta `+0.00721522`, low-group macro delta `+0.01388889`, site min macro delta `+0.00491101`, top5 overlap `1.00000000`, 3 rows reverted by strict top5 guard.
- Deployability implication: removing `v197_source_consensus_teacher_projection` improves the best strict local readout and removes the source with no `pred_test`/notebook artifact. The remaining route still depends on v150b/v193/v157 being recomputed in a self-contained CPU/no-internet notebook; it is not submittable from current artifacts.
- Decision: keep v319 as the preferred local-review materializer target over v317. Do not submit or push while v298 is pending. Next materializer work should target the exact six-class `shell_plus_context` route, not the full seven-class v317 route.

## Pending-safe v320 v319 Exact-route Materializer Shell

- Experiment: `v320-v319-exact-route-materializer`
- Status: `PREPARED-local-only / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_prepare_v320_v319_exact_route_materializer.py`
- Notebook: `birdclef-2026/notebooks/v320-v319-exact-route-materializer/submission.ipynb`
- Metadata: `birdclef-2026/notebooks/v320-v319-exact-route-materializer/kernel-metadata.json`
- Attribution: `birdclef-2026/notebooks/v320-v319-exact-route-materializer/ATTRIBUTION.md`
- Report: `experiments/v320_v319_exact_route_materializer_20260524.md`
- Structured log: `artifacts/runtime_v320_v319_exact_route_materializer_20260524.json`
- Output: `experiments/v320_v319_exact_route_materializer_20260524.csv`
- Research question: can the preferred v319 six-class route be expressed as a self-contained CPU/no-internet Kaggle notebook shell that fail-closes instead of reading OOF-shaped local artifacts?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_prepare_v320_v319_exact_route_materializer.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_prepare_v320_v319_exact_route_materializer.py`; plus notebook/metadata structural check confirming 2 notebook cells, CPU/no-internet metadata, own kernel sources, no `artifacts/`, `oof_`, or `pred_test_` references in notebook code, and fail-closed `submission.csv` write path.
- Mechanism: `47158son17`, `116570`, `47158son25`, and `47158son10` are recomputed from own v87 anchor plus own v134 donor by rank-calibrated sparse donor movement; `516975` requires own v193 source kernel output and fail-closes if unavailable; `chacha1` is recomputed from official train-soundscape site/hour context and hidden/test row_id metadata.
- Decision: concrete materializer shell is prepared, but it is not submit-ready. Required next gate after v298 resolves: Kaggle Run-mode source-path/schema/runtime audit proving v87/v134/v193 hidden-row alignment, strict top5 guard behavior, no top1 drift, CPU runtime under cap, and guarded-submit compliance.

## v321 v320 Run-mode Static Audit

- Experiment: `v321-v320-runmode-static-audit`
- Status: `READY-v320-runmode-dryrun-audit / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v321_v320_runmode_static.py`
- Report: `experiments/v321_v320_runmode_static_audit_20260524.md`
- Structured log: `artifacts/runtime_v321_v320_runmode_static_audit_20260524.json`
- Output: `experiments/v321_v320_runmode_static_audit_20260524.csv`
- Research question: is the v320 exact-route materializer shell safe to advance to a Kaggle Run-mode dry-run audit after v298 tied, or does static inspection reveal a rule/runtime/schema blocker?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v321_v320_runmode_static.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v321_v320_runmode_static.py --notebook-dir birdclef-2026/notebooks/v320-v319-exact-route-materializer --output-csv experiments/v321_v320_runmode_static_audit_20260524.csv --report experiments/v321_v320_runmode_static_audit_20260524.md --runtime-json artifacts/runtime_v321_v320_runmode_static_audit_20260524.json`
- Result: 26 static checks passed; `block_count=0`, `warn_count=0`. Checks included CPU/no-internet metadata, required own-kernel sources, no dataset/model sources, no forbidden `artifacts/`, `oof_`, `pred_test_`, `/Users/`, or `working-dir` references, `submission.csv` write path, fail-closed function, missing-v193 fail-close, top1 fail-close, top5 row guard, summary/detail outputs, official train-label context, and attribution boundary.
- Decision: v320 is ready for Kaggle Run-mode dry-run audit. It remains `NO-SUBMIT` until dry-run output proves hidden-row alignment, runtime under cap, source availability, guard behavior, and guarded-submit preflight.

## v322 v320 Run-mode Push Gate

- Experiment: `v322-v320-runmode-push-gate`
- Status: `PUSHED-v320-runmode / WAIT-running / NO-SUBMIT`
- Push gate: `scripts/push_v320_after_v321_gate.py`
- Run-mode audit: `scripts/audit_v320_runmode.py`
- Push status: `experiments/v320_after_v321_push_gate_status.md`
- Run-mode status: `experiments/v320_runmode_status.md`
- Research question: after v321 static audit clears v320, can the exact-route materializer be advanced to Kaggle Run-mode dry-run proof without making a real competition submission?
- Validation: `python3 -m py_compile scripts/push_v320_after_v321_gate.py scripts/audit_v320_runmode.py && python3 scripts/push_v320_after_v321_gate.py --write && python3 scripts/push_v320_after_v321_gate.py --write --execute && python3 scripts/audit_v320_runmode.py --fetch-if-complete --write`
- Result: dry-run gate first returned `READY-push-v320-runmode` with `live_pending_count=0`, v298 state `HOLD-tie-anchor`, and v321 decision `READY-v320-runmode-dryrun-audit`; execute then pushed the v320 kernel through Python Kaggle API. Immediate audit reports Kaggle status `RUNNING`, fetched output `False`, and decision `WAIT-running`.
- Decision: v320 is now in Kaggle Run-mode proof only. Do not real-submit. Rerun `python3 scripts/audit_v320_runmode.py --fetch-if-complete --write` until it reaches `READY`, `HOLD`, or `REJECT`; only a `READY-v320-runmode-exact-route-review` result may proceed to guarded-submit dry-run.

## v323 Post-v320 Backup Queue

- Experiment: `v323-post-v320-backup-queue`
- Status: `PROMOTE-backup-materializer-review / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_select_v323_post_v320_backup_queue.py`
- Report: `experiments/v323_post_v320_backup_queue_20260524.md`
- Structured log: `artifacts/runtime_v323_post_v320_backup_queue_20260524.json`
- Output: `experiments/v323_post_v320_backup_queue_20260524.csv`
- Research question: while v320 Run-mode is pending, which v319-family routes are worth keeping as backup materializer candidates, and which apparent alternatives should be rejected before spending another Kaggle push?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_select_v323_post_v320_backup_queue.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_select_v323_post_v320_backup_queue.py --v319-csv experiments/v319_deployability_constrained_v317_20260524.csv --output-csv experiments/v323_post_v320_backup_queue_20260524.csv --report experiments/v323_post_v320_backup_queue_20260524.md --runtime-json artifacts/runtime_v323_post_v320_backup_queue_20260524.json`
- Result: 321 v319-family rows considered, 19 queue rows selected; decisions: `PROMOTE-backup-materializer-review=2`, `KEEP-primary-running=1`, `HOLD-v193-missing-fallback-only=2`, `HOLD-too-small-without-v150b=6`, `REJECT-top5-continuity=8`.
- Best actionable backup: `v319_shell_core_v150b_v193_full_delta_w0.9_c0.06_ov5`, a no-context/core route with macro delta `+0.00189352`, follow-up delta `+0.00833147`, site min `+0.00475319`, top5 overlap `1.00000000`, and 3 top5-reverted rows. This is the best backup only if the chacha/context branch is the failure source.
- Decision: keep v320 primary evidence, but if v320 fails due context/chacha implementation risk, review a core/no-context backup materializer. If v193 or v134 donor alignment is the failure mode, the queue does not justify a new immediate push: v150b-only is below promotion/site support, and non-v150b-only lift is too small.

## v324 v320 Run-mode Output Audit

- Experiment: `v324-v320-runmode-output-audit`
- Status: `HOLD-v320-no-active-sidecar / NO-SUBMIT`
- Audit: `scripts/audit_v320_runmode.py`
- Run-mode status: `experiments/v320_runmode_status.md`
- Output dir: `/tmp/v320-output`
- Research question: does the v320 Run-mode dry-run produce a schema-valid, active, source-aligned exact-route sidecar output that can advance to guarded-submit dry-run?
- Validation: `python3 -m py_compile scripts/audit_v320_runmode.py && python3 scripts/audit_v320_runmode.py --fetch-if-complete --write`
- Result: Kaggle status `COMPLETE`, output fetched, schema/order/range checks passed over 3 dry-run rows, and runtime in-notebook was `166.235s`. However summary reports `sidecar_active=False`, `changed_cells=0`, `changed_rows=0`, `top1_changed_rows=0`, `anchor_mode=exact_test_rows`, `donor_mode=dry_run_mean_fallback`, and `v193_mode=exact_test_rows`.
- Decision: do not submit v320. The dry-run proves the notebook is safe and fail-quiet, but not that it creates useful hidden-row movement. The likely blocker is donor/source-row alignment for the v134-derived branch in Kaggle dry-run; the next implementation path should diagnose source alignment before re-pushing any v319-family materializer.

## v325 v320 Source Alignment Audit

- Experiment: `v325-v320-source-alignment`
- Status: `BLOCK-v134-donor-row-mismatch / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v325_v320_source_alignment.py`
- Report: `experiments/v325_v320_source_alignment_20260524.md`
- Structured log: `artifacts/runtime_v325_v320_source_alignment_20260524.json`
- Output: `experiments/v325_v320_source_alignment_20260524.csv`
- Research question: which v320 source kernel output prevents active sidecar movement by failing row_id alignment with the current sample/test rows?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v325_v320_source_alignment.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v325_v320_source_alignment.py --fetch-dir /tmp/v325-v320-source-alignment --output-csv experiments/v325_v320_source_alignment_20260524.csv --report experiments/v325_v320_source_alignment_20260524.md --runtime-json artifacts/runtime_v325_v320_source_alignment_20260524.json`
- Result: v87 anchor and v193 source both have exact current sample row order with 3 rows. v134 donor has 120 Train rows, contains Train row IDs, has zero overlap with the current 3 sample rows, and is pairwise disjoint from both v87 and v193. v193's own summary also reports `fail_closed_no_row_overlap_dryrun`, and v193 `submission.csv` is byte-value identical to v87 for current dry-run rows.
- Decision: block v320/v319-family materialization paths that depend on v134 donor rank-calibration or v193 active movement. The next candidate must either fix the donor route so it computes on current test rows, or move to a genuinely source-free/source-aligned mechanism. Do not re-push the v323 no-context backup unless the source dependency is replaced; it still depends on the same v134/v193 family.

## v326 Teacher-distilled Clean Branch Probe

- Experiment: `v326-teacher-distilled-clean-branch`
- Status: `HOLD-low-top5-only / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v326_teacher_distilled_clean_branch.py`
- Report: `experiments/v326_teacher_distilled_clean_branch_20260524.md`
- Structured log: `artifacts/runtime_v326_teacher_distilled_clean_branch_20260524.json`
- Outputs: `experiments/v326_teacher_distilled_clean_branch_20260524.csv`, `experiments/v326_teacher_distilled_clean_branch_classes_20260524.csv`, `experiments/v326_teacher_distilled_clean_branch_groups_20260524.csv`
- Research question: can v305's v103 teacher low-top5 behavior be distilled into a deployable static class set plus clean v110/v113 branch movement, without reading v103 at runtime?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v326_teacher_distilled_clean_branch.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v326_teacher_distilled_clean_branch.py --output-csv experiments/v326_teacher_distilled_clean_branch_20260524.csv --class-csv experiments/v326_teacher_distilled_clean_branch_classes_20260524.csv --group-csv experiments/v326_teacher_distilled_clean_branch_groups_20260524.csv --report experiments/v326_teacher_distilled_clean_branch_20260524.md --runtime-json artifacts/runtime_v326_teacher_distilled_clean_branch_20260524.json`
- Result: 144 quick-grid candidates scored, runtime `5.48s`; decisions: `REJECT-macro-negative=72`, `HOLD-low-top5-only=48`, `HOLD-local-lift-too-small=24`, no promote rows. Best row `v326_S09_hour00_or_S08_hour07_tm0.03_ma1_mp1_mc4_max_v110_v113_r20_bm0.01_w0.9` uses classes `47158son20`, `47158son15`, `47158son18`, and `47158son16`, has 3 active cells, overall macro delta `+0.00000000`, overall top5 delta `+0.02739726`, low top5 delta `+0.06896552`, no low-group regression, and correlation `0.99999913`.
- Decision: do not materialize or submit. v326 recovers some low-top5 behavior cleanly, but it does not recover the macro gain that made v305 interesting. Treat v305/v326 as evidence that the missing signal is not expressible by current v110/v113 clean branch movement alone; next progress should come from a rebuilt same-row donor/acoustic source or a genuinely new source-free mechanism, not more constant/rank tuning.

## v327 Season/hour Missing-class Prior Probe

- Experiment: `v327-season-hour-missing-prior`
- Status: `PROMOTE-prior-mechanism-review / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v327_season_hour_missing_prior.py`
- Report: `experiments/v327_season_hour_missing_prior_20260524.md`
- Structured log: `artifacts/runtime_v327_season_hour_missing_prior_20260524.json`
- Outputs: `experiments/v327_season_hour_missing_prior_20260524.csv`, `experiments/v327_season_hour_missing_prior_classes_20260524.csv`, `experiments/v327_season_hour_missing_prior_folds_20260524.csv`
- Research question: can row_id-computable season/hour/end-window priors recover signal for classes that lack common-row OOF positives, under file-blocked and leave-site validation, without using prediction source artifacts?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v327_season_hour_missing_prior.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v327_season_hour_missing_prior.py --output-csv experiments/v327_season_hour_missing_prior_20260524.csv --class-csv experiments/v327_season_hour_missing_prior_classes_20260524.csv --fold-csv experiments/v327_season_hour_missing_prior_folds_20260524.csv --report experiments/v327_season_hour_missing_prior_20260524.md --runtime-json artifacts/runtime_v327_season_hour_missing_prior_20260524.json`
- Result: 20 source-free prior candidates scored, runtime `1.67s`; decisions: `PROMOTE-prior-mechanism-review=16`, `HOLD-lift-too-small=4`. Best row `month_hour` with `alpha=1.0` has missing-class file-blocked macro delta `+0.24155208`, missing-class leave-site macro delta `+0.02203832`, missing top5 hit `0.85280728` versus global `0.78755690`, and leave-site missing top5 hit `0.63125948`.
- Decision: promote the mechanism to review, not to submission. v327 is valuable because it uses only official labels plus row_id-computable metadata and survives leave-site in aggregate, but the current evaluation is a train-label prior surface rather than an anchor-delta submission candidate. Next step is a conservative materializer/probe that converts the strongest prior into small, protected movement over the scored anchor, proves active hidden-row behavior, and rejects any top1/top5 drift before Kaggle push.

## v328 Prior Stress Probe

- Experiment: `v328-prior-stress`
- Status: `PROMOTE-stress-review / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v328_prior_stress.py`
- Report: `experiments/v328_prior_stress_20260524.md`
- Structured log: `artifacts/runtime_v328_prior_stress_20260524.json`
- Outputs: `experiments/v328_prior_stress_20260524.csv`, `experiments/v328_prior_stress_folds_20260524.csv`
- Research question: does the v327 source-free prior signal survive leave-month and leave-site-month stress, or is it mostly memorizing calendar blocks in the official train-label surface?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v328_prior_stress.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v328_prior_stress.py --output-csv experiments/v328_prior_stress_20260524.csv --fold-csv experiments/v328_prior_stress_folds_20260524.csv --report experiments/v328_prior_stress_20260524.md --runtime-json artifacts/runtime_v328_prior_stress_20260524.json`
- Result: 16 stress candidates scored, runtime `2.62s`; decisions: `PROMOTE-stress-review=4`, `HOLD-stress-lift-too-small=12`. Best row is `hour` with `alpha=1.0`: leave-site missing macro delta `+0.04060925`, leave-month delta `+0.14288294`, leave-site-month delta `+0.16165386`. Fold-level site stress is mixed, so this is aggregate evidence rather than all-site-safe evidence.
- Decision: promote `hour` prior, not `month_hour`, as the next review mechanism. The stress result suggests the transferable part of v327 is mostly hour structure rather than month/hour memorization. Next step is a tiny protected anchor-delta probe/materializer using hour prior only, with per-site veto, top1/top5 continuity checks, and Run-mode proof before any Kaggle push.

## v329 Hour-prior Anchor-delta Probe

- Experiment: `v329-hour-prior-anchor-delta`
- Status: `HOLD-no-active-movement / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v329_hour_prior_anchor_delta.py`
- Report: `experiments/v329_hour_prior_anchor_delta_20260524.md`
- Structured log: `artifacts/runtime_v329_hour_prior_anchor_delta_20260524.json`
- Outputs: `experiments/v329_hour_prior_anchor_delta_20260524.csv`, `experiments/v329_hour_prior_anchor_delta_selection_20260524.csv`, `experiments/v329_hour_prior_anchor_delta_folds_20260524.csv`
- Research question: can an hour-only prior, selected and calibrated inside each training fold, improve the v87 train-window anchor on held-out files without top1/top5 disruption?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v329_hour_prior_anchor_delta.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v329_hour_prior_anchor_delta.py --output-csv experiments/v329_hour_prior_anchor_delta_20260524.csv --selection-csv experiments/v329_hour_prior_anchor_delta_selection_20260524.csv --fold-csv experiments/v329_hour_prior_anchor_delta_folds_20260524.csv --report experiments/v329_hour_prior_anchor_delta_20260524.md --runtime-json artifacts/runtime_v329_hour_prior_anchor_delta_20260524.json`
- Result: 162 protected anchor-delta candidates scored on 240 v87 train-window rows, runtime `45.57s`; all decisions were `HOLD-no-active-movement`. Best row equals the anchor exactly: macro delta `+0.00000000`, missing macro delta `+0.00000000`, top5 overlap `1.00000000`, changed cells `0`, selected classes `0`.
- Decision: do not materialize or push. The blocker is not top5/top1 guard rollback; the selection stage found no missing-positive class where fold-internal hour-prior rankcal beats the anchor by the minimum threshold. v328 remains a prior-surface mechanism, but v329 shows it is not yet an anchor residual mechanism. Next step is a relaxed blocker diagnostic to decide whether the threshold is too strict or the hour prior has no useful anchor residual signal.

## v330 Relaxed Hour-residual Blocker Diagnostic

- Experiment: `v330-relaxed-hour-residual`
- Status: `REJECT-hour-prior-residual-route / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v330_relaxed_hour_residual.py`
- Report: `experiments/v330_relaxed_hour_residual_20260524.md`
- Structured log: `artifacts/runtime_v330_relaxed_hour_residual_20260524.json`
- Outputs: `experiments/v330_relaxed_hour_residual_20260524.csv`, `experiments/v330_relaxed_hour_residual_folds_20260524.csv`
- Research question: did v329 fail only because the class-selection threshold was too strict, or does forced hour-prior residual movement still fail to improve the held-out v87 train-window anchor?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v330_relaxed_hour_residual.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v330_relaxed_hour_residual.py --output-csv experiments/v330_relaxed_hour_residual_20260524.csv --fold-csv experiments/v330_relaxed_hour_residual_folds_20260524.csv --report experiments/v330_relaxed_hour_residual_20260524.md --runtime-json artifacts/runtime_v330_relaxed_hour_residual_20260524.json`
- Result: a narrowed 16-candidate diagnostic scored in `4.94s` after an initial wide-grid attempt was stopped for runtime. Decisions: `HOLD-no-active-movement=12`, `REJECT-macro-negative=4`. Missing-positive scope still selected zero classes even at `min_train_delta=-0.02`; any-positive forced movement selected six insect classes and changed `657-672` cells, but macro delta was negative (`-0.000134` to `-0.000144`) and micro delta was also negative.
- Decision: reject the hour-prior residual route for now. v327/v328 showed the hour prior has label-surface signal, but v329/v330 show it does not become a useful residual over the v87 train-window anchor. Next progress should come from rebuilding same-row acoustic/source evidence or a new source-aligned donor, not more hour-prior tuning.

## v331 Output-sidecar Source Census

- Experiment: `v331-output-sidecar-source-census`
- Status: `SCREENED-no-full-row-followup / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v331_output_sidecar_source_census.py`
- Report: `experiments/v331_output_sidecar_source_census_20260524.md`
- Structured log: `artifacts/runtime_v331_output_sidecar_source_census_20260524.json`
- Outputs: `experiments/v331_output_sidecar_source_census_20260524.csv`, `experiments/v331_output_sidecar_source_census_site_20260524.csv`
- Research question: which existing local output sidecars are row-aligned with the v87 train-window validation surface and provide positive residual signal over the v87 anchor, without relying on mismatched donor rows?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v331_output_sidecar_source_census.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v331_output_sidecar_source_census.py --output-csv experiments/v331_output_sidecar_source_census_20260524.csv --site-csv experiments/v331_output_sidecar_source_census_site_20260524.csv --report experiments/v331_output_sidecar_source_census_20260524.md --runtime-json artifacts/runtime_v331_output_sidecar_source_census_20260524.json`
- Result: 54 local output sidecars scanned, runtime `3.46s`; decisions: `REJECT-site-collapse-risk=8`, `REJECT-macro-negative=12`, `HOLD-partial-row-only=23`, `SKIP-not-loaded=11`. The best full-row source is the SED sidecar with macro delta `+0.00313747` and missing macro delta `+0.00623326`, but it has site min macro delta `-0.016911`, so it is rejected as a direct source.
- Decision: do not push or materialize any v331 source directly. Full-row SED has usable signal but needs site-safe cutting; 120-row v102/v103-style sources remain partial-row-only diagnostics and cannot be reused as hidden/test donors without rebuilding row alignment.

## v332 SED Site-safe Residual Probe

- Experiment: `v332-sed-sitesafe-residual`
- Status: `HOLD-local-lift-too-small / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v332_sed_sitesafe_residual.py`
- Report: `experiments/v332_sed_sitesafe_residual_20260524.md`
- Structured log: `artifacts/runtime_v332_sed_sitesafe_residual_20260524.json`
- Outputs: `experiments/v332_sed_sitesafe_residual_20260524.csv`, `experiments/v332_sed_sitesafe_residual_selection_20260524.csv`, `experiments/v332_sed_sitesafe_residual_folds_20260524.csv`
- Research question: can the full-row SED sidecar signal from v331 be converted into a fold-selected, site-safe residual over the v87 anchor without top1/top5 disruption?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v332_sed_sitesafe_residual.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v332_sed_sitesafe_residual.py --output-csv experiments/v332_sed_sitesafe_residual_20260524.csv --selection-csv experiments/v332_sed_sitesafe_residual_selection_20260524.csv --fold-csv experiments/v332_sed_sitesafe_residual_folds_20260524.csv --report experiments/v332_sed_sitesafe_residual_20260524.md --runtime-json artifacts/runtime_v332_sed_sitesafe_residual_20260524.json`
- Result: 216 SED residual candidates scored, runtime `23.01s`; decisions: `HOLD-micro-negative=116`, `HOLD-local-lift-too-small=100`. The best missing-class row has macro delta `+0.00061497` and missing delta `+0.00137164` but micro delta `-0.00030142`. The best micro-positive rank-mode rows reach macro delta `+0.000900`, micro delta `+0.000098`, missing delta `+0.000819`, top1 delta `0`, and top5 overlap `1.00000000`.
- Decision: keep SED as a weak positive, site-cut source, but do not promote alone. It is below the `+0.0015` macro and `+0.006` missing-class gates. Next progress should combine SED residual with another same-row source or rebuild an acoustic donor rather than submitting SED-only movement.

## v333 SED+OOF Fusion Probe

- Experiment: `v333-sed-oof-fusion`
- Status: `HOLD-local-lift-too-small / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v333_sed_oof_fusion.py`
- Report: `experiments/v333_sed_oof_fusion_20260524.md`
- Structured log: `artifacts/runtime_v333_sed_oof_fusion_20260524.json`
- Outputs: `experiments/v333_sed_oof_fusion_20260524.csv`, `experiments/v333_sed_oof_fusion_selection_20260524.csv`, `experiments/v333_sed_oof_fusion_folds_20260524.csv`
- Research question: does adding the full-row SED branch to the strongest row-aligned v311 OOF sources improve a fold-selected protected residual over the v87 anchor enough to clear the promotion gate?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v333_sed_oof_fusion.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v333_sed_oof_fusion.py --output-csv experiments/v333_sed_oof_fusion_20260524.csv --selection-csv experiments/v333_sed_oof_fusion_selection_20260524.csv --fold-csv experiments/v333_sed_oof_fusion_folds_20260524.csv --report experiments/v333_sed_oof_fusion_20260524.md --runtime-json artifacts/runtime_v333_sed_oof_fusion_20260524.json`
- Result: 432 fusion candidates scored on the v311/v150 120-row common surface, runtime `30.14s`; decisions: `HOLD-local-lift-too-small=360`, `HOLD-micro-negative=72`. Best `oof_diverse_sed` row has macro delta `+0.00142913`, micro delta `+0.00143924`, top1 delta `0`, and top5 overlap `1.00000000`, just under the `+0.0015` macro promotion gate.
- Decision: no push or submit. Fusion is meaningfully stronger than SED-only and close to promotion, but v333 is still below the gate and only evaluated on the 120-row common surface. A focused v334 search is justified, but any positive result must still be treated as materializer-review evidence, not final submission evidence.

## v334 Focused Fusion Search

- Experiment: `v334-focused-fusion-search`
- Status: `PROMOTE-local-common-surface-review / HIGH-FOLD-RISK / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v334_focused_fusion_search.py`
- Report: `experiments/v334_focused_fusion_search_20260524.md`
- Structured log: `artifacts/runtime_v334_focused_fusion_search_20260524.json`
- Outputs: `experiments/v334_focused_fusion_search_20260524.csv`, `experiments/v334_focused_fusion_search_selection_20260524.csv`, `experiments/v334_focused_fusion_search_folds_20260524.csv`
- Research question: can the near-threshold v333 SED+OOF fusion be tuned within the same top1/top5 guards to clear the local promotion gate on the common row-aligned validation surface?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v334_focused_fusion_search.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v334_focused_fusion_search.py --output-csv experiments/v334_focused_fusion_search_20260524.csv --selection-csv experiments/v334_focused_fusion_search_selection_20260524.csv --fold-csv experiments/v334_focused_fusion_search_folds_20260524.csv --report experiments/v334_focused_fusion_search_20260524.md --runtime-json artifacts/runtime_v334_focused_fusion_search_20260524.json`
- Result: 1440 focused fusion candidates scored, runtime `118.98s`; decisions: `PROMOTE-fusion-review=1026`, `HOLD-local-lift-too-small=414`. Best row `v334_oof_diverse_sed_d0.0005_sf-0.002_p8_w0.85_c0.08` reaches macro delta `+0.00229063`, micro delta `+0.00252213`, top1 delta `0`, top5 overlap `1.00000000`, correlation `0.99938018`, and 590 changed cells. Best `oof_sed` row without `v149` reaches macro delta `+0.002269` and micro delta `+0.002786`.
- Fold risk: no promoted row has all fold macro deltas non-negative. The best overall row has two negative macro folds (`-0.005455`, `-0.001020`); the simpler best `oof_sed` rows have one negative macro fold with fold min `-0.005455`.
- Decision: promote only to local common-surface materializer review. This is the first recent route to clear the numeric macro gate under top1/top5 guards, but it is high fold-risk and uses OOF-source evidence that still needs a hidden-test-computable reconstruction. Do not push or submit before a stricter fold-risk veto and materializer feasibility audit.

## v335 v334 Fusion Risk Audit

- Experiment: `v335-v334-fusion-risk`
- Status: `REJECT-fold-risk / QUARANTINE-v334 / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v335_v334_fusion_risk.py`
- Report: `experiments/v335_v334_fusion_risk_20260524.md`
- Structured log: `artifacts/runtime_v335_v334_fusion_risk_20260524.json`
- Outputs: `experiments/v335_v334_fusion_risk_20260524.csv`, `experiments/v335_v334_fusion_risk_sources_20260524.csv`
- Research question: can any v334 focused-fusion candidate be reduced into a fold-risk-safe and hidden-test-computable materializer candidate, or should the route remain quarantined?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v335_v334_fusion_risk.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v335_v334_fusion_risk.py --output-csv experiments/v335_v334_fusion_risk_20260524.csv --source-csv experiments/v335_v334_fusion_risk_sources_20260524.csv --report experiments/v335_v334_fusion_risk_20260524.md --runtime-json artifacts/runtime_v335_v334_fusion_risk_20260524.json`
- Result: 1440 v334 rows audited in `1.10s`; decisions: `REJECT-fold-risk=1440`. Promoted v334 rows with zero negative macro folds: `0`; all-row zero-negative macro-fold rows: `0`; fold-safe rows with ready hidden-source status: `0`.
- Best numeric v334 row remains `v334_oof_diverse_sed_d0.0005_sf-0.002_p8_w0.85_c0.08` with macro delta `+0.00229063` and micro delta `+0.00252213`, but v335 rejects it because fold macro min is `-0.00545536`, two macro folds are negative, fold micro min is `-0.00640435`, and source feasibility is `BLOCK-hidden-source-unproven`.
- Source feasibility: `sed_rank` still needs Run-mode materializer proof; `v149`, `v150b`, `v181`, `v193`, and `v155` are OOF-only, hidden-unproven, or active-hidden-movement-unproven for this exact route.
- Decision: quarantine v334 as local common-surface evidence only. Do not push or submit this route.
- Next recommended action: stop further v334 weight/cap tuning; pivot to source-aligned/source-free mechanisms, or rebuild the contributing branches inside one CPU/no-internet hidden-test notebook before any future Run-mode push.

## v336 SED Fold-safe Candidate Audit

- Experiment: `v336-sed-foldsafe-candidate`
- Status: `HOLD-foldsafe-lift-too-small / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v336_sed_foldsafe_candidate.py`
- Report: `experiments/v336_sed_foldsafe_candidate_20260524.md`
- Structured log: `artifacts/runtime_v336_sed_foldsafe_candidate_20260524.json`
- Output: `experiments/v336_sed_foldsafe_candidate_20260524.csv`
- Research question: after rejecting v334, does the source-aligned SED-only route contain an all-fold-safe candidate that is strong enough to justify a materializer or submission path?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v336_sed_foldsafe_candidate.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v336_sed_foldsafe_candidate.py --output-csv experiments/v336_sed_foldsafe_candidate_20260524.csv --report experiments/v336_sed_foldsafe_candidate_20260524.md --runtime-json artifacts/runtime_v336_sed_foldsafe_candidate_20260524.json`
- Result: 216 v332 SED-only candidates audited in `0.53s`; decisions: `HOLD-foldsafe-lift-too-small=64`, `HOLD-micro-negative=62`, `REJECT-fold-risk=90`. Zero-negative macro-fold candidates: `126`; promotion candidates: `0`.
- Best fold-safe row: `v332_rank_d0.003_sf-0.002_mc8_w0.3_c0.01`, macro delta `+0.00053751`, micro delta `+0.00002484`, missing macro delta `+0.00048708`, fold macro min `0.00000000`, fold micro min `-0.00057410`, and changed cells `917`.
- Decision: do not materialize or submit SED-only. SED is source-aligned local evidence and can be an auxiliary branch, but its standalone fold-safe lift is far below the macro and weak-class gates and still lacks exact hidden-test Run-mode proof for this movement.
- Next recommended action: keep SED only as a weak auxiliary signal; search for a stronger source-aligned acoustic branch or a source-free mechanism with promotion-sized lift.

## v337 SED Prior-gated Residual

- Experiment: `v337-sed-prior-gated-residual`
- Status: `HOLD-local-lift-too-small / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v337_sed_prior_gated_residual.py`
- Report: `experiments/v337_sed_prior_gated_residual_20260524.md`
- Structured log: `artifacts/runtime_v337_sed_prior_gated_residual_20260524.json`
- Outputs: `experiments/v337_sed_prior_gated_residual_20260524.csv`, `experiments/v337_sed_prior_gated_residual_selection_20260524.csv`, `experiments/v337_sed_prior_gated_residual_folds_20260524.csv`
- Research question: can official-label hour/month priors gate the source-aligned SED residual into a fold-safe promotion-sized candidate, without using OOF-only donor sources?
- Validation: first run failed after `136.86s` with `KeyError: 'month'` because v87 train-window metadata has no month column; the script was fixed to parse month from `file_stem` and cache fold priors. Final validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v337_sed_prior_gated_residual.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v337_sed_prior_gated_residual.py --output-csv experiments/v337_sed_prior_gated_residual_20260524.csv --selection-csv experiments/v337_sed_prior_gated_residual_selection_20260524.csv --fold-csv experiments/v337_sed_prior_gated_residual_folds_20260524.csv --report experiments/v337_sed_prior_gated_residual_20260524.md --runtime-json artifacts/runtime_v337_sed_prior_gated_residual_20260524.json`
- Result: 1152 source-aligned/source-free gated SED candidates scored, runtime `171.19s`; decisions: `HOLD-local-lift-too-small=320`, `HOLD-micro-negative=416`, `REJECT-fold-risk=416`, no promotion candidates.
- Best row `v337_rank_hour_a1_q0.5_d0.0005_sf-0.002_mc8_w0.5_c0.01` has macro delta `+0.00053255`, micro delta `+0.00016414`, missing macro delta `+0.00037630`, fold macro min `0.00000000`, fold macro negative count `0`, fold micro min `-0.00053178`, top1 delta `0`, top5 overlap `1.00000000`, and changed cells `565`.
- Decision: do not materialize or submit. Official-label hour/month gating does not amplify SED beyond the conservative v332/v336 level and remains far below macro and weak-class promotion gates.
- Next recommended action: stop standalone SED + metadata gate tuning; look for a stronger same-row acoustic branch or a genuinely new source-free mechanism.

## v338 Acoustic Portfolio Fold-risk Probe

- Experiment: `v338-acoustic-portfolio-foldrisk`
- Status: `HOLD-local-lift-too-small / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v338_acoustic_portfolio_foldrisk.py`
- Report: `experiments/v338_acoustic_portfolio_foldrisk_20260524.md`
- Structured log: `artifacts/runtime_v338_acoustic_portfolio_foldrisk_20260524.json`
- Outputs: `experiments/v338_acoustic_portfolio_foldrisk_20260524.csv`, `experiments/v338_acoustic_portfolio_foldrisk_folds_20260524.csv`
- Research question: can the weak but source-aligned acoustic/SED branches from v314/v315/v332 combine into a promotion-sized local candidate while keeping strict top5 continuity and non-negative fold macro deltas?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v338_acoustic_portfolio_foldrisk.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v338_acoustic_portfolio_foldrisk.py --output-csv experiments/v338_acoustic_portfolio_foldrisk_20260524.csv --fold-csv experiments/v338_acoustic_portfolio_foldrisk_folds_20260524.csv --report experiments/v338_acoustic_portfolio_foldrisk_20260524.md --runtime-json artifacts/runtime_v338_acoustic_portfolio_foldrisk_20260524.json`
- Result: 168 acoustic portfolio candidates scored, runtime `13.01s`; decisions: `REJECT-top5-continuity=84`, `REJECT-fold-risk=53`, `HOLD-local-lift-too-small=25`, `HOLD-site-risk=3`, `REJECT-overall-macro-negative=3`, no promotion candidates.
- Highest macro row `v338_acoustic_core_w0.15_c0.02_ov4` reaches macro delta `+0.00094409` and micro delta `+0.00187290` with fold macro min `0.00000000`, but it is rejected because top5 overlap falls to `0.97333333` under `ov4`.
- Best non-rejected strict row is `v338_proto_bird_w0.3_c0.02_ov5`, macro delta `+0.00063264`, micro delta `+0.00157237`, fold macro min `0.00000000`, site macro min `-0.00094114`, top5 overlap `1.00000000`; still below the `+0.0015` macro gate.
- Decision: do not materialize or submit. Combining weak same-row acoustic/SED branches improves over each standalone branch in some settings, but not enough under strict top5 and fold-risk guards.
- Next recommended action: stop small additive acoustic portfolio tuning; next useful route must introduce a stronger same-row acoustic signal or a different mechanism, not just combine the weak branches.

## v339 Cross-family Consensus + Acoustic Probe

- Experiment: `v339-crossfamily-consensus-acoustic`
- Status: `HOLD-crossfamily-watchlist / NEAR-GATE-FOLD-RISK / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v339_crossfamily_consensus_acoustic.py`
- Report: `experiments/v339_crossfamily_consensus_acoustic_20260524.md`
- Structured log: `artifacts/runtime_v339_crossfamily_consensus_acoustic_20260524.json`
- Outputs: `experiments/v339_crossfamily_consensus_acoustic_20260524.csv`, `experiments/v339_crossfamily_consensus_acoustic_folds_20260524.csv`
- Research question: can the strongest strict-top5 v313 source-consensus signal and v338 same-row acoustic signal combine into a fold-safe promotion-sized local candidate, or are their gains non-additive/risk-bound?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v339_crossfamily_consensus_acoustic.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v339_crossfamily_consensus_acoustic.py --output-csv experiments/v339_crossfamily_consensus_acoustic_20260524.csv --fold-csv experiments/v339_crossfamily_consensus_acoustic_folds_20260524.csv --report experiments/v339_crossfamily_consensus_acoustic_20260524.md --runtime-json artifacts/runtime_v339_crossfamily_consensus_acoustic_20260524.json`
- Result: 972 cross-family candidates scored, runtime `57.81s`; decisions: `REJECT-top5-continuity=486`, `REJECT-fold-risk=399`, `HOLD-local-lift-too-small=71`, `HOLD-crossfamily-watchlist=2`, `REJECT-overall-macro-negative=14`, no promotion candidates.
- Highest macro row `v339_n3_mean_delta_acoustic_core_cw1_aw0.3_c0.04_ov4` reaches macro delta `+0.00185538`, micro delta `+0.00453121`, fold macro min `0.00000000`, and site macro min `+0.00154185`, but it is rejected because top5 overlap drops to `0.95500000` under `ov4`.
- Best strict-top5 near-gate row `v339_n3_mean_delta_sed_eff_cw1.3_aw0.3_c0.04_ov5` reaches macro delta `+0.00153220`, micro delta `+0.00216412`, site macro min `+0.00159436`, and top5 overlap `1.00000000`, but is rejected for fold risk with fold macro min `-0.00201940` and one negative macro fold.
- Best non-rejected watchlist row `v339_n4_mean_delta_proto_bird_cw1_aw0.6_c0.02_ov5` reaches macro delta `+0.00073067`, micro delta `+0.00157035`, fold macro min `0.00000000`, and top5 overlap `1.00000000`; still below promotion.
- Decision: no push or submit. v339 shows cross-family gains can be additive and nearly promotion-sized under strict top5, but the only macro-gate row is fold-risky and all consensus sources remain hidden-test-materializer-unproven.
- Next recommended action: run a focused v340 near-frontier search around the strict-top5 `sed_eff` family to see whether the single negative fold can be removed without dropping below the macro gate; even if it passes locally, it remains materializer-review only until hidden-test source reconstruction is proven.

## v340 Cross-family Near-frontier Search

- Experiment: `v340-crossfamily-nearfrontier`
- Status: `REJECT-fold-risk / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v340_crossfamily_nearfrontier.py`
- Report: `experiments/v340_crossfamily_nearfrontier_20260524.md`
- Structured log: `artifacts/runtime_v340_crossfamily_nearfrontier_20260524.json`
- Outputs: `experiments/v340_crossfamily_nearfrontier_20260524.csv`, `experiments/v340_crossfamily_nearfrontier_folds_20260524.csv`
- Research question: can the v339 strict-top5 `sed_eff` cross-family family remove its single negative macro fold while keeping a promotion-sized macro delta, or is the near-gate signal intrinsically fold-risky?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v340_crossfamily_nearfrontier.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v340_crossfamily_nearfrontier.py --output-csv experiments/v340_crossfamily_nearfrontier_20260524.csv --fold-csv experiments/v340_crossfamily_nearfrontier_folds_20260524.csv --report experiments/v340_crossfamily_nearfrontier_20260524.md --runtime-json artifacts/runtime_v340_crossfamily_nearfrontier_20260524.json`
- Result: 500 focused near-frontier candidates scored, runtime `30.86s`; all decisions were `REJECT-fold-risk`, with zero fold-safe candidates.
- Best row `v340_n3_mean_delta_sed_eff_cw1.45_aw0.3_c0.04_ov5` reaches macro delta `+0.00156852`, micro delta `+0.00224639`, site macro min `+0.00174272`, top5 overlap `1.00000000`, and top1 changed rows `0`, but fold macro min remains `-0.00201940` with one negative macro fold and fold micro min `-0.00412232`.
- Fold detail: folds 0/1/2/3 are macro-positive (`+0.00955776`, `+0.00102606`, `+0.00547393`, `+0.00649350`), while fold 4 is negative (`-0.00201940`) on `BC2026_Train_0005_S08_20250607_070007` and `BC2026_Train_0010_S09_20250828_000000`.
- Decision: do not push or submit. The strict-top5 cross-family near-gate signal appears intrinsically fold-risky under this grid, not fixable by small weight/cap tuning.
- Next recommended action: only revisit this family with a transferable metadata/source-quality veto that is learned fold-internally; do not hand-code a fold-4/file-specific exclusion.

## v341 Source-agreement Veto

- Experiment: `v341-source-agreement-veto`
- Status: `PROMOTE-agreement-veto-review / HIDDEN-SOURCE-RISK / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v341_source_agreement_veto.py`
- Report: `experiments/v341_source_agreement_veto_20260524.md`
- Structured log: `artifacts/runtime_v341_source_agreement_veto_20260524.json`
- Outputs: `experiments/v341_source_agreement_veto_20260524.csv`, `experiments/v341_source_agreement_veto_folds_20260524.csv`
- Research question: can a label-free source-agreement veto remove the fixed negative fold from the v340 `sed_eff` near-frontier family while preserving a promotion-sized strict-top5 macro gain?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v341_source_agreement_veto.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v341_source_agreement_veto.py --output-csv experiments/v341_source_agreement_veto_20260524.csv --fold-csv experiments/v341_source_agreement_veto_folds_20260524.csv --report experiments/v341_source_agreement_veto_20260524.md --runtime-json artifacts/runtime_v341_source_agreement_veto_20260524.json`
- Result: 918 source-agreement veto candidates scored, runtime `50.37s`; decisions: `PROMOTE-agreement-veto-review-HIDDEN-SOURCE-RISK=170`, `HOLD-agreement-veto-watchlist=208`, `HOLD-local-lift-too-small=324`, `REJECT-fold-risk=216`.
- Best row `v341_n3_same_sign_q0_cw1.45_aw0.35_c0.04` uses `v184_materialized_evidence_skeleton`, `v155_rank_prior_pulls`, `v169_verifier_tribunal_arbitration`, `sed_rank`, and `effb0_sentinel`, with label-free `same_sign` source-agreement mask over only `1.036325%` of cells.
- Best metrics: macro delta `+0.00169987`, micro delta `+0.00300107`, fold macro min `0.00000000`, fold micro min `+0.00095131`, site macro min `+0.00251890`, top5 overlap `1.00000000`, top1 changed rows `0`, changed cells `284`, and Pearson vs anchor `0.99992171`.
- Fold detail: fold macro deltas are `+0.01181874`, `+0.00247669`, `+0.00155400`, `+0.00649350`, and `0.00000000`; the previous v340 negative fold is neutralized without a file-specific rule.
- Decision: promote to local materializer-readiness review only. Do not push or submit: the consensus sources are OOF/local and hidden-test-materializer-unproven.
- Next recommended action: audit whether the exact v341 source set can be recomputed in a self-contained CPU/no-internet hidden-test notebook; if not, treat v341 as a mechanism blueprint rather than a submission candidate.

## v342 v341 Materializer Readiness Audit

- Experiment: `v342-v341-materializer-readiness`
- Status: `BLOCK-v341-materializer-not-ready / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v342_v341_materializer_readiness.py`
- Report: `experiments/v342_v341_materializer_readiness_20260524.md`
- Structured log: `artifacts/runtime_v342_v341_materializer_readiness_20260524.json`
- Output: `experiments/v342_v341_materializer_readiness_20260524.csv`
- Research question: is the v341 source-agreement veto candidate ready to be expressed as a hidden-test CPU/no-internet materializer, or is it only a local mechanism blueprint because one or more sources are hidden-test-unproven?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v342_v341_materializer_readiness.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v342_v341_materializer_readiness.py --v341-csv experiments/v341_source_agreement_veto_20260524.csv --output-csv experiments/v342_v341_materializer_readiness_20260524.csv --report experiments/v342_v341_materializer_readiness_20260524.md --runtime-json artifacts/runtime_v342_v341_materializer_readiness_20260524.json`
- Result: 5 v341 sources audited, runtime `0.64s`; `block_count=2`, `hold_count=3`, and overall decision `BLOCK-v341-materializer-not-ready`.
- Blocking sources: `v169_verifier_tribunal_arbitration` is a historical proxy source with no Kaggle-pushed hidden-test materializer, and `effb0_sentinel` lacks notebook/runmode proof.
- Hold sources: `v184_materialized_evidence_skeleton` is design-only, `v155_rank_prior_pulls` has an existing `REJECT-runmode-failure`, and `sed_rank` still needs exact hidden-test recomputation proof.
- Decision: no current v341 submission. v341 remains the strongest local mechanism blueprint, but it must be rebuilt from hidden-test-computable sources before any Kaggle push or guarded submit.
- Next recommended action: start a new source-aligned rebuild/audit that replaces the historical proxy and no-runmode sources, instead of submitting v341 as-is.

## v343 Rebuildable Agreement Sources

- Experiment: `v343-rebuildable-agreement-sources`
- Status: `HOLD-local-lift-too-small / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v343_rebuildable_agreement_sources.py`
- Report: `experiments/v343_rebuildable_agreement_sources_20260524.md`
- Structured log: `artifacts/runtime_v343_rebuildable_agreement_sources_20260524.json`
- Outputs: `experiments/v343_rebuildable_agreement_sources_20260524.csv`, `experiments/v343_rebuildable_agreement_sources_folds_20260524.csv`
- Research question: after removing v341's explicitly blocked sources, can the same label-free agreement-veto mechanism preserve a promotion-sized, fold-safe local gain using only lower-risk sources that are plausible to rebuild as CPU/no-internet hidden-test materializers?
- Validation: first broad grid was stopped after about `4m16s` because it was too slow for pending-safe screening; the script was narrowed to a quick direction-finding grid. Final validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v343_rebuildable_agreement_sources.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v343_rebuildable_agreement_sources.py --output-csv experiments/v343_rebuildable_agreement_sources_20260524.csv --fold-csv experiments/v343_rebuildable_agreement_sources_folds_20260524.csv --report experiments/v343_rebuildable_agreement_sources_20260524.md --runtime-json artifacts/runtime_v343_rebuildable_agreement_sources_20260524.json`
- Result: 192 reduced-source candidates scored, runtime `11.27s`; decisions: `HOLD-local-lift-too-small-runmode-risk=120`, `HOLD-micro-negative=40`, `HOLD-local-lift-too-small=32`, and no promotion candidates.
- Best lower-risk no-runmode-error row `v343_v184_sed_same_sign_q0_cw1_aw0.35_c0.04` reaches only macro delta `+0.00029410`, micro delta `+0.00001134`, fold macro min `0.00000000`, fold micro min `0.00000000`, top5 overlap `1.00000000`, and top1 changed rows `0`.
- Best numeric rows using `v184_v155_sed` reach about macro delta `+0.001499`, but remain just below the `+0.0015` gate and are blocked as `HOLD-local-lift-too-small-runmode-risk` because `v155_rank_prior_pulls` has an existing runmode failure.
- Decision: do not push or submit. Removing v341's explicit blockers removes almost all usable lift unless the broken v155 source is retained; v343 therefore does not produce a current submit candidate.
- Next recommended action: either fix/prove a clean `v155` materializer and rerun the agreement-veto gate, or pivot to a new independent hidden-test-computable source rather than tuning the reduced v184/SED/prototype pool.

## v344 v155 Fixability Audit

- Experiment: `v344-v155-fixability`
- Status: `BLOCK-v155-shell-only-fix-insufficient / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v344_v155_fixability.py`
- Report: `experiments/v344_v155_fixability_20260524.md`
- Structured log: `artifacts/runtime_v344_v155_fixability_20260524.json`
- Output: `experiments/v344_v155_fixability_20260524.csv`
- Research question: is the v155 runmode blocker fixable by changing the materializer shell, or does v155 require recomputing the Proto/SED sources on hidden-test rows before it can be used in a submit candidate?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v344_v155_fixability.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v344_v155_fixability.py --output-csv experiments/v344_v155_fixability_20260524.csv --report experiments/v344_v155_fixability_20260524.md --runtime-json artifacts/runtime_v344_v155_fixability_20260524.json`
- Result: audit runtime `0.57s`; overall decision `BLOCK-v155-shell-only-fix-insufficient`. Notebook flags show it uses `submission.csv`, `submission_protossm.csv`, and `submission_sed.csv`, refuses row mismatch, and does not recompute Proto/SED.
- Row-kind evidence: v87 anchor `submission.csv` is current sample/test aligned with 3 rows, but v87 `submission_protossm.csv` and `submission_sed.csv` are 240-row train-window diagnostics; v155 local pred/oof artifacts are also train-window rows.
- Decision: do not re-push the current v155 shell. A shell-only patch cannot safely create hidden-test movement because the required Proto/SED sources are not hidden-row aligned.
- Next recommended action: if pursuing the v155/v341 path, build a new CPU/no-internet notebook that recomputes the needed Proto/SED-like rank signals on hidden-test rows; otherwise pivot to a different exact-row source.

## v345 Exact-row Source Inventory

- Experiment: `v345-exactrow-source-inventory`
- Status: `SOURCE-INVENTORY-COMPLETE / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v345_exactrow_source_inventory.py`
- Report: `experiments/v345_exactrow_source_inventory_20260524.md`
- Structured log: `artifacts/runtime_v345_exactrow_source_inventory_20260524.json`
- Output: `experiments/v345_exactrow_source_inventory_20260524.csv`
- Research question: which existing source artifacts are current sample/test-row aligned and therefore plausible hidden-test materializer inputs, versus train-window/local-only diagnostics that must not be reused as submit sources?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v345_exactrow_source_inventory.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v345_exactrow_source_inventory.py --output-csv experiments/v345_exactrow_source_inventory_20260524.csv --report experiments/v345_exactrow_source_inventory_20260524.md --runtime-json artifacts/runtime_v345_exactrow_source_inventory_20260524.json`
- Result: 98 artifacts scanned, runtime `0.77s`; decisions: `READY-current-sample-test-rows=10`, `BLOCK-train-window-diagnostic-rows=87`, `HOLD-unknown-row-kind=1`.
- Critical finding: all 44 `artifacts/pred_test_*` sources are actually train-window diagnostic rows, so existing pred_test artifacts cannot be used as hidden-test donors. The 10 exact current-sample rows are only `birdclef-2026/outputs/*/submission.csv` sidecars.
- Decision: no push or submit. Any future source-based candidate must regenerate its source predictions on hidden-test rows inside a compliant materializer, not reuse existing `pred_test_*` artifacts.
- Next recommended action: switch from artifact-donor reuse to an active recomputation route: either implement a CPU-safe Proto/SED-like source in-notebook, or evaluate exact-row output-sidecar families only as anchors/diagnostics, not as donor artifacts.

## v346 Active Source Recompute Feasibility

- Experiment: `v346-active-source-recompute-feasibility`
- Status: `FEASIBILITY-AUDIT-COMPLETE / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v346_active_source_recompute_feasibility.py`
- Report: `experiments/v346_active_source_recompute_feasibility_20260524.md`
- Structured log: `artifacts/runtime_v346_active_source_recompute_feasibility_20260524.json`
- Output: `experiments/v346_active_source_recompute_feasibility_20260524.csv`
- Research question: among notebooks that already produce current sample/test-row submissions, which ones can be turned into exact-row SED/Proto source exporters, and which only provide final submissions or train-window diagnostic sidecars?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v346_active_source_recompute_feasibility.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v346_active_source_recompute_feasibility.py --output-csv experiments/v346_active_source_recompute_feasibility_20260524.csv --report experiments/v346_active_source_recompute_feasibility_20260524.md --runtime-json artifacts/runtime_v346_active_source_recompute_feasibility_20260524.json`
- Result: 9 exact-row final-output notebooks audited, runtime `0.81s`; decisions: `HOLD-export-fix-needed-branch-sidecars-train-only=7`, `HOLD-final-output-only-no-active-inference=2`, and no exact-row branch source exporters found.
- Best implementation starting points: `v93`, `v94`, `v87`, `v88`, `v92`, `v91`, and `v90` are CPU/no-internet notebooks with active test soundscape inference and SED/Proto sidecar write logic, but their branch sidecars are currently train-window diagnostics rather than exact sample/test rows.
- Decision: no push or submit. Existing exact-row final submissions are useful anchors, but branch source sidecars are not exact-row exports.
- Next recommended action: patch one active notebook, preferably a compact v88/v90-family notebook or the stronger v87/v94-family notebook, so it writes exact-row SED/Proto-like source predictions for the current sample/test rows; then rerun schema/source audits before any local candidate gate.

## v347 v88 Exact Source Export Materialization

- Experiment: `v347-v88-exact-source-export-materialization`
- Status: `PREPARED-local-runmode-source-export-proof / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_prepare_v347_v88_exact_source_export.py`
- Notebook dir: `birdclef-2026/notebooks/v347-v88-exact-source-export`
- Report: `experiments/v347_v88_exact_source_export_materialization_20260524.md`
- Structured log: `artifacts/runtime_v347_v88_exact_source_export_materialization_20260524.json`
- Output: `experiments/v347_v88_exact_source_export_materialization_20260524.csv`
- Research question: can the compact v88 active CPU/no-internet notebook be materialized into a source-export proof that writes exact sample-row SED/Proto sidecars during Kaggle Run-mode, while preserving fail-closed/no-submit boundaries?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_prepare_v347_v88_exact_source_export.py && python3 birdclef-2026/scripts/birdclef_prepare_v347_v88_exact_source_export.py && python3 birdclef-2026/scripts/birdclef_prepare_v347_v88_exact_source_export.py --execute --overwrite`
- Result: local notebook materialized with kernel id `junhaochengadjcjh7u7/bc26-v347-v88-exact-source-export`; patch marker appears once; metadata remains CPU/no-internet.
- Decision: prepared for static audit only. No Kaggle push or competition submission was performed.
- Next recommended action: run static source-export audit before any Kaggle Run-mode push.

## v348 v347 Static Source Export Audit

- Experiment: `v348-v347-static-source-export`
- Status: `READY-v347-runmode-source-export-audit / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v348_v347_static_source_export.py`
- Report: `experiments/v348_v347_static_source_export_20260524.md`
- Structured log: `artifacts/runtime_v348_v347_static_source_export_20260524.json`
- Output: `experiments/v348_v347_static_source_export_20260524.csv`
- Research question: does the locally materialized v347 notebook contain the intended dry-run exact-row branch-sidecar export patch, with CPU/no-internet metadata and no competition submission path?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v348_v347_static_source_export.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v348_v347_static_source_export.py --output-csv experiments/v348_v347_static_source_export_20260524.csv --report experiments/v348_v347_static_source_export_20260524.md --runtime-json artifacts/runtime_v348_v347_static_source_export_20260524.json`
- Result: static audit passed with no blockers. Checks confirm CPU/no-internet metadata, exactly one patch marker, branch alignment for `submission_protossm.csv`, `submission_sed.csv`, and `submission_birdnet.csv`, patch before blend load, hidden-test row preservation, and no push/submit calls.
- Decision: v347 may proceed to a Kaggle Run-mode source/schema audit only. It is not a scoring candidate and must not be real-submitted.
- Next recommended action: push v347 as Run-mode proof only, fetch outputs, and verify sidecar row alignment/runtime before using its exact-row source outputs in any local candidate gate.

## v349 v347 Run-mode Push and Status

- Experiment: `v349-v347-runmode-push-and-status`
- Status: `WAIT-running / RUNMODE-PUSHED / NO-COMPETITION-SUBMIT`
- Scripts: `scripts/push_v347_after_v348_gate.py`, `scripts/audit_v347_runmode.py`
- Reports: `experiments/v347_after_v348_push_gate_status.md`, `experiments/v347_runmode_status.md`
- Structured logs: `artifacts/runtime_v347_runmode_status.json`, `artifacts/lineage_v347_runmode_status.json`
- Research question: after v348 static readiness, can v347 be safely pushed to Kaggle Run-mode for exact-row source-export proof without making a competition submission?
- Validation: `python3 -m py_compile scripts/push_v347_after_v348_gate.py scripts/audit_v347_runmode.py && python3 scripts/push_v347_after_v348_gate.py --write && python3 scripts/push_v347_after_v348_gate.py --write --execute && python3 scripts/audit_v347_runmode.py --fetch-if-complete --write`
- Result: push gate accepted the Kaggle kernel push for `junhaochengadjcjh7u7/bc26-v347-v88-exact-source-export` with `live_pending_count=0`, CPU/no-internet/no-TPU metadata, and no competition-submit path. Latest audit at `2026-05-24 10:53:31 UTC` reports Kaggle status `RUNNING`, `Fetched=False`, no output files available yet, and decision `WAIT-running`.
- Metrics: OOF Macro AUC, fold std, weak-class AUC, and expert correlation are not applicable because v349 is a Run-mode source/schema proof, not a scoring candidate.
- Runtime: Kaggle runtime is not yet known while the kernel is still `RUNNING`; target remains `<4200s`, hard cap `5400s`.
- Decision: do not real-submit v347. Continue polling until Run-mode is complete; only if `submission.csv`, `submission_protossm.csv`, `submission_sed.csv`, and `submission_birdnet.csv` are exact-row aligned and runtime-safe may the sidecars feed a later local candidate gate.
- Next recommended action: while v347 is pending, screen the next hidden-test-computable source-export starting point or a local gate that can use v347 sidecars after they become available.

## v350 Next Source Export Priority

- Experiment: `v350-next-source-export-priority`
- Status: `READY-v87-next-source-export-materialization / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v350_next_source_export_priority.py`
- Report: `experiments/v350_next_source_export_priority_20260524.md`
- Structured log: `artifacts/runtime_v350_next_source_export_priority_20260524.json`
- Output: `experiments/v350_next_source_export_priority_20260524.csv`
- Research question: while v347 Run-mode is pending, which already active CPU/no-internet notebook is the best next source-export materialization target for producing hidden-test-computable SED/Proto sidecars?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v350_next_source_export_priority.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v350_next_source_export_priority.py`
- Result: 9 candidates screened in `0.03s`; overall decision `READY-v87-next-source-export-materialization-NO-PUSH-NO-SUBMIT`.
- Best target: `v87-attributed-nina-eos5-v38plus` with priority score `97.4`, current visible-best evidence `0.949`, CPU/no-internet metadata, active test-soundscape inference, and ProtoSSM/SED sidecar writes.
- Metrics: OOF Macro AUC, fold std, weak-class AUC, and expert correlation are not applicable because v350 is a static route-priority audit. v87 is selected for materialization readiness and prior visible-best evidence, not as a newly scored candidate.
- Decision: do not push or submit. If v347 fails or the exact-row sidecars need a stronger high-anchor source, materialize a v87 exact-row source-export proof next and run the same static/Run-mode/schema gates before candidate scoring.
- Next recommended action: poll v347; if it completes READY, use v347 sidecars for local candidate gating first. If v347 fails or produces weak/unsafe sidecars, build v87 exact-row source-export materialization.

## v351 v347 Run-mode Resolution

- Experiment: `v351-v347-runmode-resolution`
- Status: `REJECT-v347-sidecar-not-exact-row / NO-SUBMIT`
- Reports: `experiments/v347_runmode_status.md`
- Structured logs: `artifacts/runtime_v347_runmode_status.json`, `artifacts/lineage_v347_runmode_status.json`
- Research question: did the v347 Kaggle Run-mode proof actually produce exact-row branch source sidecars suitable for later local candidate gating?
- Validation: `python3 scripts/audit_v347_runmode.py --fetch-if-complete --write`
- Result: Kaggle Run-mode completed and outputs were fetched. Main `submission.csv` is exact sample/test rows with shape `(3, 235)`, no NaN/inf, valid range, and runtime `245s`.
- Sidecar failure: `submission_protossm.csv`, `submission_sed.csv`, and `submission_birdnet.csv` are each `(240, 235)` train-window diagnostic rows, not sample/test rows. The log printed v347 patch messages, but it preserved active rows because `test_paths` was non-empty while row ids still contained `BC2026_Train_*`.
- Decision: reject v347 as a sidecar source-export route. Do not real-submit or use its 240-row sidecars for local candidate gating.
- Next recommended action: do not fake-align train diagnostics into source sidecars. Use v350's v87 follow-up route and export only already exact-row model variants with fail-closed row checks.

## v351 v87 Exact Variant Export Materialization

- Experiment: `v351-v87-exact-variant-export-materialization`
- Status: `PREPARED-local-v87-exact-variant-export / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_prepare_v351_v87_exact_variant_export.py`
- Notebook dir: `birdclef-2026/notebooks/v351-v87-exact-variant-export`
- Report: `experiments/v351_v87_exact_variant_export_materialization_20260524.md`
- Structured logs: `artifacts/runtime_v351_v87_exact_variant_export_materialization_20260524.json`, `artifacts/lineage_v351_v87_exact_variant_export_materialization_20260524.json`
- Research question: can the visible-best v87 notebook be materialized into a CPU/no-internet source-export proof that writes exact sample-row variant sidecars, without pretending that 240-row train diagnostics are hidden-test sources?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_prepare_v351_v87_exact_variant_export.py && python3 birdclef-2026/scripts/birdclef_prepare_v351_v87_exact_variant_export.py && python3 birdclef-2026/scripts/birdclef_prepare_v351_v87_exact_variant_export.py --execute --overwrite`
- Result: local notebook materialized with kernel id `junhaochengadjcjh7u7/bc26-v351-v87-exact-variant-export`; patch marker appears once; metadata remains CPU/no-internet/no-TPU.
- Exports: `submission_v87_eos5.csv`, `submission_v87_karnak_power.csv`, and `submission_v87_final.csv`, each guarded to match `sample_submission.csv` row order/class order, finite values, and `[0, 1]` range.
- Decision: prepared for static audit only. No Kaggle push or competition submission was performed.
- Next recommended action: run static variant-export audit before any Kaggle Run-mode push.

## v352 v351 Static Variant Export Audit

- Experiment: `v352-v351-static-variant-export`
- Status: `READY-v351-runmode-variant-export-audit / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v352_v351_static_variant_export.py`
- Report: `experiments/v352_v351_static_variant_export_20260524.md`
- Structured log: `artifacts/runtime_v352_v351_static_variant_export_20260524.json`
- Output: `experiments/v352_v351_static_variant_export_20260524.csv`
- Research question: does the locally materialized v351 notebook contain the intended exact-row variant-export patch, CPU/no-internet metadata, fail-closed row guards, and no competition submission path?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v352_v351_static_variant_export.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v352_v351_static_variant_export.py`
- Result: static audit passed with no blockers. Checks confirm CPU/no-internet/no-TPU metadata, competition source, exactly one patch marker, patch after final write, exports for all three v87 variant files, sample-row guard, train-row rejection, finite/range checks, and no push/submit calls.
- Decision: v351 may proceed to a Kaggle Run-mode variant-export audit only. It is not a scoring candidate and must not be real-submitted.
- Next recommended action: push v351 as Run-mode proof only, fetch outputs, and verify exact-row variant sidecars/runtime before using them in any local candidate gate.

## v353 v351 Run-mode Push and Waiting Gate

- Experiment: `v353-v351-runmode-push-and-wait`
- Status: `READY-runmode-output / HOLD-variants-identical / NO-COMPETITION-SUBMIT`
- Scripts: `scripts/push_v351_after_v352_gate.py`, `scripts/audit_v351_runmode.py`, `birdclef-2026/scripts/birdclef_probe_v353_v351_variant_gate.py`
- Reports: `experiments/v351_after_v352_push_gate_status.md`, `experiments/v351_runmode_status.md`, `experiments/v353_v351_variant_gate_20260524.md`
- Structured logs: `artifacts/runtime_v351_runmode_status.json`, `artifacts/lineage_v351_runmode_status.json`, `artifacts/runtime_v353_v351_variant_gate_20260524.json`
- Research question: after v352 static readiness, can v351 be safely pushed to Kaggle Run-mode for exact-row variant/source proof, and is a local variant gate ready to consume the outputs once available?
- Validation: `python3 -m py_compile scripts/push_v351_after_v352_gate.py scripts/audit_v351_runmode.py birdclef-2026/scripts/birdclef_probe_v353_v351_variant_gate.py && python3 scripts/push_v351_after_v352_gate.py --write && python3 scripts/push_v351_after_v352_gate.py --write --execute && python3 scripts/audit_v351_runmode.py --fetch-if-complete --write && python3 birdclef-2026/scripts/birdclef_probe_v353_v351_variant_gate.py`
- Result: push gate accepted the Kaggle kernel push for `junhaochengadjcjh7u7/bc26-v351-v87-exact-variant-export` with `live_pending_count=0`, CPU/no-internet/no-TPU metadata, and no competition-submit path. Latest audit at `2026-05-24 11:22:27 UTC` reports Kaggle status `COMPLETE`, `Fetched=True`, runtime `216s`, and decision `READY-v351-exact-row-variant-exports`.
- v353 local gate status: `HOLD-v351-variants-identical-NO-PUSH-NO-SUBMIT`; `submission.csv`, `submission_v87_eos5.csv`, `submission_v87_karnak_power.csv`, and `submission_v87_final.csv` all match sample rows and schema, but pairwise Pearson is `1.00000000`, MAD is `0.00000000`, max absolute difference is `0.00000000`, and top-k rows are unchanged.
- Metrics: OOF Macro AUC, fold std, and weak-class AUC are not applicable because this is a Run-mode source/schema and variant-diversity gate, not a scored candidate. Expert-correlation/diversity evidence is negative: all exact-row variants are identical.
- Decision: do not real-submit v351 and do not use its exact-row variants as a downstream candidate source. The proof is useful for runtime/schema only.
- Next recommended action: stop exact-variant-export-only work unless a new notebook can produce non-identical exact-row variants with OOF/train-window evidence. Audit whether v351 cache is new evidence before using it.

### v353 Monitor Update

- Latest poll: `2026-05-24 11:17:20 UTC`
- Status: `WAIT-running / Fetched=False / NO-COMPETITION-SUBMIT`
- Output availability: `submission.csv`, `submission_v87_eos5.csv`, `submission_v87_karnak_power.csv`, and `submission_v87_final.csv` are not yet available.
- Decision: keep waiting; do not real-submit or use v351 outputs until `scripts/audit_v351_runmode.py --fetch-if-complete --write` returns READY.

### v353 Final Update

- Completion poll: `2026-05-24 11:22:27 UTC`
- Status: `READY-v351-exact-row-variant-exports / Fetched=True / runtime=216s / NO-COMPETITION-SUBMIT`
- Variant gate: `HOLD-v351-variants-identical-NO-PUSH-NO-SUBMIT`
- Decision: v351 is not a candidate source. It proves exact-row export can be packaged safely, but the exported variants carry no diversity.

## v354 Exact Variant Family Census

- Experiment: `v354-exact-variant-family-census`
- Status: `HOLD-no-submitworthy-exact-variant-family / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v354_exact_variant_family_census.py`
- Report: `experiments/v354_exact_variant_family_census_20260524.md`
- Structured log: `artifacts/runtime_v354_exact_variant_family_census_20260524.json`
- Output: `experiments/v354_exact_variant_family_census_20260524.csv`
- Research question: after v351 proved exact-row v87 variants are identical, do any existing exact-row output families provide non-identical variant structure worth materializing for a downstream local candidate gate?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v354_exact_variant_family_census.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v354_exact_variant_family_census.py`
- Result: 37 output families scanned in `0.35s`; only 2 families have non-identical exact-row variants: `v88-attributed-zeyad-eos-parity-t3-v1` and its derivative `v347-v88-exact-source-export-runmode`, with max pair MAD `0.00182724`.
- Blocking evidence: both diverse families descend from v88, which scored public `0.921` and is rejected as a final route. Visible-best v87/v351 exact variants are identical.
- Decision: do not spend more Run-mode pushes on exact variant export alone.
- Next recommended action: the next useful path must create a new hidden-test-computable source with train-window/OOF evidence, not just variant-file plumbing.

## v355 v351 Cache Novelty Audit

- Experiment: `v355-v351-cache-novelty`
- Status: `HOLD-v351-cache-duplicate-of-v87 / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v355_v351_cache_novelty.py`
- Report: `experiments/v355_v351_cache_novelty_20260524.md`
- Structured log: `artifacts/runtime_v355_v351_cache_novelty_20260524.json`
- Output: `experiments/v355_v351_cache_novelty_20260524.csv`
- Research question: does the v351 Run-mode cache add any new OOF/source evidence beyond the existing v87 caches?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v355_v351_cache_novelty.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v355_v351_cache_novelty.py`
- Result: 3 OOF caches scanned; v351 `oof_base`, `oof_prior`, and `fold_id` hashes are byte-identical to `v87-attributed-nina-eos5-v38plus` and `v87-attributed-nina-eos5-v38plus-v2`.
- Decision: v351 cache is not independent evidence. Do not use it as a new source for downstream candidates.
- Next recommended action: retire the exact-variant/cache route and return to mechanisms that introduce genuinely new OOF/source structure, such as an actively recomputed source model or a deployable source-agreement mechanism with non-duplicate train-window evidence.

## v356 Top OOF Source Deployability Audit

- Experiment: `v356-top-oof-source-deployability`
- Status: `HOLD-no-deployable-top-oof-source / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v356_top_oof_source_deployability.py`
- Report: `experiments/v356_top_oof_source_deployability_20260524.md`
- Structured log: `artifacts/runtime_v356_top_oof_source_deployability_20260524.json`
- Output: `experiments/v356_top_oof_source_deployability_20260524.csv`
- Research question: are the strongest v311 OOF sources genuinely distinct and hidden-test-computable enough to justify a new materialization path after the v351 exact-variant/cache route collapsed?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v356_top_oof_source_deployability.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v356_top_oof_source_deployability.py`
- Result: 5 top OOF sources audited. `v150b_sparse_class_gate`, `v214_bounded_adaptive_verifier`, and `v216_spectrogram_interaction_verifier` are byte-identical train-window OOF artifacts (`120` train rows, `0` test rows), despite sharing v311 `overall_delta=0.00207367`. `v150b` also has known strict-revival and row-alignment blockers.
- Remaining site-robust sources `v181_adaptive_evidence_gate` and `v193_structural_anticollapse_router` are distinct but still train-window OOF only and below promotion alone.
- Decision: do not revive the apparent top v311 source family as a materialization route. There is no deployable top OOF source ready for push or submission.
- Next recommended action: pivot away from source-artifact reuse. The next experiment should actively recompute a new hidden-test source or design a deployable source-agreement mechanism from notebook-computable signals, then prove it with OOF/train-window evidence before any Run-mode push.

## v357 Exact-row Branch Candidate Triage

- Experiment: `v357-exactrow-branch-candidate-triage`
- Status: `HOLD-no-usable-exactrow-branch-sidecar / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v357_exactrow_branch_candidate_triage.py`
- Report: `experiments/v357_exactrow_branch_candidate_triage_20260524.md`
- Structured log: `artifacts/runtime_v357_exactrow_branch_candidate_triage_20260524.json`
- Research question: do existing exact-row branch sidecars provide a usable source for a downstream candidate?
- Result: 12 output families and 29 sidecars audited; available train-window rows or sample-row-identical outputs do not provide usable exact-row branch diversity.
- Decision: do not submit or build from these sidecars.

## v358 Active Recompute Patchpoint Audit

- Experiment: `v358-active-recompute-patchpoints`
- Status: `READY-v91-active-source-export-materialization / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v358_active_recompute_patchpoints.py`
- Report: `experiments/v358_active_recompute_patchpoints_20260524.md`
- Structured log: `artifacts/runtime_v358_active_recompute_patchpoints_20260524.json`
- Research question: which active CPU/no-internet notebook is the safest exact-row ProtoSSM/SED source-export patch point?
- Result: v91 is preferred; v92 is a feasible backup.
- Decision: materialize v91 first with fail-closed exact-row source export.

## v359 v91 Exact Source Export Materialization

- Experiment: `v359-v91-exact-source-export-materialization`
- Status: `PREPARED-local-v91-exact-source-export / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_prepare_v359_v91_exact_source_export.py`
- Notebook: `birdclef-2026/notebooks/v359-v91-exact-source-export`
- Report: `experiments/v359_v91_exact_source_export_materialization_20260524.md`
- Structured log: `artifacts/runtime_v359_v91_exact_source_export_materialization_20260524.json`
- Research question: can v91 be materialized into a fail-closed exact-row ProtoSSM/SED source exporter?
- Result: local notebook prepared with `CODEX_V359_EXACT_SOURCE_EXPORT_PATCH`.
- Decision: run static audit before any Run-mode push.

## v360 v359 Static Source Export Audit

- Experiment: `v360-v359-static-source-export`
- Status: `READY-v359-runmode-source-export-audit / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v360_v359_static_source_export.py`
- Report: `experiments/v360_v359_static_source_export_20260524.md`
- Structured log: `artifacts/runtime_v360_v359_static_source_export_20260524.json`
- Research question: does v359 contain required fail-closed exact-row source-export guards?
- Result: 16 checks passed with 0 blockers.
- Decision: v359 may be pushed for Kaggle Run-mode proof only.

## v361 v359 Run-mode Push and Resolution

- Experiment: `v361-v359-runmode-push-and-wait`
- Status: `READY-v359-runmode-failclosed-source-export-proof / NO-COMPETITION-SUBMIT`
- Scripts: `scripts/push_v359_after_v360_gate.py`, `scripts/audit_v359_runmode.py`
- Report: `experiments/v359_runmode_status.md`
- Structured log: `artifacts/runtime_v359_runmode_status.json`
- Research question: will v359 export exact-row active source sidecars or fail closed without relabeling fallback rows?
- Result: Kaggle Run-mode completed in `264s`; `submission.csv` schema is valid, but `v359_exact_source_export_summary.json` reports `active=false`, reason `fail_closed_no_test_soundscapes`, and no exact sidecars.
- Decision: v359 is a safe proof, not a candidate source.

## v362 v92 Backup Source Export Readiness

- Experiment: `v362-v92-backup-source-export-readiness`
- Status: `READY-v92-backup-source-export-materialization / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v362_v92_backup_source_export_readiness.py`
- Report: `experiments/v362_v92_backup_source_export_readiness_20260524.md`
- Structured log: `artifacts/runtime_v362_v92_backup_source_export_readiness_20260524.json`
- Research question: if v359 has no usable active sidecars, is v92 ready as backup source-export materializer?
- Result: 13 checks passed with 0 blockers.
- Decision: materialize v92 as backup.

## v363 v359 Source Gate Final

- Experiment: `v363-v359-source-gate-final`
- Status: `HOLD-v359-failclosed-no-active-source-sidecars / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v363_v359_source_gate.py`
- Report: `experiments/v363_v359_source_gate_20260524.md`
- Structured log: `artifacts/runtime_v363_v359_source_gate_20260524.json`
- Research question: do fetched v359 outputs provide exact-row ProtoSSM/SED source diversity?
- Result: `submission.csv` is available and valid, but exact source sidecars are absent because v359 failed closed.
- Decision: do not use v359 as source candidate; move to v92 backup.

## v364 v92 Exact Source Export Materialization

- Experiment: `v364-v92-exact-source-export-materialization`
- Status: `PREPARED-local-v92-exact-source-export / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_prepare_v364_v92_exact_source_export.py`
- Notebook: `birdclef-2026/notebooks/v364-v92-exact-source-export`
- Report: `experiments/v364_v92_exact_source_export_materialization_20260524.md`
- Structured log: `artifacts/runtime_v364_v92_exact_source_export_materialization_20260524.json`
- Research question: can the v92 backup notebook be materialized into a fail-closed exact-row ProtoSSM/SED source exporter?
- Result: local notebook prepared with `CODEX_V364_EXACT_SOURCE_EXPORT_PATCH`, kernel id `junhaochengadjcjh7u7/bc26-v364-v92-exact-source-export`, CPU/no-internet/no-TPU metadata.
- Decision: no push or competition submission from this step; run static source-export audit next.

## v365 v364 Static Source Export Audit

- Experiment: `v365-v364-static-source-export`
- Status: `READY-v364-runmode-source-export-audit / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v365_v364_static_source_export.py`
- Report: `experiments/v365_v364_static_source_export_20260524.md`
- Structured log: `artifacts/runtime_v365_v364_static_source_export_20260524.json`
- Output: `experiments/v365_v364_static_source_export_20260524.csv`
- Research question: does the v364 v92 materializer contain the required fail-closed exact-row source-export guards before any Kaggle Run-mode push?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v365_v364_static_source_export.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v365_v364_static_source_export.py`
- Result: 18 checks passed with 0 blockers; final write line `2405`, patch marker line `2464`, marker count `2`.
- Decision: v364 may be pushed for Kaggle Run-mode source/schema proof only. It is not a scored candidate and must not be real-submitted.
- Next recommended action: build a guarded v364 Run-mode push/audit pair, verify live pending count is 0, push only the kernel, then fetch outputs and run a source gate.

## v366 v364 Run-mode Push and Waiting Gate

- Experiment: `v366-v364-runmode-push-and-wait`
- Status: `WAIT-running / RUNMODE-PUSHED / NO-COMPETITION-SUBMIT`
- Scripts: `scripts/push_v364_after_v365_gate.py`, `scripts/audit_v364_runmode.py`
- Reports: `experiments/v364_after_v365_push_gate_status.md`, `experiments/v364_runmode_status.md`
- Structured logs: `artifacts/runtime_v364_runmode_status.json`, `artifacts/lineage_v364_runmode_status.json`
- Research question: after v365 static readiness, can v364 be safely pushed to Kaggle Run-mode for source/schema proof without making a real competition submission?
- Validation: `python3 -m py_compile scripts/push_v364_after_v365_gate.py scripts/audit_v364_runmode.py && python3 scripts/push_v364_after_v365_gate.py --write && python3 scripts/push_v364_after_v365_gate.py --write --execute && python3 scripts/audit_v364_runmode.py --fetch-if-complete --write`
- Result: push gate accepted the Kaggle kernel push for `junhaochengadjcjh7u7/bc26-v364-v92-exact-source-export` with `live_pending_count=0`, CPU/no-internet/no-TPU metadata, and no competition-submit path. Immediate audit status is `RUNNING`, fetched `False`.
- Decision: keep waiting; do not real-submit v364 or use it as a source candidate until `scripts/audit_v364_runmode.py --fetch-if-complete --write` reaches a terminal READY/HOLD/REJECT state.
- Next recommended action: poll v364 Run-mode output while continuing independent candidate screening.

### v366 Monitor Update

- Latest poll: `2026-05-24 12:28:17 UTC`
- Status: `READY-v364-runmode-failclosed-source-export-proof / Fetched=True / runtime=324s / NO-COMPETITION-SUBMIT`
- Output: `submission.csv` is schema-valid with 3 sample rows; `v364_exact_source_export_summary.json` reports `active=false`, reason `fail_closed_no_test_soundscapes`, and `exported=[]`.
- Decision: v364 is a safe Run-mode proof but not a source candidate. Do not use it for a downstream candidate; continue with v368/v87 static audit.

## v367 Post-v364 Candidate Queue

- Experiment: `v367-post-v364-candidate-queue`
- Status: `READY-v87-next-if-v364-no-active-sidecars / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v367_post_v364_candidate_queue.py`
- Report: `experiments/v367_post_v364_candidate_queue_20260524.md`
- Structured log: `artifacts/runtime_v367_post_v364_candidate_queue_20260524.json`
- Output: `experiments/v367_post_v364_candidate_queue_20260524.csv`
- Research question: while v364 Run-mode is pending, which source-export candidate should be prepared next if v364 finishes without active exact-row source sidecars?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v367_post_v364_candidate_queue.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v367_post_v364_candidate_queue.py`
- Result: 4 candidates screened. Best candidate is `v87-attributed-nina-eos5-v38plus` with decision `PROMOTE-next-if-v364-no-active-sidecars`; `v90-attributed-youssef-e1-rare-tail-birdnet` is `HOLD-secondary-if-v87-blocked`; v91 is rejected because the route already failed closed; v92 is current pending.
- Decision: no push or competition submission is authorized. If v364 yields no active exact sidecars, v87 is the next high-anchor exact source-export materialization target.

## v368 v87 Exact Source Export Materialization

- Experiment: `v368-v87-exact-source-export-materialization`
- Status: `PREPARED-local-v87-exact-source-export / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_prepare_v368_v87_exact_source_export.py`
- Notebook: `birdclef-2026/notebooks/v368-v87-exact-source-export`
- Report: `experiments/v368_v87_exact_source_export_materialization_20260524.md`
- Structured log: `artifacts/runtime_v368_v87_exact_source_export_materialization_20260524.json`
- Lineage: `artifacts/lineage_v368_v87_exact_source_export_materialization_20260524.json`
- Research question: can the v87 visible-best fallback notebook be materialized into a fail-closed exact-row ProtoSSM/SED source exporter while v364 Run-mode is pending?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_prepare_v368_v87_exact_source_export.py && python3 birdclef-2026/scripts/birdclef_prepare_v368_v87_exact_source_export.py && python3 birdclef-2026/scripts/birdclef_prepare_v368_v87_exact_source_export.py --execute --overwrite`
- Result: local notebook prepared with `CODEX_V368_EXACT_SOURCE_EXPORT_PATCH`, kernel id `junhaochengadjcjh7u7/bc26-v368-v87-exact-source-export`, CPU/no-internet/no-TPU metadata, and exact source export filenames present.
- Decision: no Kaggle push or competition submission is authorized by this step. Run static audit only if v364 finishes without active exact source sidecars.

## v369 v368 Static Source Export Audit

- Experiment: `v369-v368-static-source-export`
- Status: `READY-v368-runmode-source-export-audit / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v369_v368_static_source_export.py`
- Report: `experiments/v369_v368_static_source_export_20260524.md`
- Structured log: `artifacts/runtime_v369_v368_static_source_export_20260524.json`
- Output: `experiments/v369_v368_static_source_export_20260524.csv`
- Research question: does the v368 v87 materializer contain the required fail-closed exact-row source-export guards before any Kaggle Run-mode push?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v369_v368_static_source_export.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v369_v368_static_source_export.py`
- Result: 18 checks passed with 0 blockers; final submission line `6568`, patch marker line `6571`, marker count `2`.
- Decision: v368 may be pushed for Kaggle Run-mode source/schema proof only. It is not a scored candidate and must not be real-submitted.
- Next recommended action: build a guarded v368 Run-mode push/audit pair, verify live pending count is 0, push only the kernel, then fetch outputs and run a source gate.

## v370 v368 Run-mode Push and Waiting Gate

- Experiment: `v370-v368-runmode-push-and-wait`
- Status: `WAIT-running / RUNMODE-PUSHED / NO-COMPETITION-SUBMIT`
- Scripts: `scripts/push_v368_after_v369_gate.py`, `scripts/audit_v368_runmode.py`
- Reports: `experiments/v368_after_v369_push_gate_status.md`, `experiments/v368_runmode_status.md`
- Structured logs: `artifacts/runtime_v368_runmode_status.json`, `artifacts/lineage_v368_runmode_status.json`
- Research question: after v369 static readiness, can v368 be safely pushed to Kaggle Run-mode for source/schema proof without making a real competition submission?
- Validation: `python3 -m py_compile scripts/push_v368_after_v369_gate.py scripts/audit_v368_runmode.py && python3 scripts/push_v368_after_v369_gate.py --write && python3 scripts/push_v368_after_v369_gate.py --write --execute && python3 scripts/audit_v368_runmode.py --fetch-if-complete --write`
- Result: push gate accepted the Kaggle kernel push for `junhaochengadjcjh7u7/bc26-v368-v87-exact-source-export` with `live_pending_count=0`, CPU/no-internet/no-TPU metadata, and no competition-submit path. Immediate audit status is `RUNNING`, fetched `False`.
- Decision: keep waiting; do not real-submit v368 or use it as a source candidate until `scripts/audit_v368_runmode.py --fetch-if-complete --write` reaches a terminal READY/HOLD/REJECT state.
- Next recommended action: poll v368 Run-mode output while screening independent fallback candidates.

### v370 Monitor Update

- Latest poll: `2026-05-24 12:56:46 UTC`
- Status: `READY-v368-runmode-failclosed-source-export-proof / Fetched=True / runtime=174s / NO-COMPETITION-SUBMIT`
- Output: `submission.csv` is schema-valid with 3 sample rows; `v368_exact_source_export_summary.json` reports `active=false`, reason `fail_closed_no_test_soundscapes`, and `exported=[]`.
- Decision: v368 is a safe Run-mode proof but not a source candidate. Do not use it for a downstream candidate; continue with v90 secondary route.

## v371 v368 Source Gate

- Experiment: `v371-v368-source-gate`
- Status: `HOLD-v368-failclosed-no-active-source-sidecars / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v371_v368_source_gate.py`
- Report: `experiments/v371_v368_source_gate_20260524.md`
- Structured log: `artifacts/runtime_v371_v368_source_gate_20260524.json`
- Output: `experiments/v371_v368_source_gate_20260524.csv`
- Research question: once v368 Run-mode outputs are fetched, do its exact-row ProtoSSM/SED source sidecars provide non-identical, schema-safe source diversity worth a downstream local source-agreement experiment?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v371_v368_source_gate.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v371_v368_source_gate.py`
- Result: v368 output is fetched and schema-valid, but exact source sidecars are absent because `v368_exact_source_export_summary.json` reports `fail_closed_no_test_soundscapes`.
- Decision: do not keep polling v368 for sidecars. Screen and prepare the next independent fallback candidate.

## v372 v90 Backup Readiness

- Experiment: `v372-v90-backup-readiness`
- Status: `READY-v90-secondary-source-export-materialization / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v372_v90_backup_readiness.py`
- Report: `experiments/v372_v90_backup_readiness_20260524.md`
- Structured log: `artifacts/runtime_v372_v90_backup_readiness_20260524.json`
- Output: `experiments/v372_v90_backup_readiness_20260524.csv`
- Research question: if v368 produces no usable active exact sidecars, is v90 ready as a secondary exact-source-export materialization target despite BirdNET dependency risk?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v372_v90_backup_readiness.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v372_v90_backup_readiness.py`
- Result: 12 checks passed with 0 blockers. Risk notes are `birdnet_dependency_path` and `birdnet_can_fail_to_zero`, but model source metadata declares `shadiakiki1/birdnet-analyzer/TfLite/birdnet_global_6k_v2.4_model_fp32-1/3`, CPU/no-internet/no-TPU metadata is present, and ProtoSSM/SED branch outputs plus `df_proto/df_sed` are available.
- Decision: v90 may be materialized as a secondary/high-information exact-source-export route if v368 yields no active sidecars. It is not a scored candidate and must not be real-submitted.

## v373 v90 Exact Source Export Materialization

- Experiment: `v373-v90-exact-source-export-materialization`
- Status: `PREPARED-local-v90-exact-source-export / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_prepare_v373_v90_exact_source_export.py`
- Notebook: `birdclef-2026/notebooks/v373-v90-exact-source-export`
- Report: `experiments/v373_v90_exact_source_export_materialization_20260524.md`
- Structured log: `artifacts/runtime_v373_v90_exact_source_export_materialization_20260524.json`
- Lineage: `artifacts/lineage_v373_v90_exact_source_export_materialization_20260524.json`
- Research question: can the v90 secondary BirdNET route be materialized into a fail-closed exact-row ProtoSSM/SED source exporter after v368 completed without active exact sidecars?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_prepare_v373_v90_exact_source_export.py && python3 birdclef-2026/scripts/birdclef_prepare_v373_v90_exact_source_export.py && python3 birdclef-2026/scripts/birdclef_prepare_v373_v90_exact_source_export.py --execute --overwrite`
- Result: local notebook prepared with `CODEX_V373_EXACT_SOURCE_EXPORT_PATCH`, kernel id `junhaochengadjcjh7u7/bc26-v373-v90-exact-source-export`, CPU/no-internet/no-TPU metadata, and exact source export filenames present.
- Decision: no Kaggle push or competition submission is authorized by this step. Next gate is a static source-export audit.

## v374 v373 Static Source Export Audit

- Experiment: `v374-v373-static-source-export`
- Status: `READY-v373-runmode-source-export-audit / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v374_v373_static_source_export.py`
- Report: `experiments/v374_v373_static_source_export_20260524.md`
- Structured log: `artifacts/runtime_v374_v373_static_source_export_20260524.json`
- Output: `experiments/v374_v373_static_source_export_20260524.csv`
- Research question: does the v373 v90 materializer contain the required fail-closed exact-row source-export guards before any Kaggle Run-mode push?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v374_v373_static_source_export.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v374_v373_static_source_export.py`
- Result: 19 checks passed with 0 blockers; final write line `2099`, patch marker line `2147`, marker count `2`.
- Decision: v373 may be pushed for Kaggle Run-mode source/schema proof only. It is not a scored candidate and must not be real-submitted.
- Next recommended action: build a guarded v373 Run-mode push/audit pair, verify live pending count is 0, push only the kernel, then fetch outputs and run a source gate.

## v375 v373 Run-mode Push and Waiting Gate

- Experiment: `v375-v373-runmode-push-and-wait`
- Status: `WAIT-running / RUNMODE-PUSHED / NO-COMPETITION-SUBMIT`
- Scripts: `scripts/push_v373_after_v374_gate.py`, `scripts/audit_v373_runmode.py`
- Reports: `experiments/v373_after_v374_push_gate_status.md`, `experiments/v373_runmode_status.md`
- Structured logs: `artifacts/runtime_v373_runmode_status.json`, `artifacts/lineage_v373_runmode_status.json`
- Research question: after v374 static readiness, can v373 be safely pushed to Kaggle Run-mode for source/schema proof without making a real competition submission?
- Validation: `python3 -m py_compile scripts/push_v373_after_v374_gate.py scripts/audit_v373_runmode.py && python3 scripts/push_v373_after_v374_gate.py --write && python3 scripts/push_v373_after_v374_gate.py --write --execute && python3 scripts/audit_v373_runmode.py --fetch-if-complete --write`
- Result: push gate accepted the Kaggle kernel push for `junhaochengadjcjh7u7/bc26-v373-v90-exact-source-export` with `live_pending_count=0`, CPU/no-internet/no-TPU metadata, and no competition-submit path. Immediate audit status is `RUNNING`, fetched `False`.
- Decision: keep waiting; do not real-submit v373 or use it as a source candidate until `scripts/audit_v373_runmode.py --fetch-if-complete --write` reaches a terminal READY/HOLD/REJECT state.
- Next recommended action: poll v373 Run-mode output while screening independent fallback candidates.

### v375 Monitor Update

- Latest poll: `2026-05-24 13:14:34 UTC`
- Status: `WAIT-running / Fetched=False / NO-COMPETITION-SUBMIT`
- Decision: keep waiting; v373 output is not fetched yet.

### v375 Resolution Update

- Latest poll: `2026-05-24 13:22:39 UTC`
- Status: `READY-v373-runmode-failclosed-source-export-proof / Fetched=True / runtime=342s / NO-COMPETITION-SUBMIT`
- Output: `submission.csv` is schema-valid with 3 sample rows. Diagnostic sidecars were fetched, but `v373_exact_source_export_summary.json` reports `active=false`, reason `fail_closed_no_test_soundscapes`, and `exported=[]`.
- Decision: v373 is a safe Run-mode proof but not a source candidate. Run a source gate before any downstream use.

## v376 Post Exact-export Strategy Audit

- Experiment: `v376-post-exact-export-strategy`
- Status: `READY-next-clean-distillation-design / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v376_post_exact_export_strategy.py`
- Report: `experiments/v376_post_exact_export_strategy_20260524.md`
- Structured log: `artifacts/runtime_v376_post_exact_export_strategy_20260524.json`
- Output: `experiments/v376_post_exact_export_strategy_20260524.csv`
- Research question: after repeated exact-source-export Run-mode proofs failed closed, which non-exact-export route is worth the next engineering step under the objective's promotion and rule-risk constraints?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v376_post_exact_export_strategy.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v376_post_exact_export_strategy.py`
- Result: 5 routes audited. v103 remains strongest local proxy but is held for unknown-license risk; v107 is clean but weak; v302 triad improves mean but worsens fold variance; v340 is rejected for fold risk; v343 lift is too small. `class_coverage.csv` has 3 strong follow-up labels: `47158son17`, `516975`, `116570`.
- Decision: stop spending new pushes on exact-source-export proofs unless v373 produces active sidecars. Next local experiment should design a v107-clean-substrate distillation/rescue probe using v103 only as mechanism/teacher signal and emit fold variance, weak-class, and correlation evidence.

## v377 v107 Teacher Signal Probe

- Experiment: `v377-v107-teacher-signal-probe`
- Status: `PROMOTE-v107-teacher-signal-local-candidate / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v377_v107_teacher_signal.py`
- Report: `experiments/v377_v107_teacher_signal_probe_20260524.md`
- Structured log: `artifacts/runtime_v377_v107_teacher_signal_probe_20260524.json`
- Output: `experiments/v377_v107_teacher_signal_probe_20260524.csv`
- Research question: can a strictly local, label-verified rescue on the license-clean v107 substrate absorb limited v103 teacher signal on class-coverage follow-up labels without violating macro, weak-class, fold-variance, or diversity gates?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v377_v107_teacher_signal.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v377_v107_teacher_signal.py`
- Result: 150 local candidates screened. Best candidate `followup7:positive_rank_guard:w0.3:rm0.0:d0.0` improves local proxy macro from `0.97736356` to `0.98367415` (`+0.00631060`), strong-class mean AUC by `+0.04515569`, follow-up mean AUC by `+0.01983330`, and keeps top5 hit at `0.50684932`.
- Risk: fold std worsens by `+0.00533782` and corr vs v107 remains `0.99971980`; this is not a current real-submit candidate.
- Decision: promote only to local materialization/rebuildability audit. No Kaggle push or competition submission is authorized.

## v378 v373 Source Gate

- Experiment: `v378-v373-source-gate`
- Status: `HOLD-v373-failclosed-no-active-source-sidecars / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v378_v373_source_gate.py`
- Report: `experiments/v378_v373_source_gate_20260524.md`
- Structured log: `artifacts/runtime_v378_v373_source_gate_20260524.json`
- Output: `experiments/v378_v373_source_gate_20260524.csv`
- Research question: after v373 Run-mode completed, do its exported BirdNET/ProtoSSM/SED sidecars provide active exact-test-row source diversity worth a source-agreement experiment?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v378_v373_source_gate.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v378_v373_source_gate.py`
- Result: final `submission.csv` is sample-schema valid, but summary says `active=false`, reason `fail_closed_no_test_soundscapes`, and sidecars are diagnostic train-row files rather than active exact-test source exports.
- Decision: do not use v373 sidecars for source agreement. Continue with the v377 clean-substrate teacher-signal materialization audit.

## v379 v377 Deployable Distillation Probe

- Experiment: `v379-v377-deployable-distill`
- Status: `PROMOTE-v379-deployable-v377-distill / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v379_v377_deployable_distill.py`
- Report: `experiments/v379_v377_deployable_distill_20260524.md`
- Structured log: `artifacts/runtime_v379_v377_deployable_distill_20260524.json`
- Output: `experiments/v379_v377_deployable_distill_20260524.csv`
- Research question: can the v377 teacher movement be distilled into hidden-test-computable features from the license-clean v107 branch, train-soundscape priors, and temporal context, so that no v103 output is needed at inference time?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v379_v377_deployable_distill.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v379_v377_deployable_distill.py`
- Result: 384 deployable-distill candidates screened. Best candidate `alpha0.01_delta_bw0.7_d0_pr0` improves local proxy macro from `0.97736356` to `0.97832804` (`+0.00096449`), improves follow-up weak mean AUC by `+0.00303125`, improves top1 from `0.27397260` to `0.32876712`, keeps top5 at `0.50684932`, and lowers fold std by `-0.00022659`.
- Inference policy: uses v107 scores/ranks, train_soundscape site-hour priors, row_id temporal context, and fixed coefficients. v103 is used only to define the local distillation target, not as a runtime input.
- Risk: macro and weak-class gains are below the primary numeric gates, and corr vs v107 remains `0.99996142`; promotion rests on the lower fold variance gate.
- Decision: promote to a static notebook materializer audit only. No Kaggle push or competition submission is authorized.

## v380 v379 Static Materializer

- Experiment: `v380-v379-static-materializer`
- Status: `READY-v380-static-materializer-audit / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_prepare_v380_v379_static_materializer.py`
- Notebook: `birdclef-2026/notebooks/v380-v379-static-distill`
- Report: `experiments/v380_v379_static_materializer_20260524.md`
- Structured log: `artifacts/runtime_v380_v379_static_materializer_20260524.json`
- Lineage: `artifacts/lineage_v380_v379_static_materializer_20260524.json`
- Spec: `experiments/v380_v379_static_distill_spec.json`
- Local materialized submission: `experiments/v380_v379_static_distill_local_submission.csv`
- Research question: can the v379 deployable-distill candidate be materialized as a static, CPU-only, no-internet v107 notebook patch with fixed coefficients and no diagnostic teacher runtime dependency?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_prepare_v380_v379_static_materializer.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_prepare_v380_v379_static_materializer.py --overwrite`
- Result: static audit has `block_count=0`. Local fixed-coefficient materialization improves macro from `0.97736356` to `0.97896476` (`+0.00160120`), keeps top5 at `0.50684932`, lowers fold std by `-0.00022659`, and improves follow-up weak mean AUC by `+0.00503235`.
- Runtime/rules posture: metadata remains CPU-only/no-internet/no-TPU and keeps clean v107 sources (`rishikeshjani/perch-onnx-for-birdclef-2026`, Google Perch CPU model). Patch uses only v107 submission, competition train soundscape labels, row_id context, and fixed coefficients.
- Risk: corr vs v107 remains `0.99994875`; local fixed-coefficient scoring is train-like proxy and needs Run-mode schema/runtime proof before any real submission.
- Decision: v380 is ready for a guarded Run-mode push/audit pair, not a competition submission.

## v381 v380 Run-mode Push and Waiting Gate

- Experiment: `v381-v380-runmode-push-and-wait`
- Status: `WAIT-running / RUNMODE-PUSHED / NO-COMPETITION-SUBMIT`
- Scripts: `scripts/push_v380_after_v380_gate.py`, `scripts/audit_v380_runmode.py`
- Reports: `experiments/v380_after_v380_push_gate_status.md`, `experiments/v380_runmode_status.md`
- Structured logs: `artifacts/runtime_v380_runmode_status.json`, `artifacts/lineage_v380_runmode_status.json`
- Research question: after v380 static readiness, can v380 be safely pushed to Kaggle Run-mode for schema/runtime proof without making a real competition submission?
- Validation: `python3 -m py_compile scripts/push_v380_after_v380_gate.py scripts/audit_v380_runmode.py && python3 scripts/push_v380_after_v380_gate.py --write && python3 scripts/push_v380_after_v380_gate.py --write --execute && python3 scripts/audit_v380_runmode.py --fetch-if-complete --write`
- Result: push gate accepted the Kaggle kernel push for `junhaochengadjcjh7u7/bc26-v380-v379-static-distill` with live pending count `0`, CPU/no-internet/no-TPU metadata, clean v107 sources, and no competition-submit path. Immediate audit status is `RUNNING`, fetched `False`.
- Decision: keep waiting; do not real-submit v380 or treat it as final until `scripts/audit_v380_runmode.py --fetch-if-complete --write` reaches READY/HOLD/REJECT.

### v381 Monitor Update

- Latest poll: `2026-05-24 13:46:20 UTC`
- Status: `WAIT-running / Fetched=False / NO-COMPETITION-SUBMIT`
- Decision: keep waiting; v380 output is not fetched yet.

### v381 Resolution Update

- Latest poll: `2026-05-24 13:48:39 UTC`
- Status: `REJECT-v380-runmode-failed / Fetched=False / NO-COMPETITION-SUBMIT`
- Fetched after error: `submission.csv` and kernel log were available. The log shows v107 completed dry-run and wrote 120 train-soundscape fallback rows, then v380 patch failed with `RuntimeError: v380 refuses to run: v107 anchor row order does not match sample`.
- Decision: v380 static idea remains useful, but this Run-mode materialization is rejected. Repair with a dry-run-tolerant patch that preserves real sample-row guards.

## v382 v380 Optimism Stress Audit

- Experiment: `v382-v380-optimism-stress`
- Status: `READY-v380-optimism-stress-pass / RUNMODE-ONLY / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v382_v380_optimism_stress.py`
- Report: `experiments/v382_v380_optimism_stress_20260524.md`
- Structured log: `artifacts/runtime_v382_v380_optimism_stress_20260524.json`
- Output: `experiments/v382_v380_optimism_stress_20260524.csv`
- Research question: is the v380 full-coefficient materialization's local macro promotion mostly supported by blocked v379 OOF behavior, or is it too optimistic to continue toward Run-mode proof?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v382_v380_optimism_stress.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v382_v380_optimism_stress.py`
- Result: v379 blocked OOF macro gain is `+0.00096449`, v380 full-coef macro gain is `+0.00160120`, optimism gap is `+0.00063671`. Weak optimism gap is `+0.00200110`. Both OOF and full-coef views have non-worse fold std and no top5 regression.
- Decision: optimism is not large enough to stop Run-mode proof, but this remains Run-mode-only evidence. A separate guarded competition-submit gate is still required before any real submission.

## v383 v380 Dry-run-tolerant Materializer and Run-mode Gate

- Experiment: `v383-v380-dryrun-tolerant`
- Status: `WAIT-running / RUNMODE-PUSHED / NO-COMPETITION-SUBMIT`
- Scripts: `birdclef-2026/scripts/birdclef_prepare_v383_v380_dryrun_tolerant.py`, `scripts/push_v383_after_v383_gate.py`, `scripts/audit_v383_runmode.py`
- Notebook: `birdclef-2026/notebooks/v383-v380-dryrun-tolerant`
- Reports: `experiments/v383_v380_dryrun_tolerant_20260524.md`, `experiments/v383_after_v383_push_gate_status.md`, `experiments/v383_runmode_status.md`
- Structured logs: `artifacts/runtime_v383_v380_dryrun_tolerant_20260524.json`, `artifacts/lineage_v383_v380_dryrun_tolerant_20260524.json`, `artifacts/runtime_v383_runmode_status.json`, `artifacts/lineage_v383_runmode_status.json`
- Research question: can the v380 materializer be repaired so Kaggle Run-mode dry-run train-row fallback no longer crashes while preserving real sample-row guards and the clean v107 runtime policy?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_prepare_v383_v380_dryrun_tolerant.py scripts/push_v383_after_v383_gate.py scripts/audit_v383_runmode.py && python3 birdclef-2026/scripts/birdclef_prepare_v383_v380_dryrun_tolerant.py --overwrite && python3 scripts/push_v383_after_v383_gate.py --write && python3 scripts/push_v383_after_v383_gate.py --write --execute && python3 scripts/audit_v383_runmode.py --fetch-if-complete --write`
- Result: static audit has `block_count=0`, local macro gain remains `+0.00160120`, fold std delta remains `-0.00022659`, and push gate accepted Run-mode for `junhaochengadjcjh7u7/bc26-v383-v380-dryrun-tolerant`. Immediate audit status is `RUNNING`, fetched `False`.
- Decision: keep waiting; do not real-submit v383 or treat it as final until `scripts/audit_v383_runmode.py --fetch-if-complete --write` reaches READY/HOLD/REJECT.

### v383 Monitor Update

- Latest poll: `2026-05-24 13:55:15 UTC`
- Status: `WAIT-running / Fetched=False / NO-COMPETITION-SUBMIT`
- Decision: keep waiting; v383 output is not fetched yet.

## v384 v383 Submit-readiness Audit

- Experiment: `v384-v383-submit-readiness`
- Status: `WAIT-v383-submit-readiness-blocked / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v384_v383_submit_readiness.py`
- Report: `experiments/v384_v383_submit_readiness_20260524.md`
- Structured log: `artifacts/runtime_v384_v383_submit_readiness_20260524.json`
- Output: `experiments/v384_v383_submit_readiness_20260524.csv`
- Research question: does v383 have enough Run-mode, static, promotion, optimism, quota, and pending-submission evidence to even consider a separate real competition-submit gate?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v384_v383_submit_readiness.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v384_v383_submit_readiness.py`
- Result: blocker count `1`; the only blocker is `v383_runmode_ready`. Static audit, macro gate, top5 non-regression, fold std, optimism stress, live pending, visible quota, and no-submit checks pass.
- Decision: no real submission is authorized. Re-run after v383 Run-mode reaches READY/HOLD/REJECT.

### v383 Resolution Update

- Latest audit: `2026-05-24 14:18:42 UTC`
- Status: `READY-v383-runmode-dryrun-runtime-proof / NO-COMPETITION-SUBMIT`
- Runtime: `346` seconds, under target `4200` and hard cap `5400`.
- Output proof: Run-mode output directory contains `submission.csv`, `submission_v107_anchor.csv`, `v383_static_distill_diagnostics.csv`, `v383_static_distill_summary.csv`, and kernel log. Dry-run schema has `120` rows and `235` columns, sample columns match, no duplicate row_id, no NaN/inf, predictions are in range, and the expected train-row dry-run mismatch is tolerated.
- Decision: v383 Run-mode is no longer waiting. It is a submit candidate only for a separate guarded real competition-submit gate.

### v384 Resolution Update

- Latest audit: `2026-05-24 14:37:41 UTC`
- Status: `READY-v383-submit-readiness-AWAIT-EXPLICIT-SUBMIT-GATE / NO-SUBMIT`
- Result: blocker count `0`. Run-mode decision is `READY-v383-runmode-dryrun-runtime-proof`; static decision is `READY-v383-dryrun-tolerant-static-audit-NO-PUSH-NO-SUBMIT`; optimism stress decision is `READY-v380-optimism-stress-pass-RUNMODE-ONLY-NO-SUBMIT`.
- Gate evidence: macro gate passes with gain `+0.00160120`; top5 has no regression; fold std delta is `-0.00022659`; live pending submissions are `0`; visible submissions today are `2`.
- Decision: v383 is currently the only real-submit-ready candidate in this lane, but a competition submission still requires explicit user authorization plus fresh final checks.

## v385 v383 Final Submit Gate

- Experiment: `v385-v383-final-submit-gate`
- Status: `READY-v385-v383-final-submit-gate / SUBMITTED=False`
- Script: `birdclef-2026/scripts/birdclef_guard_v385_v383_final_submit.py`
- Report: `experiments/v385_v383_final_submit_gate_20260524.md`
- Structured log: `artifacts/runtime_v385_v383_final_submit_gate_20260524.json`
- Research question: is v383 ready for a real BirdCLEF 2026 competition submission after fresh Run-mode, readiness, quota, duplicate, metadata, and promotion-gate checks?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_guard_v385_v383_final_submit.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_guard_v385_v383_final_submit.py`
- Result: blocker count `0`; live pending `0`; visible submissions today `2`; v383 kernel status `COMPLETE`; duplicate v383 submission not found. The dry-run did not submit.
- Decision: v383 remains real-submit-ready, but executing the submit path still requires explicit user authorization with `--execute --confirm-submit-v383`.

## v386 v383 Param Stress

- Experiment: `v386-v383-param-stress`
- Status: `PROMOTE-v386-param-stress-candidate / LOCAL-ONLY / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v386_v383_param_stress.py`
- Report: `experiments/v386_v383_param_stress_20260524.md`
- Structured log: `artifacts/runtime_v386_v383_param_stress_20260524.json`
- Output: `experiments/v386_v383_param_stress_20260524.csv`
- Research question: can stricter prior-rank/delta/blend gates improve the v383 fixed-coefficient distill candidate's robustness without changing the underlying CV split or runtime feature family?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v386_v383_param_stress.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v386_v383_param_stress.py`
- Result: screened `300` parameter candidates. Best local candidate is `blend1_delta0_pr0_scale1.25`, improving macro from `0.97736356` to `0.98028181` (`+0.00291826`), lowering fold std by `-0.00083026`, improving weak follow-up AUC by `+0.00917166`, keeping top5 unchanged at `0.50684932`, and corr vs anchor `0.99983650`.
- Decision: promote for static materialization only; do not real-submit from local parameter stress.

## v387 v386 Static Materializer and Run-mode Gate

- Experiment: `v387-v386-static-materializer`
- Status: `WAIT-running / RUNMODE-PUSHED / NO-COMPETITION-SUBMIT`
- Scripts: `birdclef-2026/scripts/birdclef_prepare_v387_v386_static_materializer.py`, `scripts/push_v387_after_v387_gate.py`, `scripts/audit_v387_runmode.py`
- Notebook: `birdclef-2026/notebooks/v387-v386-static-distill`
- Reports: `experiments/v387_v386_static_materializer_20260524.md`, `experiments/v387_after_v387_push_gate_status.md`, `experiments/v387_runmode_status.md`
- Structured logs: `artifacts/runtime_v387_v386_static_materializer_20260524.json`, `artifacts/lineage_v387_v386_static_materializer_20260524.json`, `artifacts/runtime_v387_runmode_status.json`, `artifacts/lineage_v387_runmode_status.json`
- Research question: can the v386 parameter-stressed v383 route be materialized as a static CPU-only notebook while preserving the dry-run tolerant real sample-row guard?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_prepare_v387_v386_static_materializer.py scripts/push_v387_after_v387_gate.py scripts/audit_v387_runmode.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_prepare_v387_v386_static_materializer.py --overwrite && python3 scripts/push_v387_after_v387_gate.py --write && python3 scripts/push_v387_after_v387_gate.py --write --execute && python3 scripts/audit_v387_runmode.py --fetch-if-complete --write`
- Result: static audit block count `0`; local macro gain `+0.00291826`; fold std delta `-0.00083026`; Run-mode push accepted for `junhaochengadjcjh7u7/bc26-v387-v386-static-distill`; immediate audit status is `WAIT-running`, fetched `False`.
- Decision: poll v387 Run-mode until READY/HOLD/REJECT. v387 is not a real-submit candidate until Run-mode proof and a separate submit-readiness gate pass.

### v387 Resolution Update

- Latest audit: `2026-05-24 15:05:08 UTC`
- Status: `READY-v387-runmode-dryrun-runtime-proof / NO-COMPETITION-SUBMIT`
- Runtime: `298` seconds, under target `4200` and hard cap `5400`.
- Output proof: Run-mode output directory contains `submission.csv`, `submission_v107_anchor.csv`, `v387_static_distill_diagnostics.csv`, `v387_static_distill_summary.csv`, and kernel log. Dry-run schema has `120` rows and `235` columns, sample columns match, no duplicate row_id, no NaN/inf, predictions are in range, and the expected train-row dry-run mismatch is tolerated.
- Decision: v387 Run-mode is no longer waiting. It can proceed to submit-readiness only after class-risk audit.

## v388 v387 Class-risk Audit

- Experiment: `v388-v387-class-risk`
- Status: `READY-v388-v387-class-risk-pass / LOCAL-ONLY / NO-PUSH / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v388_v387_class_risk.py`
- Report: `experiments/v388_v387_class_risk_20260524.md`
- Structured log: `artifacts/runtime_v388_v387_class_risk_20260524.json`
- Outputs: `experiments/v388_v387_class_risk_20260524.csv`, `experiments/v388_v387_fold_risk_20260524.csv`
- Research question: does the v386-selected v387 candidate pass class-regression and fold-risk checks strongly enough to remain queued behind v383 while Run-mode is pending?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v388_v387_class_risk.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v388_v387_class_risk.py`
- Result: macro gain `+0.00291826`, weak follow-up gain `+0.00917166`, fold std delta `-0.00083026`, top5 unchanged `0.50684932`; class regressions below `-0.001` = `0`, material regressions below `-0.003` = `0`, fold regressions below `-0.001` = `0`.
- Decision: v387 passes local class/fold risk audit; continue to submit-readiness after Run-mode proof.

## v389 v387 Submit-readiness Audit

- Experiment: `v389-v387-submit-readiness`
- Status: `READY-v387-submit-readiness-AWAIT-EXPLICIT-SUBMIT-GATE / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v389_v387_submit_readiness.py`
- Report: `experiments/v389_v387_submit_readiness_20260524.md`
- Structured log: `artifacts/runtime_v389_v387_submit_readiness_20260524.json`
- Output: `experiments/v389_v387_submit_readiness_20260524.csv`
- Research question: does v387 have enough Run-mode, static, promotion, class-risk, quota, duplicate, and pending-submission evidence to even consider a separate real competition-submit gate?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v389_v387_submit_readiness.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v389_v387_submit_readiness.py`
- Result: blocker count `0`; Run-mode decision `READY-v387-runmode-dryrun-runtime-proof`; static decision `READY-v387-v386-static-materializer-audit-NO-PUSH-NO-SUBMIT`; class-risk decision `READY-v388-v387-class-risk-pass-NO-PUSH-NO-SUBMIT`; live pending `0`; visible submissions today `2`; duplicate v387 submission `False`.
- Decision: v387 supersedes v383 as the current stronger submit-ready candidate, but a competition submission still requires explicit user authorization plus fresh final checks.

## v390 v387 Final Submit Gate

- Experiment: `v390-v387-final-submit-gate`
- Status: `SUBMITTED-v387-competition-pending`
- Script: `birdclef-2026/scripts/birdclef_guard_v390_v387_final_submit.py`
- Report: `experiments/v390_v387_final_submit_gate_20260524.md`
- Structured log: `artifacts/runtime_v390_v387_final_submit_gate_20260524.json`
- Research question: is v387 ready for a real BirdCLEF 2026 competition submission after fresh Run-mode, readiness, quota, duplicate, metadata, and promotion-gate checks?
- Validation: `python3 birdclef-2026/scripts/birdclef_guard_v390_v387_final_submit.py && python3 birdclef-2026/scripts/birdclef_guard_v390_v387_final_submit.py --execute --confirm-submit-v387`
- Result: pre-submit gate had blocker count `0`; v387 kernel status `COMPLETE`; live pending `0`; visible submissions today `2`; duplicate v387 submission not found; metadata is CPU/no-internet/no-TPU. Explicit user authorization was then used to submit v387.
- Submit result: Kaggle ref `52991496`, submitted at `2026-05-24 15:21:09.597000`, latest status `SubmissionStatus.PENDING`, public score blank.
- Decision: wait for v387 public score before any further real competition submission. v391 safe_final Run-mode may continue, but it must not be submitted while v387 is pending.

## v391 v386 Safe Static Materializer and Run-mode Gate

- Experiment: `v391-v386-safe-static-materializer`
- Status: `WAIT-running / RUNMODE-PUSHED / SAFE_FINAL-CANDIDATE / NO-COMPETITION-SUBMIT`
- Scripts: `birdclef-2026/scripts/birdclef_prepare_v391_v386_safe_static_materializer.py`, `scripts/push_v391_after_v391_gate.py`, `scripts/audit_v391_runmode.py`
- Notebook: `birdclef-2026/notebooks/v391-v386-safe-static-distill`
- Reports: `experiments/v391_v386_safe_static_materializer_20260524.md`, `experiments/v391_after_v391_push_gate_status.md`, `experiments/v391_runmode_status.md`
- Structured logs: `artifacts/runtime_v391_v386_safe_static_materializer_20260524.json`, `artifacts/lineage_v391_v386_safe_static_materializer_20260524.json`, `artifacts/runtime_v391_runmode_status.json`, `artifacts/lineage_v391_runmode_status.json`
- Research question: can a safe_final v386 parameter set reduce active cells and fold variance while keeping macro/weak gains, and be pushed for Run-mode proof without making a real submission?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_prepare_v391_v386_safe_static_materializer.py scripts/push_v391_after_v391_gate.py scripts/audit_v391_runmode.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_prepare_v391_v386_safe_static_materializer.py --overwrite && python3 scripts/push_v391_after_v391_gate.py --write && python3 scripts/push_v391_after_v391_gate.py --write --execute && python3 scripts/audit_v391_runmode.py --fetch-if-complete --write`
- Result: static audit block count `0`; selected params `blend=1.0`, `min_delta=0.0025`, `min_prior_rank=0.7`, `delta_scale=1.25`; local macro gain `+0.00282022`; fold std delta `-0.00188085`; weak follow-up gain `+0.00886356`; active cells `98`; top5 unchanged. Run-mode push accepted for `junhaochengadjcjh7u7/bc26-v391-v386-safe-static-distill`; latest audit status `WAIT-running`, fetched `False`.
- Decision: v391 is the current safe_final candidate, pending Run-mode proof. Do not real-submit v391 while v387 ref `52991496` is pending.

### v391 Resolution Update

- Latest audit: `2026-05-24 15:27:02 UTC`
- Status: `READY-v391-runmode-dryrun-runtime-proof / SAFE_FINAL-CANDIDATE / NO-COMPETITION-SUBMIT`
- Runtime: `325` seconds, under target `4200` and hard cap `5400`.
- Output proof: Run-mode output directory contains `submission.csv`, `submission_v107_anchor.csv`, `v391_static_distill_diagnostics.csv`, `v391_static_distill_summary.csv`, and kernel log. Dry-run schema passed the same finite/range/diagnostic checks and tolerated the expected train-row dry-run mismatch.
- Decision: v391 is now Run-mode ready as safe_final, but cannot be submitted while v387 ref `52991496` is pending.

## v392 Final Portfolio Audit

- Experiment: `v392-final-portfolio`
- Status: `WAIT-safe-final-runmode-v391-bold-v387-ready`
- Script: `birdclef-2026/scripts/birdclef_audit_v392_final_portfolio.py`
- Report: `experiments/v392_final_portfolio_20260524.md`
- Structured log: `artifacts/runtime_v392_final_portfolio_20260524.json`
- Research question: do we currently have a safe_final and bold_final pair that satisfies the final-candidate rule without making a real competition submission?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v392_final_portfolio.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v392_final_portfolio.py`
- Result: `bold_final` is v387 with final gate ready and now submitted/pending; `safe_final` is v391 with static audit pass, lower fold std delta than v387, fewer active cells, and Run-mode still running.
- Result update: after v391 Run-mode completion, portfolio audit reports `READY-final-portfolio-safe-v391-bold-v387` with block count `0`.
- Decision: wait for v387 score. v391 is the safe_final fallback, but no additional real submission is allowed while v387 is pending.

## v387 Submission Monitor

- Experiment: `v387-submission-monitor`
- Status: `WAIT-pending-public-score`
- Script: `scripts/monitor_v387_submission.py`
- Reports: `experiments/v387_score_monitor_status.md`, `experiments/submission_result_v387.md`
- Validation: `python3 -m py_compile scripts/monitor_v387_submission.py && python3 scripts/monitor_v387_submission.py --write`
- Result: v387 submission found with ref `52991496`, status `SubmissionStatus.PENDING`, no public score yet, UTC-day visible submissions `3`.
- Decision: do not submit another candidate until v387 resolves.

## v393 v391 Submit-readiness Audit

- Experiment: `v393-v391-submit-readiness`
- Status: `WAIT-v391-submit-readiness-blocked / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v393_v391_submit_readiness.py`
- Report: `experiments/v393_v391_submit_readiness_20260524.md`
- Structured log: `artifacts/runtime_v393_v391_submit_readiness_20260524.json`
- Output: `experiments/v393_v391_submit_readiness_20260524.csv`
- Research question: does v391 have enough Run-mode, static, promotion, class-risk, quota, duplicate, and pending-submission evidence to even consider a separate real competition-submit gate?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v393_v391_submit_readiness.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v393_v391_submit_readiness.py`
- Result: v391 Run-mode is `READY-v391-runmode-dryrun-runtime-proof`; static audit is ready; macro/weak/fold gates pass. Blocker count is `1`, only `no_live_pending`, because v387 ref `52991496` is still pending.
- Decision: hold v391. Re-run submit-readiness only after v387 resolves.

## v394 Safe/Bold Blend Probe

- Experiment: `v394-safe-bold-blend`
- Status: `PROMOTE-v394-safe-bold-blend / LOCAL-ONLY / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_probe_v394_safe_bold_blend.py`
- Report: `experiments/v394_safe_bold_blend_20260524.md`
- Structured log: `artifacts/runtime_v394_safe_bold_blend_20260524.json`
- Output: `experiments/v394_safe_bold_blend_20260524.csv`
- Research question: can a convex blend of the v391 safe_final and v387 bold_final local candidates dominate either endpoint on robustness while v387's real submission is pending?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_probe_v394_safe_bold_blend.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_probe_v394_safe_bold_blend.py`
- Result: screened `21` safe/bold blend weights. The selected portfolio candidate is `safe0.80_bold0.20`, with macro gain `+0.00308164`, fold std delta `-0.00188085`, weak follow-up gain `+0.00968517`, top5 unchanged at `0.50684932`, no material class regression below `-0.003`, and corr vs anchor `0.99994021`.
- Comparison: safe v391 has macro gain `+0.00282022`, fold std delta `-0.00188085`, weak gain `+0.00886356`; bold v387 has macro gain `+0.00291826`, fold std delta `-0.00083026`, weak gain `+0.00917166`.
- Decision: v394 is a stronger local portfolio candidate, but it is not materialized or submitted while v387 ref `52991496` is pending. If v387 fails/ties and slots remain, materialize v394 before considering v391.

## v395 Static-distill Family Failure Audit

- Experiment: `v395-static-distill-failure`
- Status: `RETIRE-static-distill-family / NO-SUBMIT`
- Script: `birdclef-2026/scripts/birdclef_audit_v395_static_distill_failure.py`
- Report: `experiments/v395_static_distill_failure_20260524.md`
- Structured log: `artifacts/runtime_v395_static_distill_failure_20260524.json`
- Output: `experiments/v395_static_distill_failure_20260524.csv`
- Research question: after v387 scored publicly, should any v380/v383/v387/v391/v394 fixed-coefficient static-distill sibling remain submit-eligible?
- Validation: `python3 -m py_compile birdclef-2026/scripts/birdclef_audit_v395_static_distill_failure.py && /usr/bin/time -p python3 birdclef-2026/scripts/birdclef_audit_v395_static_distill_failure.py`
- Result: v387 ref `52991496` completed with public score `0.881`, which is `-0.068` below the visible `0.949` anchor. This invalidates the local static-distill proxy for this family, despite v387's pre-submit local macro gain `+0.00291826`, fold std delta `-0.00083026`, and weak follow-up gain `+0.00917166`.
- Family decision: retire v380/v383/v387 and block v391/v394 from real submission. v391 and v394 are not independent fallbacks because they inherit the same failed fixed-coefficient static-distill mechanism.
- Current goal state: visible best remains `0.949` from v298; Top5 cutoff remains `0.960`; gap to Top5 remains `0.011`; `GOAL_GATE=NOT_REACHED`.
- Next action: do not spend the remaining 2026-05-24 slots on static-distill siblings. Pivot to a non-static-distill, hidden-test-computable route with stronger real-score evidence, or protect the 0.949 visible-best fallback.
