# CEAV-M1 V6.0 RAVE — Kết quả Phase 0–1

**Kết luận cuối: NO-GO cho Phase 2 trên tập candidate/policy đã khai báo.**

Đã hoàn thành formal specification, source review, exact oracle độc lập,
feasibility certificates, targeted strategic counterexamples và kiểm chứng.
Không triển khai full engine/API/UI/blockchain hoặc Phase 2/3.

Selective audit giảm decision loss trong mô hình báo cáo ngoại sinh. Tuy nhiên,
cả bốn candidate qua Gate B đều có một pure Nash equilibrium vi phạm gate.
Một phản ví dụ cân bằng xấu đủ bác bỏ yêu cầu “mọi pure equilibrium đều đạt”;
không cần search toàn bộ equilibrium để kết luận âm này.

## Assumptions và phạm vi

Baseline checkout khớp `258d2178cfe11f67d8570484c49a9c91bd8c325e`.
Branch công việc: `research/v6-rave-phase01`. Chỉ thêm files V6; giữ nguyên
historical specs/results và các file chưa commit có sẵn.

Giữ ba fixtures F51-01, F51-02, V3-HET và primitive signals/costs V3/V5.
T có sensitivity/specificity 9/10, độc lập Z/X khi biết Y. Primary b=0;
diagnostic b=1/10 được lưu riêng và không dùng thay kết quả primary.

Các lựa chọn V6 được công bố trước checker: C_FA=2, C_FR=1, threshold=2/3,
mu=1, B=6, kappa=1/4, payout value=1, operating cost=0, exposure cap=1/2.
f=0 cho F51-01/02; f=1/10 cho V3-HET. Đây là assumptions tổng hợp, không phải
ước lượng tiền hoặc chất lượng auditor thực tế. Không tune sau output.

Policy Bayesian được calibrate theo all-H01 rồi giữ cố định khi Judge deviation.
Y chỉ nằm trong generator/evaluator; q chỉ nhận Z và locked reports. T chỉ dùng
sau audit selection và trước terminal release/reject. Audit được tính một lần
cho claim, reward reserve không nhân expected exposure để giảm cap.

## Trả lời 10 câu hỏi của brief

### 1. Cùng audit exposure, selective có giảm decision loss không?

**Có dưới báo cáo ngoại sinh đúng calibration.** Ví dụ F51-02/Q1-zero:

| Metric | Selective Q1-zero | Uniform tối ưu tại cùng exposure |
|---|---:|---:|
| Audit exposure | 12/25 | 12/25 |
| Expected decision loss | 219/3125 = 0.07008 | 17151/156250 = 0.1097664 |
| Expected reviewer payout | 522/625 | 666/625 |
| Audit cost | 3/25 | 3/25 |
| Total cash | 597/625 = 0.9552 | 741/625 = 1.1856 |
| Reward reserve | 3 | 3 |

Loss giảm `6201/156250`; cash giảm `144/625`. Cả hai dùng cùng g0/g1, T,
reward parameters và target weights. Uniform không bị chọn yếu: với fixed
calibrated reports, Bayes rules tối ưu từng state và loss không tăng theo q;
do đó q=12/25 tối ưu trong họ uniform có exposure tối đa 12/25.
Đây không phải tối ưu uniform trong game chiến lược.

Trong 12 so sánh chính, chỉ bốn trường hợp đạt rule candidate discovery:
F51-01/Q1-zero, F51-01/Q2-z1, F51-02/Q1-zero, F51-02/Q2-z0. V3-HET không có
candidate; các trường hợp fail exposure/benefit/cash được giữ nguyên.

### 2. Lợi ích đến từ chọn claim hay đổi decision rule?

Hai hiệu ứng được tách. Trên F51-02, no-audit majority có loss `39/250`,
no-audit Bayes có loss `183/1250`: phần cải thiện aggregation là `6/625`.
Selectivity so với matched uniform giữ cùng Bayes g0/g1, nên chênh lệch
`6201/156250` ở trên đến từ allocation, không thể gán cho đổi majority rule.

Trên F51-01, aggregation benefit lớn hơn: `39/250 - 6/125 = 27/250`.
Không cộng lẫn hai lợi ích này hoặc dùng truthful optimization làm incentive guarantee.

### 3. T noisy thì khi nào audit đổi quyết định?

Posterior odds nhân 9 khi T=1, nhân 1/9 khi T=0. Decision đổi khi posterior
đi qua threshold 2/3, không phải mọi lần T khác majority.

Ví dụ F51-02, Z=0/reports=110: posterior `12/19`, g0=reject; T=1 cho
posterior `108/115`, nên release. Với Z=0/reports=111, posterior `192/199`;
ngay cả T=0 vẫn vượt threshold, nên g1=(release,release). T được phép bị bỏ qua.
VOI từng observable state được lưu exact trong certificate; mọi VOI đều không âm
dưới đúng calibration, trước chi phí audit/payment.

