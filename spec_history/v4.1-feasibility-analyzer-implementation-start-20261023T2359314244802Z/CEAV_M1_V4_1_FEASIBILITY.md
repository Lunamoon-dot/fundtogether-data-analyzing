# CEAV-M1 V4.1 — Conditional Scoring + Limited Audit: feasibility trước implementation

**Ngày:** 2026-10-24.  
**Revision:** `limited-audit-feasibility-r1`.  
**Trạng thái:** nghiên cứu giải tích; chưa có model/runtime V4.1, policy grid hoặc engine.  
**Prerequisite:** negative result `all_low_persists_without_audit` của [V4.0 §8](CEAV_M1_V4_CONDITIONAL_SPEC.md).

## 1. Câu hỏi và hai mục tiêu riêng

Audit có thể cung cấp orientation theo một verification signal `T`, nhưng cần chứng minh cả:

- **Effort elicitation:** một unilateral acquisition/use of `X_i` có lợi sau khi trừ cost, tại những nhánh cần thiết để đạt quality gates.
- **Truthful label orientation:** report 1 giữ nghĩa claim đúng, và equilibrium decisions đạt FA/FR/wrong-payout gates theo `Y`.

Report nguyên trạng `X_i`, MAP prediction về `Y`, và report tối đa hóa khả năng khớp `T` là ba target khác nhau. Trong nghiên cứu này, dùng `Y` để đánh giá decision quality; không ép mọi H strategy thành `H01` và không đưa `Y` vào reward.

Với audit-only, optimal report là `argmax_r P(T=r | Z,X_i)`. Viết `p=P(Y=1 | Z,X_i)`:

```text
P(T=1 | Z,X_i) = (1-spec_T) + (sens_T+spec_T-1)*p
audit-optimal report = 1 nếu p >= (spec_T-1/2)/(sens_T+spec_T-1)
```

Giữ cả hai report tại equality. Chỉ khi `sens_T=spec_T>1/2`, threshold trên bằng `1/2`, tương ứng MAP của `Y`. Peer reward trong hybrid còn có thể đổi best response, nên audit presence không tự chứng minh truthfulness.

## 2. Game giả thuyết và baseline

Giữ signal distribution, stationary task-local strategy class, finite score `s_i,t`, majority và information boundary V4.0. Sau khi report khóa, chọn một claim-level `A_t~Bernoulli(q)` độc lập report/strategy; nếu audit thì reveal một `T_t` chung cho ba Judge.

`T_t` độc lập các primitive signals khác khi biết `Y_t`; tasks độc lập theo stratified design. Không audit theo report, không IPW và không sửa majority/payout bằng `T`.

```text
Reward_i,t = f + lambda_peer*(1+s_i,t) + mu*A_t*1(r_i,t=T_t)
Utility = expected batch reward - expected batch effort cost
0 <= q <= 1; f,lambda_peer,mu,kappa >= 0
RewardCap_per_claim = 3*f + 6*lambda_peer + 3*mu <= B
```

Audit-only đặt `lambda_peer=0`, đúng anchor-only payoff V3.0. Baseline được phép chọn `mu,q` trong cùng budget và cùng declared policy set; không cố định một baseline yếu. Conditional+audit phải có `lambda_peer>0` nếu tuyên bố lợi ích của thành phần kết hợp.

Tất cả chi phí có mẫu số rõ:

```text
N=n_0+n_1; v_z=n_z/N; w_z=P(Z=z)
R_z=sum_i E[Reward_i,t | Z_t=z]
C_z=R_z + q*kappa + operating_cost
C_batch_average=sum_z v_z*C_z
C_target_population=sum_z w_z*C_z
C_actual_batch=N*C_batch_average
audit_cost_batch_average=audit_cost_target_population=q*kappa
audit_cost_actual_batch=N*q*kappa
```

`operating_cost` là per-claim và constant ở revision này. Overhead gom batch/latency chưa được định lượng. `B` là reserve cap cho từng claim; reserve cả batch là `N*B`. Main cash gate dùng `C_target_population`; không lấy batch average thay thế.

## 3. Feasibility F1 — Thoát all-Low cần audit tự tạo gain

Giữ peer ở Low, chọn `g*(z) ∈ argmax_r P(T=r | Z=z)` cho từng Judge. Proposition P4-1 làm centered peer score của mọi focal strategy bằng 0.

```text
a_z=max_r P(T=r | Z=z)
delta_i(z)=sum_x P(X_i=x | z)*max_r P(T=r | z,x) - a_z >= 0
gain_i(z)=mu*q*delta_i(z)-c_i
```

**Mệnh đề F1:** full profile all-Low anchor-optimal là NE khi và chỉ khi `gain_i(z)<=0` với mọi Judge và mọi reachable `z`. Best L report đã tối ưu anchor; tối ưu H report map được tách theo `X_i`. Không có deviation khác trong declared class làm tăng utility nếu mọi inequality này giữ.

Loại bỏ full profile này cần ít nhất một `gain_i(z)>0`; điều đó chưa bảo đảm đủ informative Judges trong mỗi branch, loại bỏ mọi equilibrium xấu, hoặc pass quality. Tại equality, tie giữ equilibrium.

Nếu `delta_i(z)=0`, Judge đó không thể được kích thích mua thông tin bằng reward khớp `T` khi peer vẫn Low và `c_i>0`, bất kể `mu,q`. Thông tin có thể cải thiện posterior nhưng không đổi binary action tối ưu.

## 4. Feasibility F2 — Không có lợi thế ở ngưỡng entry

