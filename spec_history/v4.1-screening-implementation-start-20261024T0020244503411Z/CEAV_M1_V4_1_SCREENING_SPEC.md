# CEAV-M1 V4.1 — Minimal Equilibrium & Quality Screening

**Ngày:** 2026-10-24.  
**Revision:** `minimal-screening-r1`.  
**Trạng thái:** `SPECIFIED`; offline screening contract, chưa có production CLI/API/UI.  
**Model:** `ceav-m1-v4.1-screening`.  

## 1. Mục tiêu và phạm vi

Screening này kiểm tra trước liệu Conditional Agreement + Limited Audit có lợi ích incremental so với Audit-only trong một miền finite đã công bố hay không. Nó giữ game V4.0: ba Judge, claim nhị phân, hai public-signal branches, majority 2/3, conditional centered score, stationary task-local deterministic strategies và exact `Fraction` arithmetic.

Analyzer là offline research tool. Không đăng ký model vào runtime, không thêm CLI/API/UI production và không gọi finite policy grid là global optimum.

Mỗi kết quả phải tách bốn câu hỏi:

1. **Feasibility:** policy có thỏa reward cap và miền tham số không?
2. **Equilibrium existence:** có pure equilibrium trong declared class không?
3. **Robustness:** mọi pure equilibrium có qua quality/cash gates không?
4. **Equilibrium selection:** model không chọn equilibrium tốt nhất; selection status là `not_modeled`.

## 2. Strategy và payoff

Mỗi branch `z` giữ đủ sáu action:

```text
L0  report 0, không mua X
L1  report 1, không mua X
H00 report 0 với cả X=0,1
H01 report X
H10 report 1-X
H11 report 1 với cả X=0,1
```

Với task thuộc stratum `z`, centered score của Judge `i` là:

```text
s_i,t = (1/2) * sum_(j != i) [
          1(r_i,t=r_j,t)
          - (1/(n_z-1))*sum_(u in I_z,u != t) 1(r_i,t=r_j,u)
        ]
```

Audit là claim-level `A~Bernoulli(q)` và verification signal `T` chỉ được reveal sau khi report khóa. Payoff per claim:

```text
Reward_i = f + lambda_peer*(1+s_i) + mu*A*1(r_i=T)
Utility_i = expected Reward_i - c_i*1(action_i starts with H)
```

Expected peer payoff dùng covariance identity dưới conditional independence giữa tasks:

```text
E[s_i | Z=z] = sum_(j != i) Cov(r_i,r_j | Z=z)
```

Mọi unilateral deviation giữ nguyên toàn bộ peer actions và peer tables. Candidate payoff dùng đúng action của candidate.

## 3. Mechanisms và finite policy grid

Giữ reward budget **`B=6`** cho mọi policy. Một policy chỉ hợp lệ khi:

```text
f, lambda_peer, mu, q, kappa, operating_cost >= 0
0 <= q <= 1
3*f + 6*lambda_peer + 3*mu <= B
```

Grid được pin trước, không phải continuous/global optimization:

```text
Q = {0, 1/4, 1/2, 5/8, 3/4, 1}
M = {0, 1/4, 1/2, 3/4, 1, 5/4, 3/2, 2}
L = {1/4, 1/2, 3/4, 1}
```

- **Audit-only:** `lambda_peer=0`, mọi `mu∈M,q∈Q` hợp lệ; phải giữ toàn bộ valid candidates trước khi screening.
- **Conditional-only:** `lambda_peer∈L`, `mu=0,q=0`.
- **Hybrid:** `lambda_peer∈L`, `mu∈M` với `mu>0`, `q∈Q`, chỉ giữ policy hợp lệ.

Audit-only được phép tối ưu trên toàn bộ `M×Q` hợp lệ. Hybrid không được bù budget bằng cách nới `B`.

## 4. Equilibrium search

Có `6^3=216` branch profiles cho mỗi public branch. Với mỗi profile, analyzer:

1. tính utility exact của ba Judge;
2. kiểm tra cả sáu deviations cho từng Judge;
3. giữ profile nếu mọi regret bằng `0`;
4. ghép Cartesian product của các branch equilibria để lưu mọi full pure equilibrium.

Branch factorization chỉ hợp lệ vì strategy/payoff không có constraint nối hai public branches. Không gọi kết quả là mọi Nash equilibrium của game có history, mixed strategy, coalition hoặc arbitrary batch policy.

Mỗi equilibrium record phải giữ profile, branch actions, effort pattern, action class, utilities, regret witnesses và decision metrics. Các class tối thiểu:

```text
all_low
informative_H01
inverted_H10
asymmetric_effort
other_pure
```

