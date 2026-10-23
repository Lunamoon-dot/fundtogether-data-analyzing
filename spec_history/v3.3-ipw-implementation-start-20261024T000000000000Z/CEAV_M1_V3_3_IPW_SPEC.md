# CEAV-M1 V3.3 — Incentive-neutral report-sensitive audit

**Trạng thái:** `SPECIFIED`; chưa có implementation hoặc verification acceptance.  
**Ngày đặc tả:** 2026-10-24.  
**Model version:** `ceav-m1-v3.3`.  
**Parent:** V3.2 report-sensitive game (`ceav-m1-v3.2`).

## 1. Mục tiêu

V3.2 cho thấy khi xác suất audit khác nhau theo report, reward anchor cũng khác nhau theo report. Vì vậy Judge có thể đổi report để tăng xác suất nhận reward, dù tín hiệu và chất lượng audit không đổi. V3.3 kiểm tra một giả thuyết hẹp:

> Có thể bỏ report-selection bias của audit reward bằng inverse-probability weighting (IPW), trong khi vẫn giữ audit theo report và không sửa quyết định majority hiện tại hay không?

V3.3 là một thí nghiệm thay đổi payoff. Nó không phải bản sửa nhỏ của V3.2 và không phải bằng chứng production.

## 2. Câu hỏi nghiên cứu và tiêu chí bác bỏ

V3.3 trả lời ba câu hỏi:

1. Với cùng thông tin của Judge, expected anchor reward có còn phụ thuộc vào `q0/q1` sau khi dùng IPW không?
2. Khi `q0 != q1`, equilibrium có giảm report bias so với V3.2 không?
3. Khoản reward IPW có làm vượt reward budget, tăng payout variance hoặc làm mất pure equilibrium không?

Kết quả bị bác bỏ nếu xảy ra một trong các trường hợp sau:

- expected anchor reward còn phụ thuộc vào `q_r` sau khi đã điều kiện trên observation và report;
- validator cho phép `q0=0` hoặc `q1=0`;
- reward cap không bao phủ khoản thanh toán thực tế tối đa `mu/q_min`;
- study không giữ được kết quả invalid, no-pure-equilibrium hoặc vượt gate;
- IPW chỉ tạo ra một điểm đẹp nhưng không vượt qua toàn bộ uncertainty grid đã khai báo.

Không được gọi V3.3 thành công chỉ vì accuracy tăng ở một fixture.

## 3. Phạm vi kế thừa từ V3.2

Các phần sau không đổi:

- một claim nhị phân với ground truth ẩn `Y`;
- đúng ba Judge A, B và C;
- public signal `Z`, private signal `X_i` chỉ có sau High effort;
- mỗi Judge chọn `L` hoặc `H`, report nhị phân và peer prediction;
- decision `D` là majority của ba report;
- report bị khóa trước khi audit và verification signal xuất hiện;
- `T` không được dùng để sửa `D` hoặc payout của claim;
- pure-strategy Nash equilibrium trong reduced normal form;
- exact `Fraction` arithmetic và exhaustive search 432 branch candidates;
- conditional independence của signal theo model V3.2.

V3.3 không thêm participation, outside option, timeout, non-reveal, collusion, bribery, Sybil, stake, slashing, appeal hoặc correction. Những thay đổi đó là model version khác.

## 4. Timing và information boundary

```text
Nature sinh Y, Z, X_A, X_B, X_C và T
        ↓
Mỗi Judge thấy Z; nếu chọn H thì thấy thêm X_i
        ↓
Mỗi Judge gửi report r_i và prediction p_i
        ↓
Audit A_i được sinh độc lập theo report của chính Judge
        ↓
T và kết quả audit được mở sau khi report đã khóa
        ↓
Tính reward IPW; D vẫn là majority của r_A, r_B, r_C
```

Judge không biết `Y`, `T` hoặc `A_i` khi chọn effort và report. Audit là per-Judge như V3.2; không biến thành một common audit.

## 5. Schema V3.3

Config tối thiểu:

```json
{
  "model_version": "ceav-m1-v3.3",
  "verification_anchor": {
    "audit_probability_by_report": {"0": "1/4", "1": "3/4"},
    "audit_reward_mode": "ipw",
    "sensitivity": "9/10",
    "specificity": "9/10",
    "cost_per_audit": "1/20"
  },
  "f": "1/10",
  "lambda_peer": "0",
  "anchor_weight": "19/10",
  "reward_budget": "10"
}
```

