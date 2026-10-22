# CEAV-M1 — Thiết kế engine và hợp đồng thuật toán

**Revision:** `engine-design-r1` · **Ngày:** 22/10/2026  
**Áp dụng:** `ceav-m1-v1.0`, spec revision `math-proof-r2`.  
**Trạng thái:** thiết kế để triển khai; các module/interface dưới đây chưa tồn tại.

## 1. Nguồn chuẩn và phạm vi

[CEAV_M1_SPEC.md](CEAV_M1_SPEC.md) là nguồn chuẩn cho phân phối, thông tin, timing, payoff và phạm vi cân bằng. Tài liệu này quyết định cách biểu diễn và thực thi chúng; [VERIFICATION_PLAN.md](VERIFICATION_PLAN.md) quyết định bằng chứng nghiệm thu. Quy tắc làm việc tại [AGENTS.md](AGENTS.md).

Khi có mâu thuẫn, ghi lại vị trí và phản ví dụ, giải quyết theo spec trước khi công bố kết quả. Nếu cần đổi mô hình, tạo revision theo spec §19; không thay định nghĩa toán trong code để khớp fixture. Giữ workspace độc lập tại `C:\Users\dell\Desktop\fundtogether_data_analyzing`.

Đích thiết kế: từ cùng config/profile đã chuẩn hóa, CLI và HTML nhận cùng kết quả exact, certificate và lỗi. Engine dùng Python 3.12+ và thư viện chuẩn. Các interface là hàm thuần nhận dữ liệu, trả kết quả; IO nằm ở CLI/output/server.

## 2. Module và interface

Tên dưới đây là hợp đồng dự kiến, được phép đổi tên nội bộ nếu giữ trách nhiệm và cập nhật mapping test. Không cần lớp framework hoặc abstraction cho một implementation.

| Module | Interface chính dự kiến | Trách nhiệm và điều kiện trả về |
| --- | --- | --- |
| `model.py` | `validate_config(raw, mechanism)`, `enumerate_states(config)`, `observe(state, judge, effort)` | Config exact; 32 trạng thái có trọng số; observation đã che thông tin |
| `scoring.py` | `quadratic(p, report)`, `score_judge(reports, predictions, judge)`, `reward(score, mechanism, config)` | Chỉ nhận báo cáo/prediction, trả các thành phần score/reward; không nhận Y |
| `strategies.py` | `validate_profile(raw)`, `report_for(action, observation)`, `build_candidate(config, profile, rows)` | Action maps; candidate prediction tables trên reachable observations |
| `evaluate.py` | `evaluate(config, candidate, mechanism)`, `analyze(config, profile, mechanism)` | Payoff trực tiếp, decision metrics; analyze phối hợp evaluator và best response |
| `best_response.py` | `solve_branch(config, frozen_candidate, judge, z, mechanism)` | Tối ưu deviation một Judge, trả certificate theo nhánh |
| `equilibria.py` | `search_pure(config, mechanism, on_progress, is_cancelled)` | Đánh giá 216 candidate mỗi nhánh, giữ trạng thái/certificate/witness và quy tắc ghép |
| `output.py` | `canonicalize(...)`, `write_run(...)` | Serialization, semantic hashes, manifest, artifact và publication trạng thái cuối |
| `__main__.py` | Các command của spec §12.2 | Parse CLI, resolve đường dẫn, chạy cùng engine; exit status thật |
| `server.py` | Các route của spec §18.8 | HTTP, job lifecycle, gọi CLI worker bằng argv cố định; không chứa công thức toán |

`scoring` độc lập với evaluator. `best_response` không gọi search hoặc dựng lại candidate. `evaluate.analyze` có thể gọi `best_response`; chiều ngược lại không gọi `analyze`, tránh vòng phụ thuộc. Sweep/compare là orchestration quanh analyze, chưa cần module framework riêng.

```text
CLI hoặc HTML → validate → candidate → analyze/search → structured result
                                  ↓                         ↓
                          state-level evaluator         output artifacts

Tests oracle → evaluator độc lập trong tests → so sánh exact với engine
```

