# CEAV-M1 — Trạng thái triển khai

**Trạng thái hiện tại: IMPLEMENTED và VERIFIED trong phạm vi M1 local.**

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
