# CEAV-M1 V2.1 — Thiết kế lớp calibration

**Design revision:** `calibration-engine-r1`

## 1. Module boundary

`ceav_m1.calibration` là lớp tiền xử lý tách khỏi engine game:

```python
parse_dataset(raw_bytes) -> tuple[CalibrationRow, ...]
calibrate(raw_bytes, base_config_raw, mechanism, provenance_status, source_name) -> dict
write_calibration_run(...) -> dict
```

Module dùng `csv.DictReader`, `Fraction`, integer counts và validator V2 hiện có. Nó không import evaluator, best response, equilibrium search hoặc scoring.

## 2. Records và exact arithmetic

`CalibrationRow` giữ `case_id`, năm binary values và ba `Fraction` costs. Parser từ chối unknown/missing columns, duplicate IDs, non-binary signals, negative costs và cả hai lớp ground truth bị thiếu.

Estimator trả cho mỗi rate:

```json
{"numerator": 16, "denominator": 20, "value": "4/5"}
```

Generated config dùng `str(Fraction)` rồi được `validate_config` chuẩn hóa. Không dùng float ở bất kỳ bước tính nào.

## 3. Dataset identity

`raw_sha256` dùng bytes đầu vào. Semantic record gồm binary integers và cost canonical strings; records sort theo `case_id`, serialize JSON ổn định rồi hash. Source filename chỉ là metadata và không nằm trong semantic hash.

## 4. CLI và artifacts

CLI:

```text
python -m ceav_m1 calibrate --dataset PATH --base-config PATH --mechanism rbts --provenance-status synthetic --out PATH
```

CLI parse/calibrate trước khi tạo output directory. `new_run` nhận generated config và operation `calibrate`; calibration freeze được pin thêm vào `inputs/calibration/`. Output đã tồn tại bị từ chối như các run khác.

## 5. API/worker

`POST /api/runs` nhận operation `calibrate` với đúng:

```text
operation, dataset_csv, source_name, provenance_status, base_config, mechanism
```

Server validate dataset trước khi nhận job. Worker ghi raw text và base config vào staging rồi gọi CLI; calculation vẫn nằm trong module dùng chung. Request body tối đa hiện tại của server áp dụng, không thêm multipart parser.

## 6. HTML

Browser đọc file bằng `File.text()` và giữ nội dung trong memory. View calibration hiển thị tên file, provenance, trạng thái chưa chạy và kết quả worker. Dataset mẫu lấy qua endpoint same-origin `/api/calibration/sample.csv`.

Nút áp dụng config gọi `putDraft(calibration.config, currentProfile, currentMechanism, currentScenario)`, sau đó chuyển sang view analyze. Không tự thay profile, scenario hoặc gửi analyze job.
