# CEAV-M1 — Kế hoạch kiểm chứng implementation

**Revision:** `verification-plan-r1` · **Ngày:** 22/10/2026  
**Áp dụng:** `ceav-m1-v1.0`, spec `math-proof-r2`, design `engine-design-r1`.  
**Trạng thái:** kế hoạch nghiệm thu; bộ tests/oracle/runner được mô tả dưới đây cần xây.

## 1. Điều cần chứng minh bằng evidence

[CEAV_M1_SPEC.md](CEAV_M1_SPEC.md) quy định game và T01–T32. [ENGINE_DESIGN.md](ENGINE_DESIGN.md) quy định interface/thuật toán. Tài liệu này cụ thể hóa fixture, oracle độc lập, assertion và gate cho implementation.

Phân biệt ba mức: mệnh đề toán đúng trong mô hình; code thực hiện đúng thuật toán trên phạm vi đã kiểm tra; kết quả mô hình có ý nghĩa ngoài thực tế. Test ở đây phục vụ mức thứ hai. Một tập tests hữu hạn không phải chứng minh hình thức cho mọi đầu vào hữu tỉ, và không chứng minh con người sẽ chọn cân bằng nào.

Pass nghĩa là assertion đã thực thi trên source/config được ghi nhận. `not_run`, `unavailable`, `skipped`, lỗi runner và mất worker đều không phải pass. Các kết quả bất lợi cho RBTS phải được giữ trong fixture/report.

## 2. Bằng chứng hiện có và phần cần xây

| Artifact | Phạm vi hiện có | Giới hạn |
| --- | --- | --- |
| [verify_reference.py](verification/verify_reference.py) | Fraction checks cho G1–G4, named symmetric profiles, P2 và vài edge cases | Không có sáu action tổng quát, asymmetric cost engine, exhaustive search, API/HTML |
| [reference_results.json](verification/reference_results.json) | Exact/decimal output để đối chiếu G1–G4 | Dữ liệu sinh bởi checker; không độc lập với mọi lỗi của checker |
| Spec §9.4 và §11 | P1–P5, giá trị chuẩn và lập luận | Không thay bằng chứng implementation/certificate verifier |

Checker hiện tại suy effort H từ policy `X`, và chủ yếu tính best response focal A trong named symmetric profiles. Nó không đủ để kiểm tra H00/H11 hoặc profile bất đối xứng. Không mở rộng kết luận của checker bằng cách đổi nhãn output.

Khi triển khai, thêm test oracle độc lập trong `tests/oracle.py`, fixtures trong `tests/fixtures/`, các module `tests/test_*.py`, registry `tests/registry.json`, evidence trong từng test run ở `results/`. Đây là đường dẫn dự kiến, không phải artifact đã có.

Registry ánh xạ mỗi T-ID tới unittest IDs và browser scenario IDs; có thể có nhiều tests cho một T-ID. Một T-ID chỉ đạt acceptance khi đủ các loại evidence yêu cầu của nó. Test discovery trả 0 tests phải fail runner/gate.

## 3. Bốn lớp kiểm chứng

### 3.1. Fixture tính trực tiếp

Lưu input và expected exact values trước khi nối production engine. Mỗi fixture có `fixture_id`, model/spec revision, input, đại lượng và conditioning, derivation/source, người hoặc script đã đối chiếu và hash nếu có file nguồn.

Expected values không được lấy bằng cách gọi chính hàm đang assert. Snapshot update phải có lý do toán/contract và phép tính độc lập; test đang fail không tự cho phép thay expected. Những giá trị lấy từ checker phải mang provenance đó, không gắn nhãn hand-derived.

### 3.2. Oracle độc lập với production

Oracle nhận primitive config/profile, tự tạo trạng thái và prediction candidate, tự tính utility. Nó không import `ceav_m1.model/scoring/strategies/evaluate/best_response/equilibria`, không dùng production conditional-group helper hoặc production candidate tables làm expected.

Dùng biểu diễn khác ở nơi hữu ích: trực tiếp `Q(p,r)=1-(p-r)^2` cho r nhị phân; tính xác suất bằng vòng lặp explicit; duyệt toàn bộ sáu action của focal rồi tính payoff trên trạng thái. Own prediction tối ưu vẫn dùng P2, được kiểm tra đại số riêng. Không dùng p-grid để giả làm nghiệm exact.

