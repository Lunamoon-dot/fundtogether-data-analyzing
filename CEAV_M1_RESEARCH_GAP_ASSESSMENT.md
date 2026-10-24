# CEAV-M1 — Research gaps, threats and trust

Date: 2026-10-24. Baseline: commit `b6935ea`,
[Dual Boundary Report](CEAV_M1_DUAL_STRATEGIC_BOUNDARY_REPORT.md) and
[parent synthesis](CEAV_M1_RESEARCH_SYNTHESIS_AND_FEASIBILITY_MEMO.md).
This is a research assessment. It preserves all historical results and gates.

**Paper decision: READY_FOR_THEORY_MANUSCRIPT_DRAFT;
NOT_YET_SUBMISSION_READY.** The immediate scientific output is a scoped
theory/counterexample study. The physical audit assumptions remain hypotheses.

## 1. What is established and what is missing

| Layer | Established | Missing evidence or theorem |
|---|---|---|
| General structural reasoning | Conditional audit-seeking gain; report indifference under constant marginal payoffs; payment/decision separation identities. | These are scoped propositions, not impossibility for every selective mechanism. |
| Fixed synthetic mechanism | Neutral feasibility; exact pure intervals; three bad strict equilibria at symmetric b=1/10. | No global guarantee for mixed strategies, arbitrary heterogeneous interests, coalitions, missing reviewers or changing primitives. |
| Literature positioning | Focused primary-source comparisons in the [readiness file](CEAV_M1_PAPER_READINESS.md). | Priority of the precise contribution; manuscript-level theorem mapping and full citation screening. |
| Empirical audit reliability | A specified [physical-evidence protocol](CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md). | No observed sensitivity, specificity, effort costs, audit costs, latency, participation or b distribution. |
| Model-to-application mapping | Explicit binary acceptance and information roles can be proposed. | Evidence that a real milestone population follows the assumed joint distribution and utility model. |

The synthetic 9/10 T accuracy is not a measured statistic. Finding a real
audit with pooled accuracy near 90% would also be insufficient: sensitivity,
specificity, conditioning on risk class/defect type and correlated errors
matter separately. A marginally reliable audit may repeat the same mistake
as all reviewers.

## 2. Restricting b is an assumption, not an enforcement result

The certified utility is `E[R_i]-c_i+b_i*P(D_final=1)`. b_i is the incremental
utility of release over rejection in the same units as the review reward.
It can summarize holdings, a creator relationship, a side payment, reputation
or ideology only when those effects are compatible with this linear,
task-local model. Outcome-contingent or history-dependent bribes may not fit.

For Selective, local H01 stability against H01 peers requires
`-70/633 < b_i < 175/1102`. The all-pure quality-safe symmetric component
is narrower: `-70/633 < b < 175/1922`. At b=1/10 All-H01 remains strict,
yet three additional strict equilibria fail FA. One-biased-position results
cannot be extrapolated to two or three independently biased participants.

The parent's conservative analytic box `|b_i|<7/500` does preserve strict
H01 dominance against every peer profile, giving a unique pure equilibrium
for all three Judges within that box. What remains uncomputed is the exact
global boundary for unrestricted heterogeneous vectors, not that small-box
implication. Neither result shows that real participants satisfy the bound.

Screening relationships, random assignment, excluding declared conflicts
or selecting disinterested research participants may restrict a study
population. They do not bound hidden b_i, prevent side payments or prove
that every admitted participant lies in an interval. An experimental
endowment inducing a known marginal reward for release tests that induced
component, not the participant's entire real-world utility.

The fixed mechanism enforces neither an upper bound on b nor truthful
disclosure of b. Report-independent A_pay fixes payment eligibility, not
decision influence. No test of cooperative neutral participants can establish
robustness to economically material shared release preferences.

