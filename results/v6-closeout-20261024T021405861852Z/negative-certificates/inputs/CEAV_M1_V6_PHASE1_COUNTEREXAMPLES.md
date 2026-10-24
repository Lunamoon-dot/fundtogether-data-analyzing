# V6 Phase 1 — Targeted negative certificates and final stop rule

2026-10-24. Addendum to `CEAV_M1_V6_RAVE_SPEC.md` revision
`v6.0-rave-phase01-r1`. No primitive, loss, policy, payment, gate, calibration,
or decision table changes. This is **post-discovery targeted counterexample
analysis**, not preregistered candidate discovery and not a Phase-2 grid.

## Why an addendum

The immutable primary certificate at
`results/v6-rave-phase1-20261024T021148403371Z/` has four meaningful exogenous
H01 candidates. Its `GO_candidate_discovery_only` is a Gate-B flag. That is
necessary, not sufficient for recommending a larger strategic study after a
counterexample already disproves its required worst-equilibrium guarantee.
The original artifacts/spec freeze stay unchanged. This addendum resolves
that distinction explicitly, following the supplied brief's theory-first
stop rule; it does not reinterpret a truthful result as strategic acceptance.

## Fixed negative witnesses

All use b=(0,0,0), the original f/mu/B/kappa/loss/exposure assumptions, and
the original all-H01 calibrated frozen tables. A/B/C order is significant.

| Fixture/policy | Branch Z=0 | Branch Z=1 | Failing gate |
|---|---|---|---|
| F51-01/Q1-zero | L0,L0,L1 | L1,L1,L0 | exposure=1 > 1/2 |
| F51-01/Q2-z1 | L1,L1,L1 | L1,L1,L1 | FA=1 > 1/5 |
| F51-02/Q1-zero | L0,L1,H01 | L0,L1,H01 | exposure=1 > 1/2 |
| F51-02/Q2-z0 | H01,H01,H01 | L0,L0,L0 | FR=2321/3125 > 1/4 |

These are four explicit profiles, not enumeration over 216 branch profiles.
Their equilibrium status must be checked against every one of the six actions
for all three Judges and both Z branches; ties remain in best responses.
Maximum regret must equal zero exactly in both independent calculations.

### Analytic motivation for F51-02/Q1-zero

Opposite constant reports from A and B guarantee disagreement, so C faces
uniform audit and prefers H01: `37/50-1/20=69/100 > 33/50`.
At Z=0, A receives 33/50, B receives 17/50. A's H01 reward before cost is
`37/50-439/2500=1411/2500`; B's is
`37/50-1011/2500=839/2500`. Subtract 1/20 to get 1286/2500
and 714/2500, respectively; both are below their Low rewards.
Z=1 swaps the roles. The remaining report maps must still be checked, rather
than assuming these two comparisons exhaust deviations. Audits occur on
every case, violating the exposure cap despite the exogenous exposure 12/25.

### Analytic motivation for Q2

On a zero-audit branch neutral utility is f minus effort cost, so any Low
report is a best response. On the audited F51-02 branch H01 is strictly
optimal for binary audit match; on F51-01 copy-Z is optimal and private effort
has zero binary-action information value. This permits bad unaudited Low
reports. Terminal decisions still use the original H01 calibrated tables.

## Final stop rule and scope

For every candidate that passes Gate B, one certified bad pure equilibrium is
sufficient to refute the universal quality/exposure requirement. It is not
necessary to enumerate all equilibria to disprove a universal property.

Final recommendation is NO-GO for Phase 2 **on the declared Phase-1 candidate
set** if all four have certified zero-regret failure witnesses. If a witness
does not verify, return `UNRESOLVED`, never NO-GO or GO by assumption.
The other eight primary comparisons failed the preregistered discovery rule;
retain their original reasons. There is no claim that all RAVE policies are
impossible, no global optimum, no mixed-equilibrium result, no full Gate C/D
acceptance, and no automatic V6.1/6.2 follow-up.

Before implementing this small negative-certificate writer, pin this addendum,
the four test expectations, original config/oracle/checker and original primary
run manifest with current UTC/raw hashes. The event is explicitly after
counterexample discovery and before its automated certificate writer.
