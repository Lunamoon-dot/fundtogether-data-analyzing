# Domain-dependence audit — claims and operationalization

Date: 2026-10-25. Read-only audit of the current research documents and owning
model sources. The only artifact authored by this task is this findings file.
No existing document, code, config, certificate or historical evidence was
changed. This is an audit note, not an external mathematical referee report.

## Assessment

The formal game does not require charity. Its inputs are a binary acceptance
state, information channels, costly reviewer actions, rewards and a binary
release decision; there is no charity-purpose parameter
(`CEAV_M1_MANUSCRIPT_V0_2.md:44-52,112-127,178-185`;
`configs/dual_boundary.json:4-18`). The manuscript and external brief already
frame an escrow milestone generally, while the empirical protocol explicitly
limits its school-desk exemplar to physical acceptance and excludes claims
about other categories (`CEAV_M1_EXTERNAL_RESEARCH_BRIEF.md:8-18`;
`CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md:14-29`). No discovered error is caused by
FundTogether being general-purpose rather than charity-specific.

This does **not** establish applicability in any domain. Every signal accuracy
is synthetic; no field independence, costs, preference bounds or performance
have been established (`CEAV_M1_MANUSCRIPT_V0_2.md:112-115,477-482`;
`CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md:336-339`). The findings below distinguish
actual text inconsistencies from these explicitly acknowledged external-validity
gaps. The existing `CEAV_M1_DOMAIN_DEPENDENCE_AUDIT.md` was inspected as prior
work, not treated as proof of correctness.

## Actual text inconsistencies

### C1 — T4 proof prints profitable-deviation inequalities as apparent equilibrium conditions

**Location:** `CEAV_M1_MANUSCRIPT_V0_2.md:308-321`, especially 312-313;
same lines in `review-package/docs/CEAV_M1_MANUSCRIPT_V0_2.md`.

The two displayed expressions are deviation-minus-H01 utility differences.
At neutral `b_i=0`, each equals `-7/500`, so the printed `>=0` does not hold,
although the proposition and neutral calculation correctly say H01 is strict
(`CEAV_M1_MANUSCRIPT_V0_2.md:256-261,300-306`). Owning implementation records
`neutral_gap=base-dev` and `slope=dev_release-base_release`
(`verification/dual_boundary.py:97-106`), while equilibrium constraints use
base-minus-deviation (`verification/dual_boundary.py:127-150`).

**Minimum edit:** use `<0` for strict H01 stability, or `<=0` when describing
the closed equilibrium interval, for the displayed deviation-minus-base
expressions. Alternatively negate both expressions and retain the appropriate
positive inequality. Explicitly identify whether the row describes profitable
deviation, weak equilibrium, or strict equilibrium. This is an editorial sign
inconsistency; it does not by itself show that the stored endpoint numbers or
engine inequalities are wrong.

### C2 — Three bibliography entries have incorrect author given names

**Location:** `CEAV_M1_MANUSCRIPT_V0_2.md:515-529`; reproduced at the same
lines in `review-package/docs/CEAV_M1_MANUSCRIPT_V0_2.md`.

