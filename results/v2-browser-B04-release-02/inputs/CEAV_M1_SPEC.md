# CEAV-M1 — Đặc tả hệ thống kiểm chứng incentive và cân bằng

**Phiên bản:** `ceav-m1-v1.0`  
**Bản cập nhật đặc tả:** `math-proof-r2` — chuẩn hóa thuật ngữ, thêm P1–P5 và quản lý snapshot; giữ yêu cầu HTML bắt buộc.  
**Ngày:** 22/10/2026  
**Trạng thái:** Đặc tả để triển khai; chưa phải một cơ chế production.  
**Workspace:** `C:\Users\dell\Desktop\fundtogether_data_analyzing`

## 1. Mục tiêu và kết quả phải có

Xây một hệ thống kiểm chứng có **engine Python và giao diện HTML thân thiện**, có thể trả lời bằng kỳ vọng chính xác:

1. Với chiến lược của hai peer giữ nguyên, Judge có lợi khi trả chi phí lấy thêm thông tin không?
2. Judge nên báo cáo và dự đoán thế nào sau mỗi quan sát?
3. Một cấu hình có phải cân bằng thuần trong trò chơi đã định nghĩa không? Nếu không, ai có thể đổi chiến lược, trong tình huống nào và được lợi bao nhiêu?
4. Cân bằng đó tạo false approval, tiền giải ngân sai kỳ vọng và chi phí review bao nhiêu?

Một run hợp lệ phải xuất cấu hình, kết quả số chính xác, chứng cứ best response và phạm vi kết luận. Không được chỉ in `equilibrium=true` hoặc vài biểu đồ.

Người dùng phải cấu hình, chạy đầy đủ các phép phân tích và test, kiểm tra chứng cứ và tải kết quả ngay trong trình duyệt. CLI vẫn cần để tái lập; không yêu cầu người dùng mở terminal cho từng thao tác trên giao diện.

## 2. Phạm vi đã chốt

### 2.1. Có trong bản đầu

- Một claim với trạng thái thật nhị phân; ba Judge A, B, C.
- Một tín hiệu chung miễn phí và một tín hiệu riêng có thể thu thập bằng effort.
- Hai mức effort; báo cáo nhị phân; prediction liên tục trong `[0,1]`.
- Hai cơ chế: **fixed reward** và **công thức scoring RBTS Eq. (8) trong môi trường CEAV-M1**.
- Exact enumeration bằng phân số hữu tỉ; không cần Monte Carlo.
- Best response đầy đủ đối với effort, report và prediction.
- Tìm cân bằng thuần trong lớp chiến lược tại mục 7.
- Đánh giá accuracy và rủi ro giải ngân bằng ground truth chỉ evaluator biết.
- Giao diện HTML/CSS/JavaScript chạy local, tiếng Việt, có đầy đủ chức năng theo mục 18.

### 2.2. Không thuộc bản đầu

- Không nhập code, cấu hình, policy, dữ liệu hoặc baseline của hệ thống FundTogether hiện tại.
- Không smart contract, RPC, ví, token thật, PostgreSQL hoặc MinIO.
- Không slashing, stake, hối lộ, coalition transfers hoặc non-reveal.
- Không Creator chiến lược, evidence giả có chủ đích, multi-claim, reputation hay appeal.
- Không tự động suy ra equilibrium selection hoặc động lực hội tụ.
- Không tuyên bố đã tìm mọi mixed equilibrium, correlated equilibrium hoặc coalition-proof equilibrium.

Các phần mở rộng chỉ được thêm trong phiên bản sau. Kết quả âm là kết quả nghiên cứu hợp lệ; không sửa test hoặc baseline để làm RBTS trông tốt hơn.

## 3. Môi trường triển khai và cấu trúc dự kiến

Python 3.12 trở lên; bản đầu chỉ cần thư viện chuẩn: `fractions`, `itertools`, `dataclasses`, `json`, `csv`, `hashlib`, `argparse`, `unittest`.

Giao diện dùng HTML, CSS và JavaScript thuần; Python phục vụ static files và JSON API trên loopback. Có thể dùng thêm `http.server`, `subprocess`, `threading`, `uuid` thuộc thư viện chuẩn. Không cần Node, frontend framework hoặc CDN để khởi chạy bản đầu.

```text
fundtogether_data_analyzing/
├── CEAV_M1_SPEC.md                 # Tài liệu này
├── references/PRIMARY_SOURCES.md   # Nguồn gốc và giới hạn của các kết quả học thuật
├── spec_history/                  # Snapshot và manifest revision, không sửa bản đã lưu
├── verification/
│   ├── verify_reference.py         # Checker nhỏ đã có, không phải analyzer hoàn chỉnh
│   └── reference_results.json     # Kết quả checker tái lập được
│
│   # Các đường dẫn dưới đây là đầu ra CẦN XÂY ở giai đoạn implementation:
├── ceav_m1/
│   ├── __main__.py                # CLI
│   ├── model.py                   # Tham số, 32 trạng thái và quan sát
│   ├── scoring.py                 # Fixed reward, quadratic score, RBTS
│   ├── strategies.py              # Effort/report maps, prediction tables
│   ├── evaluate.py                # Payoff và decision metrics
│   ├── best_response.py           # Tối ưu effort/report/prediction khi peer cố định
│   ├── equilibria.py              # Enumeration cấu hình thuần
│   ├── output.py                  # Serialize phân số, cấu hình, manifest
│   └── server.py                  # Local HTTP/API, quản lý tiến trình chạy
├── web/
│   ├── index.html                 # Giao diện phòng thí nghiệm CEAV-M1
│   ├── styles.css                 # Bố cục dễ đọc, responsive
│   └── app.js                     # Form, API, trạng thái, bảng và biểu đồ
├── configs/                       # JSON đầu vào, giá trị số dưới dạng chuỗi
├── tests/                         # Engine/API tests và browser acceptance theo mục 14
└── results/                       # Mỗi run một thư mục riêng
```

Chỉ tách module theo trách nhiệm trên; không cần plugin framework, database, hàng đợi phân tán hoặc solver ngoài cho bản thuần. Local server chỉ cần quản lý một tác vụ chạy tại một thời điểm. Không sửa workspace khác. Không coi cấu trúc dự kiến là code đã tồn tại.

## 4. Tham số và phân phối sinh dữ liệu

### 4.1. Ký hiệu

| Ký hiệu | Ý nghĩa | Miền của bản đầu |
| --- | --- | --- |
| `Y` | Claim thực sự đạt | `{0,1}`; `1 = đạt` |
| `pi` | `P(Y=1)` | `0 < pi < 1` |
| `Z` | Tín hiệu chung miễn phí | `{0,1}` |
| `a` | Độ chính xác đối xứng của `Z` | `0 < a < 1` |
| `X_i` | Tín hiệu riêng tiềm năng của Judge i | `{0,1}` |
| `b` | Độ chính xác đối xứng của mỗi `X_i` | `0 < b < 1` |
| `e_i` | Có thu thập `X_i` không | `L` hoặc `H` |
| `c_i` | Chi phí khi chọn H | `c_i >= 0`; mẫu chính dùng `c_i > 0` |
| `r_i` | Báo cáo | `{0,1}` |
| `p_i` | Dự đoán peer được chấm sẽ báo 1 | `[0,1]` |
| `f` | Phần thưởng cơ bản trong RBTS | `f >= 0` |
| `lambda` | Hệ số thưởng RBTS | `lambda >= 0` |
| `F` | Fixed reward mỗi Judge | `F >= 0` |
| `B` | Trần tổng thưởng cho một claim | `B >= 0` |
| `V` | Giá trị payout dùng để đo mất mát | `V >= 0`, đơn vị nghiên cứu chuẩn hóa |

Chi phí và reward cùng đơn vị nghiên cứu; không phải tiền thực tế. `V` không tham gia utility của Judge trong M1. Mọi tham số, common prior, cơ chế và chiến lược trong phép phân tích là common knowledge. Không suy ra con người thực tế biết đúng các tham số đó.

### 4.2. Phải định nghĩa lỗi đối xứng

Đặt `L_t(s|y) = t` nếu `s=y`, ngược lại bằng `1-t`.

```text
Y ~ Bernoulli(pi)
P(Z=z | Y=y)   = L_a(z|y)
P(X_i=x | Y=y) = L_b(x|y)
Z, X_A, X_B, X_C độc lập có điều kiện theo Y.
```

Chỉ ghi `P(X_i=Y)=b` là chưa đủ để xác định mô hình. Công thức trên chốt cả sensitivity và specificity bằng b. Cho phép `a=0.5` hoặc `b=0.5` để kiểm tra tín hiệu không mang thông tin; các giá trị bằng 0 hoặc 1 chưa thuộc miền đầu vào của bản đầu.

Với `w=(y,z,x_A,x_B,x_C)`, có đúng 32 trạng thái tiềm năng:

```text
P(w) = pi^y (1-pi)^(1-y)
       * L_a(z|y)
       * L_b(x_A|y) * L_b(x_B|y) * L_b(x_C|y)
```

Các `X_i` được sinh tiềm năng ngay cả khi Judge chọn L, để dùng chung không gian trạng thái cho các phép so sánh. Judge L **không được quan sát** `X_i`. Đây không phải giả định effort làm thay đổi trạng thái Y; effort chỉ thay đổi tập thông tin được biết.

### 4.3. Phân biệt dữ liệu và thông tin được phép biết

