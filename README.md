# CEAV-M1

**Phiên bản chạy được hiện tại:** Version 2 · model mặc định `ceav-m1-v2.0`; vẫn replay đầy đủ `ceav-m1-v1.0`.

**Version 2:** `IMPLEMENTED` và `VERIFIED` local theo đặc tả `signal-heterogeneity-r1`. V1 được giữ tại Git tag `v1.0.0`; release hiện tại dùng tag `v2.0.0` sau khi push.

Phòng thí nghiệm local để phân tích incentive và cân bằng thuần của game một claim, ba Judge. Python 3.12+; ứng dụng chỉ dùng standard library và HTML/CSS/JavaScript thuần. Không cần ví, database, Node hoặc Internet để chạy ứng dụng.

## Chạy giao diện

Từ `C:\Users\dell\Desktop\fundtogether_data_analyzing`:

```powershell
python -m ceav_m1 serve --port 8765
```

Mở [http://127.0.0.1:8765](http://127.0.0.1:8765). Sáu màn hình dùng chung engine với CLI. Chỉnh tham số dạng chuỗi hữu tỉ, ví dụ `1/20` hoặc `0.05`. G4 minh họa candidate không phải cân bằng dù Delta gộp dương. Chi tiết và download của mỗi run nằm dưới kết quả.

Server chỉ bind loopback. Nếu port bận, lệnh trả lỗi; chọn port khác bằng `--port`. Chỉ chạy một tác vụ nặng tại một thời điểm. Hủy tác vụ dừng worker; run cancelled/interrupted không phải certificate hoàn chỉnh. `Ctrl+C` kết thúc server.

## CLI tái lập

Các command sau đã thực thi qua integration tests và browser acceptance. Đổi tên output cho mỗi lần chạy; thư mục đã tồn tại sẽ bị từ chối.

```powershell
python -m ceav_m1 analyze --config configs/golden_g1.json --profile configs/all_high.json --mechanism rbts --out results/my-g1
python -m ceav_m1 equilibria --config configs/golden_g1.json --mechanism rbts --out results/my-search
python -m ceav_m1 sweep --config configs/sweep.json --profile configs/all_high.json --mechanism rbts --out results/my-sweep
python -m ceav_m1 compare --config configs/golden_g1.json --profile configs/all_high.json --out results/my-compare
python -m ceav_m1 tests --suite goldens --out results/my-goldens
python -m ceav_m1 analyze --config configs/v2/heterogeneous.json --profile configs/all_high.json --scenario scenarios/sample_campaign/scenario.json --mechanism rbts --out results/my-v2
python -m ceav_m1 tests --suite v2 --out results/my-v2-tests
python -m ceav_m1 tests --suite all --out results/my-all-tests
python -m ceav_m1 tests --suite selected --test-id T01 --test-id V2-T11 --out results/my-selected
```

`configs/sweep.json` giải `base_config` tương đối với file sweep. Output tương đối với cwd. So sánh yêu cầu `F=f+2*lambda`; cùng trần không có nghĩa cùng reward thực chi. Sweep giữ profile cố định và cả hàng invalid, không tìm mọi cân bằng tại từng điểm.

## Evidence V2, hồi quy V1 và giới hạn

Nghiệm thu V2 local đạt V2-GATE-0–V2-GATE-5: V2-T01–T15 pass, V2-B01–B06 pass, V2-M01–M09 killed; full runner V1+V2 đạt 62/62. Xem [report V2](results/v2-acceptance-release-01/report.md), [acceptance.json](results/v2-acceptance-release-01/acceptance.json) và [benchmark](results/v2-acceptance-release-01/benchmark.json).

Nghiệm thu M1 local đã đạt GATE-0–GATE-5: 47 tests pass, B01–B09 pass, M01–M13 killed. Xem [report nghiệm thu](results/acceptance-release-01/report.md) và [kết quả audit](results/acceptance-release-01/acceptance.json).

- [CEAV_M1_SPEC.md](CEAV_M1_SPEC.md): game, payoff, timing và acceptance V1.
- [CEAV_M1_V2_SPEC.md](CEAV_M1_V2_SPEC.md): thay đổi V2 về sensitivity/specificity theo từng Judge, schema, tương thích V1 và gates đã nghiệm thu.
- [ENGINE_DESIGN_V2.md](ENGINE_DESIGN_V2.md) và [VERIFICATION_PLAN_V2.md](VERIFICATION_PLAN_V2.md): contract triển khai và evidence V2.
- [ENGINE_DESIGN.md](ENGINE_DESIGN.md): hợp đồng thuật toán V1.
- [VERIFICATION_PLAN.md](VERIFICATION_PLAN.md): oracle, fixtures, T01–T32, B01–B09, M01–M13 và gates V1.
- [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md): trạng thái triển khai và evidence thực tế, gồm phần chưa hoàn thành.
- [HUONG_DAN_CHO_NGUOI_MOI.md](HUONG_DAN_CHO_NGUOI_MOI.md): giải thích nền tảng và cách dùng V1.
- [HUONG_DAN_THAM_SO_V2.md](HUONG_DAN_THAM_SO_V2.md): giải thích các biến, config và cách dùng V2.

Mọi run pin input/source cùng spec/design/verification và event freeze thực tế trong `inputs/`. JSON có `exact` là nguồn số chính xác; `decimal` chỉ để xem. Có số quá lớn để hiển thị decimal thì giữ exact và ghi lý do.

Không suy từ score cao ra accuracy cao, từ một cân bằng ra equilibrium selection, hoặc từ enumeration thuần ra mọi mixed/coalition equilibrium. M1 không có stake/slashing hay ground-truth reward; đơn vị chuẩn hóa không phải tiền thực. Các kết quả âm được giữ nguyên.

Tooling Playwright chỉ dùng thu browser acceptance trong môi trường phát triển; không phải dependency của ứng dụng. Test suite đầy đủ có các phép kiểm tra chậm F12 và T17. Reference checker riêng không thay suite analyzer.
