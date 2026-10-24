# CEAV-M1

**Phiên bản ứng dụng chạy được hiện tại:** Version 3.3 · IPW audit reward `ceav-m1-v3.3`; V3.2 vẫn giữ nguyên làm baseline. V3.3 đã pass toàn bộ gate local trên source pin: engine/CLI/API/UI, IPW-B01 parity, 10 mutation probes, 54-point study và full suite 123/123. Đây là verification của mô hình synthetic/assumption trong workspace, không phải production readiness.

**Version 2.2 diagnostics:** `SPECIFIED`, `IMPLEMENTED` và đã qua targeted verification INC-T01–INC-T08 cùng INC-B01. Trạng thái full release còn chờ toàn bộ regression/evidence INC-GATE-5. V2.1, V2.0 và V1 giữ trạng thái nghiệm thu trước đó trên source đã pin của từng release.

**Version 3:** `SPECIFIED`, `IMPLEMENTED` và `VERIFIED` local. Report khóa trước khi audit; `T` chỉ xuất hiện sau đó và chỉ tham gia reward. V3 không dùng `Y` làm reward oracle và không cho Judge thấy `A/T`. Nghiệm thu r2 tại [report V3](results/v3-acceptance-closeout-r2/report.md) và [acceptance.json](results/v3-acceptance-closeout-r2/acceptance.json).

**Version 3.3:** `VERIFIED` trong phạm vi local verification plan. IPW-T01–T13 pass 13/13; IPW-B01 pass với UI/worker/artifact parity; IPW-M01–M10 pass 10/10; full 54-point study có 54/54 point, mỗi point 432/432 branch candidates; full suite pass 123/123. Ba policy đều `0/18` robust: đây là kết quả nghiên cứu bất lợi được giữ nguyên, không phải lỗi analyzer. Closeout report và evidence đã pin tại [V3.3 closeout](results/v33-closeout-final-20261024T084030/report.md). V3.3 thử IPW cho anchor reward khi `q0 != q1`, giữ V3.2 làm baseline, bắt buộc `q0,q1 > 0`, dùng cap `3f + 6lambda + 3mu/q_min` và đo variance/covariance. Đây vẫn là synthetic/assumption study; không chứng minh Judge ngoài đời, collusion/Sybil resistance hay production readiness. Xem [spec V3.3](CEAV_M1_V3_3_IPW_SPEC.md), [engine design](ENGINE_DESIGN_V3_3_IPW.md) và [verification plan](VERIFICATION_PLAN_V3_3_IPW.md).

## CEAV-M1 research review package (V3–V6)

Phần dưới đây là research synthesis và external-review packaging, tách khỏi
trạng thái ứng dụng V3.3 ở trên. Không có V7, production integration hay thay
đổi historical certificates trong package này.

- [Research Brief](CEAV_M1_EXTERNAL_RESEARCH_BRIEF.md): motivation, T3–T5 và câu hỏi cho reviewer.
- [Manuscript v0.3](CEAV_M1_MANUSCRIPT_V0_3.md): bản sửa F1–F5, assumptions tự đầy đủ, definitions, proofs và claim-to-evidence map; v0.2 được giữ làm lịch sử.
- [Manuscript correction closeout](CEAV_M1_MANUSCRIPT_V0_3_CORRECTION_CLOSEOUT.md): mapping corrections, evidence và quyết định external-review readiness.
- [Dual Strategic Boundary Report](CEAV_M1_DUAL_STRATEGIC_BOUNDARY_REPORT.md): frozen F51-02 witness và exact external-interest boundary.
- [Review package README](review-package/README.md): clean reproduction, immutable certificates, independent verification code và generated figures.

Các kết quả trung tâm đã được giữ nguyên:

- T3 net effort benefit: `7/500`, với `c=1/20` và `Delta=M_H-M_L=2/25`.
- T4 local All-H01 intervals: Selective `(-70/633, 175/1102)`; Uniform `(-218750/2070709, 218750/1365587)`.
- T5 tại `b=1/10`: bốn pure equilibria và ba bad-equilibrium witnesses; quyết định global là `STRATEGIC_FAILURE` trong strategy class đã khai báo.
- Frozen dual certificate SHA-256: `fde3ad4745b37e270469aaec2692a51c83cbcf5db7fcb0a16938296a6e25b7d5`.

Reviewer có thể chạy lại từ thư mục sạch:

```powershell
Push-Location review-package
python -X utf8 -m verification.manuscript_editorial_audit
python -X utf8 -m verification.independent_t3_t5_review
python -X utf8 -m verification.review_summary
python -X utf8 -m unittest tests.test_dual_boundary -v
python -X utf8 -m verification.manuscript_correction_checks
Pop-Location
```

Đây là exact finite research evidence với synthetic assumptions; chưa phải
external peer review, submission readiness hoặc production readiness.

Phòng thí nghiệm local để phân tích incentive và cân bằng thuần của game một claim, ba Judge. Python 3.12+; ứng dụng chỉ dùng standard library và HTML/CSS/JavaScript thuần. Không cần ví, database, Node hoặc Internet để chạy ứng dụng.

## Chạy giao diện

Từ `C:\Users\dell\Desktop\fundtogether_data_analyzing`:

```powershell
python -m ceav_m1 serve --port 8765
```

