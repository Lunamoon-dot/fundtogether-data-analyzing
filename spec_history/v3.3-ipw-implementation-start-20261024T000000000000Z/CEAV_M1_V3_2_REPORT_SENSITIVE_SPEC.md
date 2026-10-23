# CEAV-M1 V3.2 — Report-sensitive spot-checking

**Status:** specified for implementation on 2026-10-24.  
**Model version:** `ceav-m1-v3.2`.  
**Parent:** V3 anchor game (`ceav-m1-v3.0`) and the exhaustive pure-equilibrium machinery retained by V3.1.

## 1. Purpose

V3.1 showed that a high-accuracy all-High candidate can still fail the voluntary-effort test.  V3.2 tests one narrow mechanism change suggested by the incentive diagnosis: make the spot-check probability depend on the report that a Judge submits.

The question is whether a report-contingent audit creates a positive and robust private gain from acquiring the private signal, without changing the number of Judges, the signal model, the majority decision, or the equilibrium concept.

V3.2 is an incentive experiment. It is not evidence that a production auditor can observe ground truth, and it does not turn the decision into a post-audit correction.

## 2. Scope kept from V3/V3.1

- One binary claim with hidden ground truth `Y`.
- Exactly three Judges: A, B and C.
- One public signal `Z`; each Judge has one private signal `X_i` available only after High effort.
- Each Judge chooses `L` or `H` after observing `Z`, then submits a binary report and a peer prediction.
- The candidate decision is the majority of the three reports.
- Candidate strategies and unilateral deviations are searched in the six-action reduced normal form for each public branch: `L0`, `L1`, `H00`, `H01`, `H10`, `H11`.
- Arithmetic is exact `Fraction` arithmetic.
- The search keeps the existing branch decomposition: 216 six-action candidates per public branch and 432 branch candidates in total (equivalent to 6^6 full profiles when both branches are combined).
- Only pure-strategy equilibrium is certified. Mixed, correlated, coalition-proof, selected, and sequential equilibria remain outside scope.

## 3. New report-sensitive audit game

V3.2 replaces the single scalar audit probability `q` with two probabilities:

```text
q0 = P(A_i = 1 | report r_i = 0)
q1 = P(A_i = 1 | report r_i = 1)
```

`A_i` is an independent spot-check event for Judge `i`. The verification signal `T` is still generated from the same hidden `Y` with configured sensitivity and specificity. Conditional on `Y`, the `T` draw is shared by the three Judge checks; the audit events `A_A`, `A_B`, and `A_C` are independent conditional on each submitted report.

This individual-audit definition is deliberate. A single common audit cannot have probability `q0` and `q1` for three reports simultaneously without an additional aggregation rule. V3.2 therefore measures the local incentive created by each Judge's own report.

The report is locked before the Judge's audit event and verification signal are revealed. Audit and verification scores never change the current majority decision.

## 4. Configuration schema

V3.2 keeps every V3 signal, reward, cost, and budget field. The `verification_anchor` object changes as follows:

```json
{
  "audit_probability_by_report": {"0": "1/4", "1": "3/4"},
  "sensitivity": "9/10",
  "specificity": "9/10",
  "cost_per_audit": "1/20"
}
```

Validation rules:

- `0 <= q0, q1 <= 1`.
- Verification sensitivity and specificity are in `(1/2, 1]`.
- Audit cost and every reward/cost are non-negative.
- The existing hybrid reward cap remains `3F + 6λ + 3μ <= B`.
- V3 scalar `audit_probability` is not silently accepted as V3.2 input.

## 5. Reward and utility

For Judge `i`, report `r_i`, peer score `PeerScore_i`, and audit event `A_i`:

```text
Reward_i = F + λ PeerScore_i + μ A_i 1(r_i = T)
Utility_i = E[Reward_i] - c_i 1(e_i = H)
```

The engine evaluates expected values exactly. For a fixed state and report `r`, the expected anchor contribution is:

```text
q_r · 1(r = T)
```

Expected audit cost is the expected number of individual checks times `cost_per_audit`:

```text
E[audit cost] = κ Σ_i E[q_{r_i}]
```

This is a new V3.2 accounting rule; V3's `qκ` single-audit accounting is unchanged for V3 inputs.

## 6. Required outputs

In addition to V3 metrics and best-response certificates, V3.2 must expose:

- `audit_probability_by_report` and the exact expected audit cost;
- per-Judge expected anchor score and report-contingent audit exposure;
- `delta_utility = U(H) - U(L)` for every Judge and public branch;
- a failure witness for every failed candidate/policy, identifying the Judge, branch, old action, profitable action, and conditional utility gain;
- a decomposition label distinguishing `effort_cost`, `report_sensitive_anchor`, `peer_score`, and `no_pure_equilibrium` failures.

## 7. Robustness study

The V3.2 study may sweep `q0`, `q1`, `λ`, `μ`, prior `π`, verification quality, and effort-cost multiplier. A policy is robust only if every explicitly enumerated uncertainty point passes the configured worst-equilibrium gates. The grid is a finite assumption set, not a confidence interval and not an interpolation over uncomputed values.

The default study compares at least:

1. symmetric spot-checking `q0=q1=1/2`;
2. report-1 emphasis `q0=1/4,q1=3/4`;
3. report-0 emphasis `q0=3/4,q1=1/4`.

The V3.1 scalar-q baseline remains available for comparison, but is not relabelled as the same game because V3.2 audits are per Judge.

## 8. Non-goals and limitations

- No multi-task Correlated Agreement; that is reserved for V4 because it changes one claim into a batch of linked tasks.
- No participation, outside option, timeout, non-reveal, collusion, Sybil, stake, slashing, appeal, or correction.
- No claim that higher accuracy alone proves a good mechanism.
- No use of synthetic calibration as real-world Judge evidence.

## 9. Acceptance gates

V3.2 is complete only when:

1. the spec, design, and verification plan are frozen before production support;
2. schema tests reject scalar-only V3 anchor input and accept exact `q0/q1` input;
3. an independent oracle verifies state normalization, report-sensitive anchor expectation, audit cost, and a best-response witness;
4. V3.1 and all V1/V2 regression suites remain green;
5. the CLI/API exposes V3.2 runs with a pinned model version and artifacts;
6. a browser flow, if the V3.2 operation is exposed in the local UI, shows the report-contingent audit fields and failure witness rather than only a status badge.

