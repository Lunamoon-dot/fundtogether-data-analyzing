# CEAV-M1 V4 — Conditional Multi-task Peer Scoring under Common Signals

**Ngày:** 2026-10-24.  
**Spec revision:** `conditional-research-r2-closeout`.  
**Trạng thái:** `SPECIFIED` — research specification V4.0; oracle tham chiếu và closeout được ghi riêng ở §15. Chưa có full engine hoặc runtime acceptance V4.  
**Model identifier dự kiến:** `ceav-m1-v4.0`; chưa phải model được runtime hỗ trợ.  
**Workspace:** `C:\Users\dell\Desktop\fundtogether_data_analyzing`.

## 1. Câu hỏi nghiên cứu

Khi Judge đều thấy tín hiệu chung miễn phí `Z`, liệu phần tương quan giữa các report **sau khi điều kiện trên Z** có tạo động lực thu thập thông tin riêng `X_i`, và có giúp đạt chất lượng quyết định với ít audit hơn không?

V4 tách ba bài toán; một kết quả đúng không thay cho hai kết quả còn lại:

| ID | Bài toán | Yêu cầu đánh giá |
| --- | --- | --- |
| H1 | Common-signal exploitation | Copy `Z` có nhận **centered peer score** dương không? Tổng tiền nhận vẫn phải báo cáo riêng. |
| H2 | Informative equilibrium | Judge có tự nguyện trả effort cost để dùng `X_i` không? Tách tồn tại cân bằng tốt khỏi loại bỏ cân bằng xấu. |
| H3 | Limited audit | Conditional scoring có giảm audit dưới cùng budget, quality gates và uncertainty set so với audit-only không? |

H2 có hai mục tiêu độc lập: **H2-E, effort elicitation**, và **H2-O, truthful label orientation**. Mua và sử dụng `X_i` không chứng minh report đúng hướng nhãn của `Y`; §9 phát biểu đối xứng label và phản ví dụ cụ thể.

Mục tiêu cuối là chất lượng quyết định và chi phí dưới hành vi chiến lược. Số Judge chọn H là diagnostic; không tối đa hóa effort như mục tiêu độc lập.

**Điều kiện dừng sớm:** nếu prototype không audit vẫn có all-Low equilibrium, phải ghi phản ví dụ, chứng minh và giới hạn kết luận trước khi mở nghiên cứu kết hợp audit. Không thêm audit rồi gọi vấn đề không audit đã được giải quyết.

Với prototype được định nghĩa dưới đây, §8 đã đưa ra phản ví dụ tổng quát: all-Low vẫn tồn tại. Đây là kết luận giải tích trong spec, chưa phải certificate từ engine V4.

## 2. Phạm vi và quan hệ với V1–V3.3

Kế thừa likelihood nhị phân, sensitivity/specificity theo từng Judge và ranh giới thông tin từ [spec V2 §5](CEAV_M1_V2_SPEC.md); kế thừa metric decision/loss từ [spec V1 §10](CEAV_M1_SPEC.md). Các mệnh đề V1 §9.4 chỉ áp dụng trong giả định của chúng.

V4 thay đổi game ở các điểm sau:

- Một claim thành batch nhiều task có đối chứng khác task.
- RBTS và peer prediction `p_i` được thay bằng score chỉ dùng binary reports. V4.0 không thu prediction.
- Matching khác task chỉ diễn ra trong cùng public stratum `Z`.
- Phạm vi chiến lược và equilibrium được khai báo lại ở §5; không tự kế thừa chứng nhận exhaustive của V3.

V4.0 không audit, không ground-truth reward, không stake/slashing, không participation/outside option, timeout, appeal, blockchain hoặc settlement. `Y` chỉ thuộc bộ sinh/evaluator. `Z` được coi là quan sát công khai và exogenous; thao túng `Z` hoặc auditor là ngoài model.

V3.3 tiếp tục giữ nguyên. Artifact [study V3.3](results/v33-ipw-full-20261024T052707/report.md) ghi cả ba policy pass `0/18` scenario; [baseline metadata](results/v33-ipw-full-20261024T052707/baseline_comparison.json) vẫn yêu cầu rerun V3.2 cùng budget. Không dùng kết quả đó như baseline V4 đã chạy.

## 3. Prototype được chọn và prior art

Prototype chính là **conditional excess agreement**: agreement cùng task trừ agreement với report khác task trong cùng `Z`. Đây là một công thức nghiên cứu cụ thể, không đồng nhất với toàn bộ họ Correlated Agreement (CA).

