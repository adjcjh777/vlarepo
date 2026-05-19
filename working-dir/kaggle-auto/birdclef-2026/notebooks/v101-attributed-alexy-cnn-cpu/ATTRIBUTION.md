# Attribution

This candidate is an attributed public-reference derivative of
`alexycactus/birdclef-2026-cnn-infer-dataset`.

Local changes:
- force CPU-only execution even if CUDA is present;
- keep internet disabled and use only the public Alexy CNN checkpoint dataset;
- remove the train_soundscapes staging fallback;
- emit a sample-shaped prior only when Kaggle Run mode has no hidden test;
- add final row-order, duplicate-row, finite, and range assertions.

This is not original work. Do not submit without a candidate-specific
rules compliance pass and a fresh decision brief.