Progress/cancellation callbacks là phần điều khiển, không tham gia payoff, hash ngữ nghĩa hoặc thứ tự kết quả. Chúng có thể vắng mặt khi chạy một phép analyze nhỏ.

## 3. Kiểu dữ liệu, thứ tự và thông tin

### 3.1. Giá trị exact và validation

- Mọi xác suất, cost, reward, score, utility, regret dùng `fractions.Fraction` từ đầu đến cuối.
- Đọc chuỗi decimal hoặc `numerator/denominator` trực tiếp. JSON number, boolean, NaN/Infinity, mẫu số 0, chuỗi sai và field lạ đều bị từ chối; không chuyển qua float.
- Áp dụng miền theo spec §4; `operating_cost>=0`, mặc định `"0"`. `pi,a,b` thuộc khoảng mở, vẫn nhận `1/2`.
- `costs` có đúng ba phần tử theo A/B/C; profile có đúng keys `"0","1"`, mỗi nhánh đúng ba action hợp lệ.
- Validate cấu trúc toàn config; validate budget theo cơ chế chạy. Fixed kiểm tra `3F<=B`, RBTS kiểm tra `3f+6lambda<=B`; compare kiểm tra cả hai và `F=f+2lambda`.
- Mọi lỗi chỉ rõ field và lý do. Input sai là validation error; invariant sai trong engine là calculation error, không gán thành `not_equilibrium`.

### 3.2. Các record

Dùng dataclass bất biến/tuple cho dữ liệu đã validate; không dựa riêng vào `frozen=True` nếu bên trong vẫn có list/dict sửa được.

| Record | Trường cần có |
| --- | --- |
| `Config` | Model version, pi/a/b, costs tuple, f/lambda/F/B/V/operating_cost |
| `WeightedState` | State ID, y, z, tuple xa/xb/xc, probability exact |
| `LowObservation` | Chỉ z |
| `HighObservation` | z và x của chính Judge |
| `Profile` | Hai tuple action; Judge identity cố định A/B/C |
| `Candidate` | Profile; reachable prediction tables; prediction semantics; identity/hash từ nội dung |
| `BranchCertificate` | Judge, z, branch mass, candidate utility, low/high optimum, ties, regret, witness, frozen peer identity |

`report_for` nhận observation, không nhận full state. `observe` là nơi duy nhất chiếu full state sang thông tin người chơi. L không có trường x/Y/peer signal; H00/H11 vẫn nhận HighObservation để prediction dùng x dù report hằng số.

Full state chỉ đi qua generator, tích phân xác suất, evaluator và bộ dựng posterior. Scoring nhận tuple report/prediction đã hiện thực hóa; không đọc ground truth. Checker cũ có helper nhận state để tiện kiểm chứng; không sao chép interface đó thành strategy interface của engine chính.

Thứ tự chuẩn: state theo `(y,z,xa,xb,xc)` từ tích `{0,1}^5`; Judge A,B,C; z=0,1; action `L0,L1,H00,H01,H10,H11`; x=0,1. State ID là chỉ số 0–31 trong thứ tự đó. Ties giữ thứ tự trên, không phụ thuộc iteration của set.

### 3.3. Nhận diện profile và cache

Profile identity gồm cả hai nhánh. Candidate identity còn gồm model config và prediction tables thực tế nếu hỗ trợ prediction thủ công. Hai action H00 và L0 có thể cùng report nhưng khác thông tin/cost, phải có identity khác nhau.

Bản đầu ưu tiên cache cục bộ trong một candidate. Cache dùng qua candidate phải có key đủ model parameters, profile, prediction mode/tables, focal, z và effort liên quan. Utility cache thêm cơ chế, f/lambda/cost; tránh cache theo tên preset hoặc chỉ report vector. Test luôn đối chiếu bật/tắt cache nếu thêm cache.

## 4. State generator và candidate forecasts

### 4.1. State generator

```text
for (y,z,xa,xb,xc) in product((0,1), repeat=5):
    weight = prior(y) * L_a(z|y)
    for x in (xa,xb,xc): weight *= L_b(x|y)
    append WeightedState(..., weight)
require 32 distinct states, all weight > 0, sum(weight) == 1
```

