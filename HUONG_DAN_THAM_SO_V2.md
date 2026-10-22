# CEAV-M1 V2 — Hướng dẫn biến, tác động và cách dùng

**Áp dụng cho model:** `ceav-m1-v2.0`

**Trạng thái hiện tại:** `IMPLEMENTED` và `VERIFIED` local; đây là model mặc định của form mới. V1 vẫn được hỗ trợ để replay và so quy hồi.

**Đặc tả chuẩn:** [CEAV_M1_V2_SPEC.md](CEAV_M1_V2_SPEC.md)

Tài liệu này giải thích V2 bằng ngôn ngữ sử dụng. Công thức và điều kiện bắt buộc nằm trong spec. Bạn có thể chọn V2 trên giao diện hoặc dùng config trong `configs/v2/`.

## 1. V2 đang mô phỏng điều gì?

Mô hình xét một claim, ví dụ:

> “Milestone đã đáp ứng đủ tiêu chí để được duyệt giải ngân.”

Trong mô hình có một sự thật ẩn:

```text
Y=1: claim thực sự đạt
Y=0: claim thực sự không đạt
```

Ba Judge không biết trực tiếp `Y`. Họ chỉ có:

- `Z`: tín hiệu chung, miễn phí, cả ba cùng thấy;
- `X_A`, `X_B`, `X_C`: tín hiệu riêng, chỉ Judge tương ứng thấy khi chọn High Effort và trả chi phí.

Sau đó mỗi Judge gửi report và prediction. Majority của ba report tạo decision `D`. Evaluator biết `Y` trong mô phỏng để đo decision đúng/sai, nhưng `Y` không được dùng để trả thưởng cho Judge.

## 2. V1 và V2 khác nhau ở đâu?

V1 dùng:

```text
a = độ chính xác đối xứng của Z
b = độ chính xác đối xứng dùng chung cho X_A, X_B, X_C
```

Nếu `a=0.7`, V1 đồng thời giả định:

```text
P(Z=1 | Y=1) = 0.7
P(Z=0 | Y=0) = 0.7
```

V2 tách hai khả năng này và tách từng Judge:

```text
Z:   sensitivity riêng, specificity riêng
X_A: sensitivity riêng, specificity riêng
X_B: sensitivity riêng, specificity riêng
X_C: sensitivity riêng, specificity riêng
```

V2 vẫn có ba Judge, 32 trạng thái, sáu action, RBTS/fixed reward và majority 2/3 như V1.

`Z` là một tín hiệu chung duy nhất: A, B và C nhìn thấy cùng một giá trị. Vì vậy ba report có thể cùng sai theo `Z`; giả định các tín hiệu độc lập có điều kiện theo `Y` không biến ba report thành ba quan sát độc lập.

## 3. Bốn khái niệm phải phân biệt

### 3.1. Sensitivity

Sensitivity trả lời:

> Khi claim thực sự đạt, tín hiệu có báo 1 không?

```text
sensitivity = P(signal=1 | Y=1)
```

Ví dụ `sensitivity=4/5` nghĩa là trong nhóm claim thật sự đạt, 80% cho tín hiệu 1 và 20% cho tín hiệu 0.

### 3.2. Specificity

Specificity trả lời:

> Khi claim thực sự không đạt, tín hiệu có báo 0 không?

```text
specificity = P(signal=0 | Y=0)
```

Ví dụ `specificity=3/5` nghĩa là trong nhóm claim không đạt, 60% cho tín hiệu 0 và 40% vẫn cho tín hiệu 1.

### 3.3. False-negative rate

```text
false-negative rate = 1 - sensitivity
```

Đây là tỷ lệ tín hiệu bỏ sót claim thật trong nhóm `Y=1`.

### 3.4. False-positive rate

```text
false-positive rate = 1 - specificity
```

Đây là tỷ lệ tín hiệu trông tích cực dù claim thực sự không đạt. Nếu ưu tiên hạn chế giải ngân sai, đây là một thông số cần theo dõi chặt.

## 4. Giải thích từng biến