### 4. Judge có thao túng q(Z,r) không?

**Có cả audit seeking và audit avoidance trong witnesses.**

- Audit seeking: F51-02/Q1-zero/all-copy-Z, một Judge đổi Low report từ Z
  sang 1-Z làm audit rate nhánh tăng 0→1 và utility tăng `17/50`.
- Audit avoidance: F51-01/Q1-zero/all-H01, tại Z=0 Judge A đổi sang L0:
  exposure nhánh giảm `12/25→39/100`, utility tăng `421/5000`; phần tăng reward
  là `171/5000`, phần tiết kiệm effort là `1/20`. Peers/policy vẫn cố định.

Các ví dụ dùng b=0. Diagnostic b=1/10 cũng được lưu riêng; không gọi đó là
chứng nhận chống bribery hoặc collusion.

### 5. All-copy-Z còn là equilibrium hoặc failure mode không?

All-copy-Z không là neutral equilibrium của Q1-zero vì có profitable dissent.
Nhưng profile này vẫn có audit exposure bằng 0 và giữ unanimous errors:
F51-02 preliminary/final FA=FR=3/10, wrong payout=3/20.

Uniform matched baseline giữ copy-Z như một NE witness ở các fixtures đối xứng.
Loại được đúng profile copy-Z ở Q1-zero không loại được cân bằng xấu khác:
đã có asymmetric Low hoặc mixed-effort equilibria ở bảng counterexamples bên dưới.

### 6. Report-dependent audit có gây reporting bias không?

**Có.** Một Low dissent không dựa trên X vẫn có thể có giá trị tư nhân vì làm
audit xảy ra. Với peers khác nhau, Judge cũng có thể giảm effort và audit rate
để tăng utility. Reward được tối ưu theo cơ chế, không đồng nghĩa truthful report.
All-H01 có maximum regret dương trong cả bốn candidate được phát hiện.

### 7. Lợi ích còn khi tính cash và incentives không?

So với matched uniform dưới exogenous H01, F51-02/Q1-zero giảm cả loss và cash.
Economic diagnostic loss+cash giảm `42201/156250` ở cùng exposure. Tuy nhiên,
đây không phải chứng minh audit tối ưu khi được chọn cả mức chi: no-audit Bayes
có cash=0 nhưng loss cao hơn, và giả định exogenous H01 đó không phải equilibrium.
Không suy ra hiệu quả kinh tế toàn cục từ so sánh tại fixed exposure.

Khi xét incentives, candidate có NE khiến audit exposure thành 1 thay vì 12/25,
vi phạm cap. Q2 có thể giữ exposure nhưng cho phép bad unaudited Low reports.
Vì vậy không có chứng nhận economic/quality viability dưới mọi pure equilibrium.

### 8. Candidate nào đáng mở strategic screening?

Gate B phát hiện bốn candidate, nhưng targeted proofs đã bác bỏ điều kiện
robustness cần thiết của cả bốn. Không còn candidate trong tập này cần search
lớn chỉ để chứng minh lại failure đã biết.

### 9. Rủi ro trọng yếu chưa model hóa?

Auditor provenance/capture, correlated error, estimation uncertainty và evidence
do Creator chiến lược cung cấp; participation/outside option; latency/liveness;
mixed/coalition/history strategies; equilibrium selection; và fixed-point
calibration theo equilibrium đều chưa model hóa. Đây là mô hình tổng hợp hữu hạn.

Stress calibration đã được khai báo trước: giả định copy-Z calibration nhưng
đánh giá actual H01, off-support dùng public fallback. Trên F51-02/Q1-zero,
loss tăng từ `219/3125` lên `153/500`; Q2-z0 từ `633/6250` lên `77/200`.
Đây là diagnostic misspecification, không phải confidence interval hoặc robustness sweep.

### 10. GO hay NO-GO cho Phase 2?

**NO-GO trên tập candidate/policy đã khai báo**, với exact bad-equilibrium proofs:

| Fixture/policy | Z=0 actions | Z=1 actions | Max regret | Gate bị vi phạm |
|---|---|---|---:|---|
| F51-01/Q1-zero | L0,L0,L1 | L1,L1,L0 | 0 | exposure=1 > 1/2 |
| F51-01/Q2-z1 | L1,L1,L1 | L1,L1,L1 | 0 | FA=1 > 1/5; wrong payout=1/2 > 3/20 |
| F51-02/Q1-zero | L0,L1,H01 | L0,L1,H01 | 0 | exposure=1 > 1/2 |
| F51-02/Q2-z0 | H01,H01,H01 | L0,L0,L0 | 0 | FR=2321/3125 > 1/4 |

