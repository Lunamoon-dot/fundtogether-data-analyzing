# CEAV-M1: theorem and counterexample catalog

Date: 2026-10-24. Evidence baseline: commit
`b6935ea11d6dda42ec089c83e03013db7f86fdf4` on
`research/v6-rave-phase01`. This document packages existing results for a
paper; it changes no game, parameter, gate, source code or historical artifact.

The paper's defensible claim is a **conditional mechanism-separation result
with exact finite strategic counterexamples**. The identities below are
proved directly. Numerical equilibrium boundaries are exact for the frozen
finite game; they are neither simulation estimates nor guarantees for every
mechanism or every economic environment. The specific contribution's priority
is not established by the focused literature comparison in this document.

## 1. Definitions, evidence types and fixed assumptions

The [parent synthesis memo](CEAV_M1_RESEARCH_SYNTHESIS_AND_FEASIBILITY_MEMO.md)
records V3–V6 and the dual-purpose feasibility argument. The
[boundary report](CEAV_M1_DUAL_STRATEGIC_BOUNDARY_REPORT.md),
[protocol](CEAV_M1_DUAL_BOUNDARY_PROTOCOL.md) and
[configuration](configs/dual_boundary.json) define the certified fixed game.
This catalog's identifiers T1–T5 do not replace historical proposition numbers.

At a positive-probability public branch `Z=z`, each of three Judges chooses
one plan from `A={L0,L1,H00,H01,H10,H11}`. Low observes no private signal and
reports its constant label. High pays `c_i>0`, observes `X_i`, and uses the
specified two-entry report map. For example, H01 reports `X_i`; H10 reverses
it; H00/H11 may buy information and ignore it. Plans are contingent on Z;
there is no cross-branch constraint. All unilateral comparisons freeze peer
strategies, audit policy and published decision tables.

For the dual witness, the prior is `P(Y=1)=1/2`. Conditional on Y, Z, all
three potential X signals and T are independent. Their symmetric sensitivity
and specificity are respectively `7/10`, `4/5` and `9/10`; `c_i=1/20`.
These are synthetic assumptions. They are not measured audit or reviewer
performance. Ground truth Y is used for the probability model and evaluation;
the reward rule observes T rather than Y.

Payment and decision coins are hidden until reports lock:

```text
A_pay ~ Bernoulli(a), independently of signals and all reports.
A_dec ~ Bernoulli(d(Z,r)), conditionally independent of A_pay.
R_i = f + mu*A_pay*1{r_i=T}.
If A_pay OR A_dec occurs, observe one common T and charge one audit.
U_i = E[R_i] - effort_cost_i + b_i*P(D_final=1).
e(Z,r) = P(A_pay OR A_dec | Z,r) = a + (1-a)*d(Z,r).
```

The fixed dual witness has `a=2/5`, `mu=2`, `f=0`, `B=6`, `kappa=1/4`.
Selective uses `d=1/6` only on `S={Z=0,sum(r)=2}`; Uniform uses
`d=19/1250` everywhere. Both reuse T for the final decision and both pay the
bonus only on A_pay. The frozen H01-calibrated tables choose release when
posterior odds are at least 2 (`C_FA=2,C_FR=1`):

| Z | Number of reports equal to 1 | g0 | g1(T=0) | g1(T=1) |
|---:|---:|---:|---:|---:|
|0|0|0|0|0|
|0|1|0|0|0|
|0|2|0|0|1|
|0|3|1|1|1|
|1|0|0|0|0|
|1|1|0|0|1|
|1|2|1|0|1|
|1|3|1|1|1|

The decision uses g0 without either audit and g1 with their union. These
tables stay fixed when actual strategies differ from H01. Under H01 their
pre-audit odds are `(3/7 if z=0 else 7/3)*4^(2*k-3)`; T=1 multiplies them
by 9 and T=0 divides them by 9. This fully specifies off-equilibrium use.

