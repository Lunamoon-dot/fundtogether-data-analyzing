# CEAV-M1 V2 — Đặc tả tín hiệu bất đối xứng theo từng Judge

**Model version:** `ceav-m1-v2.0`

**Spec revision:** `signal-heterogeneity-r1`

**Ngày:** 22/10/2026

**Trạng thái hiện tại:** `SPECIFIED`, `IMPLEMENTED`, `VERIFIED` local theo V2-GATE-0–V2-GATE-5. Freeze implementation-start và evidence nằm tại các đường dẫn ở §15.

**Workspace:** `C:\Users\dell\Desktop\fundtogether_data_analyzing`

## 1. Vai trò của tài liệu

Tài liệu này định nghĩa Version 2 của CEAV-M1. V2 thay mô hình sinh tín hiệu đối xứng của V1 bằng:

- sensitivity và specificity riêng cho tín hiệu chung `Z`;
- sensitivity và specificity riêng cho tín hiệu riêng của từng Judge A, B, C;
- metadata kịch bản để giải thích `Y`, `Z`, `X_i` và nguồn của các tham số.

Các phần còn lại của game giữ nguyên từ [CEAV_M1_SPEC.md](CEAV_M1_SPEC.md): ba Judge, timing, hai mức effort, sáu action tại mỗi nhánh `Z`, fixed reward, RBTS scoring, majority decision, exact rational arithmetic, best response với peer cố định và tìm cân bằng thuần.

Khi triển khai `ceav-m1-v2.0`, tài liệu này là nguồn chuẩn cho phân phối tín hiệu, schema V2, tương thích V1 và yêu cầu V2. [CEAV_M1_SPEC.md](CEAV_M1_SPEC.md) tiếp tục là nguồn chuẩn cho các phần được tuyên bố kế thừa. Nếu hai tài liệu mâu thuẫn ngoài phạm vi thay đổi được liệt kê tại đây, phải ghi nhận mâu thuẫn và giải quyết trước khi công bố kết quả V2.

Tài liệu này không sửa lịch sử hay evidence của `ceav-m1-v1.0`. Git tag `v1.0.0` và các snapshot V1 là bất biến.

## 2. Vấn đề V2 cần giải quyết

V1 dùng một tham số `a` cho độ chính xác đối xứng của `Z` và một tham số `b` cho độ chính xác đối xứng của cả ba `X_i`. Vì thế V1 không phân biệt được:

- tín hiệu dễ nhận ra claim thật nhưng dễ bị claim giả tạo ra;
- tín hiệu giỏi bác claim giả nhưng đôi khi bác nhầm claim thật;
- Judge A điều tra tốt hơn Judge B hoặc C;
- cùng một chi phí nhưng chất lượng kiểm tra khác nhau;
- thay đổi riêng chất lượng của một Judge tác động thế nào đến incentive và decision.

V2 phải trả lời các câu hỏi đó mà không đồng thời thay scoring, strategy space hoặc aggregation. Giữ các phần này cố định giúp so sánh V1/V2 có ý nghĩa: khác biệt kết quả đến từ mô hình tín hiệu đã khai báo, không phải từ một game hoàn toàn khác.

## 3. Phạm vi đã chốt

### 3.1. Có trong V2.0

- Một claim nhị phân `Y`; ba Judge cố định A, B, C.
- Một tín hiệu chung miễn phí `Z`.
- Một tín hiệu riêng tiềm năng `X_i` cho mỗi Judge.
- Sensitivity và specificity riêng cho `Z`.
- Sensitivity và specificity riêng cho `X_A`, `X_B`, `X_C`.
- Chi phí High Effort riêng cho từng Judge.
- Độc lập có điều kiện của `Z, X_A, X_B, X_C` khi đã biết `Y`.
- Cùng timing, scoring, utility, decision, metrics và pure-strategy search của V1.
- Đọc được config V1 bằng đúng semantics V1 và config V2 bằng đúng semantics V2.
- Scenario metadata tùy chọn, được pin riêng với run nhưng không tham gia phép tính.
- Giao diện giải thích false-positive, false-negative và prior-weighted signal accuracy.
- Regression đầy đủ để V1 tiếp tục tái lập được.

