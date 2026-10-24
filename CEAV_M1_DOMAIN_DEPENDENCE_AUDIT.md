# CEAV-M1 — Domain Dependence & Generality Audit

**Repository:** `Lunamoon-dot/fundtogether-data-analyzing`  
**Branch:** `research/v6-rave-phase01`  
**Re-audit date:** 2026-10-25 (Asia/Saigon)

**Reviewed HEAD:** `de9368c128c0c258cd2174f9958c771215596bb0`

**Audit status:** completed for the declared research scope, with a confirmed
proof transcription error and editorial findings. No manuscript, frozen
certificate, parameter, mechanism or production contract was changed.

This re-audit supersedes the earlier blanket proof PASS in this file. The
[previous report](reviews/domain-dependence-audit-20261024T1852556143502Z/previous-audit.md)
is preserved byte-for-byte (SHA-256
`748bca86f7580a433be55a3a382e8f8e83bd12cdb1109a78789dd5c26a36b7d3`).

This audit asks whether the CEAV-M1 results require FundTogether to be a
charity platform. The correct product scope is broader: FundTogether is a
general-purpose decentralized crowdfunding protocol with escrow,
milestone-based verification and conditional fund release. Charity is one
possible application. CEAV-M1 studies the verification game behind an
observable milestone; it does not model a charity-specific transfer rule or a
production blockchain.

The evidence boundary used here is the frozen dual configuration
[`configs/dual_boundary.json`](configs/dual_boundary.json) (lines 2-18), the
exact certificate at
[`results/dual-strategic-boundary-20261024T0524070523492Z/analysis/certificate.json`](results/dual-strategic-boundary-20261024T0524070523492Z/analysis/certificate.json)
(lines 2-120) with SHA-256
`fde3ad4745b37e270469aaec2692a51c83cbcf5db7fcb0a16938296a6e25b7d5`, and the
frozen report at
[`CEAV_M1_DUAL_STRATEGIC_BOUNDARY_REPORT.md`](CEAV_M1_DUAL_STRATEGIC_BOUNDARY_REPORT.md)
(lines 1-30).

## 1. Executive assessment

| Finding | Classification | Assessment and evidence |
|---|---|---|
| The core mathematical game is charity-independent. | **PASS** | The model is stated in terms of a binary milestone state `Y`, signals `Z`, `X_i`, `T`, reviewer actions and a release decision. The manuscript describes an escrow milestone without a beneficiary-purpose restriction (`CEAV_M1_MANUSCRIPT_V0_2.md:14-20`, `44-52`, `112-127`). |
| The numbers are portable across campaign domains. | **CONDITIONAL / GAP** | They remain identical if the complete mathematical game remains identical, irrespective of the domain label. No evidence establishes that real domains share those synthetic inputs (`CEAV_M1_MANUSCRIPT_V0_2.md:112-115`; `configs/dual_boundary.json:5-18`). Different inputs require new analysis; the frozen fractions cannot simply be transported. |
| The current results can be applied directly to a live campaign. | **CONDITIONAL** | Direct application requires an objectively labelable milestone, a mapping from public/private evidence to the signal variables, a defensible operational `T`, the stated timing and independence conditions, and a utility/cost scale compatible with the game. None has been measured (`CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md:1-10`, `41-55`, `336-339`). |
| The trusted audit is a trustless oracle. | **GAP** if read that way; **PASS** under the declared model | `T` is a noisy exogenous signal with accuracy `9/10`, and the manuscript explicitly calls accuracies synthetic (`CEAV_M1_MANUSCRIPT_V0_2.md:112-115`; theorem catalog `:32-37`). The empirical protocol separately warns that independence, capture and joint errors are unmeasured (`CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md:138-164`). |
| Local truthful stability implies safe settlement in every equilibrium. | **FAIL** as a proposed implication; **PASS** as a rejected claim | T4 is explicitly local with frozen H01 peers. T5 gives three bad strict equilibria at `b=1/10` while All-H01 remains strict (`CEAV_M1_MANUSCRIPT_V0_2.md:298-367`; `CEAV_M1_DUAL_STRATEGIC_BOUNDARY_REPORT.md:181-219`). The manuscript does not make the invalid implication. |
| The T4 proof is correct as printed in the manuscript. | **FAIL — proof transcription** | Both binding deviation gains use `>=0` instead of `<=0` (`CEAV_M1_MANUSCRIPT_V0_2.md:308-313`, repeated in `review-package/docs/CEAV_M1_MANUSCRIPT_V0_2.md:308-313`). At `b=0` they read `-7/500>=0`. The catalog and executable calculation use the correct orientation; T4's stated endpoints survive. See F1 in §5. |
| The documents make universal charity, decentralization or production claims. | **PASS for these specific boundaries** | The manuscript disclaims universal impossibility, empirical audit accuracy, Sybil resistance and production readiness (`CEAV_M1_MANUSCRIPT_V0_2.md:33-40`). This does not excuse the confirmed proof and bibliographic errors in §5. |

**Answer to the central question.** No counterexample to the stated T3, T4 or
T5 results was found under their declared assumptions. Their exact numerical
claims were reproduced; T4's written proof nevertheless needs a sign correction.
The general-purpose FundTogether
scope does not require a new mechanism or a change to the frozen research
model. It does require narrowing application claims: CEAV-M1 is a conditional
verification case study for milestones that can be represented by the stated
binary and signal model.

F1 is a real mathematical error in the written derivation, repairable without
changing the theorem, game or certificate. F2 is incorrect bibliographic
attribution. Neither is evidence of a foundational failure. T5's bad equilibria
are an unfavorable mechanism result that must remain visible, rather than a
research mistake to remove. The blockers for real-world adoption are empirical
and operational: ground
truth definition, signal calibration, audit independence and capture, effort
and participation economics, external release interests, creator evidence
strategy, and settlement timing/liveness.

