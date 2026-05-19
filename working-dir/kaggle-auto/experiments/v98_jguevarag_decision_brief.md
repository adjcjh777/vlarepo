# v98 JGuevara TTA / Public Perch-SED Refresh Decision Brief

Candidate family: `jguevarag/08-winning-tta-submission-pipeline`, with adjacent checks on `jguevarag/05`, `jguevarag/06`, `jguevarag/07`, `yuki16/...v3`, `beicicc/...kosuke-convnext-may12`, and `ulyanovantonamaranta/...mirrorrare-rt010`.

Decision: `REJECT - do not materialize or submit v98 now`

## Evidence

Positive signals:

- `jguevarag/08-winning-tta-submission-pipeline` is CPU-only and internet-off.
- The notebook includes a TTA-style SED inference path and public run status is COMPLETE.
- Yuki v3 / Beicicc / Ulyanov include accessible CPU/no-internet Perch/SED side outputs with 240-row dry-run files.

Negative signals:

- `jguevarag/08` creates `submission.csv` from `sample_submission.csv` before running inference.
- Its log shows a state-dict mismatch when loading `/kaggle/input/notebooks/jguevarag/04-cnn-efficientnet-training/tf_efficientnet_b0_ns_best.pth`.
- The same log reports only one dummy segment and then rewrites the final file after sample reindexing.
- The downloaded final `submission.csv` from both `jguevarag/08` and `jguevarag/05` is `(3,235)`, all zeros, SHA prefix `b61f628d452fb004`.
- `jguevarag/07` was still RUNNING during the final status check and is a training notebook, not a final inference candidate.
- `jguevarag/06` is training-source only and had inconsistent metadata during this audit; it is not a direct final notebook.
- Yuki v3 and Beicicc Kosuke ConvNeXt final outputs are byte-identical and are already in the known Perch/SED public family.
- Ulyanov MirrorRare final sample output is close to v87 (`corr=0.988291`, `MAD=0.000790`) and its SED side output matches the same public SED sidecar.

## Proxy Check

Wrote `experiments/v98_jguevarag_proxy_scores.csv` from the scoreable 240-row dry-run outputs.

Key result:

- Yuki/Beicicc final blend: `macro_auc=0.98796316`, `micro_auc=0.96102445`, `top5_hit=0.75862069`.
- Yuki/Beicicc/Ulyanov SED side output: `macro_auc=0.99206224`, `micro_auc=0.99865115`, `top5_hit=0.99425287`.
- Ulyanov ProtoSSM side output: `macro_auc=0.97473394`, weaker than the Yuki/Beicicc ProtoSSM side output.

Interpretation: the only strong proxy result is the familiar public SED sidecar; it is not enough to justify another real submission without new OOF/stability evidence or a materially different final blend.

## Decision

Do not create a local v98 notebook and do not spend a real Kaggle submission slot on this family.

Reopen conditions:

- `jguevarag/08` must load a compatible checkpoint and produce non-fallback predictions.
- A candidate must emit a 240-row dry-run output and pass schema/distribution checks without sample or dummy fallback.
- Promotion must include OOF/stability evidence or a clear diversity argument over v87/v91, not only a public notebook title or side-output proxy.