Conditioning dùng tổng trọng số chia tổng khối lượng của event. Ghi rõ helper trả trọng số joint hay conditional; không trộn hai loại. Ở miền hợp lệ, cả hai z và mọi x của H đều có khối lượng dương. Event reachable có mass 0 là lỗi engine; không dùng epsilon hoặc denominator mặc định.

### 4.2. Candidate prediction tables

Với mỗi i, `k=(i+2)%3`; lấy candidate action tại z để xác định observation của i. Dựng report của k từ action và observation của k trong cùng state.

```text
for reachable observation I of candidate Judge i:
    denominator = sum P(w) over states consistent with I
    numerator   = sum P(w)*report_k(w) over those states
    prediction_i[I] = numerator / denominator
```

Conditioning còn xét z, nên effort map của peer đã được xác định bởi nhánh; không conditioning trên việc quan sát effort thực tế của peer. Candidate tables cho cả ba Judge được dựng xong một lần trước khi xét deviation.

Với RBTS `lambda>0`, đây là tối ưu prediction duy nhất trên reachable observations, theo P2. Report map của candidate có thể chưa tối ưu; không sửa nó trong bước dựng candidate. Tối ưu cả report rồi gọi đó là candidate cũ sẽ che mất deviation.

V1 mặc định nhận profile effort/report và dựng forecasts. Prediction thủ công là phần tùy chọn: nếu chưa triển khai thì từ chối field/mode đó rõ ràng. Nếu triển khai, giữ nguyên p đã nhập khi tính candidate payoff, freeze đúng p của peer, và cho focal tối ưu p trong deviation. Forecast sai có thể làm regret dương dù effort/report giữ nguyên.

## 5. Scoring và evaluator trực tiếp

### 5.1. Scoring

`score_judge` trả `reference_id`, `peer_id`, `shadow`, `information_score`, `prediction_score`, `total_score`. Áp dụng spec §6.2 trực tiếp, kiểm tra miền p và nhãn r. Thứ tự roles: A→(B,C), B→(C,A), C→(A,B).

Score không clipping, không chia tổng score, không thưởng theo majority. Với fixed, reward luôn F; có thể xuất RBTS score chẩn đoán nếu ghi rõ score không dùng trả fixed reward. Không dùng score chẩn đoán để chọn fixed best response.

### 5.2. State-level evaluation

Cho từng state, lấy action tại z, chiếu observation, tra report và prediction; tính score/reward/cost từng Judge. Mọi payoff candidate dùng chính các bảng đã pin, kể cả khi chúng không tối ưu.

Lưu 32 hàng trạng thái để trace: probability; y/z/x; action; report; prediction; từng score component; reward; cost; utility; majority decision. Tổng có trọng số cho ra metrics, đồng thời tính candidate utility có điều kiện từng z.

Decision là `int(sum(reports)>=2)`. Wrong payout dùng `V*P(Y=0,D=1)`; false approval có mẫu số `P(Y=0)`, false rejection có mẫu số `P(Y=1)`. Không dùng accuracy hoặc majority làm ground truth. Runtime tách khỏi resource/cash review cost, theo spec §10.

Evaluator phải chấp nhận candidate không cân bằng. Metrics của profile vẫn có ý nghĩa đánh giá, nhưng report gắn nhãn trạng thái candidate thật.

## 6. Best response: thuật toán đầy đủ

### 6.1. Frozen peer context

Đầu vào `solve_branch` bao gồm candidate bất biến. Giữ nguyên action/report map và prediction tables của cả hai peer; lưu identity trước và sau. Deviation thay effort của focal không làm peer quan sát được lựa chọn đó hoặc cập nhật forecast.

Đừng chỉ kiểm tra dict không bị mutate: một implementation có thể dựng dict peer mới trong deviation và vẫn sai. T12 phải đối chiếu giá trị payoff với oracle giữ bảng gốc, theo VERIFICATION_PLAN §4.

### 6.2. Tối ưu tại một observation

