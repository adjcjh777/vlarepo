# v111 Clean SED Source Audit

Updated: 2026-05-19 05:02 UTC

## Search Result

Kaggle asset search found several candidate SED model datasets with explicit `CC0-1.0` metadata:

| ref | title | license | files | decision |
|---|---|---:|---|---|
| `backtracking/birdclef2026-clean-sed-b0` | Clean SED B0 BirdCLEF 2026 | `CC0-1.0` | `fold0_best_overall.onnx`, `.onnx.data` | use first |
| `lantingguo/birdclef2026-own-sed-b0-v5-onnx` | BirdCLEF2026 own-SED EfficientNet-B0 v5 ONNX | `CC0-1.0` | `sed_b0.onnx` | backup |
| `tsubasatech/birdclef-2026-snowflake-sed` | birdclef-2026-snowflake-sed | `CC0-1.0` | two large ONNX files | backup, heavier |
| `alexycactus/birdclef-2026-cnn-fold-checkpoints` | BirdCLEF 2026 CNN B0 SED 5-fold Checkpoints | `CC0-1.0` | five `.pth` checkpoints | backup, PyTorch route |

## Local I/O Probe

`backtracking/birdclef2026-clean-sed-b0` was downloaded to `/tmp` for metadata and ONNX Runtime shape inspection only.

Observed ONNX Runtime I/O:

- input: `audio ['batch', 160000] tensor(float)`
- output: `clip_logits ['batch', 234] tensor(float)`
- output: `frame_logits ['batch', 234, 10] tensor(float)`

This matches the existing 5-second window pipeline and the BirdCLEF class count, making it the lowest-risk clean SED candidate to test first.

## Compliance

- Kaggle metadata license: `CC0-1.0`.
- No internet required at inference.
- CPU ONNX Runtime path.
- Added as explicit dataset source in v111 metadata.

