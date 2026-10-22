# Hướng dẫn dataset V2.1

## 1. Nhập ở đâu?

Chạy server và mở giao diện:

```powershell
python -m ceav_m1 serve --port 8765
```

Chọn tab **Dữ liệu**. Bạn có thể:

- chọn một file CSV bằng nút **File CSV**;
- bấm **Dùng dataset synthetic mẫu** để thử ngay;
- chọn đúng nguồn dữ liệu;
- bấm **Tạo config**.

Kết quả chưa tự thay config đang phân tích. Kiểm tra counts và estimates rồi bấm **Nạp config vào Phân tích**.

## 2. CSV bắt buộc

```text
case_id,ground_truth_Y,public_signal_Z,private_signal_A,private_signal_B,private_signal_C,cost_A,cost_B,cost_C
```

Mỗi case phải có cả ground truth và ba private checks. Binary fields chỉ dùng `0` hoặc `1`. Cost nhận chuỗi như `1/20`, `0.05` và phải không âm.

File mẫu: [datasets/synthetic_v2_calibration.csv](datasets/synthetic_v2_calibration.csv). Nó chỉ dùng để kiểm tra pipeline.

## 3. Tôi có cần nhập từng dòng trên giao diện không?

Không. Chuẩn bị CSV một lần rồi tải cả file. CLI cũng nhận thẳng đường dẫn:

```powershell
python -m ceav_m1 calibrate `
  --dataset datasets/synthetic_v2_calibration.csv `
  --base-config configs/v2/heterogeneous.json `
  --mechanism rbts `
  --provenance-status synthetic `
  --out results/my-calibration
```

## 4. Hệ thống tự làm gì?

Calibrator tự:

1. kiểm tra header, kiểu dữ liệu và `case_id` trùng;
2. kiểm tra có cả `Y=0` và `Y=1`;
3. tính `pi`, sensitivity, specificity và cost trung bình bằng `Fraction`;
4. giữ reward/budget từ base config;
5. chạy validator V2;
6. lưu raw CSV, counts, config, hashes và report trong một run bất biến.

Mỗi tỷ lệ có numerator và denominator. Ví dụ `16/20 -> 4/5`, nên người đọc biết estimate dựa trên bao nhiêu case.

## 5. Tôi phải cung cấp gì?

Với dữ liệu thật, cần cung cấp file CSV và định nghĩa nghiệp vụ dùng để gán `ground_truth_Y`. Hệ thống không tự bịa ground truth, không đọc đoạn văn scenario thành số và không tự coi quyết định đa số là sự thật.

`provenance_status` phải phản ánh đúng nguồn:

- `synthetic`: dữ liệu sinh để test;
- `assumption`: giả định;
- `pilot_estimate`: thử nghiệm nhỏ;
- `historical_estimate`: dữ liệu lịch sử.

## 6. Giới hạn

V2.1 dùng calibration matrix đầy đủ. Log production có missing private signal do Judge chọn Low Effort cần một thiết kế ước lượng khác để tránh selection bias. Point estimate hiện tại chưa có confidence interval và không chứng minh dataset đại diện cho tương lai.
