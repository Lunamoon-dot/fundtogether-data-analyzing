# CEAV-M1 V3 — Đặc tả hybrid reward với verification anchor

**Model version:** `ceav-m1-v3.0`

**Mechanism identifier:** `hybrid_anchor`

**Spec revision:** `verification-anchor-r1`

**Ngày:** 23/10/2026

**Trạng thái hiện tại:** `SPECIFIED`; chưa có engine design V3, verification plan V3, freeze implementation-start, code hoặc evidence V3.

**Workspace:** `C:\Users\dell\Desktop\fundtogether_data_analyzing`

## 1. Vai trò của tài liệu

Tài liệu này định nghĩa Version 3 của CEAV-M1. V3 thay payoff của model V2 bằng một hybrid reward gồm:

- score peer-prediction RBTS đang có;
- score từ một nguồn kiểm chứng độc lập được lấy sau khi report đã khóa;
- chi phí High Effort riêng của từng Judge.

V3 giữ các phần sau từ [CEAV_M1_V2_SPEC.md](CEAV_M1_V2_SPEC.md): một claim nhị phân, ba Judge A/B/C, prior, tín hiệu chung `Z`, tín hiệu riêng `X_i`, sensitivity/specificity riêng, effort chọn sau `Z`, sáu action mỗi nhánh, majority 2/3, exact rational arithmetic và phạm vi pure-strategy equilibrium của reduced normal-form representation.

V3 thay đổi game nên dùng model version mới. [CEAV_M1_V2_2_INCENTIVE_SPEC.md](CEAV_M1_V2_2_INCENTIVE_SPEC.md) tiếp tục là diagnostic baseline của model V2; không sửa V2.2 để giả làm V3.

Tài liệu này là nguồn chuẩn cho distribution mở rộng, timing của verification anchor, hybrid payoff, budget và acceptance V3. Các phần V2/V1 chỉ được kế thừa khi tài liệu này nói rõ.

## 2. Vấn đề V3 cần kiểm tra

RBTS V2 trả thưởng hoàn toàn theo report/prediction của peer. V2.2 đã tìm thấy trong config heterogeneous hiện tại:

- candidate all-High có accuracy cao nhưng không phải cân bằng;
- năm trong sáu nhánh `Judge × Z` không tự chọn High Effort;
- một số best High action bỏ qua `X_i` trong report;
- các pure equilibria retained đều có Low Effort.

Ngoài instance đó, V1 P4 đã chứng minh một failure có tính cấu trúc trong game hiện tại: nếu cả ba Judge cùng báo một quy tắc dựa trên tín hiệu chung và prediction ở endpoint, họ có thể đạt RBTS score tối đa mà không mua `X_i`.

V3 không giả định việc thêm anchor chắc chắn giải quyết failure. Câu hỏi nghiên cứu của V3 là:

```text
Khi giữ cùng signal model, strategy space và budget,
phân bổ một phần reward từ peer agreement sang verification anchor
có làm High Effort sử dụng X_i trở thành cân bằng,
đồng thời loại bỏ hoặc giảm tập cân bằng Low Effort hay không?
```

## 3. Quyết định thiết kế

### 3.1. Có trong V3.0

- Một biến audit claim-level `A ∈ {0,1}` được lấy ngẫu nhiên sau khi report khóa.
- Một tín hiệu kiểm chứng nhị phân `T ∈ {0,1}` có sensitivity/specificity riêng đối với `Y`.
- `T` độc lập có điều kiện với `Z,X_A,X_B,X_C` khi đã biết `Y`.
- Judge không thấy `A`, `T` hoặc `Y` trước khi gửi report.
- Hybrid reward gồm RBTS peer score và anchor score.
- Cùng sáu action `L0,L1,H00,H01,H10,H11` tại mỗi `Z`.
- Best response và exhaustive pure-equilibrium search dưới payoff V3.
- Exact sweep theo `lambda_peer`, `anchor_weight`, `audit_probability`, cost và chất lượng anchor.
- So sánh V2 RBTS và V3 hybrid dưới cùng signal config, profile và worst-case reward budget.