### 3.2. Không thuộc V2.0

- Correlation giữa các tín hiệu sau khi đã điều kiện theo `Y`.
- Số Judge động hoặc majority khác 2/3.
- Tín hiệu nhiều hơn hai giá trị, confidence score hoặc evidence liên tục.
- Raw PDF, ảnh, video, hóa đơn hoặc API bên ngoài làm input trực tiếp cho engine.
- Ước lượng sensitivity/specificity tự động từ dữ liệu thực.
- Xác lập ground truth ngoài đời hoặc reward dựa trên ground truth.
- Mixed equilibrium, correlated equilibrium, coalition-proof equilibrium hoặc equilibrium selection.
- Stake, slashing, non-reveal, appeal, blockchain, ví, database hoặc deployment production.

Correlation chỉ được xem xét ở một model version sau. Nếu cần, nó phải được định nghĩa bằng joint distribution hợp lệ như `P(X_A,X_B,X_C | Y)`, không thêm một hệ số `rho` mơ hồ.

## 4. Ký hiệu và ý nghĩa

| Ký hiệu | Ý nghĩa | Miền V2.0 |
| --- | --- | --- |
| `Y` | Claim thực sự đạt | `{0,1}`; `1 = đạt` |
| `pi` | Prior `P(Y=1)` | `0 < pi < 1` |
| `Z` | Tín hiệu chung miễn phí | `{0,1}` |
| `sens_Z` | `P(Z=1 | Y=1)` | `0 < sens_Z < 1` |
| `spec_Z` | `P(Z=0 | Y=0)` | `0 < spec_Z < 1` |
| `X_i` | Tín hiệu riêng tiềm năng của Judge i | `{0,1}` |
| `sens_i` | `P(X_i=1 | Y=1)` | `0 < sens_i < 1` |
| `spec_i` | `P(X_i=0 | Y=0)` | `0 < spec_i < 1` |
| `e_i` | Effort của Judge i | `L` hoặc `H` |
| `c_i` | Chi phí khi Judge i chọn H | `c_i >= 0` |
| `r_i` | Report của Judge i | `{0,1}` |
| `p_i` | Dự đoán xác suất scoring peer báo 1 | `[0,1]` |
| `f` | Thưởng nền của RBTS | `f >= 0` |
| `lambda` | Hệ số chuyển score thành reward | `lambda >= 0` |
| `F` | Fixed reward mỗi Judge | `F >= 0` |
| `B` | Trần tổng reward cho một claim | `B >= 0` |
| `V` | Payout value dùng để đo loss | `V >= 0` |
| `operating_cost` | Chi phí vận hành ngoài reward | `>= 0` |

Sensitivity đo khả năng tín hiệu báo `1` khi claim thật sự đạt. Specificity đo khả năng tín hiệu báo `0` khi claim thật sự không đạt. Hai đại lượng liên quan trực tiếp là:

```text
false_negative_rate = 1 - sensitivity
false_positive_rate = 1 - specificity
```

Không bắt buộc sensitivity hoặc specificity lớn hơn `1/2`. Giá trị dưới `1/2` mô tả một kênh có xu hướng sai theo phía tương ứng và vẫn là input toán hợp lệ. Giá trị đúng `0` hoặc `1` chưa thuộc V2.0 để mọi trạng thái vẫn có xác suất dương.

## 5. Phân phối sinh dữ liệu

### 5.1. Likelihood của một tín hiệu nhị phân

Với tín hiệu `S`, sensitivity `u` và specificity `v`, định nghĩa:

```text
K(s | y; u, v) =
    u       nếu y=1 và s=1
    1-u     nếu y=1 và s=0
    v       nếu y=0 và s=0
    1-v     nếu y=0 và s=1
```