Với cùng `mu,q` và signal/cost assumptions, gain ở F1 hoàn toàn giống audit-only: `lambda_peer` không xuất hiện. Nếu hybrid phá được profile all-Low này thì audit-only cùng `mu,q` cũng phá được; cùng mức reward reserve `B`, baseline đó vẫn hợp lệ vì bỏ `6*lambda_peer` chỉ giảm cap.

Do đó không được ghi claim “conditional scoring giảm audit để bắt đầu thoát all-Low” trong game này. Lợi ích có thể nghiên cứu phải nằm ở các equilibrium khác, sau khi peer đã sử dụng thông tin, hoặc ở quality–cost frontier đầy đủ; chưa có chứng minh lợi ích đó.

Budget cho hệ số anchor tại một `lambda_peer` cố định:

```text
mu_max=(B-3*f-6*lambda_peer)/3
```

Nếu tử số âm, policy invalid. Nếu `mu_max*delta_i(z)<=c_i` với mọi `i,z`, không `q<=1` và `mu<=mu_max` nào loại bỏ được full all-Low profile. Nếu `mu>0` và có `delta_i(z)>0`, boundary để có ít nhất một profitable entry là:

```text
q_entry_boundary=min_(i,z: delta_i(z)>0) c_i/(mu*delta_i(z))
```

Cần `q>q_entry_boundary`, không phải equality. Đây là strict-deviation boundary; không gọi là attained minimum audit hoặc quality threshold. Nếu không có positive delta, mọi gain không dương; nếu boundary `>=1`, không q hợp lệ tạo strict entry ở fixed `mu`.

## 5. Feasibility F3 — Necessary cost floor theo từng phân phối

Một Judge có thể dùng Low và report anchor-optimal. Expected centered peer score bằng 0 trước mọi peer stationary; equilibrium utility không thấp hơn fallback. Vì cost không âm:

```text
LB_z = 3*(f+lambda_peer) + 3*mu*q*a_z + q*kappa + operating_cost
LB_target_population=sum_z w_z*LB_z
LB_batch_average=sum_z v_z*LB_z
LB_actual_batch=N*LB_batch_average
```

Nếu `LB_target_population>4`, policy không thể đạt cash gate hiện tại. Các điều kiện F1–F3 là cần thiết cho các mục tiêu tương ứng, không phải bằng chứng quality đạt hoặc đủ để tồn tại equilibrium mong muốn.

## 6. Hai counterexamples/boundaries phải giữ

**F41-01 — Zero value of information cho binary audit action.** `pi=1/2`, public quality `19/20`, mỗi private quality `4/5`, audit quality `9/10`, tất cả đối xứng; costs dương. Ở `Z=1`:

```text
P(Y=1 | Z=1,X=1)=76/77
P(Y=1 | Z=1,X=0)=19/23
```

Cả hai posterior lớn hơn `1/2`; optimal audit report vẫn là 1. Nhánh `Z=0` đối xứng. Best L và best H đều khớp `T` với xác suất `43/50`; `delta_i(z)=0` cho mọi Judge/branch. All-Low copy-Z tồn tại với mọi `mu,q` hợp lệ. Audit tốt hơn random chưa đủ để khuyến khích effort.

**F41-02 — Positive delta nhưng tie ở boundary.** Dùng tín hiệu/cost F01 V4.0, audit quality `9/10`, `mu=1`. Best L bằng `33/50`, best H bằng `37/50`, `delta=2/25`, cost `1/20`. Gain dương chỉ khi `q>5/8`; tại `q=5/8` all-Low vẫn là NE.

Hai ví dụ này là finite-sum/algebraic checks cho feasibility, chưa phải một V4.1 engine run hoặc policy study.

## 7. Điều kiện tiếp tục và điều kiện dừng

Thực hiện theo thứ tự:

1. Ghi closeout V4.0 và negative result trước khi gọi bất kỳ audit study nào là V4.1.
2. Pin scenario assumptions, audit observation/quality, interpretation của label và cost denominators.
3. Tính delta, entry/budget bound và necessary cash floor. Giữ các miền bất khả thi, không lọc bỏ.
4. Chứng minh/kiểm tra full best responses của các candidate informative và inverted, cùng mọi Low/mixed-effort profile trong declared pure class.
5. Chỉ khi còn miền khả thi có ý nghĩa, viết full V4.1 spec/design/verification plan và preregister một comparison grid với audit-only trước khi xây analyzer.

Quality gates giữ `FA<=1/5`, `wrong_payout_value<=3/20`, `FR<=1/4`, `C_target_population<=4`; không đổi sau khi thấy kết quả. Điều kiện cần đạt không tự cấp policy pass.

Dừng hướng kết hợp nếu không còn miền khả thi dưới assumptions/budget đã chốt, hoặc nếu so sánh hợp lệ cho thấy thành phần conditional không cải thiện quality–cost/audit frontier. Có thể kết luận audit-only phù hợp hơn trong model này. Không thêm authority, stake, slashing hoặc correction để đổi game mà giữ nguyên revision.

## 8. Evidence và giới hạn

Các mệnh đề trên là suy luận trực tiếp từ payoff V4.0 và scalar-audit proposal, không phải bảo đảm nhập từ literature. Xem [source boundary](references/V4_CONDITIONAL_SCORING_SOURCES.md) và [V3 scalar audit](CEAV_M1_V3_ANCHOR_SPEC.md).

Chưa có policy pass, minimum audit được chứng nhận, exhaustive equilibrium result, mixed/coalition guarantee hoặc kết luận production. Full implementation V4.1 chưa được yêu cầu trong giai đoạn này.