### 3.2. Không thuộc V3.0

- Xây auditor/oracle production hoặc xác định tổ chức nào có quyền phát `T`.
- Dùng Creator tự khai `T` mà không có provenance độc lập.
- Blockchain, stake, slashing, appeal, commit–reveal hoặc escrow settlement.
- Cho `T` trực tiếp sửa decision `D` hoặc đảo ngược payout.
- Mixed, correlated, coalition-proof hoặc Sybil-resistant equilibrium.
- Judge học tham số qua nhiều vòng hoặc reputation động.
- Tự ước lượng chất lượng anchor từ dataset V2.1 hiện tại.
- Khẳng định cơ chế phù hợp production chỉ từ synthetic data.

V3.0 là model nghiên cứu về incentive. Việc triển khai nguồn kiểm chứng ngoài đời là một bài toán riêng.

## 4. Ký hiệu và miền tham số

V3 kế thừa `Y,pi,Z,X_i,e_i,c_i,r_i,p_i,f,B,V,operating_cost` từ V2 và thêm:

| Ký hiệu | Ý nghĩa | Miền V3.0 |
| --- | --- | --- |
| `A` | Claim có được audit hay không | `{0,1}` |
| `q` | Xác suất audit `P(A=1)` | `0 <= q <= 1` |
| `T` | Tín hiệu kiểm chứng sau report | `{0,1}` |
| `sens_T` | `P(T=1 | Y=1)` | `1/2 < sens_T <= 1` |
| `spec_T` | `P(T=0 | Y=0)` | `1/2 < spec_T <= 1` |
| `lambda_peer` | Trọng số RBTS peer score | `>= 0` |
| `mu_anchor` | Trọng số anchor score | `>= 0` |

Trong JSON, `mu_anchor` được lưu bằng field `anchor_weight`; các artifact toán phải xuất cả ký hiệu và field name để tránh nhầm nghĩa.

`T` là kết quả của một thủ tục kiểm chứng độc lập, không phải report của Judge khác. Nó có thể mô hình hóa audit tài liệu, kiểm tra hiện trường, oracle có bằng chứng hoặc ground truth quan sát trễ. `sens_T=spec_T=1` biểu diễn anchor hoàn hảo; giá trị thấp hơn 1 biểu diễn anchor có sai số.

`Y` vẫn là ground truth ẩn dùng để sinh phân phối và đo loss. V3 không giả định hệ thống biết `Y` tại thời điểm Judge hành động.

## 5. Phân phối mở rộng

Giữ likelihood nhị phân của V2:

```text
K(s | y; u,v) =
    u       nếu y=1 và s=1
    1-u     nếu y=1 và s=0
    v       nếu y=0 và s=0
    1-v     nếu y=0 và s=1
```

Nature sinh primitive signals như V2:

```text
Y ~ Bernoulli(pi)
P(Z=z | Y=y)   = K(z | y; sens_Z,spec_Z)
P(X_i=x | Y=y) = K(x | y; sens_i,spec_i)
```

Sau khi report khóa, audit và verification signal có phân phối:

```text
A ~ Bernoulli(q)
P(T=t | Y=y) = K(t | y; sens_T,spec_T)
```

Giả định độc lập:

```text
A độc lập với Y,Z,X_A,X_B,X_C và mọi strategy.
T độc lập với Z,X_A,X_B,X_C khi đã biết Y.
```

Để tích phân exact, engine có thể dùng potential state:

```text
w3 = (y,z,x_A,x_B,x_C,a,t)
```

với:

```text
P(w3) = P(y,z,x_A,x_B,x_C)
        * q^a * (1-q)^(1-a)
        * K(t | y; sens_T,spec_T)
```

