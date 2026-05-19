# v99 V6 / Itshyao S118-S120 Decision Brief

Candidate family: public V6 / 0949 replay plus Itshyao S118/S120 launcher refresh.

Decision: `REJECT - do not materialize or submit v99 now`

## Evidence

Positive signals:

- All five inspected kernels are CPU-only and internet-off.
- Public runs are COMPLETE.
- Itshyao S118/S120 runs completed in about 11 minutes and produced OOF/cache side artifacts in their public output.
- S118 attempted a G116 HGNet sidecar, which is structurally interesting in principle.

Negative signals:

- `mtoshidesu/testbirdclef-2026-v6` and `raunakdey07/birdclef-2026-v6` produce final `submission.csv` files byte-identical to local v87/v93.
- `yaroslavkholmirzayev/v6-0949-replay` is still a v87 near-neighbor on sample rows: `corr=0.996729`, `MAD=0.000242`.
- Itshyao S118/S120 source code is not reproducible from the pulled notebook: the visible notebook only executes hidden input notebooks, `s118_source.ipynb` or `s120_source.ipynb`.
- Current account receives `403 Forbidden` for:
  - `itshyao/birdclef-2026-s118-gated-g116-source`
  - `itshyao/birdclef-2026-s120-gated-birdnet-safe-source`
  - `itshyao/birdclef2026-g116-hgnet-b1-rawpseudo-assets`
- S118 and S120 metadata include `shadiakiki1/birdnet-analyzer/TfLite/birdnet_global_6k_v2.4_model_fp32-1/3`, a BirdNET source already treated as a prize-route license risk locally.
- S118's G116 side output is only 12 dry-run rows and the log explicitly keeps the anchor submission because of row mismatch.

## Proxy Check

Wrote `experiments/v99_v6_s118_proxy_scores.csv`.

Key result:

- Shared SED side output remains strong on the local 240-row dry-run proxy (`macro_auc=0.99206224`), but this same sidecar has appeared repeatedly and is not a new promotion signal.
- The G116 sidecar evidence is too small and unstable: only 12 rows, `macro_auc=0.33311688`, with no accessible source/assets to reproduce or fix the row mismatch.

## Decision

Do not create a v99 notebook and do not spend a real Kaggle submission slot on this family.

Reopen conditions:

- Itshyao source notebooks and G116 assets become accessible to this account with license/provenance recorded.
- BirdNET source is removed or replaced with a prize-compatible route.
- G116 or other sidecar produces full-row hidden-test-compatible predictions rather than a 12-row dry-run artifact.
- Candidate output is materially different from v87 and supported by OOF/stability evidence.