Khi `u=v=t`, hàm này trở thành likelihood lỗi đối xứng của V1:

```text
K(s | y; t, t) = t nếu s=y, ngược lại bằng 1-t.
```

### 5.2. State space

Nature sinh:

```text
Y ~ Bernoulli(pi)
P(Z=z | Y=y)   = K(z | y; sens_Z, spec_Z)
P(X_i=x | Y=y) = K(x | y; sens_i, spec_i)
```

V2.0 giữ giả định:

```text
Z, X_A, X_B, X_C độc lập có điều kiện theo Y.
```

`Z` vẫn là **một giá trị chung duy nhất** mà cả ba Judge cùng thấy, không phải ba bản sao `Z_A,Z_B,Z_C`. Độc lập có điều kiện ở đây chỉ mô tả cách Nature sinh các primitive signals khi đã biết `Y`; nó không nói report của các Judge độc lập. Report vẫn có thể tương quan mạnh vì cùng thấy `Z`, cùng biết model và dùng các strategy giống nhau.

Với `w=(y,z,x_A,x_B,x_C)`, vẫn có đúng 32 trạng thái:

```text
P(w) = pi^y * (1-pi)^(1-y)
       * K(z   | y; sens_Z, spec_Z)
       * K(x_A | y; sens_A, spec_A)
       * K(x_B | y; sens_B, spec_B)
       * K(x_C | y; sens_C, spec_C)
```

Engine phải dùng `Fraction` cho toàn bộ phép nhân, cộng, điều kiện hóa và so sánh. Với input hợp lệ, phải kiểm tra đúng 32 row, mọi mass dương và tổng mass đúng bằng 1.

### 5.3. Potential signals và effort

`X_A`, `X_B`, `X_C` được sinh tiềm năng trong state space dù Judge có thể chọn L. Điều này chỉ cho phép so sánh các strategy trên cùng một phân phối.

- Judge chọn L chỉ quan sát `Z`.
- Judge chọn H trả `c_i` và quan sát `(Z,X_i)`.
- Effort không làm thay đổi `Y`, `Z` hoặc giá trị tiềm năng của `X_i`.
- Strategy không được đọc `Y`, `X` của peer hoặc toàn state object.

### 5.4. Ground truth và dữ liệu ngoài đời

Trong một run mô phỏng, engine/evaluator biết biến ẩn `Y` để sinh phân phối và đo loss. Judge không biết `Y` khi hành động.

V2 không tạo ra ground truth ngoài đời. Khi sử dụng một scenario thực, người nghiên cứu phải định nghĩa trước điều kiện nào tương ứng `Y=1`, ground truth được xác nhận khi nào và các tham số tín hiệu đến từ giả định, pilot hay dữ liệu lịch sử. Những thông tin này nằm trong scenario metadata, không được giả làm một phần của scoring.

## 6. Timing và information boundary

V2 kế thừa timing của V1:

```text
1. Công bố model, tham số tín hiệu, reward và budget.
2. Nature sinh (Y,Z,X_A,X_B,X_C); cả ba Judge quan sát Z.
3. Mỗi Judge đồng thời chọn effort e_i(Z); peer không thấy lựa chọn này.
4. Judge H trả c_i và quan sát X_i; Judge L không thấy X_i.
5. Mỗi Judge đồng thời gửi report r_i và prediction p_i.
6. Tính score/reward; evaluator tính decision/loss riêng bằng Y.
```

Effort tiếp tục được chọn sau khi thấy `Z`. Best response và equilibrium phải kiểm tra riêng từng Judge tại `Z=0` và `Z=1` có xác suất dương. Một lợi ích H trung bình ex ante dương không đủ chứng nhận strategy chọn H ở cả hai nhánh.

Sensitivity, specificity, prior, cost và reward parameters là common knowledge trong game được phân tích. Đây là giả định mô hình, không phải tuyên bố rằng Judge ngoài đời biết chính xác các xác suất đó.

## 7. Phần kế thừa nguyên nghĩa từ V1

