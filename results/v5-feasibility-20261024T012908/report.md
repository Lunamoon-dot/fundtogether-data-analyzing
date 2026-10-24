# CEAV-M1 V5.0 — Phase 1 feasibility certificate

Scope: exact finite-sum feasibility only; no production engine or global policy search.

Finding: `v5_a_infeasible_on_f51_01_and_f51_02; direct_brier_requires_separate_screening`.

V5.0-A strict high effort is impossible at the reward cap on both public-signal fixtures.
Direct Brier is retained as a separate ablation because its reserve cap is different.

| Fixture | Mechanism | mu_max | Strict entry at selected policy | Strict entry possible at cap | Target cash floor | Cash gate |
|---|---|---:|---:|---:|---:|---:|
| F51-01 | incremental | 1 | False | False | 3 | True |
| F51-02 | incremental | 1 | False | False | 3 | True |
| F51-01 | direct | 2 | False | False | 6597/1250 | False |
| F51-02 | direct | 2 | True | True | 17451/6250 | True |
| V3-HET | incremental | 19/20 | True | True | 63/20 | True |
| V3-HET | direct | 19/10 | True | True | 2401/625 | True |

Quality metrics are `not_evaluated` in Phase 1; positive effort gain is not a policy pass.