Oracle và production cùng dựa trên mô hình toán nên vẫn có thể chia sẻ hiểu nhầm; fixture tính tay và mutation probes giảm rủi ro đó. Không mô tả hai bản code tương đồng là hai bằng chứng hoàn toàn độc lập.

### 3.3. Invariants và biến đổi đầu vào

Kiểm tra các tính chất tại §6 trên nhiều cấu hình exact. So sánh cả giá trị, action ties, prediction semantics và witness; chỉ so boolean equilibrium hoặc số lượng nghiệm là chưa đủ.

### 3.4. Mutation probes có mục tiêu

Cố ý tạo những biến thể sai ở §8 trong bản copy tạm/test-only implementation. Chạy test tương ứng, xác nhận failure do assertion liên quan. Baseline sạch phải pass trước; syntax/import error không được tính là đã bắt lỗi thuật toán. Giữ production và golden fixtures nguyên vẹn.

## 4. Thuật toán của oracle và certificate verifier

### 4.1. Brute-force unilateral deviation theo nhánh

```text
independently build state rows and candidate reports/predictions
for each focal i and z:
    save immutable peer report/prediction tables
    for each of six focal actions:
        build focal observation partition for this action
        derive focal optimal p for each observation by weighted peer report
        enumerate states directly with frozen peer tables
        compute conditional utility of the whole trial action
    compare all six trial utilities; keep all maximizers
    compare best utility against direct candidate utility
```

Production tối ưu report theo từng observation; oracle duyệt sáu maps rồi cộng utility trực tiếp. Hai đường phải khớp low/high maxima, tất cả optimal report maps, effort ties và regret. Khi prediction tự do ở fixed/lambda=0, so theo family semantics, không so một representative p như nghiệm duy nhất.

Oracle phải tối ưu prediction của focal ở mọi trial, kể cả trial có report map giống candidate. Peer tables luôn giữ candidate ban đầu. Nếu test cho nhập manual p, candidate payoff dùng đúng p đó; oracle trial dùng optimum và phải thấy prediction-only deviation khi có.

### 4.2. Direct full-profile enumeration cho T17

Ở một config G1 hợp lệ, dựng 36 maps mỗi Judge và duyệt cả `36^3=46,656` full profiles. Với mỗi profile, dựng prediction và utility độc lập, thử đủ 36 focal effort/report maps cho từng Judge trên toàn không gian 32 states; prediction của focal tối ưu theo mỗi reachable observation. Kiểm tra ex ante utility của các strategy đầy đủ.

Đường này không gọi branch equilibrium search hoặc ghép Cartesian product của hai danh sách cân bằng. So sánh **tập full profile IDs và prediction semantics**, không chỉ counts, với product từ engine. Kiểm tra ex ante ở đây hợp lệ vì thử mọi map cho phép thay riêng từng z; nó khác với chỉ kiểm tra dấu Delta trung bình của hai chính sách all-H/all-L.

Đây là test chậm bắt buộc ở GATE-3. Được cache row payoffs/observation moments có key đầy đủ để tránh lặp Fraction, nhưng không cache boolean equilibrium từ branch solver hoặc dùng một giả định đang được kiểm chứng. Lưu tổng profiles đã duyệt, số deviations thực sự được tính/tái sử dụng, exact set diff và thời gian. Hủy/timeout nghĩa là chưa hoàn thành T17.

### 4.3. Certificate replay

Verifier độc lập dựng lại config/profile, role mapping, candidate forecasts, các payoff và best responses. Kiểm tra đủ 3 Judge × 2 z, mass của observations, mọi tie và prediction semantics. Với witness: apply đúng một focal branch, giữ peer tables, tính gain exact và so với regret được công bố.

Negative tests sửa một trường của certificate: thiếu nhánh, đổi q, đổi action witness, thêm gain sai, sai config hash, đổi role hoặc gắn succeeded cho run cancelled. Verifier phải từ chối; hash đúng không thay kiểm tra toán. Verifier không tin `equilibrium_status` hoặc `peer_tables_frozen_on_deviation` do producer tự ghi.

## 5. Bộ fixture tối thiểu

Các fixture sau phải có trước acceptance của module liên quan. Chỉ các giá trị được dẫn rõ là expected đã xác định; kết quả chưa tính không được điền số suy đoán.