| Phương án | Vai trò và giới hạn |
| --- | --- |
| Agreement thô hoặc đối chứng khác task không điều kiện `Z` | Diagnostic cấu trúc: tín hiệu chung có thể tạo tương quan dương. Chưa đủ để tách thông tin riêng. |
| Conditional excess agreement | Được chọn cho V4.0 vì công thức hữu hạn rõ và cho phép chứng minh trực tiếp all-Low. |
| CA với sign matrix học từ dữ liệu hoặc biến thể heterogeneous-task | Prior art/khả năng nghiên cứu khác; không tự thêm vào prototype này. |

CA của Shnayder và cộng sự xét các giả định về task và report strategy riêng. Gao–Wright–Leyton-Brown phân tích tín hiệu chất lượng thấp và limited ground truth với các điều kiện riêng. Lu và cộng sự (2024) đã điều kiện hóa peer prediction trên thông tin synopsis chung để giảm shortcut information. Không nhập bảo đảm của các bài đó thành định lý effort/truthfulness của V4. Đối chứng task heterogeneity cũng đã có prior art.

Nguồn sơ cấp và phạm vi bảo đảm được ghi trong [V4 source note](references/V4_CONDITIONAL_SCORING_SOURCES.md). Các chứng minh ở §7–§9 và §11 là suy luận riêng cho game này. **Chưa có kết luận về tính mới học thuật** của phép điều kiện trên `Z`.

## 4. Phân phối task và thiết kế batch

### 4.1. Target population

Đúng ba Judge `A,B,C`; mỗi task có ground truth `Y_t ∈ {0,1}`, public signal chung `Z_t` và potential private signals `X_A,t,X_B,t,X_C,t`.

```text
P(Y=1) = pi,                  0 < pi < 1
P(S=s | Y=y) = K(s | y; sensitivity_S, specificity_S)
K(1|1;u,v)=u; K(0|1;u,v)=1-u
K(0|0;u,v)=v; K(1|0;u,v)=1-v

w_z     = P(Z=z)
theta_z = P(Y=1 | Z=z)
P(Y=y,X_A=x_A,X_B=x_B,X_C=x_C | Z=z)
  = P(Y=y | Z=z) * product_i K(x_i | y; sens_i,spec_i)
```

Signal sensitivities/specificities thuộc `(1/2,1]`; effort costs `c_i >= 0`. Mọi tham số là common knowledge và hữu tỉ. `X_i` được sinh tiềm năng cả khi Judge chọn L, nhưng strategy L không nhận nó.

### 4.2. Batch có phân tầng

Batch nghiên cứu có hai nhóm `I_0,I_1`, kích thước cố định `n_0,n_1 >= 2`. Chọn tối thiểu `n_0=n_1=2`, tức bốn task, cho fixture hữu hạn đầu tiên. Các task trong `I_z` được lấy độc lập từ phân phối có điều kiện ở §4.1; các task giữa hai nhóm cũng độc lập.

Đây là **stratified experiment**, không tuyên bố batch cân bằng có cùng prevalence với target population. Không giả định bốn task đủ để ước lượng một correlation matrix hay chứng minh sample complexity của CA.

- Metric target-population phải dùng `w_z`, không dùng mặc định `1/2`.
- Báo cáo thêm trung bình batch theo `n_z/(n_0+n_1)`; không trộn hai mẫu số.
- Thiếu hai task độc lập trong một nhóm là `insufficient_stratum_support`; không âm thầm thay bằng baseline không điều kiện hoặc task cùng nguồn.
- Task selection dựa trên `Z` exogenous, không dựa trên report hoặc `Y` chưa quan sát. Independence là giả định cần kiểm tra với dữ liệu ngoài đời; cùng Creator/sự kiện/nguồn bằng chứng có thể vi phạm nó.

Chi phí chờ, gom đủ batch và dependence ngoài model chưa được định lượng. Không gọi kết quả chi phí trong spec là tổng chi phí triển khai thực tế.

## 5. Timing, thông tin và chiến lược

```text
Công bố phân phối, batch design, reward và phạm vi strategy
    ↓
Nature sinh các task; Judge thấy Z_t
    ↓
Judge chọn effort sau Z_t; H trả c_i và nhận X_i,t
    ↓
Gửi binary report r_i,t; khóa toàn bộ report trước khi công bố peer reports
    ↓
Tính score cùng task và đối chứng khác task cùng Z
    ↓
Trả reward; evaluator dùng Y_t để tính majority loss riêng
```

Phạm vi chính là **stationary task-local deterministic strategies**:

```text
effort_i: z -> {L,H}
report_i khi L: z -> {0,1}
report_i khi H: (z,x_i) -> {0,1}
```

