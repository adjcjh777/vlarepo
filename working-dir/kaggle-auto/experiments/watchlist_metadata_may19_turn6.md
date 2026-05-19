# BirdCLEF 2026 Watchlist Metadata Scan - 2026-05-19 Turn 6

Checked at: 2026-05-19 01:47 UTC.

Current live gate:

- Best visible score: `0.949` from v87.
- Top-20 cutoff: `0.953`.
- Top-5 cutoff: `0.958`.
- UTC-day submissions used: `1/5`.
- Goal gate: `NOT_REACHED`.

## Pulled Candidates

Pulled into `/tmp/bc26_scan_may19_turn6` for static inspection only:

| Kernel | CPU | Internet | Static Result |
| --- | --- | --- | --- |
| `itshyao/birdclef-2026-s117-s114-g116-delta-launcher` | yes | no | Launcher only. It looks for `s117_source.ipynb` under `/kaggle/input`, but metadata only contains empty dataset-source entries plus public dependency families. Not reproducible from pulled source. |
| `raunakdey07/birdclef-2026-v6` | yes | no | Same single `Model_7` V6 family as Yaroslav/Apachikoff/Mtoshi; not a materially new route beyond current v87/v91 evidence. |
| `yaroslavkholmirzayev/v6-0949-replay` | yes | no | Same single `Model_7` V6 family; not a new candidate. |
| `samejimatink0/birdclef-2026-visual-cpu-inference` | yes | no | Same visual/Proto-SED direction already tested by v92; lower priority after v92 near-duplicate evidence. |
| `tanishq51/birdclef-0-947` | yes | yes | Reject for this goal because internet is enabled in metadata and the score claim is below current 0.949 anchor. |

## S117 Original Output Audit

Downloaded original public-kernel output into `/tmp/bc26_original_s117_output` for audit only. The public kernel status was `COMPLETE`.

Key log observations:

- The launcher executed a hidden input source notebook: `s117_source.ipynb`.
- It reported G116 assets at `/kaggle/input/datasets/itshyao/birdclef2026-g116-hgnet-b1-rawpseudo-assets`.
- The current account cannot list or search that dataset via Kaggle API; previous access checks returned 403/no hits.
- The final dry-run message was `S117 dry-run/mismatch: keeping anchor submission.csv`.
- The downloaded `submission.csv` is exactly identical to local v87 dry-run output on the 3 sample rows.
- The downloaded `submission_g116_hgnet_b1_all5.csv` has 12 train dry-run rows, not a sample-aligned final submission.

## Decision

Do not submit S117 directly and do not burn a quota slot on a blind fork. The candidate is interesting as an idea signal, but it is not currently controllable or reproducible in this workspace:

- required source notebook is not included in the pulled kernel;
- required Itshyao G116 assets are not accessible/listable to the current account;
- original public dry-run output does not prove hidden-test improvement beyond v87;
- submitting someone else's public kernel directly would not satisfy the local provenance/control standard for a prize-route candidate.

Next action remains: look for an accessible CPU/no-internet candidate with complete Run-mode evidence and material difference from v87, or design a local original/attributed blend only if it has a credible top-20-oriented rationale.