### F01 — Trạng thái đều và không có thông tin

`pi=a=b=1/2`: mỗi state có xác suất `1/32`, mỗi z là `1/2`, mỗi `(z,x_i)` là `1/4`. Candidate all-H báo X có p=1/2, expected information score=1/2, prediction score=3/4, tổng=5/4. Với peer cố định này, H không cải thiện score so với L; chênh utility là `-c_i`.

Derivation: các bit độc lập đều; peer report là đồng xu độc lập, shadow tại own report nhị phân bằng 0 hoặc 1. Fixture này kiểm tra arithmetic/conditioning; không thay fixtures có tương quan.

### F02 — Vai trò bất đối xứng trên một scoring row

Reports `(0,1,0)`, predictions `(1/5,2/5,4/5)` theo A/B/C. Roles đúng cho score `(49/25,21/25,24/25)`.

Derivation: shadows A/B/C lần lượt `(0,1,0)`; information scores `(1,0,0)`; prediction scores `(24/25,21/25,24/25)`. Đây là unit fixture của scoring interface; không cần nó là một equilibrium forecast table.

### F03 — Giữ joint distribution

Conditional distribution tổng hợp có hai outcomes equiprobable: `(p_j,r_k)=(1/4,0)` và `(3/4,1)`. Với own report 0, shadows là 0 và 1/2; information scores 1 và 3/4. Với own report 1, shadows là 1/2 và 1; information scores 3/4 và 1.

Expected information score đều là `7/8`, có report tie. Nếu thay joint bằng product marginals, cả hai thành `5/8`. Own optimal prediction là 1/2, prediction score `3/4`, tổng đúng `13/8`.

Đây là fixture kiểm tra phép tích phân có tương quan, không tự nhận là một candidate phát sinh từ M1. Tests end-to-end M1 còn dùng F04 và F09.

### F04 — Peer freeze có phản ví dụ số

Dùng G1, candidate all-H báo X. Focal A đổi cả hai nhánh sang L0, own predictions `(19/50,31/50)` theo z; peer tables giữ nguyên candidate. Expected score của A là `3611/2500`, cũng bằng số đó ở mỗi z.

Nếu dựng lại peer predictions để thích ứng với focal L0, score thành `3161/2500` ex ante; từng z là `3461/2500` và `2861/2500`. Các giá trị này đã đối chiếu bằng phép thay bảng trực tiếp với checker hiện có; oracle mới phải tái lập độc lập. Cost của focal L bằng 0; f/lambda theo G1.

Test phải bắt cả mutation dựng bảng peer mới mà không sửa object cũ. Chỉ assertion snapshot trước/sau không đủ.

### F05 — Golden G1 và P5

Input và expected nguồn chuẩn ở spec §9.4, §11.1; reference JSON chứa exact values. So sánh đủ i,z, prediction table, report margins, low report tie, V_L/V_H, utility, regret và decision metrics. Ngưỡng `lambda*=43365125/85003317` ở c=1/20.

Thử lambda bằng ngưỡng, bằng một nửa và gấp đôi, với B đủ lớn (ví dụ 12); H/L effort phải tie, L tốt hơn, H tốt hơn tương ứng khi peer giữ candidate G1. Không dùng budget không hợp lệ rồi hiểu validation failure là phản ví dụ incentive.

### F06 — Golden G2, endpoint và payoff maximum

Từng profile all-Z, all-(1-Z), all-PASS, all-FAIL dưới G1 parameters: mọi state score=2, regret=0 và H mất cost dương. Prediction endpoints được giữ đúng 0/1, không epsilon clipping. Kiểm tra report ties khi reference delta=0.

Accuracy/wrong payout all-Z là `7/10` và `3/20` với V=1; all-H G1 là `112/125` và `13/250`. Tests phải giữ thứ tự utility bất lợi cho all-H như P5.

### F07 — Golden G3

Spec §11.3: `V_L=149/100`, `V_H=23833/15680`, delta score `2349/78400`, delta utility âm ở c=1/20. Candidate all-H bị bác; accuracy `27/32`, thấp hơn all-Z `9/10`.

### F08 — Golden G4 và timing

Spec §11.4: pi=4/5, a=7/10, b=4/5, c=1/20, lambda=1. Exact delta utility theo checker:

- z=0: `28808183/546012500`.
- z=1: `-59225497/6354612500`.

Delta gộp dương, nhưng candidate không cân bằng. Witness chỉ đổi effort/report/prediction của focal ở z=1; gain ex ante phải bằng mass z=1 nhân gain conditional. So khớp exact, không chỉ dấu hoặc decimal làm tròn.

### F09 — Asymmetric roles, costs và effort maps

Input: `pi=2/3,a=3/5,b=4/5,costs=(0,1/50,3/20),f=1/10,lambda=3/4,F=8/5,B=6,V=1,operating_cost=0`.

Profile z=0 là `(H00,H10,L1)`; z=1 là `(L0,H11,H01)`. Oracle độc lập phải tính và lưu certificate trước khi chốt expected cho production. Không giả định candidate này cân bằng hoặc symmetry giữa Judges.

Assertions cấu trúc: H00/H11 có hai reachable x observations, L chỉ một; cost A bằng 0 được giữ; prediction/report khác nhau theo roles; chạy A/B/C riêng. Xoay vòng đồng thời costs và profile phải xoay kết quả tương ứng; không áp dụng hoán đổi tùy ý hai Judge như một invariant.

### F10 — Zero costs và constant rewards

Với fixed hoặc lambda=0, số lớp cân bằng mỗi nhánh là `2^(3-m)*6^m`, m là số Judge có cost=0; full count là bình phương. Chạy m=0,1,3: branch counts 8,24,216; full counts 64,576,46,656.

Reports/predictions tự do theo ENGINE_DESIGN §6.4. Với cost dương, mọi H candidate có effort regret bằng cost; cost=0 tạo tie. Oracle xác nhận rằng Bayesian prediction được xuất chỉ là representative.

### F11 — Exact arithmetic và invalid inputs

Test `"0.5"` và `"1/2"` cho cùng hash; JSON number/bool bị từ chối. Test mẫu số 0, unknown field, thiếu costs, profile sai key/action, prior/accuracy 0 hoặc 1, âm cost/reward/budget/V/operating_cost, sai model version và vượt budget.

Test giá trị `1/2 ± 1/10^18`: chúng khác nhau bằng Fraction dù float có thể làm mất khác biệt. Q-loss, tie detection và serialization round-trip phải giữ khoảng cách. Đây là fixture arithmetic, không tự nhận tạo equilibrium khác nhau nếu chưa chứng minh.

### F12 — Miền tham số và cache contamination

Catalog deterministic: tích `pi∈{1/5,1/2,4/5}`, `a∈{1/3,1/2,4/5}`, `b∈{1/4,1/2,4/5}`; costs `(0,1/50,3/20)`, f=0, lambda=1, F=2, B=6, V=1. Có 27 configs, mỗi config kiểm tra đủ 216 candidates ở mỗi z qua production và branch oracle.

Giữ danh sách input/candidate đã chạy, tất cả discrepancy, thời gian; không gọi đó là exhaustive trên mọi tham số. Chạy thứ tự đảo để phát hiện cache dùng nhầm profile. Nếu thêm cache, kết quả cache on/off phải đồng nhất.

### F13 — Report hằng số nhưng prediction vẫn dùng X

Dùng phân phối G1; ở cả hai z, peer B/C chọn H01. Thử focal A là H00, rồi H11 trong một candidate riêng. Prediction của A vẫn là `(8/31,11/19,8/19,23/31)` theo `(z,x_A)`, vì scoring peer C báo X_C; không được suy A thiếu thông tin từ việc report hằng số.

Giữ peer tables của từng candidate rồi so A dùng H00 với L0, hoặc H11 với L1. Information component không đổi trong từng phép so sánh: reference B dự đoán report hằng số của A nên delta_B=0. Expected prediction score ở H là `11613/14725`; ở L là `1911/2500`. Gain trước chi phí là `35721/1472500>0`. Derivation từ posterior table G1 và P2; kiểm tra lại bằng oracle duyệt state. Đây là lợi ích prediction, không tự khẳng định các candidate này là cân bằng.

## 6. Invariants và biến đổi bắt buộc

