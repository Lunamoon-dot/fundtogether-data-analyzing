# CEAV-M1 V6.0 — Risk-Adaptive Verification & Escalation

Revision: `v6.0-rave-phase01-r1`, 2026-10-24. Status: `SPECIFIED`.
Scope: Phase 0 and Phase 1 only; synthetic, finite exact research. No production
engine, API, UI, blockchain, or automatic Phase 2/3 execution.

## 1. Authority, provenance and decisions

The supplied V6 brief defines this new game. Primitive distributions and effort
costs inherit V3/V5; V3–V5 decisions were not corrected by the audit. Historical
specs/results remain immutable. Baseline commit is
`258d2178cfe11f67d8570484c49a9c91bd8c325e`.

Required context read: V3 anchor, V4 conditional, V4.1 feasibility/screening,
V5 information-scoring/feasibility, V5.1 decision-quality certificates, their
curated reports and manifests. V3.3 has 0/18 robust scenarios for each IPW
policy; V4.1 has no incremental hybrid dominance on its declared grid. V5.1
closes Direct Brier Phase 2: F51-02 is dominated by binary audit-only, and the
V3-HET B-entry cash lower bound exceeds 4. V6 does not reopen that hypothesis.

Implementation choice: two separate standard-library Fraction implementations.
The independent oracle sums potential `(Y,Z,X_A,X_B,X_C,T,A)` states; the checker
uses report likelihoods marginalized over private signals. Neither imports old
payoff/equilibrium code. Reuse is limited to the declared primitive values,
action semantics and quality definitions. V5 independent best responses do not
apply to report-dependent auditing.

## 2. Formal game and timing

Three mandatory-participation Judges A/B/C; hidden `Y~Bernoulli(pi)`; public Z;
potential private X_i. For signal S with sensitivity u and specificity v:
`K(1|1)=u, K(0|1)=1-u, K(0|0)=v, K(1|0)=1-v`.
Signals Z, X_i and T are mutually independent conditional on Y. T is noisy,
with sensitivity/specificity 9/10 in every primary fixture.

```text
Publish policy/reward/calibration/budget
 -> Nature samples potential signals; reveal Z
 -> each Judge chooses L or H; H costs c_i and reveals X_i
 -> binary reports locked
 -> A~Bernoulli(q(Z,r)) using only Z and locked reports
 -> if A=1 reveal T
 -> D_final=g_A(Z,r[,T])
 -> reviewer reward accounting and terminal release/reject
```

Potential T in integration is not an observed input to audit selection. Neither
Y nor unrevealed X_i/T enters q, g0, or the reward function. No transfer occurs
before the terminal decision. PENDING_AUDIT is temporary, never a success metric.
T is assumed external and trustworthy in distribution, not perfectly accurate.

Strategies are stationary task-local deterministic maps. At each z:
`L0,L1,H00,H01,H10,H11`; H maps are the two reports at x=0,1. H00/H11 still
pay effort cost. Preliminary `D0=1[sum(r)>=2]`.

`R_i=f+mu*A*1[r_i=T]`; `U_i=E[R_i]+b_i*P(D_final=1)-c_i*1[H]`.
Primary b=(0,0,0). A separate labelled diagnostic uses b=(1/10,1/10,1/10).
No negative or heterogeneous b sensitivity study is opened in this revision.
Reward reserve `3f+3mu<=B=6`; audit exposure cannot discount the reserve.

## 3. Frozen calibration and terminal decision

Primary calibration assumes every Judge reports X_i (H01 in both branches).
This is a design assumption, not an incentive theorem. Let h=(z,r). Compute

```text
m_y(h)=P(Y=y) K_Z(z|y) product_i K_i(r_i|y)
p(h)=m_1/(m_0+m_1)
p(h,t)=m_1 K_T(t|1)/(m_1 K_T(t|1)+m_0 K_T(t|0))
ell(p)=min(C_FA*(1-p), C_FR*p)
g0(h)=1[p(h)>=C_FA/(C_FA+C_FR)]
g1(h,t)=1[p(h,t)>=C_FA/(C_FA+C_FR)]
VOI(h)=ell(p(h))-sum_t P(t|h)*ell(p(h,t))
```

Main preregistered losses: C_FA=2, C_FR=1; release threshold 2/3; ties release.
Decision tables are constructed once before evaluating candidate/deviations.
Deviation changes the actual report distribution, not these posteriors/tables.
T may be ignored: g1 is not forced to equal T. Audit probability provides no
additional information after conditioning on h because q is a known function
of h and independent randomization. No equilibrium-consistent recalibration.

