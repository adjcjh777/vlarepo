# v108 Original EcoProto Plan

Updated: 2026-05-19 04:37 UTC

## Motivation

The v104-v107 license-clean Perch-only branch proved that removing unknown-license SED/cache assets is feasible, but it loses much of the row-level ranking signal seen in v103. The next candidate must add our own signal instead of only reshaping public notebook behavior.

## Original Mechanism

`v108-ecoproto-perch-guarded` adds an original EcoProto rescue layer:

- rebuild train Perch embeddings inside the Kaggle notebook from competition train soundscapes;
- build one normalized embedding prototype per class from positive train windows;
- score each test row by cosine similarity to these class prototypes;
- combine prototype rank with site/hour priors, Perch rank, and the existing probe consensus;
- apply rescue only for mid-support, non-protected, non-rare classes where Perch OOF quality suggests room for improvement;
- require temporal neighborhood agreement before making extra boosts.

## Compliance

- CPU-only metadata.
- Internet disabled.
- No unknown-license runtime dependency.
- Runtime inputs limited to the competition data, `rishikeshjani/perch-onnx-for-birdclef-2026` (`CC0-1.0`), and Google Perch model (`Apache 2.0`).
- Kaggle Run-mode only until schema, runtime, proxy, and compliance checks pass.

## Decision Rule

Do not real-submit v108 unless it materially improves the clean-branch proxy over v107 and shows a plausible path to beat the current `0.949` anchor.