Strategy không condition trên task index, batch frequencies, private signals/task history khác, peer reports, ground truth hoặc thông tin hậu kiểm. Đây là giới hạn lớp chiến lược được phân tích; không phải giả định Judge ngoài đời quên các task đã làm.

Mỗi nhánh `z` giữ đủ sáu action `L0,L1,H00,H01,H10,H11`. `H00/H11` được giữ để kiểm tra cost/tie; khác RBTS, V4.0 không còn prediction gain khi H bỏ qua `X_i`.

Utility game là expected **tổng reward của batch trừ tổng effort cost**. Vì mỗi nhánh có số task dương và không có constraint nối nhánh, kiểm tra branch-local deviations tương đương kiểm tra stationary strategy deviation toàn batch. Trung bình target-population là metric báo cáo riêng, không thay payoff của batch.

Equilibrium identifier dự kiến: `pure_strategy_nash_in_stationary_task_local_class`. Không gọi là mọi Nash equilibrium của game cho phép arbitrary batch/history strategies. Phản ví dụ all-Low ở §8 mạnh hơn phạm vi này vì score triệt tiêu theo từng realization.

## 6. Score hữu hạn, reward và budget

Với `z=Z_t`, score của Judge `i` ở task `t` là:

```text
s_i,t = (1/2) * sum_(j != i) [
          1(r_i,t = r_j,t)
          - (1/(n_z-1)) * sum_(u in I_z, u != t) 1(r_i,t = r_j,u)
        ]

-1 <= s_i,t <= 1
PeerScore_i,t = 1 + s_i,t             # trong [0,2]
Reward_i,t   = f + lambda_peer * PeerScore_i,t
Utility_i    = E[sum_t Reward_i,t - sum_t c_i * 1(e_i,t=H)]
```

Dùng toàn bộ cặp khác task trong nhóm; không cần học sign matrix hoặc ước lượng posterior để tính reward. `Y`, `X_i`, độ đúng của decision và report chưa khóa không đi vào scoring. Nhóm và trọng số không được thay đổi sau khi thấy report.

Offset `+1` giữ reward không âm với `f,lambda_peer >= 0`; không clipping, không slashing và không phân chia lại reward pool. Offset là chi phí thật:

**Copy Z có centered score bằng 0 nhưng vẫn nhận `f + lambda_peer` mỗi task. H1 không có nghĩa là không trả tiền cho copy Z.**

```text
RewardCap_per_claim = 3*f + 6*lambda_peer <= B
RewardCap_batch     = (n_0+n_1) * RewardCap_per_claim
v_z = n_z/(n_0+n_1)
R_z = sum_i E[Reward_i,t | Z_t=z]
o_z = operating cost phân bổ cho một claim trong stratum z
C_z = R_z + o_z                                             # V4.0 không audit
expected_reward_batch_average      = sum_z v_z * R_z
expected_reward_target_population  = sum_z w_z * R_z
cash_review_cost_batch_average     = sum_z v_z * C_z
cash_review_cost_target_population = sum_z w_z * C_z
expected_cash_cost_actual_batch    = (n_0+n_1) * cash_review_cost_batch_average
```

`operating_cost` kế thừa được hiểu là per-claim và giống nhau giữa các stratum, tức `o_z=operating_cost`; công thức phân tầng làm rõ mẫu số, không tự thêm operating-cost policy mới. Nếu có overhead cố định cho cả batch phải khai báo cách phân bổ riêng. Batch cân bằng vẫn khác population nếu `w_z != 1/2` và conditional costs khác nhau.

`B` là worst-case reward cap cho từng claim, không phải một trong hai expected cost averages. Reserve cả batch là `N*B`, với `N=n_0+n_1`. Không lấy expected score để giảm worst-case reserve. Effort cost là chi phí tài nguyên của Judge, không cộng lần nữa vào cash review cost.

## 7. Đại lượng kỳ vọng và giá trị thông tin

Với strategy stationary và hai task khác nhau độc lập trong cùng stratum:

```text
E[s_i,t | Z_t=z]
  = (1/2) * sum_(j != i) [
      P(r_i,t=r_j,t | z)
      - sum_(b in {0,1}) P(r_i=b | z) P(r_j=b | z)
    ]
  = sum_(j != i) Cov(r_i,r_j | Z=z)
```

Đẳng thức cuối dùng identity binary equality. Khi report chỉ phụ thuộc local signal và các private signals độc lập có điều kiện theo `Y`:

```text
d_i(z) = E[r_i | Y=1,Z=z] - E[r_i | Y=0,Z=z]
E[s_i | z] = theta_z*(1-theta_z) * d_i(z) * sum_(j != i) d_j(z)
```

Ở L hoặc H bỏ qua `X_i`, `d_i=0`. Với `H01`, `d_i=sens_i+spec_i-1`; với `H10`, dấu đảo lại. Chỉ định nghĩa conditional expectations trên support có xác suất dương; nếu `theta_z` là 0 hoặc 1 thì covariance bằng 0 trực tiếp.

Đây là giá trị kỳ vọng dưới independence/stationarity, không phải mỗi batch đều có score dương khi H. Sample variance có thể lớn và task correlation có thể phá phép phân tích.

Với peer strategy cố định, tính riêng:

```text
V_L,i(z) = max_(L report) E[Reward_i | z]
V_H,i(z) = max_(H report map) E[Reward_i | z]       # trước effort cost
Delta_i(z) = V_H,i(z) - V_L,i(z) - c_i
```

`V_H >= V_L` trước chi phí vì H có thể bỏ qua `X_i`; điều này không bảo đảm `Delta_i(z)>0`. Mỗi candidate phải dùng chính report map của nó. Optimum của focal trả riêng; không thay candidate bằng optimum hoặc cho peer thích ứng theo deviation.

## 8. Phản ví dụ bắt buộc và điều kiện dừng V4.0

### Proposition P4-1 — All-Low tồn tại với mọi lambda hợp lệ

**Giả định:** game không audit ở §4–§6; `n_z>=2`; `c_i>=0`; `f>=0`; mọi `lambda_peer>=0` thỏa cap `3*f+6*lambda_peer<=B`; Low report là hàm tất định `g_i(Z)` trong declared strategy class. Không cần các Judge dùng cùng `g_i`.

**Phát biểu:** với mọi cấu hình hợp lệ nêu trên và mọi bộ `(g_A,g_B,g_C)`, profile `e_i=L, r_i=g_i(Z)` là pure Nash equilibrium của V4.0. Do đó tuning lambda hoặc tăng batch size vẫn giữ all-Low, trong phạm vi score/strategy/payoff đã định nghĩa.

**Chứng minh:**

Giữ mọi peer ở `L`, với `r_j,t=g_j(Z_t)`. Các Judge có thể dùng các hàm `g_j` khác nhau. Với mọi `u,t` trong cùng `I_z`:

```text
r_j,t = r_j,u = g_j(z)
1(r_i,t=r_j,t) - 1(r_i,t=r_j,u) = 0
```

Do đó `s_i,t=0` với **mọi report của focal**, theo từng realization. Mua thêm `X_i` không thay reward. Với `c_i>0`, effort H làm utility giảm nghiêm ngặt; với `c_i=0`, effort hòa. Đổi Low report cũng hòa về reward.

Vì vậy **mọi profile tất cả Judge dùng Low là Nash equilibrium**, kể cả all-copy-Z, all-PASS và all-FAIL. Đây không phải strict equilibrium theo report, và không nói game sẽ hội tụ tới profile nào. Lập luận vẫn áp dụng cho focal deviation dùng nhiều thông tin task hơn, miễn peer giữ report Low và grouping theo `Z` không đổi.

Tổng gain của một batch deviation là `-sum_t c_i*1(e_i,t=H)<=0`; report-only deviations có gain 0. Khi cost bằng 0, H là tie, không phải strict loss. Kết luận phổ quát dựa trên identity theo từng realization, không dựa trên hữu hạn lambda/batch sizes được oracle lấy làm probes.

### Hệ quả quality gate

All-PASS có false approval bằng 1; all-FAIL có false rejection bằng 1. Vì chúng luôn tồn tại trong game V4.0:

```text
worst_pure_equilibrium_false_approval = 1
worst_pure_equilibrium_false_rejection = 1
```

V4.0 không thể pass các worst-equilibrium gates kế thừa (`FA <= 1/5`, `FR <= 1/4`). Không cần sweep thêm `lambda_peer` hoặc tăng batch size để bác bỏ mục tiêu loại bỏ all-Low cho **công thức này**. Không suy rộng thành định lý bất khả thi cho mọi conditional mechanism.

### Stop record bắt buộc

Khi đóng V4.0, record phải có:

- `finding`: `all_low_persists_without_audit`;
- assumptions, score/payoff revision, profile `g_i`, mọi reachable `Judge × Z`;
- centered score `0`, reward `f+lambda_peer`, deviation gain `-c_i` cho H và `0` cho Low-report changes;
- distinction: H1 về loại bỏ centered reward đạt dưới giả định; mục tiêu loại bỏ all-Low bị bác bỏ; H2 existence/decision quality vẫn đánh giá riêng;
- failure witnesses của all-PASS/all-FAIL đối với quality gate;
- `engine_certificate: not_run` cho tới khi thật sự có engine/oracle evidence.