### 4.1. `Y` — Sự thật của claim

`Y` là biến ẩn, không phải input người dùng chọn cho một lượt Judge cụ thể.

- `Y=1`: claim đạt theo định nghĩa đã công bố.
- `Y=0`: claim không đạt.

Simulator dùng cả hai khả năng với trọng số do `pi` quyết định. Judge không thấy `Y`; evaluator dùng nó để đo accuracy và loss.

Điều phải ghi ngoài đời là tiêu chí nào khiến `Y=1`. Nếu tiêu chí mơ hồ, mọi con số accuracy phía sau cũng khó diễn giải.

### 4.2. `pi` — Tỷ lệ nền claim đạt

```text
pi = P(Y=1)
```

Ví dụ `pi=1/2` nghĩa là trước khi nhìn tín hiệu, mô hình cho claim đạt và không đạt xác suất bằng nhau.

`pi` tác động đến:

- posterior của Judge sau khi thấy tín hiệu;
- prediction về report của peer;
- expected score và best response;
- prior-weighted signal accuracy;
- expected payout và wrong-payout probability.

`pi` cao không có nghĩa cơ chế tốt. Nó chỉ nói claim thật xuất hiện thường xuyên hơn trong thế giới giả định.

### 4.3. `public_signal.sensitivity`

```text
P(Z=1 | Y=1)
```

Thông số này phản ánh khả năng tín hiệu chung nhận ra claim thật sự đạt. Tăng nó trực tiếp làm `Z=1` xuất hiện nhiều hơn trong nhóm `Y=1`.

Nó không cho biết khả năng phát hiện claim giả; phần đó thuộc specificity.

### 4.4. `public_signal.specificity`

```text
P(Z=0 | Y=0)
```

Thông số này phản ánh khả năng tín hiệu chung bác claim không đạt. Specificity thấp nghĩa là claim giả dễ tạo `Z=1`.

Vì cả ba Judge cùng thấy `Z`, một tín hiệu chung có specificity thấp có thể kéo cả ba về cùng một sai lầm. Majority không tự sửa được lỗi mà mọi Judge cùng sao chép.

### 4.5. `judges.i.private_signal.sensitivity`

```text
P(X_i=1 | Y=1)
```

Đây là khả năng kiểm tra riêng của Judge i nhận ra claim thật. Mỗi Judge có giá trị riêng.

Tăng thông số này chỉ thay chất lượng kênh `X_i`. Nó không buộc Judge chọn H và không buộc Judge báo theo `X_i`.

### 4.6. `judges.i.private_signal.specificity`

```text
P(X_i=0 | Y=0)
```

Đây là khả năng kiểm tra riêng của Judge i phát hiện claim không đạt. Specificity cao làm `X_i=1` ít xuất hiện hơn trong nhóm claim giả.

Đối với false approval, specificity thường là phía cần kiểm tra riêng. Tuy nhiên kết quả cuối vẫn phụ thuộc effort, report strategy và majority.

### 4.7. `judges.i.high_effort_cost`

Đây là chi phí utility Judge i trả khi chọn H để thấy `X_i`.

- Cost tăng: H khó có lợi hơn L.
- Cost giảm: H dễ có lợi hơn, nếu tín hiệu riêng tạo thêm expected score.
- Cost bằng 0: H không bị phạt bởi chi phí, nhưng vẫn phải kiểm tra ties và degeneracy.

Cost không làm tín hiệu chính xác hơn. Signal quality và effort cost là hai biến độc lập.

### 4.8. `e_i` — L hoặc H

- `L`: Judge chỉ dùng `Z`, không thấy `X_i`, không trả `c_i`.
- `H`: Judge trả `c_i` và thấy `(Z,X_i)`.

Judge chọn effort sau khi đã thấy `Z`. Vì vậy phải kiểm tra riêng `Z=0` và `Z=1`; một trung bình chung dương có thể che việc H không có lợi ở một nhánh.

### 4.9. `r_i` — Report

```text
r_i in {0,1}
```