Có tối đa 128 row. Khi `q` hoặc chất lượng anchor nằm ở endpoint, row xác suất 0 có thể được bỏ nhưng engine phải ghi `support_size`; tổng positive mass vẫn đúng bằng 1. Toàn bộ phép tính dùng `Fraction`.

`T` tiềm năng khi `A=0` chỉ là cách tích phân chung; nó không được reveal và không tạo reward.

## 6. Timing và information boundary

```text
1. Công bố model, signal parameters, hybrid reward và budget.
2. Nature sinh Y,Z,X_A,X_B,X_C; cả ba Judge chỉ quan sát Z.
3. Mỗi Judge đồng thời chọn effort e_i(Z); peer không thấy lựa chọn này.
4. Judge H trả c_i và quan sát X_i; Judge L không thấy X_i.
5. Mỗi Judge đồng thời gửi report r_i và peer prediction p_i.
6. Khóa report; tính decision D bằng majority 2/3.
7. Sau khi report khóa, lấy A bằng randomness độc lập.
8. Nếu A=1, thủ tục kiểm chứng sinh/reveal T.
9. Tính hybrid reward; evaluator dùng Y để đo accuracy/loss riêng.
```

Ràng buộc bắt buộc:

- Strategy không nhận `A`, `T`, `Y`, `X` của peer hoặc report chưa khóa.
- Auditor/verification source không được đọc report để chọn `A` hoặc thay đổi distribution của `T`.
- RBTS scoring chỉ nhận report/prediction như V2.
- Anchor scoring chỉ nhận `A,T` sau bước 5; không truyền `Y` vào reward oracle.
- `D` không đọc `A` hoặc `T` trong V3.0.

Nếu audit được chọn có chủ đích sau khi nhìn report, hoặc `T` do chính Creator/Judge kiểm soát, đó là game khác và kết quả V3 không áp dụng.

## 7. Strategy space

V3 giữ nguyên reduced pure strategy của V2:

```text
effort_map: Z -> {L,H}
report_map: observation -> {0,1}
prediction_map: observation -> [0,1]
```

Tại mỗi nhánh `Z`, vẫn có sáu action:

| Action | Effort | Report khi `X_i=0` | Report khi `X_i=1` |
| --- | --- | --- | --- |
| `L0` | L | 0 | 0 |
| `L1` | L | 1 | 1 |
| `H00` | H | 0 | 0 |
| `H01` | H | 0 | 1 |
| `H10` | H | 1 | 0 |
| `H11` | H | 1 | 1 |

Judge không có action condition trên `A` hoặc `T` vì hai biến này chưa biết khi report. Vì vậy số effort/report profiles không đổi:

```text
216 branch candidates mỗi Z
46.656 full profiles qua cả hai Z
```

`p_i` vẫn là prediction về report của scoring peer, không phải prediction về `Y` hoặc `T`.

## 8. Hybrid scoring, utility và budget

### 8.1. Peer score

`PeerScore_i` giữ nguyên RBTS Eq. (8) của V2, gồm information score và prediction score, có miền:

```text
0 <= PeerScore_i <= 2
```

Reference/scoring-peer rotation, quadratic score, shadow report và peer-freeze giữ nguyên.

### 8.2. Anchor score

Với report nhị phân:

```text
Match(r_i,T) = 1 nếu r_i=T, ngược lại bằng 0
AnchorScore_i = A * Match(r_i,T)
```

Do đó:

```text
0 <= AnchorScore_i <= 1
E[AnchorScore_i | information, r_i]
  = q * P(T=r_i | information)
```

Anchor score không dùng majority decision và không dùng report của peer.

### 8.3. Reward và utility

```text
Reward_i = f
           + lambda_peer * PeerScore_i
           + mu_anchor * AnchorScore_i

Utility_i = Reward_i - c_i * 1[e_i=H]
```

`f` là hằng số trong game bắt buộc tham gia nên không đổi best response. V3.0 chưa mô hình hóa lựa chọn không tham gia.

### 8.4. Worst-case budget