**Dừng nhánh thiết kế V4.0 nhằm loại bỏ all-Low bằng cách tuning score này.** Vẫn có thể làm oracle tối thiểu để xác nhận phản ví dụ. Không cần xây engine tổng quát, UI hoặc sweep lớn để tạo lại kết luận giải tích.

## 9. Fixture giải tích: cân bằng informative không thay được cân bằng xấu

`V4-F01` là synthetic/assumption fixture, không phải dữ liệu Judge thực:

```text
pi = 1/2
sens_Z = spec_Z = 7/10
sens_i = spec_i = 4/5, c_i = 1/20 cho cả ba Judge
f = 0, lambda_peer = 1, B = 6
n_0 = n_1 = 2; payout_value = 1; operating_cost = 0
```

Ở cả hai nhánh, `theta_z*(1-theta_z)=21/100`. Nếu cả ba dùng `H01`, mỗi covariance là `189/2500`; centered score là `189/1250`.

Với hai peer `H01`, sáu action của focal có expected centered score lần lượt:

| Action | `L0` | `L1` | `H00` | `H01` | `H10` | `H11` |
| --- | --- | --- | --- | --- | --- | --- |
| Score | `0` | `0` | `0` | `189/1250` | `-189/1250` | `0` |

H còn trừ cost `1/20`. `H01` hơn best L đúng `253/2500`; vì vậy all-`H01` là equilibrium trong lớp stationary đã định nghĩa. Không suy ra từ so sánh tổng utility hai profile.

| Profile equilibrium | Centered score/Judge | Utility/Judge/task | Accuracy | FA | FR |
| --- | --- | --- | --- | --- | --- |
| All-Low copy `Z` | `0` | `1` | `7/10` | `3/10` | `3/10` |
| All-`H01`, report `X_i` | `189/1250` | `2753/2500` | `112/125` | `13/125` | `13/125` |
| All-`H10`, report `1-X_i` | `189/1250` | `2753/2500` | `13/125` | `112/125` | `112/125` |

Dòng cuối có cùng payoff vì score bất biến khi cùng đảo label mọi report, còn majority decision cũng đảo. Informative theo nghĩa dùng `X_i` không đồng nghĩa với đúng semantic label của `Y`.

### Proposition P4-4 — Đối xứng label không audit

**Giả định:** game V4.0; cùng đảo mọi report bằng `tau(r)=1-r`, giữ effort và phân phối primitive signals. Strategy class đóng dưới phép đảo này: `L0↔L1`, `H00↔H11`, `H01↔H10` ở từng public branch.

**Phát biểu và chứng minh:** mọi equality indicator cùng task và khác task giữ nguyên khi đảo cả hai report. Do đó centered score, reward, cost và utility của mọi profile giữ nguyên. Mỗi unilateral deviation có một deviation đối ứng dưới `tau` với cùng gain. Suy ra `sigma` là NE khi và chỉ khi `tau(sigma)` là NE.

Với majority của ba report:

```text
D(tau(sigma)) = 1-D(sigma)
Accuracy(tau(sigma)) = 1-Accuracy(sigma)
FA(tau(sigma)) = 1-FA(sigma)
FR(tau(sigma)) = 1-FR(sigma)
```

V4.0 không có thành phần reward định hướng nhãn 0/1 theo `Y`. Tách H2-E khỏi H2-O là bắt buộc. Khi nghiên cứu audit, phải phân biệt report `X_i`, MAP label của `Y` và report tối ưu để khớp `T`; chúng không mặc nhiên đồng nhất.

Các phân số trong fixture đã được đối chiếu ngày 2026-10-24 bằng finite sums độc lập dùng `Fraction`, không import production evaluator. Đây là kiểm tra số học cho spec, **không phải suite hoặc engine certificate V4**. §13 quy định evidence tái lập phải được tạo trước acceptance sau này.

## 10. Limited audit: câu hỏi giai đoạn sau

Phần này chốt cách đặt bài toán so sánh, **chưa đưa audit vào game V4.0**. Nếu tiếp tục, cần spec model riêng và ghi nhận stop record ở §8 trước; không đổi nghĩa V4.0 đã pin.

Đối chứng trực tiếp dùng cách audit **claim-level scalar q của V3.0**, không lấy per-Judge report-sensitive audit V3.2/V3.3 rồi giữ nguyên công thức chi phí:

