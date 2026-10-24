# CEAV-M1 — Research synthesis & next-mechanism feasibility memo

Date: 2026-10-24. Baseline reviewed: `6fb0f4367187cc9eeefb180d4336f237275e38c5`.
Scope: synthesis, proofs, exact checks of named examples. No V7, new policy
grid, production engine, API, UI, branch merge or historical-result changes.

Package scope note: this copy preserves the historical V3--V6 synthesis text for
context. Its older V3--V5 links point to the original repository history and are
not required for the self-contained central T3--T5/dual-boundary replay. The
central frozen certificates and all replay code used by this package are linked
from `../frozen-boundary/`, `../verification/`, and `../configs/`.

**Recommendation: GO for a bounded theoretical investigation of separated
payment/decision verification; no authorization or need here to implement a
new version.** The binary-match architecture has a nonempty analytic region
under the original F51-02 signals, B=6, cash<=4 and quality gates. Its guarantee
is conditional on neutral reviewers, the finite strategy class and trusted T.
Historical V6 remains NO-GO for its declared policies; this does not revise it.

Status: mathematical derivations and named-instance exact arithmetic verified;
not an implemented mechanism/version. The initial paper draft was saved before
the new checker existed; final execution evidence is identified in §8.

## 1. Reading rules and common definitions

Specs define games; artifact certificates record executed evidence. A green
implementation test, a `robust` flag with permissive diagnostic thresholds,
a good candidate and a quality-guaranteed equilibrium are different facts.
The following table distinguishes them rather than treating V3–V6 as a single
unchanged experiment. Values are synthetic assumptions, not measured outcomes.

Quality gates remain FA<=1/5, FR<=1/4, wrong payout value<=3/20, expected cash<=4.
FA=P(D=1|Y=0), FR=P(D=0|Y=1); wrong payout value=V*P(Y=0,D=1), V=1.
V6 loss weights C_FA=2, C_FR=1 remain fixed; wrong payout is not added twice.
Target weights are P(Z), including (2/5,3/5) for V3-HET, not balanced batch weights.

## 2. Consolidated verified evidence table

Abbreviations: H=H01; Z-copy means (L0,L0,L0) at z=0 and (L1,L1,L1) at z=1.
All equilibrium statements are restricted to the declared strategy class.

