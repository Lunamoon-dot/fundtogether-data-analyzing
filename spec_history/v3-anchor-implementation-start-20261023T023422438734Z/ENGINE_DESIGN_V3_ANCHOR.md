# CEAV-M1 V3 — Thiết kế engine hybrid anchor

**Áp dụng:** `ceav-m1-v3.0`, spec revision `verification-anchor-r1`

**Design revision:** `engine-design-v3-anchor-r1`

**Trạng thái:** thiết kế trước implementation; freeze V3 phải giữ raw bytes của revision này.

## 1. Nguồn chuẩn và mục tiêu

[CEAV_M1_V3_ANCHOR_SPEC.md](CEAV_M1_V3_ANCHOR_SPEC.md) sở hữu distribution `A,T`, timing, hybrid payoff, budget và acceptance. V2 sở hữu signal model được kế thừa; V1 sở hữu RBTS formula và reduced strategy space.

Đường chạy V3:

```text
raw V3 JSON
  -> validate_config(..., "hybrid_anchor")
  -> V3Config
  -> enumerate_states -> 128 potential rows
  -> build_candidate
  -> evaluate / solve_branch / search_pure
  -> artifacts / API / UI
```

Không tạo analyzer song song. Các module game hiện có nhận common config/state interface và dispatch theo mechanism ở đúng seam.

## 2. Version và records

`ceav_m1.__init__` thêm:

```python
V3_MODEL_VERSION = "ceav-m1-v3.0"
SUPPORTED_MODEL_VERSIONS += (V3_MODEL_VERSION,)
ENGINE_VERSION = "ceav-m1-engine-v3.0"
```

Default UI/runtime chuyển sang V3 sau khi V3 API/UI đã nối; V1/V2 vẫn đọc được.

`V3Config` cung cấp common fields:

```text
pi, public_sensitivity, public_specificity
private_sensitivities, private_specificities, costs
f, multiplier, fixed_reward, reward_budget
payout_value, operating_cost, model_version
```

Trong đó `multiplier` là internal alias của JSON `lambda_peer` để các seam prediction hiện có không cần branch theo version. V3 thêm:

```text
audit_probability
verification_sensitivity
verification_specificity
anchor_weight
```

`fixed_reward` không thuộc schema V3 nhưng record đặt `0` để giữ common interface; mechanism `fixed/rbts` bị từ chối với V3.

`WeightedState` thêm optional:

```text
audit: int | None
verification: int | None
```

V1/V2 dùng `None`; V3 dùng bit `0/1`.

## 3. Validation và budget

`validate_config` dispatch theo cặp model/mechanism:

```text
V1/V2: fixed | rbts
V3: hybrid_anchor
```

Schema V3 là exact allowlist trong spec §13. Không alias `lambda` thành `lambda_peer`, không tự thêm anchor fields cho V2.

Budget:

```text
hybrid_anchor cap = 3*f + 6*multiplier + 3*anchor_weight
```

Unknown key được báo trước missing key cùng cấp. Mọi số đi qua `rational`; canonical `raw()` dùng Fraction tối giản và Judge order A/B/C.

## 4. State distribution

`signals.signal_parameters` coi V3 public/private channels như V2. Helper mới:

```python
verification_probability(config, y, audit, verification) -> Fraction
```

`enumerate_states`:

- V1/V2 giữ product 5 bit và 32 positive rows y hệt;
- V3 dùng product 7 bit theo `(y,z,x_A,x_B,x_C,a,t)`;
- state ID là index canonical 0..127;
- giữ cả zero-mass potential row tại endpoints để state IDs ổn định;
- assert mass không âm, tổng bằng 1 và ghi support size trong diagnostics/output.

`observe` tiếp tục chỉ chiếu `Z` hoặc `(Z,X_i)`. Nó không có đường đọc `audit/verification`.

Signal diagnostics V3 kế thừa public/Judge diagnostics và thêm `verification_anchor` cùng `audit_probability`.

## 5. Candidate prediction

`build_candidate` nhóm trên observation của Judge. Việc lặp `A,T` chỉ cộng probability vào cùng group; candidate prediction vẫn là:

```text
P(scoring peer reports 1 | own observation)
```

Prediction semantics:

- `unique_on_reachable_observations` khi mechanism là `rbts` hoặc `hybrid_anchor` và multiplier > 0;
- `arbitrary_reachable_predictions` với fixed hoặc multiplier = 0.

Không dự đoán `T`; không thêm action mới.

## 6. Scoring seam

Giữ `score_judge(reports,predictions,judge)` thuần RBTS và không truyền state/Y/T vào hàm này.

Thêm:

```python
anchor_score(report, audit, verification) -> Fraction
reward(peer_score, mechanism, config, anchor=0) -> Fraction
```

