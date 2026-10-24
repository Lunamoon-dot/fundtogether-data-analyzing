# CEAV-M1 — Domain Dependence & Generality Audit

**Repository:** `Lunamoon-dot/fundtogether-data-analyzing`  
**Branch:** `research/v6-rave-phase01`  
**Audit status:** completed against the tracked research artifacts; no frozen
certificate, parameter, mechanism or production contract was changed.

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
| The numbers are portable across campaign domains. | **GAP** | The proof fixes `P(Y)`, signal accuracies, conditional independence, effort cost, audit cost, calibration, losses and gates. Those values are synthetic inputs, not measurements (`CEAV_M1_MANUSCRIPT_V0_2.md:112-115`; `CEAV_M1_DUAL_STRATEGIC_BOUNDARY_REPORT.md:20-30`). A different domain may instantiate the same structure but will not inherit `7/500`, the `b` endpoints, or the T5 safe component without new inputs and analysis. |
| The current results can be applied directly to a live campaign. | **CONDITIONAL** | Direct application requires an objectively labelable milestone, a mapping from public/private evidence to the signal variables, a defensible operational `T`, the stated timing and independence conditions, and a utility/cost scale compatible with the game. None has been measured (`CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md:1-10`, `41-55`, `336-339`). |
| The trusted audit is a trustless oracle. | **GAP** if read that way; **PASS** under the declared model | `T` is a noisy exogenous signal with accuracy `9/10`, and the manuscript explicitly calls accuracies synthetic (`CEAV_M1_MANUSCRIPT_V0_2.md:112-115`; theorem catalog `:32-37`). The empirical protocol separately warns that independence, capture and joint errors are unmeasured (`CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md:138-164`). |
| Local truthful stability implies safe settlement in every equilibrium. | **FAIL** as a proposed implication; **PASS** as a rejected claim | T4 is explicitly local with frozen H01 peers. T5 gives three bad strict equilibria at `b=1/10` while All-H01 remains strict (`CEAV_M1_MANUSCRIPT_V0_2.md:298-367`; `CEAV_M1_DUAL_STRATEGIC_BOUNDARY_REPORT.md:181-219`). The manuscript does not make the invalid implication. |
| The documents make unsupported charity, decentralization or production claims. | **PASS** for the current wording; **CONDITIONAL** editorially | The manuscript disclaims universal impossibility, empirical audit accuracy, Sybil resistance and production readiness (`CEAV_M1_MANUSCRIPT_V0_2.md:33-40`). A one-sentence general-purpose scope statement and an explicit “school-desk protocol is an exemplar” sentence would reduce reader ambiguity; see §7. |

**Answer to the central question.** T3, T4 and T5 remain mathematically valid
under their originally declared assumptions. The general-purpose FundTogether
scope does not require a new mechanism or a change to the frozen research
model. It does require narrowing application claims: CEAV-M1 is a conditional
verification case study for milestones that can be represented by the stated
binary and signal model.

No **FAIL** finding concerns the declared proofs or the immutable certificate.
The blockers for real-world adoption are empirical and operational: ground
truth definition, signal calibration, audit independence and capture, effort
and participation economics, external release interests, creator evidence
strategy, and settlement timing/liveness.

## 2. Complete assumption inventory

The inventory distinguishes a mathematical assumption from a domain condition.
“Essential” means that removing the assumption invalidates the cited proof or
changes the game; it does not mean that the assumption is true in practice.

