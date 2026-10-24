# CEAV-M1 V5.0 — Phase 1 Feasibility Contract

**Status:** `SPECIFIED`; exact offline analysis only.

## Fixed gates

The historical quality gates remain `FA<=1/5`, `FR<=1/4`, `WrongPayoutValue<=3/20`, and target-population `CashReviewCost<=4`. They are not tuned after observing V5 output.

## Necessary budget bounds

For shifted incremental Brier,

```text
mu_max_A = (B - 3*f)/6.
```

For direct Brier,

```text
mu_max_B = (B - 3*f)/3.
```

Negative numerators invalidate the policy. At fixed `mu`, strict effort requires `q > c_i/(mu*Delta_i(z))` whenever `Delta_i(z)>0`; equality is a tie, not strict entry.

## Expected payment checks

Under truthful posteriors, V5.0-A has conditional low-effort expected reward `f+mu*q` and high-effort expected reward `f+mu*q*(1+Delta_i(z))`. Direct Brier has low-effort expected reward

```text
f + mu*q*(1 - p_L(z)*(1-p_L(z)))
```

and adds `mu*q*Delta_i(z)` under high effort. These formulas are checked by finite enumeration.

## Initial exact certificates

For F51-01, `mu_max_A=1` and `Delta_T=3249/1106875`; therefore `mu_max_A*Delta_T < 1/20` and no branch can induce strict high effort for V5.0-A. For F51-02, `mu_max_A=1` and `Delta_T=15876/368125`; again `mu_max_A*Delta_T < 1/20`, so strict high effort is impossible under V5.0-A.

For V3-HET with `f=1/10`, `mu_max_A=19/20` and `mu_max_B=19/10`, the oracle reports each Judge x branch. The initial independent calculation gives:

| Judge | `Delta_T(z=0)` | `Delta_T(z=1)` | A max gain z=0 | A max gain z=1 | B max gain z=0 | B max gain z=1 |
|---|---:|---:|---:|---:|---:|---:|
| A | `147/3125` | `392/5625` | `-83/15625` | `1823/112500` | `2461/62500` | `9271/112500` |
| B | `49/775` | `12544/202275` | `-619/15500` | `-83107/2022750` | `78/3875` | `36061/2022750` |
| C | `9/775` | `7/450` | `-449/15500` | `-227/9000` | `-139/7750` | `-47/4500` |

These are feasibility certificates only. A positive branch gain does not prove that all Judges acquire information, that every equilibrium is good, or that any quality gate passes.

## Target versus batch accounting

All per-claim reward and audit formulas are reported in both target-population weighting `w_z=P(Z=z)` and declared batch weighting `v_z=n_z/N`. Actual batch cost is `N` times batch-average cost. No batch weight is substituted into the target cash gate.

## Stop decision

The initial result closes V5.0-A on F51-01 and F51-02 as infeasible for strict effort. V3-HET retains a mixed feasibility result and Direct Brier has a wider cap; a later Phase 1 screening may continue only to test that ablation and its decision-quality accounting. This document does not claim a positive mechanism result.