Budget được kiểm tra theo worst case của một claim, không dùng expected audit rate để giảm reserve:

```text
total_reward <= 3*f + 6*lambda_peer + 3*mu_anchor <= B
```

`q` không xuất hiện trong cap vì khi audit xảy ra, cả ba Judge có thể nhận anchor score 1. Output phải tách:

- worst-case reward cap;
- expected peer reward;
- expected anchor reward;
- expected total reward thực chi.

Không chia lại một reward pool sau khi thấy report hoặc audit result; việc đó sẽ tạo payoff khác.

## 9. Candidate prediction và các trường hợp suy biến

Khi `lambda_peer > 0`, prediction tối ưu trên mỗi observation reachable vẫn là:

```text
p_i*(I_i) = P(r_k=1 | I_i, candidate peer strategies)
```

Anchor component không phụ thuộc `p_i`, nên không đổi nghiệm tối ưu prediction.

Khi `lambda_peer = 0`:

- prediction không ảnh hưởng utility;
- mọi `p_i ∈ [0,1]` hòa về utility;
- certificate phải ghi `prediction_optimum=any_in_unit_interval`;
- report và effort vẫn có thể được xác định bởi anchor reward.

Khi `q=0` hoặc `mu_anchor=0`, anchor không ảnh hưởng payoff. Với cùng signal config và `lambda_peer=lambda`, V3 phải quy hồi exact về V2 RBTS sau khi marginalize `A,T`.

Không được dùng Bayesian prediction representative để giả rằng prediction là duy nhất trong trường hợp `lambda_peer=0`.

## 10. Best response và incentive decomposition

Với focal Judge `i`, nhánh `z` và peer strategy cố định, best response phải tối ưu expected hybrid utility trên từng effort và mọi report map hợp lệ.

Đặt:

```text
W_L(i,z | sigma_-i)
  = max expected [lambda_peer*PeerScore + mu_anchor*AnchorScore] khi effort=L

W_H(i,z | sigma_-i)
  = max expected [lambda_peer*PeerScore + mu_anchor*AnchorScore] khi effort=H

Delta_i(z) = W_H - W_L - c_i
```

Phân loại:

```text
Delta_i(z) > 0  -> High Effort được ưu tiên
Delta_i(z) = 0  -> Low/High hòa
Delta_i(z) < 0  -> Low Effort được ưu tiên
```

Certificate phải tách cho mỗi action:

```text
expected_peer_score
expected_anchor_score
expected_peer_reward
expected_anchor_reward
effort_cost
total_utility
```

Khi focal deviation:

- giữ nguyên report/prediction tables của hai peer;
- giữ nguyên distribution của `A,T`;
- không cho peer cập nhật prediction theo effort mới của focal;
- tối ưu lại focal report và prediction theo observation mà effort thử cho phép.

Do report tối ưu có thể đổi khi `lambda_peer`, `mu_anchor` hoặc `q` đổi, V3 không dùng một công thức threshold một chiều làm kết luận toàn cục. Threshold cục bộ chỉ được xuất khi ghi đầy đủ strategy region đang giữ cố định; kết luận equilibrium phải dựa trên exhaustive search tại từng điểm.

## 11. Pure-equilibrium landscape

V3 giữ khái niệm cân bằng thuần của reduced normal-form representation từ V2. Candidate là cân bằng khi mọi Judge, ở cả `Z=0` và `Z=1`, không có deviation effort/report/prediction làm utility tăng.

Mỗi valid parameter point phải:

- kiểm tra đủ 216 branch candidates cho mỗi `Z`;
- giữ mọi tie;
- ghép hai tập branch equilibria bằng Cartesian product;
- xuất retained equilibrium IDs và best-response certificates;
- phân loại effort/report như V2.2.

Landscape tối thiểu phải công bố:

```text
branch/full equilibrium counts
all_low_exists
all_high_signal_dependent_exists
all_high_signal_ignored_exists
mixed_effort_exists
coexistence_low_and_high_informative
```

