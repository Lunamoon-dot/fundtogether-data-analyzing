# CEAV-M1 — External Research Brief

**Version:** 0.3 manuscript correction closeout
**Scope:** verified V3–V6 evidence, the separated payment/decision-audit study, and its declared strategic boundary. This brief is a research package, not a production design or a submission-readiness claim.

## 1. Motivation

FundTogether is a general-purpose decentralized crowdfunding protocol with escrow, milestone verification and conditional fund release. Charity is one optional use case. CEAV-M1 studies one observable milestone acceptance task motivated by that workflow. A creator presents evidence that a milestone is complete; reviewers spend effort to acquire private information; a final decision controls whether a payout is released. The practical problem is to obtain useful effort and accurate decisions while keeping audit exposure, reviewer payments, and false payouts within a fixed budget.

The proposed school-desk study is one physical-acceptance exemplar. It neither defines FundTogether's overall domain nor establishes transfer across campaign categories. CEAV-M1 does not prove decentralized identity, creator incentives, donor welfare or production settlement guarantees.

The central difficulty is strategic. A reviewer may value a particular release outcome, may choose an uninformative report when reporting has no marginal payoff, or may seek an audit when an audit-contingent reward makes that privately profitable. Therefore truthful behavior cannot be inferred from a good signal model or from one truthful profile alone.

![FundTogether milestone verification problem](../figures/ceav_m1_problem_overview.png)

*Figure 1. The practical milestone-verification problem: escrow safety depends on decision quality, reviewer behavior, audit exposure and incentive design.*

## 2. Formal question

For a fixed finite CEAV-M1 game, can a mechanism simultaneously provide (i) a strict effort incentive, (ii) a truthful local equilibrium, (iii) acceptable decision quality and cash cost, and (iv) resistance to external release preferences? The study separates claims about the truthful profile from claims about every pure equilibrium in the declared stationary six-action-per-branch class.

The model uses binary ground truth `Y`, public signal `Z`, private signal `X`, a trusted audit `T`, three Judges, two public branches, exact rational arithmetic, `B=6`, `C_FA=2`, `C_FR=1`, and payout value `V=1`. False-accept and false-reject rates are conditional probabilities:

```text
FA = P(D=1 | Y=0)
FR = P(D=0 | Y=1)
WrongPayout = V × P(Y=0,D=1)
DecisionLoss = C_FA × P(Y=0,D=1) + C_FR × P(Y=1,D=0)
```

With `π=P(Y=1)=1/2`, `V=1`, `C_FA=2`, and `C_FR=1`, this reduces to `WrongPayout=FA/2` and `DecisionLoss=FA+FR/2`.

## 3. Mechanism architecture under study

The dual-purpose architecture uses independent random draws for two lotteries. Conditional on locked `(Z,r)`, `A_pay` and `A_dec` are independent Bernoulli events; the Selective decision probability still depends on the reports:

- `A_pay` selects reward eligibility with probability `a=2/5`, independently of the report. A trusted audit is observed when this event occurs, and the reviewer bonus is paid only on this event.
- `A_dec` selects decision verification with probability `t=1/6`, but only for the frozen risk class `S={Z=0, sum(reports)=2}`. It affects decision verification and does not create reward eligibility.

Whenever either lottery fires, one common audit signal `T` informs the final decision through the frozen `g1` table, including when only `A_pay` fires. Without either event, the decision uses `g0`. Only `A_pay` creates matching-bonus eligibility. The union event is charged once, so exposure is `P(A_pay ∪ A_dec)`. Separating the lotteries removes the direct report-to-payment-eligibility channel under the stated assumptions; it does not solve external-interest manipulation or global equilibrium selection.

![CEAV-M1 dual-purpose verification architecture](../figures/ceav_m1_dual_purpose_architecture.png)

*Figure 2. The signature architecture separates report-independent payment eligibility from risk-dependent decision verification while sharing trusted audit `T`.*

## 4. Verified results

### T3 — Neutral feasibility

Under neutral reviewers and the frozen All-H01 peer profile, the payment lottery supplies an exact effort calculation. The independent proof review records `M_L=33/50` and `M_H=37/50`, so the information value before effort cost is `Δ=M_H-M_L=2/25`. High effort itself costs `c=1/20`; with `μa=2·(2/5)`, the net benefit is `μaΔ-c=7/500`. The neutral profile passes the declared quality, cash, reserve, and exposure gates for the certified Selective and Uniform comparisons.

### T4 — Local external-interest stability

For one Judge with utility `E[R_i] - effort_cost_i + b_i P(D_final=1)`, affine exact payoff comparison gives the following strict All-H01 intervals:

