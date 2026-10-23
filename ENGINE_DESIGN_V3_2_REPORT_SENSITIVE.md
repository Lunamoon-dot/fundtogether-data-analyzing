# CEAV-M1 V3.2 — Engine design

## Contract

`ceav-m1-v3.2` is a separate validated model. V3 and V3.1 input and results remain backward compatible. The new `V32Config` stores `audit_probability_by_report = (q0, q1)` and uses the same public/private signal fields and reward fields as `V3Config`.

The state enumerator has 64 states `(Y,Z,X_A,X_B,X_C,T)`. It does not sample an audit bit before a report exists. Audit probabilities are applied analytically after `realized(candidate, state)` produces each report.

## Module boundaries

- `model.py`: `V32Config`, strict schema validation, and 64-state support.
- `signals.py`: V3.2 signal parameters and verification likelihood.
- `evaluate.py`: expected report-contingent anchor reward and `Σ_i E[q_{r_i}]κ` audit accounting.
- `best_response.py`: frozen-peer unilateral optimization with `q_r` in every candidate report branch.
- `equilibria.py`: unchanged exhaustive branch search; it consumes the versioned evaluator and best-response certificates.
- `report_sensitive.py`: V3.2 finite policy/uncertainty study and failure-witness decomposition.
- `output.py`: V3.2 freeze, spec identity, run provenance, and research context.

## Exact calculation

For each state row, compute the candidate reports and predictions once. For each Judge `i`:

```text
q = q0 if r_i=0 else q1
anchor_i = q * 1(r_i=T)
audit_cost_i = q * κ
```

The state row probability contains the signal and verification likelihood only. This avoids conditioning a state distribution on a report that is a strategy output.

For a focal deviation, peer reports and prediction tables remain frozen. For each observation and candidate report `r`, the branch anchor term is:

```text
Σ_s P(s | observation) q_r 1(r=T_s)
```

No ground truth is passed to a Judge strategy or peer score.

## Study output

Each study point contains the config hash, exact equilibrium status, worst equilibrium metrics, pass/fail gates, delta-utility rows, and `failure_witnesses`. A witness is retained as a data object, not prose generated from a rounded decimal.

