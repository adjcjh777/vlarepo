# v93 Watchlist Scan

Updated: 2026-05-19 01:09 UTC

## Context
- Active real submission: v91, Kaggle ref `52791730`, still `PENDING`.
- UTC `2026-05-19` real submissions used: `1/5`.
- Guard: do not submit another candidate while v91 is pending.
- Goal gate at latest check: `GOAL_GATE=NOT_REACHED`; visible best remains v87 `0.949`.

## Scan Command
`python3 birdclef-2026/scripts/birdclef_public_scan.py --page-size 50`

## Pulled For Metadata Inspection
- `mtoshidesu/testbirdclef-2026-v6`
- `cocoaai/bc26-karnak-advance-ensemble-patched`
- `apachikoff/birdclef-2026-v6`
- `adkasd/birdclef-2026-sub-v4-5-strong`

## Decisions
- `mtoshidesu/testbirdclef-2026-v6`: reject as immediate Run-mode candidate; same V6 family as `apachikoff/birdclef-2026-v6`, public-source derivative, not materially fresh enough by itself.
- `apachikoff/birdclef-2026-v6`: reject as immediate Run-mode candidate; same single `Model_7` V6 family and source notebook history as `mtoshidesu/testbirdclef-2026-v6`.
- `cocoaai/bc26-karnak-advance-ensemble-patched`: reject for prize-route submit; metadata includes `shadiakiki1/birdnet-analyzer/TfLite/birdnet_global_6k_v2.4_model_fp32-1/3`, the same BirdNET CC BY-NC risk that blocked v90.
- `adkasd/birdclef-2026-sub-v4-5-strong`: selected for v93 Run-mode-only evidence; CPU/no-internet, no BirdNET model source, source run duration about `753s`, and uses the higher-effort V6/exp019-style strong branch.

## v93 Preparation
- Local candidate: `birdclef-2026/notebooks/v93-attributed-adkasd-strong-nobirdnet`
- Local changes:
  - clear executed notebook outputs before push;
  - remove empty dataset source entry;
  - explicitly disable BirdNET lookup path;
  - keep CPU-only/no-internet metadata.

## Submission Policy
v93 is not a real submission while v91 is pending. It can only become a slot-two candidate after v91 resolves and after a candidate-specific rules compliance report plus output-diversity audit.

