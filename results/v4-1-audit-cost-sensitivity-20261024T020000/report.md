# CEAV-M1 V4.1 — Audit-cost sensitivity

Scope: fixed V3-HET pair; no policy re-optimization.

Crossover: `kappa* = 527/1500`.
Audit-only cash gate: `kappa <= 259/100`.
Hybrid cash gate: `kappa <= 9449/3000`.

Hybrid is cheaper only on the open interval above `kappa*`; equality is a tie.

| kappa | Audit cash | Hybrid cash | Cheaper | Hybrid robust |
| ---: | ---: | ---: | --- | --- |
| 0 | 381/160 | 14551/6000 | audit_only | True |
| 1/4 | 203/80 | 15301/6000 | audit_only | True |
| 527/1500 | 3121/1200 | 3121/1200 | tie | True |
| 3/8 | 837/320 | 3919/1500 | hybrid | True |
| 1/2 | 431/160 | 16051/6000 | hybrid | True |
| 1 | 481/160 | 17551/6000 | hybrid | True |
| 9449/3000 | 20879/4800 | 4 | hybrid | True |

Finding: `hybrid_fixed_pair_has_a_positive_audit_cost_tradeoff_but_quality_tradeoff_remains`.
This does not establish a frontier or production advantage.
