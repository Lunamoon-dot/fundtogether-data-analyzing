# CEAV-M1: dual-purpose strategic robustness boundary

**Decision: STRATEGIC_FAILURE.** The frozen Selective mechanism has a nonempty
robust neighborhood, but symmetric release interests of `b=1/10` admit three
strict bad equilibria alongside strict All-H01. The exact all-pure gate-safe
component around zero is **`-70/633 < b < 175/1922`** for symmetric preferences.
This result concerns the declared stationary six-action class. It is not a
universal impossibility theorem or an empirical estimate of release interests.

## 1. Frozen scope and sources

The parent is [the certified synthesis memo](CEAV_M1_RESEARCH_SYNTHESIS_AND_FEASIBILITY_MEMO.md),
at commit `df931b0ad73d464a6937a3a7c34879a978981b90`, following the historical
V6 evidence at `6fb0f4367187cc9eeefb180d4336f237275e38c5`. Its F51-02 witness
is copied explicitly into [the study configuration](configs/dual_boundary.json).
The [protocol](CEAV_M1_DUAL_BOUNDARY_PROTOCOL.md) defines this study's evidence
contract. These are primary sources for this mathematical experiment; no new
external theorem or literature novelty claim is needed for the finite proof.

We retain `a=2/5`, `t=1/6` only on `S={Z=0,sum(reports)=2}`, `mu=2`, `B=6`,
`kappa=1/4`, `C_FA=2`, `C_FR=1`, `f=0`, payout value 1 and operating cost 0.
The independent payment/decision coins are hidden until reports lock. One
trusted T is observed on their union, charged once; bonus eligibility is
only A_pay. T is correct with probability 9/10; Z with 7/10; each private X
with 4/5, conditionally independent given Y. Prior and P(Z=z) are each 1/2.
High costs 1/20. These are synthetic assumptions, not measured guarantees.

The original gates remain FA<=1/5, FR<=1/4, wrong payout<=3/20, cash<=4,
union exposure<=1/2 and reward reserve<=6. Judge deviations are not restricted
by these designer gates. No policy, reward or calibration is re-optimized.

## 2. Fixed calibration and affine utility

Under frozen H01 calibration, posterior odds before T are

```text
O(z,k) = (3/7 if z=0 else 7/3) * 4^(2k-3), k=sum(reports).
T=1 multiplies O by 9; T=0 divides O by 9.
Release iff O>=2 (posterior>=2/3).
```

| Z | k | g0 | g1(T=0) | g1(T=1) |
|---|---|---|---|---|
|0|0|0|0|0|
|0|1|0|0|0|
|0|2|0|0|1|
|0|3|1|1|1|
|1|0|0|0|0|
|1|1|0|0|1|
|1|2|1|0|1|
|1|3|1|1|1|

These tables stay fixed even when actual reports are uninformative. The
independent oracle derives them from primitive Bayes likelihoods, separately
from the analyzer's stored table. Frozen calibration is part of the game.

For a branch profile p, let `s_z(p)=P(D_final=1|Z=z,p)` and
`c_i(a,z)=(4/5)*P(report_i=T|z,a)-(1/20)*1(a is High)`. Then

```text
U_i(a,p_-i | z) = c_i(a,z) + b_i*s_z(a,p_-i).
Deviation gain against H01 = -gamma_i(a,z) + b_i*Delta s_i(a,z).
```

Payment eligibility cannot be increased by changing reports. Expected match
payment can change; external preference also rewards a different release
probability. Independent payment sampling removes the V6 audit-seeking
payment channel, while this decision channel remains. H01 here means raw X
reporting; its neutral optimality follows from posterior modes, not from an
assumption that Judges cooperate.

## 3. Exact local boundary for every Judge

Each Judge position has the same following table by fixture symmetry.
All 36 ordered rows per mechanism, and all 90 pairwise action intersections
per mechanism, are retained in the JSON certificate. Here gamma is neutral
H01 utility minus deviation utility; Delta s is deviation release minus H01
release. H01 itself is identical at every b. A listed intersection need not
be a best-response transition if another action already dominates it.