```text
A_t ~ Bernoulli(q), độc lập report/strategy, sau khi report khóa
T_t là một verification signal chung cho ba Judge trong task t
T_t độc lập Z_t,X_A,t,X_B,t,X_C,t khi biết Y_t

Reward_i,t = f + lambda_peer*(1+s_i,t) + mu*A_t*1(r_i,t=T_t)
RewardCap_per_claim = 3*f + 6*lambda_peer + 3*mu <= B
audit_cost_z = q*kappa                              # một audit/claim
C_z = sum_i E[Reward_i,t | Z_t=z] + q*kappa + o_z
cash_review_cost_batch_average     = sum_z v_z*C_z
cash_review_cost_target_population = sum_z w_z*C_z
expected_cash_cost_actual_batch    = (n_0+n_1)*cash_review_cost_batch_average
expected_audit_cost_batch_average = expected_audit_cost_target_population = q*kappa
expected_audit_cost_actual_batch = (n_0+n_1)*q*kappa
```

`q ∈ [0,1]`, `mu,kappa >= 0`; verification sensitivity/specificity thuộc `(1/2,1]`. Không IPW, không report-dependent q; `q=0` hợp lệ. `T` không sửa `D` hoặc payout. Audit-only đặt `lambda_peer=0`; cùng `f,mu,q` thì đúng payoff/chi phí anchor-only V3.0.

Ba nhánh đối chứng: conditional-only, audit-only và conditional+audit. Nhánh kết hợp chỉ được ghi nhận lợi ích kết hợp khi `lambda_peer>0`; `lambda_peer=0` chính là baseline.

Để so sánh công bằng phải giữ:

- cùng ba Judge, signal/cost scenario, target weights, majority, payout value, provenance và equilibrium scope;
- cùng reward budget `B`, fixed fee `f`, audit quality, cost per audit và operational-cost assumptions;
- cùng declared uncertainty set và quality/cash gates; tính đủ offset peer reward;
- chính sách `(lambda_peer,mu,q)` công bố trước; baseline audit-only được phép tối ưu `mu,q` trong cùng budget, không cố định một baseline yếu;
- V3 historical run chỉ là reference nếu chưa rerun hoặc chưa chứng minh mapping payoff/metric cùng inputs. Không gọi source compatibility là executed evidence.

## 11. Giới hạn audit cần chứng minh trước khi tuning

### P4-2 — Conditional score không hạ ngưỡng deviation khỏi all-Low khi giữ mu

Với peer deterministic theo `Z`, chọn all-Low report tối ưu cho anchor:

```text
g*(z) ∈ argmax_r P(T=r | Z=z)
a_z = max_r P(T=r | Z=z)
delta_i(z) = sum_x P(X_i=x | z) * max_r P(T=r | z,x) - a_z
```

Peer centered score vẫn bằng 0 cho mọi focal strategy theo P4-1. Do đó private gain từ effort chính xác là:

```text
gain_H_over_best_L = mu*q*delta_i(z) - c_i
```

Không có `lambda_peer` trong biểu thức. Nếu mọi `i,z` đều có gain `<=0`, profile all-Low anchor-optimal vẫn là equilibrium. Loại bỏ profile này cần ít nhất một deviation dương; tại equality, tie vẫn giữ equilibrium.

Với cùng `mu`, conditional scoring không giảm ngưỡng audit cho deviation khỏi profile này so với audit-only. Điều đó khác với khả năng giảm ngưỡng để **một informative candidate** trở thành equilibrium khi peer đã informative. Cả hai threshold đều chưa chứng minh worst-equilibrium quality pass.

Fixture đối chiếu tương lai: giữ tín hiệu/cost §9, thêm `sens_T=spec_T=9/10`, `mu=1`. Ở mỗi `z`, best L dự đoán `T` đúng `33/50`, best H đúng `37/50`; `delta_i(z)=2/25`. Gain dương chỉ khi `q>5/8`. Tại `q=5/8`, all-Low vẫn tồn tại. Đây là boundary của deviation, không phải minimum audit để pass quality.

### P4-3 — Necessary cost floor

Trong cùng game audit tương lai, một Judge luôn có thể chọn L và report anchor-optimal, với expected centered peer score bằng 0 trước mọi peer stationary. Do equilibrium utility không thấp hơn fallback và effort cost không âm:

```text
cash_review_cost >= 3*(f+lambda_peer)
                    + 3*mu*q*sum_z w_z*a_z
                    + q*kappa + operating_cost
```