| ID / assumption | Mathematical role and essentiality | Domain dependence and support | Consequence if violated | Evidence |
|---|---|---|---|---|
| A1. Binary ground truth `Y` and prior `P(Y=1)=1/2`. | Defines the state, likelihoods, conditional FA/FR and prior-weighted loss. Essential to the numeric certificate and calibration. | The binary abstraction is domain-neutral, but every real campaign needs a preregistered acceptance predicate. No field label exists. | Ambiguous or time-varying `Y` makes signal accuracy, decision loss and wrong-payout calculations refer to the wrong target. | `CEAV_M1_MANUSCRIPT_V0_2.md:112-115`, `191-215`; empirical protocol `:41-55`, `:83-90`. |
| A2. Public signal `Z` has accuracy `7/10` and two positive-probability branches. | Determines branch posteriors and the frozen `g0/g1` tables. Essential to T3b–T5 values. | A public dossier is plausible in many domains, but its quality and prevalence are domain-specific and unmeasured. | Different prevalence or public evidence changes calibration, risk-class frequency and all reported fractions. | `CEAV_M1_MANUSCRIPT_V0_2.md:112-115`, `129-147`; config `:5`, `14-15`. |
| A3. Each private signal `X_i` has accuracy `4/5`; Low sees no `X_i`; High pays cost and observes it. | Creates `M_L`, `M_H`, `Delta=2/25` and the effort threshold. Essential to Proposition 1/2. | A private information-acquisition workflow can exist for software, hardware or physical delivery, but `4/5` and homogeneous costs are not empirical. | If High does not improve the modal label, `Delta` may be zero; if information is correlated, the equilibrium and value calculations change. | `CEAV_M1_MANUSCRIPT_V0_2.md:117-127`, `230-265`; catalog `:194-231`. |
| A4. Trusted audit `T` has accuracy `9/10`, is common to all Judges, and is observed when either lottery fires. | Supplies the matching reward and decision update. Essential to reward, exposure and decision-loss calculations. | “Trusted” means a specified audit channel, not infallible truth or capture resistance. No sensitivity/specificity data exist. | Biased, captured, unavailable or differently routed `T` changes both incentives and final decisions. | `CEAV_M1_MANUSCRIPT_V0_2.md:112-115`, `151-176`; certificate `:12-18`, `81-90`; protocol `:94-136`, `138-164`. |
| A5. Conditional independence of `Z`, all `X_i` and `T` given `Y`. | Enables Bayes calibration, factorized enumeration and the independent oracle. Essential to the stated numerical results. | It is a strong empirical restriction. Separate people or channels do not prove it; common evidence can induce correlated errors. | Correlation can make three reports no more informative than one and can create joint false approvals even when marginal accuracy looks high. | `CEAV_M1_THEOREM_AND_COUNTEREXAMPLE_CATALOG.md:32-37`; protocol `:138-164`; gap assessment `:75-79`, `97-101`. |
| A6. Reports lock before hidden lotteries; `T` arrives before the final decision on the same claim. | Makes report-independent `A_pay` factorization and union accounting well-defined. Essential to T3 and the boundary certificate. | Timing depends on evidence access, travel and settlement latency. It is not measured. | Revealed lotteries, late audits or changing milestones create a different information game and may change incentives or make settlement unavailable. | `CEAV_M1_MANUSCRIPT_V0_2.md:149-181`; report `:20-26`; gap assessment `:80-83`. |
| A7. Six branch-local actions `{L0,L1,H00,H01,H10,H11}` and stationary strategies. | Defines the action space and the `6^3` branch enumeration. Essential to the exact T4/T5 scope. | It is an abstraction, not a claim that real reviewers have only six actions. | Omitted strategies such as abstention, delay, partial inspection, mixed actions or evidence manipulation can add equilibria or deviations. | `CEAV_M1_MANUSCRIPT_V0_2.md:117-127`; certificate scope `:32457-32464`. |
| A8. High effort cost `c=1/20`, with no Low effort cost. | Converts information value into net reward and the exact `7/500` gap. Essential to T3. | Cost includes time, access and disutility only through one scalar. It is not measured. | Different cost heterogeneity can eliminate effort or change which action is optimal. | `CEAV_M1_MANUSCRIPT_V0_2.md:124-127`, `256-265`; config `:6`. |
| A9. `H01` reports raw `X_i`; binary match is modal-label reporting. | Specifies what “truthful” means in this game. Essential to the report-payoff calculation. | This is not a proper probability report and cannot be assumed to elicit all information types. | A domain with graded quality or multi-valued evidence needs a different report space or scoring rule. | `CEAV_M1_MANUSCRIPT_V0_2.md:124-127`, `264-265`; readiness `:36-40`. |
| A10. External release utility is linear and task-local: `b_i P(D_final=1)`. | Makes every deviation affine in `b_i` and permits exact interval intersection. Essential to T4/T5. | `b_i` may summarize financial, relational or reputational interests only if they are linear and stable. It is not observed or enforced. | History-dependent bribes, outcome-specific utilities, abstention value or nonlinear interests are outside the certificate. | `CEAV_M1_MANUSCRIPT_V0_2.md:178-185`, `298-326`; gap assessment `:28-58`. |
| A11. `A_pay~Bernoulli(2/5)` is independent of information, reports, peers and future `T`; only this event pays the bonus. | Removes the direct report-to-payment-eligibility channel and yields `E[R|I,r]=f+mu*a*P(T=r|I)`. Essential to T3a and the dual architecture. | This is a protocol choice, not a domain property. It does not prevent a report from changing expected match payment or decision utility. | If eligibility depends on reports or is revealed early, T3a no longer applies and T1's audit-seeking channel can return. | `CEAV_M1_MANUSCRIPT_V0_2.md:149-176`, `230-265`; catalog `:39-48`, `196-224`. |
| A12. `A_dec` is independent of `A_pay`, selective only on `S={Z=0,sum(r)=2}`, or uniform with `d=19/1250`; one union audit is charged. | Defines exposure `a+(1-a)d` and the selective/uniform comparison. Essential to T3b and the budget rows. | Risk targeting can be domain-specific because the report class may not predict risk outside calibration. | Different risk distribution, double charging or a report-dependent payment channel changes loss, cash and exposure. | `CEAV_M1_MANUSCRIPT_V0_2.md:157-175`; config `:7-12`; report `:221-252`. |
| A13. Frozen H01 calibration and fixed off-equilibrium `g0/g1`; release threshold posterior odds `>=2`. | Defines the final decision for every actual strategy, including deviations. Essential to all T4/T5 witnesses. | Calibration is tied to the synthetic fixture and not re-estimated after deviations or domain shift. | Recalibration is a different game; using a table outside its population can invalidate quality gates. | `CEAV_M1_MANUSCRIPT_V0_2.md:129-147`; report `:32-55`; gap assessment `:83`. |
| A14. Prior-weighted metrics and asymmetric gates: `FA<=1/5`, `FR<=1/4`, wrong payout `<=3/20`, loss uses `C_FA=2,C_FR=1`. | Defines what “quality” and “bad equilibrium” mean. Essential to T3b/T5 gate verdicts. | Conditional FA/FR transfer more readily than prior-weighted loss; gate values are application-specific policy choices. | Different payout value, class prevalence, risk tolerance or loss weights can reverse a domain comparison without refuting the theorem. | `CEAV_M1_MANUSCRIPT_V0_2.md:191-226`; config `:8-12`. |
| A15. Budget and resource assumptions: `B=6`, `mu=2`, `kappa=1/4`, operating cost `0`, exposure `<=1/2`, reward reserve `<=6`, expected cash `<=4`. | Establishes the feasibility gates and reserve/cash certificate. Essential to the budget claim, not to the algebraic factorization alone. | These are normalized research units, not a token, currency or observed settlement budget. | Real audit travel, latency, payment fees or payout scale can make a mathematically feasible point unaffordable. | `CEAV_M1_MANUSCRIPT_V0_2.md:217-226`; config `:7-12`; report `:247-252`. |
| A16. Three distinct Judges, fixed peer strategies, unilateral task-local deviations and no coalitions/Sybils/entry choice. | Defines best responses and the pure equilibrium concept. Essential to T4/T5 completeness. | This is not an identity or participation guarantee for a decentralized protocol. | Sybil control, collusion, correlated identities, nonparticipation or coalition deviations produce a different game. | `CEAV_M1_MANUSCRIPT_V0_2.md:117-127`, `366-367`; certificate scope `:32457-32464`; limitations `:3-13`. |
| A17. Positive branch probabilities and independent branch-local choices. | Allows full equilibria to be formed from overlapping branch intervals and supports the `216^2` product enumeration. Essential to T5. | A real workflow may couple decisions across milestones, reputation, repeated interaction or learning. | Cross-branch history or reputation can invalidate the branch-product completeness argument. | `CEAV_M1_THEOREM_AND_COUNTEREXAMPLE_CATALOG.md:429-445`; report `:117-149`. |
| A18. Creator evidence and information-generation law are exogenous. | The game evaluates a fixed joint distribution; it does not solve creator strategy or adversarial evidence generation. Essential to interpreting the certificate as a fixed-distribution result. | Strongly domain-dependent: staged photos, common repositories, supplier records and recipient access can all be strategic. | `P(Z,X,T|Y)` may change after policy publication; current quality and incentive results do not provide an adversarial creator guarantee. | `CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md:45-55`, `138-164`; gap assessment `:78-83`. |
| A19. Exact rational arithmetic and pinned source identity. | Establishes reproducibility of the finite calculation, not truth of the assumptions. | Domain-neutral evidence practice. It is already verified. | A hash mismatch or missing source invalidates reproduction; a matching hash does not validate the real-world model. | `review-package/CLAIM_EVIDENCE_MAP.md:22-28`; certificate `:32457-32468`. |

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
| **Hardware and product development** | At a declared time, the specified unit count, identity, dimensions, tolerances and operational checks pass. This is close to the physical snapshot structure in the protocol. | `Z`: photos, tracking, invoice and claimed receipt. `X_i`: fresh inventory challenge, live recipient contact and measurements. `T`: independent site inspection of the whole batch. | Supplier, creator and recipient may collude; travel and inspection access create cost and latency; temporary placement can satisfy a presence predicate without proving ownership or durability. | **CONDITIONAL, strongest current fit.** The school-desk protocol is an exemplar for a finite physical acceptance claim, not evidence that the synthetic `9/10` audit assumption holds. |
| **Community and charitable projects** | A concrete distribution or construction milestone can be binary, such as all registered items delivered and checklist predicates passing. Beneficiary welfare, long-term impact and “community satisfaction” need separate constructs. | `Z`: public report, photos, inventory and claimed recipient receipt. `X_i`: independent recipient contact or item-level inventory. `T`: independent site census or inspection. | Privacy, safeguarding, restricted access, donor/creator relationships, beneficiary dependence and common evidence can make independence or audit access difficult. | **CONDITIONAL.** Charity is one application, not the model definition. The model transfers to observable milestones; it does not establish impact, beneficiary welfare or donor protection. |

