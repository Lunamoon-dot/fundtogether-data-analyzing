# CEAV-M1 V6.0 — Phase 0–1 feasibility contract

Revision `phase01-r1`. This file is the frozen evidence plan, not an executed
result. Executed findings belong to new immutable `results/v6-*` artifacts.
Normative model: [V6 RAVE spec](CEAV_M1_V6_RAVE_SPEC.md).

## Study and stop rules

Freeze config/spec/oracle/tests before the separate checker implementation.
Three fixtures, four selective allocations each, exact exposure-matched optimal
uniform comparisons. No reward grid, general equilibrium engine or robustness
sweep. Use all H01 only as exogenous reports for Gate B. C/D remain not run.
Report loss, cash and exposure separately; primary candidate criterion is in
spec §6. The primary objective and gate thresholds cannot change after output.

The report must answer the ten questions in the brief, including attribution,
noisy decision flips, report manipulation, unanimous copy-Z, economic cost,
candidate discovery, residual risks, and a scoped Phase-2 GO/NO-GO.

## Independent evidence

Oracle enumerates potential private signals/T and explicit audit outcomes;
checker instead aggregates report likelihoods analytically. Compare exact
posteriors, state masses, VOI, terminal metrics, rewards and utilities on all
declared fixture/policy/profile records. Oracle has no local imports. Tests
also contain hand-derived checks: F51-02 copy-Z preliminary FA=FR=3/10,
wrong payout=3/20; Q1-zero exposure=0; each Low contrarian earns 17/50
instead of zero with mu=1,b=0. V3-HET target Z weights are 2/5,3/5.

Verify six actions including H00/H11, ties at uniform q=5/8 in F51-02,
all-Low/asymmetric retained witnesses, target vs balanced-stratum cash,
claim-level kappa, non-discounted reserve, posterior normalization and frozen
policy under deviations. At least one frozen-table stress comparison must
demonstrate that recalibrating on the actual deviation would change results.

Mutation probes directly alter temporary checker source for wrong threshold,
T used before selection, frozen policy violation, majority orientation,
exposure distribution, FA/FR denominator, per-Judge audit cost, reserve
discount, dropped effort cost, dropped ties, target/batch replacement, omitted
deviations and false stop pass. Every mutation has a named executing test and
fails with an assertion; import errors/zero tests do not count as kills.

Run focused V6 tests (normal and -O), independent oracle comparison, mutation
checks, immutable manifest rehash and relevant V4/V5 regressions. Keep red and
failed runs. Output refuses existing directories. Historical manifests are
rehash-checked and their source context is recorded, never rewritten.

## Status interpretation

SPECIFIED: model/evidence contract. IMPLEMENTED: offline checker/oracle/tests.
VERIFIED: only after commands and artifacts show execution. Phase-1 GO is
candidate discovery for a future strategic study; it is not mechanism success,
exhaustive equilibrium coverage, equilibrium selection, mixed/coalition/bribery
resistance, real auditor calibration or production acceptance.
