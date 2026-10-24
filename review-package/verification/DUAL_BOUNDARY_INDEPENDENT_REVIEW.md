# Independent review: dual-purpose external-interest boundary

Date: 2026-10-24. This note independently derives the frozen Bayes tables,
local H01 thresholds and the first symmetric bad equilibria. It uses exact
`fractions.Fraction` sums over primitive binary states, without importing the
study analyzer, payoff helpers or the parent arithmetic checker. It is a
review derivation, not a replacement for the study's executable oracle and
immutable certificate.

Primary inputs are the F51-02 signal distribution represented by the packaged
[`configs/dual_boundary.json`](../configs/dual_boundary.json) and the named
dual witness in [the parent memo, sections 4–6](../docs/CEAV_M1_RESEARCH_SYNTHESIS_AND_FEASIBILITY_MEMO.md).
The configuration's historical V6 `mu=1` is not reused: this study freezes
the certified dual witness's `mu=2`, payment probability `a=2/5`, selective
decision probability `t=1/6`, uniform comparator probability `19/1250`,
`B=6`, `kappa=1/4`, and unchanged loss weights and gates. No historical file
or policy is changed.

## 1. Primitive calculation and frozen decision rule

The prior is 1/2. Conditional on Y, Z is correct with probability 7/10,
each of the three private signals X is correct with probability 4/5 and
the common audit T is correct with probability 9/10; these observations are
conditionally independent. Therefore P(Z=z)=1/2 and
P(Y=z | Z=z)=7/10.

For `k=sum(reports)` under H01 calibration, the posterior odds are

```text
O(z,k) = (3/7 if z=0 else 7/3) * 4^(2k-3).
O(z,k,T) = O(z,k) * (9 if T=1 else 1/9).
```

With C_FA=2 and C_FR=1, release minimizes expected loss when posterior
probability is at least 2/3, equivalently odds at least 2. There are no
posterior ties at this threshold in the frozen table.

| Z | k | P(Y=1 | Z,reports) | g0 | g1(T=0) | g1(T=1) |
|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 3/451 | 0 | 0 | 0 |
| 0 | 1 | 3/31 | 0 | 0 | 0 |
| 0 | 2 | 12/19 | 0 | 0 | 1 |
| 0 | 3 | 192/199 | 1 | 1 | 1 |
| 1 | 0 | 7/199 | 0 | 0 | 0 |
| 1 | 1 | 7/19 | 0 | 0 | 1 |
| 1 | 2 | 28/31 | 1 | 0 | 1 |
| 1 | 3 | 448/451 | 1 | 1 | 1 |

For each conditional-Z primitive state `(Y,X_A,X_B,X_C,T)`, multiply its
five independent conditional probabilities. Apply each actual action to
its X, then apply the frozen table to the resulting reports. The independent
audit union has probability `e=1/2` on `S={Z=0,k=2}` and `e=2/5` elsewhere
for Selective; Uniform has constant `e=2557/6250`. Its release probability
in that primitive state is `(1-e)*g0+e*g1(T)`.

Payment must be computed separately as `(4/5)*P(report_i=T)`, because
`mu*a=4/5`; it must not be multiplied by union exposure. Conditional branch
utility is `c_i(action,z)+b_i*s(profile,z)`, where c is payment minus effort
and s is actual final release probability. Integration over the two
positive-mass Z branches preserves these branch best-response comparisons.

## 2. Exact local boundary against All-H01

The following tables fix both peers at H01. Symmetry of F51-02 makes them
identical for Judges A, B and C. The listed breakpoint solves
`c(H01)-c(action)+b*(s(H01)-s(action))=0`. The H01 row is identical to itself
for every b. Any additional pairwise indifference point follows from
`b=-(c(action)-c(other))/(s(action)-s(other))` when the denominator is nonzero.

| Z | Action | Neutral c | Selective s | H01/action breakpoint |
|---:|---|---:|---:|---:|
| 0 | L0 | 66/125 | 439/5000 | -70/633 |
| 0 | L1 | 34/125 | 343/1250 | 9/2 |
| 0 | H00 | 239/500 | 439/5000 | -320/633 |
| 0 | H01 | 271/500 | 134/625 | identical |
| 0 | H10 | 79/500 | 739/5000 | -640/111 |
| 0 | H11 | 111/500 | 343/1250 | 16/3 |
| 1 | L0 | 34/125 | 1632/3125 | -3375/1798 |
| 1 | L1 | 66/125 | 2357/3125 | 175/1102 |
| 1 | H00 | 111/500 | 1632/3125 | -2000/899 |
| 1 | H01 | 271/500 | 4163/6250 | identical |
| 1 | H10 | 79/500 | 763/1250 | -200/29 |
| 1 | H11 | 239/500 | 2357/3125 | 400/551 |