One separately labelled calibration stress table assumes copy-Z reports and
then evaluates actual H01 reports. Off-support reports fall back to the public
posterior, updated with T only when audited. This declared fallback avoids
silently using actual strategies to fill off-path states; it is a diagnostic,
not an optimized or primary policy. No parameter sweep or robustness claim.

## 4. Fixed study inputs and small allocation family

`configs/v6/rave_phase1.json` owns exact values. All fixtures are synthetic
assumptions, not real Judge/auditor measurements. B=6, payout value=1, operating
cost=0, mu=1, kappa=1/4, primary exposure ceiling=1/2. Kappa is a newly declared
V6 operating assumption; historical kappa=0 is not silently inherited.

| Fixture | pi | Z sens/spec | Private sens/spec; cost | f |
|---|---|---|---|---|
| F51-01 | 1/2 | 19/20,19/20 | all 4/5,4/5; 1/20 | 0 |
| F51-02 | 1/2 | 7/10,7/10 | all 4/5,4/5; 1/20 | 0 |
| V3-HET | 1/2 | 4/5,3/5 | A 9/10,4/5;1/20; B 3/4,19/20;1/10; C 13/20,7/10;1/25 | 1/10 |

Exogenous candidate: all H01. Only four selective allocations per fixture:

- Q1-zero: q_d=1, q_u=0.
- Q1-floor: q_d=1, q_u=1/4.
- Q2-z0: q(z=0)=1, q(z=1)=0.
- Q2-z1: q(z=0)=0, q(z=1)=1.

Retain exposure/cash/quality failures. For each allocation compute its exact
realized exposure e under H01, and compare Q0 constant q=e, with identical
g0/g1, f/mu/B/T/kappa. This is the exact best uniform policy at exposure <=e
for the primary decision-loss objective: loss is affine nonincreasing in q
by P6-1, and Bayesian g0/g1 minimize statewise calibrated loss over all binary
terminal rules. Hence the uniform baseline is optimized continuously, not a
deliberately weak grid point. If aggregate VOI=0 every q ties on decision loss.
Cash differences remain separate; no strategic uniform optimality is claimed.

B0 has two explicit records: true no-audit majority (q=0, rewards=3f), and
same-allocation majority with paid audits for incentive parity. B1=matched Q0
with correction; B2=Q1/Q2 with correction; B3=public-only Bayes (no Judges or
payments, diagnostic only); B4=Y oracle, `non_deployable_oracle`, no incentive
comparison. Also retain uniform q=0 and q=1 reference endpoints.

Attribution: compare B0 vs Bayes g0 at q=0 for decision-rule benefit; compare
selective vs matched uniform using identical g0/g1 for allocation benefit.

## 5. Theory gates and proofs

**P6-1 (conditional value of information).** For fixed calibrated h and finite
T, choose the same action after every t as the optimal action without T. It
has loss ell(p(h)); minimization separately for each t cannot do worse.
Thus VOI>=0. Equality holds when no positive-mass T outcome changes an optimal
decision (including ties with equal loss). Cost kappa can exceed VOI. This
does not assume reports stay truthful after a policy is announced.

**P6-2 (report dependence creates incentives).** Under disagreement-only audit
and all-copy-Z peers, staying unanimous earns f. A focal Low deviation to
1-z causes audit with certainty and earns `f+mu*P(T=1-z|z)`. For mu>0 and
noisy T this is strictly better at b=0. This is audit seeking/reporting bias,
not audit avoidance. Conversely at b=0, mu>0, disagreement-only auditing and
unanimous peers, joining unanimity from a Low dissent removes positive audit
reward and cannot improve reward. Audit avoidance is not assumed: full six
deviations are enumerated and exposure changes are recorded, including the
separate b diagnostic. No claim every selective rule is manipulable.

**P6-3 (unanimity is not correctness).** In all-copy-Z, D0=Z, preliminary
FA=1-spec_Z, FR=1-sens_Z. Q1-zero audits zero cases. Final decisions are
computed with the fixed declared tables; do not substitute recalibrated
public posteriors or assume g0 necessarily copies Z under all calibrations.

**P6-4 (endogenous exposure).** `E[A]=sum_h P_actual(h)q(h)`. Every deviation
must recompute P_actual and audit/reward/cash/release metrics. Q2's exposure
is report-independent; Q1's need not be. Exposure ceilings at H01 do not
establish ceilings at equilibrium.

**P6-5 (allocation criterion).** Under fixed calibrated reports, improvement
over matched uniform is `sum_h P(h)*(q(h)-e)*VOI(h)`. Positive covariance
with VOI can improve decision loss. The same identity explains equality or
negative Q2/Q1 results. No strategic conclusion follows.

