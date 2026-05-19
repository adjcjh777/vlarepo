# BirdCLEF 2026 Watchlist Metadata Scan - 2026-05-19 Turn 11

Checked at: 2026-05-19 02:36 UTC.

Current live gate:

- Best visible score: `0.949` from v87.
- Top-20 cutoff: `0.953`.
- Top-5 cutoff: `0.958`.
- Gap to top-20: `0.004`.
- Gap to top-5: `0.009`.
- UTC-day real submissions used before this triage: `1/5`.
- Goal gate: `NOT_REACHED`.

## Candidate Refresh

Pulled a fresh public-kernel scan to `/tmp/bc26_public_scan_turn11.txt`, then selected non-EoS sidecar candidates with either a new CNN/HGNet route, a score-claimed EffV2S branch, or an Alexy CNN inference route not yet fully recorded.

Source and metadata were pulled into `/tmp/bc26_scan_may19_turn11`; original outputs were pulled into `/tmp/bc26_outputs_turn11` for audit only.

## Pulled Candidate Audit

| Kernel | CPU | Internet | Original status | Output evidence | Decision |
| --- | --- | --- | --- | --- | --- |
| `ttahara/birdclef-2026-hgnetv2-b0-baseline-inference` | yes | no | COMPLETE | Metadata depends on `ttahara/birdclef-2026-download-wheels` and `ttahara/birdclef-2026-hgnetv2-b0-baseline-training`. Output `submission.csv` is only `(3,235)` and all prediction values are non-finite, so no scoreable rows were found. | Reject as invalid output. |
| `claudedevore/birdclef-2026-r0946-a2prime-effv2s-submit` | yes | no | COMPLETE | Metadata includes SED, Perch, EffV2S/distill datasets and BirdNET/Perch model sources. Final `submission.csv` is `(3,235)`, close to v87 on sample rows (`corr=0.979803`, `MAD=0.001489`). Side outputs include 240-row SED, ProtoSSM, BirdNET, EffV2S, and blend variants. | Hold source-only; do not submit default or EffV2S blend now. |
| `alexycactus/birdclef-2026-cnn-infer-dataset` | yes | no | COMPLETE | Uses public `alexycactus/birdclef-2026-cnn-fold-checkpoints`; log shows `device=cpu`, 3 folds, fp32, staging fallback on first 16 train soundscapes, 51.2 s for 16 files, output `(192,235)`. | Hold as most interesting CPU CNN source, but not submit as-is. |
| `alexycactus/birdclef-2026-cnn-infer-safe` | no | no | COMPLETE | Metadata has `enable_gpu=true`; log shows `device=cuda GPU=Tesla T4`, 5 folds, output `(192,235)`. | Reject for final constraint: GPU route. |
| `alexycactus/birdclef-2026-cnn-infer-fast` | no | no | COMPLETE | Metadata has `enable_gpu=true`; log shows `device=cuda GPU=Tesla T4`, fp16, 5 folds, output `(192,235)`. | Reject for final constraint: GPU route. |

## Proxy Check

Ran `birdclef-2026/scripts/evaluate_dryrun_proxy.py` on scoreable 192/240-row side outputs and wrote `experiments/v100_sidecar_proxy_scores.csv`.

Key results:

- ClaudeDevore SED sidecar is still strongest on the local 240-row dry-run proxy: `macro_auc=0.99206224`, `micro_auc=0.99865115`, `top5_hit=0.99425287`.
- Alexy CPU dataset CNN is strong on the local 192-row fallback proxy: `macro_auc=0.98988271`, `micro_auc=0.99909419`, `top5_hit=1.0`.
- Alexy GPU safe/fast are nearly identical to the CPU dataset route on proxy (`macro_auc=0.98956-0.98962`) but are not final-eligible because they require GPU.
- ClaudeDevore EffV2S itself is weak on this proxy (`macro_auc=0.57404484`), and adding EffV2S into A2Prime blends lowers macro AUC compared with base 3-way.
- HGNet produced no scoreable prediction file because its output was sample-shaped and non-finite.

## Decision

No real Kaggle submission was made in this turn.

Do not promote v100 as a new submit candidate yet:

- The best proxy signal is the already-known SED sidecar family, not a new independent final route.
- Alexy CPU CNN is interesting and prize-compatible on metadata, but current public output is a dry-run staging fallback over 16 train files and only 3 of 5 folds; hidden-test CPU runtime and full-row output still need direct materialization before any real submission.
- EffV2S is not currently helping the A2Prime family and carries BirdNET source risk in the pulled metadata.
- HGNet is invalid from the pulled public output.

Recommended next action: materialize a private CPU-only Alexy-CNN-derived notebook only if it can run hidden test with full-row output under the 90-minute CPU budget; otherwise continue public scan for non-EoS, non-BirdNET, CPU-only sources with OOF or full hidden-compatible outputs.
