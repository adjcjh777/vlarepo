# v110-v113 Clean Branch Follow-Up Summary

Updated: 2026-05-19 05:52 UTC

## v110

v110 materialized the local `0.4*v107 + 0.6*v109` clean-branch probe as a self-contained notebook.

- Status: `COMPLETE`
- Runtime: about `287.8s` before save
- Proxy: `macro=0.97911204`, `micro=0.91481637`, `top1=0.21917808`, `top5=0.52054795`
- Decision: `HOLD`, best clean top-k fallback, but not strong enough to spend a real submission slot.

## v111

v111 tested a newly audited CC0 clean SED source:

- Source: `backtracking/birdclef2026-clean-sed-b0`
- License: `CC0-1.0`
- ONNX input/output: raw `audio [batch,160000]` to `clip_logits [batch,234]`
- Status: `COMPLETE`
- Runtime: about `337.4s` before save
- Proxy: `macro=0.75704093`, `micro=0.77120047`, `top1=0.12328767`, `top5=0.27397260`
- Decision: `REJECT`, clean but quality-breaking.

## v112

v112 tested an original train-window class-output remap for the same CC0 clean SED source:

- Source: `backtracking/birdclef2026-clean-sed-b0`
- Mechanism: 234-by-234 train-window output-to-target remap with per-class trust strength
- Status: `COMPLETE`
- Runtime: about `363.2s` before save
- Remap diagnostics: `46/234` classes remapped; clean SED train-window AUC mean `0.9283`
- Proxy: `macro=0.87568304`, `micro=0.83667571`, `top1=0.23287671`, `top5=0.53424658`
- Decision: `REJECT`, diagnostic value only; train-window alignment did not transfer enough.

## v113

v113 tested a second CC0 SED source with an original MelNormProbe:

- Source: `lantingguo/birdclef2026-own-sed-b0-v5-onnx`
- License: `CC0-1.0`
- ONNX input/output: `mel [batch,1,128,time]` to `logits [batch,234]`
- Mechanism: zscore/minmax 128-mel views with per-class train-window trust shrinkage
- Status: `COMPLETE`
- Runtime: about `466.6s` before save
- Proxy: `macro=0.97755927`, `micro=0.91558215`, `top1=0.17808219`, `top5=0.53424658`
- Correlation vs v110: `0.981988`
- Decision: `HOLD`, clean diagnostic only; direct macro below v110.
- Blend probe: `0.85*v110 + 0.15*v113` reaches `macro=0.979201`, a tiny local improvement worth a self-contained v114 check but not a real submission by itself.

## Current Best Clean Fallback

`v110-ecoproto-clean-blend` remains the best standalone license-clean fallback among v104-v113.

## Current Goal Gate

`birdclef_goal_check.py` at `2026-05-19 05:11 UTC` still reports:

- best visible score: `0.949`
- top20 cutoff: `0.953`
- top5 cutoff: `0.958`
- gate: `NOT_REACHED`

## Next Direction

Stop direct or remapped strong use of the backtracking clean SED B0 model. Continue with:

- self-contained v114 clean blend (`0.85*v110 + 0.15*v113`) if the next run should exploit the small local blend gain;
- or audit `tsubasatech` if a lower-correlation CC0 SED source is still needed.