Metrics use the actual strategy-induced distribution:
`FA=P(D=1|Y=0)`, `FR=P(D=0|Y=1)`, wrong payout `=FA/2` at payout value 1,
and decision loss `=FA+FR/2`. Original gates are `FA<=1/5`, `FR<=1/4`,
wrong payout `<=3/20`, expected cash `<=4`, union exposure `<=1/2`, and
reward reserve `<=6`. Gates constrain the designer, not player deviations.

| Label | Meaning in this package |
|---|---|
| General proposition | An algebraic implication under explicitly quantified assumptions; proof below. |
| Exact finite result | Rational evaluation of a specified finite game, with every declared action/profile checked and ties retained. Exactness removes numerical approximation, not model assumptions. |
| Finite parameter-grid result | A collection of exact results at listed configurations; it does not interpolate between them. |
| Simulation evidence | Randomly sampled numerical outcomes. No theorem or headline boundary in this package relies on Monte Carlo simulation. |
| Empirical evidence | Measurements from actual milestone/reviewer/auditor observations. None of the synthetic accuracies in this catalog has this status. |

## 2. T1: audit eligibility can create a profitable reporting deviation

**Assumptions.** Fix a branch z, constant Low peer reports z, two available
Low reports r0=z and r1=1-z with equal effort cost, and fixed T distribution
conditional on z. A report-dependent audit coin has probabilities q0 and q1
on the corresponding report vectors and is independent of future T conditional
on those locked observables. The only report-dependent transfer is
`mu*A*1{r_i=T}`, with `mu>0`; any fee is constant; `b_i=0`.

**Proposition T1.** This deviation is strictly profitable if and only if

```text
q1*P(T=1-z|z) > q0*P(T=z|z).
```

In particular, if unanimity has `q0=0`, dissent has `q1=d>0`, and
`P(T=1-z|z)>0`, the unanimous Low profile is not a branch equilibrium.

**Proof.** Staying yields `f+mu*q0*P(T=z|z)` and deviating yields
`f+mu*q1*P(T=1-z|z)`. Subtract; the fees and equal effort costs cancel.
With report-dependent peer uncertainty the correct general comparison is
`mu*Delta E[q(Z,r)*1{r_i=T}|I]`, rather than a product of unconditional
marginals. The stated assumptions justify the factorization used here.

**Exact witness.** In historical F51-02/Q1-zero, `mu=d=1`,
`P(T=1-z|z)=17/50`, and copy-Z to dissent gains exactly `17/50`.
Certificate S below contains `P1_audit_seeking_gain`; this refutes copy-Z as
an equilibrium, without asserting that all other equilibria are good.

**Counterexample to overgeneralization.** Report dependence alone is
insufficient. At the same peer reports and signal law, take `q0=1` and
`q1=1/2`. The difference divided by mu is
`(1/2)*(17/50)-33/50=-49/100`, so this dissent is unprofitable. This is a
logical counterexample to “every report-dependent audit rewards dissent,”
not a proposed replacement policy or a newly searched point.

**Applicability.** T1 diagnoses a payment-selection channel. It does not
cover compensating transfers, penalties, inverse-probability adjustments,
report-dependent audit accuracy, or external decision interests. A mismatch
with noisy T does not prove dishonesty. It is not a universal impossibility
theorem for selective verification.

