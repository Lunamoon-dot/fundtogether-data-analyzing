# CEAV-M1 — Trạng thái triển khai

## Version 3 — Hybrid Reward với Verification Anchor

**Trạng thái hiện tại: `SPECIFIED`, `IMPLEMENTED` và `VERIFIED` trong phạm vi M1 local.**

[CEAV_M1_V3_ANCHOR_SPEC.md](CEAV_M1_V3_ANCHOR_SPEC.md) revision `verification-anchor-r2-closeout` định nghĩa model `ceav-m1-v3.0`: report được khóa trước khi audit ngẫu nhiên, verification signal `T` không được Judge biết trước, reward kết hợp RBTS peer score với anchor score và budget dùng worst-case cap. [ENGINE_DESIGN_V3_ANCHOR.md](ENGINE_DESIGN_V3_ANCHOR.md) và [VERIFICATION_PLAN_V3_ANCHOR.md](VERIFICATION_PLAN_V3_ANCHOR.md) là implementation contract/evidence plan; r2 được freeze trước các closeout changes và giữ parent r1.

Nghiệm thu r2: [report](results/v3-acceptance-closeout-r2/report.md) và [acceptance.json](results/v3-acceptance-closeout-r2/acceptance.json). Audit đạt 7/7 checks; all-suite đạt 90/90, V3-T01–V3-T12 đạt 12/12, V3-B01 đạt 34/34 bước và V3-M01–V3-M10 đều killed trên source hash `bab5d6f3b62aadcd375f87160f162c225d24ac5bb1fe86f22ca48a6ba6edc8d1`.

| Phần | Evidence V3 |
| --- | --- |
| Freeze/oracle | `spec_history/v3-anchor-r2-implementation-start-20261023T070915835165Z/`; parent r1 và oracle/fixture r2 được pin trước closeout changes |
| Distribution và boundary | V3-T01–T03; 128 potential states; strategy chỉ thấy `Z` hoặc `(Z,X_i)` |
| Accounting/best response | V3-T04–T06; peer/anchor/audit cost tách riêng; exact oracle; peer tables frozen; quy hồi V2 khi anchor bằng 0 |
| Pure search/budget | V3-T07–T08; đủ 432 branch candidates; cap không nhân xác suất audit |
| CLI/API/UI/sweep | V3-T09–T12; immutable artifacts, worker parity, mỗi valid point có exhaustive landscape và exact equilibrium metric ranges |
| Browser | `results/v3-browser-closeout-r2-02/`; 34/34 bước, equilibrium accuracy/UI-artifact parity, desktop/mobile |
| Mutation | `results/v3-mutations-closeout-r2/`; V3-M01–V3-M10 đều killed; production bytes unchanged |
| Full regression | `results/v3-all-tests-closeout-r2-final/`; 90/90, không fail/error/skipped/not_run; toàn bộ 18 browser scenarios pass |

Baseline synthetic vẫn bất lợi ở một phần mục tiêu: all-High đạt accuracy `1791/2000` nhưng không phải cân bằng; exhaustive search giữ Low equilibrium ở cả hai nhánh. Quét reward/audit sau đó tìm được preset experimental `configs/v3/anchor_dominant_q50.json`: equilibrium duy nhất dùng High cho A/B, Low cho C và đạt accuracy `1813/2000`. Xem [V3_PARAMETER_SWEEP_REPORT.md](V3_PARAMETER_SWEEP_REPORT.md). Engine đã có `cost_per_audit` và `expected_audit_cost=q*cost_per_audit`; preset để `0` vì chưa có số liệu chi phí ngoài đời. Robustness r2 giữ cả các điểm tụt về 70% và các điểm không có pure equilibrium.

## Version 3.1 — Robustness trên game V3 không đổi

**Trạng thái hiện tại: `SPECIFIED`, `IMPLEMENTED` và `VERIFIED` trong phạm vi M1 local.** Acceptance audit đã đọc test runner, browser ROB-B01, mutation ROB-M01–ROB-M06 và full 108-point study trên cùng source hash.

