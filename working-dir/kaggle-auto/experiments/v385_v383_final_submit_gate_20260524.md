# v385 v383 Final Submit Gate

Updated: 2026-05-24 14:43:17 UTC

- Decision: `READY-v385-v383-final-submit-gate`
- Blocker count: `0`
- Blockers: `[]`
- Execute requested: `False`
- Submitted: `False`

## Research Question

Is v383 ready for a real BirdCLEF 2026 competition submission after fresh Run-mode, readiness, quota, duplicate, metadata, and promotion-gate checks?

## Evidence

- candidate: `v383-v380-dryrun-tolerant`
- kernel: `junhaochengadjcjh7u7/bc26-v383-v380-dryrun-tolerant`
- kernel_version: `1`
- v383_runmode_decision: `READY-v383-runmode-dryrun-runtime-proof`
- v383_runtime_seconds: `346`
- v384_decision: `READY-v383-submit-readiness-AWAIT-EXPLICIT-SUBMIT-GATE`
- v384_blocker_count: `0`
- v383_static_decision: `READY-v383-dryrun-tolerant-static-audit-NO-PUSH-NO-SUBMIT`
- v383_static_block_count: `0`
- macro_gain: `0.0016012025357819981`
- fold_std_delta: `-0.0002265860787013796`
- weak_followup_gain: `0.00503235082674347`
- corr_vs_v107_anchor: `MISSING`
- metadata_id: `junhaochengadjcjh7u7/bc26-v383-v380-dryrun-tolerant`
- metadata_enable_gpu: `False`
- metadata_enable_tpu: `False`
- metadata_enable_internet: `False`
- live: `{'ok': True, 'pending': 0, 'today_count': 2, 'kernel_status': '{"status": "COMPLETE", "failureMessage": ""}', 'duplicate_scored': False, 'duplicate_pending': False, 'latest': [{'date': '2026-05-24 05:48:20.487000', 'status': 'SubmissionStatus.COMPLETE', 'score': '0.949', 'description': 'v298 taxonomy-context swap over the v289/v288/v285/v87 high-score anchor; allows a tiny rank-6..12 top5-boundary swap only when v288 context and v289 official taxonomy-sibling signals agree, excludes inactive public0952/v296 evidence, CPU-only no-internet'}, {'date': '2026-05-24 04:01:13.187000', 'status': 'SubmissionStatus.COMPLETE', 'score': '0.949', 'description': 'v299 context-frontier swap over the v288/v285/v87 high-score anchor; uses official secondary/file-local context only to swap at most two rank-6/7 frontier classes into top5, keeps top1 immutable, blocks public0952 as positive evidence, CPU-only no-internet'}, {'date': '2026-05-22 07:04:34', 'status': 'SubmissionStatus.COMPLETE', 'score': '0.949', 'description': 'v288 adaptive context finch over the v285/v87 high-score anchor; combines official secondary cooccurrence, file-local context, and conservative margin gates to move non-top5 cells only, with zero top1/top5 drift, CPU-only no-internet'}, {'date': '2026-05-22 04:16:22.473000', 'status': 'SubmissionStatus.COMPLETE', 'score': '0.949', 'description': 'v285 secondary-context stack over the v278/v87 high-score anchor; freezes top1/top5 membership while applying official secondary cooccurrence and file-local context to non-top5 cells, requires active context movement, zero top5 drift, CPU-only no-internet'}, {'date': '2026-05-22 02:08:05.243000', 'status': 'SubmissionStatus.COMPLETE', 'score': '0.949', 'description': 'v278 NFNet active-only fail-closed verifier over the v265/v87 high-score anchor; uses CC0 brendancarlin NFNet checkpoints, removes the failed AVES branch, requires NFNet checkpoint plus smoke/hidden active evidence, CPU-only no-internet'}]}`
- max_today: `4`

## Decision

`READY-v385-v383-final-submit-gate`

This gate does not submit unless both `--execute` and `--confirm-submit-v383` are provided.
