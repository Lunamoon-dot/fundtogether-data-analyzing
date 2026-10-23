# CEAV-M1

**Phiên bản chạy được hiện tại:** Version 3.1 · robustness grid trên game hybrid RBTS + verification anchor `ceav-m1-v3.0`; V3.1 không đổi game, chỉ kiểm tra độ bền của policy dưới uncertainty.

**Version 2.2 diagnostics:** `SPECIFIED`, `IMPLEMENTED` và đã qua targeted verification INC-T01–INC-T08 cùng INC-B01. Trạng thái full release còn chờ toàn bộ regression/evidence INC-GATE-5. V2.1, V2.0 và V1 giữ trạng thái nghiệm thu trước đó trên source đã pin của từng release.

**Version 3:** `SPECIFIED`, `IMPLEMENTED` và `VERIFIED` local. Report khóa trước khi audit; `T` chỉ xuất hiện sau đó và chỉ tham gia reward. V3 không dùng `Y` làm reward oracle và không cho Judge thấy `A/T`. Nghiệm thu r2 tại [report V3](results/v3-acceptance-closeout-r2/report.md) và [acceptance.json](results/v3-acceptance-closeout-r2/acceptance.json).

Phòng thí nghiệm local để phân tích incentive và cân bằng thuần của game một claim, ba Judge. Python 3.12+; ứng dụng chỉ dùng standard library và HTML/CSS/JavaScript thuần. Không cần ví, database, Node hoặc Internet để chạy ứng dụng.

## Chạy giao diện

Từ `C:\Users\dell\Desktop\fundtogether_data_analyzing`:

```powershell
python -m ceav_m1 serve --port 8765
```