Classification used throughout: **PASS** = supported within the declared
scope; **CONDITIONAL** = needs stated additional conditions; **GAP** = missing
evidence or unmodeled behavior; **FAIL** = an actual false or inconsistent
statement. A domain mismatch or missing measurement alone is not a proof FAIL.

### Fresh verification and evidence boundary

The [run manifest](reviews/domain-dependence-audit-20261024T1852556143502Z/manifest.json)
pins the inspected raw inputs and records Python 3.12.10, commands, working
directories and exit codes. All six numerical/replay commands exited zero:

| Command (workspace root unless noted) | Fresh result |
|---|---|
| `python -X utf8 -m verification.independent_t3_t5_review` | 5,590 independent checks; 864 branch payoff/metric rows, 4,320 branch candidates, 466,560 full-profile coverage across the two mechanisms and five scenarios. |
| `python -X utf8 -m verification.manuscript_editorial_audit` | 80 stored equilibrium metric rows checked; PASS. |
| `python -X utf8 -m unittest tests.test_dual_boundary -v` | 10 tests discovered and executed; all pass. |
| Same focused suite with `python -X utf8 -O -m unittest ...` | 10 tests discovered and executed; all pass. |
| Metric audit from `review-package/` | 80 rows; PASS against the packaged certificate. |
| `python -X utf8 verification/dual_boundary.py --out reviews/domain-dependence-audit-20261024T1852556143502Z/replay` | New output directory; regenerated certificate byte-identical to frozen SHA-256 `fde3ad4745b37e270469aaec2692a51c83cbcf5db7fcb0a16938296a6e25b7d5`. |

The separate [sign probe](reviews/domain-dependence-audit-20261024T1852556143502Z/sign_probe.py)
deliberately exits 1 on the current manuscript and packaged copy; its
[stdout](reviews/domain-dependence-audit-20261024T1852556143502Z/sign-probe.stdout.txt)
and [failure](reviews/domain-dependence-audit-20261024T1852556143502Z/sign-probe.stderr.txt)
preserve the counterexample to the printed inequalities. This expected failure
is an audit finding, not a failure of the ten engine tests. The existing metric
checker reads certificate values, not manuscript proof text
(`verification/manuscript_editorial_audit.py:25-33`); a green result
therefore cannot certify the prose or catch F1. No full V1–V6 suite or browser
acceptance was rerun; this audit makes no new whole-system completion claim.

## 2. Complete assumption inventory

The inventory distinguishes a mathematical assumption from a domain condition.
“Essential” means that removing the assumption invalidates the cited proof or
changes the game; it does not mean that the assumption is true in practice.

