# CEAV-M1 — Empirical audit and trust protocol

Date: 2026-10-24. Status: **SPECIFIED empirical study; no observations collected,
no empirical parameter estimates, and no production mechanism implemented.**
This protocol supports [paper readiness](CEAV_M1_PAPER_READINESS.md), the
[theorem catalog](CEAV_M1_THEOREM_AND_COUNTEREXAMPLE_CATALOG.md), and the
[research gap assessment](CEAV_M1_RESEARCH_GAP_ASSESSMENT.md). Its mathematical
parents are the [synthesis memo](CEAV_M1_RESEARCH_SYNTHESIS_AND_FEASIBILITY_MEMO.md)
and [verified strategic boundary report](CEAV_M1_DUAL_STRATEGIC_BOUNDARY_REPORT.md).
It proposes measurement, rather than changes to those frozen experiments.

## 1. Concrete milestone and unit of analysis

Use a **batch of 20 individually identified, standard school desks delivered
to one named, consenting school**. The unit of truth, review, audit and
decision is the complete batch milestone, not each photograph or each desk.
This category permits physical counting, identity checks and measurement;
it does not establish educational impact, long-term durability, supplier
honesty in general, or the acceptability of other milestone categories.

Before any case is reviewed, register the purchase order, recipient, delivery
deadline and reference time `tau`, 20 expected desk identifiers, approved
model/drawings, dimensional tolerances supplied with the procurement, and a
finite checklist of observable assembly/condition requirements. Each item
must have an operational test and a recorded result. Procurement/safety
expertise must approve that checklist before enrollment. A photograph-based
study cannot certify structural safety or lifetime performance; any such
requirement needs an appropriate independent inspection/test in the
reference procedure, or must be outside the milestone claim.

The first study is a **consented research exercise**, with archived genuine
deliveries used only for pilot/rubric work and current study-owned staged
cases used for new paired physical observations. There is no live escrow,
release or penalty. A later prospective delivery cohort is a separate,
preregistered measurement phase. Stage missing items, identity mismatches or contradictory evidence
only with safe study materials. Do not withhold promised furniture, create
unsafe desks, deceive beneficiaries, or use failure cases to alter real
funding. Mark staged cases in the sealed research metadata. Their performance
estimates must remain separate from a later prospective delivery cohort.

## 2. Ground truth and four separate information roles

| Role | Operational definition | What it must not be confused with |
|---|---|---|
| `Y` | At `tau`, all 20 specified desks are physically at the named school, match their identifiers/model and satisfy every preregistered observable acceptance item. `Y=1` means every predicate passes; `Y=0` requires documented failure of at least one. | Creator satisfaction, reviewer consensus, a receipt alone, or the output of audit `T`. |
| Public evidence and `Z` | Frozen order, creator submission, delivery photos/video, inventory and claimed recipient receipt available identically to all reviewers. `Z=1` means that packet passes a pilot-locked public-only completeness/consistency rubric; `Z=0` means it fails. Retain the raw packet and every rubric item. | Verified delivery. Creator-selected or manipulated evidence may pass the public rubric. |
| Costly reviewer information `X_i` | A reviewer who elects the High workflow contacts the school using a separately sourced registered contact, issues a fresh inventory challenge using randomly selected desk identifiers, and examines the returned live evidence plus detailed inventory. The reviewer privately records a binary assessment using a locked rubric and the underlying observations. Low access contains only the public packet. | An automatically accurate `4/5` signal, or the reviewer's final strategic report `r_i`. Observed acquisition, perceived assessment and submitted report must be separate fields. |
| Operational audit `T` | A separate inspector makes a physical site visit, checks the whole batch inventory and identity, performs the locked measurements/condition checks and submits pass/fail before seeing reviewer reports or reference labels. | An error-free truth oracle, the reference team, or an audit of only the reviewer-selected photos. |