V3.3 kế thừa toàn bộ signal, Judge, payout và operating-cost fields của V3.2. Validator phải:

- yêu cầu đúng `model_version` `ceav-m1-v3.3`;
- yêu cầu đúng `audit_reward_mode = "ipw"`;
- yêu cầu `0 < q0 <= 1` và `0 < q1 <= 1`;
- đặt `q_min = min(q0, q1)`;
- từ chối scalar `audit_probability` của V3;
- từ chối field lạ và field thiếu;
- dùng `Fraction` cho mọi phép tính.

`q=0` không được hỗ trợ vì IPW sẽ chia cho zero. Nếu muốn tắt audit trong một nhánh, đó là payoff khác và phải tạo version mới.

## 6. Reward, utility và chứng minh IPW

Trong công thức dưới đây, `mu` chính là field `anchor_weight` của config.

Với report `r_i`, audit bit `A_i`, verification signal `T`:

```text
q_r = q0 nếu r_i = 0, q1 nếu r_i = 1

AnchorReward_i = mu * A_i * 1(r_i = T) / q_r
Reward_i       = f + lambda_peer * PeerScore_i + AnchorReward_i
Utility_i      = E[Reward_i] - c_i * 1(e_i = H)
```

Vì `E[A_i | r_i] = q_r`, với mọi observation của Judge:

```text
E[AnchorReward_i | observation, r_i]
  = mu * P(T = r_i | observation)
```

Expected anchor reward không còn nhân thêm `q_r`. Đây là tính chất cần được kiểm chứng bằng oracle, không được suy ra từ một vài output equilibrium.

Audit operating cost vẫn phụ thuộc xác suất audit:

```text
E[audit cost] = kappa * sum_i E[q_(r_i)]
```

IPW không làm audit miễn phí.

Khoản trả anchor thực tế có thể lớn hơn `mu`:

```text
0 <= AnchorReward_i <= mu / q_min
```

Vì vậy IPW có thể giữ expected incentive nhưng tăng payment variance và worst-case cash exposure.

## 7. Budget và payment cap

V3.3 dùng cùng một `reward_budget` cho mọi policy trong một study. Không được tăng budget riêng cho IPW để làm policy pass.

Validator phải dùng cap bảo thủ:

```text
IPWRewardCap = 3*f + 6*lambda_peer + 3*mu/q_min
```

Config invalid nếu:

```text
IPWRewardCap > reward_budget
```

Cash review cost vẫn được báo cáo riêng:

```text
cash_review_cost
  = expected_reward_total
  + operating_cost
  + expected_audit_cost
```

Study phải xuất thêm `max_realized_anchor_payment`, `anchor_reward_second_moment`, `anchor_reward_variance` và `payment_cap_ratio`. Không được dùng expected payment để che worst-case cap.

## 8. Study và baseline

Study V3.3 phải có ít nhất ba policy IPW với cùng base config và cùng budget:

1. `v3_3_ipw_symmetric`: `q0=q1=1/2`;
2. `v3_3_ipw_report_1`: `q0=1/4,q1=3/4`;
3. `v3_3_ipw_report_0`: `q0=3/4,q1=1/4`.

Mỗi policy được so sánh với các reference sau, không gộp chúng thành cùng model:

- V3.2 symmetric;
- V3.2 report-1 emphasis;
- V3.2 report-0 emphasis;
- V3.1/V3 scalar-anchor baseline nếu artifact cùng input tồn tại.

Baseline phải giữ đúng ba Judge, cùng signal inputs, cùng reward budget, cùng payout value và cùng uncertainty point. Nếu baseline artifact không có hoặc không khớp hash, trạng thái là `unavailable`, không tự dựng số thay thế.

Study chuẩn dùng cùng uncertainty axes như V3.1:

- `pi`: `3/10`, `1/2`, `7/10`;
- verification quality: `4/5`, `9/10`, `19/20`;
- High-effort cost multiplier: `1`, `6/5`.

Ba policy × 18 scenario = 54 points. Engine phải chạy toàn bộ tích Descartes và giữ thứ tự deterministic. Đây là declared assumption grid, không phải confidence interval và không nội suy ngoài grid.