| ID / assumption | Mathematical role and essentiality | Domain dependence and support | Consequence if violated | Evidence |
|---|---|---|---|---|
| A1. Binary ground truth `Y` and prior `P(Y=1)=1/2`. | Defines the state, likelihoods, conditional FA/FR and prior-weighted loss. Essential to the numeric certificate and calibration. | The binary abstraction is domain-neutral, but every real campaign needs a preregistered acceptance predicate. No field label exists. | Ambiguous or time-varying `Y` makes signal accuracy, decision loss and wrong-payout calculations refer to the wrong target. | `CEAV_M1_MANUSCRIPT_V0_2.md:112-115`, `191-215`; empirical protocol `:41-55`, `:83-90`. |
| A2. Public signal `Z` has symmetric sensitivity and specificity `7/10` and two positive-probability branches. | Determines branch posteriors and the frozen `g0/g1` tables. Essential to T3b–T5 values; pooled accuracy alone is insufficient. | A public dossier is plausible in many domains, but its conditional error rates and prevalence are unmeasured. | Different prevalence, asymmetric errors or public evidence changes calibration, risk-class frequency and the fractions. | Catalog `:32-37`; manuscript `:129-147`; config `:5`, `14-15`. |
| A3. Each potential `X_i` has symmetric sensitivity/specificity `4/5`; Low sees no `X_i`; High pays cost and observes it. | Produces `Delta=2/25` and makes raw-X H01 the unique modal-label High plan. Essential to the numerical T3 result, not to the general factorization identity. | Such acquisition workflows are possible interpretations; `4/5` and homogeneous expertise/cost are unmeasured. | Additional free information, asymmetric errors or no modal improvement can change the optimum and remove effort incentives. | Catalog `:24-37`; manuscript `:117-127`, `230-265`. |
| A4. Common `T` has symmetric sensitivity/specificity `9/10`, is available on either lottery, and is used by `g1` on their union. | Supplies matching reward and the decision update. Its law is exogenous, unchanged by effort/reports, audit route or workload. Essential to the numerical reward and decision calculation. | “Trusted” does not mean infallible or capture-resistant. No conditional error or route-invariance measurements exist. | A captured, unavailable, route-dependent or strategically generated `T` changes incentives and final decisions. | Catalog `:32-47`, `67-70`; manuscript `:151-176`; empirical protocol `:119-164`, `300-306`. |
| A5. Conditional independence of `Z`, all `X_i` and `T` given `Y`. | Enables Bayes calibration, factorized enumeration and the independent oracle. Essential to the stated numerical results. | It is a strong empirical restriction. Separate people or channels do not prove it; common evidence can induce correlated errors. | Correlation can make three reports no more informative than one and can create joint false approvals even when marginal accuracy looks high. | `CEAV_M1_THEOREM_AND_COUNTEREXAMPLE_CATALOG.md:32-37`; protocol `:138-164`; gap assessment `:75-79`, `97-101`. |
| A6. Reports lock before hidden lotteries; `T` arrives before the final decision on the same claim. | Makes report-independent `A_pay` factorization and union accounting well-defined. Essential to T3 and the boundary certificate. | Timing depends on evidence access, travel and settlement latency. It is not measured. | Revealed lotteries, late audits or changing milestones create a different information game and may change incentives or make settlement unavailable. | `CEAV_M1_MANUSCRIPT_V0_2.md:149-181`; report `:20-26`; gap assessment `:80-83`. |
| A7. Six branch-local actions `{L0,L1,H00,H01,H10,H11}` and stationary strategies. | Defines the action space and `6^3` branch enumeration. Essential to exact T4/T5 coverage. | An abstraction; human information and actions can be richer. | Abstention, delay, partial inspection or evidence manipulation can add deviations. Randomization over the six retained actions cannot improve on every pure action against fixed pure peers, by linearity, but additional mixed equilibria remain outside T5's all-pure quality claim. | Manuscript `:117-127`, `366-367`; dual protocol `:28-57`; certificate scope `:32457-32464`. |
| A8. High effort cost `c=1/20`, with no Low effort cost. | Converts information value into net reward and the exact `7/500` gap. Essential to T3. | Cost includes time, access and disutility only through one scalar. It is not measured. | Different cost heterogeneity can eliminate effort or change which action is optimal. | `CEAV_M1_MANUSCRIPT_V0_2.md:124-127`, `256-265`; config `:6`. |
| A9. `H01` reports raw `X_i`; binary match is modal-label reporting. | Specifies what “truthful” means in this game. Essential to the report-payoff calculation. | This is not a proper probability report and cannot be assumed to elicit all information types. | A domain with graded quality or multi-valued evidence needs a different report space or scoring rule. | `CEAV_M1_MANUSCRIPT_V0_2.md:124-127`, `264-265`; readiness `:36-40`. |
| A10. Expected utility is linear in rewards, effort cost and task-local release probability: `E[R_i]-c_i+b_i P(D_final=1)`. | Assumes risk neutrality/quasilinear units; makes deviations affine in constant `b_i`. Essential to T4/T5. | Financial, relational or reputational interests fit only if represented by this payoff. `b_i` is neither measured nor enforced and is not a percentage of escrow value. | Risk aversion, state-dependent exposure, nonlinear interests or history-dependent side payments can change best responses. | Manuscript `:178-185`; empirical protocol `:282-298`; gap assessment `:28-58`. |
| A11. `A_pay~Bernoulli(2/5)` is independent of information, reports, peers and future `T`; only this event pays the bonus. | Removes the direct report-to-payment-eligibility channel and yields `E[R|I,r]=f+mu*a*P(T=r|I)`. Essential to T3a and the dual architecture. | This is a protocol choice, not a domain property. It does not prevent a report from changing expected match payment or decision utility. | If eligibility depends on reports or is revealed early, T3a no longer applies and T1's audit-seeking channel can return. | `CEAV_M1_MANUSCRIPT_V0_2.md:149-176`, `230-265`; catalog `:39-48`, `196-224`. |
| A12. `A_dec` is independent of `A_pay`, selective only on `S={Z=0,sum(r)=2}`, or uniform with `d=19/1250`; one union audit is charged. | Defines exposure `a+(1-a)d` and the selective/uniform comparison. Essential to T3b and the budget rows. | Risk targeting can be domain-specific because the report class may not predict risk outside calibration. | Different risk distribution, double charging or a report-dependent payment channel changes loss, cash and exposure. | `CEAV_M1_MANUSCRIPT_V0_2.md:157-175`; config `:7-12`; report `:221-252`. |
| A13. Frozen H01 calibration and fixed off-equilibrium `g0/g1`; release threshold posterior odds `>=2`. | Defines the final decision for every actual strategy, including deviations. Essential to all T4/T5 witnesses. | Calibration is tied to the synthetic fixture and not re-estimated after deviations or domain shift. | Recalibration is a different game; using a table outside its population can invalidate quality gates. | `CEAV_M1_MANUSCRIPT_V0_2.md:129-147`; report `:32-55`; gap assessment `:83`. |
| A14. Prior-weighted metrics and asymmetric gates: `FA<=1/5`, `FR<=1/4`, wrong payout `<=3/20`, loss uses `C_FA=2,C_FR=1`. | Defines what “quality” and “bad equilibrium” mean. Essential to T3b/T5 gate verdicts. | Conditional FA/FR transfer more readily than prior-weighted loss; gate values are application-specific policy choices. | Different payout value, class prevalence, risk tolerance or loss weights can reverse a domain comparison without refuting the theorem. | `CEAV_M1_MANUSCRIPT_V0_2.md:191-226`; config `:8-12`. |
| A15. Budget and resource assumptions: `B=6`, `mu=2`, `kappa=1/4`, operating cost `0`, exposure `<=1/2`, reward reserve `<=6`, expected cash `<=4`. | Establishes the feasibility gates and reserve/cash certificate. Essential to the budget claim, not to the algebraic factorization alone. | These are normalized research units, not a token, currency or observed settlement budget. | Real audit travel, latency, payment fees or payout scale can make a mathematically feasible point unaffordable. | `CEAV_M1_MANUSCRIPT_V0_2.md:217-226`; config `:7-12`; report `:247-252`. |
| A16. Three distinct Judges, fixed peer strategies, unilateral task-local deviations and no coalitions/Sybils/entry choice. | Defines best responses and the pure equilibrium concept. Essential to T4/T5 completeness. | This is not an identity or participation guarantee for a decentralized protocol. | Sybil control, collusion, correlated identities, nonparticipation or coalition deviations produce a different game. | `CEAV_M1_MANUSCRIPT_V0_2.md:117-127`, `366-367`; certificate scope `:32457-32464`; limitations `:3-13`. |
| A17. Positive branch probabilities and independent branch-local choices. | Allows full equilibria to be formed from overlapping branch intervals and supports the `216^2` product enumeration. Essential to T5. | A real workflow may couple decisions across milestones, reputation, repeated interaction or learning. | Cross-branch history or reputation can invalidate the branch-product completeness argument. | `CEAV_M1_THEOREM_AND_COUNTEREXAMPLE_CATALOG.md:429-445`; report `:117-149`. |
| A18. Creator evidence and information-generation law are exogenous. | The game evaluates a fixed joint distribution; it does not solve creator strategy or adversarial evidence generation. Essential to interpreting the certificate as a fixed-distribution result. | Strongly domain-dependent: staged photos, common repositories, supplier records and recipient access can all be strategic. | `P(Z,X,T|Y)` may change after policy publication; current quality and incentive results do not provide an adversarial creator guarantee. | `CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md:45-55`, `138-164`; gap assessment `:78-83`. |
| A19. Exact rational arithmetic and pinned source identity. | Establishes reproducibility of the finite calculation, not truth of the assumptions. | Domain-neutral evidence practice. It is already verified. | A hash mismatch or missing source invalidates reproduction; a matching hash does not validate the real-world model. | `review-package/CLAIM_EVIDENCE_MAP.md:22-28`; certificate `:32457-32468`. |
| A20. The likelihoods, published rule and payoff model used in best responses are the players' operative beliefs; no learning or ambiguity model. | Expected utility and Nash comparisons use one specified distribution, not heterogeneous subjective beliefs. Essential to that strategic interpretation. | Unmeasured; a referee can inspect the stipulated game, but this is not evidence that reviewers know or believe it. | Miscalibration, ambiguity, richer private knowledge or adaptive learning breaks direct behavioral interpretation. | Manuscript `:112-127`, `230-254`; known limitations `:5-15`; evaluator `verification/dual_boundary.py:58-86`. |
| A21. Participation and payment availability are assumed; no opt-out action, funding shortfall or reward default. | A fixed set of three Judges maximizes utility over the six actions. No individual-rationality or payment-enforcement theorem is supplied. | A proposed field study records refusal and outside work, but has no observations. | Outside options or unpaid bonuses can remove participation and the effort incentive. | Manuscript `:117-127`, `172-185`; empirical protocol `:275-298`; known limitations `:10-13`, `21-28`. |
| A22. Funding/escrow ownership and actual settlement are outside the game; payout is a fixed loss exposure `V=1`. | `cash` accounts for reviewer rewards plus one union audit cost and operating cost; wrong payout is a separate metric. Essential to interpreting budget feasibility correctly. | No fundraising, ledger, source of reserve, contract authorization, refunds or settlement reliability is evidenced. | The cash/reserve gates cannot establish solvency of a real escrow, who may move funds, recovery after failed transfer, or prevention of duplicate release. | Config `:8-12`; manuscript `:199-226`; `verification/dual_boundary.py:82-88`; known limitations `:27-28`; empirical protocol `:310-317`. |