All-Low, informative, inverted và asymmetric-effort không được lọc bỏ.

## 5. Quality, cost và gates

Evaluator dùng ground truth `Y` chỉ để đo quality:

```text
D = 1(sum_i r_i >= 2)
FA = P(D=1 | Y=0)
FR = P(D=0 | Y=1)
wrong_payout_probability = P(Y=0,D=1)
wrong_payout_value = payout_value * wrong_payout_probability
```

Expected cash cost báo cáo theo target population:

```text
C_z = sum_i E[Reward_i | Z=z] + q*kappa + operating_cost
C_target_population = sum_z w_z*C_z
C_batch_average = sum_z v_z*C_z
C_actual_batch = N*C_batch_average
```

Gates giữ nguyên, không chỉnh sau khi thấy output:

```text
FA <= 1/5
FR <= 1/4
wrong_payout_value <= 3/20
C_target_population <= 4
```

Một policy chỉ `robust` khi có ít nhất một full pure equilibrium và **mọi** full pure equilibrium qua toàn bộ gates. Nếu không có pure equilibrium, policy là `no_pure_equilibrium`, không phải pass.

Không chọn equilibrium tốt nhất để cấp pass. Nếu có robust policy, screening chỉ được chọn policy theo rule đã công bố trên worst-equilibrium metrics; `equilibrium_selection=not_modeled` vẫn được giữ trong output.

## 6. Fixtures

### F41-01 — Zero audit value

```text
pi=1/2
public sens/spec=19/20
private sens/spec=4/5 cho A,B,C
audit sens/spec=9/10
cost A=B=C=1/20
f=0, payout_value=1, operating_cost=0, kappa=0
```

Independent finite sums phải cho `anchor_match=43/50`, `high_match=43/50`, `delta=0` ở cả hai branch.

### F41-02 — Positive delta boundary

```text
pi=1/2
public sens/spec=7/10
private sens/spec=4/5 cho A,B,C
audit sens/spec=9/10
cost A=B=C=1/20
f=0, payout_value=1, operating_cost=0, kappa=0
```

Independent finite sums phải cho `anchor_match=33/50`, `high_match=37/50`, `delta=2/25`, nên `q=5/8` là tie boundary khi `mu=1`.

### V3-HET — Heterogeneous anchor inheritance

Kế thừa primitive signal và costs từ [`configs/v3/heterogeneous_anchor.json`](configs/v3/heterogeneous_anchor.json):

```text
pi=1/2
Z sens/spec=4/5,3/5
A private sens/spec=9/10,4/5; cost=1/20
B private sens/spec=3/4,19/20; cost=1/10
C private sens/spec=13/20,7/10; cost=1/25
audit T sens/spec=9/10,9/10
f=1/10, payout_value=1, operating_cost=0, kappa=0
```

`w_z` được tính từ `pi` và public signal; không dùng mặc định `1/2` cho target population. Audit probability là policy parameter từ `Q`; config `q=1/5` chỉ là provenance reference, không khóa grid.

## 7. Evidence, mutation và failure witnesses

Independent oracle phải đối chiếu covariance score với direct finite pair sums trên các action profiles được chọn, kiểm tra exact F41 values, frozen-peer deviations, six actions, reward cap, FA/FR/wrong payout và cost denominators.

Mutation probes chạy trong temporary copy/test-only. Tối thiểu phải bắt các mutation:

- bỏ effort cost;
- đổi dấu hoặc bỏ centered peer covariance;
- cập nhật peer action trong focal deviation;
- dùng batch weight thay target weight cho target cash gate;
- đổi `>=` thành `>` để làm mất tie equilibrium;
- lọc bỏ `H10`, all-Low hoặc asymmetric-effort equilibrium.

Mỗi mutation phải có failure witness rõ. Không sửa golden result để làm mutation pass.

## 8. Acceptance và giới hạn

Acceptance là kết luận finite-grid có thể kiểm tra:

1. Audit-only đã được quét toàn bộ valid `M×Q` grid.
2. Conditional-only và Hybrid đã được quét toàn bộ policy grid hợp lệ dưới `B=6`.
3. Mọi pure equilibrium của từng policy được lưu hoặc policy được đánh dấu `no_pure_equilibrium`.
4. Worst-equilibrium quality/cash metrics được tính riêng khỏi equilibrium selection.
5. Kết luận incremental advantage của Hybrid so với Audit-only chỉ áp dụng trên fixtures/grid này.

Nếu Hybrid không có advantage incremental hoặc không có robust policy trong miền đã pin, ghi negative result và đề xuất dừng Conditional Agreement. Không mở rộng engine/UI trước khi kết luận này được ghi vào artifact.