|Z|Action|gamma|Selective Delta s|Selective indifference b|Uniform Delta s|Uniform indifference b|
|---|---|---|---|---|---|---|
|0|L0|7/500|-633/5000|-70/633|-2070709/15625000|-218750/2070709|
|0|L1|27/100|3/50|9/2|234943/3906250|2109375/469886|
|0|H00|8/125|-633/5000|-320/633|-2070709/15625000|-1000000/2070709|
|0|H01|0|0|all b|0|all b|
|0|H10|48/125|-333/5000|-640/111|-1130937/15625000|-2000000/376979|
|0|H11|8/25|3/50|16/3|234943/3906250|1250000/234943|
|1|L0|27/100|-899/6250|-3375/1798|-2228063/15625000|-4218750/2228063|
|1|L1|7/500|551/6250|175/1102|1365587/15625000|218750/1365587|
|1|H00|8/25|-899/6250|-2000/899|-2228063/15625000|-5000000/2228063|
|1|H01|0|0|all b|0|all b|
|1|H10|48/125|-174/3125|-200/29|-215619/3906250|-500000/71873|
|1|H11|8/125|551/6250|400/551|1365587/15625000|1000000/1365587|

Intersecting the five alternative-action inequalities in both branches gives:

| Mechanism | Exact strict H01 best-response interval against H01 peers |
|---|---|
|Dual-Selective|`(-70/633, 175/1102)`|
|Dual-Uniform|`(-218750/2070709, 218750/1365587)`|

At either finite endpoint a Low action ties. Immediately outside the negative
endpoint, L0 in Z=0 is profitable; outside the positive endpoint, L1 in Z=1
is profitable. The statement holds separately for each b_i with peer
strategies frozen; it proves local All-H01 stability, not global uniqueness.

The parent's `|b_i|<7/500` bound used `|Delta s|<=1`, so it is conservative.
For Selective the negative radius is larger by factor `5000/633` (about
7.899), and the positive endpoint by `6250/551` (about 11.343). The added
ranges are exactly `30569/316500` on the negative magnitude and
`39893/275500` on the positive side. Uniform's factors are
`15625000/2070709` and `15625000/1365587`. These factors describe local
comparisons. The exact symmetric all-pure positive threshold is instead
`175/1922`, which is `6250/961` times 7/500.

## 4. Exact pure-equilibrium completeness argument

For each of the 216 ordered branch profiles, each Judge and every one of
the six deviations, intersect

```text
c_i(candidate)-c_i(deviation)
 + b*v_i*[s(candidate)-s(candidate_-i,deviation)] >= 0,
v in {000,100,010,001,111}.
```

Each inequality is a closed half-line, all real b, or empty. Their exact
intersection is the candidate's NE interval. All finite endpoints are
rational. Retain singleton intervals and ties. Full stationary profiles
are exactly pairs of branch NE with overlapping intervals, because both
Z branches have positive probability and choices are independently
deviable. This covers all 216^2=46,656 full profiles per scenario, or
466,560 mechanism/scenario profile combinations. It checks 4,320 branch
candidates and all 77,760 affine inequalities, including self comparisons.

Partition the real line at the full-equilibrium interval endpoints into
singleton points and open intervals, with both unbounded tails. The set of
equilibria is provably constant on each open cell. Exact rational
representatives verify cells; they do not approximate the b axis. The
separate oracle audit reconstructs intervals and directly checks all
actions on every cell. No arbitrary floating-point grid is used.

H00 and H11 were included: L0 and L1 have the identical report/decision
distribution without their effort cost, so dominate them for all b. H10
was included and has no nonempty NE interval in these scenarios. Low and
asymmetric profiles remain in the certificate. No pure-equilibrium gap
occurs anywhere on the real b line in the analyzed scenarios. The code
explicitly rejects an empty pure set as robustness success.

