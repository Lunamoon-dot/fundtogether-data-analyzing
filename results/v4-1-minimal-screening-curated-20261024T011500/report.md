# CEAV-M1 V4.1 — Curated screening evidence

# CEAV-M1 V4.1 — Minimal screening

Conclusion on the declared finite grid: `negative_no_incremental_hybrid_advantage_on_declared_grid`.

Audit-only was enumerated over all valid `M x Q` policies; Conditional-only and Hybrid were enumerated over all valid policies under `B=6`.

Worst-equilibrium metrics retain all pure equilibria. Equilibrium selection is not modeled. This artifact does not claim global optimality, production readiness or quality outside the pinned fixtures/grid.

## F41-01

| Mechanism | Policies | Pure-eq policies | Robust policies | Selected robust policy |
| --- | ---: | ---: | ---: | --- |
| audit_only | 48 | 48 | 34 | Policy(lambda_peer=Fraction(0, 1), mu=Fraction(1, 4), q=Fraction(1, 4), budget=Fraction(6, 1)) |
| conditional_only | 4 | 4 | 0 | None |
| hybrid | 72 | 72 | 58 | Policy(lambda_peer=Fraction(1, 4), mu=Fraction(1, 4), q=Fraction(1, 4), budget=Fraction(6, 1)) |

## F41-02

| Mechanism | Policies | Pure-eq policies | Robust policies | Selected robust policy |
| --- | ---: | ---: | ---: | --- |
| audit_only | 48 | 48 | 13 | Policy(lambda_peer=Fraction(0, 1), mu=Fraction(3, 4), q=Fraction(1, 1), budget=Fraction(6, 1)) |
| conditional_only | 4 | 4 | 0 | None |
| hybrid | 72 | 72 | 12 | Policy(lambda_peer=Fraction(1, 4), mu=Fraction(3, 4), q=Fraction(1, 1), budget=Fraction(6, 1)) |

## V3-HET

| Mechanism | Policies | Pure-eq policies | Robust policies | Selected robust policy |
| --- | ---: | ---: | ---: | --- |
| audit_only | 42 | 42 | 6 | Policy(lambda_peer=Fraction(0, 1), mu=Fraction(5, 4), q=Fraction(3, 4), budget=Fraction(6, 1)) |
| conditional_only | 3 | 3 | 0 | None |
| hybrid | 54 | 54 | 8 | Policy(lambda_peer=Fraction(1, 4), mu=Fraction(1, 1), q=Fraction(5, 8), budget=Fraction(6, 1)) |

## Robust frontier comparison

Hybrid counts as incrementally advantageous only when it strictly dominates an Audit-only Pareto-frontier robust policy on declared audit probability, worst-equilibrium cash, worst-equilibrium accuracy and all worst-equilibrium error metrics. A lower-q/higher-cash tradeoff is not an incremental advantage.

| Fixture | Audit frontier | Audit min worst cash | Hybrid min worst cash | Audit min q | Hybrid min q | Unmatched tradeoffs | Strict dominance |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| F41-01 | 1 | 129/800 | 729/800 | 1/4 | 1/4 | 0 | False |
| F41-02 | 1 | 333/200 | 6321/2500 | 1/2 | 1/2 | 0 | False |
| V3-HET | 1 | 381/160 | 14551/6000 | 5/8 | 1/2 | 2 | False |

Incremental conclusion: `negative_no_incremental_hybrid_advantage_on_declared_grid`.

The full nested-equilibrium JSON is retained locally; screening_summary.json is the reviewed projection.