Mọi point phải chạy đủ 432 branch candidates. Invalid budget, incomplete search và no pure equilibrium đều là failure reasons được giữ lại.

## 9. Metrics và gates

Mỗi equilibrium và mỗi policy point phải xuất:

- false approval rate;
- false rejection rate;
- wrong payout probability và wrong payout value;
- accuracy chỉ để diagnostic;
- expected reward và expected audit cost;
- cash review cost;
- effort profile từng Judge và public branch;
- `P(report=1)`, `P(report=1 | Y=0)`, `P(report=1 | Y=1)`;
- report-bias delta so với V3.2 policy tương ứng;
- maximum realized anchor payment và payment variance;
- exact utility decomposition của từng profitable deviation.

Study request bắt buộc khai báo gates trước khi chạy:

```json
{
  "gates": {
    "max_false_approval_rate": "1/5",
    "max_wrong_payout_value": "3/20",
    "max_false_rejection_rate": "1/4",
    "max_cash_review_cost": "4"
  }
}
```

Các gate trên là research thresholds kế thừa từ V3.1, không phải cam kết production. Report bias là metric nghiên cứu chính nhưng trước mắt không gán một ngưỡng tùy ý; engine phải báo cáo chênh lệch exact và oracle phải kiểm tra tính chất IPW. Không được đổi gate sau khi xem kết quả mà vẫn giữ cùng study revision.

Policy chỉ pass robustness khi mọi 54 point hợp lệ, hoàn tất exhaustive search và qua toàn bộ gate theo equilibrium xấu nhất. `no_robust_policy` là kết quả khoa học hợp lệ, không phải runner failure.

## 10. Failure witness và causal decomposition

Mỗi deviation witness phải lưu đủ các thành phần:

```text
delta_utility
delta_peer_reward
delta_anchor_reward
delta_effort_cost
```

Với fixed reward triệt tiêu khi so sánh deviation:

```text
delta_utility
  = delta_peer_reward
  + delta_anchor_reward
  - delta_effort_cost
```

`reconstruction_error` phải bằng đúng `0` dưới `Fraction`.

Không được gán failure type chỉ bằng cách nhìn action cũ/mới. Witness phải ghi:

- Judge và public branch;
- candidate action và deviating action;
- tất cả component exact;
- component dương góp phần làm deviation có lợi;
- `dominant_component` chỉ khi có một component lớn nhất nghiêm ngặt;
- giữ tất cả tie;
- `mixed_components` khi không có một nguyên nhân đơn lẻ.

## 11. Non-goals và giới hạn kết luận

V3.3 không chứng minh:

- High effort tự nguyện trong mọi payoff hoặc mọi dữ liệu ngoài đời;
- report truthfulness khi peer score, collusion hoặc selection phức tạp hơn model;
- robustness với mixed, correlated hoặc coalition equilibrium;
- audit độc lập ngoài đời;
- chống collusion, bribery, Sybil hoặc thao túng auditor;
- blockchain readiness, fund safety hoặc production deployment.

Synthetic fixture chỉ kiểm tra pipeline và tính chất toán học. Kết quả V3.3 phải được ghi là `assumption` trừ khi có provenance khác đã được kiểm chứng.

## 12. Acceptance của version

V3.3 chỉ chuyển từ `SPECIFIED` sang `IMPLEMENTED` khi có freeze event mới cho spec/design/verification và có code version `ceav-m1-v3.3`. Chỉ chuyển sang `VERIFIED` khi:

1. oracle độc lập chứng minh IPW cancellation, audit cost và payment cap;
2. causal decomposition tái dựng utility exact;
3. exhaustive search đủ 432 candidates ở mọi point hợp lệ;
4. toàn bộ V1, V2, V2.1, V2.2, V3, V3.1 và V3.2 regression pass;
5. CLI/API/UI (nếu exposed) pin đúng spec, mode, budget và provenance;
6. study 54 points hoàn tất, không partial/canceled và giữ mọi kết quả bất lợi;
7. browser evidence đối chiếu được artifact với UI nếu V3.3 được public qua local app.

Hiện tại V3.3 mới ở trạng thái `SPECIFIED`; chưa được gọi là implemented, verified hoặc production-ready.