V3 thành công về mặt implementation kể cả khi không loại bỏ được Low Effort. Kết quả bất lợi phải được giữ làm evidence.

Existence của một high-information equilibrium không chứng minh hệ thống sẽ chọn equilibrium đó. Absence trong pure search không chứng minh absence của mixed equilibrium.

## 12. Decision, loss và accounting

Decision tiếp tục được khóa trước audit:

```text
D = 1[r_A+r_B+r_C >= 2]
```

Evaluator tiếp tục tính bằng `Y`:

- accuracy;
- false approval;
- false rejection;
- wrong payout probability/value;
- expected payout.

Accounting V3 thêm:

- audit occurrence probability;
- expected verification agreement `P(r_i=T)`;
- expected peer reward;
- expected anchor reward;
- expected total Judge reward;
- expected effort cost;
- operating cost;
- cash review cost.

Anchor xuất hiện sau `D`, nên nó không tự sửa một payout sai trong cùng case. Tác dụng được nghiên cứu là thay đổi incentive trước khi Judge chọn effort/report.

## 13. JSON config V3

Config chuẩn:

```json
{
  "model_version": "ceav-m1-v3.0",
  "pi": "1/2",
  "public_signal": {
    "sensitivity": "4/5",
    "specificity": "3/5"
  },
  "judges": {
    "A": {
      "private_signal": {"sensitivity": "9/10", "specificity": "4/5"},
      "high_effort_cost": "1/20"
    },
    "B": {
      "private_signal": {"sensitivity": "3/4", "specificity": "19/20"},
      "high_effort_cost": "1/10"
    },
    "C": {
      "private_signal": {"sensitivity": "13/20", "specificity": "7/10"},
      "high_effort_cost": "1/25"
    }
  },
  "verification_anchor": {
    "audit_probability": "1/5",
    "sensitivity": "9/10",
    "specificity": "9/10"
  },
  "f": "1/10",
  "lambda_peer": "1/2",
  "anchor_weight": "4/5",
  "reward_budget": "6",
  "payout_value": "1",
  "operating_cost": "0"
}
```

Các số trên minh họa schema, không phải V3 preset đã được chứng minh.

Validation bắt buộc:

- đúng ba Judge `A,B,C`, không thiếu/dư;
- mọi số là rational JSON string và canonicalize qua `Fraction`;
- không nhận đồng thời `lambda` V2 và `lambda_peer` V3;
- `0<pi<1`, signal parameters inherited đúng miền V2;
- `0<=q<=1`, `1/2<sens_T,spec_T<=1`;
- reward/cost/value không âm;
- thỏa worst-case budget;
- reject unknown fields trong config toán.

V2 config không được tự thêm anchor defaults rồi gắn nhãn V3. Conversion phải explicit và output model version mới.

## 14. Dataset và provenance

Dataset calibration V2.1 chỉ có thể cung cấp các trường inherited:

```text
pi, Z quality, X_A/X_B/X_C quality, cost_A/cost_B/cost_C
```

Nó không có dữ liệu để ước lượng:

```text
audit_probability, sens_T, spec_T, anchor_weight
```

V3.0 nhận các trường anchor từ assumption, pilot estimate hoặc historical estimate và phải pin provenance status. Synthetic fixture chỉ kiểm tra pipeline; không được gọi là bằng chứng về auditor thật.

Một dataset calibration anchor riêng là extension sau V3.0, không tự động nằm trong scope implementation đầu tiên.

## 15. Sweep và comparison bắt buộc

Sweep V3 tối thiểu hỗ trợ:

```text
lambda_peer
anchor_weight
audit_probability
verification_anchor.sensitivity
verification_anchor.specificity
judges.*.high_effort_cost
```

Mỗi điểm phải giữ nguyên full config, exact fractions, semantic hash, validation status, candidate diagnostics và exhaustive pure-equilibrium landscape.

Điểm vi phạm budget được giữ với `status=invalid_budget` và không chạy search.