Mở [http://127.0.0.1:8765](http://127.0.0.1:8765). Form mặc định là V3 với ba nhóm tín hiệu cũ và nhóm verification anchor `q/sensitivity/specificity/cost_per_audit`; reward hiển thị `f`, `lambda_peer` và `anchor_weight` riêng. Màn hình **Dữ liệu** vẫn tạo config V2; **Chẩn đoán động lực** vẫn chạy V2.2. Chỉnh tham số dạng chuỗi hữu tỉ, ví dụ `1/20` hoặc `0.05`. Chi tiết và download của mỗi run nằm dưới kết quả.

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
python -m ceav_m1 calibrate --dataset datasets/synthetic_v2_calibration.csv --base-config configs/v2/heterogeneous.json --mechanism rbts --provenance-status synthetic --out results/my-calibration
python -m ceav_m1 incentives --config configs/v2/heterogeneous.json --profile configs/all_high.json --out results/my-incentives
python -m ceav_m1 analyze --config configs/v3/heterogeneous_anchor.json --profile configs/all_high.json --mechanism hybrid_anchor --out results/my-v3
python -m ceav_m1 equilibria --config configs/v3/heterogeneous_anchor.json --mechanism hybrid_anchor --out results/my-v3-search
python -m ceav_m1 tests --suite v2 --out results/my-v2-tests
python -m ceav_m1 tests --suite calibration --out results/my-calibration-tests
python -m ceav_m1 tests --suite incentives --out results/my-incentive-tests
python -m ceav_m1 tests --suite v3 --out results/my-v3-tests
python -m ceav_m1 robustness --study configs/v3/robustness_v3_1.json --out results/my-v3.1-robustness
python -m ceav_m1 tests --suite robustness --out results/my-v3.1-tests
python -m ceav_m1 tests --suite all --out results/my-all-tests
python -m ceav_m1 tests --suite selected --test-id T01 --test-id V2-T11 --out results/my-selected
```

`configs/sweep.json` giải `base_config` tương đối với file sweep. Output tương đối với cwd. So sánh yêu cầu `F=f+2*lambda`; cùng trần không có nghĩa cùng reward thực chi. Sweep V1/V2 giữ profile cố định và chỉ phân tích candidate. Sweep V3 giữ candidate metrics, exhaustive pure-equilibrium landscape và khoảng min/max exact của decision/accounting metrics tại mọi cân bằng thuần; hàng invalid vẫn được giữ.

V3.1 dùng study đã khai báo trong [`configs/v3/robustness_v3_1.json`](configs/v3/robustness_v3_1.json): 6 policy × 18 uncertainty scenarios = 108 points, mỗi point kiểm đủ 432 branch candidates. Policy chỉ bền vững khi mọi scenario qua gate theo equilibrium xấu nhất. Kết quả chính là false approval, wrongly paid value, false rejection và cash review cost; accuracy chỉ là diagnostic. Grid không nội suy, các range là provenance assumptions chứ không phải confidence intervals, và latency chưa được mô hình hóa.

Acceptance V3.1 đã pass: [audit](results/v31-acceptance-final/report.md), [full runner](results/v31-all-tests-final/report.md), [study 108 điểm](results/v31-robustness-study-release-02/report.md), [browser ROB-B01](results/v31-browser-final-ROB-B01/report.md) và [mutation probes](results/v31-mutations-final/report.md). Kết quả chính là **không có policy robust** trong grid đã khai báo; `anchor_q80` chỉ đạt 6/18 scenario, nên đây là chẩn đoán giới hạn của policy hiện tại chứ không phải tuyên bố accuracy hay production readiness.

## Evidence V3, V2.2, V2.1, V2 và giới hạn

Nghiệm thu V3 local đạt V3-GATE-0–V3-GATE-5: all-suite 90/90; V3-T01–T12 pass; V3-B01 pass; V3-M01–M10 đều killed. Xem [report V3](results/v3-acceptance-closeout-r2/report.md), [acceptance.json](results/v3-acceptance-closeout-r2/acceptance.json), [all-suite](results/v3-all-tests-closeout-r2-final/report.md), [browser V3](results/v3-browser-closeout-r2-02/report.md), [mutation report](results/v3-mutations-closeout-r2/report.md) và [closeout study](results/v3-closeout-study-r2/report.md). Baseline synthetic vẫn bất lợi: all-High có accuracy `1791/2000` nhưng không phải cân bằng. Quét tham số sau đó tìm được preset experimental anchor-dominant có equilibrium accuracy `1813/2000`; xem [báo cáo parameter sweep](V3_PARAMETER_SWEEP_REPORT.md). Kết quả này chưa chứng minh nguồn audit ngoài đời đáng tin hoặc đủ rẻ; preset để audit cost bằng 0 vì chưa có dữ liệu thật, nhưng engine đã hỗ trợ quét chi phí này.

Targeted V2.2 đạt INC-T01–INC-T08 (8/8) tại `results/v22-incentive-tests-implementation-01/` và browser INC-B01 (13/13 bước) tại `results/v22-browser-INC-B01-implementation-01/`. Evidence này chứng minh implementation/flow V2.2 hiện tại; chưa thay cho full regression gate INC-GATE-5.

Nghiệm thu V2.1 local đạt CAL-GATE-0–CAL-GATE-5: CAL-T01–CAL-T08 pass, CAL-B01 pass, V1 47/47 và V2 15/15 methods pass trên cùng source. Xem [report V2.1](results/v21-calibration-acceptance-release-01/report.md) và [acceptance.json](results/v21-calibration-acceptance-release-01/acceptance.json). Dataset mẫu 40 case là synthetic fixture, không phải dữ liệu Judge thực.

Nghiệm thu V2 local đạt V2-GATE-0–V2-GATE-5: V2-T01–T15 pass, V2-B01–B06 pass, V2-M01–M09 killed; full runner V1+V2 đạt 62/62. Xem [report V2](results/v2-acceptance-release-01/report.md), [acceptance.json](results/v2-acceptance-release-01/acceptance.json) và [benchmark](results/v2-acceptance-release-01/benchmark.json).

Nghiệm thu M1 local đã đạt GATE-0–GATE-5: 47 tests pass, B01–B09 pass, M01–M13 killed. Xem [report nghiệm thu](results/acceptance-release-01/report.md) và [kết quả audit](results/acceptance-release-01/acceptance.json).

- [CEAV_M1_SPEC.md](CEAV_M1_SPEC.md): game, payoff, timing và acceptance V1.
- [CEAV_M1_V2_SPEC.md](CEAV_M1_V2_SPEC.md): thay đổi V2 về sensitivity/specificity theo từng Judge, schema, tương thích V1 và gates đã nghiệm thu.
- [CEAV_M1_V2_2_INCENTIVE_SPEC.md](CEAV_M1_V2_2_INCENTIVE_SPEC.md), [ENGINE_DESIGN_V2_2_INCENTIVES.md](ENGINE_DESIGN_V2_2_INCENTIVES.md) và [VERIFICATION_PLAN_V2_2_INCENTIVES.md](VERIFICATION_PLAN_V2_2_INCENTIVES.md): contract V2.2, decomposition, conditional thresholds và equilibrium landscape.
- [CEAV_M1_V3_ANCHOR_SPEC.md](CEAV_M1_V3_ANCHOR_SPEC.md), [ENGINE_DESIGN_V3_ANCHOR.md](ENGINE_DESIGN_V3_ANCHOR.md) và [VERIFICATION_PLAN_V3_ANCHOR.md](VERIFICATION_PLAN_V3_ANCHOR.md): model, implementation contract và evidence plan V3 đã nghiệm thu local.
- [CEAV_M1_V3_1_ROBUSTNESS_SPEC.md](CEAV_M1_V3_1_ROBUSTNESS_SPEC.md), [ENGINE_DESIGN_V3_1_ROBUSTNESS.md](ENGINE_DESIGN_V3_1_ROBUSTNESS.md) và [VERIFICATION_PLAN_V3_1_ROBUSTNESS.md](VERIFICATION_PLAN_V3_1_ROBUSTNESS.md): robustness grid, worst-equilibrium gates, baselines và uncertainty provenance trên game V3 không đổi.
- [ENGINE_DESIGN_V2.md](ENGINE_DESIGN_V2.md) và [VERIFICATION_PLAN_V2.md](VERIFICATION_PLAN_V2.md): contract triển khai và evidence V2.
- [ENGINE_DESIGN.md](ENGINE_DESIGN.md): hợp đồng thuật toán V1.
- [VERIFICATION_PLAN.md](VERIFICATION_PLAN.md): oracle, fixtures, T01–T32, B01–B09, M01–M13 và gates V1.
- [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md): trạng thái triển khai và evidence thực tế, gồm phần chưa hoàn thành.
- [HUONG_DAN_CHO_NGUOI_MOI.md](HUONG_DAN_CHO_NGUOI_MOI.md): giải thích nền tảng và cách dùng V1.
- [HUONG_DAN_THAM_SO_V2.md](HUONG_DAN_THAM_SO_V2.md): giải thích các biến, config và cách dùng V2.
- [HUONG_DAN_DATASET_V2_1.md](HUONG_DAN_DATASET_V2_1.md): CSV lấy từ đâu, nhập ở đâu và cách đọc config được ước lượng.
- [HUONG_DAN_CHAN_DOAN_DONG_LUC_V2_2.md](HUONG_DAN_CHAN_DOAN_DONG_LUC_V2_2.md): cách chạy và đọc từng kết quả V2.2.
- [V3.1 incentive mechanisms research](references/research/ceav-m1-v3-1-incentive-mechanisms.md): tổng hợp nguồn primary, trade-off và hướng thử nghiệm cho bài toán high-effort.

Mọi run pin input/source cùng spec/design/verification và event freeze thực tế trong `inputs/`. JSON có `exact` là nguồn số chính xác; `decimal` chỉ để xem. Có số quá lớn để hiển thị decimal thì giữ exact và ghi lý do.

Không suy từ score cao ra accuracy cao, từ một cân bằng ra equilibrium selection, hoặc từ enumeration thuần ra mọi mixed/coalition equilibrium. M1 không có stake/slashing hay ground-truth reward; đơn vị chuẩn hóa không phải tiền thực. Các kết quả âm được giữ nguyên.

Tooling Playwright chỉ dùng thu browser acceptance trong môi trường phát triển; không phải dependency của ứng dụng. Test suite đầy đủ có các phép kiểm tra chậm F12 và T17. Reference checker riêng không thay suite analyzer.
