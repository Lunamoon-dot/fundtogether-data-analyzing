# CEAV-M1 independent proof review: T3–T5

Date: 2026-10-24

Review status: **PASS WITH EXPLICIT SCOPE LIMITS**

Decision: no proof defect was found that requires a new mechanism version,
parameter change, or expansion of the declared equilibrium grid.

This review checks the paper claims T3–T5 against the frozen dual-purpose
game. It is a mathematical and reproducibility review, not a claim of peer
review or literature priority. All calculations use `Fraction`; decimal
values are explanatory only.

## 1. Frozen evidence and review boundary

The review freezes the certified F51-02 witness:

```text
a=2/5, t=1/6 on S={Z=0, sum(reports)=2},
uniform d=19/1250, mu=2, B=6, kappa=1/4,
C_FA=2, C_FR=1, c=1/20,
Z accuracy=7/10, X accuracy=4/5, T accuracy=9/10,
actions={L0,L1,H00,H01,H10,H11}.
```

The payment and decision lotteries remain independent, the union audit is
charged once, the same trusted `T` is used on either route, and the match
bonus is paid only when `A_pay=1`. The review does not recalibrate the frozen
`g0/g1` tables under deviations.

Pinned evidence identities:

| Artifact | SHA-256 |
|---|---|
| `configs/dual_boundary.json` | `17001d4aabcc971bd29b68a690d5d6b26e0c4c9c41be5670d60e1cac19d9cce5` |
| `verification/dual_boundary.py` | `8c943bb2f6f23c5032768dd60834f9e926a1d6aa3f83205482b54f4a645d6d0b` |
| `verification/dual_boundary_oracle.py` | `bab19a553f73be9d843c0e199dd66b3ef2d0c25ab918f2e9b81dc8d9e4e4d3a9` |
| `verification/dual_boundary_audit.py` | `35dcbcf243ba20ba4d2f3fe0d7258de73667f5c012bc6b2807d271d916c0a6e9` |
| `verification/independent_t3_t5_review.py` | `d875505cd83c32e93c46c47445ff09f785574c78d01dc82a3c72903727dbb897` |
| frozen boundary certificate | `fde3ad4745b37e270469aaec2692a51c83cbcf5db7fcb0a16938296a6e25b7d5` |

The review runner is [`verification/independent_t3_t5_review.py`](verification/independent_t3_t5_review.py). Its output is deterministic and records the exact fractions below.

## 2. T3 review: separated payment and decision audits

### T3a factorization

The expected payment conditional on information `I` and locked report `r`
is

```text
E[R_i | I,r] = f + mu*a*P(T=r | I).
```

This follows because `A_pay` is independent of `I`, the report, peers and
future `T`, and only `A_pay` earns the match bonus. A report therefore cannot
change payment-audit eligibility. It can still change the expected match
payment, so the reward is a modal-label objective rather than a strictly
proper probability score.

An independent conditional enumeration gives, in both public branches,

```text
M_L = 33/50,
M_H = 37/50,
delta = M_H - M_L = 2/25.
```

At the certified point the net High-over-Low effort gap is

```text
mu*a*delta - c
= 2*(2/5)*(2/25) - 1/20
= 7/500 > 0.
```

This verifies the algebra used by T3a and the effort part of T3b. It does
not prove truthful reports for non-modal scoring, and it does not remove the
`b_i P(D_final=1)` term when a Judge has an external release preference.

### T3b fixed-environment feasibility

The analytic region in the catalog is conditional on the frozen primary
environment and on neutral Judges. Its effort condition is `a>5/16`; the
union bound is obtained from `u=(1-a)t` and `u <= 1/2-a`; reserve, cash and
quality expressions are then evaluated under the fixed calibration.

The review finds no algebraic contradiction. The strict inequality matters:
at `a=5/16`, High and modal Low tie and the all-Low branch can be an
equilibrium with `FA=FR=3/10`, violating both quality gates. Thus T3b is a
strict conditional feasibility proposition, not an open claim that every
point on the effort boundary is acceptable.

The selective-versus-uniform comparison is also conditional. It holds at
matched exposure and the same equilibrium report distribution because the
selective rule puts audit probability on the stated risk class `S`. It is not
a strategic comparison after arbitrary report deviations or external
interests.

**T3 finding:** proof accepted under its stated lottery independence,
calibration, neutral-utility and finite-action assumptions. No grid expansion
is required.

## 3. T4 review: exact local external-interest boundary

For a fixed Judge and fixed H01 peers, every deviation has affine utility
difference

```text
U(H01)-U(a) = intercept + b_i*slope.
```

The independent review recomputed the binding rows. The four exact
breakpoints are:

