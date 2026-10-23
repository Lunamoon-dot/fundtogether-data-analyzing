# CEAV-M1 V3.1 — Đặc tả robustness và policy selection

**Analysis version:** `ceav-m1-v3.1-robustness`

**Model version:** `ceav-m1-v3.0`

**Spec revision:** `robustness-grid-r1`

**Ngày:** 23/10/2026

**Trạng thái tại implementation-start:** `SPECIFIED`; implementation và verification chưa tồn tại.

## 1. Mục tiêu

V3.1 kiểm tra liệu kết quả của V3 có tồn tại trên một tập điều kiện bất định đã khai báo trước hay chỉ xuất hiện tại một điểm tham số đẹp. V3.1 không thay đổi distribution, information, action, payoff, timing hoặc equilibrium concept của V3.

Tiêu chí chính của V3.1 là:

1. false approval;
2. expected wrongly paid value;
3. false rejection như guardrail;
4. cash review cost như guardrail.

Accuracy vẫn được xuất để giải thích nhưng không quyết định policy pass/fail.

## 2. Quan hệ với V3

V3.1 kế thừa toàn bộ [CEAV_M1_V3_ANCHOR_SPEC.md](CEAV_M1_V3_ANCHOR_SPEC.md). Các ràng buộc sau không đổi:

- đúng ba Judge A/B/C;
- cùng sáu action mỗi nhánh `Z`;
- majority 2/3;
- verification anchor chỉ tham gia reward sau khi report khóa;
- `T` không sửa `D` hoặc payout;
- exact `Fraction`;
- pure-strategy equilibrium trong reduced normal form;
- conditional independence của signal theo V3.

V3.1 không thêm participation, non-reveal, timeout, correlation, collusion, Sybil, stake, slashing, appeal hoặc settlement. Các thay đổi đó thuộc một model version mới.

## 3. Đại lượng chính

Với một config và một equilibrium `e`:

```text
FA(e) = P(D=1 | Y=0)
FR(e) = P(D=0 | Y=1)
WP(e) = payout_value * P(Y=0,D=1)
CC(e) = expected_reward_total + operating_cost + expected_audit_cost
```

`WP` phụ thuộc prior và payout value; `FA` là tỷ lệ có điều kiện nên không phụ thuộc trực tiếp vào prevalence của claim giả nhưng equilibrium có thể đổi khi prior đổi.

Đối với một scenario có nhiều pure equilibrium, V3.1 dùng:

```text
worst_FA = max_e FA(e)
worst_FR = max_e FR(e)
worst_WP = max_e WP(e)
worst_CC = max_e CC(e)
worst_accuracy = min_e Accuracy(e)
```

Không được dùng equilibrium tốt nhất để cấp pass cho policy.

## 4. Policy và uncertainty

Study input chứa một base V3 config, danh sách policy và các uncertainty axes.

### 4.1. Policy

Mỗi policy có:

```json
{
  "policy_id": "anchor_q50",
  "overrides": {
    "verification_anchor.audit_probability": "1/2",
    "lambda_peer": "0",
    "anchor_weight": "19/10"
  }
}
```

Policy chỉ được thay:

- `verification_anchor.audit_probability`;
- `lambda_peer`;
- `anchor_weight`.

Mọi policy giữ cùng ba Judge và cùng `reward_budget` từ base config. Budget cap vẫn được validator V3 kiểm theo worst case.

### 4.2. Uncertainty axes

V3.1 r1 hỗ trợ các axis V3 hiện có và hai axis đồng bộ:

```text
verification_anchor.quality
judges.high_effort_cost_multiplier
```

`verification_anchor.quality=x` đặt sensitivity và specificity của `T` cùng bằng `x`.

`judges.high_effort_cost_multiplier=m` nhân cả ba chi phí trong base config sau khi policy override đã được áp dụng. Nó không nhân lặp qua các axis khác.

Mọi uncertainty axis là danh sách chuỗi hữu tỉ không rỗng. Engine chạy toàn bộ tích Descartes, không lấy mẫu ngẫu nhiên.

## 5. Study schema r1

```json
{
  "analysis_version": "ceav-m1-v3.1-robustness",
  "base_config": { "model_version": "ceav-m1-v3.0" },
  "policies": [
    {"policy_id": "...", "overrides": {"...": "..."}}
  ],
  "uncertainty_axes": {
    "pi": ["3/10", "1/2", "7/10"]
  },
  "gates": {
    "max_false_approval_rate": "1/5",
    "max_wrong_payout_value": "3/20",
    "max_false_rejection_rate": "1/4",
    "max_cash_review_cost": "4"
  },
  "provenance": {
    "status": "assumption",
    "notes": "..."
  }
}
```

