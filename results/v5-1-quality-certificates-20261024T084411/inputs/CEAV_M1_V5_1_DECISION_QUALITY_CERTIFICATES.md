# CEAV-M1 V5.1 — Phase 1.5 Decision-Quality & Baseline Dominance Certificates

**Status:** `SPECIFIED` for exact offline certificates; no full engine, API, UI, or production conclusion.

**Parent:** commit `2835559652b912536439c5b504da30ba68c91436` and the immutable V5 Phase 1 artifacts.

## Scope and fixed assumptions

This revision evaluates only F51-02 and V3-HET under the declared V5 signal model. `Y` is hidden ground truth, `Z` is public, each Judge's `X_i` is available only under high effort, and `T` is a common noisy trusted audit. The audit is claim-level, independent of reports, and the majority decision is not corrected by `T`.

All arithmetic is exact `Fraction`. The decision vote is deterministic from the calibrated posterior `p_Y` with threshold `1/2` and the fixed tie rule `p_Y>=1/2 -> 1`. Forecasts are probabilities for `T`, not direct reports of `Y`.

## Certificate 1 — F51-02 dominance comparison

Fixed `B=6`, `f=0`, `kappa=0`, payout value `1`:

| Policy | Mechanism | `mu` | `q` | `s=mu*q` |
|---|---|---:|---:|---:|
| Direct | `R=mu*A*S(p,T)` | `2` | `3/5` | `6/5` |
| Binary audit-only | `R=mu*A*1(v=T)` | `2` | `1/2` | `1` |

The oracle must report every Judge's effort best response, posterior forecasts, deterministic vote maps, equilibrium profile, accuracy, conditional `FA` and `FR`, unconditional wrong-payout probability/value, realized reward cap, audit exposure, and expected cash cost.

## Certificate 2 — V3-HET Direct Brier

Fixed `f=1/10`, `mu=19/10`, `q=4/5`, `B=6`, `kappa=0`, payout value `1`. The required response profile is checked branch-by-branch, including the probability forecast for every Judge and `(Z,X)` observation. The certificate tests whether the resulting majority is `D=Z` and reports quality using conditional `FA=P(D=1|Y=0)`, `FR=P(D=0|Y=1)`, and unconditional wrong-payout value.

## Certificate 3 — V3-HET budget lower bound

Let `s=mu*q`. For Direct Brier, Judge B at `Z=0` has exact `Delta_T=49/775` and effort cost `1/10`, so

```text
s >= (1/10)/(49/775) = 155/98
```

is necessary for high effort to be weakly optimal. Equality is a tie; strict induction requires `s>155/98`.

At `s=155/98`, the cheapest response selection keeps B low at the tie while A takes high effort in both branches; C stays low. The certificate evaluates this lower-cost profile and the alternative tie resolution with B high at `Z=0`. If even the cheapest profile has target-population cash cost above `4`, then no budget-valid Direct Brier policy under the fixed V3-HET `f=1/10`, `B=6`, `kappa=0` assumptions can strictly induce B at `Z=0` while meeting the cash gate.

This is a fixed-environment Direct Brier result. It is not an impossibility theorem for another scoring rule, another budget, another `f`, or another signal environment.

## Decision rule

Direct Brier receives a Phase 2 `GO` only if it has a non-dominated decision-quality/economic opportunity after the exact baseline comparison. If F51-02 is dominated and the V3-HET B-entry region violates the cash gate, the result is `NO-GO` for a larger Direct Brier screening study. The result does not close all probabilistic scoring research.

