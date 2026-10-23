# CEAV-M1 V2.2 — Đặc tả phân rã động lực và bản đồ cân bằng

**Release feature:** `ceav-m1-v2.2-incentive-diagnostics`

**Model được phân tích:** `ceav-m1-v2.0`

**Trạng thái tài liệu:** đặc tả trước implementation

## 1. Mục đích

V2.2 giải thích vì sao một candidate High Effort thành công hoặc thất bại. Feature không thay game, timing, RBTS, strategy space, payoff, majority rule, signal distribution hoặc khái niệm cân bằng của [CEAV_M1_V2_SPEC.md](CEAV_M1_V2_SPEC.md).

```text
Config V2 + candidate profile
  -> local incentive decomposition với peer strategy cố định
  -> conditional reward thresholds
  -> exhaustive pure-equilibrium search tại từng điểm sweep
  -> equilibrium landscape và artifacts tái lập
```

Output trung tâm trả lời `Why does High Effort fail?`; nó không cố làm kết quả có lợi cho RBTS.

## 2. Phạm vi

### 2.1. Có trong V2.2

- Phân rã exact cho từng `Judge × Z`.
- Phân biệt mua thông tin với sử dụng thông tin trong report.
- Conditional threshold khi giữ nguyên toàn bộ peer strategy/prediction tables.
- Kiểm tra threshold với budget cap.
- Exhaustive pure-equilibrium search tại từng điểm sweep.
- Phân loại branch và full equilibrium theo effort/report behavior.
- CLI, local API, HTML, immutable artifacts và history.

### 2.2. Không thuộc V2.2

- Cơ chế reward mới, audit, stake, slashing, assignment hoặc ground-truth reward.
- Thay đổi cách sinh `X_i` hoặc thêm nguồn dữ liệu thực.
- Mixed, correlated, coalition-proof equilibrium hoặc equilibrium selection.
- Tuyên bố Judge đã thực hiện công việc ngoài đời.
- Tối ưu payment hoặc khuyến nghị production tự động.

## 3. Nguồn chuẩn và phần kế thừa

Game và ký hiệu kế thừa nguyên nghĩa từ V2.0. Calibration V2.1 có thể cung cấp config nhưng provenance không tham gia phép tính V2.2. `X_i` vẫn là tín hiệu riêng của chính Judge `i`; report của peer là `r_j`/`r_k`.

V2.2 chỉ hỗ trợ RBTS vì các threshold theo `lambda` không có nghĩa dưới fixed reward. Toàn bộ phép tính dùng `Fraction`; decimal chỉ để hiển thị.

## 4. Local incentive decomposition

Với Judge `i`, nhánh public signal `z` và peer strategy `sigma_-i` giữ cố định, đặt:

```text
V_L(i,z | sigma_-i)     = max total RBTS score khi effort=L
V_H(i,z | sigma_-i)     = max total RBTS score trên H00,H01,H10,H11
V_H_dep(i,z | sigma_-i) = max total RBTS score trên H01,H10
```

`H01/H10` được gọi là **signal-dependent** vì report thay đổi theo `X_i`. Tên này không khẳng định report gần ground truth; `H10` có thể đảo chiều tín hiệu. `H00/H11` là **signal-ignored report** dù High Effort vẫn có thể dùng `X_i` trong prediction.

Các đại lượng bắt buộc:

```text
information_gain_best      = V_H - V_L
information_gain_dependent = V_H_dep - V_L
report_utilization_gap     = V_H - V_H_dep

net_incentive_best      = lambda * information_gain_best - c_i
net_incentive_dependent = lambda * information_gain_dependent - c_i
```

Theo V1 P3, `information_gain_best >= 0`. `information_gain_dependent` có thể âm vì nó loại H00/H11 khỏi tập lựa chọn.

Mọi score của `H00/H01/H10/H11` phải được tính với own prediction tối ưu cho observation High và peer tables bất biến. Không dựng lại candidate hoặc cập nhật prediction của peer trong một unilateral deviation.

## 5. Conditional threshold và budget

Với gain `g` và cost `c_i`:

```text
g > 0               -> lambda_star = c_i / g
g = 0 và c_i > 0    -> UNATTAINABLE_BY_LAMBDA
g = 0 và c_i = 0    -> lambda_star = 0, effort hòa tại mọi lambda
g < 0               -> UNATTAINABLE_BY_LAMBDA
```

RBTS budget cap cho config hiện tại:

```text
lambda_max = (reward_budget - 3*f) / 6
```

Threshold là `BUDGET_FEASIBLE` khi hữu hạn và `lambda_star <= lambda_max`; ngược lại là `BUDGET_INFEASIBLE` hoặc `UNATTAINABLE_BY_LAMBDA`.

Tên đầy đủ của kết quả là:

```text
conditional_lambda_threshold_given_fixed_peer_strategies
```