**Novelty status.** The subtraction is elementary and should be presented
as a diagnostic lemma. [Zarkoob, Fu and Leyton-Brown (2020), §§2–3,
Theorems 3.3 and 5.1](https://www.ifaamas.org/Proceedings/aamas2020/pdfs/p1593.pdf)
provides incentive-compatible report-sensitive spot checks under its own
conditions. Thus report dependence is compatible with incentives; T1's
specific condition matters. Costly verification also predates CEAV:
[Ben-Porath, Dekel and Lipman (2014), official abstract](https://www.aeaweb.org/articles?id=10.1257/aer.104.12.3779)
studies allocation with checks and no transfers. That model does not imply
this bonus-specific counterexample. Priority for the exact CEAV construction
remains unestablished.

## 3. T2: absent marginal reporting incentives admit uninformative equilibria

**Assumptions.** At a reachable branch z, for every profile and unilateral
deviation considered, audits never occur, transfers are constants f_i,
`b_i=0`, High costs `c_i>0`, and there are no other report-dependent payoffs,
participation choices or cross-branch constraints.

**Proposition T2.** Every all-Low report profile is a branch Nash equilibrium.
Every High action is strictly worse than a Low action. Conditional on z,
these constant Low reports contain no additional information about Y.
If every other positive-probability branch has an equilibrium, and contingent
choices/payoffs factor by branch, any such Low branch equilibrium can be
combined with those other branch equilibria into a full pure equilibrium.
A gate violation follows only if at least one resulting decision distribution
violates a specified gate.

**Proof.** Each Low report gives utility f_i; each High plan gives
`f_i-c_i<f_i`. Thus no Low-to-Low deviation is strictly profitable and all
High deviations lose. The report vector is a constant conditional on z, so
it adds no information beyond z. Since each branch has positive weight, a
full strategy is a best response precisely when each independently changeable
branch choice is. The last sentence deliberately requires a decision-quality
witness; reporting indifference alone does not imply poor decisions.

**Exact bad witnesses.** Historical F51-01/Q2-z1 admits all L1 in both
branches, with `FA=1` and maximum unilateral regret zero. Its z0 branch
satisfies the absent-incentive condition, while z1's Low best response
extends it to a full equilibrium. Historical F51-02/Q2-z0 admits
`(H01,H01,H01)` at z0 and `(L0,L0,L0)` at z1, with
`FR=2321/3125`. Certificate V6 below retains both full deviation tables;
Certificate S separately checks the P2 witness and regret zero.

**Counterexamples to overgeneralization.** If audit probability is zero
only at the current profile, but dissent can trigger a paid audit, T2's
premise fails; T1 supplies the exact historical counterexample. Also, a
decision rule based on perfectly informative Z could decide correctly while
all reports were indifferent. Thus “uninformative reporting equilibrium”
and “bad decision equilibrium” must remain separate assertions.

**Applicability.** Constant positive fees do not restore marginal reporting
incentives. If `c_i=0`, High is no longer strictly dominated. If `b_i!=0`,
even an unpaid report can change decision utility; the proof no longer
applies. Extending a branch result requires the other branch equilibria;
their existence cannot be presumed.

**Novelty status.** Constant-payoff indifference is a standard game-theoretic
observation. [Gao, Wright and Leyton-Brown (2019), accepted manuscript §3,
Theorem 1](https://dspacemainprd01.lib.uwaterloo.ca/server/api/core/bitstreams/2cf2eab2-324c-402f-98eb-ee05f2a446f4/content)
already distinguishes costly-signal truthfulness from low-cost equilibria
under explicit universal-mechanism quantifiers. T2 is a scoped direct lemma;
the CEAV witnesses illustrate a particular settlement consequence, not a new
general impossibility result.

## 4. T3: conditional neutral feasibility with separated audit purposes

### T3a: payment factorization and effort threshold

**Assumptions.** Use the dual timing in §1. A_pay is independent of the
Judge's information I, chosen report, peers and future T; T has the same
law on payment and decision routes; reports lock first; only A_pay earns
the match bonus. For the incentive conclusion `b_i=0` and no other
report-dependent payoffs apply. The Judge may ignore X after buying it.

**Proposition T3a.** For every information set I of positive probability
and report r chosen solely from I (and independent private randomization),

```text
E[R_i | I,r] = f + mu*a*P(T=r | I).
M_L(i,z) = max_r P(T=r | z).
M_H(i,z) = sum_x P(x|z)*max_r P(T=r | z,x).
delta_i(z) = M_H(i,z)-M_L(i,z) >= 0.
```

Optimal High is strictly better than optimal Low iff
`mu*a*delta_i(z)>c_i`; equality retains both. This comparison is independent
of peers and d. A report cannot increase payment eligibility, although it
can change expected match payment. A modal label of T is optimal; binary
match is not a strictly proper probability scoring rule.

**Proof.** Factor A_pay out of the conditional expected transfer by its
independence. Optimize the resulting binary match probability first over
reports and then over effort; High can reproduce the best Low report, which
proves nonnegative delta before cost. Subtract c_i for High. No decision
quantity enters neutral utility. With nonzero b_i, the additional term is
`b_i*Delta P(D_final=1)` and this independence argument alone cannot
establish truthful reporting or useful effort.

**Boundaries and counterexamples.** If X never changes the posterior modal
label, delta is zero and no positive effort cost can be paid away with this
reward; historical F51-01 has exactly this property. If eligibility is
revealed before effort, or a decision-only audit earns a bonus, the displayed
factorization no longer represents the promised incentive game. A
report-independent lottery alone does not establish raw-X truthfulness.

### T3b: nonempty analytic region under the fixed primary environment

**Assumptions.** Fix F51-02 signals/costs, the frozen tables in §1,
`b=(0,0,0)`, `f=0`, `mu=2`, and `d=t*1_S`. For this on-paper region only,
let a and t satisfy the parent's already-derived inequalities:

```text
5/16 < a < 1/2,
0 < t <= (1/2-a)/(1-a),
u = (1-a)*t.
```

No new parameter search or recommendation to retune the certified witness
is made here.

**Proposition T3b.** Every configuration in that analytic region has unique
pure stationary equilibrium All-H01 in the declared six-action class. All
original gates pass there. Selective decision auditing has strictly smaller
decision loss than uniform decision auditing at matched union exposure,
with the same payment lottery, rewards, distributions and terminal tables.

**Proof.** In each branch, optimal Low has match `33/50`, while the unique
posterior-modal High report is H01 with match `37/50`.
`delta=2/25`, so `2*a*delta>1/20` iff `a>5/16`. Every Judge's action is
therefore uniquely optimal independently of peers. At the named point its
smallest branch gap is `7/500`; uniqueness is an incentive conclusion, not
an imposed truthful strategy.

The union is `a+u` on S and a elsewhere, so is at most `1/2` for every
report vector, including deviations. At equilibrium `P(S)=57/625`, giving
`q_bar=a+u*(57/625)`. Reward reserve is `3*mu=6`; expected cash is
`(111/25)*a+(1/4)*q_bar<469/200<4`. Reserve is not multiplied by a;
effort disutility is not charged again as cash.

Direct integration of the frozen tables gives

```text
FA = 23/625 - (24/3125)*a + (21/3125)*u <= 251/6250 < 1/5,
FR = 137/625 - (429/3125)*a - (324/3125)*u <= 137/625 < 1/4,
wrong payout = FA/2 < 3/20.
```

These conservative inequalities use `a,u>=0` and `u<=1/2`; they prove
quality throughout the region rather than interpolate a grid. At H01,
`VOI(S)=47/95` and overall `G=E[VOI]=477/6250`. Uniform decision sampling
with `d_uniform=t*P(S)` has the same union exposure. Subtracting losses
under that same report distribution gives

```text
loss_Uniform - loss_Selective
 = u*(57/625)*(47/95 - 477/6250) > 0.
```

Equal exposure and the same equilibrium reports imply equal cash here.
This equality must be recomputed at strategic equilibria with external
interests; it is not a property of arbitrary endogenous profiles.

**Certified point.** Certificate S and Certificate D agree at
`a=2/5,t=1/6,mu=2`:

| Metric | Selective | Uniform |
|---|---:|---:|
| Neutral pure equilibrium | unique All-H01 | unique All-H01 |
| FA | 43/1250 | 328691/9765625 |
| FR | 481/3125 | 3184297/19531250 |
| Decision loss | 348/3125 | 4499061/39062500 |
| Union exposure | 2557/6250 | 2557/6250 |
| Expected cash | 46957/25000 | 46957/25000 |
| Reward reserve | 6 | 6 |

**Counterexample to dropping strictness.** Algebraically, at the excluded
effort boundary `a=5/16` under the same neutral reward, H01 and modal Low
tie independently of peers. The copy-Z all-Low profile is then an
equilibrium. Its fixed tables reject for z0/k0 and release for z1/k3, so
`FA=FR=3/10`, violating both quality gates. This is a consequence of the
existing threshold proof, not a newly searched reward policy. Under the
certified parameters, T5 supplies a separate counterexample to extending
neutral feasibility to unrestricted external interests.

**Applicability.** This is conditional on T provenance, known likelihoods,
fixed calibration, lottery timing/independence, no outside options and the
declared strategy class. It is not optimality over reward policies. Historical
shifted/Direct-Brier lower bounds are score-specific and do not rule out
binary-match feasibility. Neutral quality is a strategic guarantee here
because equilibrium is proved; optimizing Bayes decisions while simply
assuming truthful reports would be only a decision-theory comparison.

**Novelty status.** Independent spot checking and costly effort incentives
are established. [Gao et al., §4, Definitions 4–8 and Theorem 2](https://dspacemainprd01.lib.uwaterloo.ca/server/api/core/bitstreams/2cf2eab2-324c-402f-98eb-ee05f2a446f4/content)
compares peer-insensitive checks with peer-prediction augmentation under its
own score and objectives. [Liu and Chen (2017), abstract and problem
formulation](https://ojs.aaai.org/index.php/AAAI/article/view/10619/10478)
studies learning reward levels for costly effort across repeated tasks.
[Chen et al. (2023), official abstract](https://proceedings.mlr.press/v202/chen23ah.html)
studies scoring-rule design for strategic information acquisition.
Zarkoob et al. (2020), §4.1 Theorem 4.3, also separates having a TA signal
from using it to spot check every student; acquisition/payment separation
itself is not claimed as a new idea.
The candidate CEAV contribution is the particular shared-T separation,
union/reserve/cash accounting and bounded quality comparison. The literature
comparison does not establish that this architecture is the first of its kind.

## 5. T4: exact local boundary under external release utility

**Assumptions.** Freeze exactly the certified point in §1, all H01 peers,
and the two published decision tables. Each Judge has constant b_i measured
in the same utility units as rewards: it is the utility difference between
certain release and certain rejection, not an audit accuracy or monetary
payout fraction. Effort/report plans remain the six declared actions.

**Finite theorem T4.** For each Judge separately, H01 is a strict best
response in both branches against H01 peers if and only if

```text
Selective: -70/633 < b_i < 175/1102.
Uniform:   -218750/2070709 < b_i < 218750/1365587.
```

Thus All-H01 is a strict pure equilibrium when every coordinate b_i lies
inside the corresponding local interval, including heterogeneous vectors.
At either endpoint H01 is a weak best response. Immediately below the
negative endpoint L0 at z0 improves utility; immediately above the positive
endpoint L1 at z1 improves utility. The result does not assert global
equilibrium uniqueness or gate quality at other equilibria.

**Proof and exact certificate.** Write the deviation gain as
`-gamma(a,z)+b_i*Delta s(a,z)`. Certificate D's
`mechanisms.{selective,uniform}.local_deviations` includes all 36 ordered
Judge/branch/action rows per mechanism, and
`all_pairwise_indifferences_against_h01_peers` retains all 90 action-pair
intersections. Each row is a rational half-line condition; intersect the
five nonself inequalities in both branches. The binding Selective rows are

```text
z0, L0: -7/500 - (633/5000)*b_i <= 0  iff b_i >= -70/633.
z1, L1: -7/500 + (551/6250)*b_i <= 0  iff b_i <= 175/1102.
```

All other rows give weaker bounds on this intersection. The independent
[review derivation](verification/DUAL_BOUNDARY_INDEPENDENT_REVIEW.md) tabulates
each of the six exact utilities and release slopes for both branches and
mechanisms. The independent oracle recomputes these from primitive states.

The parent's `|b_i|<7/500` is a sufficient bound using
`|Delta s|<=1`; it is not the maximal local interval. Selective's exact
negative magnitude is `5000/633` times that radius, and its positive endpoint
is `6250/551` times it. Neither factor is a global-equilibrium result.

There is also a narrower all-peer guarantee already implicit in the parent:
the neutral gap is at least 7/500 against every peer profile, while any
release-probability change is at most one. Thus `|b_i|<7/500` for every
Judge preserves strict H01 dominance and unique pure equilibrium even for
heterogeneous vectors in that small box. This conservative analytic guarantee
does not compute the exact global boundary throughout heterogeneous R^3.

**Counterexample to overgeneralization.** At symmetric `b=1/10`, every
coordinate is inside Selective's local interval and All-H01 remains strict,
yet bad equilibria exist by T5. Hence T4 cannot justify an all-equilibrium
guarantee. Outside T4's endpoints the binding deviations themselves refute
continued local truthfulness; no payment-audit manipulation is necessary.

**Applicability and novelty status.** External decision preferences alter
reports even with report-independent payment eligibility. [Boutilier (2012),
AAMAS paper §§3–4](https://www.cs.toronto.edu/~cebly/Papers/Boutilier_aamas12.pdf)
already studies decision-interested experts and utility uncertainty. Modeling
b or deriving sensitivity bounds is not claimed as novel. The exact CEAV
fractions are instance-specific, reproducible candidate findings whose
priority remains unestablished. This is not a bound on b enforced by the
mechanism: no identity, payment or audit rule here limits outside interests.

## 6. T5: local truthful stability does not imply global equilibrium quality

**Assumptions.** Use the fixed game and gates in §1, stationary pure
strategies, task-local unilateral deviations and scenario vectors
`b*v` for `v in {000,100,010,001,111}`. The last vector is symmetric
preferences; the middle three cover every single biased Judge position.
This is an all-real scalar b analysis of these declared scenarios, not an
analysis of every heterogeneous vector in R^3.

**Finite theorem T5.** A pure equilibrium exists for every real b in each
declared scenario for each mechanism. The maximal connected component
containing zero on which **every pure equilibrium** passes every original
gate is:

| Scenario | Selective | Uniform |
|---|---|---|
| Neutral v=000 | all real b, since actual interests stay zero | same |
| One biased Judge, each position | `(-70/633,+infinity)` | `(-218750/2070709,+infinity)` |
| Symmetric v=111 | `(-70/633,175/1922)` | `(-218750/2070709,109375/1189451)` |

All finite endpoints are excluded because a bad weak equilibrium exists
there. Within the symmetric safe component, All-H01 is the unique pure
stationary equilibrium. A gate-safe one-biased positive tail does not imply
truthful effort persists: the biased Judge changes reports past T4's positive
local endpoint while the two neutral Judges remain H01.

**Completeness proof.** For each mechanism, scenario, z and all 216 ordered
branch profiles p, impose all 18 inequalities including self comparisons:

```text
c_i(p_i,z)-c_i(a_i,z)
  + b*v_i*[s_z(p)-s_z(a_i,p_-i)] >= 0,
for every Judge i and every a_i in A.
```

Their intersection is the exact closed interval, singleton, unbounded set
or empty set on which p is an equilibrium. Positive branch probabilities
and independent contingent choices make full equilibria exactly the branch
profile pairs whose intervals overlap. Endpoints partition the real line
into singleton points and open cells with constant equilibrium sets. This
covers `216^2=46,656` full profiles per scenario, `466,560` across both
mechanisms and five scenarios, using 4,320 branch candidates and 77,760
affine inequalities. Keeping exact ties is essential to the open safe bounds.

Certificate D contains every nonempty full-profile interval, metrics and
all metricwise maximizing witnesses. For each mechanism there is 1 profile
ever an equilibrium in neutral, 5 in each one-biased scenario, and 24 in
symmetric; these are unions over b, not simultaneous counts. H00/H11 were
checked but are strictly dominated by Low with the same constant report;
H10 was retained and has no nonempty interval in these scenarios. Empty
equilibrium sets are never treated as passing robustness gates.

**Exact counterexample separating local from global.** In Selective, each
ordered version of the profile

```text
z0: (H01,H01,H01)
z1: (L1,L1,H01)
```

is an equilibrium on `[175/1922,7/46]`. A Low Judge remains Low precisely
when its extra release utility offsets `7/500` of neutral loss:
`-7/500+b*(961/6250)>=0`. The High Judge remains High while
`7/500-b*(23/250)>=0`; all remaining deviations are checked in Certificate
D. In the interior these three asymmetric equilibria are strict. At
`b=1/10` exactly four pure equilibria coexist: those three and strict All-H01.
Each bad witness has:

| Metric | Selective bad equilibrium | Uniform corresponding bad equilibrium |
|---|---:|---:|
| Closed NE interval | [175/1922,7/46] | [109375/1189451,8750/58811] |
| FA | 1391/6250 | 2148236/9765625 |
| FR | 313/3125 | 8571103/78125000 |
| Wrong payout | 1391/12500 | 1074118/9765625 |
| Decision loss | 852/3125 | 42942879/156250000 |
| Union exposure | 2557/6250 | 2557/6250 |
| Expected cash | 45357/25000 | 45357/25000 |
| Reserve | 6 | 6 |
| Failed gate | FA>1/5 | FA>1/5 |

These are witness metrics, not the simultaneous maxima of every metric;
for example, at symmetric b=1/10 Selective's worst FR and cash come from
All-H01. On the negative boundary, the Selective profile
`z0=(L0,H01,H01), z1=(H01,H01,H01)` is an NE on
`[-70/439,-70/633]` and has `FR=853/3125>1/4`. Its union exposure
`411/1000` and cash `7387/4000` differ from Uniform's corresponding
`2557/6250` and `46157/25000`. Neutral matched exposure is not an equality
constraint on subsequent equilibria.

**Boundary of applicability.** This exact enumeration proves a pure-class
statement, not mixed-equilibrium uniqueness, equilibrium selection,
coalition-proofness, Sybil resistance, participation or a claim-level
permissionless ground-truth guarantee. All-real b coverage does not make b
an empirically estimated quantity. The one-biased safe tail and symmetric
interval cannot be extended to arbitrary heterogeneous b vectors without
additional analysis. Restricting b is a trust assumption, not enforcement.

**Novelty status.** The existence/uniqueness distinction is established
game theory. [Witkowski and Parkes (2012), Theorem 9 and discussion after
Theorem 10](https://cdn.aaai.org/ojs/8261/8261-13-11789-1-2-20201228.pdf)
proves truthful best responses assuming truthful peers and separately
discusses other equilibria. T5's candidate contribution is the explicit
budget-feasible settlement example where an exact global quality boundary
precedes the truthful local boundary. This focused comparison does not
establish literature priority for that phenomenon.

## 7. Historical results that constrain the manuscript

The consolidated [parent evidence table](CEAV_M1_RESEARCH_SYNTHESIS_AND_FEASIBILITY_MEMO.md#2-consolidated-verified-evidence-table)
must remain the source for version-specific inputs and historical run paths.
The paper should not make V3–V6 look like identical parameterizations.

| Historical evidence | Permitted inference | Prohibited extrapolation |
|---|---|---|
| V3 anchor-only entry condition `q>25/57`; asymmetric effort witness | Algebraic threshold at specified V3-HET inputs; exact witness can pass quality with weak C staying Low. | All Judges must buy effort; anchor-only is generally optimal. |
| V3.1, six policies by 18 uncertainty scenarios | None of six policies passes all of its 18 scenarios; 108 policy/scenario cases are evaluated overall. | Continuous uncertainty impossibility or a confidence interval. |
| V3.2/V3.3 report-sensitive studies | Configuration-specific equilibrium and budget evidence; preserve their own gates and B values. | Treat a permissive diagnostic robust flag as original-quality success; import V3.3 B=24 as B=6 evidence. |
| V4 conditional centered peer scoring, without audits | Retain its unfavorable low-information equilibrium witnesses. | Public-signal subtraction removes every bad equilibrium. |
| V5 shifted/Direct Brier | Propriety concerns the scored event; exact effort/cap/cash bounds close those named score/input combinations. | All proper scores, binary match or all verification mechanisms are impossible. |
| V6 exogenous decision allocation | Fixed-distribution value of information and matched-exposure decision comparison. | Truthful equilibrium, useful effort or worst-equilibrium quality without deviations. |
| V6 strategic closeout | Four exact bad-NE certificates refute universal gates for the four declared discovered candidates. | Exhaustive equilibrium counts, preregistered discovery for every witness, or all-selective-mechanism impossibility. |
| Dual boundary | Exact affine all-real-b analysis in five declared pure scenarios. | Empirical validation, arbitrary heterogeneous b, mixed/coalitional robustness or production readiness. |

An external Bayes decision analysis says what an optimizer should do **if
the specified report distribution is supplied**. A mechanism guarantee must
also establish which reports and effort are equilibrium behavior and what
happens at every equilibrium in its declared scope. These are different
logical steps even when the evaluator uses the same posterior table.

## 8. Certificate and source identity register

Hashes below were read from the raw certificate files and compared to their
historical manifests during preparation. They identify bytes; proofs,
independent implementations, tests and declared coverage support correctness.
This document does not regenerate or overwrite those historical artifacts.

| ID | Exact artifact | Raw SHA-256 |
|---|---|---|
| S | [Synthesis named-instance certificate](results/research-synthesis-audit-20261024T045716506866Z/named-checks/certificate.json) | `299276eba5840d3fb7ec83501eab6f559e8cb9ad805544dc1488e3cb37f03837` |
| D | [Dual boundary certificate](results/dual-strategic-boundary-20261024T0524070523492Z/analysis/certificate.json) | `fde3ad4745b37e270469aaec2692a51c83cbcf5db7fcb0a16938296a6e25b7d5` |
| V6 | [Four targeted V6 negative certificates](results/v6-closeout-20261024T021405861852Z/negative-certificates/certificate.json) | `edd11133109d71625473bd35210409f9da9d35b6f836475c71b4eef6ce7d5df1` |

The [boundary evidence manifest](results/dual-strategic-boundary-20261024T0524070523492Z/manifest.json)
binds the complete per-cell Markdown, pinned sources and replay. It records
5,590 independent checks, all 864 branch metrics compared between separate
implementations, 10 focused tests normally and under `-O`, 24 V6 regression
tests and nine detected mutation probes. Its pinned analyzer and independent
oracle hashes are respectively
`8c943bb2f6f23c5032768dd60834f9e926a1d6aa3f83205482b54f4a645d6d0b`
and `bab19a553f73be9d843c0e199dd66b3ef2d0c25ab918f2e9b81dc8d9e4e4d3a9`.
The implementations share no payoff, Bayes or interval helper. They remain
executable rational verification, not a proof-assistant formalization.

The [synthesis manifest](results/research-synthesis-audit-20261024T045716506866Z/manifest.json)
records 224 named checks normally and under `-O`, independent cross-oracle
comparisons, a byte-identical pinned replay and historical identity checks.
It does not certify a new mechanism version. Historical freeze declarations
state their actual timing; neither exploratory work nor post-discovery
witnesses should be relabeled as preregistered.

## 9. Paper claim boundary

Suitable title-level framing is a study of **separated verification purposes,
budget-constrained incentives and exact external-interest failure**. T1/T2
are diagnostic propositions; T3 combines a direct incentive argument with
an analytic feasible region; T4/T5 are exact finite-game theorems backed by
complete rational certificates. None is a new general theory of spot
checking, scoring rules, costly verification or decision-interested experts.

The candidate scientific result is worth writing with all negative evidence
intact. Submission novelty claims must await the additional priority
assessment identified after the focused comparison in
[paper readiness](CEAV_M1_PAPER_READINESS.md) and
[research gaps](CEAV_M1_RESEARCH_GAP_ASSESSMENT.md). Real signal quality,
auditor independence, costs, external interests and participation remain
empirical/trust questions governed by the
[empirical protocol](CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md). This package
supports preparing a conditional theory paper; it supplies no production
readiness claim and authorizes no new mechanism version.