### 7.1. Strategy space

V2 giữ sáu action cho từng Judge tại mỗi nhánh `Z`:

| Action | Effort | Report khi `X_i=0` | Report khi `X_i=1` |
| --- | --- | --- | --- |
| `L0` | L | 0, không đọc `X_i` | 0, không đọc `X_i` |
| `L1` | L | 1, không đọc `X_i` | 1, không đọc `X_i` |
| `H00` | H | 0 | 0 |
| `H01` | H | 0 | 1 |
| `H10` | H | 1 | 0 |
| `H11` | H | 1 | 1 |

Mỗi Judge vẫn có `6*6=36` behavior maps qua hai giá trị `Z`; toàn game có `36^3=46.656` full pure profiles. Từng nhánh có `6^3=216` branch candidates.

### 7.2. Scoring và utility

Fixed reward và RBTS giữ nguyên công thức tại V1 §6. Reference/scoring-peer rotation `[A,B,C]`, quadratic score, shadow report, budget cap và xử lý `lambda=0` không đổi.

Thay đổi phân phối tín hiệu có thể làm posterior, candidate prediction, expected score, utility, best response và equilibrium thay đổi. Điều đó không tạo ra một scoring formula mới.

Candidate prediction phải được dựng từ phân phối đúng model version. Khi kiểm tra focal deviation, toàn bộ report/prediction tables của peer vẫn được đóng băng.

### 7.3. Decision và loss

Decision vẫn là majority 2/3:

```text
D = 1[r_A + r_B + r_C >= 2]
```

Các metric V1 tiếp tục giữ nguyên: `accuracy`, `false_approval_rate`, `false_rejection_rate`, `wrong_payout_probability`, `wrong_payout_value`, `expected_payout`, reward, effort cost, Judge utility, operating cost và cash review cost.

Scoring không được đọc `D` hoặc `Y`. Payout value `V` chỉ dùng đo loss, không tham gia utility của Judge.

### 7.4. Phạm vi chứng nhận

Một certificate V2 chỉ chứng nhận best response hoặc pure equilibrium trong game V2 với config, profile, mechanism và source revision đã pin. Nó không chứng nhận:

- model tín hiệu khớp thế giới thực;
- tham số đã được ước lượng đúng;
- equilibrium nào sẽ được chọn;
- chống collusion, Sybil hoặc coalition;
- mixed equilibrium hoặc production safety.

## 8. JSON config V2

### 8.1. Schema chuẩn

Một config V2 có dạng:

```json
{
  "model_version": "ceav-m1-v2.0",
  "pi": "1/2",
  "public_signal": {
    "sensitivity": "4/5",
    "specificity": "3/5"
  },
  "judges": {
    "A": {
      "private_signal": {
        "sensitivity": "9/10",
        "specificity": "4/5"
      },
      "high_effort_cost": "1/20"
    },
    "B": {
      "private_signal": {
        "sensitivity": "3/4",
        "specificity": "19/20"
      },
      "high_effort_cost": "1/10"
    },
    "C": {
      "private_signal": {
        "sensitivity": "13/20",
        "specificity": "7/10"
      },
      "high_effort_cost": "1/25"
    }
  },
  "f": "1/10",
  "lambda": "3/4",
  "fixed_reward": "8/5",
  "reward_budget": "6",
  "payout_value": "1",
  "operating_cost": "0"
}
```

### 8.2. Validation

- Mọi số phải là chuỗi thập phân hoặc `numerator/denominator`, parse trực tiếp bằng `Fraction`.
- `pi`, mọi sensitivity và mọi specificity phải thuộc khoảng mở `(0,1)`.
- `high_effort_cost`, `f`, `lambda`, `fixed_reward`, `reward_budget`, `payout_value` và `operating_cost` không được âm.
- `judges` phải có đúng ba key `A`, `B`, `C`.
- Mỗi Judge phải có đúng `private_signal` và `high_effort_cost`.
- Object tín hiệu phải có đúng `sensitivity` và `specificity`.
- `operating_cost` có thể vắng và mặc định bằng `"0"`; các field khác bắt buộc.
- Field không biết phải bị từ chối để phát hiện typo.
- Budget validation giữ nguyên V1: RBTS cần `3*f + 6*lambda <= reward_budget`; fixed cần `3*fixed_reward <= reward_budget`.
- Config V2 chứa field V1 `a`, `b` hoặc `costs` phải bị từ chối; không tự diễn giải mixed schema.