Không cho field lạ. `policy_id` phải duy nhất và ổn định. `provenance.status` nhận `assumption`, `pilot_estimate` hoặc `historical_estimate`. Synthetic/assumption ranges không được gọi là confidence interval.

## 6. Expansion order và identity

Policy giữ thứ tự trong input. Uncertainty axes được sắp theo allowlist chuẩn của engine, không theo thứ tự JSON. Giá trị giữ thứ tự khai báo. `point_id` liên tục từ 0 theo:

```text
for policy in policies:
    for scenario in Cartesian product(uncertainty axes):
        emit point
```

Mỗi point lưu full config, config semantic hash, policy id, exact axis values và trạng thái exhaustive search.

## 7. Pass/fail

Một scenario point fail nếu:

- config không hợp lệ hoặc vượt budget;
- exhaustive search không hoàn tất đủ 432 branch candidates;
- không có pure equilibrium;
- bất kỳ worst metric nào vượt gate tương ứng.

Một policy pass robustness khi và chỉ khi mọi uncertainty point của policy pass.

Study classification:

```text
no_robust_policy       nếu 0 policy pass
isolated_robust_point  nếu đúng 1 policy pass
observed_robust_set    nếu ít nhất 2 policy pass
```

Đây là phân loại trên declared grid. Không nội suy miền giữa các policy hoặc scenario point.

## 8. Failure map

Mỗi point phải giữ mọi failure reason, không dừng tại lỗi đầu:

```text
invalid_input
invalid_budget
incomplete_search
no_pure_equilibrium
false_approval_gate
wrong_payout_gate
false_rejection_gate
cash_review_cost_gate
```

Summary đếm theo policy và toàn study. Kết quả bất lợi không được lọc khỏi report.

## 9. Pareto frontier

Chỉ policy có đủ scenario hợp lệ và pure equilibrium mới vào tập so sánh Pareto. Vector của policy là:

```text
(worst_FA, worst_WP, worst_FR, worst_CC)
```

Policy `p` dominate `q` khi mọi thành phần của `p` không lớn hơn `q` và ít nhất một thành phần nhỏ hơn. Frontier được tính exact. Một policy trên frontier không mặc nhiên pass gates.

## 10. Baseline references

V3.1 xuất hai reference cho từng uncertainty scenario:

- `public_signal_rule`: quyết định trực tiếp `D=Z`; không phải so sánh ngang hàng về Judge reward.
- `forced_all_high`: ba Judge dùng `H01`; cùng config, Judge count, reward budget và audit policy nhưng không được gọi là equilibrium nếu có regret dương.

Policy comparison giữ cùng `reward_budget` và đúng ba Judge. V3.1 không có time model, vì vậy không được tuyên bố equal latency. `audit_probability` và expected audit cost chỉ là workload/cost proxy.

## 11. Predeclared study

Study chuẩn nằm tại `configs/v3/robustness_v3_1.json` và dùng:

- 6 policy points;
- prior `3/10, 1/2, 7/10`;
- anchor quality `4/5, 9/10, 19/20`;
- Judge cost multiplier `1, 6/5`;
- 18 uncertainty scenarios cho mỗi policy, tổng 108 points;
- audit cost assumption `1/5` trong base config;
- gates đúng như schema mẫu ở §5.

Các ranges là assumption nghiên cứu, không phải dữ liệu thật. Không được đổi gates sau khi nhìn output mà vẫn gọi cùng study revision.

## 12. Output bắt buộc

Mỗi run thành công có:

```text
robustness.json
robustness_points.csv
policy_summary.csv
failure_map.json
pareto_frontier.json
baseline_comparison.json
report.md
manifest.json
```

`report.md` phải dẫn bằng false approval và wrongly paid value, sau đó mới hiển thị accuracy. Nó phải ghi model limits, provenance và `latency_not_modeled`.

## 13. Giới hạn kết luận

V3.1 có thể chọn hoặc bác policy trong declared synthetic/assumption grid. Nó không chứng minh:

- uncertainty ranges đại diện ngoài đời;
- mixed-equilibrium selection;
- signal independence ngoài đời;
- auditor độc lập hoặc chống thao túng;
- collusion/Sybil/bribery resistance;
- blockchain readiness hoặc fund safety.

## 14. Acceptance

V3.1 chỉ `VERIFIED` khi:

- spec/design/verification được freeze trước production support;
- schema, expansion, worst-equilibrium gates, failure map và Pareto khớp oracle độc lập;
- CLI từ chối overwrite và pin inputs/source;
- server worker chạy cùng interface nếu operation được public qua API;
- registered V3.1 tests và toàn bộ V1–V3 regression pass;
- predeclared 108-point study hoàn tất, không partial/canceled;
- report giữ kết quả xấu và giới hạn synthetic.