Report là thông tin Judge gửi vào cơ chế. Nó không tự động bằng `Y`, `Z` hay `X_i`.

Judge có thể:

- báo theo `Z`;
- báo theo `X_i`;
- luôn báo 0 hoặc 1;
- đảo tín hiệu nếu đó là best response trong game đang xét.

### 4.10. `p_i` — Prediction

`p_i` là xác suất Judge i dự đoán scoring peer sẽ báo 1. Nó không phải xác suất claim thật và không được chấm trực tiếp với `Y`.

Engine tính candidate prediction Bayesian từ đúng thông tin Judge biết:

- L: điều kiện trên `Z`;
- H: điều kiện trên `(Z,X_i)`.

### 4.11. `f` — Thưởng nền RBTS

Trong RBTS:

```text
Reward_i = f + lambda * Score_i
```

`f` cộng cùng một lượng vào reward khi Judge bắt buộc tham gia. Nó tăng chi tiêu nhưng không tự thay đổi chênh lệch payoff giữa các action.

### 4.12. `lambda` — Độ mạnh của phần thưởng theo score

`lambda` biến score thành reward. Tăng `lambda` làm lợi ích score có trọng lượng lớn hơn so với effort cost.

Điều này có thể làm H hấp dẫn hơn trong một candidate, nhưng không loại bỏ các equilibrium dùng tín hiệu chung đạt score cao. Vì vậy phải xem certificate và equilibrium set, không chỉ nhìn `lambda`.

### 4.13. `fixed_reward`

Đây là reward mỗi Judge trong cơ chế fixed. Với cost H dương, fixed reward không bù thêm cho việc điều tra vì reward không phụ thuộc report/prediction.

### 4.14. `reward_budget`

Budget là trần tổng reward cam kết cho ba Judge.

```text
RBTS cần: 3*f + 6*lambda <= reward_budget
Fixed cần: 3*fixed_reward <= reward_budget
```

Budget chỉ kiểm tra khả năng chi trả theo trần. Cùng budget cap không có nghĩa hai cơ chế chi thực tế bằng nhau.

### 4.15. `payout_value`

`payout_value=V` dùng để đổi một false approval thành loss chuẩn hóa:

```text
wrong_payout_value = V * P(Y=0, D=1)
```

V không được đưa vào reward hoặc utility của Judge trong V2.0.

### 4.16. `operating_cost`

Đây là chi phí vận hành ngoài reward, mặc định 0. Nó được cộng vào `cash_review_cost`, không tác động best response nếu là hằng số công bố trước.

## 5. Signal accuracy hiển thị được tính thế nào?

Một tín hiệu có sensitivity cao nhưng specificity thấp chưa chắc có accuracy cao. Accuracy phụ thuộc cả `pi`:

```text
signal_accuracy = pi * sensitivity + (1-pi) * specificity
```

Ví dụ:

```text
pi = 1/2
sensitivity = 4/5
specificity = 3/5

signal_accuracy = 1/2 * 4/5 + 1/2 * 3/5
                = 7/10
```

Con số `7/10` chỉ mô tả bản thân tín hiệu. Decision accuracy còn phụ thuộc việc Judge chọn L/H, report thế nào và majority tổng hợp ra sao.

## 6. Cách đọc một config V2

Ví dụ:

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
  "f": "1/10",
  "lambda": "3/4",
  "fixed_reward": "8/5",
  "reward_budget": "6",
  "payout_value": "1",
  "operating_cost": "0"
}
```

Cách diễn giải đúng:

- Tỷ lệ nền claim đạt là 50%.
- Tín hiệu chung nhận ra claim thật 80%, nhưng chỉ bác claim giả 60%; false-positive rate của Z là 40%.
- A nhận ra claim thật tốt và bác claim giả khá tốt, cost 0.05.
- B có specificity rất cao nhưng cost 0.10.
- C rẻ nhất nhưng tín hiệu yếu hơn A/B theo phần lớn phía.
- Cơ chế vẫn phải được analyze để biết Judge có chọn H hay không và decision có tốt không.

Không được kết luận trước rằng B là Judge tốt nhất hoặc majority chắc chắn chính xác nhất. Hai Judge có thể dùng strategy khác tín hiệu và incentive có thể khiến họ chọn L.

## 7. V1 quy đổi sang V2

Config V1:

```json
{
  "pi": "1/2",
  "a": "7/10",
  "b": "4/5",
  "costs": ["1/20", "1/20", "1/20"]
}
```

Quy đổi phần signal/cost sang V2:

```text
public sensitivity = public specificity = 7/10