The binary coding of `Z` and `X_i` is a model interface, not a description of
all the information humans possess. Develop the rubric in the pilot, then
freeze it for held-out evaluation. Record richer item-level data so that
failure of this compression can be diagnosed without silently relabeling
the confirmatory endpoint. Where a reviewer declines or cannot obtain the
High information, record that fact; do not substitute a simulated `X_i`.

### Independent reference procedure

A reference team, operationally separate from the `T` team and reviewers,
conducts an independently documented full physical census against the
registered acceptance specification. It verifies recipient identity using
the school's independent contact/authority record, captures identifiers and
measurements, and creates a sealed evidence file. Two assessors apply the
reference rubric independently; a third qualified assessor resolves item
disagreements using additional factual inspection under that same rubric.
No assessor may use the candidate `T` result, reviewer votes or creator's
preferred outcome to determine `Y`.

For prospective paired visits, define one observation window around `tau`,
record all visits and changes, and prevent moves/repairs between observations
with recipient consent. Randomize visit order when feasible without revealing
the other team's findings. A change in physical condition is a temporal
classification problem, not automatically an error by either team. Cases
without a defensible common-time comparison are marked indeterminate and
reported. Archives support pilot/rubric work, not confirmatory new-visit
audit accuracy for a historical tau. A current site visit cannot establish
what T would have reported at the historical delivery time. Any separately
declared retrospective paired analysis would require genuine contemporaneous,
blinded operational-T records and an independent contemporaneous reference,
with its own eligibility and missingness rules; it is not supplied by this
protocol. A retrospective invoice is insufficient.

