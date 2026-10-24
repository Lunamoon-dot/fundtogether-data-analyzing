# CEAV-M1 novelty audit for T3–T5

Date: 2026-10-24

Evidence baseline: `b6935ea11d6dda42ec089c83e03013db7f86fdf4` on
`research/v6-rave-phase01`
Scope: focused primary-source audit of the T3, T4 and T5 claims in
[`CEAV_M1_THEOREM_AND_COUNTEREXAMPLE_CATALOG.md`](CEAV_M1_THEOREM_AND_COUNTEREXAMPLE_CATALOG.md).

This note is a priority audit, not a systematic literature review. It does
not alter the certified game, study parameters, historical results or
equilibrium grid. “No direct prior found” means that the focused search did
not locate an identical result; it is not a claim that the result is globally
novel. A paper should state candidate novelty only after a broader search and
author-level priority check.

## Executive assessment

The audit supports the following positioning.

* The general ingredients of T3—costly information, matching or spot-check
  rewards, report-sensitive audit selection, and allocating verification to
  states with greater decision value—are established. The exact CEAV
  combination of a report-independent payment lottery, a separate
  report/risk-dependent decision lottery, one shared noisy audit, union
  accounting, and a reserve/cash gate was not located in the sources below.
  It is therefore a **candidate architectural novelty**, not a priority
  claim.
* T4’s substantive behavioral claim is established: an expert who benefits
  from the induced decision can misreport, and proper compensation must offset
  that utility. The exact rational endpoints in the frozen CEAV finite game
  are an instance-specific certificate. They are not a new general theorem
  about biased experts.
* T5’s warning that a truthful equilibrium can coexist with uninformative or
  bad equilibria is established in peer-prediction research. The exact
  parameterized all-pure-equilibrium boundary with external release utility,
  settlement-quality gates, exposure and cash metrics is a candidate
  instance-level contribution. It must be described as a finite certificate
  for the declared game, not as an equilibrium-selection theorem in general.

The defensible paper claim is thus: **an exact, budget-constrained case study
of separated payment/decision verification and its external-interest failure
boundary, with explicit negative equilibria**. The sources do not support
“first selective-auditing mechanism,” “first dual-purpose audit,” or a
universal impossibility/robustness claim.

## Method and source boundary

The audit checked primary papers or official publisher/author copies available
through AAAI, IJCAI, AAMAS/IFAAMAS, AEA, Theoretical Economics, JAIR and author
repositories. The search focused on `costly effort`, `spot checking`,
`report-sensitive verification`, `decision-interested experts`, `strategic
information acquisition`, `peer prediction`, `uninformative equilibria`, and
`equilibrium selection`. The relevant source set is:

1. [Zarkoob, Fu and Leyton-Brown, “Report-Sensitive Spot-Checking in
   Peer-Grading Systems,” AAMAS 2020](https://www.ifaamas.org/Proceedings/aamas2020/pdfs/p1593.pdf).
   Definitions 2.1, 2.5–2.7, Theorem 3.1 and Theorem 3.3 explicitly compare
   report-oblivious and report-sensitive spot-checking and derive minimum
   spot-check probabilities under costly noisy observations.
2. [Gao, Wright and Leyton-Brown, “Incentivizing Evaluation with Peer
   Prediction and Limited Access to Ground Truth,” Artificial Intelligence
   275 (2019), DOI 10.1016/j.artint.2019.03.004](https://doi.org/10.1016/j.artint.2019.03.004),
   with the [IJCAI-20 extended abstract](https://www.ijcai.org/Proceedings/2020/0723.pdf).
   The latter states the universal-mechanism limitation, spot-checking
   construction and minimum-effort threshold explicitly in §§3–5.
3. [Witkowski, Bachrach, Key and Parkes, “Dwelling on the Negative:
   Incentivizing Effort in Peer Prediction,” HCOMP 2013, DOI
   10.1609/hcomp.v1i1.13089](https://doi.org/10.1609/hcomp.v1i1.13089).
   It analyzes output agreement, costly effort, penalties and unwanted
   equilibria.
4. [Azrieli, “Monitoring Experts,” Theoretical Economics 16 (2021), DOI
   10.3982/TE4017](https://onlinelibrary.wiley.com/doi/10.3982/TE4017).
   The abstract and §§1–2 study contracts that induce costly information and
   truthful reports by making transfers depend on the vector of reports.
5. [Carroll, “Robust Incentives for Information Acquisition,” Journal of
   Economic Theory 181 (2019), DOI 10.1016/j.jet.2019.03.001](https://doi.org/10.1016/j.jet.2019.03.001).
   This is prior art on effort incentives, uncertainty over experiments and
   limited liability; it is not a CEAV equilibrium result.
6. [Boutilier, “Eliciting Forecasts from Self-interested Experts: Scoring
   Rules for Decision Makers,” AAMAS 2012](https://www.cs.toronto.edu/~cebly/Papers/Boutilier_aamas12.pdf).
   The abstract, §§2–4 and Theorem 3 model experts with direct utility for the
   induced decision and characterize compensating scoring rules.
7. [Argenziano, Severinov and Squintani, “Strategic Information Acquisition
   and Transmission,” AEJ: Microeconomics 8 (2016), DOI
   10.1257/mic.20140135](https://www.aeaweb.org/articles?id=10.1257/mic.20140135).
   The abstract and model analyze costly information acquisition with biased
   strategic communication.
8. [Kong and Ligett and Schoenebeck, “Putting Peer Prediction Under the
   Micro(economic)scope and Making Truth-telling Focal”](https://schoeneb.people.si.umich.edu/papers/PeerFocal.html).
   The paper’s primary abstract explicitly identifies uninformative equilibria
   and classifies equilibria in a binary peer-prediction setting.
9. [Kong and Schoenebeck, “Equilibrium Selection in Information Elicitation
   without Verification via Information Monotonicity,” ITCS 2018, DOI
   10.4230/LIPIcs.ITCS.2018.13](https://drops.dagstuhl.de/storage/00lipics/lipics-vol094-itcs2018/LIPIcs.ITCS.2018.13/LIPIcs.ITCS.2018.13.pdf).
   It studies equilibrium multiplicity and focality rather than settlement
   loss.
10. [Ben-Porath, Dekel and Lipman, “Optimal Allocation with Costly
    Verification,” AER 104 (2014), DOI 10.1257/aer.104.12.3779](https://www.aeaweb.org/articles?id=10.1257/aer.104.12.3779),
    and [Erlanson and Kleiner, “Costly Verification in Collective Decisions,”
    Theoretical Economics 15 (2020), DOI 10.3982/TE3101](https://econtheory.org/ojs/index.php/te/article/viewArticle/3101).
    These establish closely related strategic verification and collective
    decision models, but use different information, transfers and checks.
11. [Krause and Guestrin, “Optimal Value of Information in Graphical Models,”
    JAIR 35 (2009), DOI 10.1613/jair.2737](https://doi.org/10.1613/jair.2737).
    This is the decision-theoretic precedent for conditioning observation
    effort on information value and terminal consequences.

## Claim-by-claim audit

### T3: separated payment and decision audits

#### T3a, factorization and effort threshold

CEAV states that, when `A_pay` is independent of information, reports and
peers, the expected matching reward is

```text
E[R_i | I,r] = f + mu*a*P(T=r | I),
```

and that High effort is strictly preferred to the best Low report exactly
when `mu*a*delta_i(z) > c_i`. This is a direct conditional-expectation
calculation in the fixed CEAV game. The nonnegative value-of-information
observation is also elementary: High can reproduce the best Low report, so
the pre-cost maximum cannot decrease.

The threshold principle is not novel. Zarkoob et al. derive an explicit
minimum spot-check probability for a report-oblivious mechanism in their
Theorem 3.1 and a report-sensitive optimum in Theorem 3.3. Gao et al.’s
Lemma 1 likewise equates the expected truthful high-effort reward net of cost
with the best no-effort reward to obtain the minimum trusted-check probability.
Witkowski et al. analyze the same economic tradeoff for output agreement,
including the role of penalties. Azrieli explicitly frames the problem as
inducing experts to collect information and truthfully report it when the
state is not directly verifiable. Carroll studies effort contracts under
uncertain information-acquisition technologies.

Therefore:

* “Costly effort can be induced by an audit-linked reward above a value-minus-
  cost threshold” is **established prior art**.
* The frozen CEAV value `delta=2/25`, the `a>5/16` lower bound, and the exact
  branchwise gap are **new instance calculations unless an identical model is
  found**, but they should be labeled a finite certificate.
* A binary match reward remains a modal-label incentive, not a strictly proper
  probability score. T3 does not prove truthfulness of arbitrary probability
  reports or recover the proper-scoring-rule guarantees of RBTS.

#### T3’s separation architecture

The closest prior architecture is not an exact match. Zarkoob et al. define
report-oblivious spot checking (fixed audit probability) and report-sensitive
spot checking (audit probability can depend on reports). Their mechanism uses
the trusted report both to evaluate reports and to determine reward. Gao et al.
also use a spot check to compare signal and belief reports with a trusted
report; the “peer-insensitive” construction pays a constant when no spot
check occurs. Those results establish that payment eligibility and audit
selection can be designed separately from peer prediction, but do not contain
the exact CEAV pair of lotteries:

```text
A_pay independent of reports -> payment eligibility;
A_dec depending on risk/report class -> decision verification;
one common T if either occurs;
bonus only when A_pay=1;
one audit charged for A_pay union A_dec.
```

The focused search found no paper stating this exact dual-lottery, shared-
noisy-audit, union-accounting architecture together with a reserve cap and a
three-Judge stationary game. This is a **candidate structural novelty**. The
following narrower claims are safe:

* The independent payment lottery blocks a direct report-to-payment-
  eligibility channel by construction.
* It does not make the report irrelevant to expected reward: reports still
  choose which label is matched to `T`.
* It does not by itself establish raw-signal truthfulness, since modal binary
  matching can have ties or constant-label optima.
* It does not establish global equilibrium quality; T5’s enumeration is still
  required.

#### T3 selective versus uniform decision auditing

The comparison at equal expected exposure is a standard value-of-information
allocation argument. Krause and Guestrin formalize choosing observations by
terminal decision value and cost. Zarkoob et al. show that changing the
probability of a trusted check as a function of reports can reduce expected
checking work under their own DSIC constraints. The general claim that one
should place more audit probability on states with greater `VOI` is therefore
not novel.

What remains specific to CEAV is the exact finite comparison under frozen
calibrated tables, asymmetric false-approval/false-rejection loss, a noisy
claim-level `T`, one shared audit, and the union exposure identity
`a+(1-a)d`. The inequality in T3b is a **model-specific exact result**. It is
not a universal theorem that selective auditing is better than uniform
auditing, because the comparison can reverse when report distributions,
calibration, audit accuracy, costs or terminal rules differ.

The equal-exposure statement must be conditioned on the same report
distribution. It cannot be carried over to T4/T5 strategic equilibria where a
biased Judge changes reports and therefore changes risk-class frequencies,
cash and union exposure.

### T4: exact local external-interest boundary

T4 freezes all peers at H01 and gives Judge `i` utility

```text
E[R_i] - effort_cost_i + b_i*P(D_final=1).
```

Every unilateral deviation has affine utility in `b_i`. Intersecting the exact
half-lines for the five non-self actions in each branch yields the stated
rational intervals. The binding Selective rows are the exact L0 deviation at
`z=0` and L1 deviation at `z=1`; the Uniform rows are analogous.

The behavioral premise is already known. Boutilier’s AAMAS paper states that
an expert who has an inherent interest in the decision usually has an
incentive to misreport, and Theorem 3 characterizes compensation rules that
offset that utility. It defines the expert’s utility for a report through the
decision induced by that report, which is the same strategic channel modeled
by CEAV’s `b_i`. Argenziano et al. likewise analyze costly acquisition and
biased communication. The CEAV bound is therefore not a new theory of
decision-interested experts.

The following are the only potentially novel parts of T4:

1. the exact fractions `-70/633`, `175/1102` and Uniform analogues for the
   frozen six-action, three-Judge, calibrated settlement game;
2. the identification of which action/branch is first profitable on each
   side; and
3. the conservative box `|b_i|<7/500` derived from the minimum neutral gap and
   bounded decision slope.

These are **instance-specific parametric-game certificates**. Affine utility
and endpoint intersection are generic finite-game algebra, so the paper must
not present them as a new general equilibrium-boundary method. The endpoint
calculation is also conditional on fixed peer strategies and fixed off-
equilibrium decision tables. It does not prove a global equilibrium result.

Boutilier’s paper also supplies a key limitation: truthful reporting with
decision interest requires compensation tied to the expert’s utility or a
known bound on it. CEAV does neither. The interval is a trust assumption for
the model, not an enforced restriction on a real Judge’s preference.

### T5: local truthfulness versus all-equilibrium settlement quality

T5 enumerates all pure stationary branch profiles in the declared six-action
class and intersects exact affine inequalities in the scalar external-interest
parameter. It then evaluates every surviving equilibrium against quality,
cash, reserve and exposure gates. This yields a connected component around
zero where every declared pure equilibrium is gate-safe, plus explicit bad
equilibrium witnesses at positive and negative endpoints.

The conceptual distinction is established. The Kong–Ligett–Schoenebeck paper
states that peer prediction can have a strict truthful equilibrium together
with uninformative equilibria and studies methods for making truth-telling
focal. Kong and Schoenebeck’s ITCS paper likewise treats equilibrium
multiplicity and focality as central problems. Zarkoob et al. explicitly note
that many peer-prediction mechanisms have uninformative equilibria and that
some methods make truthful equilibrium unique only with additional trusted
agents or assumptions. Gao et al.’s Theorem 1 separates existence of a
truthful equilibrium from Pareto dominance over other equilibria.

Thus the following is established prior art:

* a truthful equilibrium may coexist with uninformative equilibria;
* equilibrium selection/focality is separate from local best-response
  truthfulness; and
* trusted checks can alter the comparison, but do not automatically remove
  all bad equilibria under every model.

The candidate CEAV contribution is narrower: the exact rational global quality
boundary for a budget-feasible settlement mechanism with external release
utility, noisy shared audit, asymmetric FA/FR gates, cash and reserve limits.
No directly identical source was found in this focused audit. That result must
be described as a **finite, pure-stationary certificate for the frozen
instance**, not a theorem about all mixed, sequential, coalition-proof or
Bayesian equilibria.

The T5 count is also a reproducibility result rather than a novelty claim by
itself. Enumerating `216^2` full branch-profile pairs per scenario and keeping
ties is the correct evidence for the declared class. It does not establish:

* uniqueness of equilibrium outside the declared pure stationary class;
* robustness to mixed strategies, sequential deviations or coalitions;
* Sybil resistance, participation or realistic outside options; or
* an empirically calibrated value of `b`.

## Literature-to-claim matrix

| CEAV claim | Closest primary sources | Audit result | Permitted wording |
|---|---|---|---|
| Audit-linked reward can induce costly effort above a threshold | Zarkoob et al. Thm. 3.1/3.3; Gao et al. Lemma 1; Witkowski et al.; Azrieli; Carroll | Established principle | “We derive the threshold for our frozen game.” |
| Report-sensitive audit selection can reduce expected checking work | Zarkoob et al. Definitions 2.5–2.7 and Thm. 3.3 | Established in a different DSIC model | “Our risk-class allocation is a different finite settlement application.” |
| Separate payment eligibility and decision-audit lotteries | Zarkoob/Gao are adjacent; no exact match found | Candidate structural novelty; priority open | “We study a separated architecture” (not “first”). |
| Selective verification improves loss at equal exposure | Krause–Guestrin VOI; Zarkoob workload allocation | General principle established; CEAV inequality instance-specific | “Under frozen calibration and matched reports, exact calculation shows…” |
| External release utility can make truthful reports unprofitable | Boutilier Thm. 3; Argenziano et al. | Established | “We specialize this known channel to a finite settlement game.” |
| Exact `b` breakpoints | No identical source found | Instance-specific certificate; general method not claimed | “The certificate gives exact endpoints for this game.” |
| Truthful/local equilibrium need not imply global quality | Kong–Ligett–Schoenebeck; Kong–Schoenebeck; Gao et al.; Zarkoob et al. | Established conceptual issue | “We provide an explicit settlement counterexample and boundary.” |
| Exact all-pure-equilibrium quality boundary | No directly identical source found | Candidate instance-level contribution; priority open | “For the declared class, exhaustive rational enumeration gives…” |

## Required caveats for the manuscript

1. Use “candidate novelty,” “instance-specific certificate” or “focused audit
   found no direct prior,” unless a systematic review and author priority check
   establishes stronger language.
2. Keep T3’s neutral effort/truthfulness result separate from T4/T5 strategic
   external-interest analysis. Payment eligibility independence does not
   remove the `b_i P(D=1)` channel.
3. Keep local H01 strictness separate from global all-equilibrium gates. The
   T5 bad equilibrium at `b=1/10` is precisely evidence against collapsing
   those claims.
4. State the strategy class, frozen calibration, independent lotteries,
   report-lock timing, gate definitions and exact certificate hash whenever
   reporting T3–T5.
5. Do not import the assumptions or guarantees of Zarkoob, Gao, Boutilier,
   Azrieli or Carroll into CEAV. Their agents, signals, payments, verification
   technologies and equilibrium concepts differ.
6. Do not call the synthetic `Z`, `X` or `T` accuracies empirical evidence.
   The novelty question is independent of the empirical trust protocol.

## Search limitations and next priority check

This audit was focused on primary sources already adjacent to the CEAV model;
it did not search every working-paper version, economics database, non-English
venue, dissertation or 2026 preprint. It also did not perform citation-chain
closure for every source’s references. Before submission, the authors should
run a documented systematic search around “dual-purpose verification,”
“payment-independent audit,” “decision-contingent verification,” “strategic
auditing,” “biased expert scoring,” and “global equilibrium quality,” then
send the exact T3–T5 claim wording to the authors of the closest papers for a
priority check.

Until that work is done, the paper-readiness decision is:

```text
Theory manuscript draft: READY, with conditional/instance-level claims.
Submission novelty claim: NOT YET READY.
Mechanism production readiness: OUT OF SCOPE.
```