- Evaluator được đọc toàn trạng thái, gồm Y, để tính xác suất và loss.
- Strategy L chỉ nhận `Z` và tham số công khai.
- Strategy H nhận `(Z,X_i)` và tham số công khai.
- Strategy không nhận Y, tín hiệu riêng của peer, báo cáo chưa mở hoặc toàn state object.
- Ground truth tuyệt đối không được truyền vào scoring hay used as reward oracle.
- Backend nghiên cứu có thể tính posterior từ phân phối đã khai báo; không được đưa giá trị Y đã hiện thực hóa cho Judge.

## 5. Thời điểm hành động và thông tin

```text
1. Công bố model, reward và trần ngân sách.
2. Nature sinh trạng thái; tất cả Judge quan sát Z.
3. Judge đồng thời chọn effort e_i(Z); lựa chọn này không được peer quan sát.
4. Judge H trả c_i và quan sát X_i; Judge L không thấy X_i.
5. Judge đồng thời gửi (r_i,p_i) theo thông tin được phép biết.
6. Tính score và reward; evaluator tính decision/loss riêng.
```

Bước 5 mô hình hóa thông tin bị che trước lúc gửi báo cáo; không cần triển khai cryptographic commit–reveal trong M1. Judge có thể dùng quy tắc chung như `r=Z`; việc che báo cáo không loại bỏ cân bằng này.

**Effort được chọn SAU Z.** Điều kiện incentive và cân bằng phải kiểm tra riêng với `Z=0` và `Z=1`. Kỳ vọng gộp dương không đủ để chứng nhận một strategy luôn chọn H.

Không thêm quan sát effort của peer trong phép deviation. Một game cho phép peer thấy effort rồi phản ứng là một game khác.

## 6. Scoring, utility và ngân sách

### 6.1. Fixed reward

```text
Reward_i = F
Utility_i = F - c_i * 1[e_i=H]
```

Khi `c_i>0`, chọn L tốt hơn H nếu những yếu tố khác không ảnh hưởng utility. Báo cáo và prediction không ảnh hưởng tiền; analyzer có thể tính Bayesian prediction làm giá trị chuẩn để xuất, nhưng không được nói đó là lựa chọn duy nhất của fixed-reward equilibrium.

### 6.2. Công thức scoring RBTS Eq. (8) trong CEAV-M1

CEAV-M1 giữ nguyên công thức scoring RBTS Eq. (8), đồng thời nghiên cứu cân bằng trong môi trường có tín hiệu chung Z và thu thập thông tin tốn chi phí, với effort được chọn sau Z. Tên hiển thị ngắn có thể là `RBTS scoring`; identifier `rbts` trong CLI/API giữ nguyên. Không thêm một baseline canonical/adapted riêng khi cả hai chỉ dùng cùng công thức scoring.

Với thứ tự `[A,B,C]`, reference `j=(i+1) mod 3`, peer để đối chiếu `k=(i+2) mod 3`. Ba vai trò phải khác nhau.

```text
Q(p,1) = 2p - p^2
Q(p,0) = 1 - p^2
delta_j = min(p_j, 1-p_j)
shadow_i = p_j + (2*r_i-1)*delta_j
InfoScore_i = Q(shadow_i, r_k)
PredictionScore_i = Q(p_i, r_k)
Score_i = InfoScore_i + PredictionScore_i
Reward_i = f + lambda*Score_i
Utility_i = Reward_i - c_i*1[e_i=H]
```

