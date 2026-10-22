# CEAV-M1 — Trạng thái triển khai

## Version 2.1 — Data Calibration

**Trạng thái hiện tại: `SPECIFIED`, `IMPLEMENTED` và `VERIFIED` trong phạm vi calibration local.**

V2.1 thêm view **Dữ liệu**, strict CSV parser, exact estimator, CLI/API worker và immutable calibration artifacts. Feature sinh config `ceav-m1-v2.0`; game, scoring và equilibrium search không đổi. Dataset mẫu 40 case là synthetic fixture, không phải evidence thực tế.

Nguồn chuẩn: [spec](CEAV_M1_V2_1_CALIBRATION_SPEC.md), [engine design](ENGINE_DESIGN_V2_1_CALIBRATION.md), [verification plan](VERIFICATION_PLAN_V2_1_CALIBRATION.md), [hướng dẫn sử dụng](HUONG_DAN_DATASET_V2_1.md).

Nghiệm thu: [report](results/v21-calibration-acceptance-release-01/report.md) và [acceptance.json](results/v21-calibration-acceptance-release-01/acceptance.json). Audit calibration đạt 9/9 checks; CAL-T01–CAL-T08 đạt 8/8, V1 đạt 47/47 methods, V2 đạt 15/15, CAL-B01 và toàn bộ V1/V2 browser regression đều pass trên source hash `b66df2cf8d518f638f86e18a812c8d44e9ae4cec7490805328879492cd4ed436`.

| Phần | Evidence V2.1 |
| --- | --- |
| Freeze/fixture | `spec_history/v2.1-calibration-implementation-start-20261022T173242126063Z/`; spec/design/plan, CSV 40 case và expected độc lập được pin trước production module |
| Parser/estimator/config | CAL-T01–CAL-T04; exact Fraction, strict schema, semantic/raw hashes, generated config chạy được |
| CLI/API/artifacts | CAL-T05–CAL-T06; worker/direct parity, no-overwrite, raw dataset và freeze được pin |
| Browser | `results/v21-browser-CAL-B01-release-05/`; 13/13 bước desktop/mobile, explicit apply và không có JavaScript error |
| Regression | `results/v21-v1-regression-release-02/` 47/47; `results/v21-v2-tests-release-02/` 15/15; V1 B01–B09 và V2-B01–B06 pass |

Phạm vi VERIFIED chỉ chứng minh pipeline calibration local và giữ nguyên behavior V1/V2. Dataset mẫu vẫn là synthetic; hệ thống chưa có dữ liệu Judge thực, confidence interval, missing-signal estimator hoặc bằng chứng dataset đại diện.

## Version 2

**Trạng thái V2: `SPECIFIED`, `IMPLEMENTED` và `VERIFIED` trong phạm vi M1 local.**

[CEAV_M1_V2_SPEC.md](CEAV_M1_V2_SPEC.md) revision `signal-heterogeneity-r1` định nghĩa sensitivity/specificity riêng cho tín hiệu chung và từng Judge, schema V2, quy hồi về V1, scenario metadata và V2-GATE-0–V2-GATE-5. [ENGINE_DESIGN_V2.md](ENGINE_DESIGN_V2.md) và [VERIFICATION_PLAN_V2.md](VERIFICATION_PLAN_V2.md) là contract/evidence plan đã được freeze trước production V2.

Nghiệm thu: [report](results/v2-acceptance-release-01/report.md), [acceptance.json](results/v2-acceptance-release-01/acceptance.json), [benchmark](results/v2-acceptance-release-01/benchmark.json). Audit đạt 26/26 checks; `suite=v2` đạt 15/15 và `suite=all` đạt 62/62 methods, không fail/error/skipped/not_run.

| Phần | Evidence V2 |
| --- | --- |
| Freeze/provenance | `spec_history/v2-implementation-start-20261022T161522230020Z/`; raw hashes spec/design/plan và oracle/tests có trước production |
| Parser, distribution, diagnostics | V2-T01–T04; exact Fraction; heterogeneous, below-half và V1 reduction fixtures |
| Candidate, best response, pure search | V2-T05–T07; đủ 3 Judge × 2 Z; direct oracle 46.656 profiles và 5.038.848 deviations; exact set equality |
| Scenario, artifact, CLI, sweep | V2-T08–T11; scenario hash tách config hash; nested axes; no-overwrite |
| API, UI, history, runner | V2-T12–T15; selector V1/V2, draft riêng, import/export, diagnostics và differences model/config/profile/scenario |
| Browser | V2-B01–B06; Edge 155; desktop/mobile/keyboard; V1 B01–B09 cũng pass lại trên source cuối |
| Mutation | `results/v2-mutations-release-04/`; V2-M01–M09 đều killed; baseline pass, production bytes unchanged |
| Hồi quy V1 | `results/v2-v1-regression-release-02/`; đủ T01–T32, 47 methods pass |

V2 không tạo ground truth ngoài đời và không tự ước lượng sensitivity/specificity. Scenario chỉ là metadata provenance, không tham gia phép tính. Kết quả vẫn giới hạn ở ba Judge, conditional independence và pure strategies.

## Version 1

**Trạng thái V1: `IMPLEMENTED` và `VERIFIED` trong phạm vi M1 local.**

Nghiệm thu: [report](results/acceptance-release-01/report.md), [acceptance.json](results/acceptance-release-01/acceptance.json), [benchmark](results/acceptance-release-01/benchmark.json). Audit đối chiếu 68 điều kiện và đạt GATE-0–GATE-5; kiểm tra bổ sung đã đối chiếu raw hashes của 98 artifact cuối thuộc 12 run.

