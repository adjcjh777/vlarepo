# v394 Safe/Bold Blend Probe

Updated: 2026-05-24 15:33:16 UTC

Status: `PROMOTE-v394-safe-bold-blend-LOCAL-ONLY-NO-SUBMIT`.

## Research Question

Can a convex blend of the v391 safe_final and v387 bold_final local candidates dominate either endpoint on robustness while v387's real submission is pending?

## Result

- Pass-count: `21`
- Best portfolio candidate: `safe0.80_bold0.20`
- Best macro gain: `+0.00308164`
- Best fold std delta: `-0.00188085`
- Best weak gain: `+0.00968517`
- Decision: `PROMOTE-v394-safe-bold-blend-LOCAL-ONLY-NO-SUBMIT`
- Next: Materialize only after v387 resolves and only if this blended portfolio is needed over v391/v387 endpoints.

## Endpoint Metrics

- safe v391: macro_gain `+0.00282022`, fold_std_delta `-0.00188085`, weak_gain `+0.00886356`
- bold v387: macro_gain `+0.00291826`, fold_std_delta `-0.00083026`, weak_gain `+0.00917166`

## Top Macro Rows

candidate,macro_gain,fold_std_delta,weak_followup_gain,top5_hit,changed_cells,material_class_regressions_lt_003
safe0.30_bold0.70,0.003147000196065619,-0.0009458113492890052,0.009890572044777834,0.5068493150684932,323,0
safe0.80_bold0.20,0.0030816449905235466,-0.0018808458385290716,0.009685169970216734,0.5068493150684932,323,0
safe0.50_bold0.50,0.0030816449905235466,-0.0009458113492890052,0.009685169970216734,0.5068493150684932,323,0
safe0.45_bold0.55,0.0030816449905235466,-0.0009458113492890052,0.009685169970216734,0.5068493150684932,323,0
safe0.40_bold0.60,0.0030816449905235466,-0.0009458113492890052,0.009685169970216734,0.5068493150684932,323,0
safe0.35_bold0.65,0.0030816449905235466,-0.0009458113492890052,0.009685169970216734,0.5068493150684932,323,0
safe0.20_bold0.80,0.0030816449905235466,-0.0009458113492890052,0.009685169970216734,0.5068493150684932,323,0
safe0.15_bold0.85,0.0030816449905235466,-0.0008302581915264617,0.009685169970216734,0.5068493150684932,323,0
