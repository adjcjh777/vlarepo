# BirdCLEF 2026 Watchlist Metadata Scan - 2026-05-19 Turn 8

Checked at: 2026-05-19 02:05 UTC.

Current live gate:

- Best visible score: `0.949` from v87.
- Top-20 cutoff: `0.953`.
- Top-5 cutoff: `0.958`.
- UTC-day real submissions used: `1/5`.
- Goal gate: `NOT_REACHED`.

## Candidate Refresh

Pulled latest / score-desc / vote-count public-kernel metadata with the local BirdCLEF scanner and compared candidate refs against the local reports. Already-covered near-neighbor families remain blocked:

- EoS5 / S106 / V6 / Anthony near-neighbor variants are too close to v87 or previous v51-v53/v87/v91 evidence.
- Karnak rank-power and cocoa/adkasd variants mostly reuse the same ProtoSSM + SED + rank-power base.
- BirdNET-linked variants remain blocked for prize-route use unless the CC BY-NC model source is removed.

Pulled into `/tmp/bc26_scan_may19_turn8b` and downloaded original outputs into `/tmp/bc26_outputs_turn8` for audit only.

## Pulled Candidate Audit

| Kernel | CPU | Internet | Original Status | Output Evidence | Decision |
| --- | --- | --- | --- | --- | --- |
| `itshyao/birdclef-2026-s116-g116-hgnet-b1-rawpseudo-all5` | yes | no | COMPLETE | `submission.csv` is `(12,235)` train-dry-run output; required G116 assets are mounted at `/kaggle/input/datasets/itshyao/...` in the public run. | Reject for now: required dataset is still `403 Forbidden` to current account, so the kernel is not reproducible/control-safe. |
| `lucataco/bc26-claude-a2prime-nfnet-fix` | yes | no | COMPLETE | Runtime about `1812s`; NFNet branch active with 5 CPU models; final sample output vs v87 `corr=0.979803`, `MAD=0.001489`. | Hold as source-only: NFNet is structurally diverse, but default final stays near v87 and metadata includes BirdNET CC BY-NC model source. |
| `adkasd/birdclef-2026-sub-v4-2-optimal` | yes | no | COMPLETE | Final sample output vs v87 `corr=0.162290`, but the v4 prior cell requires `adkasd/birdclef-2026-priors-research`. | Reject for direct fork: required priors dataset is unavailable in this account; v93 already failed on the same blocker. |
| `adkasd/birdclef-2026-sub-v4-4-combined` | yes | no | COMPLETE | Final sample output vs v87 `corr=0.113534`, same prior dependency path as v4-2. | Reject for direct fork: inaccessible prior dependency; output diversity cannot be promoted without reproducible inputs. |
| `cocoaai/bc26-karnak-advance-ensemble-patched` | yes | no | COMPLETE | Final sample output vs v87 `corr=0.986623`, `MAD=0.001071`; BirdNET branch active in log. | Reject for prize-route: near-neighbor and still attaches BirdNET model source. |
| `nina2025/birdclef-2026-melspectrogram-wave-songs` | yes | yes | COMPLETE | Training/exploration-style notebook; internet enabled; no attached submission model assets. | Reject as near-term submission candidate. |
| `muhammadsaadalvi/birdclef-2026-wildsound-v8` | no | yes | ERROR | GPU + internet + cross-year training sources. | Reject for final-route constraints. |
| `rauffauzanrambe/birdclef-26-real-load-adapter-reasoning` | no | yes | COMPLETE | GPU + internet + Gemma/model reasoning sources. | Reject for final-route constraints. |

## NFNet Branch Notes

The Lucataco A2Prime/NFNet run is the only genuinely interesting signal in this refresh:

- `brendancarlin/birdclef2026-models` is accessible and metadata reports `CC0-1.0`.
- `nfnet_branch_summary.csv` shows 5 `eca_nfnet_l0` CPU checkpoints, selected `cfg224_tta0`, and `(240,235)` dry-run rows.
- The notebook reports `rank corr(nfnet, proto) = 0.169`, so the branch is diverse.
- Sanity hit-rate on 20 train dry-run files is weak: `6/20 = 0.30` for selected `cfg224_tta0`.
- The source still attaches `shadiakiki1/birdnet-analyzer/.../3`, previously recorded as `CC BY-NC 4.0`.
- The default `submission.csv` remains the base 3-way candidate rather than an NFNet-weighted output.

## Decision

Do not spend the 2026-05-19 UTC second real-submission slot on this scan.

Rationale:

- S116/G116 and adkasd v4 variants require unavailable hidden/private datasets.
- Lucataco NFNet is a useful idea signal, but current evidence does not clear the prize-route gate: BirdNET license risk remains, public score family is around `0946`, selected NFNet sanity is weak, and final dry-run output stays close to v87.
- Cocoa/Karnak-style variants are near-neighbors and/or BirdNET-linked.
- GPU/internet candidates violate the final inference constraints.

Reopen the NFNet route only as a BirdNET-removed local derivative if a stronger OOF/proxy rationale appears; do not submit the public source directly.