Comparison V2/V3 hợp lệ yêu cầu:

- cùng inherited signal config;
- cùng Judge costs;
- cùng candidate profile hoặc cùng rule chọn profile đã khai báo;
- cùng worst-case budget `B`;
- tách actual expected spend khỏi cap;
- ghi rõ model/scoring khác nhau.

Không gọi một comparison là causal evidence ngoài miền parameter đã tính.

## 16. CLI, API, artifacts và HTML mục tiêu

Các interface dưới đây là **mục tiêu chưa triển khai**.

CLI dự kiến:

```text
python -m ceav_m1 analyze --config PATH --profile PATH --mechanism hybrid_anchor --out PATH
python -m ceav_m1 equilibria --config PATH --mechanism hybrid_anchor --out PATH
python -m ceav_m1 sweep --config PATH --profile PATH --mechanism hybrid_anchor --out PATH
```

Mỗi run V3 phải pin:

```text
CEAV_M1_V3_ANCHOR_SPEC.md
ENGINE_DESIGN_V3_ANCHOR.md
VERIFICATION_PLAN_V3_ANCHOR.md
freeze_event.json
config/profile/scenario
source bytes thực tế
```

Artifacts tối thiểu:

```text
states.json
summary.json
best_responses.json
equilibria.json khi search
accounting.json
manifest.json
report.md
```

HTML mục tiêu phải hiển thị:

- flow `report locked -> random audit -> T -> reward settlement`;
- input `q,sens_T,spec_T,lambda_peer,mu_anchor`;
- peer reward, anchor reward, cost và utility tách riêng;
- landscape Low/High, không chỉ candidate verdict;
- comparison V2/V3 dưới cùng cap;
- cảnh báo provenance của anchor.

Frontend không tự tính payoff; CLI, API, worker và UI phải gọi cùng engine interface.

## 17. Tuyên bố khoa học được phép

Một V3 run đã verified chỉ được kết luận trong config/sweep/source đã pin rằng:

- anchor làm tăng/giảm net incentive của từng `Judge × Z` bao nhiêu;
- High signal-dependent equilibrium có hoặc không tồn tại trong pure search;
- Low Effort equilibrium có hoặc không còn trong pure search;
- reward allocation nào thỏa hoặc vượt budget;
- accuracy, false approval/rejection và expected spend thay đổi thế nào tại các equilibrium/candidate được nêu rõ.

Không được kết luận:

- anchor ngoài đời đáng tin nếu chưa có dữ liệu provenance;
- cơ chế chống collusion/Sybil;
- pure equilibrium sẽ được chọn trong production;
- audit reward tự sửa payout sai;
- V3 tốt hơn trên mọi prior, signal quality hoặc cost;
- source code/spec tương đương deployment blockchain.

Nguồn Gao, Wright và Leyton-Brown về peer prediction với limited access to ground truth được dùng để định vị hướng spot-check/trusted report; V3 không kế thừa theorem của họ vì game, population, signals và payoff ở đây khác. RBTS component tiếp tục đối chiếu Witkowski–Parkes. Xem [references/PRIMARY_SOURCES.md](references/PRIMARY_SOURCES.md).

## 18. Rủi ro và trade-offs phải giữ trong output

- **Anchor manipulation:** nếu bên phát `T` bị Creator/Judge kiểm soát, incentive có thể lệch theo bên đó.
- **Anchor error:** specificity/sensitivity thấp có thể thưởng report sai so với `Y`.
- **Delay:** anchor reward chỉ settle sau verification; V3 chưa thiết kế cash-flow production.
- **Budget concentration:** audit hiếm không làm giảm worst-case reserve cho case được audit.
- **External payoff:** bribe, stake hoặc lợi ích từ payout không nằm trong utility hiện tại.
- **Equilibrium selection:** high equilibrium có thể cùng tồn tại với low equilibrium.
- **Decision timing:** `D` xảy ra trước `T`; current-case wrong payout không được undo.