The domain matrix supports a general-purpose scope with a narrow application
condition: the campaign must make the milestone observable and contractually
testable. The school-desk study explicitly says it does not establish other
milestone categories or educational impact (`CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md:14-19`).

## 4. T3–T5 mathematical and external-validity assessment

Legend: **M** = mathematical validity under the declared assumptions; **P** =
portability of the numerical parameters; **A** = applicability to a real
campaign; **G** = generality of the result; **E** = missing external evidence.

| Result | M | P | A | G | E | Classification and evidence |
|---|---|---|---|---|---|---|
| **T3a: payment factorization and effort threshold** | **PASS.** Independence of `A_pay` gives `E[R|I,r]=f+mu*a*P(T=r|I)`; High is strictly better than best Low iff `mu*a*Delta>c`. The proof is algebraic. | **CONDITIONAL.** The form is portable, but `Delta=2/25`, `c=1/20`, and the net gap `7/500` are fixture values. | **CONDITIONAL.** Requires hidden report-lock timing, known likelihoods, neutral utility and only the declared report-dependent payoff. | **Moderate.** The factorization applies to a class of binary match games; it is not a general truthfulness or proper-scoring theorem. | **GAP.** No measured information value or reviewer cost; no evidence that modal binary matching is suitable for the domain. | `CEAV_M1_MANUSCRIPT_V0_2.md:230-265`; catalog `:194-231`; novelty audit `:113-148`. |
| **T3b: conditional neutral feasibility and selective-versus-uniform comparison** | **PASS.** The analytic region `5/16<a<1/2`, `0<t<=(1/2-a)/(1-a)` and the gate/loss inequalities are proved for F51-02, fixed tables and neutral Judges. | **No.** The exact region and values depend on F51-02, losses, gates, calibration and risk class. | **CONDITIONAL.** Requires the same distributions, fixed calibration, independent lotteries, trusted `T`, no outside options and the declared action class. | **Limited but more than a grid.** It is an analytic region for one fixed primary environment, not a theorem over campaign domains or reward policies. | **GAP.** No domain has measured equal exposure, audit value or cost. The equal-exposure loss comparison is conditional on the same report distribution. | `CEAV_M1_MANUSCRIPT_V0_2.md:267-296`; catalog `:233-333`; novelty audit `:184-205`. |
| **T4: local external-interest boundary** | **PASS.** Exact affine deviations against frozen H01 peers yield Selective `(-70/633,175/1102)` and Uniform `(-218750/2070709,218750/1365587)`. | **No.** Endpoints are tied to the frozen signals, tables, costs and action class. | **CONDITIONAL.** Requires a stable linear `b_i`, fixed peers and fixed off-equilibrium calibration. The mechanism does not enforce the interval. | **Finite local generality.** It covers each Judge position in the declared fixture, not arbitrary heterogeneous or dynamic games. | **GAP.** No empirical distribution or measurement of `b_i`; disclosure and screening do not prove the bound. | `CEAV_M1_MANUSCRIPT_V0_2.md:298-326`; report `:72-115`; catalog `:335-401`. |
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