|Scenario, per mechanism|Distinct full profiles that are NE somewhere|Exact b cells|Existence on all real b|
|---|---:|---:|---|
|Neutral (0,0,0)|1|1|yes|
|One biased A (b,0,0)|5|9|yes|
|One biased B (0,b,0)|5|9|yes|
|One biased C (0,0,b)|5|9|yes|
|Symmetric (b,b,b)|24|21|yes|

Counts here are the union across b, not simultaneous equilibrium counts.
The generated **interval-report.md** gives each cell's actual count,
All-H01 status, metricwise worst FA, FR, wrong payout, loss, cash, exposure,
reserve, gates and bad witness IDs. The JSON retains complete profiles,
their closed intervals and every maximizing witness. Worst metrics may
come from different equilibria.

## 5. Exact robustness components and the failure witness

|Scenario|Selective: maximal all-pure gate-safe component containing zero|Uniform: same component|
|---|---|---|
|Neutral|all real parameter b (actual interests remain zero)|same|
|One biased Judge, each position|`(-70/633, +infinity)`|`(-218750/2070709, +infinity)`|
|Symmetric|`(-70/633, 175/1922)`|`(-218750/2070709, 109375/1189451)`|

All finite endpoints above are excluded because a bad weak equilibrium
already exists there. For one biased Judge, H01 is unique only inside its
local interval; beyond the positive local threshold that Judge changes
reports, while the two neutral Judges retain H01. Every resulting pure
equilibrium still passes the original gates for all positive b in this
particular model. This is a gate guarantee, not continued truthful effort.

For symmetric Selective preferences, a new profile has Z=0 actions HHH
and Z=1 actions L1,L1,H, where H=H01. For either Low Judge, switching back
to H sacrifices release probability `961/6250` to gain neutral utility
`7/500`. Thus Low is willing to remain exactly when

```text
-(7/500) + b*(961/6250) >= 0  <=>  b >= 175/1922.
```

For the remaining High Judge, keeping High rather than becoming the third
L1 requires `7/500-b*(23/250)>=0`, or `b<=7/46`. All other deviations
were checked as well. Consequently each of the three ordered versions is
an equilibrium on **`[175/1922,7/46]`**, strict in its interior. The bad
equilibria coexist with strict All-H01; they are not caused by an All-H01
best-response failure. At b=1/10 exactly four full equilibria exist.

|Metric at the first positive bad witness|Selective|Uniform|
|---|---:|---:|
|Closed equilibrium interval|[175/1922,7/46]|[109375/1189451,8750/58811]|
|FA|1391/6250|2148236/9765625|
|FR|313/3125|8571103/78125000|
|Wrong payout|1391/12500|1074118/9765625|
|Decision loss|852/3125|42942879/156250000|
|Expected total rewards|214/125|214/125|
|Union exposure|2557/6250|2557/6250|
|Cash|45357/25000|45357/25000|
|Reserve|6|6|
|Failed gate|FA>1/5|FA>1/5|

At b=1/10 the worst FR and cash still come from All-H01: Selective worst
FR is 481/3125 and worst cash is 46957/25000. A single bad witness's
metrics must not be mislabeled as simultaneous maxima of all metrics.

The nearest negative bad Selective witness is Z=0 L0,H,H and Z=1 HHH,
with any ordered Low position. Its interval is `[-70/439,-70/633]`,
FA=671/25000, FR=853/3125>1/4, wrong payout=671/50000,
loss=4083/25000, exposure=411/1000 and cash=7387/4000.
For one biased Judge only its own ordered position is available. For
symmetric preferences all three ordered versions occur.

## 6. Fair strategic comparison and budget boundary

Uniform freezes the parent's `d=19/1250`, hence union `2557/6250` for any
reports. It uses the same a, mu, T/X/Z distributions, reward reserve,
g0/g1 and losses. Matching exposure under neutral All-H01 does not force
matching actual exposure or cash under different equilibrium reports.