A private sensitivity = A private specificity = 4/5
B private sensitivity = B private specificity = 4/5
C private sensitivity = C private specificity = 4/5

A/B/C high_effort_cost = 1/20
```

Với mapping này, mọi state probability và kết quả toán phải khớp V1. Đây là regression bắt buộc của implementation V2.

## 8. Scenario metadata dùng để làm gì?

Config chỉ chứa con số. Scenario giải thích con số phản ánh thứ gì:

```text
Y=1 được định nghĩa bằng tiêu chí nào?
Z đến từ tài liệu công khai nào?
Judge A/B/C thực hiện loại kiểm tra riêng nào?
Các xác suất là giả định, pilot estimate hay historical estimate?
Ground truth được xác nhận khi nào?
```

Scenario metadata không làm engine tự tin hơn và không tham gia phép tính. Nó giúp người đọc biết run đang mô phỏng câu chuyện nào và tránh dùng một tỷ lệ không có nguồn như dữ liệu thật.

## 9. Nên thay đổi thông số theo thứ tự nào?

Khi khảo sát, giữ mọi thứ khác cố định và đổi một nhóm có chủ đích:

1. Chọn `pi` cho tỷ lệ nền.
2. Đặt public sensitivity/specificity để mô tả evidence chung.
3. Đặt từng private sensitivity/specificity và cost.
4. Chạy cùng một profile để xem decision và incentive.
5. Tìm equilibrium để kiểm tra Judge có thực sự giữ profile đó không.
6. Quét một tham số hoặc một axis rõ ràng.
7. So false approval, wrong payout, effort rate, reward và regret.

Nếu mục tiêu ưu tiên bảo vệ quỹ khỏi duyệt sai, bắt đầu bằng các scenario khác nhau về specificity và false-positive rate. Nếu mục tiêu kiểm tra động lực điều tra, quét signal quality cùng `high_effort_cost` và `lambda`, rồi đọc best-response certificate tại cả `Z=0` và `Z=1`.

## 10. Những kết luận không được rút ra

- Sensitivity 90% không có nghĩa Judge đúng 90% trên mọi claim.
- Signal accuracy cao không bảo đảm decision accuracy cao.
- Ba tín hiệu tốt không bảo đảm ba report độc lập nếu Judge cùng dùng Z.
- Tăng `lambda` không bảo đảm loại bỏ low-effort equilibrium.
- Nhiều Judge hơn không thuộc V2.0 và không tự bảo đảm chính xác hơn.
- Một pure equilibrium tốt không chứng minh người chơi sẽ chọn equilibrium đó.
- Scenario metadata không chứng minh tham số đã được hiệu chuẩn.
- Kết quả simulator không phải bằng chứng deployment production an toàn.

## 11. Trạng thái sử dụng hiện tại

| Phần | Trạng thái |
| --- | --- |
| V2 spec và định nghĩa tham số | Có |
| V2 config parser | Có; V2-T01 |
| V2 state generator | Có; V2-T02 và oracle độc lập |
| V2 oracle/tests | Có; V2-T01–T15 |
| V2 CLI/API/UI | Có; V2-T10–T13, V2-B01–B06 |
| V2 runtime evidence | Có; `results/v2-acceptance-release-01/` |

Giao diện chọn rõ V1 hoặc V2 và giữ draft riêng cho mỗi version. V2 đã đạt V2-GATE-0 đến V2-GATE-5; giới hạn vẫn là mô hình local ba Judge và pure strategies, không phải xác nhận dữ liệu thực hay production deployment.