Biểu thức trên là `cash_review_cost_target_population`. Với batch average, thay `w_z` bằng `v_z=n_z/N`; với actual batch total, nhân batch-average bound với `N`. Scalar `q,kappa` giống nhau giữa các stratum nên phần audit operating cost bằng nhau theo hai cách lấy trung bình; conditional reward costs vẫn có thể khác.

Đây là cận dưới cần thiết, không phải chi phí thực tế hoặc điều kiện đủ. Quality/cash gates chính được đánh giá trên target population; batch averages và actual batch totals được xuất riêng. Nếu cận dưới vượt cash gate, ghi feasibility certificate và giữ điểm fail; không sửa gate hoặc lược bỏ offset để tiếp tục tuning.

## 12. Metrics, gates và cách kết luận H1–H3

Các expected values/joint event probabilities của target population được tính bằng `sum_z w_z * E[value | Z=z]`. FA/FR dùng joint numerators rồi chia đúng conditional denominators theo `Y`; không lấy trung bình các stratum error rates theo `w_z` để thay Bayes conditioning theo `Y`.

```text
D_t = 1(r_A,t+r_B,t+r_C,t >= 2)
FA = P(D=1 | Y=0); FR = P(D=0 | Y=1)
FA = sum_z w_z * P(Y=0,D=1 | Z=z) / (1-pi)
FR = sum_z w_z * P(Y=1,D=0 | Z=z) / pi
wrong_payout_probability = P(Y=0,D=1)
wrong_payout_value = payout_value * wrong_payout_probability
```

Báo cáo thêm expected peer score/reward, anchor reward nếu có, fixed/offset payments, cash review cost, effort cost, audit rate/cost, worst-case cap, score/payment variance theo batch design và utility từng Judge/nhánh. Accuracy là diagnostic.

H1 được đánh giá bằng score identity, không bằng accuracy. H2 phải có full best-response witnesses và tách `informative_equilibrium_exists`, `bad_equilibrium_exists`, `decision_quality_passes`. Không dùng utility all-H lớn hơn all-L như bằng chứng transition/selection.

Research thresholds giữ nguyên để làm reference comparison:

```text
max_false_approval_rate = 1/5
max_wrong_payout_value = 3/20
max_false_rejection_rate = 1/4
max_cash_review_cost = 4
```

Mỗi scenario lấy metric xấu nhất trên mọi pure equilibrium trong declared class. Invalid, incomplete search và no-pure-equilibrium không được pass. Một policy robust chỉ khi mọi declared uncertainty point pass; không đồng nhất hai worst metrics với cùng một equilibrium witness nếu chúng đạt cực trị ở các equilibrium khác nhau.

H3 chỉ được đánh giá sau stop record và spec audit riêng. Phải preregister finite policy grid và uncertainty grid, rồi so sánh `minimum_audit_on_declared_grid` của policy robust giữa hai cơ chế. Không gọi minimum trên grid là continuous/global minimum. Nếu một phía không có policy đạt gate thì ghi `no_feasible_policy_on_grid`, không tự gán audit rate bằng 1 hoặc suy ra lợi ích định lượng.

Không chốt grid hay kết quả audit trong revision này. Trade-off/Pareto report phải giữ false approval, wrong payout, false rejection, cash cost và audit exposure riêng. Mọi sensitivity analysis đổi gates/assumptions dùng study revision riêng.

## 13. Verification requirements cho giai đoạn sau

Đây là evidence plan trong research spec, chưa phải các test đã tồn tại hoặc đã chạy:

| T-ID dự kiến | Requirement và independent oracle |
| --- | --- |
| V4-T01 | Chuẩn hóa `w_z,theta_z` bằng Bayes; mass từng stratum đúng 1; endpoint support rõ. |
| V4-T02 | Score finite-batch đúng §6, không dùng own task làm cross-task reference; cả hai peer có trọng số `1/2`. |
| V4-T03 | Finite sums hai task độc lập khớp equality/covariance identity §7; không sinh expected từ production score. |
| V4-T04 | Mọi all-Low profile cho centered score exact 0 theo realization; đủ sáu focal actions, mỗi Judge/nhánh. |
| V4-T05 | Fixture §9 có all-H và all-L cùng tồn tại; label-flipped equilibrium giữ reward và đổi decision quality. |
| V4-T06 | Best response giữ peer strategy, dùng candidate payoff thật, đủ effort/report deviations và ties; `lambda=0`, `c=0` xử lý riêng. |
| V4-T07 | Offset/cap/cash accounting đúng; không coi score 0 là payment 0 hoặc trừ effort cost hai lần. |
| V4-T08 | Batch imbalance không đổi target weights; thiếu stratum support báo lỗi; dependent-task fixture phát hiện assumption violation. |
| V4-T09 | Nếu có search, xác nhận đầy đủ declared class, retained bad equilibria và worst-metric witnesses. |
| V4-T10 | Audit tương lai: độc lập claim-level event, chi phí `q*kappa`, P4-2/P4-3, equality boundary và baseline parity. Chưa thuộc acceptance V4.0. |