## 5. Unsupported or overstated claims

The current manuscript and brief are largely claim-disciplined. The findings
below are editorial safeguards rather than discovered proof errors.

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

There is no evidence of a logical inconsistency caused by a charity-specific
definition. The only direct domain-specific artifact is the proposed physical
measurement protocol, and that document already limits its scope.

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

## 7. Minimum editorial corrections needed

No code or certificate change is required. Before external academic review,
make these narrow textual corrections in a subsequent editorial pass:

1. In the manuscript introduction and research brief, state explicitly:
   “FundTogether is a general-purpose decentralized crowdfunding protocol;
   CEAV-M1 abstracts one observable escrow milestone, and charity is only one
   possible application.”
2. Label the school-desk protocol as a **concrete physical-evidence
   exemplar**, not a representative sample of all FundTogether campaigns.
3. Define “trusted audit” as a noisy, externally supplied model signal whose
   provenance, independence and capture resistance are empirical questions.
4. Replace unqualified “truthful” in overview prose with “truthful raw-label
   H01 reporting” where the statement refers to T3.
5. Keep the qualifiers “fixed,” “declared pure stationary class,” “synthetic”
   and “candidate instance-level contribution” next to the corresponding
   numerical or novelty claims.
6. Add one sentence separating reviewer-game results from creator strategy,
   donor welfare, blockchain execution, settlement finality and liveness.

