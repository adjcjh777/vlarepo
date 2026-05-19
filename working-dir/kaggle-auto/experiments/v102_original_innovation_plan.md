# v102 Original Innovation Plan

Updated: 2026-05-19 02:50 UTC

## Why This Exists

The user explicitly corrected the strategy: do not only reference public notebooks. v101 was already submitted as a guarded public-reference probe, but the next lane must add a clearly original component from this workspace.

## Original Contribution

v102 will use a workspace-original `macro-risk rescue table`:

- It is derived from local OOF/per-class failure evidence, train soundscape support counts, and taxonomy buckets.
- It assigns each class to a behavior: `protect_anchor`, `cnn_rescue_candidate`, `texture_prior_rescue`, `rare_prior_floor`, `mild_rescue`, `neutral`, or `no_oof_evidence`.
- It proposes class-wise weights for anchor / SED / private probe / CNN sidecar, instead of copying a public notebook's global blend.
- It targets macro-AUC weak spots, especially mid-support sonotypes and frogs where the current OOF base is weak.

Generated artifacts:

- `experiments/v102_original_rescue_table.csv`
- `experiments/v102_original_rescue_summary.csv`
- generator script: `birdclef-2026/scripts/birdclef_build_v102_original_rescue_table.py`

## Current Findings

The first rescue table has 234 class rows:

- `14` classes are `cnn_rescue_candidate` with mean OOF base AUC `0.3774`.
- `40` classes are `protect_anchor` with mean OOF base AUC `0.9530`.
- `12` classes are `rare_prior_floor`.
- `159` classes have no local OOF evidence and should not be aggressively tuned from weak evidence.

Top rescue targets include:

- `22961` Pointedbelly Frog, support `72`, OOF base AUC `0.172750`.
- Multiple insect sonotypes with support `6..46` and OOF base AUC around `0.345..0.432`.
- `25092` Two-colored oval frog, support `48`, OOF base AUC `0.470368`.
- `nacnig1` Nacunda Nighthawk, support `22`, OOF base AUC `0.481519`.

## Implementation Direction

Do not spend another real submission while v101 is pending.

After v101 completes:

1. If v101 is strong or at least diverse, build v102 as a class-wise rescue blend inside a CPU-only notebook: use v87/v86-style anchor for protected classes and the Alexy CNN branch only for `cnn_rescue_candidate` / `mild_rescue` classes.
2. If v101 times out or scores poorly, keep the rescue table but replace the CNN sidecar with a cheaper private probe/SED rescue branch.
3. Add candidate-specific OOF/proxy checks before any submission; do not submit v102 merely because the concept is original.

## Guardrail

This innovation is a meta-layer and decision policy. It must not use hidden test labels, manual listening, private data, or public notebook code beyond permitted model/input dependencies with attribution.