These dependencies differ by result. T3a's factorization needs the payment
coin independent jointly of reporting information and future `T`; mutual
conditional independence of all information channels is not necessary for
that identity. The stronger signal assumptions are needed for the frozen
`Delta`, H01 optimality, calibration and numerical boundaries. Proposition 1
should explicitly restate independence from `T` when quoted alone; the full
model already supplies it (`CEAV_M1_MANUSCRIPT_V0_2.md:151-158,232-250`;
catalog `:196-231`). Likewise, a reserve/cash gate is an accounting statement
for review/audit spending, not a proof about escrow ownership or settlement.

## 3. Domain applicability matrix

The mappings below are candidate operationalizations, not empirical findings.
No accuracy, independence or cost number is assigned to a domain. The same
mathematical structure is usable only when a campaign owner can preregister a
binary acceptance predicate and collect the required signals under the frozen
timing and audit conditions.

| Campaign type | Candidate `Y` | Candidate `Z`, `X_i`, `T` | Independence and strategic risks | Transfer assessment |
|---|---|---|---|---|
| **Software and open-source development** | A preregistered release commit passes reproducible build, test, security and interface predicates. Subjective “quality” should not be folded into `Y` without a separate rubric. | `Z`: public CI, demo and repository evidence. `X_i`: private clone/build, test, dependency or security checks. `T`: independently reproducible build and locked acceptance audit. | Reviewers may share the same repository evidence, depend on the same CI, or have maintainer/competitor interests. A maintainer can strategically curate public evidence. | **CONDITIONAL.** The binary structure can transfer for a fixed release snapshot. Signal correlation, security depth, reviewer effort and audit latency require measurement; numerical T3–T5 values do not transfer automatically. |
| **Creative projects and game development** | Objective deliverable predicates such as a build runs, specified assets exist, licensed files are present and the milestone package matches the contract. Audience appeal or artistic merit is not automatically binary ground truth. | `Z`: public build, trailer or asset manifest. `X_i`: private playtest, asset/provenance or platform checks. `T`: independent build/artifact inspection under a locked checklist. | Fan communities, publishers, creators and competitors can share evidence or have strong release preferences. Subjective evaluations create label disagreement and correlated reports. | **CONDITIONAL / GAP.** Apply only to observable contractual deliverables. A quality or audience-impact claim needs a different `Y`, signal model and loss function. |
| **Hardware and product development** | At a declared time, the specified unit count, identity, dimensions, tolerances and operational checks pass. This resembles the physical snapshot protocol. | `Z`: photos, tracking, invoice and claimed receipt. `X_i`: fresh inventory challenge, live recipient contact and measurements. `T`: independent site inspection of the whole batch. | Supplier, creator and recipient may collude; travel and inspection access create cost and latency; temporary placement can satisfy presence without proving ownership or durability. | **CONDITIONAL.** The school-desk protocol supplies a concrete measurement design for one narrow physical claim. There is no empirical comparison establishing that hardware is a better fit than the other domains, or that `9/10` holds. |
| **Community and charitable projects** | A concrete distribution or construction milestone can be binary, such as all registered items delivered and checklist predicates passing. Beneficiary welfare, long-term impact and “community satisfaction” need separate constructs. | `Z`: public report, photos, inventory and claimed recipient receipt. `X_i`: independent recipient contact or item-level inventory. `T`: independent site census or inspection. | Privacy, safeguarding, restricted access, donor/creator relationships, beneficiary dependence and common evidence can make independence or audit access difficult. | **CONDITIONAL.** Charity is one application, not the model definition. The model transfers to observable milestones; it does not establish impact, beneficiary welfare or donor protection. |