Từ branch z, thử focal L rồi H. Group theo thông tin mà effort thử cho phép, độc lập với effort của candidate focal. Peer vẫn tra observation theo effort candidate của chính họ.

```text
for trial_effort in (L,H):
    for focal observation I allowed by trial_effort at z:
        m = P(I | Z=z)
        q = E[peer_report_k | I]
        for report r in (0,1):
            A[r] = sum_{w consistent with I} P(w|I)
                   * Q(frozen_p_j(w)+(2*r-1)*min(frozen_p_j(w),1-frozen_p_j(w)),
                       frozen_report_k(w))
        best_reports[I] = every r attaining max(A[0],A[1])
        best_prediction[I] = q
        best_value[I] = max(A[0],A[1]) + 1-q+q*q
    V[trial_effort] = sum_I m * best_value[I]
```

`m` bằng 1 với L; hai `m` của H cộng thành 1. Không thay `(p_j,r_k)` bằng các biên độc lập. Hai report choices dùng chung q, bởi own prediction score không phụ thuộc own report khi peer cố định.

Các optimal report maps của H là tích Descartes của ties tại x=0,1; L có một tập tie. Giữ cả H constant maps. Mỗi observation ghi mass, A[0], A[1], q, tối ưu prediction score và tất cả report ties.

### 6.3. Effort, regret và witness

Với RBTS lambda dương:

```text
U_L = f + lambda*V[L]
U_H = f + lambda*V[H] - cost_i
best_efforts = argmax_all({L: U_L, H: U_H})
best_utility = max(U_L,U_H)
regret = best_utility - directly_evaluated_candidate_utility_given_z
```

Require `V[H]>=V[L]` và `regret>=0` bằng Fraction. Khi regret dương, witness phải chứa focal, z, action/report map, prediction map, old/new utility và gain. Chọn witness đầu tiên theo thứ tự chuẩn để tái lập, nhưng vẫn xuất mọi tie trong certificate.

Witness chỉ đổi nhánh z của focal; nhánh kia và toàn bộ peer giữ nguyên. Gain có điều kiện bằng regret khi witness đạt best response; gain ex ante bằng `P(Z=z)*regret`. Hai đại lượng cần tên khác nhau.

Điều kiện certify: đủ 6 cặp `(i,z)` và tất cả regret bằng 0. Không dùng dấu của Delta trung bình thay điều kiện này. Có thể xuất `max_regret` và `sum_z P(z)*regret_i(z)` để mô tả, nhưng không bỏ certificate từng nhánh.

### 6.4. Thưởng hằng số và continuum prediction

Fixed hoặc RBTS lambda=0 có utility lần lượt `F-cost_i*H` hoặc `f-cost_i*H`. Với cost dương chỉ L tối ưu; cost=0 thì L/H cùng tối ưu. Mọi report maps hợp lệ và mọi reachable prediction trong `[0,1]` đều hòa về utility.

Nếu vẫn xuất score-maximizing q/report cho chẩn đoán, đặt trong field riêng; không gắn chúng là tập utility best responses duy nhất. Certificate dùng `prediction_optimum: "any_in_unit_interval"`, `report_optimum: "any_admissible_map"` cùng một representative cụ thể để hiển thị/witness.

Enumeration trả các **lớp effort/report với prediction tự do**, không đếm chúng như một tập hữu hạn đầy đủ của numerical prediction strategies. `prediction_semantics` phân biệt `unique_on_reachable_observations` với `arbitrary_reachable_predictions`; representative Bayesian chỉ là cách trình bày.

## 7. Search cân bằng và phạm vi certificate

Với từng z, duyệt đúng 216 tuple actions theo thứ tự chuẩn. Dựng forecasts cho candidate đó, evaluate và kiểm tra đủ A/B/C với peer cố định. Kết quả giữ cả candidate bị bác, witness và ties theo spec §12.3.

Mỗi branch candidate có ID từ z và ba actions. Full profile ID ghép ID của z=0 và z=1. Có `216*216=46,656` effort/report profiles; output nêu số branch candidates thực sự kiểm tra, số cân bằng mỗi nhánh và tích hai số cân bằng. Dạng factorized là cách lưu; chưa phải chứng minh thuật toán factorization đúng. T17 đối chiếu với đường duyệt full profiles độc lập.