V3.1 không thêm tín hiệu, payoff, Judge hay authority mới. Analyzer mở rộng theo Cartesian grid gồm 6 policy × 18 uncertainty scenarios; mỗi point chạy exhaustive pure search 432 branch candidates. Gate dùng equilibrium xấu nhất và yêu cầu mọi scenario của policy đều đạt. Baseline public-Z và forced-all-High được ghi là reference, không bị gọi là equilibrium.

| Phần | Evidence đã kiểm chứng |
| --- | --- |
| Freeze, schema, independent oracle | `spec_history/v3.1-robustness-implementation-start-20261023T141156959593Z/`; ROB-T01–T02 |
| Worst-case gates, policy aggregation, Pareto, references | ROB-T03–T07; fixture expected độc lập |
| CLI/API/artifacts/runner | ROB-T08–T10; `results/v31-all-tests-final/` — 100/100 pass, không fail/error/skipped/not_run |
| Browser | `results/v31-browser-final-ROB-B01/` — 10/10 bước pass, desktop/mobile, giữ caveat latency/provenance |
| Mutation | `results/v31-mutations-final/` — ROB-M01–ROB-M06 đều killed trong isolated copies |
| Full study | `results/v31-robustness-study-release-02/` — 108/108 points, mỗi point 432 branch candidates, search hoàn tất |

Kết quả nghiên cứu không chọn được policy robust: cả 6 policy đều có ít nhất một uncertainty point vi phạm gate. Pareto frontier gồm `v3_r1_baseline`, `anchor_q50` và `anchor_q80`; `anchor_q80` có nhiều point pass nhất (6/18) nhưng vẫn vi phạm false-approval, false-rejection hoặc cash-cost gate ở các point khác. Đây là kết quả bất lợi được giữ nguyên, không phải bằng chứng V3.1 đã sẵn sàng production. [Acceptance audit](results/v31-acceptance-final/report.md) xác nhận toàn bộ gate, nhưng không biến assumption grid thành confidence interval và không mô hình hóa latency.

## Version 3.2 — Report-sensitive spot-checking

V3.2 là một game version mới, được freeze tại `spec_history/v3.2-report-sensitive-implementation-start-20261024T030000000000Z/`. Nó giữ 3 Judge, signal model, majority decision và pure search của V3.1 nhưng thay audit scalar `q` bằng `q0/q1`: mỗi Judge có audit riêng, xác suất audit phụ thuộc report của chính Judge. State support giảm từ 128 potential states của V3 xuống 64 state rows vì audit chỉ được áp dụng sau report, bằng kỳ vọng exact.

| Phần | Evidence V3.2 |
| --- | --- |
| Strict schema và boundary | V32-T01–T03; q0/q1 bắt buộc, scalar `audit_probability` bị từ chối, 64 states normalize |
| Accounting và report-sensitive incentive | V32-T04–T06; independent oracle, expected audit exposure, anchor theo `q_r`, peer tables frozen |
| Exhaustive pure search | V32-T07; đủ 432 branch candidates |
| Study và failure witnesses | V32-T08; finite policy grid, worst-equilibrium gates, decomposition theo failure type |
| CLI/API provenance | V32-T09–T10; run pin spec/freeze, API validation, registry discoverability |

Acceptance runner V3.2 đã pass `10/10`: [results/v32-tests-final-02/test_results.json](results/v32-tests-final-02/test_results.json). Fixture study có ba policy ở một uncertainty point: symmetric `q0=q1=1/2` đạt accuracy `1813/2000`, false approval `51/500`; report-1 emphasis `q0=1/4,q1=3/4` đạt accuracy `7633/10000`, false approval `2237/5000`; report-0 emphasis `q0=3/4,q1=1/4` đạt accuracy `96/125`, false approval `1/250` nhưng false rejection `23/50`. Cả ba đều qua gate rộng của fixture; trade-off report-0 được giữ nguyên thay vì gọi là cải thiện tổng quát. Study cuối: [report](results/v32-report-sensitive-final-02/report.md) và [JSON](results/v32-report-sensitive-final-02/report_sensitive.json). Đây là kết quả của synthetic/assumption fixture, chưa phải dữ liệu Judge ngoài đời và chưa phải production readiness.

## Version 3.3 — IPW audit reward

