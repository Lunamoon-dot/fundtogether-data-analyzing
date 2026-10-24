# CEAV-M1 — Hướng dẫn triển khai trong workspace độc lập

## 1. Phạm vi và tài liệu phải đọc

Workspace: `C:\Users\dell\Desktop\fundtogether_data_analyzing`. Chỉ thực hiện thay đổi cho hệ thống nghiên cứu này trong thư mục này. Hệ thống dùng Python 3.12+ standard library và HTML/CSS/JavaScript thuần theo đặc tả.

Chọn nguồn chuẩn theo model version trước khi thay đổi behavior:

- **V1:** đọc [CEAV_M1_SPEC.md](CEAV_M1_SPEC.md); đây là nguồn chuẩn của model `ceav-m1-v1.0`.
- **V2 signal/schema hoặc implementation V2:** đọc [CEAV_M1_V2_SPEC.md](CEAV_M1_V2_SPEC.md), [ENGINE_DESIGN_V2.md](ENGINE_DESIGN_V2.md), [VERIFICATION_PLAN_V2.md](VERIFICATION_PLAN_V2.md), rồi đọc các phần V1 mà spec V2 tuyên bố kế thừa. V2 đã được kiểm chứng local; giữ evidence V2 và hồi quy V1 khi thay đổi vùng dùng chung.
- **Dataset calibration V2.1:** đọc [CEAV_M1_V2_1_CALIBRATION_SPEC.md](CEAV_M1_V2_1_CALIBRATION_SPEC.md), [ENGINE_DESIGN_V2_1_CALIBRATION.md](ENGINE_DESIGN_V2_1_CALIBRATION.md) và [VERIFICATION_PLAN_V2_1_CALIBRATION.md](VERIFICATION_PLAN_V2_1_CALIBRATION.md). Calibration sinh config V2 nhưng không được gọi synthetic data là dữ liệu thực.
- **Incentive diagnostics V2.2:** đọc [CEAV_M1_V2_2_INCENTIVE_SPEC.md](CEAV_M1_V2_2_INCENTIVE_SPEC.md), [ENGINE_DESIGN_V2_2_INCENTIVES.md](ENGINE_DESIGN_V2_2_INCENTIVES.md) và [VERIFICATION_PLAN_V2_2_INCENTIVES.md](VERIFICATION_PLAN_V2_2_INCENTIVES.md). V2.2 giữ model `ceav-m1-v2.0`; phân biệt conditional threshold với exhaustive equilibrium landscape trước khi kết luận reward tuning có hiệu quả.
- **Robustness V3.1:** đọc [CEAV_M1_V3_1_ROBUSTNESS_SPEC.md](CEAV_M1_V3_1_ROBUSTNESS_SPEC.md), [ENGINE_DESIGN_V3_1_ROBUSTNESS.md](ENGINE_DESIGN_V3_1_ROBUSTNESS.md) và [VERIFICATION_PLAN_V3_1_ROBUSTNESS.md](VERIFICATION_PLAN_V3_1_ROBUSTNESS.md). V3.1 giữ nguyên game `ceav-m1-v3.0`; policy chỉ bền vững khi mọi uncertainty point qua gate theo cân bằng thuần xấu nhất. Không nội suy grid hoặc gọi assumption range là confidence interval.

- **Engine/thuật toán, schema hoặc tối ưu hiệu năng V1:** đọc [ENGINE_DESIGN.md](ENGINE_DESIGN.md), nhất là module interface, observation, peer freeze, degeneracy và certificates.
- **Viết test, sửa bug, review hoặc kết luận V1 đã hoàn thành:** đọc [VERIFICATION_PLAN.md](VERIFICATION_PLAN.md); chọn fixture, oracle và gate tương ứng trước khi sửa.
- **Thiết kế/kiểm chứng V2:** dùng spec V2 làm requirement; ghi implementation contract và evidence plan vào hai tài liệu V2 riêng, không sửa nghĩa của design/verification V1.
- **HTML/API/worker V1:** đọc thêm spec V1 §18 và ENGINE_DESIGN §10; phải nối engine thật, đủ chức năng browser acceptance. Với V2, đọc spec V2 §12 và design V2 sau khi tài liệu đó được tạo.
- **Thay đổi lý luận hoặc tuyên bố học thuật:** đọc spec V1 §9.4, phần V2 kế thừa và [references/PRIMARY_SOURCES.md](references/PRIMARY_SOURCES.md); đối chiếu lại nguồn khi đưa ra khẳng định mới.

Giữ nguồn chuẩn theo vai trò: spec định nghĩa game; engine design định nghĩa implementation contract; verification plan định nghĩa evidence; file này định nghĩa workflow. Khi các tài liệu mâu thuẫn, chỉ rõ điều khoản và xử lý theo spec, không chọn phiên bản dễ pass test hơn. Ghi và giải quyết mâu thuẫn ảnh hưởng toán trước khi công bố kết quả phụ thuộc nó.

Không nhập baseline, code, policy, cấu hình hoặc dữ liệu của workspace FundTogether cũ. Scope M1 không có blockchain, ví, database, stake, appeal hoặc cơ chế review production.

## 2. Trước khi viết code

