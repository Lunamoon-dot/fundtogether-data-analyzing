# CEAV-M1 — Paper readiness

Date: 2026-10-24. Evidence baseline: commit
`b6935ea11d6dda42ec089c83e03013db7f86fdf4`, branch
`research/v6-rave-phase01`. This document prepares an academic argument;
it does not add a mechanism version or change any verified experiment.

**Decision: READY_FOR_THEORY_MANUSCRIPT_DRAFT; NOT_YET_SUBMISSION_READY.**
There is a coherent, reproducible theory-and-counterexample paper to write.
Priority of the proposed contribution remains unestablished. There is no
empirical evidence yet that a FundTogether audit satisfies the model.
A theory paper can state that limitation; a field-validation claim cannot.

## 1. Proposed paper and claim discipline

Working title: **Verification Incentives and Settlement Decisions: Exact
Feasibility and Failure Boundaries in a Three-Reviewer Milestone Game**.

Research question: when one noisy verification signal both rewards reviewers
and informs a binary milestone decision, which guarantees concern acquiring
information, reporting it, and obtaining good decisions at every equilibrium?

Proposed abstract material: We study a finite costly-information game motivated
by milestone verification. Report-contingent audits can reward audit seeking;
unrewarded branches can admit uninformative reports. Separating payment
eligibility from decision verification yields a conditional neutral feasibility
region under a reward reserve and audit-exposure cap. At one fixed synthetic
instance, exact rational analysis identifies distinct local truthful-stability
and quality boundaries over all pure stationary equilibria. Shared release
interests produce bad strict pure stationary equilibria while truthful
reporting remains a strict equilibrium. We provide proofs, independently checked finite certificates,
unfavorable baselines and an empirical protocol for testing audit assumptions.
The findings are conditional on the stated signals, costs, strategy class
and trust boundary; they do not validate a deployed escrow protocol.

Use the five numbered propositions in the
[theorem catalog](CEAV_M1_THEOREM_AND_COUNTEREXAMPLE_CATALOG.md).
The word “truthful” must identify its object: raw private label X in the
binary-match game, a posterior for noisy T in the Brier game, or a correct
decision about Y. These are different properties.

## 2. Evidence ledger for the manuscript

The [parent synthesis, §2](CEAV_M1_RESEARCH_SYNTHESIS_AND_FEASIBILITY_MEMO.md)
owns the consolidated V3–V6 table, including exact witnesses and artifact
locations. The [Dual Boundary Report](CEAV_M1_DUAL_STRATEGIC_BOUNDARY_REPORT.md)
owns the later external-interest result. Preserve both histories.

| Evidence family | Safe manuscript use | Required limitation |
|---|---|---|
| V3 / V3.1 | Useful asymmetric effort exists at a named anchor point; the tested uncertainty policies do not pass all scenarios. | Exact finite instances/grid, not a continuous robustness or empirical interval. |
| V3.2 / V3.3 | Report-sensitive selection can bias reporting; IPW cancels the selection factor in expected payments but enlarges reserve needs. | V3.2 diagnostic `robust=True` used permissive gates; V3.3 study used B=24. Neither is a B=6 quality-success comparison. |
| V4 | Centering public-signal agreement does not remove all-Low or inverted-label equilibria. | Statements belong to that centered payoff and information structure. |
| V4.1 | Entry/cost bounds and a tested quality–cash trade-off; a fixed pair has an analytic audit-cost crossover. | No hybrid dominance on the declared grid is not a global impossibility theorem. |
| V5 / V5.1 | Propriety for T, effort-value and reserve/cash bounds are separate; binary match can dominate a named Direct-Brier point. | Bounds are score- and environment-specific; no general rejection of proper scoring. |
| V6 | Positive information value with exogenous truthful reports coexists with strategic failures of all four declared candidates. | Four bad-NE certificates refute their all-equilibrium gates without enumerating all equilibria; they do not rule out every selective audit mechanism. |
| Dual, neutral | A nonempty analytic region and one certified point pass the retained gates. | Independent payment eligibility, trusted T, fixed calibration and neutral interests are assumptions. |
| Dual, external b | All-real-b, exact pure stationary equilibrium intervals for neutral, each one-biased position and symmetric interests. | Mixed equilibria, general heterogeneous b vectors, coalitions and empirical behavior remain outside the certificate. |