| Property | Điều kiện và assertion |
| --- | --- |
| Probability | 32 positive masses, tổng 1; mọi conditional group tổng 1 |
| Observation isolation | Hai states cùng observation của một Judge cho cùng report/prediction; thay hidden bits không làm strategy output đổi |
| Q propriety | Với q,p exact, chênh expected Q bằng `(p-q)^2`; utility loss nhân lambda khi lambda>0 |
| Bounds | Shadow thuộc [0,1], mỗi Q thuộc [0,1], score thuộc [0,2] |
| Value of information | Giữ peer context: V_H>=V_L; prediction gain bằng conditional variance, không gán cho total gain |
| Regret | Regret>=0; witness replay đúng gain; đủ i,z trước khi certify |
| Accounting | Tổng reward bằng tổng expected reward của ba Judge; utility=reward-effort cost; wrong payout=V*joint false approval |
| Binary relabel | Đổi Y/Z/X/r thành 1-minus, p thành 1-p, pi thành 1-pi; a,b,c giữ; utility/accuracy giữ, FP/FN hoán đổi |
| Cyclic relabel | Xoay A→B→C đồng thời costs/actions/tables; kết quả xoay đúng theo roles |
| Reward shift | Tăng f cùng một hằng số và nâng B đủ: utility tăng hằng số đó, regret/ties không đổi |
| Payout scaling | Tăng V: wrong payout value/expected payout scale; reward, utility, regret không đổi |
| Output determinism | Cùng input/source: numeric payload, canonical hashes, order/ties giống; metadata thời gian/runtime được tách |

Binary relabel phải đổi cả action maps: đổi nhánh z; L0↔L1, H00↔H11, H01/H10 giữ tên khi đồng thời đổi nhãn x và r. Test transformation trước khi dùng làm oracle; một phép relabel sai có thể gây failure giả.

## 7. Mapping T01–T32 sang test triển khai

Các module/tests trong bảng là **tên mục tiêu cần tạo**. Mỗi hàng phải có evidence, không đánh dấu pass chỉ vì tên đã đăng ký. Nhóm có browser scenario cần cả test tự động và thao tác browser theo §10.

