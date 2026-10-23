# CEAV-M1 V3.2 — Verification plan

## Precondition

Freeze the V3.2 spec, engine design, verification plan, independent oracle, and red tests in one implementation-start event. The freeze must record that no V3.2 production support existed before the event.

## Tests

| ID | Gate | Evidence |
| --- | --- | --- |
| V32-T01 | strict schema accepts exact `q0/q1` | unit result and error field |
| V32-T02 | scalar V3 `audit_probability` is rejected | negative schema test |
| V32-T03 | V3.2 state support is 64 and normalizes to one | independent probability sum |
| V32-T04 | report-dependent anchor expectation matches oracle | exact fractions |
| V32-T05 | expected audit cost sums three Judge exposures | exact fractions |
| V32-T06 | focal best response uses `q_r` and frozen peers | independent witness |
| V32-T07 | V3.2 search enumerates 432 branch candidates | exhaustive count |
| V32-T08 | V3.2 study emits gates and failure witnesses | acceptance fixture |
| V32-T09 | V1/V2/V3/V3.1 regression suites remain green | test runner log |
| V32-T10 | CLI/API run provenance pins V3.2 spec and freeze | manifest/certificate |

## Independent oracle

`tests/oracle_v3_2.py` must calculate the small fixture directly from likelihoods and finite sums. It must not import `evaluate`, `best_response`, `report_sensitive`, or the production state enumerator.

## Acceptance fixture

The fixture uses three Judges, `π=1/2`, public/private sensitivities from the V3 heterogeneous preset, `q0=1/4`, `q1=3/4`, and a small reward budget sufficient for hybrid scoring. Expected values are exact strings and are generated independently before implementation support.

## Interpretation

Passing V32-T08 means the finite, declared uncertainty grid satisfies its gates. It does not prove production performance, mixed-equilibrium robustness, or resistance to collusion and Sybil attacks.