`p_i` là prediction report mà Judge tự chọn trong `[0,1]`; nó được chấm với report của k, không phải Y, majority hoặc xác suất claim thật sự đạt. `p_j` trong shadow là prediction report của reference j trong cùng candidate profile. Công thức Q và shadowing tương ứng Eq. 7–8 của [Witkowski–Parkes (2012)](https://cdn.aaai.org/ojs/8261/8261-13-11789-1-2-20201228.pdf).

Bài gốc mô tả prediction về tần suất tín hiệu cao. Khi peer trung thực, `r_k=S_k`, nên posterior về report của peer trùng posterior về tín hiệu của peer. Với peer strategy bất kỳ giữ cố định, `p_i*=P(r_k=1|I_i)` là **kết quả tối ưu hóa** của cùng quadratic score, không phải ràng buộc bắt người chơi phải nhập giá trị đó. Giữ công thức scoring không có nghĩa giữ nguyên toàn bộ môi trường thông tin hoặc tự kế thừa định lý incentive compatibility.

RBTS gốc đã xét người chơi chiến lược và khả năng báo cáo sai. Strategic reporting tự nó không phải đóng góp mới của CEAV. Những thay đổi được phân tích ở M1 là tín hiệu chung, chi phí lấy thêm thông tin và thời điểm chọn effort; các bảo đảm trong môi trường này phải được lập luận và kiểm chứng riêng.

### 6.3. Ngân sách độc lập

```text
0 <= Score_i <= 2
RBTS: total_reward <= 3*f + 6*lambda <= B
Fixed: total_reward = 3*F <= B
```

So sánh cùng trần có thể đặt `F=f+2*lambda`; khi đó hai cơ chế có cùng maximum reward budget, **không có nghĩa cùng reward thực chi**. Luôn xuất cả hai đại lượng. Không chuẩn hóa score theo tổng score hoặc chia lại một pool sau khi thấy báo cáo: cách đó thay đổi incentives và không còn là RBTS đang xét.

Reward là tiền giả định từ ngân sách nghiên cứu, tách khỏi payout V. Cộng một hằng số f không làm thay đổi best response trong game bắt buộc tham gia này. M1 chưa mô hình hóa quyết định không tham gia hoặc thị trường tuyển Judge.

## 7. Không gian chiến lược thuần và prediction liên tục

Một chiến lược gồm ba phần:

```text
effort_map: Z -> {L,H}
report_map: quan sát được phép biết -> {0,1}
prediction_map: quan sát được phép biết -> [0,1]
```

Không coi `Honest`, `Lazy`, `Always PASS` là các loại chiến lược đầy đủ. Có Judge chọn H nhưng báo hằng số, dùng X_i chỉ để dự đoán peer tốt hơn.

### 7.1. Sáu action tại mỗi nhánh Z cố định

| Action | Effort | Báo cáo khi `X_i=0` | Báo cáo khi `X_i=1` |
| --- | --- | --- | --- |
| `L0` | L | 0, không đọc X_i | 0, không đọc X_i |
| `L1` | L | 1, không đọc X_i | 1, không đọc X_i |
| `H00` | H | 0 | 0 |
| `H01` | H | 0 | 1 |
| `H10` | H | 1 | 0 |
| `H11` | H | 1 | 1 |

Giữ cả H00 và H11; không loại chúng chỉ vì report hằng số. Prediction của chúng vẫn có thể phụ thuộc X_i.

Một Judge có `6*6=36` bản đồ hành vi effort/report qua hai giá trị Z. Có `36^3=46,656` profile effort/report thuần đầy đủ. Các hành động khác nhau chỉ ở lịch sử không thể xảy ra do lựa chọn effort của chính Judge được coi tương đương để enumeration; không tuyên bố có uniqueness ở off-path histories.

### 7.2. Loại prediction bằng giải tích tại candidate profile

Với `lambda>0`, prediction tối ưu ở mỗi quan sát có xác suất dương là:

```text
q_i(I_i) = P(r_k=1 | I_i, candidate strategies)
p_i*(I_i) = q_i(I_i)
max E[Q(p_i,r_k)|I_i] = 1 - q_i + q_i^2
```

Vì vậy, mỗi candidate effort/report profile tạo một bộ prediction Bayesian duy nhất trên các quan sát reachable. Không cần quét lưới p. Prediction có thể bằng 0 hoặc 1, dù prior và signal accuracy nằm trong khoảng mở.

Điều này giảm không gian ứng viên **thuần**; không giải quyết mixed equilibrium. Khi `lambda=0`, prediction không được xác định duy nhất bởi payoff; xử lý như game thưởng hằng số và ghi rõ sự suy biến.

## 8. Best response với peer cố định

### 8.1. Quy tắc bắt buộc

1. Dựng candidate report maps và prediction tables cho cả ba Judge.
2. Chọn focal i. Đóng băng toàn bộ strategy và prediction tables của hai peer.
3. Cho i thử L/H, tối ưu báo cáo theo từng quan sát và tối ưu prediction liên tục.
4. Không tính lại prediction của peer để thích ứng với deviation của i.
5. Lặp lại cho từng i và từng Z.

Phải giữ tương quan của `(p_j,r_k)` từ cùng trạng thái. Không thay expectation của tích bằng tích các expectation. Khi candidate thay đổi để kiểm tra một profile mới thì dựng lại prediction tables; khi focal đang deviation trong một profile thì không dựng lại tables của peer.

### 8.2. Công thức tính

Với quan sát I của focal, giữ các peer cố định:

```text
A_i(I,r) = E[ Q(p_j + (2*r-1)*min(p_j,1-p_j), r_k) | I ]
q_i(I)   = P(r_k=1 | I)
v_i(I)   = max(A_i(I,0), A_i(I,1)) + 1-q_i(I)+q_i(I)^2
V_L,i(z) = v_i(Z=z)
V_H,i(z) = sum_x P(X_i=x | Z=z) * v_i(Z=z,X_i=x)
Delta_i(z) = lambda*(V_H,i(z)-V_L,i(z)) - c_i
```

Effort tốt nhất: H nếu Delta dương, L nếu âm, cả hai nếu bằng 0. Các r cùng đạt maximum đều phải được giữ như tie. Không ép H báo X_i, L báo Z hoặc dùng prediction theo Y.

Ở RBTS:

```text
BR_i(z) = f + max(lambda*V_L,i(z), lambda*V_H,i(z)-c_i)
Regret_i(z) = BR_i(z) - CandidateUtility_i(z)
```

Với fixed reward: `BR_i(z)=F` khi `c_i>=0`; regret bằng chi phí H của candidate. Khi `c_i=0`, L/H hòa nhau.

### 8.3. Chứng cứ phải xuất

Với mỗi focal và z: candidate action, candidate utility, utility tốt nhất ở L/H, Delta, regret, các report tối ưu, prediction tối ưu và xác suất của từng quan sát. Nếu profile thất bại, phải xuất ít nhất một deviation cụ thể tạo utility cao hơn.

High Effort có thể bỏ qua X_i, nên `V_H >= V_L` trước chi phí. Vi phạm bất đẳng thức này là lỗi engine. Nó không kéo theo `Delta>=0` sau chi phí.

## 9. Chứng nhận và tìm cân bằng thuần

### 9.1. Định nghĩa operational

Tên đầy đủ dùng trong tài liệu/báo cáo là **cân bằng chiến lược thuần của biểu diễn dạng chuẩn rút gọn của trò chơi CEAV-M1 đã định nghĩa** (`pure-strategy equilibrium of the reduced normal-form representation`). Strategy đầy đủ là `sigma_i=(e_i,rho_i,phi_i)`, gồm effort map theo Z, report map và prediction map theo thông tin được phép biết ở mục 7. Khi mô tả cấu trúc thông tin Bayesian, có thể gọi là pure-strategy Bayesian Nash equilibrium của game này; không coi đó là một refinement tuần tự khác.

Điều kiện cân bằng là, với mọi Judge i và mọi strategy deviation hợp lệ `sigma_i`:

```text
E[U_i(sigma_i*, sigma_-i*)] >= E[U_i(sigma_i, sigma_-i*)]
```

Vì hai nhánh Z đều có xác suất dương, được quan sát trước effort và không có ràng buộc nối nhánh, engine chứng nhận điều kiện trên bằng kiểm tra tối ưu riêng từng nhánh. Candidate là một cân bằng thuần nếu, với mọi i và cả hai z:

```text
Regret_i(z) = 0
```

Dùng equality của Fraction trong chế độ exact. `Regret_i(z)<0` là lỗi tính toán. Nếu sau này hỗ trợ float, chỉ được gắn nhãn `epsilon_equilibrium` và xuất epsilon; không làm tròn rồi gọi là exact equilibrium.

Đây là kiểm tra lệch đơn phương trong game thông tin đã chốt. Không tự gắn nhãn sequential equilibrium, coalition-proof hoặc dynamically stable.

UI có thể ghi ngắn `Cân bằng thuần`, kèm liên kết tới định nghĩa này. Output phải có `equilibrium_concept: "pure_strategy_nash_in_reduced_normal_form"` và strategy_scope. Không rút thành tuyên bố tìm mọi Nash equilibrium; prediction ngoài những quan sát reachable và mixed equilibria không được bao phủ bởi enumeration hiện tại.

### 9.2. Enumeration hoàn chỉnh cho lớp thuần

Vì Z được quan sát trước effort và payoff không có ràng buộc liên nhánh:

```text
for z in [0,1]:
    for action_profile in product(SIX_ACTIONS, repeat=3):  # 216 profiles/z
        build candidate prediction tables conditional on z
        evaluate candidate utility
        for i in [A,B,C]:
            freeze peer strategies and prediction tables
            solve full unilateral best response
        keep candidate iff all exact regrets are zero

full_pure_equilibria = CartesianProduct(equilibria_z0, equilibria_z1)
```

Một profile HHH theo nghĩa chỉ chọn effort H chưa phải một candidate đầy đủ: phải ghi report maps và prediction. Không tìm trên tám effort profiles rồi tuyên bố tìm hết cân bằng.

Đầu ra phải ghi: `strategy_scope`, số ứng viên mỗi nhánh, số cân bằng mỗi nhánh, số tổ hợp đầy đủ và tất cả ties. Có thể xuất dạng branch-factorized để tránh lặp dữ liệu; số lượng đầy đủ bằng tích hai số lượng nhánh. Không gộp hai nhánh chỉ bằng expected regret trung bình.

### 9.3. Không dùng một q duy nhất để suy ra cân bằng

Phân tích niềm tin về peer hoặc mixed strategies chưa thuộc bản đầu. Nếu bổ sung, cần joint distribution, prediction beliefs và loại tương quan giữa peer. Chỉ biết `P(peer chooses H)=q` không xác định được payoff khi hai peer tương quan. Không tạo đồ thị threshold q rồi gọi đó là equilibrium selection.

### 9.4. Mệnh đề nền và chứng minh

P1–P4 là các kết quả nền cho mô hình và thuật toán, không được tự nhận là đóng góp mới chỉ vì được viết thành proposition. P5 là kết quả cho instance G1. Tách rõ: **mệnh đề và lập luận**, **checker tham chiếu**, **certificate của instance từ engine chính khi đã triển khai**.

#### P1 — Fixed reward không khuyến khích High Effort có chi phí

**Điều kiện:** utility chỉ gồm fixed reward F trừ chi phí effort; `c_i>0`; không có lợi ích ngoài cơ chế hoặc penalty khác.

**Phát biểu:** tại mỗi Z, action effort H bị L trội nghiêm ngặt về utility, bất kể peer và report/prediction.

**Chứng minh:** `U_i(H)=F-c_i<F=U_i(L)`. Thay report hoặc prediction không thay F. Khi `c_i=0`, hai effort hòa nhau; không được tiếp tục gắn nhãn strict dominance.

**Đối chiếu:** T06. Kết quả không nói về chất lượng quyết định dưới fixed reward, vì utility này không thưởng trực tiếp cho chất lượng.

#### P2 — Prediction tối ưu dưới quadratic score

**Điều kiện:** giữ nguyên peer strategy; xét quan sát I có xác suất dương; đặt `q=P(r_k=1|I)`. Own prediction chỉ ảnh hưởng prediction score của chính Judge.

```text
E[Q(p,r_k)|I] = q*(2*p-p^2) + (1-q)*(1-p^2)
              = 1-q+q^2 - (p-q)^2
```

**Phát biểu và chứng minh:** prediction score đạt tối đa duy nhất tại `p=q`, kể cả q bằng 0 hoặc 1; chênh lệch score với p bất kỳ bằng `(p-q)^2`. Trong utility RBTS, mất mát tương ứng là `lambda*(p-q)^2`, nên uniqueness của lựa chọn tối ưu theo utility đòi hỏi `lambda>0`. Khi lambda bằng 0 hoặc dùng fixed reward, mọi p hòa về utility.

Đây là kết quả về best response khi peer cố định, không bắt người chơi báo prediction trung thực ở mọi profile hoặc chứng minh equilibrium selection.

**Đối chiếu:** T05, T19; cho phép loại prediction liên tục bằng giải tích khi tìm candidate thuần.

#### P3 — Giá trị thông tin trước chi phí không âm

**Điều kiện:** `I_L=Z`, `I_H=(Z,X_i)`; H có thể bỏ qua X_i; giữ nguyên phân phối trạng thái, peer report/prediction tables và scoring khi so sánh. `V_H,V_L` tối ưu cả own report và own prediction trước khi trừ chi phí.

**Phát biểu:** với mỗi Judge và mỗi nhánh Z, `V_H,i(z)>=V_L,i(z)`.

**Chứng minh:** mọi quy tắc report/prediction khả thi ở L đều thực hiện được ở H bằng cách bỏ qua X_i. Tối ưu trên tập lớn hơn không thể giảm expected score. Điều này so sánh hai lựa chọn của một Judge với cùng peer cố định; không so utility của all-H với all-L.

Riêng prediction component, đặt `q_H=P(r_k=1|Z,X_i)` và `q_L=P(r_k=1|Z)`. Luật kỳ vọng lặp cho `E[q_H|Z]=q_L`. Kết hợp P2:

```text
E[max_p E[Q(p,r_k)|Z,X_i] | Z] - max_p E[Q(p,r_k)|Z]
    = E[q_H^2|Z] - q_L^2
    = E[(q_H-q_L)^2|Z]
```

Đẳng thức variance này áp dụng cho **prediction gain**, không phải toàn bộ information score hoặc tổng score. Incentive ròng vẫn là `Delta_i(z)=lambda*(V_H,i(z)-V_L,i(z))-c_i`; nó có thể âm dù P3 đúng.

**Đối chiếu:** T07, T12–T14; không thay peer tables khi tính hai vế.

#### P4 — Cân bằng không effort đạt score tối đa

**Điều kiện:** cùng quan sát public Z, mọi Judge có thể chọn cùng một quy tắc nhị phân `g(Z)`, prediction được phép nhận endpoints 0/1; `lambda>0`, `c_i>0`.

**Phát biểu:** profile `e_i=L, r_i=g(Z), p_i=g(Z)` cho cả ba Judge là một cân bằng thuần và cho `Score_i=2` tại mọi trạng thái. Chọn `g(Z)=Z` được all-Z; các trường hợp hằng số cho all-PASS/all-FAIL.

**Chứng minh:** `p_j` bằng 0 hoặc 1 nên `delta_j=0`, shadow bằng `g(Z)`, và `r_k=g(Z)`. Mỗi Q bằng 1. Score không thể vượt 2, nên deviation không thể tăng reward trên `f+2*lambda`; H còn mất thêm chi phí dương. Không có unilateral deviation sinh utility lớn hơn.

Đây không phải strict equilibrium đối với mọi thành phần strategy: với peer giữ endpoints, thay riêng own report có thể không đổi score vì shadow không đổi. Không suy ra coalition stability hoặc dự đoán hệ thống nhất thiết hội tụ tới profile này. Với lambda bằng 0, tính không effort đi theo P1; prediction không còn duy nhất.

**Đối chiếu:** T03, T08; không cần kênh liên lạc hoặc ground-truth oracle cho phản ví dụ này.

#### P5 — G1 có đồng thời cân bằng high-effort và low-effort

**Điều kiện instance:** `pi=1/2, a=7/10, b=4/5`, ba chi phí `c_i=1/20`, `lambda=1, f=0`, thông tin và timing tại mục 4–5. Candidate high là `e_i=H,r_i=X_i`, prediction Bayesian theo `(Z,X_i)` cho cả ba Judge; candidate low là all-Z ở P4.

**Phát biểu:** cả hai candidate là cân bằng thuần trong game M1 này. Độ chính xác majority lần lượt là `112/125` và `7/10`; low-effort có utility cao hơn cho từng Judge trong instance này. Đây không phải định lý cho mọi tham số hoặc bằng chứng về equilibrium selection.

**Chứng minh candidate high:**

1. Với peer giữ candidate strategy, prediction tối ưu lần lượt là `8/31,11/19,8/19,23/31` ở `(Z,X_i)=(0,0),(0,1),(1,0),(1,1)`, theo Bayes và P2.
2. Tính `A_i(I,r)` đúng theo joint distribution ở mục 4. Chênh lệch information score giữa report X_i và report đối lập đều dương:

| `(Z,X_i)` | `A_i(I,X_i)-A_i(I,1-X_i)` |
| --- | --- |
| `(0,0)` | `31981824/268863775` |
| `(0,1)` | `31981824/164787475` |
| `(1,0)` | `31981824/164787475` |
| `(1,1)` | `31981824/268863775` |

Do đó report tối ưu ở H là X_i; không phải giả định ép sẵn. Khi thử L, cả hai report hòa về information score trong G1; P2 vẫn xác định prediction tối ưu theo Z.

3. Sau khi tối ưu report và prediction ở từng observation, tại **cả hai** nhánh Z:

```text
V_L,i(z) = 3611/2500
V_H,i(z) = 334433762/216825625
Delta_i(z) = V_H,i(z)-V_L,i(z)-1/20
           = 10409548/216825625 > 0
```

H tốt hơn mọi lựa chọn L; các quy tắc report/prediction khác trong H không tốt hơn lựa chọn đã tối ưu. Mô hình và vai trò cyclic đối xứng theo phép hoán vị vòng A→B→C, nên các kiểm tra trên áp dụng cho từng Judge. Vì mọi Z có xác suất dương và không có ràng buộc nối nhánh, không có strategy deviation hợp lệ nào tốt hơn candidate high.

4. Candidate low là cân bằng theo P4. Utility high mỗi Judge là `1294369923/867302500`, trong khi utility low là 2. Accuracy theo majority được tính từ phân phối trạng thái: `3*b^2-2*b^3=112/125` ở high và a bằng `7/10` ở low.

**Trạng thái bằng chứng:** các số hữu tỉ ở đây đã được đối chiếu bằng checker tham chiếu và phép tính có điều kiện trực tiếp. Khi analyzer chính được xây, G1 certificate phải ghi đủ từng i,z, report margins, prediction, effort utility và regret bằng 0. Không dùng việc một script in `true` thay cho kiểm tra phạm vi của thuật toán. Exact computation cùng lập luận bao phủ mọi deviation có thể chứng nhận instance hữu hạn; không tự chứng minh toàn bộ miền tham số.

**Đối chiếu:** T05, T09, T12–T15. G1 là kết quả nền để xác nhận phương pháp; tính mới so với literature phải được đánh giá riêng.

## 10. Decision và mất mát tài chính

Decision baseline của M1 là majority trên ba report:

```text
D = 1[r_A+r_B+r_C >= 2]
```

Scoring không đọc D hoặc Y. Evaluator được dùng Y để xuất riêng:

| Metric | Định nghĩa |
| --- | --- |
| `accuracy` | `P(D=Y)` |
| `false_approval_rate` | `P(D=1 \| Y=0)` |
| `false_rejection_rate` | `P(D=0 \| Y=1)` |
| `wrong_payout_probability` | `P(Y=0,D=1)` |
| `wrong_payout_value` | `V * P(Y=0,D=1)` |
| `expected_payout` | `V * P(D=1)` |
| `expected_reward_total` | `sum_i E[Reward_i]` |
| `expected_effort_cost` | `sum_i c_i*P(e_i=H)` |
| `expected_judge_utility` | Reward trừ effort cost, từng Judge |
| `operating_cost` | Hằng số công bố trước, mặc định 0 |
| `cash_review_cost` | Reward cộng operating cost |

Không cộng effort cost vào cash_review_cost rồi tiếp tục trừ lần nữa trong utility; xuất effort cost như chi phí tài nguyên riêng. Runtime Python là metric hiệu năng máy tính, không tự coi là chi phí review con người.

M1 luôn có ba report nhị phân nên không có tie hoặc INCONCLUSIVE trong decision baseline. Không giả tạo dữ liệu timeout/liveness từ mô hình không có các hành động đó. M3 sẽ cần policy claim aggregation riêng.

## 11. Các kết quả chuẩn phải tái lập

### 11.1. Golden G1 — Hai peer H và báo X

```json
{
  "model_version": "ceav-m1-v1.0",
  "pi": "0.5", "a": "0.7", "b": "0.8",
  "costs": ["0.05", "0.05", "0.05"],
  "f": "0", "lambda": "1", "fixed_reward": "2",
  "reward_budget": "6", "payout_value": "1"
}
```

Candidate: cả ba chọn H với report `r_i=X_i`, prediction Bayesian theo `(Z,X_i)`. Khi tính deviation, peer prediction tables của candidate này phải giữ nguyên.

| Đại lượng của focal A | Exact | Xấp xỉ |
| --- | --- | ---: |
| V_L | `3611/2500` | 1.444400000000 |
| V_H | `334433762/216825625` | 1.542408845818 |
| V_H-V_L | `85003317/867302500` | 0.098008845818 |
| Delta utility | Delta score trừ `1/20` | 0.048008845818 |
| Ngưỡng lambda tại c=0.05 | `(1/20)/(85003317/867302500)` | 0.510158033009 |
| H information score | Exact enumeration | 0.753750102185 |
| H prediction score | Exact enumeration | 0.788658743633 |

Prediction tối ưu của H theo `(Z,X_i)`: `(0,0):8/31`, `(0,1):11/19`, `(1,0):8/19`, `(1,1):23/31`. Prediction L theo Z: `0:19/50`, `1:31/50`. Trong G1, information score của L có tie giữa hai report; không được ghi report L là nghiệm duy nhất.

Trong G1, H report tối ưu là X_i, và Delta dương ở cả hai nhánh Z. Candidate all-H này vượt kiểm tra lệch đơn phương. Đây là kết quả của mô hình cụ thể, không phải mọi cấu trúc evidence.

### 11.2. Golden G2 — Dùng tín hiệu chung

Candidate: mọi Judge chọn L, báo `r_i=Z`, prediction `p_i=Z`.

```text
Score_i = 2 ở mọi trạng thái
Utility_i = f + 2*lambda
H không thể tăng reward trên maximum và phải trả chi phí.
```

Với chi phí dương, đây là một cân bằng không effort. Tương tự có all-PASS, all-FAIL và `r_i=1-Z,p_i=1-Z`. Những cân bằng này không cần kênh liên lạc trực tiếp; chúng không chứng minh cơ chế chống thông đồng.

| Decision metric, G1 parameters | all-Z | all-H báo X |
| --- | ---: | ---: |
| Accuracy | 0.700 | 0.896 |
| False approval có điều kiện Y=0 | 0.300 | 0.104 |
| Wrong payout probability | 0.150 | 0.052 |
| Wrong payout value với V=1 | 0.150 | 0.052 |

All-Z có utility cao hơn all-H cho từng Judge trong mẫu này. Báo cáo phải giữ kết quả bất lợi đó; tăng lambda không loại bỏ cân bằng đạt score maximum.

### 11.3. Golden G3 — Thông tin chung tốt hơn decision dựa riêng vào X

`pi=0.5,a=0.9,b=0.75,c=0.05,lambda=1`, giữ candidate peer H báo X:

```text
V_L = 149/100 = 1.49
V_H = 23833/15680 = 1.519961734694
Delta score = 2349/78400 = 0.029961734694
Delta utility = -0.020038265306
```

All-H báo X không phải cân bằng với chi phí này. Nếu vẫn đánh giá decision của profile đó, accuracy majority X là `0.84375`, thấp hơn accuracy `0.9` của all-Z. Có thêm thông tin không đồng nghĩa report/aggregation đang dùng khai thác thông tin tốt nhất.

### 11.4. Golden G4 — Kỳ vọng gộp che lệch chiến lược sau Z

`pi=0.8,a=0.7,b=0.8,c=0.05,lambda=1`, candidate all-H báo X:

```text
Delta utility | Z=0 = +0.052761032028
Delta utility | Z=1 = -0.009320080021
```

Kỳ vọng gộp của Delta vẫn dương, nhưng Judge được chọn effort sau Z. All-H không phải cân bằng: khi Z=1 có lợi nếu đổi sang L. Đây là regression bắt buộc để không dùng trung bình sai thời điểm.

## 12. Hợp đồng đầu vào, CLI và đầu ra cần xây

### 12.1. JSON config

Số hữu tỉ phải là chuỗi thập phân hoặc `numerator/denominator`, đọc trực tiếp bằng Fraction; không đi qua float. Config dùng schema cố định, từ chối field không biết để phát hiện lỗi chính tả.

Các trường: `model_version, pi, a, b, costs[3], f, lambda, fixed_reward, reward_budget, payout_value, operating_cost`. `operating_cost` mặc định `"0"`; các trường còn lại bắt buộc. Model version sai, tham số sai miền hoặc budget không đủ phải trả lỗi trước khi chạy.

Profile JSON riêng chứa action của A/B/C tại từng Z, ví dụ all-H: `{"0":["H01","H01","H01"],"1":["H01","H01","H01"]}`. Prediction được dựng từ profile; nếu command cho nhập prediction thủ công để kiểm tra sai lệch thì phải xác nhận miền và đo cả prediction regret, không âm thầm thay nó bằng prediction tối ưu.

### 12.2. CLI mục tiêu, chưa phải lệnh đã triển khai

```powershell
python -m unittest discover -s tests -v
python -m ceav_m1 analyze --config configs/golden_g1.json --profile configs/all_high.json --mechanism rbts --out results/g1
python -m ceav_m1 equilibria --config configs/golden_g1.json --mechanism rbts --out results/g1_equilibria
python -m ceav_m1 sweep --config configs/sweep.json --profile configs/all_high.json --mechanism rbts --out results/sweep
python -m ceav_m1 compare --config configs/golden_g1.json --profile configs/all_high.json --out results/comparison
python -m ceav_m1 serve --port 8765
```

`sweep` bản đầu chỉ lặp **analyze trên một profile cố định và một mechanism được chọn bằng CLI**; không tìm toàn bộ cân bằng tại từng điểm. `sweep.json` có `base_config` trỏ tới config đầy đủ và `axes` với danh sách chuỗi hữu tỉ cho `pi,a,b,c,lambda`; `c` đặt bằng nhau cho ba Judge. Quét tích Descartes, ghi cả điểm vi phạm budget là `invalid_budget`, không âm thầm bỏ. Mỗi hàng hợp lệ gồm metrics, Delta/regret theo từng i,z và trạng thái của candidate cố định. Ghi cơ chế và profile hash trong manifest. Thực hiện sweep sau khi analyze và equilibria qua acceptance; không chạy grid lớn trước đó.

Không dùng q-grid hoặc p-grid trong CLI bản đầu. Mỗi output directory phải mới; nếu đã tồn tại thì dừng với thông báo rõ, không ghi đè kết quả cũ. Đường dẫn trong config/profile được giải tương đối với file chứa chúng; output được giải tương đối với cwd.

`compare` chạy analyze cho fixed reward và RBTS trên cùng config/profile; yêu cầu `F=f+2*lambda` và cả hai không vượt B. Tạo hai thư mục con `fixed/`, `rbts/` chứa đủ artifact analyze, cùng manifest/summary/report tổng hợp tại thư mục comparison. Đây là so sánh candidate cố định giữa hai cơ chế; không được gọi là so sánh toàn bộ cân bằng. Cùng trần thưởng không có nghĩa cùng thực chi.

`serve` mặc định bind `127.0.0.1`, mở địa chỉ `http://127.0.0.1:8765` để người dùng truy cập. Nếu port đã bận, thông báo rõ và cho chọn port bằng cờ CLI; không âm thầm chuyển port. Sau bước khởi động này, mọi thao tác phân tích và test phải thực hiện được trên HTML. Chi tiết API và tác vụ ở mục 18.

### 12.3. Artifact theo từng command

| File | Nội dung |
| --- | --- |
| `manifest.json` | Model/engine/spec revision, Python version, canonical config/profile, SHA-256, command, scope, thời điểm UTC; tham chiếu snapshot và freeze status ở mục 19 |
| `summary.json` | Analyze: metrics, utility từng Judge, regret tối đa, trạng thái equilibrium và budget; equilibria: counts và scope |
| `best_responses.json` | Chỉ analyze: chi tiết từng i,z và từng quan sát; deviation witness hoặc ties |
| `states.csv` | Chỉ analyze: 32 trạng thái, probability, action/report/prediction/score từng Judge, decision |
| `report.md` | Kết luận, giả định và giới hạn sinh từ các file số liệu |
| `equilibria.json` | Chỉ equilibria: danh sách 216 ứng viên/nhánh cùng trạng thái; cân bằng giữ lại có đủ certificate best response; ứng viên bị bác có deviation witness; mô tả cách ghép nhánh |
| `sweep.csv` | Chỉ sweep: một hàng mỗi parameter tuple trên profile cố định, gồm lỗi validation nếu có |
| `test_results.json` | Chỉ test run: test ID, pass/fail/error/skipped/not_run, duration và lỗi thực tế |
| `test_log.txt` | Chỉ test run: stdout/stderr của runner để chẩn đoán và tải xuống |

Manifest và report bắt buộc cho mọi command. Sweep không cần summary.json, states.csv hoặc bảng best response đầy đủ cho từng điểm; chạy lại một hàng bằng analyze để lấy các artifact chi tiết. Equilibria không bắt buộc tạo 32 hàng trạng thái cho mọi profile, vì certificate được nhúng trong equilibria.json. Report của sweep phải gọi kết quả là phân tích candidate cố định, không phải bản đồ mọi cân bằng.

Comparison có cấu trúc được mô tả ở mục 12.2. Test run có manifest, report, test_results và test_log; không tạo metrics giả khi test chưa chạy hoặc bị hủy.

Giá trị chính xác lưu `{ "exact": "3611/2500", "decimal": 1.4444 }`; decimal chỉ để xem. CSV có cột `_exact` và `_decimal`. Thứ tự trạng thái, Judge, nhánh và action phải cố định để kết quả diff được.

Hash cấu hình từ JSON normalized với số chuyển về fraction canonical, keys sắp xếp và encoding UTF-8. Không đưa timestamp vào hash ngữ nghĩa. Manifest ghi engine revision nếu có Git, ngược lại ghi hash nội dung source; không bắt buộc khởi tạo Git. Run exact không cần seed; ghi `randomness: "none"`, không tạo seed giả.

Mẫu trường kết luận:

```json
{
  "strategy_scope": "pure_effort_report_with_continuous_optimal_predictions",
  "equilibrium_concept": "pure_strategy_nash_in_reduced_normal_form",
  "scoring_rule": "rbts_eq8",
  "effort_timing": "after_public_signal",
  "arithmetic": "rational_exact",
  "peer_tables_frozen_on_deviation": true,
  "equilibrium_status": "exact_pure_equilibrium",
  "claims_mixed_equilibrium_coverage": false,
  "claims_equilibrium_selection": false
}
```

## 13. Tính đúng và hiệu năng

- Dùng Fraction cho mọi nhánh quyết định, tie, posterior và certificate.
- Tính xác suất điều kiện bằng tổng trạng thái phù hợp chia tổng khối lượng, không dựa vào assumption chưa khai báo.
- Cache posterior/report/prediction trong cùng profile khi có ích; cache không được dùng nhầm sang candidate khác.
- Với peer cố định, tối ưu report nhị phân bằng so sánh hai expected information scores; tối ưu p bằng công thức giải tích.
- Named profiles tối thiểu: all-PASS, all-FAIL, all-Z, all-(1-Z), all-H báo X, all-H báo (1-X), cùng các profile bất đối xứng do enumeration tạo.
- Không gắn nhãn coalition stability chỉ vì all-Z Pareto tốt hơn all-H; chứng nhận coalition cần bài toán deviation riêng.
- Phải đo thời gian cho analyze và exhaustive pure search trên máy chạy. Không đặt mục tiêu tốc độ tùy ý làm lý do chuyển sang xấp xỉ trước khi có benchmark.

## 14. Test bắt buộc và tiêu chí nghiệm thu

| ID | Kiểm tra | Kết quả phải đạt |
| --- | --- | --- |
| T01 | Phân phối trạng thái | Đúng 32 trạng thái; tổng xác suất bằng 1 chính xác |
| T02 | Bảo mật thông tin của mô hình | L không đọc X; strategy không đọc Y hoặc X của peer |
| T03 | Q và bounds | Q tại 0/1 đúng; `0<=shadow<=1`, `0<=Score<=2` |
| T04 | Vai trò RBTS | Cyclic reference/peer đúng; không dùng chính i làm j/k |
| T05 | Prediction tối ưu | Chứng minh `E Q(q,R)-E Q(p,R)=(p-q)^2`; thử số hữu tỉ và endpoints |
| T06 | Fixed reward | Với c>0, H không thể là best response effort; c=0 là tie |
| T07 | Tín hiệu không thông tin | Với b=0.5, `V_H=V_L` với peer cố định; H mất thêm c |
| T08 | All-PASS/FAIL/Z/(1-Z) | Score=2, regret=0 với chi phí dương; H không có lợi |
| T09 | Golden G1 | Số chính xác tại mục 11 khớp; report H=X; giữ ties ở L |
| T10 | Golden G3 | Delta âm; all-H báo X bị bác; accuracy theo bảng đúng |
| T11 | Golden G4 | Phát hiện deviation ở Z=1 dù Delta gộp dương |
| T12 | Peer freeze | Snapshot peer tables bất biến khi focal thử effort/report khác |
| T13 | Joint expectation | Hand-calculated fixture có p_j và r_k tương quan; không nhân kỳ vọng sai |
| T14 | Value of information | `V_H>=V_L`; prediction gain bằng `E[(q_H-q_L)^2\|Z]` |
| T15 | Regret | Không âm; certificate gồm deviation witness tái tính được |
| T16 | Enumeration completeness | Đúng 6 actions/Judge/z, 216 candidates/z; giữ H00/H11 và mọi report tie |
| T17 | Branch factorization | Với một config, so sánh tập nghiệm branch product với kiểm tra trực tiếp 46,656 full profiles |
| T18 | Label symmetry | Đổi nhãn toàn bộ Y,Z,X,r và pi->1-pi: utility/accuracy giữ; FP và FN hoán đổi |
| T19 | Lambda và f | f không đổi regret; lambda=0 xử lý như thưởng hằng số; threshold G1 đúng |
| T20 | Budget và output | Reject vượt trần; cùng trần không bị ghi thành cùng thực chi; exact serialization round-trip |
| T21 | Reproducibility | Cùng input/source cho cùng numeric output và config hash, bỏ qua timestamp/runtime |
| T22 | CLI | Invalid config trả exit khác 0; thành công tạo đủ artifact; không ghi đè thư mục run |
| T23 | Khởi động HTML local | Một lệnh serve; tải đủ asset khi offline; API báo đúng khả năng engine và lỗi startup |
| T24 | Form và import/export | Preset G1–G4, mọi tham số/action map chỉnh được; chuỗi phân số giữ nguyên; validation cùng quy tắc engine |
| T25 | UI/CLI parity | Cùng config/profile cho cùng exact output và config hash; tái lập G1–G4 qua trình duyệt |
| T26 | Best response trên UI | Hiển thị đủ i,z, effort/report/prediction tối ưu, ties và deviation witness; G4 không bị báo cân bằng |
| T27 | Equilibrium explorer | Duyệt đủ 216 profile/nhánh; lọc/xem certificate và chuyển candidate sang màn hình analyze |
| T28 | Sweep trên UI | Chọn profile/cơ chế cố định và axes; preview số điểm; giữ hàng lỗi budget; bảng/biểu đồ khớp artifact |
| T29 | Test runner trên UI | Chạy reference, golden, toàn bộ engine/API suite hoặc nhóm được chọn; lỗi thật hiện thành fail/error, test thiếu hiện not_run |
| T30 | Tác vụ và comparison | Tiến trình thật, không chạy trùng, hủy được; cancelled không thành passed; comparison đúng cùng trần và ghi thực chi |
| T31 | Lịch sử và API local | Mở lại run, tải đúng artifact; chặn path traversal, tác vụ tùy ý và request ghi từ origin không được phép |
| T32 | UX và browser acceptance | Kiểm tra trên trình duyệt ở 1366×768 và 390×844; bàn phím, focus, label, tương phản, lỗi form và bảng rộng dùng được |

Golden values độc lập với runtime implementation: không tạo expected bằng chính hàm đang được test. Có ít nhất một đường tính payoff trực tiếp từ trạng thái để đối chiếu đường tối ưu theo conditional groups.

### Định nghĩa hoàn thành hệ thống M1

- T01–T32 đều qua, có log và lệnh tái lập; browser acceptance có ảnh và kết quả thao tác thật. P1–P5 có đối chiếu test theo mục 9.4; G1 certificate bao phủ report/prediction/effort ở từng i,z.
- Analyze tái lập G1–G4, chứng nhận hoặc bác candidate đúng, có witness.
- Pure search duyệt đủ phạm vi, xuất certificates và count; kết quả âm không bị ẩn.
- Report luôn ghi rõ miền tham số, timing, no slashing, no ground-truth reward, no mixed/coalition guarantee.
- Có một run so sánh fixed/RBTS cùng trần và ghi actual spend.
- Giao diện HTML bắt buộc, gọi engine thật, có đủ các chức năng tại mục 18 và hiển thị kết quả đúng với CLI.
- Không cần blockchain, nhiều triệu simulation hoặc một cơ chế reward mới để gọi bản M1 hoàn thành.

## 15. Thứ tự triển khai

1. **Model + scoring + evaluator:** dựng state, posterior, score, metric → T01–T05, G1/G2/G3.
2. **Best-response engine:** đóng băng peer, tối ưu report/prediction/effort theo z → T06–T15, G4.
3. **Pure-equilibrium search:** 216 profiles/z và branch product → T16–T19.
4. **CLI + artifacts + sweep nhỏ:** manifest, CSV/JSON/report và budget → T20–T22.
5. **HTML + local API:** form, analysis, equilibrium, sweep, comparison, test runner và run history → T23–T31.
6. **Browser và acceptance run:** thao tác thật, kiểm tra responsive và chạy toàn bộ suite → T01–T32. Sau đó mới quyết định bước M2.

Ngay trước bước 1, tạo snapshot implementation-start theo mục 19. Checker tham chiếu đã có trước bước này; không mô tả toàn bộ công việc viết mã là diễn ra sau thời điểm đóng băng.

Không mở rộng M2/M3 để né một kết quả âm ở M1. M1 không có assignment nhiều claim, nên kết quả của nó chưa chứng minh lợi ích của claim-based assignment.

## 16. Cách kiểm tra các mốc của tài liệu ngay bây giờ

Checker dưới đây chỉ là công cụ kiểm chứng các kết quả chuẩn và timing; nó không thực hiện pure-equilibrium search, CLI analyzer, HTML UI hay toàn bộ T01–T32:

```powershell
Set-Location 'C:\Users\dell\Desktop\fundtogether_data_analyzing'
python verification/verify_reference.py --output verification/reference_results.json
```

Nguồn và phạm vi các định lý: [PRIMARY_SOURCES.md](references/PRIMARY_SOURCES.md). Nguồn học thuật giải thích cơ chế và giới hạn; G1–G4 là kết quả tự tính của mô hình đã định nghĩa ở đây, không phải số liệu đo từ người dùng hoặc hiệu năng sản phẩm.

## 17. Trạng thái bàn giao của phiên bản tài liệu này

- Đã tạo đặc tả, đối chiếu nguồn và chạy checker độc lập bằng Python 3.12.
- Đã tái lập G1–G4 bằng Fraction, kiểm tra score maximum của các profile không effort, ties ở L, prediction tối ưu và regression chọn effort sau Z.
- Đã kiểm tra liên kết nội bộ, code fences, UTF-8 và khả năng sinh lại JSON giống nhau từng byte.
- `verification/reference_results.json` có SHA-256 `85622a6a7d2a03b787009b9a2f21a6fc7079dd87276b5ed7eb2cbd22c1ff7209`.
- Bản cập nhật `html-ui-r1` đã bổ sung yêu cầu HTML/local API và các test T23–T32; không thay đổi mô hình toán hoặc các kết quả chuẩn.
- Bản cập nhật `math-proof-r2` chuẩn hóa tên scoring/cân bằng, bổ sung P1–P5 và quy trình snapshot; không đổi công thức, strategy space, timing hoặc G1–G4.
- **Chưa xây analyzer hoàn chỉnh, HTML UI hoặc local API; chưa chạy exhaustive pure-equilibrium search, chưa hoàn thành suite T01–T32.** Các mục đó là tiêu chí nghiệm thu cho giai đoạn implementation theo tài liệu này.

### Theo dõi SPECIFIED / IMPLEMENTED / VERIFIED

Ba trạng thái độc lập: SPECIFIED là đã định nghĩa trong tài liệu; IMPLEMENTED là có code/artifact đúng component; VERIFIED là đã kiểm tra trong phạm vi nêu rõ và có evidence. Có checker tham chiếu không làm component analyzer chính tự chuyển sang IMPLEMENTED hoặc VERIFIED.

| Component | SPECIFIED | IMPLEMENTED | VERIFIED / evidence hiện tại |
| --- | --- | --- | --- |
| State model và RBTS scoring của analyzer chính | Có | Chưa | Chưa nghiệm thu engine chính |
| Best-response engine chính | Có | Chưa | Chưa nghiệm thu engine chính |
| Exhaustive pure-equilibrium search | Có | Chưa | Chưa chạy; chưa có certificate từ analyzer chính |
| G1–G4 trong checker tham chiếu | Có | Có, tại `verification/verify_reference.py` | Đã chạy exact reference checks; kết quả tại `verification/reference_results.json` |
| P1–P4 | Có, phát biểu và chứng minh ở mục 9.4 | Chứng minh trong tài liệu; chưa có suite engine chính | Đối chiếu đại số và kiểm tra tham chiếu liên quan; không tuyên bố proof-assistant verification |
| P5 / G1 | Có, instance và lập luận ở mục 9.4 | Có checker tham chiếu; chưa có G1 certificate của engine chính | Đã đối chiếu exact values, report margins và hai nhánh Z; không suy rộng mọi tham số |
| T01–T22 | Có | Chưa có đầy đủ suite | Chưa nghiệm thu suite |
| HTML và local API | Có, bắt buộc | Chưa | Chưa browser/API acceptance |
| T23–T32 | Có | Chưa | Chưa nghiệm thu suite |
| Snapshot revision tài liệu | Có, mục 19 | Có snapshot và manifest tại spec_history | SHA-256 đối chiếu raw bytes; không đồng nghĩa đã bắt đầu/freeze implementation |

Mỗi lần đổi trạng thái phải thêm lệnh kiểm tra hoặc đường dẫn artifact/commit tương ứng. Không dùng màu xanh, nhãn hoàn thành hoặc ngày dự kiến thay cho evidence. Run manifest ghi riêng engine revision và spec revision để không đánh đồng hai loại thay đổi.

## 18. Giao diện HTML — bắt buộc khi triển khai

### 18.1. Mục tiêu sử dụng

Tạo một phòng thí nghiệm CEAV-M1 dùng được bằng trình duyệt, không chỉ một trang hiển thị kết quả có sẵn. Người dùng phải sửa giả định, chạy tác vụ, xem chứng cứ, tìm nguyên nhân kết quả và tải artifact mà không cần sửa Python.

```text
HTML/CSS/JavaScript
       ↓ JSON request; tham số hữu tỉ vẫn là chuỗi
Python local API
       ↓ cùng model/evaluator/test runner với CLI
Engine Fraction → artifact trong results/<run_id>/
       ↓ trạng thái thật và kết quả đã ghi
UI: bảng, biểu đồ, certificate, log và tải xuống
```

Frontend không tính lại score, posterior, best response hoặc equilibrium bằng floating point. JavaScript chỉ định dạng kết quả và vẽ biểu đồ từ decimal đi kèm; giá trị exact do Python trả về là nguồn để so sánh và xuất dữ liệu. Các preset chỉ là input; không gắn cứng kết quả mẫu vào UI.

### 18.2. Bố cục và tiêu chuẩn dễ dùng

- Giao diện tiếng Việt; thuật ngữ có chú giải ngắn: effort, peer prediction, regret, false approval và trần thưởng.
- Nền sáng, chữ tối rõ, khoảng cách thoáng; một vùng làm việc chính, tiêu đề và nút chạy dễ nhận biết. Tránh nhồi các ô thông tin lồng nhiều tầng.
- Navigation gồm: **Phân tích**, **Tìm cân bằng**, **Quét tham số**, **So sánh**, **Kiểm thử**, **Lịch sử**. Chuyển màn hình giữ bản nháp config/profile trong phiên.
- Màn hình phân tích chia form bên trái và kết quả bên phải trên desktop; xếp dọc ở màn hình hẹp. Bảng rộng có vùng cuộn ngang riêng, header rõ, cột số căn phải.
- Kết quả ưu tiên: tiền giải ngân sai kỳ vọng, false approval, lợi ích ròng của effort theo từng Z, chi phí review và trạng thái cân bằng. Ghi rõ đơn vị chuẩn hóa và mẫu số của tỷ lệ.
- Có các trạng thái chưa chạy, input lỗi, đang chạy, thành công, thất bại, đã hủy và kết quả không còn khớp bản nháp. Không để màn hình trống hoặc dùng giá trị 0 thay cho dữ liệu chưa có.
- Nút có nhãn hành động rõ; form có label, mô tả miền hợp lệ và lỗi tại trường tương ứng. Dùng input text cho số hữu tỉ, ví dụ `0.05` hoặc `1/20`; không dùng slider làm cách nhập duy nhất.
- Có focus nhìn thấy, thao tác bằng bàn phím, thông báo trạng thái đọc được qua `aria-live`; không dùng riêng màu để biểu thị pass/fail hoặc Delta âm/dương. Mỗi biểu đồ có bảng số liệu tương ứng.
- Không cần login, kết nối ví hoặc Internet. Phần giải thích mặc định ngắn; công thức, exact fractions và log đầy đủ mở ở vùng chi tiết khi cần.

### 18.3. Phân tích và thiết kế kịch bản

1. Nạp preset G1–G4 hoặc cấu hình tùy chỉnh. Với G2 có các profile all-Z, all-PASS, all-FAIL và all-(1-Z).
2. Chỉnh `pi,a,b`, chi phí A/B/C, `f,lambda,F,B,V,operating_cost`; chọn fixed reward hoặc RBTS. UI giải thích tham số nhưng không thay đổi miền tại mục 4.
3. Profile editor có sáu lựa chọn action cho từng Judge ở cả hai nhánh Z; nạp nhanh all-H, all-Z và các profile đã chọn từ equilibrium explorer. Prediction Bayesian được dựng bởi engine và hiện trong kết quả.
4. Validate trước khi chạy; xem và tải config/profile JSON. Cho nhập lại bằng file JSON, báo rõ field sai hoặc không được hỗ trợ.
5. Chạy analyze và xem utility/score từng Judge, false approval/rejection, wrong payout, actual reward và trần thưởng. Hiển thị exact fraction bên cạnh decimal hoặc trong chi tiết.
6. Mở bảng best response theo Judge/Z, xem optimal report/prediction, tie và deviation witness. Có nút lấy deviation tìm được làm candidate mới rồi chạy lại; giữ run gốc.
7. Xem đủ 32 trạng thái, lọc theo Y/Z/decision, kiểm tra xác suất và đóng góp vào wrong payout; tải CSV/JSON/report từ run thật.

Nếu cho nhập prediction thủ công, đó phải là một chế độ rõ ràng, có kiểm tra prediction regret đầy đủ như mục 12.1. Không thêm ô prediction có vẻ chỉnh được nhưng engine âm thầm thay bằng Bayesian prediction.

### 18.4. Tìm cân bằng thuần

- Dùng config hiện tại; chọn fixed hoặc RBTS; preview phạm vi 216 candidates/nhánh và 46,656 profile effort/report đầy đủ.
- Hiển thị số candidates đã kiểm tra trên tổng, cân bằng mỗi nhánh và số tổ hợp đầy đủ. Chỉ dùng progress có dữ liệu từ backend; nếu chưa có count thì hiện trạng thái đang xử lý, không chạy phần trăm giả.
- Bảng kết quả lọc được theo Z, action của A/B/C, effort và trạng thái candidate. Xem certificate của cân bằng hoặc witness bác bỏ candidate.
- Cho chọn một kết hợp giữa hai nhánh và mở analyze để xem decision metrics đầy đủ. Không suy ra accuracy của full profile chỉ từ bảng effort.
- Hiển thị rõ đây là pure-equilibrium search; không gắn nhãn đã tìm hết mixed equilibria hoặc đã giải quyết equilibrium selection.

### 18.5. Quét tham số và so sánh

**Quét tham số:** chọn config cơ sở, profile cố định, cơ chế và danh sách giá trị hữu tỉ cho các axes được hỗ trợ. Preview số điểm, cho người dùng sửa trước khi chạy. Bảng giữ cả các điểm `invalid_budget`, không chỉ hiện điểm thuận lợi. Khi có một axis, có biểu đồ Delta/regret hoặc wrong payout theo axis; với nhiều axes cho chọn một hoặc hai trục và cố định các trục còn lại. Không làm mượt hoặc nội suy để suy ra miền chưa tính. Từ một hàng có thể mở analyze bằng đúng cấu hình đó.

**So sánh:** chạy fixed và RBTS trên cùng profile/config, cùng trần theo mục 12.2. Có nút chủ động đặt `F=f+2*lambda` và giải thích thay đổi; không âm thầm đổi input. Xem utility, incentive, accuracy, wrong payout và actual spend cạnh nhau. Cho ghim hai run đã có để xem khác biệt; nếu config/profile/model version khác nhau thì chỉ rõ các khác biệt, không gắn nhãn là so sánh có kiểm soát.

Mỗi bảng/biểu đồ ghi mechanism, profile, model version và run ID; giá trị âm, invalid hoặc kết quả bác cơ chế vẫn phải hiển thị đầy đủ.

### 18.6. Trang kiểm thử đầy đủ

Có các thao tác độc lập:

| Thao tác | Phạm vi |
| --- | --- |
| Kiểm tra tham chiếu | Chạy checker thực tế trong verification, đọc kết quả và log mới |
| Chạy golden G1–G4 | Chạy engine với các preset chuẩn, so sánh exact values và trạng thái candidate |
| Chạy toàn bộ engine/API test | Chạy suite bằng runner thật; có bảng mapping T01–T31 tới các test tự động tương ứng |
| Chạy nhóm được chọn | Chọn các ID đã đăng ký; runner không nhận tên module/lệnh tùy ý từ trình duyệt |
| Xem browser acceptance | Hiển thị bằng chứng T32 và phần kiểm thử trình duyệt của các nhóm UI; không tự đánh dấu đã qua chỉ vì HTML tải được |

Hiển thị tổng pass/fail/error/skipped/not_run, thời gian chạy, danh sách test, assertion/traceback khi lỗi và log tải được. Test chưa triển khai phải là `not_run` hoặc `unavailable`; `skipped` phải kèm lý do; cả hai không được tính vào pass hoặc hoàn thành nghiệm thu.

T23–T32 bao gồm engine/API assertions và browser scenarios. Python unittest không thay thế kiểm tra thao tác trên trình duyệt. Có thể dùng công cụ browser automation của môi trường triển khai để chạy scenarios và lưu ảnh/log; không cần đưa công cụ đó thành runtime dependency của ứng dụng. Lệnh test trên trang chỉ được báo phần đã thực thi, không giả vờ đã tự kiểm tra responsive hoặc accessibility.

Tính năng test được coi là hoàn thành khi một lỗi cố ý trong fixture kiểm thử làm xuất hiện failure đúng ở giao diện và log; fixture phải tách biệt, không sửa engine/research results để diễn kịch.

### 18.7. Tác vụ, lịch sử và tải kết quả

- Snapshot config/profile tại thời điểm bấm chạy và gán run ID mới; sửa bản nháp sau đó không đổi run đang chạy. Kết quả cũ gắn nhãn khi không khớp input hiện tại.
- Mỗi lần chỉ chạy một tác vụ nặng; khóa nút submit trùng, backend cũng từ chối nếu đang bận. Không cần queue nhiều người dùng.
- Tác vụ có trạng thái queued/running/succeeded/failed/cancelled/interrupted và tiến trình thật khi engine cung cấp. Có nút hủy để dừng tiến trình tính toán; artifact dở dang ghi trạng thái cancelled, không dùng làm certificate.
- Runner tách khỏi HTTP request để trang vẫn phản hồi. Có thể dùng tiến trình Python con với argv cố định theo operation; không dựng shell command từ text người dùng. Khi hủy phải dừng cả tiến trình tính toán thuộc tác vụ đó, không chỉ ngừng polling ở trình duyệt.
- Sau khi server khởi động lại, đọc các run đã hoàn tất từ results; run dở dang chuyển interrupted, không tự tiếp tục hoặc báo thành công. In-memory job tracking là đủ cho bản đầu.
- Lịch sử có run ID, ngày chạy, loại tác vụ, cơ chế, config hash và trạng thái; cho mở lại và tải từng artifact. Không cần tính năng xóa run trong bản đầu.
- Muốn tái lập, người dùng có thể tải config/profile hoặc xem lệnh CLI tương đương trong vùng chi tiết. Giao diện không bắt người dùng chạy lệnh đó để sử dụng chức năng.

### 18.8. JSON API và ranh giới local

| Route | Trách nhiệm |
| --- | --- |
| `GET /api/status` | Phiên bản, capability thực sự có, tác vụ đang chạy |
| `POST /api/validate` | Validate config/profile bằng cùng validator với CLI |
| `POST /api/runs` | Tạo run; operation trong allowlist `analyze,equilibria,sweep,compare,tests` |
| `GET /api/jobs/{job_id}` | Trạng thái, counts, lỗi và run ID; không suy đoán progress |
| `POST /api/jobs/{job_id}/cancel` | Hủy tác vụ đang chạy hoặc trả trạng thái đã kết thúc |
| `GET /api/runs` | Liệt kê metadata run trong results |
| `GET /api/runs/{run_id}` | Metadata và danh sách artifact của run hợp lệ |
| `GET /api/runs/{run_id}/artifacts/{name}` | Đọc/tải artifact thuộc chính run, theo allowlist |

Request tạo run dùng config/profile JSON có số hữu tỉ dạng chuỗi. Với operation tests, dùng suite selector cố định `reference,goldens,all,selected` cùng các test IDs đã đăng ký. Các operation và suite phải ánh xạ tới cùng engine/test runner dùng ở CLI, không có bản công thức riêng cho frontend. Engine hoặc suite chưa có phải trả capability unavailable và lỗi rõ; không dùng dữ liệu mẫu thay kết quả thật.

Local server chỉ phục vụ static assets trong web và artifact trong results. Run ID, artifact name và path do server kiểm soát; resolve rồi kiểm tra vẫn nằm trong thư mục cho phép. Không cho UI gửi đường dẫn tuyệt đối, Python expression, module tùy ý hoặc shell command. Với thao tác tạo/hủy run, kiểm tra same-origin và session token do server sinh; không bật CORS toàn cục. Những kiểm tra này thuộc T31, không yêu cầu xây hệ thống tài khoản.

### 18.9. Tiêu chí nghiệm thu giao diện

Người kiểm thử phải thực hiện được từ trình duyệt:

1. Khởi động server, nạp G1, chỉnh một tham số và chạy analyze; exact output trùng CLI.
2. Nạp G4, thấy nhánh Z=1 có incentive âm và candidate không phải cân bằng.
3. Tìm cân bằng, mở một certificate và chuyển candidate sang analyze.
4. Chạy sweep nhỏ có điểm vượt budget; xem cả hàng lỗi, biểu đồ và cấu hình từng điểm.
5. Chạy comparison cùng trần; phân biệt actual reward spend của hai cơ chế.
6. Chạy checker, golden và suite; xem test failure thật và tải log.
7. Hủy tác vụ đang chạy; xác nhận dừng tính toán và không sinh success/certificate giả.
8. Mở lại run trong lịch sử, tải JSON/CSV/report và tái lập được config.
9. Hoàn tất các thao tác chính bằng bàn phím, kiểm tra hai kích thước màn hình ở T32, ghi lại ảnh và lỗi đã sửa.

Chỉ giao một HTML đẹp, màn hình tĩnh, nút chưa nối engine, hoặc dashboard chỉ mở reference_results.json là chưa đạt yêu cầu này.

## 19. Phiên bản, snapshot và thời điểm bắt đầu implementation

### 19.1. Phân biệt model version, spec revision và engine revision

- `model_version=ceav-m1-v1.0` định danh mô hình toán. Sửa câu chữ, bổ sung chứng minh hoặc UI mà không đổi phân phối, timing, strategy space hay payoff không tự tạo model version mới.
- `spec_revision=math-proof-r2` định danh bản đặc tả hiện tại. Bản `html-ui-r1` được lưu trước đợt chỉnh sửa này.
- Engine revision định danh code thực thi. Checker tham chiếu đã tồn tại trong quá trình xây đặc tả và không được ghi thành engine hoàn chỉnh.
- Snapshot/checksum xác định nội dung được lưu; **hash riêng lẻ không chứng minh thời điểm nội dung đó có trước code**. Cần ghi nhận event, thời gian và thứ tự snapshot/implementation, cùng commit nếu có Git.

Tại lần bàn giao này, lưu [manifest bản trước](spec_history/html-ui-r1/manifest.json) và [manifest bản hiện tại](spec_history/math-proof-r2/manifest.json). Đây là các snapshot phục vụ review; **chưa phải event bắt đầu implementation của analyzer chính**.

### 19.2. Quy tắc lưu snapshot

```text
spec_history/
├── html-ui-r1/
│   ├── CEAV_M1_SPEC.md
│   └── manifest.json
└── math-proof-r2/
    ├── CEAV_M1_SPEC.md
    └── manifest.json
```

Snapshot lưu nguyên raw bytes của file tại thời điểm chụp; SHA-256 tính trên chính bytes đó, không normalize line ending/Unicode hoặc thêm BOM. Metadata/hash nằm ở manifest riêng, không nhúng hash của chính file vào nội dung file rồi tiếp tục sửa file đó.

Manifest tối thiểu ghi spec revision, model version, snapshot filename, sha256, hash basis, event, thời gian UTC và freeze status. Khi có parent revision, ghi parent revision/hash để nối lịch sử. Timestamp là nhật ký cục bộ, không được mô tả như xác nhận thời gian độc lập của bên thứ ba.

Không sửa hoặc ghi đè snapshot/manifest đã lưu. Nếu thư mục revision tồn tại mà nội dung khác, tạo revision mới. File đặc tả chính vẫn là tài liệu làm việc; các snapshot dùng để xác minh phiên bản và cần đọc theo ngữ cảnh đường dẫn của workspace gốc.

### 19.3. Event đóng băng trước analyzer implementation

Ngay trước khi tạo code analyzer chính:

1. Kiểm tra phiên bản đặc tả dự kiến dùng; lưu snapshot mới nếu đã khác revision đang lưu.
2. Xác minh snapshot bytes và checksum khớp file dự kiến triển khai.
3. Tạo một event riêng ghi revision/hash được chọn, thời điểm UTC, `reference_checker_preexisted=true` và freeze status `frozen_at_analyzer_implementation_start`. Không đổi manifest review cũ thành event freeze.
4. Sau event đó mới bắt đầu lưu code analyzer chính; lưu commit nếu có Git, hoặc nhật ký và source hash nếu chưa có Git.

Nếu code analyzer chính đã có trước event, phải ghi thực trạng; không gán lùi thời điểm hoặc tự nhận đã preregister từ trước. Câu được phép dùng khi có bằng chứng phù hợp là: **“Đặc tả được đóng băng trước khi triển khai analyzer chính; checker tham chiếu đã tồn tại trong giai đoạn xây dựng đặc tả.”**

Thay đổi đặc tả sau event freeze phải tạo revision/snapshot mới và ghi lý do, phạm vi ảnh hưởng cùng tests cần chạy lại. Giữ nguyên snapshot và run artifacts theo revision cũ; không viết lại lịch sử để mọi run trông như dùng đặc tả mới.

### 19.4. Run manifest phải tham chiếu phiên bản thực tế

Ví dụ dưới đây là cấu trúc metadata cho run trong giai đoạn chưa freeze, không phải một run đã được thực hiện:

```json
{
  "spec": {
    "model_version": "ceav-m1-v1.0",
    "revision": "math-proof-r2",
    "snapshot": "spec_history/math-proof-r2/CEAV_M1_SPEC.md",
    "sha256": "<đọc từ manifest snapshot và xác minh raw bytes>",
    "freeze_status": "not_frozen_for_analyzer_implementation",
    "freeze_event": null,
    "reference_checker_preexisted": true
  },
  "implementation": {
    "engine_revision": "<commit hoặc source-content hash thực tế>",
    "status": "<trạng thái thực tế, không suy ra từ spec>"
  }
}
```

Sau event freeze thực sự, manifest của run mới tham chiếu event đó cùng trạng thái tương ứng. Không dùng một checksum gõ sẵn từ báo cáo khác; đọc và đối chiếu snapshot được pin cho run. Nếu checksum không khớp thì dừng run với lỗi rõ. Khi file đặc tả chính thay đổi, có thể ghi thêm current working spec hash nhưng không thay pinned spec hash của run cũ.

### 19.5. Kiểm tra phiên bản thuộc acceptance

Mở rộng T20–T21 để kiểm tra checksum snapshot, parent revision, raw-byte hashing và round-trip metadata. Phải phát hiện snapshot bị thay đổi, không nhận freeze khi event còn thiếu, và bảo toàn run manifest cũ sau khi đặc tả có revision mới. UI history/report phải hiển thị spec revision, engine revision và freeze status thực tế; không dùng nhãn VERIFIED chỉ vì manifest tồn tại.