Tên Judge nằm trong schema để tránh lệch vị trí giữa signal quality và cost. Canonical serialization phải dùng thứ tự Judge `A,B,C`, chuẩn hóa mọi phân số và không phụ thuộc thứ tự key của JSON input.

### 8.3. Profile

Profile JSON không đổi:

```json
{
  "0": ["H01", "H01", "H01"],
  "1": ["H01", "H01", "H01"]
}
```

Thứ tự trong mỗi mảng tiếp tục là `[A,B,C]`. Prediction Bayesian được dựng từ profile và phân phối của model version tương ứng.

## 9. Tương thích và quy hồi về V1

### 9.1. Ánh xạ chính xác

Một config V1 có tham số `a`, `b`, `costs=[c_A,c_B,c_C]` tương đương toán với config V2 khi:

```text
sens_Z = spec_Z = a

sens_A = spec_A = b
sens_B = spec_B = b
sens_C = spec_C = b

high_effort_cost_A = c_A
high_effort_cost_B = c_B
high_effort_cost_C = c_C
```

Các tham số còn lại giữ nguyên.

### 9.2. Yêu cầu runtime đa phiên bản

Runtime V2 phải dispatch bằng `model_version`:

- `ceav-m1-v1.0`: parse schema V1 và dùng phân phối lỗi đối xứng V1.
- `ceav-m1-v2.0`: parse schema V2 và dùng phân phối bất đối xứng theo Judge.
- Version khác: trả lỗi có cấu trúc trước khi tạo run.

Không tự nâng V1 config thành V2 và không ghi đè `model_version` người dùng gửi. Nếu cung cấp chức năng chuyển đổi, nó phải xuất một file mới để người dùng kiểm tra, giữ file nguồn và ghi mapping đã áp dụng.

### 9.3. Regression bắt buộc

Với mapping tại §9.1, hai model phải có:

- cùng 32 state values và exact probability cho từng state;
- cùng candidate predictions;
- cùng state-level scores, rewards và utilities;
- cùng metrics và best-response values;
- cùng equilibrium set trong phạm vi pure strategies.

Manifest, model version, config schema và config hash được phép khác. Test quy hồi phải so payload toán sau khi loại metadata được định nghĩa là version-specific; không được yêu cầu hai artifact toàn phần có cùng bytes.

Tất cả V1 tests và evidence release cũ vẫn phải tái lập từ source/tag phù hợp. Việc V2 pass không thay thế V1 regression.

## 10. Scenario metadata

### 10.1. Mục đích

Config định nghĩa game bằng số. Scenario metadata giải thích các số đó đại diện cho tình huống nào. Hai lớp phải tách nhau:

```text
config.json    -> tham gia phép tính -> config_hash
scenario.json  -> ngữ cảnh/provenance -> scenario_hash
```

Một config có thể chạy không kèm scenario. Khi đó report phải ghi `scenario: not_provided`, không tự suy diễn nguồn dữ liệu.

### 10.2. Schema metadata tối thiểu