Mở [http://127.0.0.1:8765](http://127.0.0.1:8765). Form có V3.3 với hai trường audit `q0/q1` theo report, mode IPW được khóa bởi model; reward hiển thị `f`, `lambda_peer` và `anchor_weight` riêng. Tab **V3.3 IPW** chạy acceptance/full study đã đóng. Màn hình **Dữ liệu** vẫn tạo config V2; **Chẩn đoán động lực** vẫn chạy V2.2. Chỉnh tham số dạng chuỗi hữu tỉ, ví dụ `1/20` hoặc `0.05`. Chi tiết và download của mỗi run nằm dưới kết quả.

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
python -m ceav_m1 report-sensitive --study tests/fixtures/v3_2_report_sensitive_study.json --out results/my-v3.2-report-sensitive
python -m ceav_m1 tests --suite v3_2 --out results/my-v3.2-tests
python -m ceav_m1 ipw --study tests/fixtures/v3_3_ipw_study.json --out results/my-v3.3-ipw
python -m ceav_m1 tests --suite v3_3 --out results/my-v3.3-tests
python -m ceav_m1 tests --suite all --out results/my-all-tests
python -m ceav_m1 tests --suite selected --test-id T01 --test-id V2-T11 --out results/my-selected
```

`configs/sweep.json` giải `base_config` tương đối với file sweep. Output tương đối với cwd. So sánh yêu cầu `F=f+2*lambda`; cùng trần không có nghĩa cùng reward thực chi. Sweep V1/V2 giữ profile cố định và chỉ phân tích candidate. Sweep V3 giữ candidate metrics, exhaustive pure-equilibrium landscape và khoảng min/max exact của decision/accounting metrics tại mọi cân bằng thuần; hàng invalid vẫn được giữ.

V3.1 dùng study đã khai báo trong [`configs/v3/robustness_v3_1.json`](configs/v3/robustness_v3_1.json): 6 policy × 18 uncertainty scenarios = 108 points, mỗi point kiểm đủ 432 branch candidates. Policy chỉ bền vững khi mọi scenario qua gate theo equilibrium xấu nhất. Kết quả chính là false approval, wrongly paid value, false rejection và cash review cost; accuracy chỉ là diagnostic. Grid không nội suy, các range là provenance assumptions chứ không phải confidence intervals, và latency chưa được mô hình hóa.

V3.2 dùng [`CEAV_M1_V3_2_REPORT_SENSITIVE_SPEC.md`](CEAV_M1_V3_2_REPORT_SENSITIVE_SPEC.md): spot-check theo report `q0/q1` và audit riêng cho từng Judge. Study finite giữ 3 Judge, majority decision và exhaustive 432 branch candidates; output thêm expected audit exposure, failure witness và decomposition `effort_cost/report_sensitive_anchor/peer_score`. Fixture mặc định so sánh symmetric, report-1 emphasis và report-0 emphasis; report-0 giảm false approval nhưng làm false rejection tăng mạnh trong run synthetic. Đây là mô hình incentive mới, không phải claim về nguồn audit thực tế.


V3.3 dùng [`tests/fixtures/v3_3_ipw_study.json`](tests/fixtures/v3_3_ipw_study.json): 3 policy × 18 uncertainty points = 54 points, mỗi point exhaustive 432 branch candidates. Kết quả run hiện tại: cả ba policy đều `0/18` robust; mọi point đều fail ít nhất cash-review gate, một phần fail false-approval/false-rejection. Bảng exact point-level đã push trong [`ipw_public.json`](results/v33-ipw-full-20261024T052707/ipw_public.json), cùng [`ipw_points.csv`](results/v33-ipw-full-20261024T052707/ipw_points.csv), failure map và manifest. File `ipw.json` đầy đủ có nested equilibrium diagnostics và dài 116,954,127 bytes nên vượt giới hạn file thường của GitHub; `ipw_public.json` giữ nguyên policy summary, 54 point rows, exact metrics, gate và SHA-256 của file gốc. Ở một equilibrium đại diện, expected reward tổng giữ nguyên `107193/25000`, nhưng variance anchor tăng từ khoảng `3.32` ở q đối xứng lên khoảng `6.72` khi q1 được nhấn mạnh; max realized payment tăng từ `19/5` lên `38/5`. V3.2 baseline cùng budget `24` vẫn là reference rerun required, không được suy diễn từ kết quả V3.3.

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
- [CEAV_M1_V3_2_REPORT_SENSITIVE_SPEC.md](CEAV_M1_V3_2_REPORT_SENSITIVE_SPEC.md), [ENGINE_DESIGN_V3_2_REPORT_SENSITIVE.md](ENGINE_DESIGN_V3_2_REPORT_SENSITIVE.md) và [VERIFICATION_PLAN_V3_2_REPORT_SENSITIVE.md](VERIFICATION_PLAN_V3_2_REPORT_SENSITIVE.md): q0/q1 report-sensitive spot-checking, per-Judge audit accounting và failure witnesses.
- [CEAV_M1_V3_3_IPW_SPEC.md](CEAV_M1_V3_3_IPW_SPEC.md), [ENGINE_DESIGN_V3_3_IPW.md](ENGINE_DESIGN_V3_3_IPW.md) và [VERIFICATION_PLAN_V3_3_IPW.md](VERIFICATION_PLAN_V3_3_IPW.md): IPW anchor reward, payment-cap/variance analysis và causal utility decomposition; implementation/evidence targeted nằm ở phần V3.3 bên trên.
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
