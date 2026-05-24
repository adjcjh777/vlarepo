# v380 v379 Static Distillation Attribution

This candidate is an original derivative of the local v107
license-clean Perch-only route. It preserves v107's declared
public Perch inputs and appends a fixed-coefficient, CPU-only
post-processing layer learned in the v379 local probe.

The appended layer uses only the v107-generated submission,
competition train soundscape labels, row_id-derived temporal
metadata, and fixed coefficients embedded in the notebook. It
does not read diagnostic teacher outputs at inference time.

This materialization is for static audit only until a separate
Run-mode gate authorizes any Kaggle push. It is not a real
competition submission candidate by itself.