| Z | Action | Neutral c | Uniform s | H01/action breakpoint |
|---:|---|---:|---:|---:|
| 0 | L0 | 66/125 | 1122523/15625000 | -218750/2070709 |
| 0 | L1 | 34/125 | 1033251/3906250 | 2109375/469886 |
| 0 | H00 | 239/500 | 1122523/15625000 | -1000000/2070709 |
| 0 | H01 | 271/500 | 399154/1953125 | identical |
| 0 | H10 | 79/500 | 412459/3125000 | -2000000/376979 |
| 0 | H11 | 111/500 | 1033251/3906250 | 1250000/234943 |
| 1 | L0 | 34/125 | 8182173/15625000 | -4218750/2228063 |
| 1 | L1 | 66/125 | 11775823/15625000 | 218750/1365587 |
| 1 | H00 | 111/500 | 8182173/15625000 | -5000000/2228063 |
| 1 | H01 | 271/500 | 2602559/3906250 | identical |
| 1 | H10 | 79/500 | 238694/390625 | -500000/71873 |
| 1 | H11 | 239/500 | 11775823/15625000 | 1000000/1365587 |

Consequently each Judge's H01 is a strict best response in both branches iff

```text
Selective: -70/633 < b_i < 175/1102.
Uniform:   -218750/2070709 < b_i < 218750/1365587.
```

At either endpoint a Low action ties H01; immediately outside, that action
is profitable. For both mechanisms the first positive deviation is L1 in
Z=1, and the first negative deviation is L0 in Z=0. Other Judges' b values
do not affect this local comparison while their strategies remain H01.

The parent's `|b_i|<7/500` is a sufficient bound valid against all peer
profiles, obtained using `|Delta release|<=1`. It is not asserted to be the
maximal local or global interval. Relative to the exact local boundaries:

| Mechanism | Negative magnitude / (7/500) | Positive endpoint / (7/500) | Added negative magnitude | Added positive range |
|---|---:|---:|---:|---:|
| Selective | 5000/633 | 6250/551 | 30569/316500 | 39893/275500 |
| Uniform | 15625000/2070709 | 15625000/1365587 | 94880037/1035354500 | 99815891/682793500 |

Selective's symmetric local radius is 70/633, about 7.899 times 7/500;
its positive local endpoint is about 11.343 times that bound. These are
local comparisons, not a global-uniqueness guarantee.

## 3. Independent symmetric pure-equilibrium interval enumeration

For each mechanism, branch and each of 216 ordered branch profiles, I
intersected all 18 unilateral inequalities `gap+b*release_difference>=0`.
The action identical to the candidate was retained as an equality. No
floating point was used. This gives the following complete nonempty branch
NE intervals for the symmetric scenario `(b,b,b)`. Every finite endpoint is
included; infinity is unbounded. `perm` includes each distinct ordering.
Here H means H01, and multiplicities count ordered Judge identities.

| Z | Branch profile | Multiplicity | Selective b interval | Uniform b interval |
|---:|---|---:|---|---|
| 0 | perm(L0,L0,H) | 3 | (-infinity,-70/439] | (-infinity,-218750/1122523] |
| 0 | perm(L0,H,H) | 3 | [-70/439,-70/633] | [-218750/1122523,-218750/2070709] |
| 0 | (H,H,H) | 1 | [-70/633,9/2] | [-218750/2070709,2109375/469886] |
| 0 | (L1,L1,L1) | 1 | [54/113,infinity) | [56250/119791,infinity) |
| 1 | (L0,L0,L0) | 1 | (-infinity,-45/34] | (-infinity,-56250/43469] |
| 1 | perm(L0,L0,H) | 3 | [-45/34,-375/442] | [-56250/43469,-703125/820333] |
| 1 | (H,H,H) | 1 | [-3375/1798,175/1102] | [-4218750/2228063,218750/1365587] |
| 1 | perm(L1,L1,H) | 3 | [175/1922,7/46] | [109375/1189451,8750/58811] |
| 1 | (L1,L1,L1) | 1 | [7/46,infinity) | [8750/58811,infinity) |

Thus there are 8 distinct branch profiles with some nonempty NE interval
at Z=0, and 9 at Z=1, for each mechanism. This does not mean 8 or 9
equilibria coexist at every b. Full stationary equilibria are exactly the
branch-profile pairs whose two closed b intervals intersect. These branch
NE intervals cover the real line in each branch, so a pure equilibrium
exists at every real b in this symmetric scenario.

H00 and H11 were included in the checks but cannot be equilibria: they
produce exactly the same report as L0 and L1 respectively and pay effort
1/20 unnecessarily. Their identical decision distribution makes that
dominance valid for every b. H10 was also retained; no H10 profile has a
nonempty NE interval in this symmetric calculation.

