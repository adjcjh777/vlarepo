# Watchlist Metadata: 2026-05-19 Turn 12

Updated: 2026-05-19 07:04 UTC

## Goal State

- Best visible team score remains `0.949`.
- Top-20 cutoff remains `0.953`; Top-5 cutoff remains `0.958`.
- UTC-day real submissions visible before this scan: `2/5`.
- No new real submission was made during this scan.

## Public Scan Boundary

Public kernels are idea references only. Do not fork, copy code, or represent
public work as original. Any candidate promoted from a public scan must have:

- CPU-only/no-internet metadata for final inference;
- complete source and reproducible dependencies;
- attribution and license/provenance evidence;
- local proxy/runtime/schema evidence;
- a non-trivial original mechanism beyond direct public replication.

## Inspected Candidates

### `aiaiaiooo/birdclef2026`

- Title: `BirdCLEF2026_端到端训练推理_本地版`
- Kaggle status: `ERROR`
- Metadata: public notebook, GPU enabled, internet disabled, competition source
  only, no dataset/model sources declared.
- Output fetched: five `tf_efficientnetv2_b0` checkpoints plus one history CSV.
- Evidence:
  - training log reports `AUC: nan`;
  - inference fails at `best_model.pth` not found;
  - model history shows five short epochs and no usable validation AUC;
  - no valid `submission.csv` output.
- Decision: `REJECT-as-candidate`, keep only as a failed lightweight Mel-CNN
  source audit.

### `ommodi07/birdclef2026`

- Title: `birdclef2026`
- Claimed concept: `HC-TransBird` / habitat-context transformer.
- Kaggle status: `COMPLETE`
- Metadata: public notebook, GPU enabled, internet enabled, no declared
  datasets/models beyond the competition.
- Output fetched: `best_model_full.pth` and `submission.csv`.
- Evidence:
  - notebook trains on dummy random tensors, not BirdCLEF training audio;
  - checkpoint AUC is a dummy validation score around `0.5124`;
  - hidden Run-mode finds no `.ogg` files and emits a zero-probability fallback;
  - fetched `submission.csv` is `3 x 235`, all-zero predictions.
- Decision: `REJECT-as-candidate`; do not submit, fork, or use its checkpoint.

## Originality Response

The inspected public work did not produce a compliant candidate. The useful
idea-level signal is not the code, but the general notion of acoustic context
or habitat context. To avoid copying, I converted that into a workspace-original
local probe:

- use existing clean `v110` and `v113` internal branches;
- gate the sidecar by internal per-class AUC deltas and support;
- add row-level prediction-geometry gates as an acoustic-context proxy;
- score formulas locally before materializing any notebook.

The resulting v118 probe is recorded in:

- `birdclef-2026/scripts/birdclef_probe_v118_ecohabitat_rescue.py`
- `experiments/v118_ecohabitat_selective_probe.csv`
- `experiments/v118_ecohabitat_selective_probe.md`

