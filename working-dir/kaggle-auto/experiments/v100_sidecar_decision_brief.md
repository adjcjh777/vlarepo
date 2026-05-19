# v100 Sidecar CNN / EffV2S Decision Brief

Candidate family: Alexy CNN inference variants, ClaudeDevore A2Prime EffV2S, and Ttahara HGNetV2 baseline.

Decision: `HOLD - do not submit v100 now`

## Evidence

Positive signals:

- `alexycactus/birdclef-2026-cnn-infer-dataset` is CPU-only, internet-off, and uses a public Kaggle dataset checkpoint source already recorded locally.
- Alexy CPU CNN has a strong local dry-run proxy result: `macro_auc=0.98988271`, `micro_auc=0.99909419`, `top5_hit=1.0`.
- ClaudeDevore's SED sidecar remains strong on the same local proxy: `macro_auc=0.99206224`, `micro_auc=0.99865115`.
- All inspected kernels are public and their pulled original runs are COMPLETE.

Negative signals:

- Alexy CPU CNN public output is a staging fallback: first 16 train soundscapes, `(192,235)`, not hidden-test full-row evidence.
- Alexy CPU CNN loads only 3 folds from `alexycactus/birdclef-2026-cnn-fold-checkpoints`; the GPU safe/fast variants use 5 folds but violate the CPU-only final constraint.
- The Alexy CPU log shows 51.2 seconds for 16 files on Kaggle CPU. This is promising but not enough by itself to prove hidden-test runtime under 90 minutes.
- ClaudeDevore default final `submission.csv` is only `(3,235)` and is near v87 on sample rows (`corr=0.979803`, `MAD=0.001489`).
- ClaudeDevore EffV2S branch has low local proxy quality (`macro_auc=0.57404484`) and a log warning about very low rank correlation with ProtoSSM (`0.053`).
- ClaudeDevore metadata includes the BirdNET analyzer model source, a route already treated locally as license/provenance risk for prize-zone submissions.
- Ttahara HGNet output is `(3,235)` with non-finite prediction values and no scoreable rows.

## Proxy Check

Wrote `experiments/v100_sidecar_proxy_scores.csv`.

Best proxy rows:

- `claudedevore_a2prime_effv2s/submission_sed`: `macro_auc=0.99206224`, `micro_auc=0.99865115`, `top5_hit=0.99425287`.
- `alexycactus_cnn_dataset_cpu/submission`: `macro_auc=0.98988271`, `micro_auc=0.99909419`, `top5_hit=1.0`.
- `claudedevore_a2prime_effv2s/submission_base_3way`: `macro_auc=0.98214004`.
- `claudedevore_a2prime_effv2s/submission_effv2s`: `macro_auc=0.57404484`.

## Decision

Do not use the 2026-05-19 UTC second real-submission slot on this family.

The only candidate worth carrying forward is `alexycactus/birdclef-2026-cnn-infer-dataset` as a CPU CNN source for a possible private materialization. Promotion requires:

- full hidden-test compatible output rather than dry-run staging fallback;
- CPU-only runtime evidence under the 90-minute Kaggle notebook budget;
- checksum/correlation evidence showing it is materially different from v87/v91;
- provenance kept to public, prize-compatible dataset/model sources;
- no GPU-only fold route unless rewritten and verified as CPU-only.

Everything else in this turn is either invalid output, near-neighbor output, GPU-only, or blocked by BirdNET/provenance risk.
