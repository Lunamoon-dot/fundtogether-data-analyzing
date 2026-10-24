# V6 RAVE: primary-source boundary

Checked on 2026-10-24 for Phase 0–1. This is a focused prior-art note, not a systematic literature review or a novelty claim. It does not establish V6 equilibrium acceptance or authorize Phase 2.

V6 combines a binary settlement decision, costly noisy information, and strategic reports. These are established research subjects. The exact V6 timing, reward rule, finite strategy class, calibration contract, and certificates must be derived and verified separately.

## 1. Decision-theoretic information value

### S1 — Information value depends on consequences

**Howard, R. A. (1966). _Information Value Theory_. IEEE Transactions on Systems Science and Cybernetics 2(1), 22–26. DOI `10.1109/TSSC.1966.300074`.**

[Publisher record and abstract](https://ieeexplore.ieee.org/document/4082064/)

- **Access boundary:** publisher-indexed abstract and metadata were available; the full IEEE page presented an access challenge. No page-specific theorem from the inaccessible text is used here.
- The abstract connects probabilities with the economic consequences of decisions when valuing information. This supports using declared asymmetric loss, rather than entropy reduction or raw signal accuracy, as the V6 objective.
- **Not transferred:** any strategic-reporting, selective-audit, or equilibrium guarantee. The V6 binary threshold and value-of-information inequality are proved directly in the V6 feasibility work.

### S2 — Sequential information gathering and stopping

**Krause, A.; Guestrin, C. (2009). _Optimal Value of Information in Graphical Models_. Journal of Artificial Intelligence Research 35, 557–591. DOI `10.1613/jair.2737`.**

[Authors' full paper](https://arxiv.org/pdf/1401.3474) · [Official journal volume](https://ocs.aaai.org/Press/Journals/jairvol35.php)

- **Locator:** §2–2.2, decision-theoretic local reward and observation cost; §4.2.1, Eq. (4)–(5), printed pp. 567–568; Proposition 8 and Proposition 9.
- The paper distinguishes selecting observations in advance from conditional plans that use only already observed values. Its recursion compares stopping with buying another observation and then acting optimally.
- Its decision-theoretic objective optimizes terminal utility under a specified distribution. Monotonic information value concerns the ability to use more information before subtracting observation costs; it does not imply every costly observation should be purchased. Decision-theoretic value need not be submodular.
- **Not transferred:** strategic agents, report-dependent changes in the data distribution, or a guarantee for the V6 payment game. Its sequential-plan budget is a maximum path cost; V6's expected audit exposure, expected cash, and reward reserve are distinct constraints. A single optional V6 audit needs a finite comparison, not a general planning engine.

## 2. Selective verification under strategic reports

### S3 — Verification and allocation must be designed together

**Ben-Porath, E.; Dekel, E.; Lipman, B. L. (2014). _Optimal Allocation with Costly Verification_. American Economic Review 104(12), 3779–3813. DOI `10.1257/aer.104.12.3779`.**

[Publisher record](https://www.aeaweb.org/articles?id=10.1257/aer.104.12.3779) · [Institutional full manuscript, March 2014](https://www.bu.edu/econ/files/2014/05/Lipman-Optimal-Allocation-with-March-2013.pdf)

- **Locator:** manuscript §2–3; §7 discussion of noisy verification. The linked manuscript's cover says March 2014 despite its filename.
- A principal allocates one object among privately informed agents, who prefer receiving it. Checks are costly and reveal an agent's type perfectly; monetary transfers are unavailable. Favored-agent mechanisms use a default allocation and verify sufficiently strong competing reports.
- This is direct prior art against claiming that selective costly verification of strategic reports is itself new.
- **Not transferred:** the favored-agent theorem, independent private types, perfect checks, or allocation optimality for V6. V6 Judges observe correlated evidence about one common hidden truth, pay effort costs, receive money, and can have external release preferences. Intermediate noisy-check regimes require separate analysis even in the paper's own discussion.

### S4 — Binary collective decisions and imperfect verification

**Erlanson, A.; Kleiner, A. (2020). _Costly verification in collective decisions_. Theoretical Economics 15, 923–954. DOI `10.3982/TE3101`.**

[Official journal record](https://econtheory.org/ojs/index.php/te/article/viewArticle/3101) · [Author's full published paper](https://andykleiner.github.io/MyWebsite/Erlanson%2C%20Kleiner%20-%202020%20-%20Costly%20Verification%20in%20Collective%20Decisions.pdf)

- **Locator:** §2; §3.1, Remark 1 and Theorem 1; §4.1, Lemma 2 and Theorem 2, printed pp. 935–937; §4.2.
- A principal chooses between a policy and the status quo using agents' privately held information, without transfers. The benchmark voting-with-evidence mechanism checks decisive claims; its incentive and optimality results rely on that model.
- The imperfect-verification extension sometimes requires checking agents who are not decisive. Its technology reveals the true type with probability `p`; otherwise it returns the reported type. A discrepancy certifies a lie, and repeated checks add no information.
- **Not transferred:** this is not V6's independent binary signal `T` with false positives and false negatives. A mismatch `r_i != T` cannot certify a V6 Judge lied. The paper's checks concern individual types, whereas V6 buys one claim-level signal usable for all Judges. Its no-transfer preference assumptions and private-type independence differ from V6's effort/payment/common-truth game. Neither “check only pivotal reports” nor its imperfect-verification theorem establishes V6 incentive compatibility.

## 3. Noisy trusted evaluations and effort incentives

### S5 — Cheap-signal equilibria and limited spot checking

**Gao, X. A.; Wright, J. R.; Leyton-Brown, K. (2019). _Incentivizing Evaluation with Peer Prediction and Limited Access to Ground Truth_. Artificial Intelligence 275, 618–638. DOI `10.1016/j.artint.2019.03.004`.**

[Institutional record](https://uwspace.uwaterloo.ca/items/19ea8bc1-f265-48d7-8ce4-8591b86a928a) · [Full accepted manuscript](https://dspacemainprd01.lib.uwaterloo.ca/server/api/core/bitstreams/2cf2eab2-324c-402f-98eb-ee05f2a446f4/content)

- **Locator:** §2, Definition 1; §3, Theorem 1; §4, Definitions 4–8, Eq. (1)–(2), Theorem 2.
- The paper models costly evaluations, low-cost signals, and trusted noisy evaluations. Its universal-mechanism limitation has explicit quantifiers and does not assert failure of every report-only mechanism in every environment.
- Its spot-check comparison has a sufficient condition involving a no-effort equilibrium and its payments. The checked score includes an independent-object baseline; it is not V6's simple binary-match bonus. Its designer does not price agents' rewards as cash expenditure.
- **Not transferred:** a reward threshold for V6, a guarantee for report-dependent `q(z,r)`, or a theorem about correcting settlement decisions before transfer. The prior art motivates retaining cheap-signal equilibrium witnesses, not assuming they disappear after adding an audit. V6 must charge its own expected payouts, one audit cost per claim, and reserve cap explicitly.

## 4. V6 derivations and claim boundaries

The following are finite-model V6 deductions, not theorems imported from S1–S5.

Let `w=(z,r)` and fix the calibrated distribution. Let `p_w=P(Y=1|w)` and `ell(p)=min(C_FA*(1-p), C_FR*p)`.

```text
release threshold = C_FA / (C_FA + C_FR)
VOI(w) = ell(p_w) - sum_t P(T=t|w) ell(P(Y=1|w,T=t))
```

The option of ignoring `T` makes `VOI(w)>=0` under correct calibration and an unrestricted Bayes terminal decision. Strict improvement requires an audit outcome of positive probability that makes changing the pre-audit optimal action strictly beneficial. Merely increasing confidence need not change a binary decision. Audit cost and payment incentives are outside this inequality.

For fixed exogenous reports and fixed calibrated Bayes terminal rules, allocation reduces expected decision loss by `sum_w P(w) q(w) VOI(w)` relative to no audit under that same Bayes rule. At equal expected exposure, selective allocation can improve on uniform allocation when it shifts audit probability toward states with greater VOI. This is a conditional decision argument, not an equilibrium comparison. If the no-audit rule is majority instead, improvement after an audit can include correcting the initial aggregation rule as well as acquiring information; report those contributions separately.

For a published randomized rule whose coin uses only `w`, conditioning on the audit event adds no further truth information once `w` is known. Selection must not use the realized future `T`. The calibrated posterior table and its off-support actions must remain fixed when evaluating deviations. Re-estimating the table from a deviating strategy would change the tested mechanism.

| Proposed V6 claim | Evidence required |
| --- | --- |
| Additional information cannot increase optimal decision loss before costs | V6 conditional proof and exact oracle; decision-theory precedent S1–S2. |
| Selective verification is better at equal exposure | Exact comparison with the same calibrated report distribution, noisy audit, terminal-policy class, and exposure; not a universal literature theorem. |
| Selectivity preserves truthful reporting or High effort | Full frozen-policy unilateral deviations; S3–S5 supply related problems, not this result. |
| Disagreement measures correctness | Unsupported. Common-signal unanimous errors require explicit V6 witnesses. |
| Audits remove all bad equilibria | Every declared pure equilibrium must be checked; a favorable truthful profile cannot establish this. |
| Matching a noisy audit proves correctness | Unsupported; the audit itself can be wrong. |
| A positive Phase 1 result proves economic viability | Unsupported until cash, reserve, exposure, and worst-equilibrium gates pass. |
| V6 is a novel general selective-auditing mechanism | Unsupported by this focused source check. |

Safe positioning: a finite research prototype studying how known decision-theoretic verification ideas interact with a specified three-Judge effort/report game. Positive exogenous-report information value, strategic viability, and budget robustness remain separate questions.