Từng witness được kiểm tra đủ 36 unilateral options: 6 actions × 3 Judges ×
2 Z, bằng checker và oracle độc lập. Không có profitable deviation; giữ mọi tie.

Hai negative profiles bổ sung của F51-02 được dẫn xuất sau candidate discovery,
rồi freeze declaration/tests/inputs trước certificate writer. Đó là
**post-discovery exact counterexamples**, không gọi là preregistered discovery.
Primary spec/config/decision rules/gates và artifacts cũ không thay đổi.

`GO_candidate_discovery_only` trong primary certificate là kết quả Gate B;
negative closeout này thay thế **khuyến nghị mở screening**, không xóa lợi ích
decision-theoretic đã chứng minh. Không có kết luận bất khả thi cho mọi họ RAVE,
không có full equilibrium count/worst-case certificate hoặc mixed-equilibrium claim.

## Trạng thái H6 và gates

| Mục | Kết luận giới hạn |
|---|---|
| H6-1 | Có giá trị decision information trong các states được xác định; trước chi phí, đúng calibration. |
| H6-2 | Selective allocation thắng optimized uniform trong một số so sánh exogenous cùng exposure. |
| H6-3 | Bị bác bỏ cho bốn candidate được phát hiện: mỗi policy có bad pure NE. |
| H6-4 | Không có robust improving candidate được chứng nhận trong tập discovery này. |
| Gate A | Hoàn thành formal model, proof và manipulation counterexamples. |
| Gate B | Positive candidate discovery dưới exogenous H01. |
| Gate C/D | Điều kiện cần cho các candidate bị refute bằng witnesses; không có acceptance exhaustive. |

## Evidence và khả năng tái lập

- Primary spec/evidence contract: `CEAV_M1_V6_RAVE_SPEC.md`, `CEAV_M1_V6_FEASIBILITY.md`.
- Primary sources: `references/V6_RAVE_PRIMARY_SOURCES.md`; không có novelty claim.
- Primary freeze: `spec_history/v6.0-rave-pre-checker-freeze-20261024T020618028417Z/`.
- Primary immutable run: `results/v6-rave-phase1-20261024T021148403371Z/`.
- Negative addendum: `CEAV_M1_V6_PHASE1_COUNTEREXAMPLES.md`.
- Negative freeze: `spec_history/v6.0-rave-negative-witness-check-20261024T021827535728Z/`.
- Final negative certificates: `negative-certificates/` cạnh báo cáo này.
- Independent recheck: `independent-recheck.json`, với script `recheck_certificate.py`.
- Final tests: `v6-tests-normal.log`, `v6-tests-optimized.log`, `verification-summary.json`.
- V4/V5 regression và mutations: `results/v6-verification-20261024T021221745773Z/`.

Kết quả kiểm chứng: **24/24 V6 tests** ở chế độ thường và -O, zero skipped;
**60/60 V4/V5 regression tests**; **15/15 mutation probes** bị bắt bằng assertion,
không tính import error/zero tests là kill. Independent oracle recheck có
**40.202 checks**, **240 targeted profile records**, **8.640 deviation records**.
Bốn negative witnesses bổ sung có **144 independent deviation checks**.

Primary và negative certificate đều được replay từ chính pinned input snapshots;
certificate bytes phải khớp nguyên bản. Historical identity check đã xác nhận
38 hashes liên quan V3.3–V5.1, không thay đổi artifacts đó.

Hai review findings đã sửa bằng RED→GREEN: run bundle thiếu nested freeze
snapshots (R04); UNRESOLVED phải truyền qua status/Gate C/D/report (R05/R06).
Mutation còn phát hiện test neutral utility không bắt decision recalibration;
R01 bổ sung oracle comparison với external b và giữ frozen policy.

Lệnh đã thực sự chạy từ workspace root:

```powershell
python -m unittest tests.test_v6_feasibility tests.test_v6_regressions tests.test_v6_mutations tests.test_v6_stop_certificates -v
python -O -m unittest tests.test_v6_feasibility tests.test_v6_regressions tests.test_v6_mutations tests.test_v6_stop_certificates -v
python results/v6-closeout-20261024T021405861852Z/recheck_certificate.py --run results/v6-rave-phase1-20261024T021148403371Z --out NEW_RECHECK.json
python results/v6-rave-phase1-20261024T021148403371Z/inputs/verification/feasibility_v6.py --out NEW_PRIMARY_REPLAY_DIRECTORY
python results/v6-closeout-20261024T021405861852Z/negative-certificates/inputs/verification/v6_phase1_stop.py --out NEW_NEGATIVE_REPLAY_DIRECTORY
```

`NEW_*` là tên output mới người chạy phải chọn; writer từ chối output tồn tại.
Không có kết luận HTML/browser/production acceptance; tất cả evidence ở đây là
offline finite-model research. Dừng tại Phase 1, không tự mở V6.1/V6.2.
