# Reproduction guide

## Environment

Use Python 3.12 or newer. The package uses only the standard library. Run all
commands from the `review-package` directory so that the namespace packages
`verification` and `tests` resolve only to files in this bundle.

## Commands

```text
python -X utf8 -m verification.manuscript_editorial_audit
```

Expected output:

```text
status: PASS
certificate_sha256: fde3ad4745b37e270469aaec2692a51c83cbcf5db7fcb0a16938296a6e25b7d5
metric_rows_checked: 80
```

This checks every equilibrium row stored in the certificate. It verifies the
conditional definitions and exact reductions `WrongPayout=FA/2` and
`Loss=FA+FR/2`, then checks the neutral, positive-witness, negative-witness,
local-boundary, and safe-component values used by the manuscript.

```text
python -X utf8 -m verification.independent_t3_t5_review
```

Expected exact outputs include:

```text
T3 certified_effort_gap: 7/500
T3 M_L: 33/50
T3 M_H: 37/50
T3 delta: 2/25
T4 Selective: (-70/633, 175/1102)
T4 Uniform: (-218750/2070709, 218750/1365587)
T5 branch_candidates: 4320
T5 full_profiles_covered: 466560
T5 checks: 5590
T5 Selective symmetric safe component: (-70/633, 175/1922)
T5 Uniform symmetric safe component: (-218750/2070709, 109375/1189451)
```

The runner reports exact Fraction values and checks four pure equilibria at
Selective `b=1/10`, three of which fail a quality gate.

```text
python -X utf8 -m verification.review_summary
```

This prints the full active equilibrium profiles and metrics at `b=1/10` for
both mechanisms, followed by the neutral All-H01 metrics. It is the quickest
reviewer-facing check of the three bad witnesses and the Selective/Uniform
baseline.

```text
python -X utf8 -m unittest tests.test_dual_boundary -v
```

Expected result: ten tests, all passing. The suite checks frozen calibration,
all branch profiles, exact local boundaries, closed interval behavior, metric
weights, mutation probes, all three Judge positions, the `b=1/10` failure tie,
and the independent completeness audit.

## Clean-directory procedure

To avoid accidental imports from a parent checkout, copy this directory to a
new empty directory, change into that directory, and run the four commands
above. Do not set `PYTHONPATH` to the parent repository. A valid clean run
must show the package root as the current directory and must not require any
file outside it.

## Expected central values

| Result | Selective | Uniform |
|---|---:|---:|
| neutral exposure | `2557/6250` | `2557/6250` |
| neutral expected cash | `46957/25000` | `46957/25000` |
| neutral loss | `348/3125` | `4499061/39062500` |
| local H01 interval | `(-70/633,175/1102)` | `(-218750/2070709,218750/1365587)` |
| symmetric all-pure safe component | `(-70/633,175/1922)` | `(-218750/2070709,109375/1189451)` |
| pure equilibria at symmetric `b=1/10` | 4 | 4 |
| bad equilibria at symmetric `b=1/10` | 3 | 3 |
