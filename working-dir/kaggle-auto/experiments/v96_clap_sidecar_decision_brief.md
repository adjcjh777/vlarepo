# v96 CLAP Sidecar Decision Brief

Candidate family: Henry/Lucataco CLAP INT8 sidecar (`bc2026-raunak0946-clap-v53`, `bc26-henry-clap-v53-fasttop`)

Decision: `HOLD - do not materialize or submit v96`

## Evidence

Accessible extra assets:

- `konbu17/bird26-train-audio-head-v1`
- `habedi/birdclef-2026-clap-int8-bundle`

Public Run-mode evidence:

- Henry v53 completes only through a quick public dry-run guard and emits a uniform sample-shaped CSV.
- Lucataco fasttop completes the heavier staging path in about 8.8 minutes, creates valid intermediate dry-run outputs, and uses the train-audio-head branch.
- Lucataco fasttop explicitly skips CLAP sidecar in dry-run mode because public Run-mode has no test audio.
- Lucataco final sample-shaped output is close to v87 (`corr=0.989536`, `MAD=0.000609`).

Score/risk context:

- Current live anchor is v87 at `0.949`.
- This family is labeled around `0946`, so public evidence is below the anchor.
- The desired gap is not small: current top-20 is `0.953`, top-5 is `0.958`.

## Decision

Do not create a v96 notebook or submit a CLAP sidecar candidate now. The idea is structurally interesting, but current evidence does not justify a real Kaggle slot.

Reopen only if:

- a new sidecar route shows public evidence above the 0.949 anchor or a credible top-20 path;
- CLAP activation can be validated without relying on blind hidden-test behavior;
- BirdNET-linked variants are patched to remove any non-commercial license risk before prize-route consideration.