The domain matrix supports a general-purpose scope with a narrow application
condition: the campaign must make the milestone observable and contractually
testable. The school-desk study explicitly says it does not establish other
milestone categories or educational impact (`CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md:14-19`).
These are operationalization proposals inferred from the declared variables,
not observations from the four industries. The mathematical structure can
remain unchanged for a binary deliverable with the stipulated information and
payoff structure. Richer subjective outcomes, endogenous evidence or different
information structures would require a separately justified application model;
the present audit does not create one. In particular, running software tests
cannot establish absence of all security defects, just as inspecting a batch
at one time cannot establish lifetime product quality.

## 4. T3–T5 mathematical and external-validity assessment

Legend: **M** = mathematical validity under the declared assumptions; **P** =
portability of the numerical parameters; **A** = applicability to a real
campaign; **G** = generality of the result; **E** = missing external evidence.

| Result | M | P | A | G | E | Classification and evidence |
|---|---|---|---|---|---|---|
| **T3a: payment factorization and effort threshold** | **PASS under the full model.** Joint independence from reporting information and `T` gives `E[R|I,r]=f+mu*a*P(T=r|I)`; best High beats best Low iff `mu*a*Delta>c`. | **CONDITIONAL.** The identity is structural; `Delta=2/25`, `c=1/20`, H01 optimality and gap `7/500` are fixture-specific. | **CONDITIONAL.** Requires hidden lottery timing and its stated independence. The effort conclusion also uses the specified risk-neutral utility, beliefs and available actions. | **Algebraic class result.** Not a general probabilistic-truthfulness theorem; no need to assume mutual conditional independence just for the identity. | **GAP.** No measured information value or reviewer cost. | Manuscript `:151-158`, `230-265`; catalog `:194-231`. |
| **T3b: conditional neutral feasibility and selective-versus-uniform comparison** | **PASS.** The analytic region `5/16<a<1/2`, `0<t<=(1/2-a)/(1-a)` and the gate/loss inequalities are proved for F51-02, fixed tables and neutral Judges. | **No.** The exact region and values depend on F51-02, losses, gates, calibration and risk class. | **CONDITIONAL.** Requires the same distributions, fixed calibration, independent lotteries, trusted `T`, no outside options and the declared action class. | **Limited but more than a grid.** It is an analytic region for one fixed primary environment, not a theorem over campaign domains or reward policies. | **GAP.** No domain has measured equal exposure, audit value or cost. The equal-exposure loss comparison is conditional on the same report distribution. | `CEAV_M1_MANUSCRIPT_V0_2.md:267-296`; catalog `:233-333`; novelty audit `:184-205`. |
| **T4: local external-interest boundary** | **PASS for the theorem endpoints and calculation; FAIL for the two printed proof signs (F1).** Exact deviations yield Selective `(-70/633,175/1102)` and Uniform `(-218750/2070709,218750/1365587)`. | **CONDITIONAL.** Same game gives same endpoints; no evidence transports that game to another campaign population. | **CONDITIONAL.** Stable linear `b_i`, frozen H01 peers and calibration; no enforcement of the interval. | **Finite local result, including heterogeneous vectors.** Each coordinate may differ inside its interval. This does not prove an exact global boundary over heterogeneous `R^3`. | **GAP.** No empirical distribution or measurement of `b_i`. | Manuscript `:298-326`; catalog `:335-401`; fresh `independent.stdout.txt` and focused-suite logs in the audit evidence directory. |
| **T5: exact pure-equilibrium quality boundary** | **PASS.** The certificate checks all `216^2` branch-profile pairs, all declared scenarios and ties; the status is `VERIFIED_IN_DECLARED_PURE_CLASS`. | **No.** The safe components and bad-witness metrics are specific to the frozen mechanism and gates. | **CONDITIONAL.** Requires stationary pure branch actions, task-local deviations, positive branch probabilities and the five declared preference vectors. | **Exact but narrow.** It covers the declared pure class and scenarios; it does not cover mixed, sequential, coalition, Sybil, participation or arbitrary `b in R^3`. | **GAP.** No field equilibrium observation or evidence that the declared class captures actual reviewer behavior. | `CEAV_M1_MANUSCRIPT_V0_2.md:328-367`; certificate `:32457-32468`; report `:117-219`. |

The T3–T5 claims therefore have the following interpretation:

1. T3 is an exact conditional incentive and feasibility result. It does not
   prove that a real reviewer acquires useful information or reports a
   probability truthfully.
2. T4 is a local sensitivity calculation. `|b_i|<7/500` is a sufficient
   analytical trust assumption in the parent analysis, not an identity,
   screening or payment enforcement mechanism (`CEAV_M1_THEOREM_AND_COUNTEREXAMPLE_CATALOG.md:376-386`).