Các tài liệu spec/design/verification và snapshot gốc giữ nguyên bytes tại thời điểm freeze. Các mô tả “chưa triển khai” trong bản bàn giao tài liệu gốc là trạng thái trước implementation; bảng dưới đây ghi trạng thái code và evidence hiện tại.

| Phần | SPECIFIED | IMPLEMENTED | VERIFIED / evidence |
| --- | --- | --- | --- |
| Freeze và provenance | Có | Có | `spec_history/implementation-start-20261022T081942148684Z/`; raw bytes/hash ba tài liệu, parent chain, reference checker preexisted |
| Model, blinded observations, scoring, direct accounting | Có | Có | T01–T05, T20; state/conditional oracle độc lập; Fraction xuyên suốt |
| Best response và certificates | Có | Có | T06–T15; đủ 3 Judge × 2 Z; giữ peer tables, mọi report/effort tie; replay độc lập, reject tamper và cancelled run |
| Exhaustive pure search | Có | Có | T16–T19; 216 candidates/Z; T17 kiểm tra 46.656 full profiles và 5.038.848 full-strategy deviations; exact set equality ở G1 |
| Differential F12 | Có | Có | 27 configs × 432 = 11.664 branch candidates theo thứ tự xuôi, và 11.664 theo thứ tự đảo; 0 discrepancy |
| CLI và artifacts | Có | Có | T20–T22; analyze/equilibria/sweep/compare, no-overwrite, canonical hashes, source/config/profile/spec pin; failed runs giữ report/log |
| HTML/API/worker/history | Có | Có | T23–T31; six screens gọi engine thật; same-origin/token, path containment, duplicate lock, queued/during/after cancel, child tree cleanup, abrupt restart |
| Browser và accessibility | Có | Có | B01–B09; Edge 155.0.4283.62; 1366×768 và 390×844; keyboard/focus, wide-table scroll, labels, contrast, import/export/download, real failures |
| Mutation probes | Có | Có | M01–M13: cả 13 killed bởi assertion/invariant liên quan; baseline pass; production/fixture bytes unchanged |

## Evidence cuối

- Full suite: `results/run-20261022T095215-bfe5abfabb/` — 47 unittest methods, đủ T01–T32; 47 pass, 0 fail/error/skipped/not_run; khoảng 252 giây trên máy kiểm chứng. [Registry](tests/registry.json) là mapping; kết quả pass lấy từ records đã thực thi.
- Mutation: `results/mutations-release-01/` — baseline, patch/hash mutant, assertion logs và kết quả M01–M13.
- Browser: `browser-B01-release-01`, `browser-B02-release-01`, `browser-B03-release-02`, `browser-B04-release-01`, `browser-B05-release-01`, `browser-B06-release-01`, `browser-B07-release-01`, `browser-B08-release-01`, `browser-B09-release-01`, đều dưới `results/`.
- B03: G1–G4 UI/API khớp byte-for-byte với CLI ở summary, best responses và states; G1/G4 có ảnh exact/certificate/witness; lọc Y/Z/decision và clone candidate giữ run gốc.
- B05: sweep một/nhiều axes, hàng invalid_budget, replay từng điểm; comparison cùng trần và download artifact cả hai nhánh fixed/rbts.
- B06: reference mới, goldens, selected, missing-discovery evidence, actual failure fixture và full suite qua giao diện.
- B07: snapshot không đổi khi sửa draft, backend từ chối duplicate, cancel dừng worker; abrupt server exit dừng computation và run mở lại interrupted.
- B08: file tải từ browser khớp hashes trong manifest; pin hai run chỉ rõ khác biệt config/profile/model.
- Checker reference và `verification/reference_results.json` gốc được giữ nguyên; SHA-256 JSON vẫn là `85622a6a7d2a03b787009b9a2f21a6fc7079dd87276b5ed7eb2cbd22c1ff7209`.

Mỗi evidence áp dụng cho source được pin trong manifest của chính run đó. Browser freshness so engine/web/presets; full suite pin toàn bộ source; mutation audit kiểm tra source engine/web/tests/presets tương ứng. Oracle F09 có raw source trước production khớp hash đã ghi; `tests/fixtures/oracle_recovery.json` ghi rõ file bytes đó được materialize lại sau này, không gán lùi timestamp.

## Kết quả và giới hạn

G1 all-H báo X là cân bằng thuần với accuracy `112/125`, wrong payout `13/250`. All-Z cũng là cân bằng, accuracy `7/10`, wrong payout `3/20`, và utility mỗi Judge bằng 2, cao hơn all-H trong G1. G3 và G4 bác all-H; G4 có deviation có lợi ở Z=1 dù Delta gộp dương. Các kết quả bất lợi được giữ trong output.

M1 được nghiệm thu cho game và lớp pure strategies đã định nghĩa. Đây chưa phải deployment production, thực nghiệm người dùng, chứng nhận mixed/coalition equilibrium hoặc equilibrium selection. Thời gian Python là benchmark tính toán, không phải cash review cost; đơn vị payout/reward là chuẩn hóa, không phải tiền thực.

Các run lỗi cũ vẫn giữ nguyên để truy vết. Riêng `browser-B06-final-01` lỗi observation timeout trong driver; worker của run đó vẫn hoàn tất 47 tests pass. Lượt B06 release theo dõi handle thật, chịu được lỗi quan sát tạm thời và có evidence terminal/render đầy đủ. Không sửa artifact cũ thành pass.
