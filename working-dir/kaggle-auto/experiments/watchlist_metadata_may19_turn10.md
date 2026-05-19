# BirdCLEF 2026 Watchlist Metadata Scan - 2026-05-19 Turn 10

Checked at: 2026-05-19 02:26 UTC.

Current live gate:

- Best visible score: `0.949` from v87.
- Top-20 cutoff: `0.953`.
- Top-5 cutoff: `0.958`.
- UTC-day real submissions used: `1/5`.
- Goal gate: `NOT_REACHED`.

## Candidate Refresh

Pulled a fresh public-kernel scan to `/tmp/bc26_public_scan_turn10.txt`, then selected CPU/no-internet candidates that were either latest and not yet fully recorded or score-claimed/near-0.949 but not already in the external registry.

Pulled source/metadata into `/tmp/bc26_scan_may19_turn10` and original outputs into `/tmp/bc26_outputs_turn10` for audit only.

## Pulled Candidate Audit

| Kernel | CPU | Internet | Original status | Output evidence | Decision |
| --- | --- | --- | --- | --- | --- |
| `yaroslavkholmirzayev/v6-0949-replay` | yes | no | COMPLETE | Final `submission.csv` is `(3,235)`, SHA prefix `1db57756a2a44b5f`; sample-row output vs v87 has `corr=0.996729`, `MAD=0.000242`. | Reject as v87 near-neighbor replay. |
| `itshyao/birdclef-2026-s118-gated-g116-delta-launcher` | yes | no | COMPLETE | 1-cell launcher executes `/kaggle/input/datasets/itshyao/birdclef-2026-s118-gated-g116-source/s118_source.ipynb`; this dataset and G116 assets are `403` to current account. Final `submission.csv` is `(3,235)`, close to v87 (`corr=0.986376`, `MAD=0.001088`). G116 side output is only `(12,235)` and was not used because of row mismatch. | Reject for direct promotion: inaccessible source/assets, BirdNET model source in metadata, and final output is a near-neighbor fallback/anchor. |
| `itshyao/birdclef-2026-s120-gated-birdnet-safe-launcher` | yes | no | COMPLETE | 1-cell launcher executes `/kaggle/input/datasets/itshyao/birdclef-2026-s120-gated-birdnet-safe-source/s120_source.ipynb`; source dataset is `403`. Metadata includes BirdNET analyzer model source. Final `submission.csv` is byte-identical to S118. | Reject for direct promotion: inaccessible source and BirdNET license/provenance risk. |
| `mtoshidesu/testbirdclef-2026-v6` | yes | no | COMPLETE | Final `submission.csv` is byte-identical to local v87/v93 (`corr=1.0`, `MAD=0.0`). | Reject as already-covered v87 family. |
| `raunakdey07/birdclef-2026-v6` | yes | no | COMPLETE | Final `submission.csv` is byte-identical to local v87/v93 and Mtoshi V6. | Reject as already-covered v87 family. |

## Proxy Check

Ran `birdclef-2026/scripts/evaluate_dryrun_proxy.py` on available 240-row dry-run side outputs and wrote `experiments/v99_v6_s118_proxy_scores.csv`.

Key results:

- Shared SED side output: `macro_auc=0.99206224`, `micro_auc=0.99865115`, `top5_hit=0.99425287`.
- Raunak/Mtoshi/Itshyao ProtoSSM side output: `macro_auc=0.98062194`, `micro_auc=0.93313195`.
- Yaroslav ProtoSSM side output: `macro_auc=0.98278611`, `micro_auc=0.95780924`.
- S118 G116 side output is only 12 rows; it has high micro/top-hit on that tiny slice but macro `0.33311688`, which is not usable evidence.

## Decision

Do not use the 2026-05-19 UTC second real-submission slot on this scan.

Rationale:

- The visible `0949` replay is not a new route; it stays almost identical to v87 on the only score-shaped rows available.
- Mtoshi/Raunak V6 are literally the current v87 sample output.
- S118/S120 depend on private/inaccessible source notebooks or assets, and S120/S118 metadata still attaches the previously blocked BirdNET model source. Their final submission falls back to the anchor output rather than incorporating a valid full-row G116 branch.