**Branch factorization.** Fixed tables, q and per-task utility depend only on
the current z/local reports/T. No shared ex-ante constraint restricts a
Judge's strategy; exposure/cash gates evaluate policies, not feasible player
deviations. Expected utility is sum_z P(z) U_i(z), P(z)>0. Therefore a full
profile is a pure NE iff each branch has no profitable unilateral deviation.
This permits branch-local witness checks, not V5 independent best responses.

## 6. Metrics and acceptance contract

FA=P(D=1|Y=0), FR=P(D=0|Y=1), wrong payout=P(Y=0,D=1)*V.
Expected loss=C_FA*P(Y=0,D=1)+C_FR*P(Y=1,D=0). Do not add wrong payout to this
loss again. Accuracy, preliminary/final FA/FR, release probability, audit
exposure and audit rates conditional on each Y are distinct fields.

Cash=expected total reviewer reward+kappa*exposure+operating cost. Effort cost
is subtracted only in utility. Also report loss+cash as a declared common-unit
economic diagnostic, not a new gate or an empirically calibrated money value.
Target metrics use P(z) (V3-HET 2/5,3/5); show balanced-stratum cash separately.

Historical gates: FA<=1/5; FR<=1/4; wrong payout<=3/20; cash<=4; reserve<=6.
Additional V6 primary exposure<=1/2. A Phase-1 meaningful candidate requires
strictly lower calibrated decision loss than matched uniform, no greater
cash, and all these gates at H01. Failure records remain in certificates.
This is only candidate discovery, not a strategic pass.

Targeted profiles per policy: all H01; all-copy-Z; all L0; all L1; split-copy-Z
(A/B copy Z, C opposes Z). For each Judge and branch evaluate every one of six
deviations, freeze peers and policy; retain all argmax ties and candidate
utility, max regret, delta exposure/release/reward and effort. Evaluate b=0
before the labelled b diagnostic. A zero-regret witness certifies only that
profile. Do not count these as exhaustive enumeration of 216 profiles/branch.
Report witnessed equilibrium count and worst metrics among witnessed full
equilibria with profile IDs; total equilibrium count/worst-equilibrium metrics
are `not_computed_phase1`. Empty witness set is never robust pass.

Gate A requires this formalization, posterior proof and report-dependent
counterexample. Gate B requires a meaningful exogenous candidate. C/D are
`not_run_phase2`: no pure-equilibrium viability or budget-robustness certificate.
GO means permission is scientifically justified for a future Phase 2 request;
it does not execute Phase 2. Otherwise NO-GO; never open V6.1 automatically.

## 7. Interfaces, verification and freeze

Checker: `verification/feasibility_v6.py`: `load_study()`,
`decision_table(fixture, losses, calibration='H01')`,
`audit_table(kind, params)`, `evaluate(fixture, policy, decisions, profile,b)`,
`deviations(...)`, `run_certificate()`, `write_run(out)`.
Fixture/policy dictionaries use Fraction; profile is `(branch0,branch1)`, each
branch a three-action tuple. Audit table keys `(z, reports_tuple)`; decision
table same keys with posterior, g0, g1 tuple, state mass and VOI.

Independent oracle: `verification/oracle_v6_feasibility.py` uses only stdlib;
interfaces `decision_table(fixture, losses, calibration='H01')`,
`evaluate(fixture, policy, decisions, profile, b=(0,0,0))`. It must not import
the checker, CEAV engine, tests or old oracle. The two implementations share
input data and table formats only, never a Bayesian/scoring helper.

Policy fields: `audit` mapping; `f,mu,budget,kappa,operating_cost,payout_value,
exposure_limit,c_fa,c_fr`; metrics contain Fraction values and utilities
`utility_by_z[z][i]`. B0-majority is an alternate fixed decision table.

V6-T01 normalization/posterior/independence; T02 observables/no T leak;
T03 majority and noisy update/VOI; T04 frozen calibration and peers;
T05 actual audit exposure; T06 audit seeking/copy-Z witness;
T07 no-audit/uniform parity; T08 FA/FR orientation;
T09 cash/cap; T10 exact ties/all six actions; T11 witnessed worst metrics and
non-exhaustive stop handling; T12 target/batch weights;
T13 independent oracle parity; T14 immutable freeze/output refusal;
T15 calibration stress; T16 direct mutation probes.

Freeze before checker implementation: exact spec, feasibility contract, source
note, config, independent oracle, tests and plan. Use current UTC, raw SHA-256
and semantic config SHA-256; no backdating. Record oracle/test preparation as
pre-checker research work, not pre-oracle preregistration. Each run uses a new
directory with input/source/spec snapshots, certificate, report, manifest.
Mutation probes use temporary source copies and explicit failing test IDs;
missing/zero/skipped tests cannot pass. Historical shared code is unchanged;
run relevant V4/V5 regression, no browser claim for offline-only work.
