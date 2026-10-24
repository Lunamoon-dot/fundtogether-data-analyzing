# Separating Payment and Decision Verification in Escrow Review

## A finite strategic boundary for costly information, external release interests, and equilibrium quality

**Manuscript version:** v0.1 (research draft)

**Date:** 2026-10-24

**Evidence baseline:** commit `886d2d4` on `research/v6-rave-phase01`

**Status:** ready for theory-draft circulation; not yet submission-ready

## Abstract

Escrow systems often ask reviewers to buy costly information, report a
binary judgment, and support a final release decision. A verification lottery
can improve the decision while damaging incentives when the lottery itself is
contingent on the report and the verified outcome earns a reward. This paper
studies that interaction in a frozen three-reviewer escrow model with a public
signal, private noisy signals, a trusted but noisy audit, a binary release
decision, and explicit cash, reserve, quality, and exposure gates.

The analysis separates two audit purposes. A report-independent payment lottery
determines eligibility for a match bonus, while a risk-dependent decision
lottery determines whether the trusted audit is observed before the final
decision. Under neutral reviewers, the separation produces an exact effort
threshold and a nonempty conditional feasibility region. With external utility
`b_i` for release, each reviewer’s utility is affine in `b_i`. Exact Fraction
calculation gives local All-H01 best-response intervals, but exhaustive
interval enumeration of all declared pure stationary equilibria finds a
smaller global-quality interval. For the certified selective mechanism, at
`b=1/10` All-H01 remains strict while three strict bad equilibria coexist and
violate the false-approval gate. The result distinguishes local truthful
stability from a guarantee over all equilibria.

The paper makes scoped finite claims. It does not claim a universal
impossibility theorem, empirical audit accuracy, mixed-equilibrium robustness,
Sybil resistance, or production readiness. A focused prior-art audit finds
close work on costly verification, limited spot checking, effort incentives,
decision-interested experts, and peer prediction; priority for the exact CEAV
construction remains unestablished.

**Keywords:** escrow verification, costly information, strategic reporting,
spot checking, decision quality, pure equilibria, external utility, exact
finite analysis

## 1. Introduction

An escrow release decision is a small decision problem with a large downside.
A reviewer may observe a noisy public signal, spend effort to acquire a private
signal, report a binary label, and influence whether funds are released. The
system may also buy an independent audit. That audit has two distinct jobs:
it can reward a reviewer whose report matches a trusted signal, and it can
improve the final release decision. Treating these jobs as one event creates a
tempting but fragile design: select a reviewer for an audit because of the
report, then pay the reviewer when the audit agrees with the report.

The first question in this project is therefore structural. Can payment
eligibility be separated from decision verification while preserving effort
incentives and an explicit budget? The second question is strategic. Even if
the truthful profile is a strict best response, do other equilibria satisfy the
same quality gates when reviewers care about release itself?

The CEAV-M1 study answers both questions in a deliberately narrow model. It
freezes the signals, costs, calibration tables, action class, and gates. The
positive result is conditional: a report-independent payment lottery can make
costly information worthwhile at a neutral reviewer. The negative result is
also conditional but exact: a modest positive external release preference
creates bad pure equilibria before it destroys the truthful profile’s local
best-response property.

The contributions are five scoped observations.

1. A report-contingent audit paired with an audit-contingent match reward can
   make a dissenting report privately profitable. This is a diagnostic lemma,
   not an impossibility theorem for all report-sensitive mechanisms.
2. A branch with no marginal reporting payoff admits constant, uninformative
   Low equilibria. Uninformative reporting and bad final decisions are separate
   claims and require separate witnesses.
3. Separating a report-independent payment lottery from a risk-dependent
   decision lottery yields an exact neutral effort condition and a conditional
   cash/exposure region.
4. Under external release utility, the truthful profile has an exact local
   affine boundary.
5. Exact all-profile interval enumeration reveals a smaller boundary for
   global pure-equilibrium quality. Local truthful stability does not imply
   that every equilibrium is acceptable.

