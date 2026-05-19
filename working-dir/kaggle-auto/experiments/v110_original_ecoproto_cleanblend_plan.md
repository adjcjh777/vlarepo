# v110 Original EcoProto Clean Blend Plan

Updated: 2026-05-19 04:58 UTC

## Motivation

v107 has the best clean-branch top-k proxy, while v109 has the best clean-branch macro proxy and includes the original EcoProto signal. A local probe suggested that a probability blend around `0.4*v107 + 0.6*v109` may improve clean fallback top-k without reintroducing unknown-license SED/cache dependencies.

## Mechanism

`v110-ecoproto-clean-blend` is self-contained:

- rebuild train Perch features in the Kaggle notebook;
- create the same license-clean Perch-only surrogate used by v104-v109;
- replay a v107-like rank-ceiling branch inside the notebook;
- replay a v109-like EcoProto rank-launch branch inside the notebook;
- blend both branches with `v107_like=0.40` and `v109_like=0.60`;
- keep CPU-only/no-internet metadata and do not mount previous output CSVs as dependencies.

## Compliance

- CPU-only.
- Internet disabled.
- No unknown-license runtime dependency.
- Runtime metadata only uses competition data, `rishikeshjani/perch-onnx-for-birdclef-2026` (`CC0-1.0`), and Google Perch (`Apache 2.0`).

## Decision Rule

Do not real-submit unless Run-mode output materially improves clean-branch top-k and has a plausible chance to beat the current `0.949` anchor.

