# CEAV-M1 V2.1 — Đặc tả hiệu chỉnh từ dataset

**Release feature:** `ceav-m1-v2.1-calibration`

**Calibration schema:** `ceav-calibration-v1`

**Model được tạo:** `ceav-m1-v2.0`

## 1. Mục đích và ranh giới

V2.1 thêm một lớp chuyển dataset đã gắn nhãn thành config V2. Nó không thay đổi game, timing, strategy, scoring, payoff, majority hoặc phạm vi cân bằng trong [CEAV_M1_V2_SPEC.md](CEAV_M1_V2_SPEC.md).

```text
CSV đã gắn nhãn
  -> validate
  -> đếm confusion matrix bằng số nguyên
  -> ước lượng exact Fraction
  -> config ceav-m1-v2.0
  -> analyzer V2 hiện có
```

Module không tạo ground truth thực, không đọc PDF/ảnh/video, không suy diễn tín hiệu từ văn bản và không gọi dữ liệu synthetic là evidence thực nghiệm.

## 2. Schema CSV

Header phải có đúng chín cột:

```text
case_id,ground_truth_Y,public_signal_Z,private_signal_A,private_signal_B,private_signal_C,cost_A,cost_B,cost_C
```

- `case_id`: chuỗi không rỗng và duy nhất trong file.
- `ground_truth_Y`, `public_signal_Z`, `private_signal_A/B/C`: chỉ nhận ký tự `0` hoặc `1`.
- `cost_A/B/C`: chuỗi số hữu tỉ hoặc thập phân không âm, parse bằng `Fraction`.
- Mỗi dòng là một case đã có ground truth hậu nghiệm và cả ba private check. Đây là calibration study matrix, không phải log production bị thiếu private signal khi Judge chọn Low Effort.
- File UTF-8 hoặc UTF-8 BOM. Dòng trống cuối file được chấp nhận; cột lạ, cột thiếu, dòng thừa/thiếu ô và header trùng bị từ chối.
- Dataset phải có ít nhất một case `Y=1` và một case `Y=0`.

## 3. Ước lượng

Không smoothing và không làm tròn trong engine:

```text
pi = count(Y=1) / count(all)

sens_Z = count(Y=1,Z=1) / count(Y=1)
spec_Z = count(Y=0,Z=0) / count(Y=0)

sens_i = count(Y=1,X_i=1) / count(Y=1)
spec_i = count(Y=0,X_i=0) / count(Y=0)

cost_i = sum(cost_i) / count(all)
```

Nếu bất kỳ sensitivity hoặc specificity bằng `0` hoặc `1`, config V2.0 sinh ra sẽ bị validator V2 từ chối vì V2.0 yêu cầu khoảng mở `(0,1)`. Calibrator không tự thêm pseudo-count để che degeneracy.

Base config phải là `ceav-m1-v2.0`. Calibrator giữ nguyên `f`, `lambda`, `fixed_reward`, `reward_budget`, `payout_value`, `operating_cost`; thay `pi`, toàn bộ signal parameters và ba `high_effort_cost`. Config kết quả phải qua validator với mechanism được chọn.

## 4. Identity và provenance

Output ghi hai identity:

- `raw_sha256`: hash bytes CSV thực sự được nhập.
- `dataset_hash`: semantic hash của records đã chuẩn hóa và sắp theo `case_id`; đổi line ending hoặc thứ tự dòng không đổi semantic hash.

`provenance_status` phải thuộc:

```text
synthetic | assumption | pilot_estimate | historical_estimate
```

Dataset mẫu trong repository bắt buộc dùng `synthetic`. Trạng thái provenance không làm thay đổi phép tính.

## 5. Output bắt buộc

Một calibration run thành công chứa:

- `dataset.csv`: raw bytes đầu vào;
- `calibration.json`: counts, confusion numerators/denominators, estimates, hashes, warnings và generated config;
- `config.json`: config V2 canonical có thể nạp thẳng vào analyzer;
- `report.md`: giải thích nguồn, số case và giới hạn;
- `manifest.json`: trạng thái terminal, source/spec/calibration freeze và artifact hashes.

API/UI không được chỉ hiển thị tỷ lệ. Mỗi estimate phải kèm numerator, denominator và exact value để người dùng thấy lượng evidence phía sau.

## 6. Giao diện

Giao diện có view **Dữ liệu** tách khỏi form scenario:

1. chọn CSV hoặc nạp dataset synthetic mẫu;
2. chọn provenance;
3. chạy calibration qua worker thật;
4. xem số case, class balance và estimates;
5. chủ động bấm **Nạp config vào Phân tích**.

Calibration không tự chạy analyzer và không tự ghi đè draft hiện tại.

## 7. Giới hạn diễn giải

- Estimate từ synthetic chỉ kiểm tra pipeline và minh họa giả định.
- Estimate từ dữ liệu quan sát có thể bị selection bias, label leakage hoặc ground-truth error.
- Chi phí phải được quy đổi về cùng đơn vị utility/reward trước khi nhập.
- Point estimate không phải chứng nhận tính đại diện hoặc độ chắc chắn thống kê.
- V2.1 không hỗ trợ missing private signal, operational effort/report logs, confidence interval hoặc tự lấy dữ liệu bên ngoài.