| Mechanism / assumptions and evidence | Confirmed positive | Negative result / exact witness | Failure type | Proof versus finite evidence | Still open |
|---|---|---|---|---|---|
| **V3 anchor hybrid**, RBTS+independent noisy audit after majority decision; V3-HET, B=6. Historical sweep `V3_PARAMETER_SWEEP_REPORT.md`, `results/v3-closeout-study-r2/study.json` (context only; outside this package). | At lambda=0, mu=19/10, q=1/2: unique pure profile z0=(H,H,L0), z1=(H,H,L1); accuracy=1813/2000, FA=51/500, FR=17/200, wrong payout=51/1000. Weak Judge C need not buy effort. | Baseline lambda=1/2, mu=4/5,q=1/5 has Z-copy NE: FA=2/5, wrong payout=1/5. With q=2/5 improvement disappears; peer weights 1/20 and 1/10 in closeout sensitivity have no pure NE. | effort; equilibrium quality; equilibrium existence | Binary anchor-only entry bound q>25/57 is algebraic for fixed inputs. Listed hybrid allocations and perturbations are finite instances; no-pure is not success. | Real audit reliability/cost, wider uncertainty, mixed/coalition behavior; not general anchor superiority. |
| **V3.1 robustness**, unchanged V3 game, 6 policies × 18 uncertainty scenarios, B=6. `results/v31-robustness-study-release-02/robustness.json`. | Anchor-q50 passes 3/18 scenarios; q60 5/18; q80 6/18. Failures/witnesses retained. | No robust policy. Anchor-q50 point 30: pi=7/10,T quality=4/5,cost multiplier=1; z0=(H,H,H), z1=(L1,L1,L1); FA=2237/5000. Point 18 has FR=38/125. | equilibrium quality; budget; effort | Exhaustive pure analysis at 108 fixed points; assumption grid is not a confidence interval or a continuous impossibility result. | Uncomputed policies/environments and actual estimation uncertainty. |
| **V3.2 report-sensitive audit**, separate per-Judge audit probabilities q(report), no correction of majority. `results/v32-report-sensitive-final-02/report_sensitive.json`. | Symmetric q0=q1=1/2 reproduces H,H,Z-copy and accuracy=1813/2000; report-dependent incentives are computed exactly. | Point 1, q0=1/4,q1=3/4: z0=(H,H,H), z1=(L1,L1,L1), FA=2237/5000, wrong payout=2237/10000. Point 2 reversed q has FR=23/50. | reporting bias; equilibrium quality | Three exact instances, not a robustness proof. Artifact `robust=True` uses diagnostic gates FA=FR=wrong=1,cash=100; it does **not** pass standard quality gates. | A beneficial report-sensitive policy under matched strict gates. Per-Judge audit cost is not V6's one-claim audit cost. |
| **V3.3 IPW**, reward mu*A_i*match/q(report), per-Judge audits. `results/v33-ipw-full-20261024T052707/ipw_public.json`, final local acceptance in `results/v33-closeout-final-20261024T084030/report.md`. | E[anchor reward|I,r]=mu*P(T=r|I), removing the multiplicative selection factor. Local implementation closeout is verified, not economic success. | Each policy passes 0/18. Symmetric policy point 4: cash=257829/50000>4, FR=38/125. Cap is 3f+6lambda+3mu/q_min. | budget; equilibrium quality | Expectation cancellation/cap formulas are proved. Negative study is finite and used **B=24**, not B=6; V3.2 same-budget rerun is explicitly required. | Whether a different bounded payment design is useful; no matched-budget dominance claim. |
| **V4 conditional excess agreement**, same-stratum cross-task centering, no audit. Historical `CEAV_M1_V4_CONDITIONAL_SPEC.md` §§8–9 and `results/v4-research-closeout-20261023T2357325229450Z/` (context only; outside this package). | Copy-Z centered score=0; informative all-H NE exists in V4-F01, accuracy=112/125. | Every all-Low profile is an NE; all-PASS FA=1, all-FAIL FR=1. All-H10 inversion is also NE, accuracy=13/125. | effort; reporting orientation; equilibrium quality | Statewise cancellation and label symmetry are mathematical propositions for this payoff. Numeric certificates verify named instances, not all conditional mechanisms. | Other scores/information structures; equilibrium selection is not solved by existence of all-H. |
| **V4.1 conditional+uniform audit**, B=6, fixed finite M×Q×L grid. `results/v4-1-minimal-screening-curated-20261024T011500/report.md`. | Robust audit-only and hybrid policies exist on this grid; conditional peer reward can support informative profiles. | No incremental hybrid strict dominance under the declared multi-metric rule. V3-HET audit frontier min cash=381/160 versus hybrid=14551/6000; lower-q hybrid trades cost/quality. | decision quality/cost trade-off; budget | No dominance is grid-only. All-Low entry gain mu*q*delta-c and fallback cash bound are algebraic. | Global frontier, changed audit prices; not a universal impossibility of peer assistance. |
| **V4.1 audit-cost sensitivity**, fixed V3-HET pair only. `results/v4-1-audit-cost-sensitivity-20261024T020000/report.md`. | Hybrid becomes cheaper than this audit-only pair for kappa>527/1500; remains within its cash gate up to 9449/3000. | At kappa=1/4, audit-only cash=203/80 versus hybrid=15301/6000; hybrid is dearer. Quality trade-off remains. | budget/economic trade-off | Linear cash crossover is exact for the pinned pair, not re-optimization or global frontier dominance. | Best policies after changing cost and empirical kappa. |
| **V5 shifted incremental Brier**, scores forecasts of noisy T, cap 3f+6mu<=6. Historical `CEAV_M1_V5_FEASIBILITY.md` and `results/v5-feasibility-20261024T012908/` (context only; outside this package). | Strict propriety for P(T=1|I) when mu*q>0; private score value is posterior variance. HET shifted A,z1 has positive cap gain 1823/112500, a partial branch result. | F51-01 Delta_T=3249/1106875 and F51-02 Delta_T=15876/368125; each is <cost=1/20 at mu_max=1. No strict effort on either. | effort; budget | Propriety, variance/noise attenuation and cap-bound inequalities are algebraic, exact for the stated environment. | Other proper scores/rewards; propriety alone does not buy information or ensure good decisions. |
| **V5.1 Direct Brier**, cap 3f+3mu<=6; audit does not correct decision. `results/v5-1-quality-certificates-20261024T084411/`. | F51-02 Direct (mu=2,q=3/5) has all-H and accuracy=112/125. | Binary audit-only (mu=2,q=1/2) has identical quality but lower cash: 111/50 versus 434007/147250. V3-HET B,z0 needs s>=155/98; cheapest threshold cash=14998033/3675000>4. | budget; economic dominance; decision quality | Exact two-fixture certificates plus a scoped Direct-Brier cash bound. NO-GO for Direct-Brier Phase 2 remains in force. | Other scoring rules; not an impossibility theorem for binary match or all probabilistic scoring. |
| **V6 RAVE decision layer**, fixed H01 calibration, noisy pre-settlement audit, C_FA=2,C_FR=1,B=6,kappa=1/4. `results/v6-rave-phase1-20261024T021148403371Z/`. | F51-02 Q1-zero vs matched uniform, exposure=12/25: loss 219/3125 versus 17151/156250; cash 597/625 versus 741/625. This is exogenous-report optimization. | All-H01 is not NE for any of the four discovered candidates. Copy-Z contrarian earns 17/50 by inducing audit in F51-02. | reporting; effort; audit exposure | Nonnegative VOI theorem assumes fixed correctly calibrated reports. Finite comparisons do not transfer this to strategic behavior. | Which incentive-independent audit allocation could retain benefits; calibration and external interests. |
| **V6 strategic closeout**, same policies/inputs/gates. `results/v6-closeout-20261024T021405861852Z/negative-certificates/certificate.json`. | Exact counterexamples distinguish discovery from strategic acceptance; no large equilibrium search needed to refute a universal gate. | F51-01 Q1-zero: (L0,L0,L1)/(L1,L1,L0), exposure=1. Q2-z1: all L1, FA=1. F51-02 Q1-zero: (L0,L1,H)/(L0,L1,H), exposure=1. Q2-z0: (H,H,H)/(L0,L0,L0), FR=2321/3125. All four max regret=0. | equilibrium quality; audit exposure | Four 36-deviation certificates. Last two witnesses are explicitly post-discovery. Sufficient to refute all-NE gates for these candidates; not an exhaustive equilibrium count. | Other policy/payment architectures. No universal RAVE impossibility or production conclusion. |