These are editorial corrections. They do not retune the model, alter the
historical results or create a new mechanism version.

## 8. Final recommendation

**Recommendation: NARROW the application claims while RETAINING the existing
mathematical model and certificates.** Do not fundamentally revise CEAV-M1 for
charity/general-purpose scope. The model is sufficiently domain-agnostic to
support a class of crowdfunding milestones, but only conditionally: the
milestone must admit a defensible binary acceptance predicate and the campaign
must supply empirical evidence for the signal, audit, cost, timing and utility
assumptions.

The manuscript remains appropriate for **external academic review as a
conditional theory/counterexample case study**, subject to the editorial
clarifications in §7. It is not ready to claim field validity, production
readiness, universal decentralized guarantees or broad novelty. This conclusion
is consistent with the paper-readiness decision (`CEAV_M1_PAPER_READINESS.md:8-12`),
the novelty boundary (`CEAV_M1_NOVELTY_AUDIT_T3_T5.md:338-344`) and the frozen
certificate status (`results/dual-strategic-boundary-20261024T0524070523492Z/analysis/certificate.json:32457-32468`).

### Required final answers

1. **Do T3–T5 remain mathematically valid?** Yes, under the originally
   declared finite-game assumptions. Their numerical values are not portable
   without recalibration and reanalysis.
2. **Does general-purpose FundTogether scope require material model changes?**
   No for the research model; yes for application mapping and empirical
   validation. The correct action is editorial narrowing, not V7 or a new
   mechanism.
3. **What prevents direct adoption?** Objective `Y`, calibrated and
   conditionally independent `Z/X/T`, audit integrity, measured effort/cost,
   bounded external interests, creator/evidence strategy, participation and
   settlement liveness.
4. **Which findings are editorial versus mathematical?** The proofs and exact
   certificate pass within scope. General-purpose framing, “trusted” wording,
   school-desk transfer and unqualified “truthful” wording are editorial
   safeguards; portability and field adoption are empirical gaps.
5. **Is the manuscript appropriate for external academic review?** Yes, as a
   clearly conditional theory/counterexample draft after the minimum wording
   corrections; no claim of external peer review or submission readiness is
   made.