| ID | Module test mục tiêu | Fixture hoặc thao tác | Assertion / evidence bắt buộc |
| --- | --- | --- | --- |
| T01 | `test_model.py` | F01, F12 | 32 unique states, mass exact và conditioning khớp oracle |
| T02 | `test_information.py` | F09; đổi hidden bits | Strategy chỉ nhận observation; L invariant với x; scoring không có Y input |
| T03 | `test_scoring.py` | F02, F06; p=0,1/2,1 | Q/shadow/score bounds và endpoint exact |
| T04 | `test_scoring.py` | F02, F09 | j/k khác i và đúng cyclic; score tuple đúng từng Judge |
| T05 | `test_predictions.py` | F05, F11, F13; q,p=0,1/3,1 | Q-loss identity; prediction nhắm report của k; H constants vẫn dùng x |
| T06 | `test_fixed.py` | F10 với fixed | Regret của H là c; zero-cost ties; báo cáo/prediction tự do |
| T07 | `test_information.py` | F01; F12 với b=1/2 | V_H=V_L giữ peer; chi phí chỉ trừ utility H |
| T08 | `test_goldens.py` | F06 | Mọi state score2, regret0, prediction endpoints và report ties |
| T09 | `test_goldens.py` | F05 | Exact G1, mọi i,z, report margins, low ties, decision metrics |
| T10 | `test_goldens.py` | F07 | Bác all-H, đúng deviation và accuracy thấp hơn all-Z |
| T11 | `test_goldens.py` | F08 | Delta gộp dương nhưng witness ở z=1; candidate bị bác |
| T12 | `test_best_response.py` | F04, F09 | Bảng peer bất biến và payoff đúng bảng gốc; mutant rebuild bị bắt |
| T13 | `test_best_response.py` | F03, F09 | Joint expectation đúng 7/8 ở toy; end-to-end khớp oracle |
| T14 | `test_best_response.py` | F05, F12 | V_H>=V_L; prediction variance identity cho từng i,z |
| T15 | `test_certificates.py` | F05/F08/F09; tamper certificate | Regret/witness replay, reject thiếu nhánh/sai gain/prediction |
| T16 | `test_equilibria.py` | F09/F10/F13; sáu actions | Đúng 216 candidates/z, giữ H00/H11 và ties; finite classes vs continuum |
| T17 | `test_full_profiles.py` | G1; oracle §4.2 | Duyệt 46,656 full profiles, exact set equality với branch product |
| T18 | `test_symmetry.py` | F09, F12 | Binary/cyclic transforms đúng, FP/FN đổi mẫu số tương ứng |
| T19 | `test_rewards.py` | F05 threshold, F10, f shift | Threshold effort tie; lambda0 semantics; regret bất biến theo f |
| T20 | `test_output.py` | F11; B bằng trần/vượt trần | Budget reject; exact round-trip; reward actual khác cap; snapshot/manifest schema |
| T21 | `test_reproducibility.py` | Chạy lặp, đổi cwd/order; tamper snapshot | Semantic hash/order ổn định; raw-byte hash đúng, parent/freeze event hợp lệ; run cũ giữ nguyên |
| T22 | `test_cli.py` | Analyze/equilibria/sweep/compare; lỗi config | Subprocess thật, exit code, artifact đủ theo command, từ chối output đã tồn tại |
| T23 | `test_server.py` + B01 | Serve loopback/offline; port bận | Assets tải, capability thật, startup lỗi rõ; UI không cần CDN |
| T24 | `test_forms.py` + B02 | Presets, F09/F11, import/export | Mọi field/action sửa được, giữ fraction, lỗi đúng field, không silent override |
| T25 | `test_ui_parity.py` + B03 | G1–G4 qua API/UI và CLI | Exact output/config/profile hash đồng nhất, giá trị render khớp artifact |
| T26 | `test_ui_certificates.py` + B03 | G1/G4; mở witness | Đủ i,z/ties, G4 bị bác, chuyển witness thành candidate mới giữ run cũ |
| T27 | `test_ui_search.py` + B04 | Search; chọn tổ hợp branch | Counts/certificate thật, lọc được, mở analyze đúng full profile |
| T28 | `test_ui_sweep.py` + B05 | Grid nhỏ có invalid_budget | Giữ hàng lỗi, chart dùng dữ liệu engine; chọn hàng tái lập bằng analyze |
| T29 | `test_test_runner.py` + B06 | Reference/golden/all/selected; injected fail | Fail/error/skipped/not_run đúng; 0 tests không pass; tải log thật |
| T30 | `test_jobs.py` + B05/B07 | Compare; duplicate submit; cancel races | Equal cap và actual spend; lock; worker dừng; terminal state nhất quán |
| T31 | `test_history_security.py` + B07/B08 | Restart/history/path/origin tests | Interrupted đúng; artifact đúng run; chặn traversal/junction và request ghi sai origin/token |
| T32 | Browser B01–B08 + B09 | 1366×768 và 390×844, keyboard | Hoàn thành flows spec §18.9; ảnh/log và lỗi được sửa; không suy từ HTTP200 |

T20–T21 gồm version checks bổ sung tại spec §19.5. Mỗi mapping đăng ký một test/scenario thật trước khi chuyển trạng thái implemented; registry coverage không đồng nghĩa assertion coverage.

## 8. Mutation probes tối thiểu

| ID | Lỗi cố ý | Test phải phát hiện |
| --- | --- | --- |
| M01 | Tính lại peer prediction theo focal deviation | T12/F04, payoff đổi 3611/2500 thành 3161/2500 |
| M02 | Chỉ dùng Delta ex ante để nhận all-H | T11/F08 |
| M03 | Thay joint p_j/r_k bằng product marginals | T13/F03 |
| M04 | Loại H00/H11 hoặc dùng LowObservation cho chúng | T05/T16/F09/F13 |
| M05 | Nhầm reference với scoring peer | T04/F02 |
| M06 | Chuyển Fraction sang float trước equality/tie | T05/T20/F11 |
| M07 | Chỉ giữ report đầu tiên trong tie | T09/F05; T16 |
| M08 | Dùng posterior Y làm prediction của peer constant | T05/T08/F06 |
| M09 | Dùng cost A cho cả ba Judge | T06/T15/F09/F10 |
| M10 | Chia FP joint cho P(Y=1) thay P(Y=0) | T18/F09; oracle metric |
| M11 | Đếm lambda0 Bayesian representative là prediction duy nhất | T16/T19/F10 |
| M12 | Cancel chỉ đổi UI, worker tiếp tục hoặc ghi success | T30/B07 |
| M13 | Test runner báo pass khi discovery=0 hoặc selected ID thiếu | T29/B06 |