| Mechanism | Local interval for `b_i` |
|---|---:|
| Selective | `-70/633 < b_i < 175/1102` |
| Uniform | `-218750/2070709 < b_i < 218750/1365587` |

These are local best-response results against frozen peers and calibration. They are not a global uniqueness theorem.

### T5 — Global-quality failure at `b=1/10`

At symmetric preferences `b=(1/10,1/10,1/10)`, exhaustive factorized checking of the declared pure stationary class finds four pure Nash equilibria for each frozen mechanism. All-H01 remains locally strict, while three additional strict pure Nash equilibria are bad: each fails the false-accept gate. For Selective, the safe all-pure component around zero is `-70/633 < b < 175/1922`; additional bad pure equilibrium profiles become sustainable before All-H01 loses local stability. Each candidate is checked against unilateral task-local deviations. The analysis does not model coordinated deviations or an equilibrium-selection process. The frozen report labels the study `STRATEGIC_FAILURE` for global robustness, while preserving a nonempty local neutral neighborhood.

![CEAV-M1 T3, T4 and T5 results](../figures/ceav_m1_t3_t4_t5_summary.png)

*Figure 3. T3 establishes neutral feasibility, T4 gives local best-response intervals, and T5 exposes the global bad-equilibrium boundary.*

At neutral `b=0`, Selective has `FA=43/1250`, `FR=481/3125`, loss `348/3125`; Uniform has `FA=328691/9765625`, `FR=3184297/19531250`, loss `4499061/39062500`. Both have union exposure `2557/6250` and expected cash `46957/25000` under All-H01. These comparisons are equilibrium-specific; equal neutral exposure does not imply equal exposure under different equilibrium reports.

## 5. Contribution relative to prior work

The candidate contribution is instance-level and conditional: exact rational incentive and equilibrium boundaries for a separated payment/decision-audit architecture under the stated finite CEAV game. It is not a claim to have invented proper scoring, peer grading, costly-information incentives, or report-sensitive auditing. Relevant prior sources include Boutilier’s decision-maker scoring rules ([AAMAS 2012 primary PDF](https://www.cs.toronto.edu/~cebly/Papers/Boutilier_aamas12.pdf)), Chen et al.’s principal-agent treatment of information acquisition ([ICML 2023 / PMLR](https://proceedings.mlr.press/v202/chen23ah.html)), and Zarkoob, Fu, and Leyton-Brown’s report-sensitive spot checking ([AAMAS 2020 primary PDF](https://www.ifaamas.org/Proceedings/aamas2020/pdfs/p1593.pdf)). A systematic literature review is still required before making a broad novelty claim.

## 6. Limitations and trust assumptions

- The equilibrium conclusions are exact for the frozen finite strategy class and named distributions; they do not cover mixed strategies, coalitions, dynamic learning, or arbitrary mechanisms.
- `T`, `Z`, and `X` accuracy and conditional independence are synthetic assumptions. No field measurements of audit sensitivity, specificity, effort, cost, latency, or reviewer participation are supplied.
- The bound on `b` is an assumption about reviewer preferences, not an enforcement mechanism. Sybil resistance, independence, collusion resistance, evidence integrity, and settlement reliability remain open operational questions.
- Hashes establish artifact identity. Independent code checks establish the reported finite calculations; neither constitutes external human peer review.

Verification attribution is specific: the independent primitive oracle and DB01–DB03 support payoff/calibration and local-boundary calculations. The existing proof-review runner derives T3 from primitive probabilities, checks T4 arithmetic on hardcoded binding rows, and calls the independent completeness audit for T5. The certificate metric checker verifies stored values, not the prose. The v0.3 correction checker and the documented prose inspection address the corrected signs and document consistency; they are not general proof verification.

## 7. Questions for an external reviewer

1. Is the separation of report-independent payment auditing from risk-dependent decision auditing a meaningful instance-level contribution once the prior-art boundaries are fully screened?
2. Are the finite-class equilibrium claims, conditioning conventions, and factorized exhaustive coverage sufficient for the stated local-versus-global conclusions?
3. Which empirical milestone, audit protocol, and reviewer-participation assumptions must be measured before these theoretical results can inform a real escrow workflow?

The detailed derivations, certificates, hashes, and clean replay instructions are in [`CEAV_M1_MANUSCRIPT_V0_3.md`](CEAV_M1_MANUSCRIPT_V0_3.md) and [`review-package/README.md`](../README.md). The [v0.3 correction closeout](CEAV_M1_MANUSCRIPT_V0_3_CORRECTION_CLOSEOUT.md) maps the resolved findings and remaining review limitations. Historical v0.2 and audit evidence remain preserved.
