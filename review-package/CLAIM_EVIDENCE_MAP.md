# Claim-to-evidence map

This map separates algebraic proofs, exact certificate evidence, independent
computational checks, and external literature. The package contains no human
referee report.

| Claim | Evidence in this package | Exact location or command | Evidence class |
|---|---|---|---|
| `FA=P(D=1|Y=0)` and `FR=P(D=0|Y=1)` | Manuscript metric section and editorial audit | `docs/CEAV_M1_MANUSCRIPT_V0_2.md` §4; `python -m verification.manuscript_editorial_audit` | definition plus exact replay |
| `WrongPayout=V*P(Y=0,D=1)` | Manuscript and audit | `docs/CEAV_M1_MANUSCRIPT_V0_2.md` §4 | algebra |
| `Loss=C_FA*P(Y=0,D=1)+C_FR*P(Y=1,D=0)` | Manuscript and audit | same §4; audit checks all 80 rows | algebra plus exact replay |
| Frozen calibration table | Configuration | `configs/dual_boundary.json:g0_by_z_and_report_sum`, `g1_by_z_and_report_sum` | frozen input |
| T3 effort gap `7/500` | Independent Fraction runner | `python -m verification.independent_t3_t5_review`; output key `T3.certified_effort_gap` | independent computation |
| T3 factorization | Proof text | `docs/CEAV_M1_MANUSCRIPT_V0_2.md` Proposition 1; theorem catalog | algebraic proof |
| T4 Selective local interval | Certificate and test | `frozen-boundary/certificate.json:mechanisms.selective.scenarios.symmetric.all_h01_closed_equilibrium_interval`; `tests/test_dual_boundary.py::test_DB01_local_paper_boundaries` | exact certificate plus test |
| T4 Uniform local interval | Certificate and test | same JSON path under `uniform` | exact certificate plus test |
| T5 Selective symmetric safe component | Certificate and test | `...mechanisms.selective.scenarios.symmetric.safe_component_containing_zero`; `test_DB09_global_boundary_and_failure_ties` | exhaustive pure-class certificate |
| T5 Uniform symmetric safe component | Certificate and test | same JSON path under `uniform` | exhaustive pure-class certificate |
| Four pure equilibria at `b=1/10` | Summary and certificate | `python -m verification.review_summary`; symmetric equilibrium arrays in `certificate.json` | exact witness enumeration |
| Three bad witnesses at `b=1/10` | Summary and gate fields | summary output `all_gates_pass=false`; certificate `metrics` and `gates` | exact witness enumeration |
| Neutral Selective/Uniform comparison | Summary and certificate | summary neutral metrics; `scenarios.neutral.equilibria` All-H01 rows | exact baseline certificate |
| Exhaustive scope | Manifest and independent audit | `frozen-boundary/manifest.json:independent_audit`; `verification/dual_boundary_audit.py` | reproducibility metadata |
| T3–T5 prior art boundary | Novelty note and bibliography check | `docs/CEAV_M1_NOVELTY_AUDIT_T3_T5.md`, `docs/CEAV_M1_BIBLIOGRAPHY_PRIMARY_CHECK.md` | primary-source review |

The central certificate SHA-256 is
`fde3ad4745b37e270469aaec2692a51c83cbcf5db7fcb0a16938296a6e25b7d5`.
This proves byte identity of the artifact, not universal truth beyond the
declared model and strategy class.