Decision-interested experts already appear in
[Boutilier, AAMAS 2012, §§3–4](https://www.cs.toronto.edu/~cebly/Papers/Boutilier_aamas12.pdf).
CEAV's numerical boundaries do not supersede that general literature or
justify compensating away arbitrary external incentives under reserve B=6.
This study does not propose a new compensation policy.

## 3. Threat and trust assessment

The proposed research controls below improve identification and measurement.
They are **not implemented protocol protections**, and they do not add
Resolver/Admin settlement authority to FundTogether.

| Threat or assumption | Failure channel and mathematical consequence | Proposed empirical check/control | Residual trust boundary |
|---|---|---|---|
| Reviewer conflicts | Shared positive b supports Low-approval equilibria before truthful local stability fails; negative b can induce rejection. | Record disclosed ties and incentive exposures before assignment; report separate neutral/conflicted strata; use consented experimental outcome bonuses only in a separately frozen behavioral study. | Hidden holdings, reputation and bribes remain unbounded; declarations do not enforce b. |
| Sybil identities | Three accounts may be one optimizing actor; unilateral three-player analysis no longer describes the game. | Recruit distinct research participants, document recruitment/assignment and shared affiliations; retain cluster identifiers without exposing private identity data. | Study recruitment is a trusted sampling condition, not permissionless identity resistance. |
| Reviewer independence | Different people can use one creator photo, contact or rumor. Conditional independence of X_i can fail even if each looks accurate. | Record evidence provenance, overlapping contacts and error co-occurrence conditional on reference Y and defect type; use campaign/school clusters in uncertainty analysis. | No finite test proves independence; conditioning on binary Y may conceal material common causes. |
| Correlation with T | Reviewer callback and site audit may both accept a forged inventory or miss the same condition defect. More matching rewards need not mean more truth. | Separate personnel, evidence channels and timing; cross-tabulate joint errors, including rare shared false approvals; preserve defect-level records. | Organizational separation alone does not establish `T independent of (Z,X) given Y`. |
| Auditor capture/collusion | T quality becomes strategy-dependent; a creator or reviewer can control both reward target and final evidence. | Fixed fee independent of audit label, blinded assignment, independent reference inspections and documented conflicts; evaluate seeded evidence attacks only with consent and outside real settlement. | These controls cannot certify an uncapturable auditor or independently priced honest T. External audit remains a trust source. |
| Creator evidence strategy | Reused photographs, selective framing, false identity/location or temporary placement changes P(Z,X,T|Y), possibly after seeing the policy. | Lock dossier and cutoff, retain provenance, use registered recipient channels and independent physical inventory; include hard negative cases in the held-out design. | No creator-strategy equilibrium or adversarial distribution guarantee is proved. A hash proves bytes, not physical truth. |
| Participation and outside options | A Judge may decline, delay, abandon costly checks or prefer no participation. Forced three-Judge NE omits these actions. | Record invitations, take-up, attrition, time and stated reservation compensation; report selection by experience/conflict and nonresponse outcomes. | Positive modeled utility relative to zero is not individual rationality relative to actual alternatives; no endogenous entry theorem exists. |
| Audit latency and settlement | T may arrive after a decision deadline, or Y may change between inspections. The model assumes T arrives before the final decision on the same claim. | Freeze claim-time semantics and record evidence/inspection timestamps, queue/travel delays, unavailable sites, rework and timeout frequency. | No timeout, retry, appeal or liveness mechanism is certified; unavailable T is not silently assigned 0/1. |
| Changing effort and costs | Public evidence strength, training, travel or workload changes effort value; the F51-01 strong-Z example has zero binary effort gain. | Separate access assignment, actual use, active time and cost disutility; measure learning/workload and estimate branch-specific information gains. | Time is not automatically c_i; cost and signal distributions are neither homogeneous nor stationary by default. |
| Calibration and prevalence shift | A table calibrated to H01 and prior 1/2 can be miscalibrated on biased or new reports. Prevalence changes wrong-payout/loss weighting and expected cash; conditional FA/FR stay fixed if class-conditional laws and the decision rule are fixed. | Keep a pilot/training population distinct from held-out clusters and times; lock report encoding, table and analysis before evaluation; report deployment-target weighting separately. | Do not refit on deviations or on held-out outcomes and retain the old guarantee. Any new model claim needs a separate authorized study. |

The identity issue is established in
[Douceur's original Sybil paper, introduction and model](https://www.microsoft.com/en-us/research/wp-content/uploads/2002/01/IPTPS2002.pdf).
Its assumptions are not a universal statement about every identity technology;
the immediate CEAV implication is simply that account count is not evidence
of independent strategic actors. No identity mechanism is added here.

The desk protocol defines a snapshot acceptance claim. Physical presence
at tau does not by itself establish ownership or continued availability;
temporary placement is not an error relative to a presence-only predicate.
Any stronger ownership or persistence claim needs its own acceptance
predicate and evidence, rather than relabeling a successful snapshot.

As a direct correlation counterexample, if `X_A=X_B=X_C` is the same noisy
label, majority has exactly that label's accuracy; three reports do not create
three independent observations. If T copies that label too, perfect agreement
with T can coexist with joint errors relative to Y. This logical example is
outside the certified independent-signal model, not a measured attack rate.

## 4. Research priorities and falsifiers

| Priority | Bounded next research question | What would refute the intended application claim? |
|---|---|---|
| P0: paper validity | Can an independent reader reproduce the five scoped propositions and every cited exact witness? | A payoff/timing mismatch, missing deviation/tie, inconsistent denominator or irreproducible pinned certificate. |
| P0: prior art | What precise claim survives comparison with report-sensitive spot checking and decision-interested forecasting? | A prior result already contains the claimed theorem under equivalent assumptions. Reframe as replication/case study; do not invent novelty. |
| P1: reference feasibility | Can the chosen desk-delivery milestone receive a stable, independent contractual reference label? | High unresolved-label/missing-site rates or shared reference/T capture; do not relabel consensus as truth. |
| P1: empirical T | What are held-out sensitivity/specificity and joint error structure for the defined operational audit? | Reliability or dependence incompatible with the stated assumptions, or uncertainty too large to assess them. Do not substitute a point estimate for a guarantee. |
| P1: economics | What are all-in audit costs, reviewer disutility, outside options and delay in an agreed unit? | No credible mapping to the fixed synthetic reward/cost ratios, or low participation. This falsifies application fit, not the already proved synthetic theorem. |
| P1: conflicts | Is the required b restriction defensible for the sampled population and utility scale? | Undisclosed/shared interests or a material unverifiable component of utility. Unmeasured b means the interval cannot be claimed to apply. |
| P2: wider theory, only if separately requested | Mixed/coalitional equilibria, arbitrary b vectors, dependence, participation or uncertain calibration. | Current results provide no answer; absence of a counterexample is not a guarantee. |

The [empirical protocol](CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md) is a proposed
study plan, not data or authorization to recruit, inspect, pay or settle
milestones. It must be operationally frozen after selecting consenting sites,
reference personnel, cost units and feasible precision targets. Research
adjudication defines study labels and does not become production authority.

## 5. Scientific contribution and paper decision

The defensible story is the separation of five questions: correct scoring,
paid information acquisition, truthful local reporting, equilibrium selection,
and all-equilibrium decision quality. The verified sequence supplies
counterexamples to treating one favorable layer as proof of the next.
It also preserves a useful conditional construction and its later failure.

Carefully designed report-sensitive checks can succeed in other models
([Zarkoob et al., 2020](https://www.ifaamas.org/Proceedings/aamas2020/pdfs/p1593.pdf));
report-independent verification also has adjacent prior art
([Zhang et al., 2026 preprint](https://arxiv.org/html/2610.01514v1)).
Thus the paper should pursue a reproducible, conditional boundary result,
not a universal anti-selectivity theorem or a claim to invent spot checking.

Proceed to a **theory/counterexample manuscript draft**. Before submission,
resolve priority positioning, obtain independent proof review, and prepare
an archival, clean-replay package. Empirical validation is a separate
prerequisite for claims about real FundTogether milestones, not evidence
that can be inferred from synthetic 90% accuracy. This is a paper-readiness
decision; no production-readiness conclusion or new mechanism follows.