**Synthesis:** V3 shows useful asymmetric effort can be incentive-compatible;
V3.1 prevents overstating its robustness. V4 shows eliminating a public-signal
score is not eliminating bad equilibria. V5 separates truthfulness of a forecast
from willingness to acquire information. V6 separates decision information
value from the incentives created by acquiring that information selectively.

## 3. Two structural propositions for the V6 failures

### P1 — Positive audit-contingent bonus can reward audit seeking

Assume one public branch z has positive mass; peers use Low and report z;
f is constant, mu>0, b_i=0, no peer score/other report-dependent transfers;
q(unanimous)=0, q(disagreement)=d>0. Reports lock before selection/T. T has
unchanged conditional distribution with P(T=1-z|z)>0. Focal can choose either
Low report without effort cost.

Staying unanimous has utility f. Deviating to Low report 1-z has utility
f+mu*d*P(T=1-z|z). The gain is strictly positive. For F51-02, mu=d=1,
P(T=1-z|z)=17/50, exactly the historical deviation.

This is an **existence proposition under these assumptions**, not a claim
that every report-dependent rule permits profitable audit seeking. Fixed
audit probability, zero bonus, penalties, other transfers or decision interests
can change the comparison. A discrepancy with noisy T is not proof of lying.

### P2 — A genuinely unrewarded branch permits uninformative best responses