**Trạng thái:** `SPECIFIED` + `IMPLEMENTED` + `VERIFIED` trong phạm vi local verification plan. Engine/CLI/API/UI và browser acceptance đã được kiểm tra trên source pin; không phải production readiness.

V3.3 được freeze tại `spec_history/v3.3-ipw-implementation-start-20261024T000000000000Z/`. Nó thay đổi payoff anchor, không sửa nghĩa V3.2: với `q0,q1 > 0`, expected anchor reward trở thành `mu * P(T=r | observation)`; cap dùng `3f + 6lambda + 3mu/q_min`; output thêm second moment, variance, covariance, payment cap và decomposition exact của utility deviation.

Evidence closeout: IPW-T01–T13 `13/13`; IPW-B01 UI/worker/artifact parity pass; IPW-M01–M10 `10/10` killed trong isolated copies; full study `54/54` points, mỗi point `432/432` branch candidates; V1 regression `47/47`, V2 regression `15/15`, V3.3 regression `13/13`, full suite `123/123` với zero fail/error/skipped/not_run. Artifact study: [report](results/v33-ipw-full-20261024T052707/report.md), [public exact projection](results/v33-ipw-full-20261024T052707/ipw_public.json), [point CSV](results/v33-ipw-full-20261024T052707/ipw_points.csv), [closeout report](results/v33-closeout-final-20261024T084030/report.md). File `ipw.json` gốc dài 117,018,796 bytes nên không push như file thường lên GitHub; `ipw_public.json` giữ exact policy/point evidence và hash của file gốc để kiểm tra độc lập kết luận `0/18`. Cả ba policy đều `0/18` robust trong assumption grid; đây là kết quả nghiên cứu bất lợi, không phải lỗi analyzer. Sáu failure lịch sử của run `117 pass / 6 fail` là T32, V2-T14, V2-T15, CAL-T07, CAL-T08 và INC-T08 do evidence browser/regression stale; chúng đã được regenerate/pin lại và full suite mới pass. Không gọi kết quả này là dữ liệu Judge thật hoặc production readiness.

## Version 2.2 — Incentive Diagnostics

**Trạng thái hiện tại: `SPECIFIED`, `IMPLEMENTED` và targeted verification; chưa công bố full `VERIFIED` release.**

V2.2 giữ model `ceav-m1-v2.0` và RBTS hiện có. Feature thêm exact decomposition theo từng `Judge × Z`, conditional lambda threshold, report-utilization gap, budget feasibility và exhaustive pure-equilibrium landscape tại từng điểm sweep.

Nguồn chuẩn: [spec](CEAV_M1_V2_2_INCENTIVE_SPEC.md), [engine design](ENGINE_DESIGN_V2_2_INCENTIVES.md), [verification plan](VERIFICATION_PLAN_V2_2_INCENTIVES.md), [hướng dẫn](HUONG_DAN_CHAN_DOAN_DONG_LUC_V2_2.md).

| Phần | Evidence hiện tại |
| --- | --- |
| Freeze/fixture | `spec_history/v2.2-incentives-implementation-start-20261022T2025258297100Z/`; docs và INC-F01 được pin trước production module |
| Exact decomposition | INC-T01–INC-T03; bốn High action, `V_L/V_H/V_H_dep`, net incentive, threshold và hierarchical status |
| Equilibrium landscape | INC-T04–INC-T05; retained IDs giữ nguyên, 432 candidates mỗi valid point, G1 coexistence và heterogeneous Low-only |
| CLI/API/artifacts | INC-T06–INC-T07; JSON/CSV, no-overwrite, feature freeze, worker/history/direct parity |
| Browser | `results/v22-browser-INC-B01-implementation-01/`; 13/13 bước, desktop/mobile, không JavaScript error |
| Targeted suite | `results/v22-incentive-tests-implementation-01/`; INC-T01–INC-T08 đạt 8/8 |

INC-GATE-0–INC-GATE-4 có evidence targeted. INC-GATE-5 yêu cầu chạy lại toàn bộ V1/V2/V2.1 regression và acceptance audit trên current source trước khi gắn nhãn full `VERIFIED` hoặc tạo release tag.

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
