# CEAV-M1 V2.2 — Thiết kế incentive diagnostics

**Design revision:** `incentive-diagnostics-engine-r1`

**Model:** `ceav-m1-v2.0`; feature không đổi game semantics.

## 1. Module boundary

Module mới `ceav_m1.incentives` dùng public mathematical seams hiện có:

```python
analyze(config, profile, "rbts")
search_pure(config, "rbts")
```

Interface:

```python
decompose_branch(config, certificate) -> dict
diagnose_candidate(config, profile, analysis=None) -> dict
classify_landscape(search_result) -> dict
run_incentive_study(raw_config, profile, axes=None, on_progress=None) -> dict
write_incentive_run(...) -> dict
```

Module không sửa scoring, posterior, best-response solver hoặc equilibrium solver. Nó biến outputs exact hiện có thành diagnostics và gọi lại exhaustive search tại mỗi point.

## 2. Per-action High score

`solve_branch.high.observations` đã chứa, cho từng `(Z,X_i)` reachable:

- `probability_given_z`;
- `information_by_report[0/1]`;
- `optimal_prediction_score`.

Score của action `Hxy`:

```text
sum_observation probability_given_z
  * (information_by_report[report_for_x] + optimal_prediction_score)
```

Trong đó report tại `X=0` là `x`, tại `X=1` là `y`. Kết quả max của bốn action phải bằng `certificate.high.score`; sai khác là invariant failure.

`V_H_dep=max(score(H01),score(H10))`. Utility constrained dùng cùng `f`, `lambda` và effort cost; không tái tối ưu peer.

## 3. Exact statuses

Mọi so sánh thực hiện trên `Fraction`, kể cả threshold với budget. Decimal chỉ xuất qua serializer chung.

Best effort status lấy dấu của `net_incentive_best`; dependent-report status lấy dấu của `net_incentive_dependent`. Report status xét toàn bộ action hòa tại `V_H`, không chọn một representative tùy ý.

## 4. Landscape summarizer

Input phải có `enumeration_completed=true` và đúng `432` branch candidates. Chỉ records `accepted=true` được phân loại. Engine giữ nguyên retained IDs; summarizer không tự tìm hoặc bỏ equilibrium.

Full counts được tính bằng Cartesian product hai danh sách retained branch records. Không dựng lại predictions để phân loại effort/report. `full_equilibrium_count` tính lại phải bằng output solver.

## 5. Sweep execution

`run_incentive_study`:

1. validate base V2 config và RBTS;
2. validate profile;
3. dựng ordered grid từ allowlisted axes;
4. với mỗi point, clone raw config rồi validate;
5. invalid point được ghi và bỏ qua math;
6. valid point gọi `analyze`, `diagnose_candidate`, `search_pure`, `classify_landscape`;
7. emit progress trên tổng `valid/invalid points` và bên trong search quy đổi thành point progress;
8. giữ config/hash và exact outputs.

Không cache equilibrium giữa các point trong revision đầu. Ưu tiên output đơn giản, exact và dễ kiểm tra.

## 6. Artifacts

`write_incentive_run` dùng `new_run`/`finish_run`, no-overwrite và source pin hiện có. Nó pin thêm freeze V2.2 vào `inputs/incentives/` và ghi metadata:

```json
{
  "incentive_diagnostics": {
    "feature_version": "ceav-m1-v2.2-incentive-diagnostics",
    "freeze": "...",
    "documents": []
  }
}
```

CSV diagnostics có một row cho mỗi `Judge × Z`. CSV sweep có một row mỗi point với counts/status quan trọng; JSON giữ cấu trúc đầy đủ và equilibrium IDs.

## 7. CLI/API/UI

CLI/API chỉ chấp nhận RBTS. API validation chặn unknown fields trước khi tạo job. Worker snapshot và cancel behavior kế thừa server hiện tại.

UI gửi `axes` từ control riêng của view incentives. Kết quả được load lại từ artifacts trong history. Card giải thích threshold là conditional; landscape ghi rõ exhaustive pure search và giới hạn equilibrium selection.

## 8. Versioning

Giữ:

```text
model_version = ceav-m1-v2.0
```

Tăng runtime label thành `ceav-m1-engine-v2.2`. V2.2 là release feature, không phải model/game version mới.
