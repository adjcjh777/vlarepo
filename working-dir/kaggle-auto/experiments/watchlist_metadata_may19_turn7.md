# BirdCLEF 2026 Watchlist Metadata Scan - 2026-05-19 Turn 7

Checked at: 2026-05-19 01:53 UTC.

Current live gate:

- Best visible score: `0.949` from v87.
- Top-20 cutoff: `0.953`.
- Top-5 cutoff: `0.958`.
- UTC-day submissions used: `1/5`.
- Goal gate: `NOT_REACHED`.

## Candidate-Diff Pass

Built a score/latest/vote candidate table from Kaggle and compared refs against local experiment/report text. The useful uncovered cluster was not another EoS/V6 near-neighbor, but sidecar / CLAP / router style public references.

Pulled into `/tmp/bc26_scan_may19_turn7`:

| Kernel | CPU | Internet | Main Signal | Static Result |
| --- | --- | --- | --- | --- |
| `nina2025/birdclef-2026-ensemble-of-solutions` | yes | no | direct blend, Model_3/Model_4 | Lower-score public-family reference; not above current v87 anchor. |
| `zeyadmohamadezzat/birdclef-2026-two-branch-perch-sed-sidecar` | yes | no | sidecar + CLAP/CV artifacts | Includes BirdNET model source in metadata; not a clean prize-route without patching/removal. |
| `phyterx/birdclef-2026-v3-cv9245-sidecar-w0-05` | yes | no | CV9245 sidecar | Includes BirdNET references/model path; not a clean direct candidate. |
| `claudedevore/bc26-species-router-v2` | yes | no | species router | Includes BirdNET model source; lower priority because of license/provenance risk. |
| `claudedevore/birdclef-2026-r0947-ted-improved-submit` | yes | no | TED/species improvements | Includes BirdNET model source; score claim below current anchor. |
| `henryszy/bc2026-raunak0946-clap-v53` | yes | no | CLAP INT8 + train-audio-head | Cleanest sidecar source family, but public dry-run exits via sample-shaped quick guard. |
| `lucataco/bc26-henry-clap-v53-fasttop` | yes | no | CLAP INT8 + train-audio-head, full staging path | Cleanest Run-mode evidence for this family; public score signal remains below current anchor. |

## Asset Access

Checked with Kaggle API:

| Dataset | Status |
| --- | --- |
| `konbu17/bird26-train-audio-head-v1` | accessible; contains `head_weights_train_audio.npz`. |
| `habedi/birdclef-2026-clap-int8-bundle` | accessible; contains `clap_audio_int8.onnx`, mel filters, probe config, and probe weights. |
| `chaneyma/birdclef-2026-cv9245-moe-artifacts` | accessible; contains MoE/student artifacts. |
| `tsubasatech/birdclef-2026-snowflake-sed` | accessible; contains two SED ONNX files. |

## Original Output Audit

Downloaded original outputs for:

- `henryszy/bc2026-raunak0946-clap-v53` into `/tmp/bc26_original_clap_v53_output`.
- `lucataco/bc26-henry-clap-v53-fasttop` into `/tmp/bc26_original_clap_fasttop_output`.

Key observations:

- Henry v53 public run used a quick public dry-run guard and wrote a uniform sample-shaped `submission.csv`; it is not useful output evidence.
- Lucataco fasttop ran the full staging path on train dry-run:
  - Perch cache built;
  - ProtoSSM and SED branches produced 240-row train dry-run intermediate files;
  - train-audio-head was used with `uniform blend=0.03`;
  - CLAP sidecar was skipped in dry-run mode because there is no test audio.
- Lucataco final sample-shaped dry-run output is close to v87:
  - Pearson vs v87: `0.989536`;
  - MAD vs v87: `0.000609`.

## Decision

Do not submit a CLAP/sidecar candidate now.

Rationale:

- The cleanest candidate family is still below the current 0.949 anchor by public naming/history (`0946`-style).
- Dry-run final output is a near-neighbor of v87.
- CLAP sidecar does not activate under public Run-mode, so Run-mode cannot prove hidden improvement.
- Several sidecar/router variants include BirdNET model sources and require additional license-compatible patching before any prize-route use.

Keep the CLAP sidecar idea as a possible future local augmentation only if a concrete hidden-test-safe implementation and stronger score rationale appear. Do not spend the 2026-05-19 UTC second slot on this family now.