Không gộp bỏ candidate vì chỉ khác role, cost hoặc report constant. Mô hình có đối xứng quay vòng A→B→C khi xoay cả costs/profile; hoán đổi tùy ý hai Judge có thể đổi vai trò reference/peer. Optimizations symmetry cần chứng minh và test riêng; v1 không cần chúng.

Với thưởng hằng số và m Judge có cost=0: mỗi nhánh có `2^(3-m)*6^m` lớp effort/report cân bằng; full count là bình phương. Có thể dùng công thức làm assertion độc lập; vẫn xuất trạng thái đủ 216 candidates/nhánh. Prediction có continuum theo §6.4.

Tên kết luận theo spec §9.1; fields giữ `claims_mixed_equilibrium_coverage=false` và `claims_equilibrium_selection=false`. Search chưa hoàn thành/hủy không được xuất kết luận exhaustive, dù đã tìm thấy một số candidate đạt điều kiện.

## 8. Certificate có thể kiểm tra lại

Certificate cần đủ dữ liệu để verifier dựng lại phép tính từ config/profile, không tin cờ boolean của producer:

| Nhóm | Nội dung tối thiểu |
| --- | --- |
| Identity | Model/spec/design revision, source hash, config/profile hash, mechanism, scope |
| Candidate | Action maps, actual prediction tables, prediction semantics, role mapping |
| Branch | i,z,P(z), candidate score/reward/cost/utility |
| Low/high | Mỗi observation và mass, A0/A1/q, score components, optimal report sets, effort utilities |
| Verdict | Delta, regret, all optimal efforts, witness nếu regret dương |
| Completeness | Đủ i/z/observations, tested profile counts, completed/cancelled/error status |

Verifier kiểm tra state distribution, own candidate payoff, low/high alternatives và witness bằng đường tính riêng ở VERIFICATION_PLAN. Thiếu nhánh hoặc observation là certificate invalid, không mặc định zero. Hash khớp chỉ xác định bytes, không chứng minh toán đúng.

## 9. CLI, artifacts, sweep và comparison

CLI trong spec §12.2 là interface cần xây. Các command gọi chung validation/analyze/search; không copy công thức sang CLI, server hoặc JavaScript.

Canonical JSON: số thành `str(Fraction)` với mẫu số dương, tối giản; keys sắp xếp; UTF-8; separators cố định; không timestamp/decimal preview. `config_hash` bao gồm config đầy đủ đã thêm default; `profile_hash` gồm action maps. Mechanism được pin riêng và đưa vào identity của analysis, tránh dùng kết quả fixed cho RBTS.

`0.5` và `1/2` tạo cùng semantic hash. Raw spec/source hash giữ bytes gốc, không dùng canonicalization kiểu config. Source-content manifest liệt kê đường dẫn tương đối và hash từng file engine/web liên quan; không bao gồm results, cache, timestamp hoặc bí mật. Có Git vẫn ghi dirty state/source hash khi HEAD không đại diện code đang chạy.

Exact JSON/CSV theo spec §12.3. Decimal chỉ để hiển thị; giá trị không biểu diễn hữu hạn bằng float có thể xuất `decimal: null` kèm lý do, vẫn giữ exact. UI phải dùng exact fallback. Không để JSON sinh NaN/Infinity hoặc dùng decimal làm input vòng sau.

Output directory được tạo mới độc quyền, không ghi đè. Manifest bắt đầu running; ghi artifact qua temporary file rồi replace trong chính run; chỉ chuyển succeeded sau khi đủ file hợp lệ. Crash/cancel lưu trạng thái thật. Report lấy số từ structured result đã ghi, không tính lại bằng JS hoặc hardcode kết luận.

Sweep: axes hữu tỉ `pi,a,b,c,lambda`, c gán cả ba costs; thứ tự axes chuẩn và tích Descartes xác định. Giữ từng hàng invalid, gồm `invalid_budget`, và profile cố định. Hàng valid phải tái lập bằng analyze. Comparison bắt buộc equal cap và cùng config/profile; trả actual spend riêng, không suy rộng thành comparison của toàn bộ equilibria.

