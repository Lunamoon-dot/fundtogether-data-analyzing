# Claim-to-evidence map

This map separates algebraic proofs, exact certificate evidence, independent
computational checks, and external literature. The package contains no human
referee report.

Active manuscript: [v0.3](docs/CEAV_M1_MANUSCRIPT_V0_3.md). The
[correction closeout](docs/CEAV_M1_MANUSCRIPT_V0_3_CORRECTION_CLOSEOUT.md)
supersedes the reported prose defects in historical v0.2 without changing
the frozen game or evidence.

| Claim | Evidence in this package | Exact location or command | Evidence class |
|---|---|---|---|
| `FA=P(D=1|Y=0)` and `FR=P(D=0|Y=1)` | Manuscript metric section and certificate checker | `docs/CEAV_M1_MANUSCRIPT_V0_3.md` §4; `python -m verification.manuscript_editorial_audit` | definition plus stored-metric check; no automatic prose inspection |
| `WrongPayout=V*P(Y=0,D=1)` | Manuscript and certificate checker | `docs/CEAV_M1_MANUSCRIPT_V0_3.md` §4 | algebra |
| `Loss=C_FA*P(Y=0,D=1)+C_FR*P(Y=1,D=0)` | Manuscript and audit | same §4; audit checks all 80 rows | algebra plus exact replay |
| Frozen calibration table | Configuration | `configs/dual_boundary.json:g0_by_z_and_report_sum`, `g1_by_z_and_report_sum` | frozen input |
| T3 effort gap `7/500` | Independent Fraction runner | `python -m verification.independent_t3_t5_review`; output key `T3.certified_effort_gap` | independent computation |
| T3 factorization | Self-contained assumptions and proof text | `docs/CEAV_M1_MANUSCRIPT_V0_3.md` Proposition 1; theorem catalog | algebraic proof; coin independent jointly of information and future T |
| T4 Selective local interval | Certificate and test | `frozen-boundary/certificate.json:mechanisms.selective.scenarios.symmetric.all_h01_closed_equilibrium_interval`; `tests/test_dual_boundary.py::test_DB01_local_paper_boundaries` | exact certificate plus test |
| T4 Uniform local interval | Certificate and test | same JSON path under `uniform` | exact certificate plus test |
| T4 primitive payoffs and corrected signs | Independent primitive oracle and focused tests; scoped correction check | `dual_boundary_oracle.py`; DB01–DB03; `python -m verification.manuscript_correction_checks` | primitive calculations plus neutral/endpoint sign checks; runner T4 only divides hardcoded binding rows |
| T5 Selective symmetric safe component | Certificate and test | `...mechanisms.selective.scenarios.symmetric.safe_component_containing_zero`; `test_DB09_global_boundary_and_failure_ties` | exhaustive pure-class certificate |
| T5 Uniform symmetric safe component | Certificate and test | same JSON path under `uniform` | exhaustive pure-class certificate |
| Four pure equilibria at `b=1/10` | Summary and certificate | `python -m verification.review_summary`; symmetric equilibrium arrays in `certificate.json` | exact witness enumeration |
| Three bad witnesses at `b=1/10` | Summary and gate fields | summary output `all_gates_pass=false`; certificate `metrics` and `gates` | exact witness enumeration |
| Neutral Selective/Uniform comparison | Summary and certificate | summary neutral metrics; `scenarios.neutral.equilibria` All-H01 rows | exact baseline certificate |
| Exhaustive scope | Manifest and independent audit | `frozen-boundary/manifest.json:independent_audit`; `verification/dual_boundary_audit.py` | reproducibility metadata |
| T3–T5 prior art boundary | Novelty note and bibliography check | `docs/CEAV_M1_NOVELTY_AUDIT_T3_T5.md`, `docs/CEAV_M1_BIBLIOGRAPHY_PRIMARY_CHECK.md` | primary-source review |
| F1–F5 prose, scope and copy synchronization | v0.3 correction closeout; selected text checks | `docs/CEAV_M1_MANUSCRIPT_V0_3_CORRECTION_CLOSEOUT.md`; correction checker | scoped agent prose inspection and primary byline verification, not human referee review |

The central certificate SHA-256 is
`fde3ad4745b37e270469aaec2692a51c83cbcf5db7fcb0a16938296a6e25b7d5`.
This proves byte identity of the artifact, not universal truth beyond the
declared model and strategy class.
