# BirdCLEF 2026 Watchlist Metadata Scan - 2026-05-19 Turn 9

Checked at: 2026-05-19 02:19 UTC.

Current live gate at the start of this scan:

- Best visible score: `0.949` from v87.
- Top-20 cutoff: `0.953`.
- Top-5 cutoff: `0.958`.
- UTC-day real submissions used: `1/5`.
- Goal gate: `NOT_REACHED`.

## Candidate Refresh

Pulled latest public-kernel metadata with the local BirdCLEF scanner and inspected newly active or previously unscored CPU/no-internet candidates. Source copies were pulled into `/tmp/bc26_scan_may19_turn9` and original outputs into `/tmp/bc26_outputs_turn9` for audit only.

## Pulled Candidate Audit

| Kernel | CPU | Internet | Original status | Output evidence | Decision |
| --- | --- | --- | --- | --- | --- |
| `jguevarag/08-winning-tta-submission-pipeline` | yes | no | COMPLETE | `submission.csv` is `(3,235)`, all zeros, SHA prefix `b61f628d452fb004`. Log shows fallback sample file creation, failed state-dict load from `04-cnn-efficientnet-training`, one dummy segment, then sample reindex. | Reject for submission: the public output is fallback-only, not a valid signal. |
| `jguevarag/05-kaggle-inference-submission` | yes | no | COMPLETE | `submission.csv` is the same `(3,235)` all-zero file as 08, SHA prefix `b61f628d452fb004`. Log says no test files and dummy submission. | Reject for submission; keep as source-only reference. |
| `jguevarag/07-optimal-sed-training` | yes | no | RUNNING | Training notebook, no submission output available in this audit. No OOF artifacts observed in pulled source. | Hold as training-source only; do not spend a slot. |
| `jguevarag/06-master-optimal-sed-training` | yes | no in current status check | COMPLETE after refresh | Training notebook source only. Earlier metadata pull reported internet enabled; no direct submission path. | Hold as training-source only; not a final inference candidate. |
| `yuki16/bird-clef2026-perch-prot-vectormlp-fattail-sed-v3` | yes | no | COMPLETE | Final `submission.csv` is `(240,235)` train-dry-run; byte-identical to Beicicc Kosuke ConvNeXt output. Proxy macro for final blend `0.98796316`; SED side output `0.99206224`. | Source/reference only: near-neighbor public Perch/SED family already covered; no new slot-worthy signal. |
| `beicicc/birdclef2026-kosuke-convnext-may12` | yes | no | COMPLETE | Same final output as Yuki v3; same proxy metrics. Uses Perch/ONNX/SED dependency family. | Source/reference only; duplicate of Yuki v3 output. |
| `ulyanovantonamaranta/birdclef-2026-gate-f008-mirrorrare-rt010` | yes | no | COMPLETE | Final `submission.csv` is sample-shaped `(3,235)` and very close to v87 on sample rows (`corr=0.988291`, `MAD=0.000790`). Its 240-row `submission_sed.csv` equals the Yuki/Beicicc SED side output. | Hold/reject as near-neighbor; no distinct evidence for a real submission slot. |

## Proxy Check

Ran `birdclef-2026/scripts/evaluate_dryrun_proxy.py` on the 240-row dry-run outputs from Yuki v3, Beicicc Kosuke ConvNeXt, and Ulyanov MirrorRare. Results were written to `experiments/v98_jguevarag_proxy_scores.csv`.

Key points:

- `yuki16/...v3` and `beicicc/...kosuke-convnext-may12` final outputs are identical (`corr=1.0`, `MAD=0.0`).
- Their `submission_sed.csv` proxy is strong on the local 240-row dry-run set (`macro_auc=0.99206224`, `micro_auc=0.99865115`), but this is the same public SED sidecar pattern already seen in prior routes.
- `jguevarag/08` and `jguevarag/05` do not produce scoreable 240-row outputs and should not be materialized.

## Decision

Do not use the 2026-05-19 UTC second real-submission slot on this scan.

Rationale:

- The fresh `jguevarag/08` title is misleading for our gate: its public output is all-zero fallback after a state-dict mismatch.
- The Yuki/Beicicc/Ulyanov outputs are not a new high-diversity route; they collapse to already-known Perch/SED behavior or sample-shaped near-neighbors.
- No candidate here clears the dedicated-skill promotion rules: no new OOF/stability evidence, no material diversity over the current v87/v91 route, and no CPU dry-run evidence that justifies a prize-route submission.

