# Post-v91 Score Watchlist Scan

Updated: 2026-05-19 01:24 UTC

## Context
- v91 has scored `0.948`, below the v87 anchor `0.949`.
- The BirdNET-disabled E1 route is retired.
- v92 and v93 are rejected as slot-two candidates.
- Goal gate remains `GOAL_GATE=NOT_REACHED`.

## Pulled For Metadata Inspection
- `kijiang/birdclef2026-v337`
- `muhammadsaadalvi/birdclef-2026-wildsound-v8`
- `anthonytherrien/birdclef-2026-ensemble`

## Decisions
- `muhammadsaadalvi/birdclef-2026-wildsound-v8`: reject for final route; metadata has `enable_gpu=true` and `enable_internet=true`, and it depends on several prior BirdCLEF competition sources. This violates the CPU-only/no-internet final inference target.
- `kijiang/birdclef2026-v337`: reject as immediate Run-mode candidate; it is the same Anthony/Model_2+Model_5 style public-reference family and is extremely close to the existing v87/v53/v38 family. Source similarity to `anthonytherrien/birdclef-2026-ensemble` is `0.999993`; source similarity to local v87 is about `0.993897`.
- `anthonytherrien/birdclef-2026-ensemble`: reject as immediate Run-mode candidate; prior local v51/v52/v53 attempts already tested the Anthony family, with v53 completing but becoming a v38-family near-duplicate. Re-running the same family is unlikely to justify UTC slot two.

## Next Candidate Direction
Search should move away from:
- EoS5/Model_5/Karnak/v38-v87 near-duplicates;
- Youssef E1/BirdNET-disabled route;
- BirdNET CC BY-NC routes;
- GPU/internet notebooks.

The next real candidate should be structurally different in final output, CPU/no-internet, and complete Run-mode before any competition submission.

