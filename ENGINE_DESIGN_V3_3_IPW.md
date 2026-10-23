# CEAV-M1 V3.3 — Engine design cho IPW audit reward

**Analysis version:** `ceav-m1-v3.3-ipw`  
**Trạng thái:** implementation contract; engine/CLI/API/UI đã triển khai, targeted evidence đã pass.

## 1. Boundary

V3.3 là model mới vì payoff anchor thay đổi. V3.2 không bị sửa nghĩa và vẫn chạy bằng `ceav-m1-v3.2`.

```text
V3.3 study JSON
  -> validate_ipw_study
  -> expand policy × uncertainty grid
  -> validate V33Config and IPW budget cap
  -> enumerate 64 signal/verification rows
  -> search pure equilibria (432 branch candidates)
  -> calculate exact metrics, moments and witnesses
  -> worst-equilibrium gates / baseline comparison / artifacts
```

CLI, server worker và UI chỉ gọi cùng public interface; không chép công thức sang frontend.

## 2. Model and schema boundary

`model.py` thêm `V33Config` hoặc một config type tương đương có `model_version=ceav-m1-v3.3`. Config phải giữ các field signal/reward của V3.2 và thêm `audit_reward_mode="ipw"` trong `verification_anchor`.

Validator tính:

```text
q0 = audit_probability_by_report[0]
q1 = audit_probability_by_report[1]
q_min = min(q0, q1)
cap = 3*f + 6*lambda_peer + 3*anchor_weight/q_min
```

`q0=0` hoặc `q1=0` là invalid trước khi tạo state. Scalar V3 `audit_probability` không được silently convert.

## 3. Exact accounting

State support giữ 64 rows `(Y,Z,X_A,X_B,X_C,T)`. Không sinh audit bit như một state dimension; audit được áp dụng analytically sau khi `realized(candidate, state)` tạo report.

Với report `r`:

```text
q = q0 if r == 0 else q1
mu = anchor_weight
anchor_unit = A * 1(r == T) / q
anchor_reward = anchor_weight * anchor_unit
audit_cost = q * cost_per_audit
```

Expected value dùng state probability. Khi cần moment:

```text
E[anchor_reward]   = mu * P(T=r | observation)
E[anchor_reward^2] = mu^2 * P(T=r | observation) / q
```

Shared `T` được giữ nguyên giữa ba Judge; vì vậy second moment/covariance phải tính trên cùng state rows, không nhân độc lập các verification likelihood.

`D`, false approval, false rejection và wrong payout không đọc audit hoặc `T` sau report lock.

## 4. Best response

Focal deviation dựng candidate prediction một lần. Peer reports, peer tables và hành vi của các Judge còn lại giữ nguyên.

Khi thử report `r`, branch anchor utility dùng:

```text
anchor = anchor_weight * P(T=r | focal observation)
```

không dùng `q_r * anchor_weight` trong expected utility. Chi phí effort vẫn trừ trực tiếp theo action `L/H`.

Mỗi certificate lưu cả payoff gốc và deviation payoff. Không dùng `Y`, `T` hoặc audit bit làm observation của strategy.

## 5. Utility decomposition

`best_response.py` hoặc module accounting phải trả về:

```text
delta_peer_reward
delta_anchor_reward
delta_effort_cost
delta_utility
reconstruction_error
```

Tất cả là `Fraction`. `reconstruction_error` phải exact zero. Phân loại witness thực hiện sau khi có các số này; không suy luận từ tên action. Tie phải được giữ trong output.

## 6. Study driver

Thêm module study riêng, ví dụ `ceav_m1/ipw.py`, với interface:

```python
validate_ipw_study(raw) -> normalized study
expand_ipw_study(study) -> deterministic points
run_ipw_study(raw, on_progress=None) -> result
write_ipw_run(raw, out, ..., on_progress=None) -> result
```

Allowlists policy chỉ gồm `verification_anchor.audit_probability_by_report` ở bản đầu để cô lập tác động IPW. Không sweep đồng thời `lambda_peer` hoặc `anchor_weight` trong cùng policy comparison nếu không khai báo đó là một study khác.

Uncertainty expansion dùng thứ tự cố định của V3.1: policy, `pi`, verification quality, cost multiplier. Pseudo-axis phải áp dụng từ base value mỗi point, không nhân lặp qua các điểm.

## 7. Baselines and budget parity

Mọi V3.3 policy dùng cùng `reward_budget`, Judge count, payout value và uncertainty point. V3.2/V3.1 là reference models, không được ép vào `V33Config` hoặc gọi là cùng equilibrium.

Nếu IPW cap vượt budget, point có `invalid_budget`. Không tự tăng budget, hạ `anchor_weight` hoặc bỏ policy để che lỗi.

Latency chưa được mô hình hóa; output phải ghi `latency_not_modeled`.

## 8. Required artifacts

Một run thành công xuất:

```text
ipw.json
ipw_points.csv
policy_summary.csv
failure_map.json
baseline_comparison.json
pareto_frontier.json
report.md
manifest.json
```

`report.md` phải trình bày false approval và wrong payout trước accuracy; nêu rõ V3.2 baseline, budget parity, q-min, payment cap, variance và các policy không pass.

Mỗi run dùng thư mục mới, pin raw study, source/spec hashes và từ chối overwrite.

## 9. No premature optimization

Bản đầu không cache search giữa các points. Trước khi tối ưu, phải có differential test chứng minh retained equilibria, exact metrics, moments và witnesses không đổi.