This is an operational reference standard with an auditable error risk, not
metaphysical certainty. A disagreement about the acceptance contract is a
specification defect, not something to settle by majority vote. Resolve
that contract for future cases and retain the original case as unresolved.
If a credible reference cannot be established, report agreement with the
comparator rather than calling it sensitivity/specificity. These design
choices follow the statistical distinction between accuracy and agreement
in [FDA's 2007 guidance, §§2–5](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/statistical-guidance-reporting-results-studies-evaluating-diagnostic-tests-guidance-industry-and-fda).
That source supplies a measurement analogy; this is not a medical study or
a claim that medical regulation applies to crowdfunding.

## 3. Audit validation and missing outcomes

Apply both operational `T` and the reference procedure to **every held-out
milestone**, irrespective of `Z`, reviewer reports, agreement, or the risk
class `S`. Collect `T` in a sealed research channel even when a simulated
payment/decision lottery would not request it; the simulated decision must
not receive that unselected observation. Thus accuracy measurement does not
depend on report-contingent operational selection. Avoid revising reference
labels only when `T` disagrees: selective discrepancy resolution can produce
misleading accuracy estimates. See [FDA guidance, §§3 and 5](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/statistical-guidance-reporting-results-studies-evaluating-diagnostic-tests-guidance-industry-and-fda).

If audit-all measurement later proves unaffordable, declare the confirmatory
design incomplete. A replacement must be preregistered before further
unblinding: a probability sample with strictly positive, recorded inclusion
probability in every relevant stratum, paired reference checks, and
design-weighted accuracy and variance estimates. Raw proportions from a
risk-selected subset do not estimate population sensitivity/specificity.

For determinate reference labels, report the complete table:

| | `Y=1` | `Y=0` |
|---|---:|---:|
| `T=1` | TP | FP |
| `T=0` | FN | TN |

Estimate `Se_T=TP/(TP+FN)` and `Sp_T=TN/(TN+FP)` separately. Also report
`P(T=1|Y,Z)` and error rates by defect type, evidence source, creator,
school, inspector, stage/prospective source, and audit route when data permit.
Report denominators and uncertainty; sparse strata are not evidence of
homogeneity. The synthetic assumption `Se_T=Sp_T=9/10` is **unmeasured**.
Neither high overall agreement nor a single pooled accuracy establishes it.

Use explicit `indeterminate`, `not obtained`, `late` and `withdrawn` states
for both `T` and the reference; retain their reasons and a full case-flow
table. Primary binary rates are conditional on determinate paired labels,
with that restriction stated. Alongside them report operational completion
and worst/best classification bounds: among known `Y=1`, unresolved `T`
contributes between zero and one success each, and analogously for `Y=0`.
Show bounds over unresolved `Y` assignments or label target accuracy
unidentified if those cases prevent a defensible estimate. Do not quietly
drop difficult cases or convert missing truth into `Y=0`. This reporting
plan adapts the original [STARD 2015 checklist, items 15–19 and 23–25](https://www.bmj.com/content/351/bmj.h5527.long)
to a physical verification study.

## 4. Independence and strategic evidence are testable risks

Separate teams, concealed outputs, no shared payments and independently
sourced recipient contacts reduce information leakage; they do **not** prove
`T independent of (Z,X_A,X_B,X_C) conditional on Y`. A binary label hides
defect severity, common counterfeit documents, a cooperative or deceptive
recipient, location and access difficulty. Those can create common errors
even under perfect blinding. Three independent accounts are not three
independent information sources.

Record defect families and item-level reasons, evidence provenance, who
created each artifact, shared contacts, shared reviewer affiliations, and
all communications. Compare joint error frequencies with products of
conditional marginals, with cluster-aware uncertainty, both given `Y` and
within preregistered defect strata. A small nonsignificant dependence test
does not validate independence. Report detectable effect sizes and leave
the exact factorized model unverified where samples cannot distinguish
meaningful dependence. Do not replace it by a fitted correlated mechanism
in this protocol.

Use distinct consenting reviewers with conflict disclosures and record
their assignment/communication graph. Recipient/creator financial links,
repeat employment, donations, related-party relationships and common
organizations are measured conflict indicators. They neither identify all
Sybil identities nor prove absence of side payments. Similarly, independent
auditor procurement is an institutional trust assumption; a captured auditor
can return a coordinated false `T`. Preserve such failures as limitations.

## 5. Calibration and held-out evaluation

1. **Pilot/calibration phase:** refine feasibility, consent, acceptance
   definitions, evidence rubrics, case flow, time logging and dependence/cost
   planning. Identify every pilot case as exploratory. Estimate candidate
   distributions with uncertainty; never call a synthetic fixture calibrated
   to real behavior without the actual data and estimation method.
2. **Freeze before evaluation:** register the target population, inclusion
   and exclusion rules, all rubrics, label/adjudication rules, sample plan,
   precision endpoints, missingness rules, analyses, stopping limits and
   immutable hashes of the evaluation code/materials. Record amendments with
   dates and their consequences. This is a proposed preregistration, not an
   assertion that historical computations were preregistered. [OSF's
   preregistration guidance](https://help.osf.io/article/330-welcome-to-registrations)
   provides a suitable registration workflow.
3. **Held-out phase:** allocate whole creator/supplier-school case families
   to one phase, including near-duplicate submissions and repeated batches.
   Keep a later time block for prospective evaluation where feasible. Do not
   let an overlapping school/creator component leak across splits; if that
   leaves too few independent components, state that independent external
   evaluation is not yet feasible. Repeated reviewers/inspectors are recorded
   crossed clusters; reserve separate personnel for transportability checks.
4. **Locked analysis:** apply the frozen mappings to held-out cases without
   tuning thresholds after labels are seen. Report distributions, `Se/Sp`
   for `Z`, costly assessments and `T`, dependence diagnostics, selection,
   cost and latency. Keep all cases in the flow record. Any later refit is
   exploratory and requires a new held-out sample before confirmatory claims.

The certified H01 decision tables and historical gates are unchanged. A
field distribution incompatible with those synthetic assumptions is evidence
against transporting the certificate; it does not authorize silently
recalibrating the existing result. Research-only replay of the frozen rule
must retain separate observed and simulated outputs, with assumptions about
unobserved effort/reporting made explicit. It is not a field equilibrium test.

## 6. Required sample size and uncertainty methodology

The primary precision endpoints are **separate sensitivity and specificity**
of `T`. Plan independently for `n_1` determinate `Y=1` milestones and `n_0`
determinate `Y=0` milestones, not for one arbitrary total number of desks.
Choose a two-sided interval width at most `0.10` for each endpoint as a
proposed design target. To obtain at least 95% simultaneous coverage for
the pair under independent-binomial sampling, use a 97.5% interval for each
endpoint (Bonferroni). This is a statistical precision target, not a change
to any historical mechanism gate or an accuracy threshold.

For planning only, the normal approximation

```text
n_y approximately ceil(z_(1-alpha_e/2)^2 * p_star*(1-p_star) / h^2),
h=0.05, alpha_e=0.025 for each of the two primary endpoints.
```

uses the conservative planning value `p_star=1/2` when there is no pilot
estimate. It gives approximately **503 independent milestones per truth
class**. This illustrative approximation is not an exact sample requirement,
not a claim that these cases exist, and not 503 desks or 503 reviewer votes.
The final independent-case requirement is the smallest `n_y` such that
**for every possible success count `k=0,...,n_y`, the equal-tailed
Clopper–Pearson interval has width at most `0.10` at confidence 97.5%**.
Compute that integer and archive the planning calculation before enrollment.
Use [NIST's binomial interval construction](https://itl.nist.gov/div898/handbook/prc/section2/prc241.htm)
for the tail inversion, including `L=0` at `k=0` and `U=1` at `k=n`.
Wilson intervals can be shown as a labelled secondary display; do not use a
normal Wald interval at small counts or imply that exact binomial coverage
holds for correlated milestones.

Enrollment must account for prevalence and missingness. At an assumed
planning prevalence `pi`, `max(n_1/pi,n_0/(1-pi))` is only a first expected
total; the final maximum enrollment requires assurance calculations for
obtaining both class counts, reference indeterminacy and attrition. Show
several plausible `pi` values if it is unknown. If failures are rare, an
enriched documented failure cohort can estimate conditional performance
for its declared defect mix; it cannot estimate field prevalence, predictive
values, decision loss or expected cash without justified population weights.
Report staged and natural failures separately.

Creator, school, supplier, reviewer and inspector reuse induce clustering.
For an equal-size single-cluster planning approximation, inflate by
`DE=1+(m-1)*rho`; this limitation and the loss of effective sample size are
described in the original [CONSORT cluster-trial extension](https://www.bmj.com/content/328/7441/702.full).
This exercise is not thereby a cluster randomized trial. Use pilot-informed
correlation ranges and actual cluster sizes for final assurance, accounting
for crossed personnel effects. Held-out inference must resample independent
case clusters or use a justified cluster/survey model; simple binomial
intervals are descriptive only when dependence remains. Report the number
of independent clusters, cluster sizes, design effect, method assumptions,
and the uncertainty caused by few clusters. More photographs from one
delivery cannot repair a shortage of independent deliveries.

Freeze a maximum number of milestones/clusters, recruitment window and
missingness allowance before evaluation. No early success claim based on
peeking at favorable accuracy estimates. Administrative interim checks may
count enrollment/completion without accessing errors. Reaching the limit
with insufficient precision is an inconclusive empirical result. Any
sequential outcome-based design instead needs a separately specified
coverage-valid stopping method before use; it is not supplied here.

## 7. Reviewer effort, costs and external preferences

Measure access acquisition separately from quality. In an initial consented
research comparison, randomize access to public-only versus public plus
costly workflow information across independent cases/reviewers using a
locked assignment, so the information gain is not estimated only among
self-selected diligent reviewers. Log requests, active task time, elapsed
time, failed contacts, distances and materials. Preserve a later voluntary
choice exercise as a separate exploratory study: access assignment does
not identify equilibrium effort under the certified reward mechanism.

Record recruitment, acceptance, refusal, dropout, completion and alternative
paid activity. A task timer estimates time, not subjective disutility. Use
consented opportunity-cost/compensation questions or a separately designed
incentivized choice exercise, retaining their measurement limitations.
Fixed research compensation is not evidence that `c_i=1/20`, or that the
mechanism's transfers secure participation.

| Quantity | Measurement and accounting boundary |
|---|---|
| Operational `kappa` | All-in incremental cost of one completed `T`: inspector labor, travel, equipment, administrative scheduling, failed attempts and required repeat visits. Report currency, price date, scale and fixed/variable components. Route-specific costs and latency may differ. |
| Empirical study cost | Reference census, audit-all measurement, double coding, adjudication, research data management and participant compensation. Keep separately from mechanism cash and never charge it as if incurred only on `A_pay union A_dec`. |
| Reviewer disutility `c_i` | Individual utility cost of the High workflow, distinct from cash paid and from auditor cost. Record heterogeneity and outside options; monetary conversion needs a declared model. |
| Reward reserve/payment | Mathematical cap and actual transfer are different. No transfer or settlement is required here. A replay may calculate counterfactual payments from the frozen rule; it cannot turn research fees into observed mechanism payouts. |
| Release preference `b_i` | Utility gain from release versus rejection, including financial or nonfinancial interests. Conflict disclosures and self-report are proxies, not observed complete utility. |

Before comparing any measured money or effort to `B=6`, `mu=2`,
`kappa=1/4`, `c_i=1/20` or a boundary in `b_i`, declare the currency-to-model
unit, payout normalization and assumptions of linear/quasilinear utility.
`b=1/10` is not automatically ten percent of a real milestone value. No
observed average can establish a bound for every participating Judge, and
the exact study covers selected bias vectors, not every heterogeneous vector
inside a box. **Assuming a restricted `b_i` is not enforcing that restriction.**
No identity, conflict-screening or punishment mechanism in this study
guarantees it.

Independent payment and decision coins are mathematically frozen, but their
physical work can overlap. For a research replay, record both event draws,
the union and one operational audit charge per union; do not add two
`kappa` charges or count the reference visit as a mechanism audit. Research
audit-all expenses remain visible in the separate study budget. Empirical
error estimates must also check whether inspector quality changes with
workload, route, reason for inspection or prior report visibility.

## 8. Latency, deliverables and empirical stop rules

Record time from submission to locked review, audit request, contact, visit,
completed `T`, reference completion and any hypothetical decision. Report
medians, upper quantiles, missed windows, missing audits and access failures;
cash means alone hide a potentially unusable settlement delay. Define a
maximum acceptable observation window before recruitment. Late audit is
an operational failure for that window even when its eventual label is
correct; do not equate eventual correctness with pre-settlement feasibility.
This protocol does not choose a production escrow timeout or fallback owner.

The empirical package must contain the registered protocol/amendments,
consented provenance and access controls, immutable public/High/audit/reference
packets, item-level labels with adjudication history, a case-flow table,
cluster IDs and split manifest, a blinded analysis log, accuracy and missingness
tables with uncertainty, dependence diagnostics, measured cost/latency and
de-identified conflict/participation summaries. Do not publish schoolchild
images, personal contacts or unconsented identity data in open artifacts.

Stop short of empirical validation if the reference is not defensible, too
few independent `Y=0` cases exist, leakage prevents held-out evaluation,
missingness defeats accuracy identification, or precision targets are unmet.
Contradictory cost, dependence or accuracy data must be retained. A completed
measurement protocol could support a paper about the gap between the model
and a physical verification task; it cannot retroactively validate synthetic
signals, establish a strategic equilibrium in the field, or make the
mechanism production-ready.

**Empirical readiness decision: protocol-ready for review and preregistration;
empirical claims are not ready.** The proposed study has not been funded,
approved, registered, recruited or run. No real-world accuracy, effort, cost,
independence or bounded-interest guarantee is established by this document.