Assume at reachable z: audit probability is zero **for every report vector
reachable by a unilateral deviation**, rewards are constant f_i, b_i=0,
effort costs c_i>0, no other report-dependent payoff or cross-branch constraints.
Then every Low report has utility f_i; every High action has f_i-c_i.
All combinations of Low reports are branch Nash equilibria, with reporting
indifference. The f_i=0 case is the requested zero-reward case; fixed fees do
not fix the absence of marginal incentives.

If other branches admit equilibrium and payoff factorizes, these branch
profiles can be combined into full pure equilibria. A **bad** equilibrium
additionally requires the published decision rule to make poor decisions on
one such report profile. It is not automatic: an accurate public-only rule
could ignore them. Historical F51-01/Q2-z1 all-L1 gives a concrete bad NE:
z0 has zero audits, z1 prefers L1; fixed H01-calibrated decisions release always,
so FA=1. F51-02/Q2-z0's (H,H,H)/(L0,L0,L0) has FR=2321/3125.

Crucial limitation: q=0 **only on the current unanimous profile** does not
satisfy P2. In Q1-zero a dissent can trigger audit; P1 explains why copy-Z
is then not an equilibrium. Do not conflate these two mechanisms.

## 4. Paper architecture: separate payment eligibility from decision audit

This is an unversioned mathematical hypothesis, not a new implemented model.
Retain binary-match rewards initially; no peer score, IPW or new scoring rule.

```text
Announce signals, a, d(z,r), f, mu, fixed g0/g1 and budgets
 -> Judge sees Z, chooses L/H, receives X only if H, locks binary report
 -> draw A_pay~Bernoulli(a), independent of reports/signals and hidden until lock
 -> draw A_dec~Bernoulli(d(Z,r)), using only locked observables
 -> if A_pay OR A_dec: obtain one common noisy T before settlement
 -> use fixed g0/g1 to release/reject
 -> pay f+mu*1(A_pay)*1(report=T); no bonus on decision-only audits
```

T quality must be the same on both routes and independent of Z/X given Y.
No report-selected auditor, report-dependent payment pool, repeated audit,
eligibility revealed before effort, or recalibration during deviation.
Using T from a pay audit for decision correction incurs no second audit charge.

Main analysis uses coins conditionally independent given h=(Z,r). For general
coupling let j(h)=P(A_pay=1,A_dec=1|h); then

```text
e(h)=P(A_pay OR A_dec | h)=a+d(h)-j(h)
max(a,d(h)) <= e(h) <= min(1,a+d(h))
independent coins: e(h)=a+(1-a)*d(h)
q_bar=E_actual[e(Z,R)]
```

Different coupling is a separate implementation choice, not silently another
budget model. A shared T is paid/acquired once. Expected exposure is evaluated
under actual strategies; it is not frozen at a truthful distribution.

### P3 — Neutral payment incentives factor independently of decision selectivity

For information I and a chosen report r, independence gives

```text
E[R_i | I,r] = f + mu*a*P(T=r | I).
```

d, peers' reports and final decision do not enter this expression at b_i=0.
Changing a report cannot increase payment eligibility or cause a decision-only
audit to earn a bonus. It **can** change the expected match payment: the best
report is a modal label of T, not an arbitrary unscored truthful statement.

With symmetric T noise, P(T=1|I)=1/10+(4/5)P(Y=1|I), so modal T and modal Y
coincide at threshold 1/2. Raw report X is optimal only where X flips the
posterior mode. F51-02 has this property; F51-01 does not. If a*mu=0, reports
are indifferent again. Proper Brier scores elicit P(T=1|I), with their separate
historical effort/cash bounds; do not call binary match strictly proper.