```json
{
  "scenario_version": "ceav-scenario-v1",
  "scenario_id": "sample-campaign-01",
  "claim": {
    "text": "Milestone có đạt tiêu chí nghiệm thu hay không",
    "y_equals_1_when": "Tất cả tiêu chí nghiệm thu bắt buộc được đáp ứng",
    "truth_resolution": "Đánh giá hậu nghiệm độc lập sau quyết định"
  },
  "public_signal": {
    "meaning_of_1": "Tài liệu công khai có vẻ ủng hộ claim",
    "source": "Bộ tài liệu do Creator công bố"
  },
  "judges": {
    "A": {"private_check": "Đối chiếu hóa đơn và nhà cung cấp"},
    "B": {"private_check": "Kiểm tra sản phẩm thực tế"},
    "C": {"private_check": "Đối chiếu tiến độ và hồ sơ nghiệm thu"}
  },
  "parameter_provenance": {
    "status": "assumption",
    "notes": "Thông số phục vụ thí nghiệm; chưa hiệu chuẩn bằng dữ liệu thực"
  }
}
```

Scenario metadata không được chứa instruction làm thay đổi engine, không được cấp cho Judge thông tin ngoài timing và không được dùng làm evidence rằng tham số đã đúng. Raw evidence nhạy cảm hoặc dung lượng lớn nằm ngoài artifact V2.0.

### 10.3. Controlled comparison

Một comparison được gắn nhãn cùng scenario chỉ khi `scenario_hash` giống nhau hoặc cả hai đều không có scenario. Khác scenario vẫn có thể đặt cạnh nhau để quan sát, nhưng UI/report phải ghi đây không phải controlled comparison.

So sánh V1 với V2 chỉ được gọi là **reduction check** khi config thỏa mapping §9.1. Các so sánh cross-version khác phải hiển thị rõ model khác nhau.

## 11. Output và diễn giải

### 11.1. Signal diagnostics

Ngoài output V1, V2 phải xuất exact và decimal cho:

```text
public_false_negative_rate = 1 - sens_Z
public_false_positive_rate = 1 - spec_Z
public_signal_accuracy = pi*sens_Z + (1-pi)*spec_Z

private_false_negative_rate_i = 1 - sens_i
private_false_positive_rate_i = 1 - spec_i
private_signal_accuracy_i = pi*sens_i + (1-pi)*spec_i
```

`signal_accuracy` là prior-weighted descriptive diagnostic. Nó không phải decision accuracy, score, utility hoặc bằng chứng Judge sẽ chọn H.

### 11.2. Manifest và hashes

Manifest V2 phải pin:

- model version thực tế của config;
- spec revision và V2 freeze status;
- engine/source revision;
- canonical config và `config_hash`;
- profile và `profile_hash` khi có;
- scenario snapshot và `scenario_hash` khi có;
- mechanism, arithmetic mode, command, scope và run status;
- V2 engine design và verification plan thực tế dùng khi implementation bắt đầu.

Output không được lấy model version từ một hằng toàn cục nếu run đang replay V1. Hash đúng chỉ chứng minh identity của bytes/canonical data, không chứng minh mô hình hoặc thuật toán đúng.

### 11.3. Báo cáo

Report phải tách bốn lớp:

1. **Input assumption:** prior và chất lượng từng tín hiệu.
2. **Behavior/incentive:** effort, utility, regret và equilibrium.
3. **Decision outcome:** accuracy, false approval/rejection và wrong payout.
4. **Provenance:** scenario, model/spec/source và trạng thái kiểm chứng.

Không được viết “Judge A chính xác 90%” chỉ từ `sens_A=0.9`; đó mới là tỷ lệ nhận ra claim thật. Muốn nói prior-weighted accuracy phải dùng cả sensitivity, specificity và `pi`.

Không được suy từ signal quality cao ra decision accuracy cao: Judge có thể chọn L, báo khác tín hiệu, hoặc game có equilibrium chất lượng thấp.

## 12. CLI, API, sweep và HTML

### 12.1. CLI/API

Các operation `analyze`, `equilibria`, `sweep`, `compare`, `tests` và `serve` giữ vai trò V1. Config quyết định adapter V1/V2. CLI, API và HTML phải gọi cùng engine và validation path.

API status phải công bố:

- `supported_model_versions`;
- model mặc định của form mới;
- suite/gate nào sẵn sàng cho từng version;
- V2 freeze status thực tế.