1. Kiểm tra files/runtime hiện có; phân biệt code thực sự tồn tại với đường dẫn dự kiến trong tài liệu.
2. Xác định requirement, interface, fixture và T-ID bị ảnh hưởng; nêu kế hoạch ngắn cùng bằng chứng hoàn thành.
3. Trước khi tạo analyzer của một model version lần đầu, thực hiện freeze event của version đó. V1 dùng event/spec §19 hiện có. V2 phải pin `CEAV_M1_V2_SPEC.md`, `ENGINE_DESIGN_V2.md` và `VERIFICATION_PLAN_V2.md` với raw bytes/hash thực tế; freeze V1 không bao phủ V2.
4. Chọn giải pháp đơn giản trong scope. Các quyết định reversible về tên/file có thể tự xử lý; thay đổi game, thông tin, payoff hoặc phạm vi cân bằng phải được giải thích và version hóa trước khi dùng.

Các snapshot/manifest lịch sử là bất biến. Snapshot review hiện có không phải event implementation-start; không ghi lùi thời gian hoặc sửa lịch sử thành đã preregister.

## 3. Quy tắc khi sửa engine

- Giữ Fraction xuyên suốt phép tính và so sánh; decimal chỉ để hiển thị.
- Strategy nhận observation đã che thông tin; scoring nhận report/prediction. Ground truth chỉ phục vụ phân phối/evaluator.
- Dựng candidate prediction một lần; khi focal deviation, giữ nguyên toàn bộ peer tables và hành vi của peer.
- Kiểm tra đủ từng Judge và từng Z, giữ mọi tie và sáu action; đọc riêng quy tắc fixed/lambda=0 trước khi viết best response/search.
- Candidate payoff dùng strategy thật của candidate. Tối ưu của focal được trả riêng, không âm thầm thay candidate bằng optimum.
- Giữ math ở engine; CLI, server và UI gọi cùng interface. Schema/metadata phải thể hiện đúng scope và trạng thái run.
- Ưu tiên đường tính đơn giản đã đối chiếu oracle trước khi cache/tối ưu. Khi tối ưu, exact outputs, witnesses, ties và cache on/off phải khớp.

Chi tiết thuật toán nằm ở engine design đúng version; không sao chép một bản công thức riêng vào file hướng dẫn này hoặc frontend.

## 4. Quy tắc kiểm chứng và sửa lỗi

Với bug thuật toán, tạo regression phát hiện lỗi trước khi sửa; với module mới, chuẩn bị fixture/oracle độc lập trước acceptance. Expected không được sinh bằng chính hàm đang test. Khi test fail, chẩn đoán cả code lẫn fixture; chỉ đổi expected khi có derivation độc lập và ghi lý do.

Chạy checks phù hợp thay đổi, rồi các gates phụ thuộc bị ảnh hưởng theo verification plan đúng version. Giữ kết quả fail, log, config và witness tái lập. Mutation probes chạy trong bản copy tạm/test-only; không sửa production/golden để trình diễn failure.

Test runner phải xác nhận tests đã được discover và thực thi. Thiếu suite hoặc selected ID là unavailable/error; zero tests, skipped và not_run không tính là pass. Kiểm tra HTML bằng browser flows, không suy từ server HTTP200 hoặc unittest xanh.

Chỉ tuyên bố search exhaustive khi đã kiểm tra đủ phạm vi và T17 đạt; canceled/partial run không phải certificate. Hash đúng chứng minh identity của bytes, không chứng minh thuật toán đúng.

## 5. Files, artifacts và khả năng tái lập

- Giữ thay đổi tập trung; bảo toàn dữ liệu/kết quả và công việc không liên quan.
- Mỗi run có thư mục mới và pinned inputs/source/spec; output đã tồn tại phải được từ chối thay vì ghi đè.
- Phân biệt config semantic hash với raw file hash; timestamp/runtime không tham gia config hash.
- Lệnh trong docs phải được đánh dấu hiện có hoặc mục tiêu. README hướng dẫn chạy chỉ được bổ sung từ lệnh đã thực sự kiểm tra.
- Khi sửa contract triển khai, cập nhật đúng tài liệu sở hữu và mapping tests; giữ lịch sử revision của artifacts đã pin.

## 6. Báo cáo tiến độ và hoàn thành

Luôn phân biệt `SPECIFIED`, `IMPLEMENTED`, `VERIFIED` theo đúng module/phạm vi. Reference checker G1–G4 không đại diện analyzer tổng quát hoặc suite T01–T32.

Báo cáo ngắn gồm: thay đổi; lý do; tests/commands đã chạy và kết quả; evidence paths; phần còn thiếu. Giữ giới hạn pure-equilibrium và kết quả bất lợi cho cơ chế trong output.

V1 hoàn thành khi đủ GATE-0–GATE-5 trong `VERIFICATION_PLAN.md`. V2 chỉ hoàn thành khi đủ V2-GATE-0–V2-GATE-5 và toàn bộ V1 regression theo spec/verification plan V2, gồm HTML/API và browser acceptance. Không tự giảm phạm vi để hoàn thành sớm, hoặc thêm model ngoài phạm vi để tránh kết quả âm.