The independent [review derivation](verification/DUAL_BOUNDARY_INDEPENDENT_REVIEW.md)
and the generated per-cell tables give both strategic outcomes. Three
exact comparisons illustrate their differences:

- At neutral b=0 both have unique All-H01. Selective loss=348/3125;
  Uniform loss=4499061/39062500. Both cash=46957/25000 and
  exposure=2557/6250. The parent's neutral loss gain is preserved.
- At symmetric b=1/10 both have four equilibria and fail FA in their
  three bad equilibria. Selective worst loss=852/3125;
  Uniform worst loss=42942879/156250000. The latter fails slightly later
  on the positive side, while Selective tolerates a larger negative
  magnitude. Neither has general strategic dominance.
- At one-biased b=4/25, Selective's unique equilibrium changes that Judge
  to L1 in Z=1, yielding cash=46157/25000; Uniform still has unique
  All-H01 and cash=46957/25000. At the negative bad witnesses above,
  Selective exposure=411/1000 and cash=7387/4000, whereas Uniform's
  corresponding witness has exposure=2557/6250 and cash=46157/25000.
  These are actual profile computations, not imposed equal-cost claims.

For any reports and b, Selective union exposure is at most 1/2 statewise.
Total expected rewards are at most `3*mu*a=12/5`. Hence cash is at most
`12/5+(1/4)*(1/2)=101/40<4`, and reserve is always `3*mu=6`.
Uniform has lower constant exposure than 1/2. These gates cannot fail in
this fixed study; the failure is reporting/effort and equilibrium decision
quality. Payment independence does not pay away external decision utility.

## 7. Evidence, reproducibility and recommendation

The two implementations share no payoff/Bayes/interval code: the analyzer
marginalizes actual reports; the independent Fraction oracle enumerates
potential X,T states and both audit coins. Every one of 864 branch profiles
agrees in every metric and each Judge's neutral utility. A second interval
audit uses separate bound collection, full branch products and direct
best-response checks. The independent research review also derived the
local and symmetric global boundaries separately.

Focused tests cover DB01-DB10. Nine in-memory/test-only mutations check
union-based payments, double audit charges, recalibration, dropped exact
ties, omitted Low/asymmetric profiles, reversed external slopes and changed
peer strategies, plus reporting a minimum as the worst metric. Historical
source/results are not edited. The new freeze
record explicitly says it occurred after exploratory local arithmetic,
before analyzer implementation; it is not a new version preregistration.

The reproducibility bundle is generated by the checked commands below;
its top-level manifest binds the analysis certificate, per-cell Markdown,
normal and optimized tests, mutation results, independent audit, pinned
source replay, and raw source/output hashes. Existing output directories
are refused. Raw hashes establish identity, separately from correctness.

```powershell
python -X utf8 -m unittest tests.test_dual_boundary -v
python -X utf8 -m verification.dual_boundary_mutations
python -X utf8 -m verification.dual_boundary_evidence --out NEW_DIRECTORY
```

**Scientific recommendation:** publish the bounded mechanism-separation
result together with its exact external-interest failure boundary. State
that independent payment sampling fixes audit eligibility manipulation
under neutral interests, but shared release preferences can sustain bad
equilibria before truthful effort loses local stability. The useful positive
result is a declared pure-equilibrium interval under fixed signal, audit,
timing and calibration assumptions; it does not support production release
guarantees at unbounded b or establish global mixed-equilibrium uniqueness.

The verdict is **STRATEGIC_FAILURE at symmetric b=1/10**, with the exact
safe symmetric component `(-70/633,175/1922)` and local interval
`(-70/633,175/1102)` recorded separately. Unknown or heterogeneous release
interests, mixed strategies, collusion, participation, auditor provenance
and calibration error remain outside this study. No broader uncertainty
study, retuning, V7, merge, blockchain, API or UI implementation follows.