Các rủi ro này không được ẩn bằng cách chỉ báo cáo accuracy tốt nhất.

## 19. Acceptance gates V3

| Gate | Bằng chứng bắt buộc | Chưa được tuyên bố |
| --- | --- | --- |
| `V3-GATE-0` | Spec, engine design, verification plan và independent oracle/fixtures được pin trong freeze thật | Chưa có engine đúng |
| `V3-GATE-1` | Parser/distribution exact; 128 potential rows; endpoint support; V2 reduction khi `q=0` hoặc `mu=0` | Chưa chứng nhận best response |
| `V3-GATE-2` | Candidate accounting và best response đủ `3 Judge × 2 Z`; independent oracle; peer freeze | Chưa tìm hết pure profiles |
| `V3-GATE-3` | Exhaustive branch/full search, ties và set equality trên fixtures | Chỉ coverage pure game đã định nghĩa |
| `V3-GATE-4` | CLI/artifacts/sweep/V2 comparison/hashes/no-overwrite | Chưa browser accepted |
| `V3-GATE-5` | API/UI/history/browser/mutations và toàn bộ V1/V2/V2.1/V2.2 regression trên current source | Hoàn thành local V3; chưa production |

Test IDs, oracle derivations, fixtures, browser scenarios và mutation probes phải được chốt trong `VERIFICATION_PLAN_V3_ANCHOR.md` trước implementation-start. Không tái sử dụng test ID cũ với nghĩa mới.

Mutation plan tối thiểu phải phát hiện:

- reveal `T` hoặc `A` cho strategy trước report;
- dùng `Y` thay `T` trong anchor score;
- áp anchor reward khi `A=0`;
- dùng expected cap có `q` thay worst-case budget;
- cho audit selection phụ thuộc report;
- bỏ effort cost;
- cập nhật peer prediction khi focal deviation;
- làm sai V2 reduction;
- UI tự tính khác engine.

## 20. Trình tự triển khai

1. Review và chốt spec này.
2. Viết `ENGINE_DESIGN_V3_ANCHOR.md` với records, observation boundary, scorer separation và solver contract.
3. Viết `VERIFICATION_PLAN_V3_ANCHOR.md` với oracle độc lập, V3 test IDs, fixtures, browser và mutations.
4. Tạo freeze event V3 từ raw bytes/hash thực tế của ba tài liệu và fixtures có trước analyzer.
5. Xây parser/distribution cùng exact V2 reduction.
6. Nối candidate evaluation và best response.
7. Nối exhaustive equilibrium search, artifacts, CLI và comparison.
8. Nối API/UI/history.
9. Chạy V3 gates cùng toàn bộ regression cũ.
10. Chỉ đổi trạng thái thành `VERIFIED` khi đủ evidence.

Không tạo freeze lùi thời gian hoặc coi file spec này là implementation-start event.

## 21. Trạng thái bàn giao của revision này

| Hạng mục | SPECIFIED | IMPLEMENTED | VERIFIED |
| --- | --- | --- | --- |
| Distribution `A,T` | Có | Chưa | Chưa |
| Hybrid payoff và budget | Có | Chưa | Chưa |
| Strategy/timing/information boundary | Có | Chưa | Chưa |
| Best response và equilibrium semantics | Có | Chưa | Chưa |
| Schema V3 | Có | Chưa | Chưa |
| Engine design V3 | Chưa | Chưa | Chưa |
| Verification plan/oracle V3 | Chưa | Chưa | Chưa |
| CLI/API/UI V3 | Mục tiêu | Chưa | Chưa |
| Freeze implementation-start V3 | Chưa | Chưa | Chưa |

Revision `verification-anchor-r1` chốt quyết định trung tâm: **anchor là tín hiệu kiểm chứng độc lập xuất hiện sau report và chỉ tham gia reward; ground truth `Y` vẫn không được đưa cho Judge hoặc dùng trực tiếp làm reward oracle.**
