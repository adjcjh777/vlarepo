# v115-v117 Tsubasa SED Summary

Updated: 2026-05-19 06:51 UTC

## Source

- `tsubasatech/birdclef-2026-snowflake-sed`
- Kaggle metadata license: `CC0-1.0`
- Files audited:
  - `sed_convnext-tiny_fold0.onnx`: `audio ['B',160000] -> logits ['B',234]`
  - `sed_tf-efficientnetv2-m_fold0.onnx`: `audio ['B',160000] -> logits ['B',234]`

## v115

- Design: two-model Snowflake SED ensemble plus v112-style train-window remap.
- Status: `ERROR`
- Failure: Kaggle memory exceeded after Perch train feature rebuild and before
  completing Snowflake SED train rebuild.
- Decision: `REJECT - runtime memory`

## v116

- Design: single `sed_convnext-tiny_fold0.onnx` plus train-window remap.
- Status: `COMPLETE`
- Runtime before save: about `489.9s`
- Proxy: `macro=0.85930903`, `micro=0.83251880`, `top5=0.39726027`
- Remap diagnostics: `44/234` classes remapped, max strength `0.88`.
- Correlation vs v110: `0.764711`
- Decision: `REJECT - quality collapse`

## v117

- Design: single `sed_convnext-tiny_fold0.onnx`, remap disabled.
- Status: `COMPLETE`
- Runtime before save: about `435.3s`
- Proxy: `macro=0.71214482`, `micro=0.72131755`, `top5=0.32876712`
- Remap diagnostics: `0/234` classes remapped.
- Correlation vs v110: `0.772860`
- Decision: `REJECT - quality collapse`

## Conclusion

The Tsubasa Snowflake/ConvNeXt SED source is compliance-clean and
low-correlation, but it does not transfer into the current clean EcoProto final
layer. It should not be submitted and should not be tuned further in this lane
without a new, stronger OOF-style rationale.
