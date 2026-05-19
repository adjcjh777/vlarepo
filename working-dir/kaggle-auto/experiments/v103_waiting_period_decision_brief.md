# v103 Waiting-Period Blend Decision Brief

Updated: 2026-05-19 03:28 UTC

## Context

v101 real submission ref `52795021` is still `PENDING`, so no further real submission should be made. During the waiting period, I tested whether v103 should be blended with aligned 120-row dry-run side outputs from v87/v91/v94.

## Evidence

Only predictions sharing the same 120 train-like dry-run row IDs are proxy-scoreable. v101 and several final `submission.csv` files use the 3-row sample-prior/test-like dry-run schema, so they were excluded from this local proxy comparison.

Aligned side outputs and correlation versus v103:

- v102: corr `0.999919`, MAD `0.000594`
- v87/v94 ProtoSSM: corr about `0.366..0.368`, MAD about `0.395..0.399`
- v91 ProtoSSM: corr `0.388235`, MAD `0.361932`
- SED side outputs: corr `0.220375`, MAD `0.493566`
- v94 subm2: corr `0.324427`, MAD `0.308259`

Best macro proxy remains standalone v103:

- v103: macro `0.98906455`, micro `0.92885549`, top5 `0.71232877`
- best tested side blend by macro, v103+v94_subm2_w35: macro `0.98518780`, micro `0.90757900`, top5 `0.54794521`
- SED-heavy blends improve top-hit/top5 but lose too much macro; e.g. v103+v87_sed_w35 reaches top5 `0.89041096` but macro drops to `0.98004596`

## Decision

`DO NOT CREATE v104 BLEND SUBMISSION FROM THESE SIDECARS`

Reason: current dry-run evidence says sidecar blends are not macro-safe. The competition metric is macro ROC-AUC, so sacrificing nearly `0.009` macro for top-hit proxy is not justified without stronger OOF evidence.

## Next Automatic Action

Keep v103 as the current best original Run-mode candidate. Continue waiting for v101 to resolve; if v101 underperforms, v103 is the next original candidate to consider after quota and compliance checks.
