# CEAV-M1 V3.1 — Engine design cho robustness

**Analysis version:** `ceav-m1-v3.1-robustness`  
**Design revision:** `engine-robustness-grid-r1`

## 1. Module boundary

Thêm `ceav_m1/robustness.py`. Module này điều phối validator V3, exhaustive search và equilibrium metrics hiện có; nó không sao chép payoff hoặc công thức signal.

```text
study JSON
  -> validate_robustness_study
  -> expand policy × uncertainty grid
  -> validate_config(V3)
  -> search_pure(432 candidates)
  -> summarize_equilibrium_metrics
  -> worst-equilibrium gate
  -> policy aggregation / Pareto / artifacts
```

CLI/API/UI chỉ gọi interface này.

## 2. Public interface

```python
validate_robustness_study(raw) -> normalized study
run_robustness_study(raw, on_progress=None) -> result
write_robustness_run(raw, out, ..., on_progress=None) -> result
```

Normalized study giữ chuỗi hữu tỉ trong request; math/result dùng `Fraction` cho đến serializer.

## 3. Allowlists

Policy paths:

```text
verification_anchor.audit_probability
lambda_peer
anchor_weight
```

Uncertainty paths:

```text
pi
public_signal.sensitivity
public_signal.specificity
judges.A/B/C.private_signal.sensitivity
judges.A/B/C.private_signal.specificity
judges.A/B/C.high_effort_cost
verification_anchor.sensitivity
verification_anchor.specificity
verification_anchor.cost_per_audit
payout_value
operating_cost
verification_anchor.quality
judges.high_effort_cost_multiplier
```

Pseudo-axis luôn áp dụng từ base costs/base anchor fields của point, không đọc giá trị đã nhân ở iteration trước.

## 4. Point evaluation

Với từng point:

1. Deep-copy base config.
2. Apply policy overrides.
3. Apply uncertainty values theo allowlist order.
4. Validate V3 hybrid config và budget.
5. Chạy `search_pure` đủ 432 candidates.
6. Chạy `summarize_equilibrium_metrics` cho mọi full equilibrium.
7. Lấy max của bốn risk/cost metrics và min accuracy.
8. Đánh giá tất cả gates, giữ mọi reason.

Không dùng candidate profile để thay equilibrium. Không gọi search incomplete là no-equilibrium.

## 5. References

`public_signal_rule` tính trực tiếp từ config:

```text
FA = 1 - specificity_Z
FR = 1 - sensitivity_Z
WP = payout_value * (1-pi) * FA
accuracy = pi*sensitivity_Z + (1-pi)*specificity_Z
```

`forced_all_high` dùng profile `H01` cho cả ba Judge ở cả hai nhánh và `evaluate`; output ghi `reference_only` và không thay equilibrium.

## 6. Policy aggregation

Policy record gồm:

- point count;
- pass/fail counts;
- all-points-pass;
- failure reason counts;
- worst metric value và witness point id;
- worst accuracy và witness;
- expected audit probability/cost ranges;
- policy overrides.

Nếu bất kỳ point invalid, incomplete hoặc no-pure, policy không Pareto-eligible.

## 7. Pareto

So sánh exact tuple bốn chiều theo spec §9. Giữ policy id theo input order để output deterministic. Frontier không lọc theo gate pass.

## 8. Artifacts

`write_robustness_run` dùng `new_run` với base config, operation `robustness`, mechanism `hybrid_anchor`, full study trong request. Mỗi run là thư mục mới; ghi artifact bằng atomic JSON writer và `write_csv`.

CSV chỉ chứa scalar/exact values và JSON text cho override/witness khi cần. `robustness.json` là artifact đầy đủ.

## 9. Progress và cancellation

Progress bọc search hiện có:

```json
{"phase":"robustness_equilibria","policy":2,"policies_total":6,"point":19,"points_total":108,"completed":216,"total":432}
```

Sau mỗi point emit `phase=robustness`. Cancellation từ worker tiếp tục theo contract hiện có; run partial không được xuất success certificate.

## 10. Không tối ưu sớm

R1 không cache search giữa các point dù một số accounting-only field không đổi strategy. Exact baseline đơn giản được ưu tiên trước. Chỉ thêm cache sau khi có differential test chứng minh search, retained equilibria, metrics và witnesses không đổi.

## 11. UI/API

Operation public là `robustness`.

- `/api/validate` nhận `{operation, study}` và trả grid size/gates.
- worker ghi study vào staging rồi gọi cùng CLI.
- status công bố predeclared study.
- UI hiển thị số policy, scenario, point, robust classification, failure reasons, Pareto và worst-case table.

UI không cho gọi assumption range là confidence interval và không hiển thị equal-latency claim.