Mỗi run pin spec snapshot theo §19 và hash của hai tài liệu thiết kế/kiểm chứng dùng lúc triển khai. Trước implementation-start, lưu bản bytes của các tài liệu đi kèm vào lịch sử riêng; giữ snapshot `math-proof-r2` đã có. Các revision thiết kế không tự biến thành model version mới.

## 10. HTML, local API và job lifecycle

Yêu cầu chức năng/route/UX lấy từ spec §18; không giảm HTML thành viewer JSON. HTML/CSS/JS thuần, offline; giao diện tiếng Việt, đủ Analyze/Equilibria/Sweep/Compare/Tests/History. Frontend render exact/decimal, chỉnh input, gọi API; engine sở hữu toán.

Server tạo immutable request snapshot và job ID, giữ một job nặng tại một thời điểm bằng lock. Worker là subprocess với operation/argv allowlist; không shell interpolation. CLI tương đương chạy cùng engine. Tiến trình worker truyền progress thật; backend không suy đoán phần trăm.

```text
queued → running → succeeded | failed | cancelled
queued → cancelled
queued/running khi server chết → interrupted khi khởi động lại
```

Terminal states bất biến. Cancel và success phải được phân xử trong cùng vùng khóa: nếu success đã được công bố, cancel trả terminal state; nếu cancel được nhận trước, dừng worker thuộc job, reap process, và không publish succeeded. Chỉ chấp nhận cancelled sau khi worker dừng; trong lúc dừng vẫn báo đang xử lý hủy. Dừng toàn bộ process tree của job nếu worker tạo child, không giết theo tên python chung.

API validation đồng nhất CLI; response ghi job/run ID, status, capability thật và lỗi có cấu trúc. Reference suite có thể sẵn sàng trong khi engine/UI suite còn unavailable. Test selector chỉ dùng IDs đăng ký. Khởi động lại đọc history từ artifacts và đánh dấu interrupted cho job dở dang, không tự resume.

Loopback, same-origin/session token và path confinement theo spec §18.8. Path resolve kiểm tra containment sau symlink/junction resolution, không kiểm tra bằng string prefix. Artifact route đọc allowlist trong đúng run. Không có chức năng gửi lệnh shell/path tùy ý từ browser.

## 11. Trình tự xây và điều kiện qua bước

| Bước | Sản phẩm cần xây | Gate trong VERIFICATION_PLAN |
| --- | --- | --- |
| 0 | Pin spec/design/verification, ghi freeze event thực tế; giữ checker cũ | GATE-0 |
| 1 | Model, strategy views, scoring, direct evaluator | GATE-1 |
| 2 | Candidate forecasts, best response, certificates | GATE-2 |
| 3 | Exhaustive search và kiểm chứng độc lập full profiles | GATE-3 |
| 4 | CLI, artifact, sweep, comparison | GATE-4 |
| 5 | HTML/API, worker, history/test runner, browser acceptance | GATE-5 |

Có thể dựng giao diện tĩnh sớm khi có yêu cầu, nhưng không dùng nó để chứng nhận engine hoặc bỏ gate. Chỉ tối ưu sau khi đường exact đơn giản và oracle thống nhất. Benchmark ghi cấu hình/máy/Python/source hash; mọi thay đổi cache/parallelism phải giữ exact output, ties và certificate.

## 12. Trạng thái thiết kế

Đã định nghĩa interface và thuật toán; chưa xây các module trên, oracle tổng quát, certificate verifier, API hoặc HTML. Checker [verify_reference.py](verification/verify_reference.py) chỉ kiểm tra named profiles trong phạm vi riêng; không chứng minh T01–T32 đã được nghiệm thu.

Hoàn thành implementation đòi hỏi tất cả gates trong [VERIFICATION_PLAN.md](VERIFICATION_PLAN.md), không chỉ việc file này tồn tại hoặc G1–G4 pass.