Với M06, probe phải thực sự đi qua production arithmetic/serialization path; việc kiểm tra riêng `Fraction != float` không chứng minh test phát hiện implementation bị thay. Với M08, all-PASS cho peer report probability=1 dù posterior Y có thể nhỏ hơn 1.

Mỗi mutation lưu baseline source hash, patch/hash mutant, test IDs chạy, expected failure, assertion thực tế, exit code và kết luận killed/survived/invalid. Mutant survived cần bổ sung test hoặc giải thích vì sao tương đương trong phạm vi; không bỏ âm thầm. Không đặt mục tiêu coverage phần trăm thay cho các probes cụ thể này.

## 9. API, runner và lifecycle tests

API integration dùng server/worker thật trên loopback và temp workspace fixture, không phụ thuộc results cá nhân. Error conditions như port bận, worker crash, invalid JSON và output tồn tại phải tạo được bằng test có kiểm soát.

Cancel test dùng worker test-only có handshake báo đã bắt đầu và barrier có thể giữ, không trông chờ một workload tình cờ chậm. Xác nhận PID/job ownership, worker đã dừng, artifact không succeeded; barrier chỉ dùng cho integration test, không thay kết quả khoa học. Test cả cancel-before-start, cancel-during-run và cancel-after-success.

Restart test đóng server khi job đang chạy, xác nhận process cleanup theo thiết kế và run được đọc lại interrupted; run đã completed vẫn mở được. Dữ liệu request snapshot không đổi khi người dùng sửa form hoặc gửi request thứ hai. Tạo hai request đồng thời để test backend lock, không chỉ disabled button.

Security scope local theo spec: traversal `..`, encoded path, absolute path, Windows drive/UNC, prefix sibling, symlink/junction nếu môi trường cho phép; artifact name không có trong allowlist; sai/missing origin và token cho request ghi. Nếu một fixture hệ điều hành không tạo được, ghi skipped kèm lý do và evidence thay thế; T31 còn thiếu nhánh đó cho đến khi có kiểm tra tương đương, không gắn pass toàn bộ.

## 10. Browser scenarios và evidence

| ID | Flow cần thao tác thật | Evidence |
| --- | --- | --- |
| B01 | Serve, mở offline, navigation sáu màn hình; port conflict | Browser log, assets/network, screenshot và startup stderr |
| B02 | Nạp preset, chỉnh mọi nhóm field/action, import invalid/valid JSON, export | Input snapshot, lỗi field, file export round-trip |
| B03 | Analyze G1–G4, mở exact/details, G4 witness, clone candidate | CLI/API artifacts đối chiếu và ảnh render đúng số/trạng thái |
| B04 | Search đủ 216 mỗi nhánh, lọc/chọn tổ hợp, mở analyze | Progress backend, certificate được chọn và profile chuyển sang |
| B05 | Sweep nhỏ có invalid budget; chart/table; compare equal cap | Hàng lỗi, giá trị exact, actual spend riêng và config từng run |
| B06 | Chạy các suites, selected IDs, injected failure, missing test, tải log | Test_results/log thật; UI phân biệt pass/fail/error/skipped/not_run |
| B07 | Duplicate submit, cancel, đổi draft khi đang chạy, restart | Job IDs, snapshot, process evidence và terminal artifacts |
| B08 | History, tải từng artifact, mở lại run, xem versions/freeze status | Artifact hashes, metadata và screenshot |
| B09 | Lặp flows chính bằng bàn phím ở desktop/mobile | Focus/label, form errors, table scroll, contrast measurements và ảnh hai viewport |

Mỗi scenario ghi browser/version, viewport, source hash, config/run IDs, bước thực hiện, expected/observed, pass/fail, ảnh và log. Accessibility gồm label gắn control, focus nhìn thấy, không keyboard trap; text thường đạt contrast ít nhất 4.5:1, text lớn 3:1. Dùng công cụ browser môi trường nếu có; screenshot riêng lẻ không chứng minh tương tác hoặc accessibility.

