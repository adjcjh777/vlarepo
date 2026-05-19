# BirdCLEF 2026 Watchlist Metadata Scan - 2026-05-19 Turn 5

Checked at: 2026-05-19 UTC

Scope: latest public kernels after v91 scored 0.948, plus candidate dependencies that could plausibly differ from the v87 0.949 anchor.

## Dataset Access Checks

| Ref | Status | Decision |
| --- | --- | --- |
| `itshyao/birdclef2026-g116-hgnet-b1-rawpseudo-assets` | Kaggle API `403 Forbidden`; dataset search returned 0 hits | Reject for now: required HGNet rawpseudo assets are not accessible in the current account/session. |
| `jacqueszhelinzhang/birdclef26-perch-model` | Kaggle API `403 Forbidden`; dataset search returned 0 hits | Reject for now: required Perch model assets are not accessible in the current account/session. |

## Pulled For Static Audit

Pulled to `/tmp/bc26_scan_may19_turn5` with Kaggle Python API metadata:

| Kernel | CPU | Internet | Static Decision |
| --- | --- | --- | --- |
| `mtoshidesu/testbirdclef-2026-v6` | yes | no | Same Model_7 single-branch family; lower priority after v91/v92. |
| `huydo170302/dsai1-internship-birdclef-2026` | yes | no | Training/EDA-style notebook, no attached model assets; not a near-term submission candidate. |
| `cocoaai/bc26-apachikoff-v6` | yes | no | Apachikoff/Model_7 family with BirdNET fallback text; lower priority after license-compatible E1/visual evidence. |
| `cocoaai/bc26-karnak-advance-ensemble-patched` | yes | no | Same dependency family as Karnak advance, with BirdNET model source in metadata; not preferred. |
| `jguevarag/05-kaggle-inference-submission` | yes | no | Depends on kernel sources and model source placeholders; not mature enough for slot use. |
| `evgendvorkin/birdclef-baseline` | yes | no | Baseline-level assets; not a score-push candidate. |
| `karnakbaevarthur/birdclef-advance-ensemble` | yes | no | Best candidate from this scan for Run-mode evidence; materialized as v94. |
| `damianleandrotamburi/20260329-birdclef` | yes | no | Perch starter-like baseline; not a score-push candidate. |
| `apachikoff/birdclef-2026-v6` | yes | no | Model_7 single-branch family; defer unless leaderboard evidence changes. |
| `rauffauzanrambe/birdclef-26-real-load-adapter-reasoning` | no | yes | Reject: metadata requires GPU and internet. |

## Net Decision

The only candidate worth Run-mode evidence in this scan was `karnakbaevarthur/birdclef-advance-ensemble`, because it is CPU/no-internet and uses public dependencies. It was materialized as v94 with BirdNET disabled and strict final checks.