Nó không được diễn giải thành lambda tối thiểu bảo đảm High-Effort equilibrium. Khi lambda hoặc config đổi, strategy của peer và tập equilibrium có thể đổi.

## 6. Chẩn đoán phân cấp

Mỗi `Judge × Z` trả các chiều độc lập:

```json
{
  "effort": {"best_high_status": "PREFERRED|TIED|NOT_PREFERRED"},
  "report": {"status": "SIGNAL_DEPENDENT_ONLY|SIGNAL_IGNORED_ONLY|TIE_DEPENDENT_AND_IGNORED"},
  "budget": {"best_high": "BUDGET_FEASIBLE|BUDGET_INFEASIBLE|UNATTAINABLE_BY_LAMBDA"},
  "dependent_report": {"status": "PREFERRED|TIED|NOT_PREFERRED"}
}
```

Không ép một branch vào một enum duy nhất vì effort, report và budget có thể đồng thời thất bại.

## 7. Equilibrium landscape

Tại mỗi điểm sweep, engine phải gọi exhaustive `search_pure` hiện có và giữ `enumeration_completed=true`, `432` branch candidates cùng retained equilibrium IDs cho `Z=0/1`.

Mỗi branch equilibrium được xếp đúng một nhóm:

- `all_low`: cả ba action là `L0/L1`.
- `all_high_signal_dependent`: cả ba là `H01/H10`.
- `all_high_signal_ignored`: cả ba là `H00/H11`.
- `all_high_mixed_report`: cả ba dùng H nhưng trộn signal-dependent và signal-ignored.
- `mixed_effort`: có cả L và H.

Hai branch equilibrium được ghép Cartesian như V2.0. Full profile dùng cùng taxonomy, yêu cầu điều kiện tương ứng đúng ở cả `Z=0` và `Z=1`; các trường hợp còn lại là `mixed_behavior`.

Landscape bắt buộc công bố:

```text
branch equilibrium IDs và counts theo class
full_equilibrium_count và counts theo class
low_effort_exists
all_high_signal_dependent_exists
all_high_signal_ignored_exists
coexistence_low_and_dependent_high
```

Existence không chứng minh equilibrium selection. Không gộp utility ba Judge thành một “highest utility” nếu chưa định nghĩa social welfare; output chỉ giữ utility vector của candidate đang phân tích.

## 8. Sweep

Sweep hỗ trợ exact paths của V2.0 và thêm `reward_budget`. Tối thiểu UI phải cho phép sweep `lambda`; người dùng có thể thêm cost hoặc signal quality. Mỗi point chứa full canonical `config_json`, semantic config hash, validation status, local diagnostics, equilibrium IDs/counts và classification.

Điểm vi phạm budget được giữ với `status=invalid_budget`; không chạy search và không nội suy kết quả. Sweep một candidate không được gọi là equilibrium landscape nếu chưa chạy exhaustive search tại từng điểm hợp lệ.

## 9. Output và artifacts

Một run thành công chứa:

```text
config.json
profile.json
incentive_diagnostics.json
incentive_diagnostics.csv
incentive_sweep.json
incentive_sweep.csv
equilibrium_landscape.json
summary.json
report.md
manifest.json
```

Manifest pin model V2.0 và freeze V2.2 riêng. `feature_version` không thay `model_version`; runtime tiếp tục ghi `ceav-m1-v2.0` cho game.

## 10. CLI, API và HTML

CLI mục tiêu:

```text
python -m ceav_m1 incentives --config PATH --profile PATH --axes PATH --out PATH
```

`--axes` là optional JSON object; bỏ qua nghĩa là chỉ chạy base point. Mechanism cố định là `rbts`.

Local API thêm operation `incentives` với `config`, `profile`, optional `axes`, `scenario`. HTML thêm view **Chẩn đoán động lực** hiển thị:

1. sáu card `Judge × Z`;
2. `V_L`, `V_H`, `V_H_dep`, gains, costs và net incentives;
3. threshold/budget status;
4. best High actions và report utilization;
5. bảng landscape theo point, không chỉ trạng thái candidate.

## 11. Kết quả khoa học được phép kết luận

V2.2 có thể chứng minh trong config/profile/sweep đã pin:

- information không đủ giá trị;
- information có giá trị cho prediction nhưng best report bỏ qua `X_i`;
- reward threshold vượt budget;
- informative/signal-dependent High equilibrium tồn tại;
- Low Effort equilibrium vẫn tồn tại cùng High equilibrium;
- reward scaling làm regret/report failure tăng ở một miền đã tính.

V2.2 không được suy ra các kết luận trên cho tham số chưa sweep, dữ liệu thực, mixed equilibrium hoặc production behavior.

## 12. Acceptance

V2.2 chỉ được gọi là verified khi đạt plan V2.2 tương ứng: exact decomposition, independent fixture, conditional/global separation, exhaustive search per point, immutable artifacts, CLI/API/UI parity, browser acceptance và hồi quy V1/V2/V2.1 trên current source.
