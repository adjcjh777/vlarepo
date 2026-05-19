# v97 A2Prime NFNet Decision Brief

Candidate family: Lucataco / Claude A2Prime NFNet (`lucataco/bc26-claude-a2prime-nfnet-fix`)

Decision: `HOLD - do not materialize or submit v97 now`

## Evidence

Pulled source and original output for static/output audit only.

Positive signals:

- Metadata is CPU-only and internet-off.
- Public run completed in about `1812s`, within the 90-minute target.
- `brendancarlin/birdclef2026-models` is accessible and reports `CC0-1.0`.
- NFNet branch is active with 5 CPU checkpoints.
- NFNet is diverse relative to ProtoSSM: logged rank correlation `0.168992`.

Negative signals:

- Metadata still attaches `shadiakiki1/birdnet-analyzer/TfLite/birdnet_global_6k_v2.4_model_fp32-1/3`, which is already recorded locally as `CC BY-NC 4.0` and rejected for prize-route use.
- The source family is labeled around `R0946`, below the current v87 visible anchor `0.949`.
- The selected NFNet sanity hit rate is only `6/20 = 0.30` on train dry-run files.
- The notebook's default final `submission.csv` remains `base_3way`; NFNet-weighted files are side outputs, not the selected final candidate.
- Final sample output remains close to v87: `corr=0.979803`, `MAD=0.001489`.

## Added Proxy Check

Ran `birdclef-2026/scripts/evaluate_dryrun_proxy.py` on the original-output train dry-run files and wrote `experiments/v97_nfnet_proxy_scores.csv`.

Key proxy result:

- `submission_sed`: macro `0.99206224`, micro `0.99865115`.
- `submission_base_3way`: macro `0.98214004`, micro `0.93134066`.
- `submission_a2_nfnet_w03`: macro `0.98073675`, micro `0.93232850`.
- `submission_a2_nfnet_w05`: macro `0.97972491`, micro `0.93286546`.
- `submission_a2_nfnet_w08`: macro `0.97719511`, micro `0.93311099`.
- `submission_nfnet`: macro `0.73311292`, micro `0.66131207`.

Interpretation: NFNet diversity does not translate into useful macro-AUC proxy evidence. Increasing NFNet weight slightly improves micro/top-5-style behavior but consistently lowers macro, which is the competition metric direction that matters.

## Decision

Do not create a local v97 notebook and do not spend a real Kaggle submission slot on this family now.

Reopen conditions:

- remove BirdNET lookup/model source entirely;
- make the selected final candidate explicitly use a justified NFNet weight;
- obtain stronger OOF/proxy evidence that the low-correlation branch is helpful rather than noisy;
- keep CPU-only runtime under 90 minutes after patching.

Until those conditions are met, treat A2Prime/NFNet as an idea-level source signal only.