`anchor_score` chỉ kiểm tra binary inputs và trả `audit * int(report==verification)`. `reward` cho hybrid áp công thức spec. Tách hai hàm giúp test mutation “dùng Y thay T” và giữ RBTS boundary.

## 7. Evaluator

`evaluate` với hybrid ghi mỗi state/Judge:

```text
peer_score
anchor_score
peer_reward = f + lambda_peer*peer_score
anchor_reward = anchor_weight*anchor_score
reward, effort_cost, utility
```

Để không đổi payload V1/V2, các field anchor chỉ xuất cho hybrid. State V3 thêm `audit` và `verification`; `y` vẫn chỉ dùng decision metrics.

Totals/conditional hybrid có cùng decomposition. Metrics thêm expected peer/anchor reward và verification agreement. Reward cap dispatch theo mechanism.

`scope` phải là function theo mechanism. V1/V2 giữ `scoring_rule=rbts_eq8`; V3 dùng `hybrid_rbts_plus_verification_anchor`.

## 8. Best response

Với mỗi focal observation, solver tính cho từng report `r`:

```text
I_r = E[RBTS information score | observation, r]
A_r = E[audit * 1[r=T] | observation]
P*  = max prediction score như V2
G_r = lambda_peer*(I_r + P*) + anchor_weight*A_r
```

Report tối ưu lấy mọi tie của `G_r`. Utility effort:

```text
U_e = f + E[max_r G_r] - cost_i*1[e=H]
```

Với RBTS cũ, solver tiếp tục tối ưu `I_r`; với fixed giữ degeneration hiện có.

Certificate hybrid thêm `anchor_by_report`, `anchor_score`, `peer_reward`, `anchor_reward`, `gross_reward_value`. Invariant value-of-information so sánh gross hybrid value H>=L, không so riêng peer score của action đã tối ưu theo hybrid.

Prediction optimum và report optimum là hai cờ độc lập. Khi `lambda_peer=0` nhưng anchor active, prediction arbitrary còn report vẫn có thể unique.

## 9. Exhaustive search

`search_pure` giữ 216 candidates mỗi Z, 432 tổng và 46.656 full effort/report profiles. Nó gọi cùng evaluator/solver với `hybrid_anchor`; không thêm pruning.

Output giữ branch IDs cũ để comparison dễ đọc. `scope` và config xác định model/mechanism nên không có collision artifact.

## 10. CLI, output và freeze

CLI choices thêm `hybrid_anchor`. Validation chặn mismatch version/mechanism trước `new_run`.

Sweep V3 axes theo spec; `compare` cũ vẫn chỉ fixed/RBTS V1/V2. Comparison V2/V3 đầu tiên được thực hiện bằng hai run pin riêng và UI/history ghim; không nhét hai model vào một config parser.

`output.FREEZES` thêm V3 freeze. Manifest chọn spec filename từ mapping theo version, không dùng ternary V1/V2. Research context và limitations ghi đúng anchor semantics.

Source pin tiếp tục lấy toàn bộ source files. V3 run pin raw spec/design/plan/freeze manifest vào `inputs/`.

## 11. API và HTML

`/api/status` trả V3 preset và freeze. `/api/validate` chấp nhận `hybrid_anchor` đúng với V3; operation hiện có dùng chung worker.

Form V3 thêm group verification anchor và reward fields `f,lambda_peer,anchor_weight,reward_budget,payout_value,operating_cost`. Mechanism tự chuyển `hybrid_anchor` khi chọn V3; V1/V2 không hiển thị lựa chọn này.

Analyze V3 hiển thị decomposition peer/anchor, 128 potential states và support size. Search/sweep/history dùng renderer hiện có với label mechanism/model đúng.

Browser scenario V3-B01 phải thực hiện validate, analyze, exact artifact parity, search, mobile/desktop và không có JS error.

## 12. Failure behavior

- Reject V3 with fixed/rbts and V1/V2 with hybrid_anchor.
- Reject missing/unknown anchor fields before run creation.
- Failed/cancelled search không có exhaustive certificate.
- Audit endpoints không làm divide by zero; zero-mass rows không tạo observation groups.
- Artifact directory no-overwrite và terminal manifest bất biến giữ nguyên.
- UI không được gửi `Y`, audit realization hoặc T realization làm strategy input.

## 13. Trình tự triển khai

1. Independent oracle/config/expected fixture và seam tests.
2. Freeze spec/design/plan/assets.
3. Version/config/distribution/reduction.
4. Scoring/evaluator/best response.
5. Search/output/CLI.
6. API/UI/browser.
7. Targeted V3 suite, full regression và completion audit.

Revision này không phải evidence implementation.