3. T5 is the strongest finite result: it separates local All-H01 stability
   from all-equilibrium quality, and at `b=1/10` gives three strict bad
   witnesses alongside strict All-H01. It is not a global theorem over all
   strategic behaviors.

The boundary analyzer is deliberately a fixed-fixture checker: its conditional
weights, half-weight aggregation and reserve six rely on the frozen inputs
(`verification/dual_boundary.py:57-65,158-165`; independent oracle
`verification/dual_boundary_oracle.py:35-58`). Editing a JSON accuracy or prior
alone is not a verified domain-calibration workflow. Any future application
needs a justified model and fresh evidence; this audit changes neither.

## 5. Unsupported or overstated claims

### Confirmed errors and evidence wording to repair

| ID | Classification and exact location | Evidence and impact | Minimum correction |
|---|---|---|---|
| **F1** | **FAIL — mathematical transcription in a proof.** Manuscript `:308-313`; packaged manuscript same lines. | The displayed expressions are `U(deviation)-U(H01)`, but both use `>=0` for stability. At `b_i=0`, each equals `-7/500`. Taken literally the rows require simultaneously `b_i<=-70/633` and `b_i>=175/1102`, an empty intersection. Catalog `:358-374` correctly uses `<=0`; analyzer `verification/dual_boundary.py:97-106,127-150` uses consistent signs. Fresh interval replay agrees with the catalog. | Change both displayed conditions to `<=0` for weak stability, and say `<0` in the strict interior. Identify the direction of the utility difference. Do this in a subsequent editable revision of both manuscript copies; preserve frozen evidence. |
| **F2** | **FAIL — bibliographic attribution.** Manuscript `:515-529`; packaged manuscript same lines. | Entry 4 wrongly names Gao as “Siyu”; the primary byline is Xi Alice Gao. Entries 6 and 7 wrongly name Kong as “Yiling”; the author is Yuqing Kong. Entry 6 names Ligett as “Jennifer”; the author is Katrina Ligett. Primary sources below establish these corrections. This does not refute the cited results, but the draft is not bibliographically clean. | Correct the three entries and synchronize the editable package copy. The earlier bibliography check covers other entries (`CEAV_M1_BIBLIOGRAPHY_PRIMARY_CHECK.md:7-36`); it is not validation of these names. |
| **F3** | **FAIL — inaccurate explanation of T5.** External brief `:63`; packaged brief `:63`. | “Global deviations can coordinate through equilibrium profiles” misdescribes an analysis of unilateral best responses. The proof checks `base-deviation>=0` separately for each Judge (`verification/dual_boundary.py:127-134`; manuscript `:330-352`). Multiple bad equilibria need neither a modeled coordination process nor a profitable coalition deviation. The brief already excludes coalitions in `:77-79`; do not mislabel this as a coalition-proofness claim. | Say “additional bad pure equilibrium profiles become sustainable before All-H01 loses local stability.” The equilibrium counts and boundaries are unchanged. |
| **F4** | **CONDITIONAL — architecture ambiguity.** Manuscript abstract `:22-24`; packaged manuscript same lines. | The sentence attributes observation of `T` for the final decision to the risk lottery. Actually, a payment-only audit also informs the final decision: `g1` is used on `A_pay OR A_dec` (catalog `:67-70`; analyzer `:68-74`). The full model `:165-169` correctly describes the union. | Call `A_dec` an additional opportunity for decision verification and state that either event supplies the common `T` for the final decision. |
| **F5** | **GAP — precision of verification attribution.** Manuscript `:318-320`; proof-review runner `verification/independent_t3_t5_review.py:64-92`; metric checker `verification/manuscript_editorial_audit.py:25-33`. | The T4 subsection divides hardcoded binding intercepts/slopes; it does not derive those rows from primitive signals. Its T5 call separately invokes the broad independent audit. Combined oracle comparisons and focused tests support the arithmetic, but the named T4 subsection and the certificate metric checker alone do not verify proof text. F1 survives a green metric audit. | Attribute primitive arithmetic to the independent oracle/table comparison and DB01–DB03 tests; describe the runner's T4 subsection as checking supplied rows. Avoid treating a numerical checker as a prose-proof checker. No new analyzer is needed. |

Primary attribution checks, accessed for this audit on 2026-10-25:

- Gao et al., [accepted manuscript](https://dspacemainprd01.lib.uwaterloo.ca/server/api/core/bitstreams/2cf2eab2-324c-402f-98eb-ee05f2a446f4/content), PDF cover and article title page: Xi Alice Gao, James R. Wright, Kevin Leyton-Brown.
- Kong et al., [author-hosted paper page](https://mail.schoeneb.people.si.umich.edu/papers/PeerFocal.html), byline: Yuqing Kong, Katrina Ligett, Grant Schoenebeck.
- Kong and Schoenebeck, [ITCS primary article](https://drops.dagstuhl.de/storage/00lipics/lipics-vol094-itcs2018/LIPIcs.ITCS.2018.13/LIPIcs.ITCS.2018.13.pdf), title page: Yuqing Kong and Grant Schoenebeck.

The focused novelty boundary remains appropriate: report-sensitive checking
already appears in [Zarkoob et al., abstract](https://www.ifaamas.org/Proceedings/aamas2020/pdfs/p1593.pdf),
and decision-interested experts already appear in
[Boutilier, abstract](https://www.cs.toronto.edu/~cebly/Papers/Boutilier_aamas12.pdf).
These sources support adjacent prior art, not priority for CEAV's exact
combination. No new systematic literature review was completed here.

The independent [mathematical note](reviews/domain-dependence-audit-20261025-math.md)
documents the direct neutral-region derivation and boundary cross-checks;
the [claims note](reviews/domain-dependence-audit-20261025-claims.md) documents
domain and primary-source checks. They are agent audit notes, not external
human referee reports.

### Claim boundaries checked without finding a corresponding false claim

The following rows separate existing scope discipline from potential reader
overinterpretation. They are not additional discovered mathematical errors.

| ID | Finding | Classification | Exact evidence | Required disposition |
|---|---|---|---|---|
| C1 | The research documents motivate “escrow-like crowdfunding” but do not state in one sentence that FundTogether is general-purpose and that charity is only one application. | **GAP (editorial)** | Brief `:6-18`; manuscript `:14-20`, `44-52`; paper readiness `:138-142`. | Add the scope sentence to the introduction/brief. Do not change the game or reframe the school-desk measurement as a universal domain. |
| C2 | A reader could mistake the school-desk protocol for the product definition or for evidence about charity-wide outcomes. | **CONDITIONAL (editorial)** | Protocol `:12-19`, `31-39`, `83-92`. | Label it “one physical-evidence exemplar for protocol validation”; retain the explicit exclusions of educational impact and other milestones. |
| C3 | “Trusted audit” could be read as an incorruptible oracle outside the mathematical model. | **GAP (terminology)** | Model uses noisy `T` and synthetic accuracy (`CEAV_M1_MANUSCRIPT_V0_2.md:112-115`); protocol lists capture and dependence risks (`CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md:138-164`). | Define trusted as an exogenous audited channel in the model, with empirical reliability and capture left open. |
| C4 | “Truthful” can be overread as proper probabilistic truthfulness. | **CONDITIONAL** | H01 is raw-X reporting and binary match is modal-label incentive (`CEAV_M1_MANUSCRIPT_V0_2.md:124-127`, `256-265`; readiness `:36-40`). | Use “truthful raw-label reporting under H01” or “modal-label H01” near T3 headlines. |
| C5 | “Decentralized” could be read as a proved protocol property even though identity, Sybil, collusion, settlement and liveness are outside the game. | **PASS for current claims; editorial GAP for scope clarity** | Manuscript disclaims Sybil/production readiness (`:33-40`); catalog excludes Sybil/participation and permissionless ground truth (`:492-498`); limitations `:17-28`. | State that the paper studies an incentive layer motivated by a decentralized crowdfunding protocol; it proves no decentralized identity or settlement guarantee. |
| C6 | Selective auditing could be read as universally better than Uniform. | **PASS under current wording** | The catalog conditions the comparison on the same report distribution (`:267-289`); novelty audit explicitly says the inequality is instance-specific (`:184-205`). | Preserve the condition in every summary table and avoid extrapolating to strategic profiles with changed report frequencies. |
| C7 | T4 local stability could be read as global robustness. | **PASS under current wording** | Manuscript `:323-326`; T5 counterexample `:354-367`; report `:3-8`, `:293-298`. | Keep “local” in the theorem title and pair it with the T5 `b=1/10` witness. |
| C8 | The novelty claim could be overstated as firstness. | **PASS under current wording; GAP for future submission** | Manuscript `:100-106`; novelty audit `:17-45`, `:326-342`; limitations `:30-38`. | Retain “candidate/instance-level contribution”; complete broader priority screening before submission. |
| C9 | Synthetic signal or audit accuracy could be read as empirical effectiveness. | **PASS** | Manuscript `:112-115`; brief `:75-80`; protocol status `:1-10`, `:336-339`. | No mathematical correction is needed. Keep the “no observations collected” status adjacent to future empirical claims. |
| C10 | Reviewer equilibrium results could be read as creator, donor or escrow-settlement guarantees. | **PASS with editorial reinforcement** | The game specifies reviewer utility and decision gates (`CEAV_M1_MANUSCRIPT_V0_2.md:178-185`, `328-367`); real ownership, recovery and finality are excluded (`CEAV_M1_PAPER_READINESS.md:138-142`). | Add one explicit sentence that creator strategy, donor welfare, contract execution, failure recovery and finality are outside CEAV-M1. |

There is no detected logical inconsistency caused by a charity-specific
definition. F1–F3 are genuine document errors independent of charity versus
general-purpose scope. The concrete school-desk protocol is domain-specific
and already explicitly limits its scope; that limitation does not make the
game charity-specific.

## 6. Critical research gaps

These gaps prevent direct real-world adoption claims; they do not invalidate
the finite proofs.

1. **Contractual ground truth.** Each campaign type needs a stable, observable
   acceptance predicate for `Y`. Subjective impact, ownership, durability and
   beneficiary welfare cannot be silently substituted for the snapshot claim
   used by the physical protocol (`CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md:41-55`,
   `83-90`).
2. **Signal calibration and dependence.** `Z`, `X_i` and `T` require held-out
   sensitivity/specificity, defect-stratified error tables and joint-error
   analysis. Separate reviewers or channels do not prove conditional
   independence (`CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md:94-136`, `138-164`).
3. **Audit integrity.** Auditor capture, collusion, strategic evidence and
   shared provenance can make `T` strategy-dependent. The current controls are
   proposed study controls, not mechanism enforcement (`CEAV_M1_RESEARCH_GAP_ASSESSMENT.md:72-83`).
4. **Effort and economics.** The scalar `c=1/20`, audit cost `kappa=1/4`,
   reward scale and reserve are normalized. Participation, refusal, delay,
   training, workload and actual all-in cost are not measured (`CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md:264-304`).
5. **External interests.** `b_i` is not observable from a conflict declaration
   and is not bounded by the mechanism. Hidden holdings, side payments and
   reputational interests remain outside the model (`CEAV_M1_RESEARCH_GAP_ASSESSMENT.md:28-58`).
6. **Creator and evidence strategy.** A creator can select, stage, reuse or
   alter evidence after learning the policy. No adversarial distribution or
   creator equilibrium is proved (`CEAV_M1_RESEARCH_GAP_ASSESSMENT.md:78-83`).
7. **Temporal and settlement behavior.** The model has no timeout, retry,
   appeal, unavailable-audit, rework or liveness mechanism; `Y` can change
   between observations (`CEAV_M1_RESEARCH_GAP_ASSESSMENT.md:80-83`).
8. **Strategic scope.** Mixed, correlated, coalition-proof, sequential,
   Sybil, participation and arbitrary heterogeneous-`b` analyses remain open
   (`review-package/KNOWN_LIMITATIONS.md:3-15`; certificate scope
   `:32457-32464`).
9. **Domain-specific loss and prevalence.** The conditional FA/FR definitions
   are portable, but prior-weighted loss, payout value and gate thresholds need
   a campaign policy. Changing them changes the application question even when
   the signal model is unchanged (`CEAV_M1_MANUSCRIPT_V0_2.md:191-226`).

The first-order research transfer gap is therefore the joint information and
incentive model, not merely a missing blockchain integration. Even perfect
settlement code would not establish independent signals, bound `b_i`, remove
T5's bad equilibria or make subjective impact a measured binary deliverable.
Conversely, the absence of a production settlement design is not an error in
a paper that explicitly excludes one (`review-package/KNOWN_LIMITATIONS.md:17-28`).

## 7. Minimum editorial corrections needed

No engine or certificate correction is indicated by the reproduced results.
The following edits are proposed, not applied in this audit. Repair the actual
errors before describing the draft as clean; then add the scope clarifications
in the same small editorial pass:

1. **Required proof repair:** fix both T4 signs as derived in F1, in the root
   manuscript and editable review-package copy. Keep the correct endpoints.
2. **Required attribution repair:** correct Xi Alice Gao, Yuqing Kong and
   Katrina Ligett in bibliography entries 4, 6 and 7 (F2).
3. **Required explanation repair:** replace coordinated-deviation language
   with coexistence of bad unilateral Nash equilibria (F3). Clarify the union
   observation rule in the abstract and the verification attribution (F4–F5).
4. In the manuscript introduction and research brief, state explicitly:
   “FundTogether is a general-purpose decentralized crowdfunding protocol;
   CEAV-M1 abstracts one observable escrow milestone, and charity is only one
   possible application.”
5. Label the school-desk protocol as a **concrete physical-evidence
   exemplar**, not a representative sample of all FundTogether campaigns.
6. Define “trusted audit” as a noisy, externally supplied model signal whose
   provenance, independence and capture resistance are empirical questions.
7. Replace unqualified “truthful” in overview prose with “truthful raw-label
   H01 reporting” where the statement refers to T3.
8. Keep the qualifiers “fixed,” “declared pure stationary class,” “synthetic”
   and “candidate instance-level contribution” next to the corresponding
   numerical or novelty claims.
9. Add one sentence separating reviewer-game results from creator strategy,
   donor welfare, blockchain execution, settlement finality and liveness.

F1 is a mathematical correction to the written proof, rather than a cosmetic
style edit. It is local and does not require revising the game or its verified
results. F2–F5 concern attribution, explanation and evidence precision. None
requires parameter retuning, a new mechanism or alteration of historical
artifacts. If the package is revised later, label it as a new editable revision
instead of rewriting a frozen snapshot.

## 8. Final recommendation

**Recommendation: NARROW the application claims while RETAINING the existing
mathematical model and certificates.** Do not fundamentally revise CEAV-M1 for
charity/general-purpose scope. The model is sufficiently domain-agnostic to
support a class of crowdfunding milestones, but only conditionally: the
milestone must admit a defensible binary acceptance predicate and the campaign
must supply empirical evidence for the signal, audit, cost, timing and utility
assumptions.

The research remains appropriate for **external academic review as a
conditional theory/counterexample case study**. The current manuscript should
first receive the small proof and editorial repairs in §7, or be sent with an
explicit errata sheet. It should not be presented as a clean, error-free draft.
It is not ready to claim field validity, production
readiness, universal decentralized guarantees or broad novelty. This conclusion
is consistent with the paper-readiness decision (`CEAV_M1_PAPER_READINESS.md:8-12`),
the novelty boundary (`CEAV_M1_NOVELTY_AUDIT_T3_T5.md:338-344`) and the frozen
certificate status (`results/dual-strategic-boundary-20261024T0524070523492Z/analysis/certificate.json:32457-32468`).

### Required final answers

1. **Do T3–T5 remain mathematically valid?** Their stated results and exact
   boundaries reproduce under the declared assumptions; no foundational
   counterexample was found. The printed T4 proof has a confirmed sign error
   (F1) and must be corrected. Identical mathematical inputs give identical
   numbers across domain labels, but that identity is not field evidence.
2. **Does general-purpose FundTogether scope require material model changes?**
   No for the research model; yes for application mapping and empirical
   validation. The correct action is editorial narrowing, not V7 or a new
   mechanism.
3. **What prevents direct adoption?** Objective `Y`, calibrated and
   conditionally independent `Z/X/T`, audit integrity, measured effort/cost,
   bounded external interests, creator/evidence strategy, participation and
   settlement liveness.
4. **Which findings are editorial versus mathematical?** F1 is an actual
   mathematical transcription error in the proof, without a detected error in
   the theorem or certificate. F2–F3 are actual attribution/explanation errors;
   F4–F5 require clarification. Domain transfer, trust and settlement are
   empirical/strategic/implementation gaps, not proof refutations.
5. **Is the manuscript appropriate for external academic review?** Yes, after
   these local repairs or with explicit errata, as a conditional theory and
   negative-equilibrium case study. Keep CEAV-M1 and seek expert criticism;
   no new model version or fundamental rebuild is justified by this audit.