Trước khi V2 được implement, API/UI hiện tại vẫn chỉ được công bố hỗ trợ `ceav-m1-v1.0`.

### 12.2. Sweep

V2 sweep phải hỗ trợ tối thiểu các axis path riêng:

```text
pi
public_signal.sensitivity
public_signal.specificity
judges.A.private_signal.sensitivity
judges.A.private_signal.specificity
judges.A.high_effort_cost
judges.B.private_signal.sensitivity
judges.B.private_signal.specificity
judges.B.high_effort_cost
judges.C.private_signal.sensitivity
judges.C.private_signal.specificity
judges.C.high_effort_cost
lambda
```

Mỗi axis dùng chuỗi hữu tỉ. Thứ tự canonical, tích Descartes, giữ hàng invalid và replay từng điểm tiếp tục theo contract V1. Shorthand đặt cùng giá trị cho ba Judge có thể được thêm sau nhưng không phải acceptance V2.0.

### 12.3. Giao diện

Form V2 phải chia rõ:

1. Prior và tín hiệu chung.
2. Tín hiệu riêng cùng chi phí của A, B, C.
3. Reward, budget, payout và operating cost.

Mỗi sensitivity/specificity phải hiển thị mô tả điều kiện đầy đủ, ví dụ `P(Z=1 | Y=1)`, cùng false-positive/false-negative tương ứng. Không chỉ ghi một nhãn ngắn như “độ chính xác”.

UI phải:

- chọn rõ V1 hoặc V2;
- đổi form theo version mà không làm mất draft chưa lưu của version kia;
- import/export round-trip đúng schema;
- từ chối mixed schema tại đúng field;
- hiển thị signal diagnostics trước khi chạy hoặc trong phần kiểm tra input;
- ghi model version trên mọi result/history/comparison;
- cảnh báo khi so run khác model, config, profile hoặc scenario;
- giữ đầy đủ browser acceptance desktop/mobile và keyboard của V1.

## 13. Verification bắt buộc trước khi gọi V2 hoàn thành

### 13.1. Oracle và fixtures

Trước production analyzer V2 phải có derivation/fixture độc lập cho:

- một config đối xứng quy hồi đúng G1 V1;
- một config public sensitivity khác specificity;
- một config ba Judge có signal quality và cost khác nhau;
- một config có sensitivity hoặc specificity dưới `1/2`;
- invalid schemas: thiếu Judge, dư Judge, mixed V1/V2, sai miền và sai budget.

Expected không được sinh bằng chính state generator hoặc evaluator đang test.

### 13.2. Invariants

- 32 states, mass dương, tổng đúng 1.
- Đổi riêng tham số A chỉ đổi factor của `X_A`, không âm thầm đổi B/C.
- Đổi sensitivity chỉ tác động likelihood tại `Y=1`; đổi specificity chỉ tác động likelihood tại `Y=0`.
- Hoán đổi toàn bộ parameters/costs/strategy labels của hai Judge cho kết quả hoán đổi tương ứng.
- V1 reduction §9 cho exact mathematical equality.
- Observation boundary, peer freeze, ties, six actions và exact arithmetic tiếp tục đúng.
- Cache on/off và thứ tự enumeration không đổi result/certificate set.

### 13.3. Mutation probes tối thiểu

V2 verification plan phải có probe phát hiện ít nhất:

- dùng sensitivity thay specificity khi `Y=0`;
- dùng specificity thay sensitivity khi `Y=1`;
- dùng parameters của A cho cả ba Judge;
- đảo A/B do dựa vào JSON key order;
- tự lấp specificity bằng sensitivity khi field bị thiếu;
- bỏ model version khỏi config hash/dispatch;
- tính signal accuracy bằng trung bình đơn giản thay vì trọng số `pi`;
- dùng scenario metadata để thay đổi phép tính;
- V2 pass nhưng làm hỏng V1 regression.

### 13.4. Gates V2

