# v109 Original EcoProto Rank-Launch Plan

Updated: 2026-05-19 04:33 UTC

## Motivation

v108 introduced a genuine original EcoProto signal and improved clean-branch macro proxy, but it failed row-level top-k ranking. v109 keeps the original signal and uses it inside a rank-launch view so the clean branch can recover top-k behavior without reintroducing unknown-license SED/cache assets.

## Mechanism

- Rebuild train Perch embeddings inside Kaggle from competition soundscapes.
- Build class prototypes from positive train windows.
- Compute EcoProto rank from prototype similarity plus site/hour prior and probe consensus.
- Blend EcoProto into a guarded rank-launch view with Perch/probe/adaptive ranks.
- Exclude rare and protected classes from broad rank launch.
- Preserve confident row winners with a local top guard.

## Compliance

- CPU-only.
- Internet disabled.
- No unknown-license runtime dependency.
- Runtime metadata only uses competition data, `rishikeshjani/perch-onnx-for-birdclef-2026` (`CC0-1.0`), and Google Perch (`Apache 2.0`).

## Submission Rule

Do not submit unless v109 materially exceeds v107 clean-branch top-k behavior and has a plausible path to improve the current `0.949` anchor.

