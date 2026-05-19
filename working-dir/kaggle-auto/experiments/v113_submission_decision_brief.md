# v113 Submission Decision Brief

Updated: 2026-05-19 05:52 UTC

## Candidate

- `v113-lantingguo-melnorm-ecoproto`
- Local path: `birdclef-2026/notebooks/v113-lantingguo-melnorm-ecoproto`
- Kaggle kernel: `junhaochengadjcjh7u7/bc26-v113-lanting-melnorm`
- Run-mode output: `birdclef-2026/outputs/v113-lantingguo-melnorm-ecoproto-v1`

## Evidence

- Kaggle Run-mode status: `COMPLETE`.
- Runtime: about `466.6s` before save and about `480.5s` through nbconvert.
- Metadata: private, CPU-only, internet disabled.
- Unknown-license runtime dependencies: none.
- New clean SED source: `lantingguo/birdclef2026-own-sed-b0-v5-onnx`, Kaggle metadata license `CC0-1.0`.
- LantingGuo ONNX I/O: input `mel ['batch', 1, 128, 'time']`, output `logits ['batch', 234]`.
- Output artifacts:
  - `submission.csv`
  - `v113_lantingguo_melnorm_diagnostics.csv`
  - `bc26-v113-lanting-melnorm.log`
- Output schema: `(120,235)`, finite, no duplicate row IDs, score range `[0.01114442, 0.99950665]`.
- MelNorm diagnostics: trusted classes `23/234`, trust mean/max `0.0528/0.8200`.
- LantingGuo train-window AUC reference after view selection: mean `0.4956`, active `234`.
- Proxy: `macro_auc=0.97755927`, `micro_auc=0.91558215`, `top1_hit=0.17808219`, `top5_hit=0.53424658`.
- Correlation: vs v110 `0.981988`, vs v112 `0.770740`, vs v111 `0.757553`, vs v103 `0.777067`.
- Local blend probe: `0.85*v110 + 0.15*v113` gives `macro_auc=0.979201`, `micro_auc=0.915724`, `top1_hit=0.232877`, `top5_hit=0.520548`.

## Interpretation

v113 is a useful clean diagnostic but not a direct submission candidate. It does not beat v110 on macro proxy, although it improves top5 proxy. The high correlation with v110 means it is mostly a small perturbation of the current best clean fallback, not a new independent high-value branch.

The blend probe is mildly positive and can seed a v114 self-contained clean blend, but the gain is too small to spend a real daily submission slot without a notebook that reproduces the blend inside Kaggle and passes the same audit.

## Decision

`HOLD - do not submit`

Reason: v113 has clean provenance and valid runtime, but direct proxy is below v110. Use it only as a source for a possible self-contained v114 blend, not as a real submission.

## Next Action

If continuing the clean branch, implement a self-contained `v114` that replays the v110 clean fallback and the v113 LantingGuo MelNorm sidecar inside one notebook, then blends at `0.85/0.15`. Do not attach local output CSVs as Kaggle inputs.