| Mechanism | Negative binding deviation | Positive binding deviation |
|---|---|---|
| Selective | `z=0, L0`: `-7/500 -(633/5000)b_i >= 0`, so `b_i >= -70/633` | `z=1, L1`: `-7/500 +(551/6250)b_i >= 0`, so `b_i <= 175/1102` |
| Uniform | `z=0, L0`: `-7/500 -(2070709/15625000)b_i >= 0`, so `b_i >= -218750/2070709` | `z=1, L1`: `-7/500 +(1365587/15625000)b_i >= 0`, so `b_i <= 218750/1365587` |

The remaining six-action rows in both branches are weaker bounds on the
intersection. The complete certificate retains all branch/action rows and
all pairwise indifferences; the independent potential-state review checks
the same exact utility and release values.

Therefore All-H01 is a strict local best-response profile exactly on the
open intervals

```text
Selective: (-70/633, 175/1102)
Uniform:   (-218750/2070709, 218750/1365587).
```

At either endpoint the binding deviation is a tie, and immediately outside
it is profitable. The older `|b_i|<7/500` condition remains a conservative
peer-profile-independent box because `|Delta release|<=1`; it is not a
mechanism-enforced bound and is not the maximal local interval.

The result is local: it freezes all peers at H01 and says nothing about
other equilibria, mixed strategies, coalitions, participation or whether
real Judges have those utility units.

**T4 finding:** exact local theorem accepted. No missing proof step was
found; the global-robustness question must remain separate.

## 4. T5 review: all-pure equilibrium quality boundary

For each branch profile `p` and scenario multiplier vector `v`, the review
uses the exact inequalities

```text
c_i(p_i,z)-c_i(a_i,z)
  + b*v_i*[s_z(p)-s_z(a_i,p_-i)] >= 0
```

for every Judge and all six actions. Each candidate therefore produces an
exact closed interval, a singleton, an unbounded interval or the empty
set. Full stationary equilibria are exactly the overlapping products of the
two branch intervals.

The independent completeness replay reports:

| Check | Result |
|---|---:|
| Branch candidates | 4,320 |
| Full profiles covered | 466,560 |
| Exact audit checks | 5,590 |
| `b` coverage | all real values, via interval cells |
| Mutant probes in the frozen certificate | 9 detected |

At symmetric preferences, the maximal all-pure gate-safe component containing
zero is

```text
Selective: (-70/633, 175/1922)
Uniform:   (-218750/2070709, 109375/1189451).
```

Both endpoints are excluded because weak bad equilibria exist there. In the
interior, All-H01 is the unique pure stationary equilibrium in this declared
class. At Selective `b=1/10`, the exact replay finds four pure equilibria:
All-H01 plus three permutations of the bad branch witness

```text
z=0: (H01,H01,H01)
z=1: (L1,L1,H01).
```

The three bad equilibria are strict in the interior of their interval and
fail `FA<=1/5`; their exact Selective `FA` is `1391/6250`. This is the
required separation between local truthful stability and a guarantee over
all equilibria.

The one-biased-Judge scenario and neutral scenario are included in the
certificate and the completeness audit. The finite theorem remains limited
to the five declared vectors `{000,100,010,001,111}`. It does not cover
arbitrary heterogeneous `b` in `R^3`, mixed or correlated equilibria,
coalitions, equilibrium selection, Sybil behavior, or participation.

**T5 finding:** exact finite pure-class theorem accepted. The counterexample
is a genuine strategic failure of global quality at modest positive `b`, not
a failure of the All-H01 local best response.

## 5. Reviewer disposition

| Claim | Disposition | Reason |
|---|---|---|
| T3a factorization and effort threshold | Accepted, conditional | Exact Fraction derivation; report objective is modal match, not proper scoring. |
| T3b neutral feasibility region | Accepted, conditional | Gate algebra and strict effort boundary are explicit; no policy optimality claimed. |
| T4 local boundary | Accepted | Exact affine rows and binding endpoints agree with the independent review. |
| T5 pure-class global boundary | Accepted, scope-limited | Exhaustive exact interval replay; no mixed/coalition/global heterogeneity claim. |
| “Mechanism enforces small `b`” | Rejected | The bound is an assumption or analysis domain, not an enforcement rule. |
| “T5 proves universal impossibility” | Rejected | It is one frozen finite mechanism and declared strategy class. |

The proof review therefore authorizes manuscript use of T3–T5 with the
scope labels above. It does not authorize V7, production deployment, or a
new reward search.

## 6. Reproduction commands

From the repository root:

```text
python -X utf8 -m verification.independent_t3_t5_review
python -X utf8 -m unittest tests.test_dual_boundary -v
```

The first command produced the exact T3/T4 values and the T5 replay summary
recorded here. The second command ran 10 focused tests and passed. Historical
V6 regressions and the immutable boundary certificate remain the evidence of
the broader study; this review did not rewrite them.
