# V4 conditional multi-task scoring: primary-source boundary

Checked directly against primary papers on 2026-10-24. Research note only: no V4 engine, acceptance result, or production mechanism is established here.
Read with [PRIMARY_SOURCES.md](PRIMARY_SOURCES.md); this note adds literature relevant to the proposed V4 game without changing V1–V3.1.

## 1. Verified sources and transferable claims

### S1 — Binary agreement minus an independent-task baseline

**Dasgupta, A.; Ghosh, A. (2013). _Crowdsourced Judgement Elicitation with Endogenous Proficiency_. WWW, 319–330.**
[Official proceedings PDF](https://archives.iw3c2.org/www2013/proceedings/p319.pdf) · [DOI](https://doi.org/10.1145/2488388.2488417)

- **Locator:** §2; §3, Definition 2 / Eq. (1)–(2), printed pp. 321–323; §4–5.
- The binary score subtracts agreement expected from report frequencies on non-overlapping tasks; `d=1` uses one other task per rater.
- Its effort model has zero-effort proficiency `1/2`, homogeneous task priors, effort-dependent proficiency, and reward scaling relative to effort cost. Independence of baseline-task reports is explicit.
- This is direct prior art for the prototype's agreement-minus-baseline ingredient, not a new scoring idea attributable to V4.
- **Not transferred:** free task-specific shared `Z` changes the information structure. The paper's high-effort / maximum-payoff equilibrium results do not prove uniqueness, desired-effort selection, or the V4 game. The paper separates elicitation from optimal report aggregation.

### S2 — Correlated Agreement (CA)

**Shnayder, V.; Agarwal, A.; Frongillo, R.; Parkes, D. C. (2016). _Informed Truthfulness in Multi-Task Peer Prediction_. EC, 179–196.**
[Authors' full paper, arXiv PDF](https://arxiv.org/pdf/1603.03151) · [DOI](https://doi.org/10.1145/2940716.2940790)

- **Locator:** §2; Definition 3.1 / Eq. (15); Definition 5.1 / Theorem 5.2; §5.5, “Unintended Signals”.
- CA scores a same-task pair minus a distinct-task pair using `S(a,b)=1{Delta(a,b)>0}`, where `Delta` is joint probability minus product of marginals.
- The model uses at least three tasks, iid signal pairs, exchangeable agents, uniform report channels, and hidden bonus/penalty roles.
- Informed truthfulness ranks payments across channels; it does not require every equilibrium to be truthful. Costly effort needs an adequate payment margin.
- §5.5 explicitly warns that cheaper unintended signals can yield more favorable correlation and payments.
- **Not transferred:** hardcoding equality is CA only under the appropriate conditional sign structure. A free shared `Z`, effort chosen after `Z`, three-player incentives, and incomplete conditioning require separate proofs.

### S3 — Low-cost signals and limited ground truth

**Gao, X. A.; Wright, J. R.; Leyton-Brown, K. (2019). _Incentivizing Evaluation with Peer Prediction and Limited Access to Ground Truth_. Artificial Intelligence 275, 618–638.**
[Institutional accepted manuscript, full text](https://dspacemainprd01.lib.uwaterloo.ca/server/api/core/bitstreams/2cf2eab2-324c-402f-98eb-ee05f2a446f4/content) · [DOI](https://doi.org/10.1016/j.artint.2019.03.004)

- **Locator:** §2, Definition 1; §3, Theorem 1; §4, Eq. (2), Lemma 1, Theorem 2.
- Theorem 1 says: for each **universal** report-only mechanism with additional positive high-quality-signal cost, there exists a multi-signal environment where the truthful equilibrium is not Pareto dominant.
- Universality requires detail-free truthful-equilibrium guarantees for any task count and `n>=3`; §2 explicitly excludes CA and CA-DF from that class.
- Spot-checking assumes trusted noisy evaluations, categorical signals, stationary strategies, and a specified payment. Theorem 2 compares audit probabilities under a sufficient condition involving a no-effort equilibrium.
- **Not transferred:** neither theorem proves V4's all-Low equilibrium, an arbitrary audit threshold, or that every peer/audit hybrid is inferior. V4 with no trusted reports receives no spot-checking guarantee.

### S4 — Closest verified baseline generalization: heterogeneous tasks

**Mandal, D.; Leifer, M.; Parkes, D. C.; Pickard, G.; Shnayder, V. _Peer Prediction with Heterogeneous Tasks_. CrowdML workshop (2016); arXiv v2 (2017).**
[Authors' arXiv v2 PDF](https://arxiv.org/pdf/1612.00928v2) · [Author's publication record](https://parkes.seas.harvard.edu/publications/peer-prediction-heterogeneous-tasks)

- **Locator:** §2; §3, Algorithm 1 / Eq. (2), Theorems 2–3; §3.4 (CCAH).
- CAH corrects the delta matrix for the baseline distribution induced by heterogeneous penalty tasks; a naive per-task CA extension can fail.
- Its main analysis assumes independent tasks, exchangeable agents, only task type plus costly signal as information, and the same reporting strategy across tasks. The authors flag the last restriction as substantive for heterogeneous tasks.
- Theorem 2 requires symmetric, entrywise nonzero adjusted delta matrices; stronger truthfulness requires additional sign conditions. CCAH additionally accounts for cross-task correlations.
- **Not transferred:** these are not theorems for the proposed `Z`-stratified game or arbitrary `Z`-dependent effort/report policies. They are close prior art against claiming that correcting cross-task baselines or handling task types is itself new.

### S5 — Direct precedent for conditioning out cheap shared information

**Lu, Y.; Xu, S.; Zhang, Y.; Kong, Y.; Schoenebeck, G. (2024). _Eliciting Informative Text Evaluations with Large Language Models_. EC.**
[Authors' full paper, arXiv v4](https://arxiv.org/pdf/2405.15077v4) · [Primary publication metadata](https://arxiv.org/abs/2405.15077)

- **Locator:** §3, Definitions 3.2–3.3; §4.3, Definition 4.3; Assumption 4.1; Propositions 4.5/4.7.
- GSPPM conditions a log-score peer predictor on a commonly known synopsis to reduce rewards for cheap shortcut information. This is direct prior art for that broad motivation, although its score is not V4's equality difference.
- Guarantees assume common knowledge of a sufficiently accurate conditional predictor (KL-error bound), positive residual information, and suitable payment scaling. The best-response analysis fixes a high-effort, truthful peer.
- **Not transferred:** an approximate truthful equilibrium does not remove all low-effort equilibria. The result does not establish V4's exact score, stationary three-Judge game, audit threshold, or a guarantee without its predictor assumptions. V4 does not require an LLM.

## 2. Elementary V4 derivation, not an imported theorem

The following statements are our algebra for the proposed prototype. They are not attributed to S1–S5 as new literature theorems.

Fix a positive-probability stratum `Z=z`, observable to the scorer and exogenous to reports. Let `t,u` be distinct tasks in that stratum, with iid task draws conditional on their stratum labels.
Use stationary, task-independent effort/report policies within each stratum; no report depends on its task identifier, peer report, or shared random seed beyond `Z`. The prototype reuses the focal report from task `t` in both terms; it does not require the three distinct bonus/penalty tasks used in S2.
For a fixed other Judge `j`, define the pair score:

```text
s_i(j,z) = 1{R_i,t = R_j,t} - 1{R_i,t = R_j,u}
```

Independent baseline draws and equal within-stratum marginals give:

```text
E[s_i(j,z)]
  = sum_a [P(R_i=a,R_j=a | z) - P(R_i=a | z)P(R_j=a | z)]
  = 2 Cov(R_i,R_j | z)                         [binary reports coded 0/1]
```

Thus the score rewards **residual report correlation**, not accuracy or effort by definition. Its sign need not be positive for an arbitrary signal model.
This remains true when the three-Judge score averages its pair scores over the two other Judges, or uses an exogenously selected peer.

If a peer reports deterministically `R_j,t=g_j(Z_t)`, its report is constant `g_j(z)` inside the stratum. For any focal report, even one chosen using extra task information:

```text
s_i(j,z) = 1{R_i,t=g_j(z)} - 1{R_i,t=g_j(z)} = 0.
```

Therefore, when both peers use deterministic Low policies, the focal Judge has zero expected peer score under either Low or High.
The pair-score terms cancel **statewise**, including High deviations, even if Judges use different `g_i`. Averaging over all other tasks within the stratum preserves the cancellation.
For utility `f + lambda*(1+E[score]) - c_i(z)*1{High}`, with `c_i(z)>0`, acquiring High strictly loses cost; changing only a Low report ties.
Every deterministic all-Low profile in this restricted stationary game is consequently a **weak Nash equilibrium**, including all-copy-`Z`, all-0, and all-1. This is conditional on each reachable `z`, not merely ex ante.
The offset preserves incentives and pays `f+lambda` at centered score zero; zero score does not mean zero payment. Nonnegative costs suffice for equilibrium existence; strict positivity makes High strictly worse against Low peers.
It does not prove stability against coalitions, adaptive policies, mixed-strategy equilibrium completeness, or a learning process; no equilibrium selection is implied.

For comparison, an **unconditioned** baseline with all reports equal to task-specific binary `Z` yields `1-[p^2+(1-p)^2]=2p(1-p)` for `p=P(Z=1)`.
Conditioning removes this particular source of public-signal payment; it does not create a unilateral reason to acquire information when all peers remain Low.

## 3. Claim / evidence map and novelty wording

| Proposed claim | Evidence and permissible wording |
| --- | --- |
| Same-task agreement minus independent-task agreement | Established ingredient: S1, S2. |
| Baseline must match the relevant task distribution | Established close precedent: S4; V4's exact stratum formula is specified and derived here. |
| Condition out commonly known shortcut information | Direct motivation precedent: S5; no broad novelty claim is justified. |
| Generic peer prediction can reward an unintended cheap signal | Explicit warning: S2 §5.5; quantified universal-mechanism limitation: S3 Theorem 1. |
| Copying `Z` gets zero conditional expected score | Elementary V4 cancellation above; depends on matching within-stratum marginals. |
| All-Low survives without audit | Elementary V4 unilateral-deviation proof above; no literature theorem is imported. |
| Audit can remove the bad equilibrium | Research question; must specify audit observation, cost, score, timing, and prove the exact condition. S3 supplies motivation, not V4 acceptance. |
| Conditional score is novel | **Unsupported.** No comprehensive novelty review was performed. |

Safe positioning: a research prototype applying known multi-task debiasing ingredients to a specified public-signal/effort game, with exact comparisons and explicit failure cases.
Do not call it a new CA mechanism, claim unique high-effort equilibrium, or infer better decision accuracy from expected score.
Conditioning on an observed `Z` cannot remove other omitted shared signals; finite-stratum sample availability, role assignment, stationarity, and baseline independence need separate implementation/verification contracts.
