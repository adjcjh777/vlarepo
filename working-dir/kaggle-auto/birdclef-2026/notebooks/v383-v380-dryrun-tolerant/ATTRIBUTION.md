# v383 v380 Dry-run-tolerant Static Distillation Attribution

This candidate fixes the v380 Run-mode dry-run failure. The v380
static distillation layer is preserved, but when the v107 base
notebook falls back to train-soundscape dry-run rows that do not
match sample_submission.csv, the patch no longer crashes. It
applies the same fixed-coefficient transformation to those fallback
rows and marks the diagnostic as dry-run row mismatch.

In real test/sample-aligned execution, the same row-order guard is
still enforced against sample_submission.csv. The notebook remains
CPU-only, no-internet, and uses only the clean v107 sources plus
competition labels and embedded coefficients.