| Entry | Current error | Owning primary source and correction |
|---|---|---|
| 4, *Incentivizing Evaluation with Peer Prediction and Limited Access to Ground Truth* | Gao is named “Siyu”. | Accepted manuscript cover and first article page name **Xi Alice Gao**, James R. Wright and Kevin Leyton-Brown. [Primary accepted manuscript](https://dspacemainprd01.lib.uwaterloo.ca/server/api/core/bitstreams/2cf2eab2-324c-402f-98eb-ee05f2a446f4/content), PDF pp. 1-2; DOI `10.1016/j.artint.2019.03.004`. |
| 6, *Putting Peer Prediction Under the Micro(economic)scope and Making Truth-telling Focal* | Kong is “Yiling”; Ligett is “Jennifer”. | The author-hosted page names **Yuqing Kong, Katrina Ligett**, and Grant Schoenebeck. [Primary author page](https://schoeneb.people.si.umich.edu/papers/PeerFocal.html), byline. |
| 7, *Equilibrium Selection in Information Elicitation without Verification via Information Monotonicity* | Kong is “Yiling”. | The article title page names **Yuqing Kong** and Grant Schoenebeck. [Primary ITCS article](https://drops.dagstuhl.de/storage/00lipics/lipics-vol094-itcs2018/LIPIcs.ITCS.2018.13/LIPIcs.ITCS.2018.13.pdf), p. 13:1; DOI `10.4230/LIPIcs.ITCS.2018.13`. |

**Minimum edit:** correct these bylines in the next editable manuscript/package
revision. This is an attribution error, not evidence against the substantive
prior-art comparisons. The bibliography primary-check document concentrates
on three other corrected entries (`CEAV_M1_BIBLIOGRAPHY_PRIMARY_CHECK.md`),
so its existence does not validate the remaining names.

### C3 — The brief's explanation of T5 incorrectly invokes coordinated deviations

**Location:** `CEAV_M1_EXTERNAL_RESEARCH_BRIEF.md:63`, also
`review-package/docs/CEAV_M1_EXTERNAL_RESEARCH_BRIEF.md:63`.

The explanation that the smaller boundary arises because “global deviations
can coordinate through equilibrium profiles” misdescribes the certified test.
Every candidate is checked against **unilateral** task-local deviations
(`CEAV_M1_MANUSCRIPT_V0_2.md:330-352`;
`configs/dual_boundary.json:18`; `verification/dual_boundary.py:127-134`).
The bad profile has two L1 reporters in one branch, but it is supported by
individual best responses, without modeling a coordination process.

**Minimum edit:** replace that clause with “because additional bad pure
equilibrium profiles become sustainable before All-H01 loses local stability.”
This is an inaccurate causal explanation; the brief does not explicitly claim
coalition-proofness, and the limitations expressly exclude coalitions
(`CEAV_M1_EXTERNAL_RESEARCH_BRIEF.md:77-79`). Do not relabel this as a proved
coalition attack or claim that the model demonstrates how agents coordinate.

## Editorial ambiguity, not an engine error

The abstract says the risk-dependent lottery determines whether `T` is observed
for the final decision (`CEAV_M1_MANUSCRIPT_V0_2.md:22-24`). More precisely,
the final decision uses `T` on **either** audit event, including a payment-only
audit. The owning contract says g1 is used on the union
(`CEAV_M1_THEOREM_AND_COUNTEREXAMPLE_CATALOG.md:67-70`), and both computation
paths implement that rule (`verification/dual_boundary.py:68-74`;
`verification/dual_boundary_oracle.py:44-48`).

Minimum clarification: “A report-independent lottery supplies payment-audit
eligibility; a risk-dependent lottery supplies additional decision verification.
The final decision uses their shared audit whenever either event occurs.”
The later manuscript model does state the union correctly (165-169).

## Domain operationalization — conditional examples, not measured results

The following mappings are audit reasoning about whether the declared variables
could be operationalized. They are neither datasets nor claims that the
synthetic accuracies hold. All require a fixed acceptance contract/reference
time and a reference procedure separate from `T`; a reference disagreement
about the contract must remain unresolved rather than be converted to truth
by a vote (`CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md:41-55,57-90`).

| Domain | Possible narrow `Y`; corresponding `Z`, `X_i`, `T` | Trust, dependence and conflict boundary |
|---|---|---|
| Software / open-source | `Y`: a pinned release meets registered functional/artifact predicates in a specified environment. `Z`: public repository, build logs and demo. `X_i`: a reviewer's additional reproduction, code inspection or task-specific tests. `T`: separately executed acceptance inspection on the pinned artifact. | Reusing one CI pipeline, dependency chain or test oracle can produce shared errors despite separate reviewers. Maintainer, contributor, sponsor or competitor interests can affect release preferences. Passing finite tests does not establish absence of security defects, maintainability or future support. No source establishes accuracy or independence for these roles. |
| Creative projects / games | `Y`: a promised build, asset set, access feature or other observable contractual deliverable exists and meets a locked checklist. `Z`: trailer/demo/manifest. `X_i`: additional playtest or artifact/provenance examination. `T`: independent checklist-based build/artifact inspection. | Audience enjoyment, artistic merit and commercial success are different constructs; they are not automatically one objective binary state. Shared demo content, fandom or publisher interests can correlate labels/preferences. A checklist can support delivery acceptance without validating a broad artistic-quality claim. |
| Hardware / products | `Y`: specified units meet identified batch, quantity, dimensional and functional predicates at the declared time. `Z`: creator evidence and inventory. `X_i`: fresh inventory challenge or additional inspection. `T`: a separate physical acceptance inspection. | Supplier/recipient evidence can be a common source; access, destructive testing, travel and latent defects affect both accuracy and cost. Presence at one time does not establish ownership, durability or future safety. The desk protocol provides a concrete measurement design for one such narrow claim, explicitly excluding unsupported safety/lifetime claims (`CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md:14-29,45-48`). |
| Community / charity | `Y`: a specified delivery, construction or distribution predicate passes at the reference time. `Z`: public report and claimed receipts. `X_i`: additional recipient/item-level investigation. `T`: separate physical or documentary inspection appropriate to that predicate. | Recipient dependence, creator/donor affiliations and common evidence can threaten the same trust assumptions. Delivery is not equivalent to long-term benefit, welfare or community satisfaction. Charity is an application category, not the game definition; the desk protocol expressly excludes educational impact and other categories (14-19). |

Across all four domains, separate identities or teams do not imply independent
information. The existing protocol explicitly identifies shared defect type,
evidence, contacts and auditor capture as unverified risks
(`CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md:138-164`). These are plausible failure
channels to measure, not observed accusations or estimated error rates.

## What transfers, and what does not

1. **Factorization versus numerical truthfulness.** T3a's reward identity
   needs payment eligibility independent of the information/report and future
   `T`; it does not itself need mutual conditional independence of `Z,X_i,T`.
   That stronger independence and the symmetric sensitivities/specificities
   supply the frozen joint law and its exact numbers
   (`CEAV_M1_THEOREM_AND_COUNTEREXAMPLE_CATALOG.md:32-37,196-231`). In a new
   domain, High need not change the posterior modal label at all; the catalog
   already supplies this failure condition (226-230). A new domain cannot
   inherit `delta=2/25`, strict H01 or `7/500` just by naming its information
   channels public/private/audit.
2. **Bayesian calibration is conditional.** The table is Bayes-optimal under
   the stated H01 signal law and loss odds threshold, then intentionally
   frozen under deviations (`CEAV_M1_MANUSCRIPT_V0_2.md:129-147`;
   `CEAV_M1_THEOREM_AND_COUNTEREXAMPLE_CATALOG.md:67-70`). It is not an
   empirical posterior table for all campaigns or strategic report profiles.
   Changing prevalence, asymmetric Se/Sp, error dependence or acceptance
   predicates can invalidate transport of the table and every numerical gate
   without refuting the original finite calculation.
3. **External-interest bounds are not screening guarantees.** Linear
   `b_i*P(D=1)` permits affine inequalities, but self-report/conflict proxies
   do not establish a bound on any individual Judge. `b=1/10` is not
   automatically ten percent of a real payout
   (`CEAV_M1_EMPIRICAL_TRUST_PROTOCOL.md:288-298`). The five tested vectors do
   not certify arbitrary heterogeneous preferences
   (`review-package/KNOWN_LIMITATIONS.md:10-13`).
4. **Cash is review/audit spending, not escrow accounting.** The code computes
   cash as reward plus audit and operating costs, while WrongPayout is a
   separate expected error metric (`verification/dual_boundary.py:82-86`;
   `configs/dual_boundary.json:8-12`). It does not model fund ownership,
   who can submit an on-chain transfer, settlement failure, recovery or
   duplicate release. Those cannot follow from the reserve/cash gate. This
   is consistent with the explicit absence of settlement/production
   integration (`review-package/KNOWN_LIMITATIONS.md:27-28`), not a discovered
   cash-calculation bug.

## Focused prior-art verification

Primary sources were opened directly on 2026-10-25. This audit checked specific
existing claims, not firstness or completeness of the literature search.

| Existing claim | Primary check | Disposition |
|---|---|---|
| Limited trusted noisy evaluations and low-cost uninformative equilibria predate CEAV (`CEAV_M1_NOVELTY_AUDIT_T3_T5.md:61-66,258-266`). | Gao et al., [accepted manuscript](https://dspacemainprd01.lib.uwaterloo.ca/server/api/core/bitstreams/2cf2eab2-324c-402f-98eb-ee05f2a446f4/content), abstract and introduction, PDF pp. 2-4. | Supported as adjacent prior art; no claim that its guarantees transfer to this game. |
| Report-sensitive spot checking is prior art (same audit:56-60,128-132). | Zarkoob, Fu and Leyton-Brown, [AAMAS 2020 primary article](https://www.ifaamas.org/Proceedings/aamas2020/pdfs/p1593.pdf), p. 1593 abstract and p. 1594 introduction. | Supported: checking can depend on reported grades under that paper's model. This does not establish that CEAV's exact dual-lottery architecture is new. |
| Direct utility for the induced decision can distort expert reporting (same audit:220-227). | Craig Boutilier, [AAMAS 2012 primary article](https://www.cs.toronto.edu/~cebly/Papers/Boutilier_aamas12.pdf), abstract and sections 3-4. | Supported. Compensation with known utility and bounds under utility uncertainty are prior work; do not turn this into a universal claim that a known bound alone guarantees exact truthfulness for arbitrary mechanisms. |
| Truthful equilibrium and uninformative equilibria/focality are distinct (same audit:258-274). | [Kong–Ligett–Schoenebeck author page](https://schoeneb.people.si.umich.edu/papers/PeerFocal.html), abstract; [Kong–Schoenebeck ITCS article](https://drops.dagstuhl.de/storage/00lipics/lipics-vol094-itcs2018/LIPIcs.ITCS.2018.13/LIPIcs.ITCS.2018.13.pdf), pp. 13:1-13:2. | Supported. No CEAV mixed-equilibrium, selection-process or coalition guarantee follows. Author bylines need C2 corrections. |

The candidate/instance-level wording and open-priority caveats are already
appropriate (`CEAV_M1_MANUSCRIPT_V0_2.md:100-106`;
`CEAV_M1_NOVELTY_AUDIT_T3_T5.md:326-343`;
`review-package/KNOWN_LIMITATIONS.md:30-38`). There is no need to invent a
novelty defect merely because the underlying ingredients have prior art.

## Minimum editorial disposition and verification boundary

Correct C1-C3 and clarify the union sentence in a subsequent editable revision;
preserve frozen evidence. Optionally add one sentence to the introduction and
brief: “FundTogether motivates general-purpose milestone crowdfunding;
CEAV-M1 abstracts one observable escrow acceptance task, and charity is one
application.” Label the school-desk study a concrete physical-acceptance
exemplar. These additions clarify product scope; they do not add an empirical
or decentralization guarantee.

Verification performed here: inspected the named documents and their package
copies; traced timing/calibration/payment/cash/unilateral constraints to config,
analyzer and independent oracle; opened the primary sources above. No engine
suite or browser flows were rerun, no new accuracy or field estimates were
computed, and this note does not claim a fresh proof/certificate revalidation.
Only textual corrections are proposed. No mechanism development, retuning,
V7, production integration or empirical collection is proposed or performed.