Failure injection UI chỉ dùng suite fixture tách biệt, công khai là test failure fixture. Sau scenario, xác nhận production engine và fixtures G1–G4 vẫn nguyên bytes. Không làm hỏng engine để trình diễn một nút đỏ.

## 11. Gates và lệnh kiểm tra

| Gate | Điều kiện hoàn thành | Điều chưa được kết luận |
| --- | --- | --- |
| GATE-0 | Pin spec/design/verification bytes; log freeze thực tế, checker preexisted; fixtures và test registry kế hoạch rõ | Chưa có engine đúng |
| GATE-1 | T01–T05; direct state metrics và F01/F02/F03; oracle có kiểm tra độc lập | Chưa chứng nhận best response/search |
| GATE-2 | T06–T15; G1–G4 và F09/F10; replay certificate; M01–M03/M05/M07–M10 | Chưa tìm hết pure profiles |
| GATE-3 | T16–T19; F12 differential, T17 full set equality; M04/M11; benchmark | Chỉ coverage game/lớp thuần đã định nghĩa |
| GATE-4 | T20–T22; CLI/artifact/sweep/compare và hashes; M06 | Chưa có browser acceptance |
| GATE-5 | T23–T32, B01–B09, M12–M13; tổng registry đủ; rerun suite cần thiết sau fixes | Hoàn thành M1 acceptance; chưa phải thực nghiệm người dùng/production |

Những phần T05 cần candidate forecasts có thể triển khai tối thiểu ở bước 1; bước 2 mở rộng best response. Test đang chờ module sau phải hiển thị pending, không báo gate đã hoàn thành.

Lệnh đang có để kiểm tra reference (chạy tại workspace này):

```powershell
python verification/verify_reference.py
```

Lệnh mục tiêu sau khi tạo tests/engine theo spec, hiện **chưa có suite để chạy**:

```powershell
python -m unittest discover -s tests -v
python -m ceav_m1 analyze --config configs/golden_g1.json --profile configs/all_high.json --mechanism rbts --out results/acceptance_g1
python -m ceav_m1 equilibria --config configs/golden_g1.json --mechanism rbts --out results/acceptance_equilibria
python -m ceav_m1 serve --port 8765
```

Chọn output mới mỗi lần, theo no-overwrite contract. Runner tích hợp CLI/API phải ghi lệnh/argv thực tế và exit code; các đoạn lệnh trong Markdown không tự là evidence.

Phân nhóm `reference`, `goldens`, `all`, `selected` theo spec; all chạy toàn bộ engine/API tests, bao gồm test chậm T17. Browser evidence được thu riêng rồi hợp nhất ở acceptance; Python runner không tự nhận đã chạy B01–B09. Nếu chạy selected để phát triển nhanh, báo rõ gate nào còn thiếu.

## 12. Evidence schema và quy trình sửa lỗi

Test run manifest pin config/source/spec/design/verification revisions và raw hashes; ghi Python/OS/browser nếu liên quan. Numeric payload deterministic; thời gian, duration và stdout/stderr giữ nguyên để chẩn đoán, không đưa vào semantic hash.

Một test record tối thiểu: `test_id`, `unittest_id` hoặc `browser_scenario_id`, fixture IDs, status, duration, assertion/error, expected/observed hoặc artifact pointers. Summary tính từ records; record thiếu hoặc process crash không được tự fill pass.

Khi thất bại:

1. Lưu config/profile, versions và witness nhỏ nhất đủ tái lập, giữ artifact thất bại.
2. Đối chiếu spec, fixture derivation và oracle để xác định lỗi thuộc code, test hay đặc tả.
3. Thêm regression có assertion phát hiện đúng lỗi; sửa đúng module chịu trách nhiệm.
4. Chạy regression, tests module và gate phụ thuộc bị ảnh hưởng; thay đổi toán/scoring/observation phải chạy lại core differential/search checks liên quan.
5. Nếu expected cần đổi, ghi lập luận độc lập và revision; giữ lịch sử run cũ. Kết quả bất lợi cho cơ chế vẫn được xuất.

Trước báo cáo hoàn thành, kiểm tra registry có đủ T01–T32, scenarios B01–B09, mutation evidence M01–M13, exact comparisons và artifacts của mọi gate. Báo riêng phần chưa chạy/chưa hỗ trợ. Các tài liệu này hoàn thành không đồng nghĩa các gates implementation đã pass.