Let M_L(i,z)=max_r P(T=r|z),
M_H(i,z)=sum_x P(x|z)max_r P(T=r|z,x), delta=M_H-M_L, s=mu*a.
Best H beats best L iff s*delta>c_i; equality retains both efforts.
Thus a>c_i/(mu*delta) when delta>0; delta=0,c_i>0 rules out useful High
for **this reward**, independently of decision-audit intensity.

### External release interests remain a strategic channel

With U_i=E[R_i]+b_i*P(D_final=1)-cost, a deviation changes utility by
mu*a*Delta(match)-Delta(cost)+b_i*Delta(P(release)). Reports can manipulate
decision-audit selection or g0/g1 to affect release, even though eligibility
is independent. No bribery/collusion claim follows from b=0.

If the neutral chosen action has a uniform strict gap gamma_i(z)>0 against
all five other actions, |b_i|<gamma_i(z) is sufficient to preserve it against
all peers, since |Delta(P(release)|<=1. This conservative bound is a proof,
not an estimate of real external interests. Fixed policy is essential.

## 5. Reserve, cash and historical feasibility bounds

```text
Reward reserve: 3f+3mu <= B=6; mu_max=(6-3f)/3
Expected reviewer payout: 3f+s*sum_i P_actual(r_i=T)
Expected cash: 3f+s*sum_i P_actual(r_i=T)+kappa*q_bar+OperatingCost
Audit exposure: q_bar>=a
```

Do not multiply reserve by a, add effort cost to cash again, or charge three
audits because three Judges use T. If any s is needed for useful effort,
a>=s/mu_max is a necessary exposure floor. More decision-only audits cannot
reduce that floor or improve a Judge's reward signal after reports are locked.

| Fixture / reward | Exact entry facts | What follows, and what does not |
|---|---|---|
| F51-01 binary match | delta=0 all Judges/branches; M_L=M_H=43/50. | No paid private effort for this reward at any valid a,mu; strong public Z may already support good decisions, so no mechanism-wide failure follows. |
| F51-02 binary match | delta=2/25, c=1/20, so s>5/8. With f=0,mu_max=2, need a>5/16. | Nonempty below exposure 1/2; historical binary bounds do **not** close dual-purpose feasibility. Keeping V6's mu=1 and a<=1/2 would fail effort, but mu=1 was a prototype value, not a fixed signal or B constraint. |
| V3-HET binary match | A deltas (3/50,4/25), B (3/25,3/25), C (0,0). A/B informative in both branches require s>5/6; C optimally stays Low. | With f=1/10,mu_max=19/10, need a>25/57; still below 1/2. Historical positive asymmetric effort is relevant. At that profile sum_i match=111/50 and cash=3/10+(111/50)s+kappa*q_bar. No new HET decision/calibration certificate is claimed here. |
| V5 shifted Brier | F51-02 mu_max*Delta_T=15876/368125<1/20; F51-01 also fails. | Replacing q by a preserves this effort impossibility for the same shifted score/cap. Decision-only audits do not help. |
| Direct Brier F51-02 | Need s>73625/63504>1. With mu_max=2 and a<=q_bar<=1/2, s<=1. | Infeasible for informative effort with the retained exposure cap. This is a score-specific bound; it cannot rule out binary match. |
| Direct Brier V3-HET | B,z0 needs s>=155/98. Cheapest threshold cash already 14998033/3675000>4 at kappa=0. | The same reward game is still closed for B entry, even before adding nonnegative union-audit costs. With exposure<=1/2, s<=19/20 makes the entry bound fail even sooner. |

Main kappa remains V6's 1/4, not historical V3/V5's 0. These are synthetic
cost assumptions. No sensitivity changes to B, quality gates, prior, signal
qualities, effort costs, f or loss weights are used to obtain a positive region.

## 6. Constructive analytic region, before any policy-grid search

Use F51-02, f=0, mu=2 (the reserve boundary), neutral b=0, original independent
signals and six actions. Choose the named observable risk class
S={Z=0, exactly two reports are 1}. Its posterior is 12/19, conditional VOI
is 47/95, and its target mass is 57/625. Thus VOI exceeds the unchanged audit
cost kappa=1/4. Let d(h)=t on S and 0 otherwise. Define

```text
5/16 < a < 1/2,
0 < t <= (1/2-a)/(1-a).
```

Then mu*a*delta-c>0, and H01 uniquely maximizes each Judge's branch utility,
independently of peers. Its strictly correct report orientation follows from
the F51-02 posterior modes, not an assumption of cooperative reporting.
Therefore all-H01 is the unique pure equilibrium in this six-action class.
This is a dominance argument, not inference from a searched truthful profile.
The announced H01 calibration is consequently consistent at this neutral
equilibrium; it is never recalibrated in response to deviations.

For every report vector, e(h)<=1/2; endogenous reports cannot overshoot the
cap as they did in V6. At equilibrium P(S)=57/625, so
q_bar=a+(1-a)t*(57/625). Cash=(111/25)a+(1/4)q_bar<469/200<4.

Freeze the original F51-02 H01 Bayes table with loss threshold 2/3. Set
u=(1-a)t. Exact final error formulas in this region are

```text
FA = 23/625 - (24/3125)*a + (21/3125)*u,
FR = 137/625 - (429/3125)*a - (324/3125)*u.
```

Since a,u>=0 and u<=1/2, FA<=251/6250<1/5 and FR<=137/625<1/4.
Wrong payout=FA/2<=251/12500<3/20. These are conservative analytic bounds;
they establish quality throughout the region without a grid.

Let G=E[VOI]=477/6250. Against the uniform decision lottery with the same
a,mu and union exposure, the exact loss reduction is

```text
u*(57/625)*(47/95-G) > 0.
```

Payments and cash are identical at matched exposure. Uniform uses optimal
Bayes terminal rules too. Relative to using pay audits alone, the extra
decision audits also improve loss+cash by u*(57/625)*(47/95-1/4)>0; this
separately checks that their information value exceeds their operating cost.
This isolates allocation value; it does not prove
global cost optimality over a,mu. Both mechanisms can reduce expected payments
by approaching the strict effort boundary; at equality effort ties reappear.

### One named arithmetic witness, not a new grid

Take a=2/5,t=1/6,mu=2. Then e=1/2 on S and 2/5 elsewhere,
q_bar=2557/6250. Uniform decision coin d=19/1250 has the same union exposure.

| Metric | Selective decision lottery | Matched uniform decision lottery |
|---|---:|---:|
| Unique neutral pure equilibrium | all H01 | all H01 |
| Preliminary accuracy | 112/125 | 112/125 |
| Final FA | 43/1250 | 328691/9765625 |
| Final FR | 481/3125 | 3184297/19531250 |
| Wrong payout value | 43/2500 | 328691/19531250 |
| Expected decision loss | 348/3125 | 4499061/39062500 |
| Union audit exposure | 2557/6250 | 2557/6250 |
| Expected reviewer payout | 222/125 | 222/125 |
| Expected audit cost | 2557/25000 | 2557/25000 |
| Expected cash | 46957/25000 | 46957/25000 |
| Reward reserve | 6 | 6 |

Loss improves by 149061/39062500 at equal cash/exposure. Loss+cash improves
by 279/125000 relative to using pay audits alone. Strict effort gap is
7/500; |b_i|<7/500 is a sufficient conservative robustness condition in the
same finite class. It is not a claim for b=1/10 or arbitrary side payments.

The reward rule is algebraically V3 binary audit-only with q=a. Its useful
effort is not new; the question studied here is whether decision selectivity
can exploit already-incentivized reports while keeping the reward lottery
independent and reusing a single noisy audit. This closes neither empirical
calibration nor auditor provenance, participation, collusion, or deployment.

## 7. Decision and scientific contribution

**GO: a nonempty paper feasibility region exists for binary-match dual-purpose
verification under the fixed primary F51-02 environment.** No larger grid
was necessary to establish this. **NO-GO** for rescuing shifted/Direct Brier
under the bounds above, or treating the old V6 candidates as strategic successes.

FundTogether's defensible contribution should be a conditional theory and
reproducible evidence story: structural failure propositions, separation of
payment/decision sampling, exact exposure/cash/effort bounds, and a clearly
bounded decision-quality comparison. Do not market independent spot checking,
Bayesian information value or Brier propriety as newly invented ideas.

The next scientific uncertainty is whether an economically credible trusted
T exists at the assumed quality/cost and whether the small neutral incentive
margin survives real release interests and calibration errors. An external
noisy verification channel is a trust boundary; this memo is not a proof of
permissionless/decentralized correctness or a production escrow design.
Quantify that boundary before engineering a new system.

Any future empirical study should separate training/calibration, predeclared
test distributions, audit-quality/cost evidence, b sensitivity and participation.
No such new study, grid, version, merge or runtime change is performed here.

## 8. Verification and literature boundary

The mathematical arguments above precede the new finite checks. Verification
must independently enumerate primitive states for P1/P2 and the one named
dual witness, keep policies fixed, compare all six own actions, and check
normalization, union accounting, cap, target weights, gates and exact ties.
It must not import production payoff/Bayes helpers or search a new policy grid.
Hash verification proves artifact identity, not a theorem by itself.

Relevant primary work already recognizes costly evaluation/spot checking
([Gao et al., official 2020 extended abstract of the 2019 article](https://www.ijcai.org/proceedings/2020/0723.pdf))
and principal-agent incentives for costly information
([Chen et al., ICML/PMLR 2023, abstract](https://proceedings.mlr.press/v202/chen23ah.html)).
Their assumptions and objectives do not supply the specific CEAV bounds here.
The prior source boundaries in the historical `references/V6_RAVE_PRIMARY_SOURCES.md`
and `references/V5_INFORMATION_SCORING_SOURCES.md` remain relevant;
this is not a systematic novelty review. New propositions here are derived
for the explicitly stated payoff, timing, strategy and signal assumptions.

Execution evidence is under the historical
`results/research-synthesis-audit-20261024T045716506866Z/` directory; the
central parent arithmetic certificate is copied into this package as
`../frozen-boundary/parent-arithmetic-certificate.json`.

- `named-checks/certificate.json`: 224 exact checks, one new design point,
  P1/P2 witnesses, all 36 neutral deviations for the dual point, and the
  original three fixtures' binary effort bounds.
- `optimized-checks/certificate.json`: the same checks under `python -O`;
  explicit verification guards do not disappear when assertions are optimized.
- `cross-oracle-and-identity.json`: 10 decision-metric matches against the
  historical V6 potential-state oracle, payment and all six branch optima
  checked against the separate V5.1 binary oracle; 42 output hashes checked
  across 11 historical manifests. Identity is separate from correctness.
- `pinned-replay/`: replay of the new checker from its own pinned memo/source/
  config snapshots, with an identical certificate.
- `v6-regression.log`: the existing V6 regression suite, without edits to it.

The new checker imports only the Python standard library. Its finite sums
are separate from the paper formulas and are also cross-checked with two
pre-existing independently authored oracles. This is arithmetic verification
plus explicit proofs, not proof-assistant verification or a new equilibrium
engine. No new policy grid or sensitivity study ran.

The on-paper-before-checker record is
`results/research-synthesis-paper-20261024T045417906990Z/declaration.json`;
it states explicitly that this is not a model-version preregistration.

Commands checked from the workspace root:

```powershell
python verification/research_synthesis_checks.py --out NEW_OUTPUT_DIRECTORY
python -O verification/research_synthesis_checks.py --out NEW_OPTIMIZED_DIRECTORY
python -m unittest tests.test_v6_feasibility tests.test_v6_regressions tests.test_v6_mutations tests.test_v6_stop_certificates -v
```

`NEW_*` denotes a fresh directory; existing outputs are rejected. Historical
artifacts and commit `6fb0f43` remain unchanged. This memo does not merge or
automatically publish the branch.
