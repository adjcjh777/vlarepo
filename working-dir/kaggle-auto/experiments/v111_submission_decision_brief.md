# v111 Submission Decision Brief

Updated: 2026-05-19 05:12 UTC

## Candidate

- `v111-clean-sed-ecoproto-blend`
- Local path: `birdclef-2026/notebooks/v111-clean-sed-ecoproto-blend`
- Kaggle kernel: `junhaochengadjcjh7u7/bc26-v111-clean-sed-ecoproto`
- Run-mode output: `birdclef-2026/outputs/v111-clean-sed-ecoproto-blend-v1`

## Evidence

- Kaggle Run-mode status: `COMPLETE`.
- Runtime: about `337.4s` before save and about `342.6s` through nbconvert.
- Metadata: private, CPU-only, internet disabled.
- Unknown-license runtime dependencies: none.
- New clean SED source: `backtracking/birdclef2026-clean-sed-b0`, Kaggle metadata license `CC0-1.0`.
- Clean SED ONNX I/O in Kaggle: input `audio ['batch', 160000]`, output `clip_logits ['batch', 234]` and `frame_logits ['batch', 234, 10]`.
- Output: `submission.csv` shape `(120,235)`, finite, no duplicate row IDs, range `[0.012436418, 0.999418900]`.
- Proxy: `macro_auc=0.75704093`, `micro_auc=0.77120047`, `top1_hit=0.12328767`, `top5_hit=0.27397260`.
- Correlation: vs v110 `0.76312781`, vs v103 `0.63270335`.

## Decision

`REJECT - do not submit`

Reason: v111 proves that the CC0 clean SED asset can run in the final CPU/no-internet Kaggle path, but its signal is not aligned with the local proxy task. It sharply degrades macro and top-k quality relative to v110 and v103.

## Next Action

Do not use `backtracking/birdclef2026-clean-sed-b0` as a direct SED branch. If continuing the license-clean SED direction, audit the backup CC0 sources (`lantingguo` ONNX, `tsubasatech` ONNX) or use clean SED only as a heavily gated diagnostic sidecar after proving class/order alignment.