Classify every result in the paper: **analytic proposition**, **exact finite
certificate**, **finite policy/assumption grid**, **software validation**, or
**empirical observation**. The present central results use finite probability
sums and exact enumeration, not Monte Carlo simulations. No human or field
measurements are available. Browser/test acceptance validates software flows,
not behavioral assumptions or scientific novelty.

## 3. Focused prior-art comparison and novelty status

The following comparison was refreshed on 2026-10-24 using primary papers,
author/institutional copies and publisher records. It is a focused comparison,
not a systematic review proving the absence of prior work. Established ideas
must be credited even where their assumptions differ.

| Primary work and material inspected | Established result relevant here | Consequence for CEAV-M1 positioning |
|---|---|---|
| [Witkowski–Parkes, RBTS, AAAI 2012](https://cdn.aaai.org/ojs/8261/8261-13-11789-1-2-20201228.pdf), Theorems 9–10; source boundary in `references/PRIMARY_SOURCES.md` | Small-population reporting incentives under its admissibility assumptions. | Its theorem does not establish CEAV effort, uniqueness or decision quality. |
| [Gneiting–Raftery, JASA 2007](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf), abstract and §1 definitions | Proper scoring rewards truthful probability forecasts in its expected-score problem. | Propriety is established theory; it alone neither pays information costs nor handles external decision preferences. Binary label matching is a different elicitation objective. |
| [Gao–Wright–Leyton-Brown, AI 2019](https://uwspace.uwaterloo.ca/items/19ea8bc1-f265-48d7-8ce4-8591b86a928a), accepted manuscript §§3–4; [2020 author summary](https://www.ijcai.org/proceedings/2020/0723.pdf) | Costly versus cheap information and limited noisy trusted evaluations are established subjects. | Neither spot checking nor cheap-signal failure is new here. Compare objectives and cash accounting rather than transfer its theorem. |
| [Zarkoob–Fu–Leyton-Brown, AAMAS 2020](https://www.ifaamas.org/Proceedings/aamas2020/pdfs/p1593.pdf), §§2–4, Theorems 3.3 and 4.3; §5 | Carefully designed report-sensitive checks can be DSIC; using an available TA signal for every report can be suboptimal. | Direct counterweight to any universal anti-selectivity claim, and close precedent for separating signal acquisition from payment use. CEAV adds no priority claim for that separation. |
| [Ben-Porath–Dekel–Lipman, AER 2014](https://www.aeaweb.org/articles?id=10.1257/aer.104.12.3779), publisher abstract; [manuscript](https://www.bu.edu/econ/files/2014/05/Lipman-Optimal-Allocation-with-March-2013.pdf), prior source note | Costly verification of strategic allocation reports is established. | Different transfer/information assumptions; neither general costly verification nor selection is a CEAV invention. Full theorem-level mapping remains a submission task. |
| [Erlanson–Kleiner, TE 2020](https://econtheory.org/ojs/index.php/te/article/viewArticle/3101), §§3–4 as recorded in `references/V6_RAVE_PRIMARY_SOURCES.md` | Collective decisions with costly, possibly imperfect verification. | Its imperfect check technology differs from an independent noisy claim-level T; no inherited incentive guarantee. |
| [Liu–Chen, AAAI 2017](https://ojs.aaai.org/index.php/AAAI/article/view/10619), model and posted-price setting | Eliciting costly effort through rewards predates CEAV. | No novelty claim for effort thresholds or reward tuning. |
| [Chen–Wu–Wu–Yang, ICML 2023](https://proceedings.mlr.press/v202/chen23ah.html), abstract/model boundary | Proper scoring and information acquisition form a principal-agent problem. | Propriety and effort must be analyzed separately. Only the inspected abstract is used; inspect the full optimization model before asserting a distinct theorem. |
| [Othman–Sandholm, AAMAS 2010](https://www.cs.cmu.edu/~sandholm/decision%20rules%20and%20decision%20markets.AAMAS10.pdf), §§1–2 | Forecast scoring and the decision rule interact even for decision-agnostic experts. | Forecast truthfulness does not automatically transfer to decision settings. CEAV is not a decision-market impossibility result. |
| [Chen–Kash–Ruberry–Shnayder, TEAC 2014](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/04/TEAC-final1.pdf), abstract and problem statement | Incentive-compatible advice and randomized decision rules have prior characterizations. | Their action-conditional prediction problem differs from auditing a pre-existing binary milestone truth. No transfer of a complete-mixing condition to CEAV. |
| [Boutilier, AAMAS 2012](https://www.cs.toronto.edu/~cebly/Papers/Boutilier_aamas12.pdf), §3 Theorem 3; §4 Theorems 10 and 17 | Decision-interested experts, compensation and uncertainty about their utilities are explicitly studied. | The external-interest term b and the need to bound its influence are established. The candidate contribution is the particular certified multi-Judge equilibrium boundary, not that modeling idea. |
| [Zhang et al., October 2026 preprint](https://arxiv.org/html/2610.01514v1), §3.3 Proposition 2; §3.4 Theorem 4 | Noisy, report-dependent verification can distort LLM factor reports; independent audit components change incentives. | Recent adjacent prior art weakens broad novelty claims about report-independent auditing. Its factor-vector score and behavioral experiments do not prove CEAV escrow results; peer-review status is not assumed. |

**Completed:** focused assumption/objective comparison above. **Open:** a
priority assessment for the precise theorem combination. Search terms included
“report-sensitive spot-checking”, “report-dependent auditing”, “decision
markets”, “self-interested experts”, and “verification payment decision
spot-checking”; the search covered archival papers and current preprints,
with backward references in the closest works. It was not an exhaustive
database/citation-chain screening, and no negative search proves novelty.

Before submission, expand forward/backward citation checks around Zarkoob,
Gao and Boutilier; compare theorem quantifiers, cost objectives, observability,
audit reuse and equilibrium concept side by side. Record exclusions and
access limits. If the certified numerical boundary is the main residual
contribution, frame this as a reproducible case study/negative-result paper
unless independent subject review supports a broader theorem contribution.

## 4. Academic manuscript outline

| Section | Argument and material to include |
|---|---|
| 1. Introduction and research problem | Motivate the gap between verifying an escrow condition and rewarding its reviewers. State research questions, the five scoped findings, negative outcome and empirical boundary immediately. |
| 2. Related work and novelty comparison | Use §3 and the catalog's novelty fields. Separate peer prediction, spot checking, costly verification, decision-interested experts and information value. Avoid claiming firstness. |
| 3. Formal model and escrow-verification setting | Define Y,Z,X,T, information timing, action maps, losses, b utility, pure stationary scope, reserve versus cash/exposure, and every fixed gate. Escrow is the motivating decision context, not implemented contract semantics. |
| 4. Mechanism architecture | Define A_pay and A_dec, independent hidden coins, one shared noisy T, frozen g0/g1 and bonus only on A_pay. State what changing a report can still affect. |
| 5. Incentive and feasibility propositions | Present catalog T1–T3, assumptions before proofs, modal-label reporting and the strict effort entry inequality. Distinguish a binary match from a strictly proper forecast score. |
| 6. Exact equilibrium analysis | Present T4–T5 and affine half-line intersection, branch-product completeness, endpoint ties, all Judge positions, pure existence and worst-equilibrium gates. |
| 7. Negative results and counterexamples | Keep V4 cheap/inverted equilibria, V5 effort/cash failures, V6 audit seeking and the Dual b=1/10 coexistence witness. Do not replace unfavorable results with retuned parameters. |
| 8. Experimental evaluation | Call current work computational exact evaluation. Describe pinned distributions, old finite grids, independent oracles, mutation checks, fair Uniform baseline and actual equilibrium costs. Put the proposed physical-evidence study in a clearly labeled future/protocol subsection. |
| 9. Limitations and trust assumptions | Separate missing empirical T quality/cost and dependence from unproved strategic cases, outside options, Sybils/collusion and calibration shift. Cite the empirical protocol and gap assessment. |
| 10. Conclusion | A conditional separation result with an exact failure boundary. Explain which claim is supported now and which observation or theorem could falsify the intended application. |

Appendices: complete proofs/counterexamples; V3–V6 evidence table; exact
equilibrium interval tables; source/output hashes and reproducibility steps;
empirical protocol and empty data dictionary. No fabricated results section.

Suggested paper tables: guarantee taxonomy; prior-art assumption matrix;
neutral Selective/Uniform metrics; local versus global b endpoints; bad
equilibrium witness; empirical assumption-to-measurement map. Any exported
plot should be generated directly from the certified fractions and label
synthetic axes; no new sweep is needed.

## 5. Minimum formal model to keep unchanged

At the certified Dual point, use F51-02: prior 1/2, public accuracy 7/10,
private accuracies 4/5, T accuracy 9/10, conditional independence given Y,
three Judges, six actions in each Z branch, cost 1/20, f=0. Freeze
a=2/5, t=1/6 on S={Z=0,sum(reports)=2}, mu=2, B=6, kappa=1/4,
C_FA=2, C_FR=1 and payout value 1. Freeze the H01 Bayes tables at threshold
2/3. Uniform uses d=19/1250. Gates are unchanged.

The motivating escrow asks whether a fixed contractual milestone is met
before a hypothetical release. Y is an evaluator/reference construct;
reviewer scoring uses T, never Y. This paper does not specify ownership,
execution, failure recovery or finality of real funds. A creator strategically
changing physical work/evidence is outside the fixed-distribution game.

## 6. Reproducibility and submission checklist

Primary evidence:

- [Dual certificate](results/dual-strategic-boundary-20261024T0524070523492Z/analysis/certificate.json),
  SHA-256 `fde3ad4745b37e270469aaec2692a51c83cbcf5db7fcb0a16938296a6e25b7d5`.
- [Dual bundle manifest](results/dual-strategic-boundary-20261024T0524070523492Z/manifest.json):
  5,590 independent checks, 864 oracle branch profiles, 4,320 branch candidates,
  466,560 full profile/scenario/mechanism combinations covered by factorization,
  10 normal and 10 optimized focused tests, 24 historical V6 tests, nine detected
  mutants, identical pinned replay. Hash identity alone is not correctness.
- [Dual exact interval tables](results/dual-strategic-boundary-20261024T0524070523492Z/analysis/interval-report.md)
  and [parent arithmetic evidence](results/research-synthesis-audit-20261024T045716506866Z/named-checks/certificate.json).
  Preserve the [actual freeze chronology](results/dual-boundary-freeze-20261024T051535026599Z/declaration.json);
  it is explicitly not retrospective preregistration.

The historical commands and pinned sources are in their owning reports;
do not rerun into an existing directory or silently regenerate their bytes.
Package a clean offline replay for reviewers, include environment/command
and source hashes, and check that every paper claim links to the proper
artifact. Larger raw historical files kept local must be identified and
distributed separately if required, with the public projection/hash limit
disclosed; do not imply every local raw run is hosted on GitHub.

| Requirement | Present status | Submission action |
|---|---|---|
| Coherent model, proofs and exact negative witness | Available in the catalog and certified reports | Independent mathematical referee check of quantifiers/strategy class. |
| Reproducible central finite result | Verified bundle available | Reviewer-facing clean replay and archival deposit/package check. |
| Prior-art comparison | Focused comparison complete; priority open | Finish closest-work theorem mapping and forward/backward search before any novelty assertion. |
| Full paper prose and bibliography | Outline/package prepared | Write manuscript to target venue and verify bibliographic metadata/full-text access limits. |
| Real audit and reviewer measurements | None collected | Needed only for an empirical/application-validity claim; otherwise state as an unvalidated protocol. |
| Wider strategic guarantee | Not proved | Keep conclusions in the declared class; no automatic larger study. |

Proceed with a theory/counterexample manuscript draft under these boundaries.
Submission readiness depends on the scoped novelty assessment, independent
proof review and a complete reproducibility package, not on adding V7.