The analysis is a research prototype. The synthetic signal accuracies are not
measurements, the trusted audit is not an empirical service, and the parameter
`b_i` is an analysis assumption rather than something enforced by identity,
payment, or audit rules.

## 2. Related work and novelty boundary

The model sits at the intersection of several established literatures.

Costly verification mechanisms study how a principal can check strategically
reported information. Ben-Porath, Dekel, and Lipman’s favored-agent mechanism
uses costly verification in an allocation problem without monetary transfers
([AER record](https://www.aeaweb.org/articles?id=10.1257/aer.104.12.3779)).
Erlanson and Kleiner study costly verification in binary collective decisions
with imperfect checks ([Theoretical Economics](https://econtheory.org/ojs/index.php/te/article/viewArticle/3101)).
These results establish that verification and allocation must be designed
together, but their private-type, no-transfer, and verification technologies
are different from a common hidden escrow truth with noisy signals and a
match bonus.

Peer prediction and limited ground-truth access provide close precedent for
costly evaluations and spot checks. Gao, Wright, and Leyton-Brown analyze
low-cost signals, trusted noisy evaluations, and universal-mechanism limits
([accepted manuscript](https://dspacemainprd01.lib.uwaterloo.ca/server/api/core/bitstreams/2cf2eab2-324c-402f-98eb-ee05f2a446f4/content)).
Their scores and objective differ from the CEAV binary-match reward and their
results do not price an escrow system’s cash, reserve, and union audit charge.
Zarkoob, Fu, and Leyton-Brown give report-sensitive incentive-compatible
checks under their own conditions ([AAMAS paper](https://www.ifaamas.org/Proceedings/aamas2020/pdfs/p1593.pdf)).
That work is direct prior art against presenting report-sensitive checking as
new by itself.

Liu and Chen study reward levels for costly effort across repeated tasks
([AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/10619/10478)); Chen,
Wu, Wu, and Yang study scoring-rule design for strategic information
acquisition ([PMLR](https://proceedings.mlr.press/v202/chen23ah.html)).
Boutilier studies decision-interested experts and uncertain utility
([AAMAS paper](https://www.cs.toronto.edu/~cebly/Papers/Boutilier_aamas12.pdf)).
These sources motivate the effort, scoring, and external-interest components;
they do not establish the exact CEAV fractions or its gate boundary.

The focused novelty audit is recorded in
[`CEAV_M1_NOVELTY_AUDIT_T3_T5.md`](CEAV_M1_NOVELTY_AUDIT_T3_T5.md). Its safe
positioning is that CEAV-M1 is a finite, reproducible case study of how a
separated payment/decision audit interacts with a specified reviewer game.
Priority for the exact architecture, the cash-aware union accounting, and the
global-quality boundary has not been established. The paper therefore uses
“we show in this frozen model” rather than “we are the first to show”
throughout.

## 3. Model

### 3.1 Hidden truth and signals

The milestone truth is `Y in {0,1}` with prior `P(Y=1)=1/2`. A public signal
`Z` has accuracy `7/10`. Each of three Judges can buy a private binary signal
`X_i` with accuracy `4/5`. A trusted audit `T` has accuracy `9/10`. Conditional
on `Y`, the signals are independent. These are synthetic likelihoods used to
make every probability rational and reproducible.

The public branch is `Z=z`. Each Judge chooses a branch-local action from

```text
A = {L0, L1, H00, H01, H10, H11}.
```

`L0` and `L1` report a constant without buying `X_i`. High actions buy `X_i`
at cost `c=1/20`; `H01` reports the observed signal, `H10` reverses it, and
`H00/H11` buy effort but ignore the signal. The action is chosen separately in
each public branch, so a stationary strategy is a pair of branch actions.

### 3.2 Frozen decision rule

The calibration table is computed under H01 peers and then frozen for every
unilateral deviation. With false approval cost `C_FA=2` and false rejection
cost `C_FR=1`, release is chosen when posterior odds for `Y=1` are at least
two. The no-audit table `g0` and trusted-audit table `g1` are:

| `Z` | report sum | `g0` | `g1(T=0)` | `g1(T=1)` |
|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 0 |
| 0 | 1 | 0 | 0 | 0 |
| 0 | 2 | 0 | 0 | 1 |
| 0 | 3 | 1 | 1 | 1 |
| 1 | 0 | 0 | 0 | 0 |
| 1 | 1 | 0 | 0 | 1 |
| 1 | 2 | 1 | 0 | 1 |
| 1 | 3 | 1 | 1 | 1 |

The table is an implementation contract, not a recalibrated estimator. This
choice is essential: recalibrating after a deviation would define a different
game and could hide the strategic effect being measured.

### 3.3 Separated audit architecture

Reports lock before either hidden lottery is revealed. The payment lottery is

```text
A_pay ~ Bernoulli(a),       a=2/5,
```

and is independent of signals, reports, peers, and future `T`. The decision
lottery is independent of `A_pay` and is either:

```text
Selective: d(Z,r)=1/6 only on S={Z=0 and sum(r)=2}, else 0;
Uniform:   d(Z,r)=19/1250 everywhere.
```

If either lottery fires, one common `T` is observed and one audit cost
`kappa=1/4` is charged. The union probability is

```text
e(Z,r) = a + (1-a)d(Z,r).
```

Only payment-audit eligibility earns the match reward:

```text
R_i = f + mu*A_pay*1{r_i=T},   mu=2, f=0.
```

Judge utility is

```text
U_i = E[R_i] - effort_cost_i + b_i*P(D_final=1).
```

The coefficient `b_i` is measured in the same utility units as reward. It is
the utility difference between certain release and certain rejection; it is
not an audit probability, a payout fraction, or a measured personality trait.

### 3.4 Gates and evaluation metrics

The frozen gates are

```text
FA <= 1/5, FR <= 1/4, wrong payout <= 3/20,
expected cash <= 4, union exposure <= 1/2, reward reserve <= 6.
```

Metrics use the strategy-induced distribution. `FA=P(D=1|Y=0)` and
`FR=P(D=0|Y=1)`. Wrong payout equals the false-approval probability at unit
payout value. Decision loss is `2*FA+FR`, matching the declared asymmetric
costs. Reward reserve is the cap `3*mu=6`, not expected cash.

## 4. Mechanism-separation propositions

### Proposition 1: payment factorization and effort

Assume `A_pay` is independent of all information used to choose the report,
the report is locked before the lottery is revealed, and no decision utility
enters the Judge’s objective. For any information set `I` and report `r`
chosen from `I`,

```text
E[R_i | I,r] = f + mu*a*P(T=r | I).
```

The optimal Low report obtains `M_L=max_r P(T=r|z)`. The optimal High action
obtains `M_H=sum_x P(x|z) max_r P(T=r|z,x)`. High effort is strictly useful
exactly when

```text
mu*a*(M_H-M_L) > c.
```

**Proof.** Independence factors `A_pay` out of the conditional transfer.
Optimizing reports after Low and after each observed `X` gives `M_L` and
`M_H`. High can imitate the best Low report, so `M_H>=M_L`; subtracting effort
cost gives the displayed condition. The decision lottery `d` and peer reports
do not enter neutral payment utility.

At the frozen signals, exact enumeration gives `M_L=33/50`, `M_H=37/50`, and
`M_H-M_L=2/25`. Hence the certified gap is
`2*(2/5)*(2/25)-1/20=7/500>0`.

This does not make binary match a strictly proper probability score. It also
does not prove truthful reporting when `b_i != 0`.

### Proposition 2: neutral conditional feasibility

For the frozen environment, neutral Judges, fixed tables, and
`5/16<a<1/2`, `0<t<=(1/2-a)/(1-a)`, the declared six-action game has unique
pure stationary equilibrium All-H01 and passes the original gates. Selective
decision verification has lower decision loss than uniform verification at
matched exposure and the same equilibrium report distribution.

This is an exact algebraic region, not a parameter search or policy optimum.
The strict effort boundary is necessary for the proof. At `a=5/16`, Low and
High tie and the all-Low witness has `FA=FR=3/10`; therefore weak effort
thresholds cannot be silently treated as robust feasibility.

### Proposition 3: local external-interest boundary

Fix H01 peers and the frozen tables. Each deviation has utility difference
`gamma+b_i*Delta s`. Intersecting all six-action inequalities in both branches
gives:

| Mechanism | Strict H01 interval for one Judge |
|---|---|
| Selective | `-70/633 < b_i < 175/1102` |
| Uniform | `-218750/2070709 < b_i < 218750/1365587` |

For Selective, the first negative deviation is `L0` in `Z=0` and the first
positive deviation is `L1` in `Z=1`. The same deviation identities hold for
Uniform. All-H01 is therefore a strict pure equilibrium when each coordinate
lies in its local interval. The conservative box `|b_i|<7/500` is smaller and
peer-profile-independent because release probability changes by at most one.

This proposition is local. It does not state that other equilibria do not
exist.

### Proposition 4: global pure-quality boundary

Consider stationary pure strategies, task-local unilateral deviations, and
the five declared preference vectors

```text
000, 100, 010, 001, 111.
```

For every branch profile, all 18 deviation inequalities are affine in the
scalar `b`. Their exact intersection is a closed interval or empty. Combining
the two branches yields every full pure equilibrium for every real `b` in
each declared scenario.

The maximal all-pure gate-safe component containing zero is:

| Scenario | Selective | Uniform |
|---|---|---|
| Neutral `000` | all real `b` | all real `b` |
| One biased Judge | `(-70/633,+infinity)` | `(-218750/2070709,+infinity)` |
| Symmetric `111` | `(-70/633,175/1922)` | `(-218750/2070709,109375/1189451)` |

The endpoints are open because weak bad equilibria appear there. In the
interior of the symmetric component All-H01 is the unique pure stationary
equilibrium. At `b=1/10`, Selective has exactly four pure equilibria: All-H01
and three permutations of the branch witness

```text
Z=0: H01,H01,H01
Z=1: L1,L1,H01.
```

Each bad witness is strict at `b=1/10` and has `FA=1391/6250>1/5`.
All-H01 is still strict there. The mechanism therefore has local truthful
stability but fails the all-equilibrium quality requirement.

## 5. Earlier failure mechanisms and negative evidence

The separated design was motivated by two earlier failure modes.

First, if the audit probability depends on a report and the match reward is
paid only when that audit occurs, a report can seek audit eligibility. In the
simple two-report comparison, a deviation from `r_0` to `r_1` is profitable
when

```text
q_1*P(T=r_1|z) > q_0*P(T=r_0|z).
```

The condition is exact under the stated independence and equal-cost
assumptions. It does not say every report-sensitive audit fails; compensating
transfers, penalties, or other scores can change the comparison.

Second, if a reachable branch has no audit, no marginal report payoff, no
external decision preference, and positive effort cost, every all-Low profile
is a branch equilibrium and every High action is strictly worse. The branch
report is constant and uninformative. A bad final decision requires a separate
decision witness; uninformative reporting alone is not enough.

These negative results are deliberately modest. They diagnose channels in
the frozen game and preserve counterexamples rather than turning them into
universal impossibility claims.

## 6. Exact strategic analysis

### 6.1 Enumeration method

The equilibrium analysis uses exact rational arithmetic. There are 216 ordered
branch profiles (`6^3`) and 18 unilateral action comparisons per branch
profile. For each preference scenario and mechanism, branch intervals are
constructed from all inequalities, including exact ties. Full equilibria are
the overlapping products of the two branch intervals. Arrangement endpoints
are retained as point cells; open cells use an exact rational representative.

The independent completeness replay covers:

| Quantity | Count |
|---|---:|
| branch candidates | 4,320 |
| full profiles per scenario | 46,656 |
| mechanisms × five scenarios | 466,560 full profiles |
| independent audit checks | 5,590 |

The replay also checks branch metrics, gates, cell equilibrium sets, worst
metric witnesses, and All-H01 status. Nine mutation probes were detected in
the frozen certificate. No Monte Carlo sample or floating-point grid supports
the reported boundary.

### 6.2 Fair baseline

Uniform uses the same payment lottery, reward coefficient, signal law, audit
distribution, reserve, tables, and gates. At neutral H01 equilibrium, both
mechanisms have exposure `2557/6250`, expected cash `46957/25000`, and reserve
six. Selective has lower decision loss because it concentrates decision audits
on the risk class `S`.

Once external interests create different equilibrium report distributions,
the comparison must be made at those equilibria. Equal neutral exposure does
not imply equal exposure or cash at a bad equilibrium. For example, the
negative Selective witness has exposure `411/1000` and cash `7387/4000`, while
the corresponding Uniform witness has exposure `2557/6250` and cash
`46157/25000`. These are separate strategic outcomes, not a contradiction in
the neutral baseline.

### 6.3 Interpretation

The first strategic failure is not a payment manipulation by changing audit
eligibility. Payment eligibility is independent of reports in this design.
The failure is a decision-interest channel: a Judge can reduce effort and
change the final release probability while accepting a small reward loss.
That distinction matters for mechanism diagnosis. Removing report-contingent
payment eligibility addresses one channel but does not make external release
preferences disappear.

## 7. Experimental and computational evaluation

This paper’s “experiment” is a reproducible finite calculation, not a field
study. The exact evidence package contains the frozen configuration, source
hashes, a certificate, interval report, independent Fraction oracle, mutation
probes, and replay logs. The main certificate hash is
`fde3ad4745b37e270469aaec2692a51c83cbcf5db7fcb0a16938296a6e25b7d5`.

The proof review is recorded in
[`CEAV_M1_INDEPENDENT_PROOF_REVIEW_T3_T5.md`](CEAV_M1_INDEPENDENT_PROOF_REVIEW_T3_T5.md)
and runs with:

```text
python -X utf8 -m verification.independent_t3_t5_review
python -X utf8 -m unittest tests.test_dual_boundary -v
```

The first command independently reproduces the T3 effort gap, the four T4
binding fractions, the T5 all-real interval coverage, and the four-equilibrium
Selective witness at `b=1/10`. The focused test command runs ten tests and
passes. Historical V3–V6 artifacts are preserved; the current work does not
rewrite their results or parameters.

No claim in this section treats the synthetic `90%` audit accuracy as an
empirical measurement. The companion
[`CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md`](CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md)
specifies how a future independently verified physical milestone study could
measure ground truth, evidence, audit sensitivity/specificity, reviewer effort,
cost, latency, and disagreement. That study has not been run.

## 8. Threats, assumptions, and trust boundaries

The model assumes that `T` is a trusted noisy signal with known accuracy and
that its conditional relationship with `Y` is stable. In practice, the audit
could be captured, correlated with reviewer evidence, manipulated by a
creator, delayed beyond settlement, or unavailable for some milestones.

Reviewer independence is also an assumption. Three identities are not three
independent information sources if they share evidence, coordinate, or are
Sybil accounts. The present finite game has no identity mechanism, stake,
collusion model, coalition deviation, or participation constraint.

The parameter `b_i` is restricted only by the declared analytical scenario.
The mechanism does not enforce a bound on outside release utility. A social or
contractual restriction on reviewer incentives would be a separate trust
assumption, not a result of the payment lottery.

The calibration table is frozen. That is appropriate for a strategic test of
a published rule, but it means the model does not estimate calibration under
distribution shift. Similarly, the finite action class excludes richer
randomized, history-dependent, collusive, or adversarial strategies.

Finally, the cash gate is a model-level expected-cost gate. It is not a proof
that a live escrow has adequate liquidity under timing risk, failed audits,
currency changes, or settlement disputes.

## 9. Limitations and open questions

The exact results leave several questions open.

- Mixed, correlated, coalition-proof, and claim-level equilibria are not
  analyzed.
- The exact boundary for arbitrary heterogeneous `(b_1,b_2,b_3)` is not
  computed; the conservative `|b_i|<7/500` box is the available global
  sufficient condition.
- Synthetic accuracies and costs require empirical calibration before any
  economic interpretation.
- Audit independence, reviewer independence, creator evidence quality,
  participation, latency, and dispute resolution require field protocols.
- Literature priority for the combined architecture and boundary is not
  established by a focused source audit.
- The model studies a fixed terminal decision table rather than an adaptive
  mechanism that recalibrates online.

These are boundaries of the paper’s claims, not invitations to silently alter
the current mechanism or historical study. A future paper may address them
only with a preregistered scope and a new evidence artifact.

## 10. Conclusion

Separating payment-audit eligibility from decision-audit selection is useful in
the frozen CEAV model. It removes the direct audit-seeking payment channel and
creates a strict neutral effort margin at the certified point. That positive
result is conditional on signal provenance, lottery timing, known calibration,
and neutral utility.

The same separation does not solve every strategic problem. External release
utility enters final decisions directly. Exact local bounds show where All-H01
remains a strict best response; exact pure-equilibrium enumeration shows that
bad equilibria can appear earlier. At `b=1/10`, the selective mechanism is the
clearest witness: truthful behavior remains locally strict, yet three strict
bad equilibria violate the false-approval gate.

The scientific contribution FundTogether can defend at this stage is a
reproducible conditional analysis of mechanism separation and the difference
between local truthful stability and global pure-equilibrium quality. The
paper is ready for theory-draft circulation after independent mathematical
review, but it is not ready for a novelty claim, empirical claim, or
production deployment.

## References

The following references are the primary sources used for positioning and are
also listed in the project’s novelty audit and V6 source note.

1. Ben-Porath, E., Dekel, E., and Lipman, B. L. “Optimal Allocation with
   Costly Verification.” *American Economic Review* 104(12), 2014.
   [Publisher](https://www.aeaweb.org/articles?id=10.1257/aer.104.12.3779)
2. Boutilier, C. “On the Decision-Making Abilities of Experts.” *AAMAS*,
   2012. [Paper](https://www.cs.toronto.edu/~cebly/Papers/Boutilier_aamas12.pdf)
3. Chen, Y., Wu, H., Wu, X., and Yang, J. “Scoring Rules for Strategic
   Information Acquisition.” *PMLR* 2023.
   [Paper](https://proceedings.mlr.press/v202/chen23ah.html)
4. Erlanson, A. and Kleiner, A. “Costly Verification in Collective
   Decisions.” *Theoretical Economics* 15, 2020.
   [Paper](https://econtheory.org/ojs/index.php/te/article/viewArticle/3101)
5. Gao, X. A., Wright, J. R., and Leyton-Brown, K. “Incentivizing Evaluation
   with Peer Prediction and Limited Access to Ground Truth.” *Artificial
   Intelligence* 275, 2019.
   [Manuscript](https://dspacemainprd01.lib.uwaterloo.ca/server/api/core/bitstreams/2cf2eab2-324c-402f-98eb-ee05f2a446f4/content)
6. Liu, Y. and Chen, Y. “A Bandit Approach to Bayesian Incentive Compatible
   Mechanism Design.” *AAAI*, 2017.
   [Paper](https://ojs.aaai.org/index.php/AAAI/article/view/10619/10478)
7. Zarkoob, H., Fu, H., and Leyton-Brown, K. “Report-Sensitive Spot
   Checking.” *AAMAS*, 2020.
   [Paper](https://www.ifaamas.org/Proceedings/aamas2020/pdfs/p1593.pdf)
