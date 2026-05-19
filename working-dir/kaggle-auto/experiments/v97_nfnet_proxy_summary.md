# v97 NFNet Train-Dry-Run Proxy Summary

Updated: 2026-05-19 02:12 UTC

## Scope

Evaluated original-output train dry-run files from `lucataco/bc26-claude-a2prime-nfnet-fix` using:

```bash
python3 birdclef-2026/scripts/evaluate_dryrun_proxy.py \
  --pred-dir /tmp/bc26_outputs_turn8/lucataco_bc26_claude_a2prime_nfnet_fix \
  --output-csv experiments/v97_nfnet_proxy_scores.csv
```

The proxy aligns `row_id` values with `birdclef-2026/data/train_soundscapes_labels.csv`. This is a sanity proxy, not public or private leaderboard proof.

## Key Results

| Candidate | Macro AUC | Micro AUC | Top-5 Hit | Notes |
| --- | ---: | ---: | ---: | --- |
| `submission_sed` | `0.99206224` | `0.99865115` | `0.99425287` | Best proxy branch; familiar SED behavior. |
| `submission_base_3way` | `0.98214004` | `0.93134066` | `0.49425287` | Public notebook's default final family. |
| `submission_a2_nfnet_w03` | `0.98073675` | `0.93232850` | `0.51149425` | NFNet weight lowers macro vs base. |
| `submission_a2_nfnet_w05` | `0.97972491` | `0.93286546` | `0.51149425` | NFNet weight lowers macro further. |
| `submission_a2_nfnet_w08` | `0.97719511` | `0.93311099` | `0.54022989` | More NFNet improves top-5 slightly but hurts macro. |
| `submission_nfnet` | `0.73311292` | `0.66131207` | `0.27586207` | Standalone NFNet branch is weak on this proxy. |
| `submission_birdnet` | `0.58170497` | `0.26647060` | `0.21839080` | Confirms BirdNET branch is not useful here and remains license-blocked. |

Synthetic rank blends adding NFNet to Proto/SED also failed to improve macro:

- `w=0.01`: macro `0.97845930`, micro `0.95900402`, top-5 `0.79885057`.
- `w=0.03`: macro `0.97787930`, micro `0.95730517`, top-5 `0.79310345`.
- `w=0.10`: macro `0.97296327`, micro `0.94952102`, top-5 `0.67241379`.

## Decision

Keep `v97` blocked.

The NFNet branch is diverse, but this proxy says the diversity is more likely noise than useful macro-AUC signal. It does not satisfy the reopen condition in `v97_a2nfnet_decision_brief.md` requiring stronger OOF/proxy evidence.

No local v97 notebook was materialized and no real Kaggle submission was made.