### Nearest loss of global quality around zero

For Selective, the component containing zero on which every pure stationary
equilibrium passes the original gates is exactly

```text
-70/633 < b < 175/1922, symmetric scenario only.
```

For Uniform the corresponding component is

```text
-218750/2070709 < b < 109375/1189451, symmetric scenario only.
```

In each open interval All-H is the unique pure stationary equilibrium.
The endpoints are excluded because a bad weak equilibrium exists there.
These statements follow from all branch profiles and all deviations, not
from an arbitrary grid of b samples. They do not assert anything about
mixed equilibria, correlated equilibria, coalitions or richer strategies.

At the positive endpoints, three additional bad equilibria appear while
All-H remains strict. Each has Z=0 profile HHH and Z=1 a permutation of
L1,L1,H. The relevant exact metrics are:

| Metric | Selective | Uniform |
|---|---:|---:|
| First bad positive b | 175/1922 | 109375/1189451 |
| This witness remains NE through | 7/46 | 8750/58811 |
| FA | 1391/6250 | 2148236/9765625 |
| FR | 313/3125 | 8571103/78125000 |
| Wrong payout | 1391/12500 | 1074118/9765625 |
| Decision loss | 852/3125 | 42942879/156250000 |
| Union exposure | 2557/6250 | 2557/6250 |
| Expected cash | 45357/25000 | 45357/25000 |
| Reward reserve | 6 | 6 |

Both FA values exceed 1/5. At the first positive threshold there are four
full equilibria: All-H plus the three ordered bad witnesses. For Selective,
the first bad threshold is about 0.09105, strictly below the local H01
threshold about 0.15880. At b=1/10 this bad witness is a strict equilibrium
and All-H is also strict. A claim of global robustness at 1/10 is false.

At the negative endpoints, three additional bad equilibria have Z=0 a
permutation of L0,H,H and Z=1 HHH. Their exact metrics are:

| Metric | Selective | Uniform |
|---|---:|---:|
| Nearest negative bad boundary | -70/633 | -218750/2070709 |
| This witness's lower NE endpoint | -70/439 | -218750/1122523 |
| FA | 671/25000 | 413347/15625000 |
| FR | 853/3125 | 1126397/3906250 |
| Wrong payout | 671/50000 | 413347/31250000 |
| Decision loss | 4083/25000 | 2666141/15625000 |
| Union exposure | 411/1000 | 2557/6250 |
| Expected cash | 7387/4000 | 46157/25000 |
| Reward reserve | 6 | 6 |

Both FR values exceed 1/4. This is an explicit comparison where equilibrium
report distributions make Selective's exposure and cash differ from the
Uniform comparator's, despite the original neutral exposure match.

## 4. Interval-algorithm requirements and scope

For scenario coefficients `k_i` (all 1 for symmetric; only one 1 for a
single biased Judge), the candidate branch profile is an NE exactly when
every action satisfies

```text
c(candidate_i,z)-c(deviation_i,z)
 + k_i*b*[s(candidate,z)-s(candidate_-i,deviation_i,z)] >= 0.
```

A zero slope with negative intercept rejects the candidate. A positive
slope imposes a closed lower bound; a negative slope a closed upper bound.
The intersection may be empty, a singleton, bounded or unbounded. Exact
ties must survive. Splitting endpoint singletons from open arrangement
cells is essential: dropping weak equilibria would wrongly include both
global-quality endpoints above. A rational cell representative is valid
only after exact interval construction proves the equilibrium set constant
throughout that open cell.

Neutral players in a single-biased-Judge scenario must still have every
deviation checked; their strictly dominant H01 action then follows from
the payment calculation. Checking each Judge position verifies ordering
and permutation handling even though this fixture is symmetric. This
independent review does not tabulate that scenario's full interval report.

For full-profile metrics, weight the conditional-Z contributions by the
actual P(Z)=1/2. FA and FR require dividing the joint error mass by
P(Y=0)=P(Y=1)=1/2; never average conditional-Z FA/FR with arbitrary batch
weights. Reward cash excludes effort costs and includes one audit charge
per union. Reserve is 3*mu=6, not expected payout or probability times cap.
Cash is always at most `3*(4/5)+(1/4)*(1/2)=101/40<4`, and exposure is at
most 1/2 statewise for Selective, so these two gates cannot be rescued or
violated by changing b in this frozen study. Quality can still fail.

All calibration tables, peer actions, audit reliability, payment eligibility
and policy constants must remain frozen during unilateral deviations.
Recalibrating g0/g1 at each actual profile would analyze a different game.
The positive coexistence failure above separates All-H local stability
from a guarantee over all equilibria; it is not a universal impossibility
theorem for dual-purpose mechanisms.