| Gate | Bằng chứng bắt buộc | Chưa được tuyên bố |
| --- | --- | --- |
| `V2-GATE-0` | Spec, engine design, verification plan được pin; freeze event V2 thật | Chưa có engine đúng |
| `V2-GATE-1` | Parser/state generator V1+V2; oracle và reduction fixtures | Chưa chứng nhận best response |
| `V2-GATE-2` | Analyze/best response/certificates trên heterogeneous configs | Chưa tìm hết pure profiles |
| `V2-GATE-3` | Exhaustive branch/full-profile equality với oracle; benchmark | Chỉ coverage lớp pure đã định nghĩa |
| `V2-GATE-4` | CLI/artifacts/sweep/compare/hashes/scenario pin | Chưa browser accepted |
| `V2-GATE-5` | API/UI/history/test runner/browser/mutations và toàn bộ V1 regression | Hoàn thành local V2; chưa production |

Test IDs, fixture IDs, browser scenarios và exact commands phải được chốt trong `VERIFICATION_PLAN_V2.md` trước V2 implementation-start. Không tái sử dụng T01–T32 với nghĩa mới; dùng namespace V2 riêng.

## 14. Trình tự triển khai

1. Review và chốt spec này.
2. Viết `ENGINE_DESIGN_V2.md` với seam phân phối tín hiệu, records, canonicalization và adapter V1/V2.
3. Viết `VERIFICATION_PLAN_V2.md` với oracle, fixtures, V2 test IDs, browser scenarios và mutation probes.
4. Tạo freeze event V2, lưu raw bytes/hash của cả ba tài liệu và parent revision thực tế.
5. Xây parser/state generator và làm V1 reduction pass.
6. Nối evaluator, best response, equilibrium, artifacts và CLI.
7. Nối API/UI/history và scenario metadata.
8. Chạy V2 gates cùng toàn bộ V1 regression.
9. Chỉ sau khi đủ evidence mới đổi trạng thái thành `VERIFIED` và tạo tag `v2.0.0`.

Mỗi bước phải báo đúng `SPECIFIED`, `IMPLEMENTED` hoặc `VERIFIED`. Một file spec, UI mockup hoặc config mẫu không chứng minh engine V2 tồn tại.

## 15. Trạng thái bàn giao của revision này

| Hạng mục | SPECIFIED | IMPLEMENTED | VERIFIED |
| --- | --- | --- | --- |
| Phân phối sensitivity/specificity theo Judge | Có | Có | V2-T02–T07; direct oracle/set equality |
| Schema V2 và validation contract | Có | Có | V2-T01, V2-M04/M05/M06 |
| V1 reduction và runtime đa phiên bản | Có | Có | V2-T04/T14; V1 T01–T32 |
| Scenario metadata và hashes | Có | Có | V2-T08/T09, V2-B05/B06, V2-M08 |
| Signal diagnostics | Có | Có | V2-T03, V2-B01/B03, V2-M07 |
| Sweep/UI/API V2 | Có | Có | V2-T10–T13, V2-B01–B06 |
| Oracle, fixtures và V2 gates | Có | Có | `tests/oracle_v2.py`, `tests/registry_v2.json`, `results/v2-acceptance-release-01/` |
| Freeze event V2 | Có | Có | `spec_history/v2-implementation-start-20261022T161522230020Z/` |

Revision `signal-heterogeneity-r1` chốt phạm vi thiết kế ban đầu: **ba Judge, tín hiệu nhị phân bất đối xứng và độc lập có điều kiện**. Mọi đề xuất thêm correlation, số Judge động hoặc raw evidence phải được đánh giá như thay đổi model mới, không lặng lẽ đưa vào implementation V2.0.

Evidence nghiệm thu cuối: `results/v2-acceptance-release-01/` đạt 26/26 checks; `suite=v2` đạt 15/15 và `suite=all` đạt 62/62 test methods, không có fail/error/skipped/not_run. Trạng thái `VERIFIED` chỉ áp dụng cho local M1 và lớp pure strategies đã đặc tả, không phải production deployment hay xác nhận tham số khớp thế giới thật.