Trước mọi analyzer implementation phải tạo `ENGINE_DESIGN_V4_*.md`, `VERIFICATION_PLAN_V4_*.md`, independent oracle/red fixtures và implementation-start freeze từ raw bytes/hash thực tế. Không backdate hoặc dùng spec được tạo hôm nay làm bằng chứng một implementation trước đó đã preregister.

Search sau này có thể có `216` stationary action candidates mỗi stratum, `432` branch candidates khi cả hai stratum reachable, vì **game cụ thể này** có expected payoff tách nhánh. Phải chứng minh factorization và kiểm tra đủ sáu deviations; không dùng lại con số V3 như bằng chứng bao phủ arbitrary batch strategies. Mở rộng strategy scope cần tính lại enumeration contract.

Mutation requirements tối thiểu: cross-task reference dùng nhầm task hiện tại; bỏ điều kiện `Z`; chia sai `n_z-1`; nhìn `Y` trong scoring; cho L nhìn `X_i`; cập nhật peer khi focal deviation; bỏ offset khỏi cash cost; chọn best equilibrium; đổi claim-level audit cost thành per-Judge; dùng `>=` để loại equilibrium tại tie. Mỗi probe sau này phải liên kết test cụ thể, không gọi danh sách này là mutation evidence.

## 14. Deliverables và trạng thái hiện tại

| Phần | Trạng thái revision này |
| --- | --- |
| Game V4.0, finite score, strategy scope, reward/budget | `SPECIFIED` |
| Counterexample all-Low và cost/threshold derivations | Lập luận giải tích trong spec; fixture có đối chiếu số học độc lập |
| Literature/novelty boundary | Nguồn sơ cấp trong source note; chưa systematic novelty review |
| V4 engine, CLI, API, UI, config validator | `NOT_IMPLEMENTED` |
| Fixed-fixture reference oracle | `VERIFIED` — 9 tests, 43,008 statewise checks, 30 F01 certificates |
| Exhaustive equilibrium certificates, browser/release acceptance | `NOT_RUN` |
| Conditional+audit model/study | `PROPOSED_FOLLOW_UP`; chưa đưa vào V4.0 |

Acceptance nghiên cứu V4.0 có thể kết thúc ở **negative result được chứng minh rõ**. Không cần kết quả tích cực để xem nghiên cứu có giá trị; cũng không gọi việc viết spec hay đối chiếu phân số là engine đã được kiểm chứng.

Không sửa historical artifacts, không nới gate và không nhập code/config từ workspace FundTogether cũ để thay kết quả này.

## 15. V4.0 closeout evidence

Revision `conditional-research-r2-closeout` được đối chiếu bằng independent reference oracle ở:

```text
verification/oracle_v4.py
tests/test_v4_research_oracle.py
```

Artifact run mới, không ghi đè output cũ:

```text
results/v4-research-closeout-20261023T2357325229450Z/
```

Artifact này pin raw bytes của spec V4.0, feasibility note V4.1, source note, oracle và test file trong `inputs/`, kèm `manifest.json`, `oracle.json` và `report.md`. Manifest đánh dấu `implementation_start=false` và `preregistered=false`; đây là closeout của research specification, không phải implementation freeze hay engine acceptance.

Các kiểm tra đã chạy:

```text
python -m unittest tests.test_v4_research_oracle -v
python -O -m unittest tests.test_v4_research_oracle -v
python verification/oracle_v4.py --out results/v4-research-closeout-20261023T2357325229450Z
```

Kết quả oracle là `status=passed`, finding `all_low_persists_without_audit`, với statewise finite probes và sáu-action certificates của F01. Regression O09 còn cố ý thay `realized_score` bằng hàm sai trong subprocess `-O`; oracle bị từ chối với `AssertionError`, chứng minh guard không bị tối ưu hóa bỏ qua. Không được coi các kiểm tra này là bằng chứng cho exhaustive equilibrium search, full engine, audit advantage hoặc production behavior.

Red evidence trước khi oracle tồn tại được giữ nguyên tại:

```text
results/v4-oracle-red-20261023T235006391555Z/unittest.log
```

Red run là bằng chứng test-first của fixture/oracle độc lập, không phải lỗi của model V4.0.
