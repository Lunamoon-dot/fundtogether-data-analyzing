# CEAV-M1 V5.0 — Audit-Grounded Incremental Information Scoring (AGIIS)

**Status:** `SPECIFIED` — Phase 1 research specification; not a verified mechanism and not a production engine.

**Revision:** `v5.0-agiis-phase1-r1` (2026-10-24)

**Scope:** exact feasibility analysis for probabilistic forecasts scored against a noisy trusted audit. This revision does not add CLI, API, UI, blockchain settlement, peer coupling, collusion, stake, slashing, appeals, or correction of the majority decision.

## 1. Research questions

V5 separates four claims:

1. whether a Judge pays for private information `X_i`;
2. whether a Judge truthfully reports a probability about the scored event `T`;
3. whether the resulting calibrated decision improves false approval, false rejection, and wrong payout under `Y`;
4. whether the payment is feasible under the reward and audit budgets.

Strict propriety for `T` is not a claim that the report is automatically truthful about `Y`, nor that effort is induced.

## 2. Information and timing

There are three Judges, hidden binary ground truth `Y`, public binary signal `Z`, private binary signal `X_i`, and noisy trusted verification signal `T`. A Judge chooses `L` or pays cost `c_i` for `H`; only after `H` is chosen is `X_i` observed. The report is locked before claim-level audit `A~Bernoulli(q)`. If `A=1`, one common `T` is used to score all Judges. `T` is conditionally independent of `Z` and `X_i` given `Y`.

Low information is `I_L=Z`; high information is `I_H=(Z,X_i)`. The forecast target is `T`:

```text
p_L(z)     = P(T=1 | Z=z)
p_H(z,x)  = P(T=1 | Z=z, X_i=x)
```

The baseline `p_0(z)=p_L(z)` is model-defined and announced before reporting. It is never estimated from reports on the same task.

## 3. Quadratic score and payment variants

The normalized quadratic score is

```text
S(p,t) = 1 - (p-t)^2,       0 <= S <= 1.
```

### V5.0-A: shifted incremental Brier

```text
G_i = S(p_i,T) - S(p_L(Z),T),       -1 <= G_i <= 1
R_i = f + mu*A*(1 + G_i)
```

The payment is nonnegative and lies in `[f, f+2*mu]`. The per-claim reserve cap is

```text
3*f + 6*mu <= B.
```

The expected cash cost is expected Judge reward plus `q*kappa + operatingCost`. Effort cost is a Judge utility term and is not paid again as cash.

### Direct Brier ablation

```text
R_i = f + mu*A*S(p_i,T)
```

This remains strictly proper when `mu*q>0`, but it is not a baseline-improvement payment. It has realized payment range `[f,f+mu]` and reserve cap `3*f+3*mu<=B`. Its expected high-versus-low score improvement is still `mu*q*Delta_i(z)`; the accounting floor differs from V5.0-A.

Spherical or another bounded strictly proper score is out of scope unless a later Phase 1 revision names one prior-art rule and proves its bound and feasibility. Brier, its affine shifts, and baseline subtraction are not claimed as new inventions.

## 4. P5-1 — strict propriety for the scored event

For a Judge's information `I`, let `p*=P(T=1|I)`. Then

```text
E[S(p,T) | I] = 1 - Var(T|I) - (p-p*)^2.
```

Thus `p*` is the unique maximizer over `[0,1]` when the coefficient `mu*q` is positive and no other payoff depends on `p`. When `mu*q=0`, the mechanism makes no strict-truthfulness claim.

This is a theorem about reporting the posterior of `T`.

## 5. P5-2 — value of private information

For each Judge and public branch,

```text
Delta_i(z) = E[(p_H(z,X_i)-p_L(z))^2 | Z=z].
Gain_i(z)  = mu*q*Delta_i(z) - c_i.
```

Strict high effort requires `Gain_i(z)>0`. Equality keeps both `L` and `H` as tied best responses. If `mu_max*Delta_i(z)<=c_i`, where `mu_max=(B-3f)/6` for V5.0-A, no valid `mu,q` can create strict high effort on that branch.

## 6. Noise attenuation and decision calibration

Let `a=1-specificity_T` and `d=sensitivity_T+specificity_T-1`. Then

```text
p_T(I) = a + d*p_Y(I)
Delta_T(i,z) = d^2*Delta_Y(i,z).
```

For `d>0`, the calibrated ground-truth posterior is

```text
p_Y = (p_T - (1-specificity_T))/d.
```

The binary vote is deterministic from `p_Y` using a preregistered threshold `1/2` and fixed tie rule. No unscored independent vote is accepted. Majority remains 2-of-3 and is not corrected by `T`.

## 7. Fixtures and baselines

F51-01 inherits F41-01: `pi=1/2`, public and private sensitivity/specificity `19/20` and `4/5`, audit sensitivity/specificity `9/10`, costs `1/20`, `B=6`, `f=0`. The exact benchmarks are

```text
Delta_Y = 3249/708400
Delta_T = 3249/1106875
```

F51-02 uses public sensitivity/specificity `7/10`, private `4/5`, audit `9/10`, cost `1/20`, `B=6`, `f=0`:

```text
Delta_Y = 3969/58900
Delta_T = 15876/368125
```

V3-HET inherits `configs/v3/heterogeneous_anchor.json`, uses `f=1/10`, `B=6`, and evaluates each Judge and each `Z` branch separately. Target-population weights are derived from `pi` and the public signal; batch weights remain separate.

The comparison set is Public-Z-only, V3 binary audit-only, V5.0-A, Direct Brier, and the compatible V4.1 hybrid reference. All use the same signals, prior, costs, audit quality, `B`, `kappa`, operating cost, majority rule, gates, and target weights. Binary baselines may use every deterministic map `H00/H01/H10/H11`.

## 8. Phase gates and limits

Phase 1 produces an independent Fraction oracle, exact fixture certificates, feasibility bounds, and immutable hashes. It does not claim a continuous policy optimum, a selected equilibrium, robustness beyond the declared fixtures, or production readiness.

If V5.0-A has no meaningful budget-feasible strict-effort region, that prototype is closed with a negative result. Direct Brier may proceed only if its distinct cap and cash accounting leave a meaningful candidate. No Phase 2 engine is opened solely to repeat a negative result.

