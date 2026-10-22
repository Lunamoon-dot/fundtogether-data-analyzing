# CEAV-M1 — Hướng dẫn từ đầu: biến, thông số, tác động và cách dùng

**Dành cho người chưa biết mô hình hoặc lý thuyết trò chơi.** Đối chiếu với code và chạy lại các ví dụ ngày 22/10/2026.

**Phạm vi:** phần giải thích `a`, `b` và các ví dụ G1–G4 trong hướng dẫn này áp dụng cho Version 1 (`ceav-m1-v1.0`). Giao diện hiện hỗ trợ cả V1 và V2, mặc định V2; xem [HUONG_DAN_THAM_SO_V2.md](HUONG_DAN_THAM_SO_V2.md) để dùng sensitivity/specificity theo từng Judge.

Bạn không cần đọc công thức trước. Hãy đọc mục 1–3, làm thử mục 2 trên giao diện, rồi tra từng thông số ở mục 4. Mục 7–9 giải thích kết quả và các chức năng còn lại; công thức nằm cuối file.

## 1. Phần mềm này dùng để trả lời điều gì?

Giả sử có một yêu cầu cần xét duyệt, gọi là **claim**. Ví dụ để dễ hình dung: “Sản phẩm đã đáp ứng yêu cầu, có nên duyệt giải ngân không?”. Trong M1, nội dung này được rút gọn thành hai khả năng: thực sự đạt hoặc thực sự không đạt.

Có ba người đánh giá, gọi là **Judge A, B, C**. Mỗi người có thể chỉ dùng thông tin chung miễn phí, hoặc bỏ thêm công sức để lấy thông tin riêng. Sau đó họ gửi ý kiến và dự đoán về ý kiến của một người khác.

Hệ thống kiểm tra ba câu hỏi riêng:

| Câu hỏi | Kết quả cần đọc |
| --- | --- |
| Người đánh giá có lợi khi bỏ công sức không? | `Delta H−L`, utility L/H theo từng Judge và từng Z |
| Họ có muốn đổi cách làm hiện tại để được lợi hơn không? | `regret`, `max_regret`, trạng thái cân bằng, witness |
| Cách làm đó có đưa ra quyết định đúng và hạn chế giải ngân sai không? | `accuracy`, `false_approval_rate`, `wrong_payout_value` |

**Một cách làm có thể ổn định về lợi ích cá nhân nhưng vẫn quyết định sai nhiều.** Đây chính là điều phần mềm giúp bạn phát hiện.

Các con số đầu vào là **giả định của thí nghiệm**. Ví dụ, nhập `b=4/5` có nghĩa “hãy phân tích thế giới giả định có tín hiệu riêng chính xác 80%”. Phần mềm chưa đo được năng lực của Judge ngoài đời và chưa xác nhận mức 80% là thực tế.

Bạn chọn **config** để định nghĩa thế giới giả định, chọn **profile** để định nghĩa cách người chơi hành xử, rồi engine tính hệ quả và kiểm tra cách đổi có lợi. Mô hình giả định các tham số và chiến lược đem phân tích là kiến thức chung; nó không học chúng từ dữ liệu bỏ phiếu thực.

M1 là phòng thí nghiệm toán cho một claim và ba Judge. Không có kết nối ví, blockchain, chuyển tiền thật hoặc thu thập hành vi người dùng trong lần chạy này. Các khoản thưởng, chi phí và giải ngân dùng đơn vị nghiên cứu chuẩn hóa.

## 2. Dùng thử lần đầu: chỉ cần làm các bước này

### 2.1. Mở giao diện

Nếu giao diện đã chạy, mở [http://127.0.0.1:8765](http://127.0.0.1:8765).

Nếu chưa chạy, mở PowerShell và chạy:

```powershell
Set-Location 'C:\Users\dell\Desktop\fundtogether_data_analyzing'
python -m ceav_m1 serve --port 8765
```

Giữ cửa sổ PowerShell đó hoạt động, rồi mở địa chỉ trên. `Ctrl+C` trong cửa sổ đó dùng để dừng server. Nếu cổng 8765 đang bị dùng bởi chương trình khác, đổi `--port` và mở địa chỉ có đúng cổng mới.

Không mở trực tiếp `web/index.html` bằng cách nhấp đôi: giao diện cần kết nối với engine Python qua server.

### 2.2. Chạy ví dụ G1

1. Chọn trang **Phân tích**.
2. Ở **Preset đầu vào**, chọn **G1 · High effort và low effort cùng tồn tại**. Preset là bộ đầu vào mẫu, giúp bạn khỏi nhập từng ô.
3. Giữ **Cơ chế thưởng = RBTS scoring · Eq. (8)**.
4. Ở **Nạp nhanh profile**, chọn **All-H · báo X**. Profile là cách hành xử đang đem ra kiểm tra.
5. Bấm **Kiểm tra đầu vào**. Thông báo hợp lệ chỉ xác nhận bạn nhập đúng miền và đủ ngân sách.
6. Bấm **Chạy phân tích** và đợi tác vụ kết thúc.

Lần đầu, chỉ cần tìm các giá trị sau:

| Kết quả G1, all-H báo X | Giá trị | Đọc bằng lời |
| --- | ---: | --- |
| Accuracy | `0.896 = 89.6%` | Quyết định đúng trong 89.6% trường hợp theo mô hình |
| False approval | `0.104 = 10.4%` | Trong các claim thực sự không đạt, 10.4% bị duyệt nhầm |
| Giải ngân sai kỳ vọng | `0.052` | Trung bình mỗi claim giải ngân sai 0.052 đơn vị, với V=1 |
| Cash review cost | khoảng `4.62722654` | Tổng thưởng kỳ vọng cho ba Judge, cộng chi phí vận hành |
| Max regret | `0` | Không Judge nào có cách đổi chiến lược đơn phương để tăng utility |
| Kết luận | Cân bằng thuần | Candidate qua kiểm tra lợi ích cá nhân trong phạm vi M1 |

Ở dưới, mở **Judge A · Z=0 · H01** rồi **Judge A · Z=1 · H01**. Cả hai có `Delta H−L` khoảng `+0.04800885` và `Regret = 0`. Hai Judge còn lại cũng qua kiểm tra; không chỉ kiểm tra riêng A.

Chưa cần hiểu phân số dài. Đọc số thập phân trước; phân số là giá trị chính xác để lưu và kiểm chứng.

### 2.3. Đổi đúng một thứ để hiểu tác dụng

Giữ nguyên các thông số G1, chỉ đổi **Nạp nhanh profile** sang **All-Z** rồi chạy lại.

Bạn sẽ thấy accuracy giảm còn `70%`, giải ngân sai kỳ vọng tăng lên `0.15`, nhưng mỗi Judge đạt score `2`, và candidate vẫn là cân bằng. Mục 8 giải thích vì sao.

Lưu ý: đổi **profile** thay đổi cách người chơi hành xử. Đổi **preset đầu vào** có thể nạp lại cả cấu hình, profile và cơ chế; hãy kiểm tra form sau khi chọn.

## 3. Hiểu các biến bằng một câu chuyện

### 3.1. Luồng của một claim

```text
Claim có sự thật Y: đạt hoặc không đạt
                 ↓
Cả ba Judge thấy tín hiệu chung Z miễn phí
                 ↓
Mỗi Judge chọn L hoặc H sau khi đã biết Z
       L: chỉ biết Z
       H: trả chi phí c_i, biết thêm tín hiệu riêng X_i
                 ↓
Mỗi Judge gửi báo cáo r_i và dự đoán p_i
                 ↓
Tính điểm → tính thưởng → trừ chi phí để có utility
                 ↓
Lấy đa số ba báo cáo để có quyết định D
                 ↓
Evaluator đối chiếu D với Y để đo đúng/sai và giải ngân sai
```

**Thông tin nhìn thấy, báo cáo gửi đi và sự thật là các biến khác nhau.** Người chơi có thể thấy tín hiệu 0 nhưng chọn báo cáo 1.

### 3.2. Các biến của một tình huống

| Biến | Đọc là gì? | Giá trị có thể có | Ai biết hoặc tạo ra? |
| --- | --- | --- | --- |
| `Y` | Sự thật của claim | `1`: thực sự đạt; `0`: thực sự không đạt | Bộ sinh mô hình/evaluator biết; Judge không được nhìn trực tiếp |
| `Z` | Tín hiệu chung | `1`: gợi ý đạt; `0`: gợi ý không đạt | Cả ba Judge đều thấy, miễn phí |
| `X_A`, `X_B`, `X_C` | Tín hiệu riêng của từng Judge | `0` hoặc `1` | Chỉ Judge tương ứng thấy nếu chọn H |
| `e_i` | Lựa chọn công sức của Judge i | `L` hoặc `H` | Judge chọn sau khi thấy Z |
| `r_i` | Báo cáo của Judge i | `0`: báo không đạt; `1`: báo đạt | Judge chọn theo thông tin mình có |
| `p_i` | Dự đoán xác suất peer được chấm sẽ báo 1 | Từ `0` đến `1`, gồm hai đầu mút | Trong lần phân tích hiện tại, engine dựng theo profile và thông tin của Judge |
| `D` | Quyết định cuối cùng | `1`: duyệt; `0`: không duyệt | Lấy đa số từ ba báo cáo |
| `i` | Người đang xét | A, B hoặc C | Chỉ là ký hiệu chỉ số |
| `I_i` | Toàn bộ thông tin Judge i được phép biết | Z nếu L; (Z, X_i) nếu H | Không chứa Y hay tín hiệu riêng của người khác |

`L` là **Low effort**, không trả chi phí lấy X. `H` là **High effort**, có trả chi phí để biết X. Chọn H không có nghĩa biết chắc sự thật hoặc buộc phải báo trung thực.

Ví dụ một trạng thái:

```text
Y=0: claim thực sự không đạt
Z=1: thông tin chung lại gợi ý đạt
X_A=1, X_B=0, X_C=1

Nếu cả ba dùng H01, báo cáo là (1,0,1)
Có hai phiếu 1 → D=1 → duyệt nhầm
```

Trong G1, trạng thái cụ thể này có xác suất `3/625 = 0.0048`. Nó chỉ là một trong các trường hợp có thể xảy ra, không phải kết quả duy nhất của lần chạy.

### 3.3. Vì sao kết quả có 32 trạng thái?

Có năm bit: `(Y, Z, X_A, X_B, X_C)`. Mỗi bit nhận 0 hoặc 1, nên có `2^5 = 32` tổ hợp. Engine tính xác suất và kết quả của cả 32 tổ hợp rồi cộng có trọng số.

Đó là **tính kỳ vọng chính xác**, không phải bốc ngẫu nhiên 32 người hoặc chạy 32 lần thử. Không có seed ngẫu nhiên cần chọn.

Các X vẫn có trong bảng trạng thái khi Judge chọn L, để dùng chung không gian tính toán. Điều đó không cho phép Judge L nhìn X.

### 3.4. Cách đọc ký hiệu xác suất

| Ký hiệu | Nghĩa bằng lời |
| --- | --- |
| `P(Y=1)` | Xác suất claim thực sự đạt |
| `P(D=1 \| Y=0)` | Trong nhóm claim không đạt, xác suất bị duyệt là bao nhiêu? |
| `P(Y=0,D=1)` | Trên toàn bộ claim, xác suất đồng thời không đạt và bị duyệt |
| `E[Reward]` | Thưởng trung bình theo xác suất của các tình huống |
| `\| Z=1` | Chỉ xét các tình huống tín hiệu chung bằng 1 |
| `1[điều kiện]` | Bằng 1 khi điều kiện đúng, bằng 0 khi sai |

Dấu `|` đọc là “với điều kiện”. Khác điều kiện thì khác nhóm làm mẫu số; không được đọc mọi số `0.1` thành cùng một tỷ lệ.

## 4. Từng thông số đầu vào: ý nghĩa, mục đích và tác động

### 4.1. Bảng tra nhanh theo đúng ô trên giao diện

| Ô trên giao diện | Tên trong JSON | G1 mặc định | Bạn đang đặt giả định gì? |
| --- | --- | --- | --- |
| `π · P(Y=1)` | `pi` | `1/2` | Tỷ lệ claim thực sự đạt trước khi quan sát tín hiệu |
| `a · Độ chính xác Z` | `a` | `7/10` | Chất lượng của thông tin chung miễn phí |
| `b · Độ chính xác X` | `b` | `4/5` | Chất lượng của mỗi tín hiệu riêng |
| `c_A · Chi phí A` | `costs[0]` | `1/20` | A phải trả bao nhiêu nếu chọn H |
| `c_B · Chi phí B` | `costs[1]` | `1/20` | B phải trả bao nhiêu nếu chọn H |
| `c_C · Chi phí C` | `costs[2]` | `1/20` | C phải trả bao nhiêu nếu chọn H |
| `f · Reward cơ bản` | `f` | `0` | Phần thưởng cố định trong cơ chế RBTS |
| `λ · Hệ số RBTS` | `lambda` | `1` | Mỗi điểm RBTS được đổi thành bao nhiêu đơn vị thưởng |
| `F · Fixed reward` | `fixed_reward` | `2` | Mỗi Judge nhận bao nhiêu trong cơ chế fixed |
| `B · Trần ngân sách` | `reward_budget` | `6` | Tổng thưởng tối đa được phép cam kết cho ba Judge |
| `V · Giá trị payout` | `payout_value` | `1` | Một lần được duyệt tương ứng bao nhiêu giá trị giải ngân |
| `Operating cost` | `operating_cost` | `0` | Chi phí vận hành cố định cho một claim |

Trong JSON còn có `model_version="ceav-m1-v1.0"`. Đây là nhãn phiên bản mô hình, không phải nút chỉnh incentive.

### 4.2. `pi` / π — Trước khi xem thông tin, claim có khả năng đạt bao nhiêu?

Ví dụ `pi=4/5=0.8`: mô hình giả định 80% claim thực sự đạt và 20% không đạt. Đây là tỷ lệ nền của tập claim, không phải tỷ lệ phiếu thuận và không phải dự đoán p của một Judge.

**Mục đích:** kiểm tra cơ chế khi claim đạt phổ biến hoặc hiếm gặp.

Khi thay pi, bạn đổi tỷ trọng các trạng thái Y=0/1, các dự đoán có điều kiện và có thể đổi best response/cân bằng. Không có quy tắc “pi càng lớn thì cơ chế càng tốt”.

Quan hệ giúp đọc mất mát:

```text
wrong_payout_probability = (1-pi) × false_approval_rate
```

Nếu cùng false approval 10.4%, pi=0.5 cho xác suất giải ngân sai `0.5×0.104=0.052`; pi=0.8 cho `0.2×0.104=0.0208`. Xác suất giải ngân sai nhỏ hơn trong ví dụ này do có ít claim không đạt hơn. Chưa thể kết luận năng lực phân biệt của cơ chế tốt hơn.

**Miền hợp lệ:** `0 < pi < 1`. Không nhập `0` hoặc `1` trong M1.

### 4.3. `a` — Thông tin chung Z đáng tin đến mức nào?

`a=7/10` nghĩa là:

- Nếu Y=1, xác suất Z=1 là 70%.
- Nếu Y=0, xác suất Z=0 cũng là 70%.

Đây là giả định lỗi đối xứng. Nó **không** có nghĩa cứ thấy Z=1 thì claim đạt với xác suất 70% trong mọi cấu hình; xác suất đó còn phụ thuộc pi.

**Mục đích:** mô hình hóa một nguồn thông tin mà mọi Judge đều có sẵn. Có thể hình dung một bản tóm tắt chung; M1 chỉ mô hình hóa độ chính xác, không xử lý nội dung tài liệu thực.

Khi a tăng trong khoảng từ 0.5 đến gần 1, Z chính xác hơn. Nếu profile là all-Z thì D=Z và accuracy đúng bằng a. Với profile khác, tác động lên reward/incentive còn tùy cách dùng tín hiệu; không có một chiều thay đổi chung cho mọi metric.

Thông tin chung tốt hơn có thể khiến lấy thêm X ít đáng tiền hơn trong một số cấu hình. G3 là ví dụ cụ thể; không suy thành quy luật giảm đơn điệu cho mọi game.

**Miền hợp lệ:** `0 < a < 1`. `a=1/2` là tín hiệu không cung cấp thêm thông tin về Y. `a<1/2` là tín hiệu thường bị đảo; nếu biết cấu trúc này, người chơi có thể dùng nhãn ngược. Vì thế tăng a từ 0.1 lên 0.2 không nên diễn giải đơn giản là “tăng lượng thông tin”.

### 4.4. `b` — Thông tin riêng X đáng tin đến mức nào?

`b=4/5` nghĩa là mỗi X_i đúng với Y với xác suất 80% ở cả hai loại claim. Trong M1, A/B/C dùng chung b; không có ba ô b_A/b_B/b_C.

**Mục đích:** đặt chất lượng thông tin có thể mua bằng effort. H làm Judge **được nhìn X_i**; H không tự làm b tăng hoặc thay đổi sự thật Y.

Khi b tăng từ 0.5 về gần 1, X_i chính xác hơn. Với all-H báo X, decision majority thường được bạn dùng để quan sát lợi ích của các tín hiệu riêng; trong chính mô hình này accuracy của profile đó là `3b²−2b³`.

Nhưng b không phải xác suất Judge sẽ báo đúng: Judge vẫn được chọn H10, H00 hoặc H11. Cũng không được kết luận b tăng thì mọi cân bằng hoặc mọi incentive đều tốt hơn.

**Miền hợp lệ:** `0 < b < 1`; 0.5 là không có thông tin, dưới 0.5 là tín hiệu có cấu trúc đảo tương tự a.

Các tín hiệu độc lập **khi đã cố định Y**. Không nên hiểu thành báo cáo hoặc dự đoán của các Judge độc lập vô điều kiện: chúng vẫn liên quan đến cùng một sự thật và cùng Z.

### 4.5. `c_A`, `c_B`, `c_C` — Cái giá của việc lấy thông tin riêng

`c_A=1/20=0.05`: nếu A chọn H thì trừ 0.05 vào utility của A; nếu chọn L thì không trả khoản đó. Đây là 0.05 đơn vị chi phí, **không phải xác suất 5%**.

**Mục đích:** hỏi phần thưởng tăng thêm có đủ bù công sức không; có thể hình dung thời gian hoặc nguồn lực đã quy đổi về cùng đơn vị với reward.

Giữ nguyên peer và cấu hình còn lại, tăng c_A làm lựa chọn H của A kém hấp dẫn hơn. Nó không trực tiếp trừ vào utility của B/C. Nếu tìm lại cân bằng sau khi đổi cost, hành vi cân bằng có thể thay đổi và tác động đến cả hệ thống.

Với một profile cố định, đổi cost không tự làm report hay decision đổi. Vì vậy accuracy của profile có thể giữ nguyên trong khi trạng thái cân bằng đổi.

Các chi phí có thể khác nhau. `c_i=0` hợp lệ, tạo khả năng L/H hòa nhau trong game thưởng hằng số; không được mặc định H luôn tệ hơn L khi cost bằng 0.

**Miền hợp lệ:** từng chi phí không âm. Trong JSON, `costs` bắt buộc có đúng ba phần tử theo thứ tự A, B, C.

### 4.6. `f` — Thưởng nền trong RBTS

RBTS trả `f + lambda×score`. Nếu f=0.1, mỗi Judge được cộng thêm 0.1 bất kể lựa chọn effort/report.

**Mục đích:** đặt khoản thưởng cơ bản, tách khỏi phần phụ thuộc score.

Trong M1, người chơi luôn tham gia. Vì vậy, giữ mọi thứ khác và đủ budget, tăng f làm reward và utility tăng nhưng không thay đổi best response, Delta, regret hoặc tập cân bằng: mọi lựa chọn của cùng Judge được cộng cùng một khoản.

Tăng f cũng tăng trần thưởng cần có. M1 chưa trả lời thưởng nền giúp tuyển người tham gia thế nào, vì không có lựa chọn bỏ tham gia.

**Miền hợp lệ:** `f >= 0`. Cơ chế fixed dùng F để trả thưởng, không dùng f.

### 4.7. `lambda` / λ — Đổi điểm RBTS ra thưởng mạnh đến mức nào?

Ví dụ, score=1.5 và f=0:

| Lambda | Reward |
| ---: | ---: |
| `0` | `0` |
| `1/2` | `0.75` |
| `1` | `1.5` |
| `2` | `3` |

**Mục đích:** điều chỉnh độ lớn phần thưởng gắn với score so với chi phí effort.

Với peer context cố định, lợi ích điểm tối ưu H so với L không âm; nhân lambda lớn hơn có thể giúp bù cost. Ví dụ G1 cần lambda khoảng `0.51015803` để H hòa L khi c=0.05.

Tuy nhiên, tăng lambda cũng thưởng mạnh hơn cho các profile như all-Z vốn đã đạt điểm tối đa. Nó không loại bỏ cân bằng all-Z. Bạn phải đọc cả incentive, chất lượng quyết định và thực chi.

`lambda=0` làm reward RBTS chỉ còn f. Report và prediction không còn ảnh hưởng utility. Prediction Bayesian được xuất lúc này là một giá trị đại diện; mọi prediction hợp lệ đều hòa về lợi ích.

**Miền hợp lệ:** `lambda >= 0`, đồng thời phải đủ B. Cơ chế fixed không dùng lambda để trả thưởng.

### 4.8. `F` / `fixed_reward` — Thưởng mỗi người trong cơ chế fixed

`F=2` nghĩa là mỗi Judge được 2 dù báo 0/1 hay prediction thế nào.

**Mục đích:** làm đối chứng: chỉ trả khoản cố định thì có tạo lý do tài chính để lấy thêm thông tin không?

Trong M1, nếu c_i>0, chọn H nhận cùng F như L nhưng phải trả thêm cost. Vì vậy L có utility cao hơn. Tăng F không thay đổi chênh lệch này.

Khi đang chọn RBTS, ô F vẫn xuất hiện để dùng cho so sánh nhưng không quyết định thưởng RBTS.

**Miền hợp lệ:** `F >= 0`, và fixed yêu cầu `3F <= B`.

### 4.9. `B` / `reward_budget` — Có đủ ngân sách cam kết thưởng không?

B là giới hạn **tổng thưởng của cả ba Judge cho một claim**. Nó không phải mức thưởng mỗi Judge và không phải khoản payout cho claim.

```text
RBTS: trần tổng thưởng = 3f + 6lambda
Fixed: trần tổng thưởng = 3F

Trần của cơ chế đang chạy phải <= B
```

**Mục đích:** ngăn cấu hình cam kết mức thưởng tối đa vượt ngân sách. Validator kiểm tra trần, dù profile đang xét có thực chi thấp hơn trần.

Ví dụ f=0, lambda=1 thì cần B>=6. Đổi lambda=2 cần B>=12. Nếu vẫn B=6, đó là `invalid_budget`; engine không tự cắt thưởng hoặc chia lại pool.

Tăng B mà không đổi f/lambda/F chỉ nới giới hạn. Nó không tự tăng thưởng, thay đổi score hoặc thay đổi incentive của cấu hình đã hợp lệ.

Chi phí vận hành và payout không được cộng vào trần thưởng này. Nếu muốn đọc chi phí vận hành, xem cash review cost riêng.

### 4.10. `V` / `payout_value` — Mỗi lần duyệt giải ngân bao nhiêu giá trị?

V=1 là dùng một đơn vị giải ngân làm chuẩn. V=10 nghĩa là cùng một lần duyệt có giá trị 10 đơn vị trong phép đo.

**Mục đích:** chuyển xác suất sai thành mất mát kỳ vọng:

```text
wrong_payout_value = V × xác suất claim không đạt mà vẫn bị duyệt
expected_payout    = V × xác suất được duyệt, gồm cả đúng và sai
```

Trong G1, V=1 cho giải ngân sai kỳ vọng 0.052; V=10 cho 0.52. Tăng V không làm Judge đổi utility, reward hoặc best response trong M1: Judge không được chia V và không bị trừ V khi sai.

**Miền hợp lệ:** `V >= 0`. V=0 làm các giá trị payout bằng 0 nhưng xác suất duyệt sai vẫn có thể dương. Không nên dùng mất mát bằng 0 ở V=0 để kết luận cơ chế xét đúng.

### 4.11. `operating_cost` — Chi phí vận hành ngoài thưởng

Đây là hằng số cho một claim, cộng một lần vào tổng thưởng kỳ vọng:

```text
cash_review_cost = expected_reward_total + operating_cost
```

**Mục đích:** cho phép tính một khoản vận hành giả định riêng. Tăng operating cost làm cash review cost tăng đúng bằng khoản thêm đó; không thay đổi utility của Judge hoặc cân bằng.

Không tự lấy thời gian Python chạy làm operating cost. Chi phí effort của Judge được xuất riêng, đã trừ khi tính utility, và không cộng thêm vào cash review cost.

**Miền hợp lệ:** không âm; mặc định 0 nếu bỏ trường này trong JSON.

### 4.12. Quy tắc nhập số

| Muốn nhập | Cách nhập |
| --- | --- |
| Một nửa | `1/2` hoặc `0.5` |
| 80% | `4/5` hoặc `0.8` |
| Chi phí 0.05 | `1/20` hoặc `0.05` |
| Số 0 | `0` |

Trong ô nhập của giao diện, gõ trực tiếp các dạng trên. Dùng dấu chấm cho thập phân; không nhập `0,8` hoặc `80%`. Trong file JSON, các số đầu vào phải là **chuỗi**: `"b":"0.8"`, không dùng `"b":0.8`.

`pi`, a, b thuộc khoảng mở (0,1), còn prediction p được phép bằng 0 hoặc 1. Không nhầm hai miền này. Các trường không phải xác suất như lambda, F, B, V được phép lớn hơn 1.

## 5. Chiến lược: L0, L1, H00, H01, H10, H11 là gì?

### 5.1. Cách đọc mã action

Chữ đầu nói Judge có lấy X không. Với H, hai số sau lần lượt là report khi X=0 và khi X=1.

| Action | Có trả cost để thấy X? | Nếu X=0 thì báo | Nếu X=1 thì báo | Diễn giải |
| --- | --- | ---: | ---: | --- |
| `L0` | Không | 0 | 0 | Chỉ dùng thông tin cho phép ở L, báo 0 tại nhánh Z đang xét |
| `L1` | Không | 1 | 1 | Chỉ dùng thông tin cho phép ở L, báo 1 tại nhánh Z đang xét |
| `H00` | Có | 0 | 0 | Lấy X nhưng report luôn 0 tại nhánh này |
| `H01` | Có | 0 | 1 | Lấy X rồi báo đúng giá trị X |
| `H10` | Có | 1 | 0 | Lấy X rồi báo ngược X |
| `H11` | Có | 1 | 1 | Lấy X nhưng report luôn 1 tại nhánh này |

Hai cột X của L chỉ mô tả report không đổi; Judge L không được nhìn X. H00/H11 vẫn có thể dùng X để dự đoán peer tốt hơn dù report hằng số.

**H01 báo đúng tín hiệu, chưa có nghĩa báo đúng sự thật.** X vẫn có thể sai so với Y.

### 5.2. Vì sao phải nhập riêng Z=0 và Z=1?

Judge được thấy Z trước khi chọn effort. Do đó họ có thể chọn một action khi Z=0 và action khác khi Z=1.

Ví dụ all-Z được viết là:

```json
{
  "0": ["L0", "L0", "L0"],
  "1": ["L1", "L1", "L1"]
}
```

Mỗi hàng theo thứ tự A, B, C. `"0"`/`"1"` là giá trị của **Z**, không phải Y. All-Z không cần nhìn X; nó chỉ lặp lại tín hiệu chung.

### 5.3. Các profile nạp nhanh

| Tên trên giao diện | Hành vi ở Z=0 | Hành vi ở Z=1 |
| --- | --- | --- |
| All-H · báo X | Cả ba H01 | Cả ba H01 |
| All-H · báo (1−X) | Cả ba H10 | Cả ba H10 |
| All-Z | Cả ba L0 | Cả ba L1 |
| All-(1−Z) | Cả ba L1 | Cả ba L0 |
| All-PASS | Cả ba L1 | Cả ba L1 |
| All-FAIL | Cả ba L0 | Cả ba L0 |
| F09 · bất đối xứng | A=H00, B=H10, C=L1 | A=L0, B=H11, C=H01 |

“Candidate” nghĩa là **profile đang đem ra kiểm tra**. Bạn có thể kiểm tra một candidate không phải cân bằng; phần mềm vẫn tính chất lượng quyết định của nó rồi chỉ rõ có người muốn đổi chiến lược.

## 6. Dự đoán p và điểm RBTS thực sự nói về điều gì?

### 6.1. p dự đoán report của peer, không phải sự thật Y

Trong ba Judge, vai trò được sắp vòng như sau:

| Judge đang được chấm i | Người tham chiếu j: lấy prediction để dựng shadow | Peer k: lấy report để đối chiếu điểm |
| --- | --- | --- |
| A | B | C |
| B | C | A |
| C | A | B |

Vậy `p_A=0.8` nghĩa là A dự đoán C sẽ báo 1 với xác suất 80%, theo thông tin A được biết. Nó không phải “claim đạt 80%”, “A đúng 80%”, hoặc “A có 0.8 phiếu”.

Giao diện hiện tại cho bạn nhập action, còn engine dựng các prediction phù hợp với profile. Với RBTS lambda>0, prediction tối ưu của i là `P(r_k=1 | I_i)`. Không cần tự thử một lưới các giá trị p.

Ví dụ ở G1 all-H báo X, nếu A thấy Z=1 và X_A=1:

| Đại lượng | Giá trị |
| --- | ---: |
| Xác suất Y=1 sau thông tin đó | `28/31 ≈ 90.32%` |
| Prediction p_A về report của C | `23/31 ≈ 74.19%` |

Hai số khác nhau vì tín hiệu riêng của C vẫn có thể sai. Nếu C luôn báo 1 thì p_A=1, kể cả khi claim thực sự không đạt.

### 6.2. Hai thành phần điểm

| Thành phần | Chấm cái gì? | Có đọc trực tiếp Y không? |
| --- | --- | --- |
| `information_score` | Report của i qua phép shadow, dùng prediction của j và report của k | Không |
| `prediction_score` | Prediction của i so với report của k | Không |
| `score` / `total_score` | Tổng hai thành phần trên, từ 0 đến 2 | Không |

Tên “information score” không có nghĩa evaluator đã xác nhận report chứa sự thật. Đây là tên thành phần của công thức.

`score=1.8` không có nghĩa độ chính xác 180% hoặc 90%. Score được dùng trả thưởng; accuracy phải đo riêng bằng Y.

### 6.3. Score, reward và utility khác nhau thế nào?

```text
Score:   số điểm cơ chế chấm
Reward:  khoản thưởng nhận được
Utility: reward trừ chi phí effort
```

Ví dụ RBTS có score=1.5, f=0.1, lambda=2 và Judge chọn H với c=0.05:

```text
Reward  = 0.1 + 2×1.5 = 3.1
Utility = 3.1 - 0.05 = 3.05
```

Trong fixed, reward luôn bằng F; score chẩn đoán vẫn có thể xuất hiện nhưng không dùng tính thưởng fixed.

## 7. Đọc từng nhóm kết quả

### 7.1. Quyết định và mất mát

| Tên kết quả | Nghĩa và cách đọc |
| --- | --- |
| `accuracy` | `P(D=Y)`: tỷ lệ quyết định đúng trên toàn bộ claim |
| `false_approval_rate` | `P(D=1 \| Y=0)`: tỷ lệ duyệt nhầm trong nhóm thực sự không đạt |
| `false_rejection_rate` | `P(D=0 \| Y=1)`: tỷ lệ từ chối nhầm trong nhóm thực sự đạt |
| `wrong_payout_probability` | `P(Y=0,D=1)`: xác suất giải ngân sai trên toàn bộ claim |
| `wrong_payout_value` | V nhân xác suất giải ngân sai: giá trị sai kỳ vọng cho mỗi claim |
| `expected_payout` | V nhân xác suất duyệt: tổng giải ngân kỳ vọng, gồm đúng và sai |

Accuracy cao riêng lẻ vẫn có thể gây hiểu nhầm nếu claim đạt quá phổ biến. Ví dụ, all-PASS luôn duyệt nên accuracy bằng pi, nhưng false approval bằng 100%: mọi claim không đạt đều lọt qua. Vì thế hãy đọc cả tỷ lệ sai theo từng nhóm và giá trị giải ngân sai.

Ví dụ **1.000 claim giả định** cùng phân phối G1, all-H báo X:

- Kỳ vọng 500 claim thực sự không đạt. Trong nhóm này, 10.4% bị duyệt nhầm, tức 52 claim.
- Kỳ vọng 500 claim thực sự đạt. Trong nhóm này, 10.4% bị từ chối nhầm, tức 52 claim.
- Tổng đúng kỳ vọng là 896/1.000; tổng duyệt kỳ vọng là 500/1.000.
- Với V=1, giải ngân sai kỳ vọng là 52 đơn vị cho 1.000 claim, hay 0.052 cho mỗi claim.

Đây là cách diễn giải kỳ vọng, không phải hệ thống đã chạy 1.000 claim thực tế. Không lấy `10.4% × 1.000` để tính số giải ngân sai: 10.4% ở đây chỉ áp dụng cho nhóm Y=0.

### 7.2. Tiền thưởng và chi phí

| Tên kết quả | Nghĩa |
| --- | --- |
| `expected_reward_total` | Tổng thưởng trung bình của A+B+C cho một claim |
| `expected_effort_cost` | Tổng chi phí effort trung bình: `sum c_i×P(i chọn H)` |
| `expected_judge_utility` | Danh sách utility trung bình theo thứ tự A, B, C |
| `cash_review_cost` | Thưởng trung bình cộng operating cost |
| `reward_cap` / Maximum reward | Trần thưởng của cơ chế với f/lambda/F đã đặt |
| `reward_budget` / Budget | Ngân sách B mà bạn cho phép |

Trong bảng **Accounting của candidate**, mỗi dòng là một Judge:

- **Expected score:** điểm trung bình khi người đó thực hiện chính candidate đang xét.
- **Reward thực chi:** thưởng kỳ vọng của người đó; là số tính trong mô hình, không phải giao dịch đã thanh toán.
- **Effort cost:** chi phí effort trung bình của người đó.
- **Utility:** reward trừ effort cost của người đó.

Không cộng cả reward và utility thành hai khoản chi: utility đã bắt đầu từ reward. Payout cho claim và reward cho Judge cũng là hai nhóm khác nhau.

### 7.3. Bảng best response: phần giải thích người chơi muốn làm gì

**Best response** là cách một Judge có thể tối đa hóa utility khi hai người kia giữ nguyên cách làm và prediction của candidate gốc.

Mỗi certificate thuộc một cặp `(Judge, Z)`. Có sáu cặp: A0, A1, B0, B1, C0, C1.

| Tên trong bảng | Nghĩa |
| --- | --- |
| `Candidate utility` | Utility của action candidate đang thực sự dùng tại nhánh này |
| `Utility L tối ưu` | Utility cao nhất nếu người đó chọn L, được tối ưu report và prediction |
| `Utility H tối ưu` | Utility cao nhất nếu chọn H, được tối ưu report và prediction, đã trừ cost |
| `Delta H−L` / `delta_utility` | Utility H tối ưu trừ utility L tối ưu |
| `Regret` | Utility tốt nhất có thể đạt trừ candidate utility |
| `Optimal actions` | Các action cùng đạt utility tối ưu |
| `Effort tốt nhất` / `best_efforts` | L, H hoặc cả hai khi hòa |

Cách đọc **Delta**:

| Dấu | Kết luận tại nhánh này, với peer context đang giữ nguyên |
| --- | --- |
| `Delta > 0` | H tối ưu có lợi hơn L tối ưu |
| `Delta < 0` | L tối ưu có lợi hơn H tối ưu |
| `Delta = 0` | Hai mức effort hòa về utility |

Cách đọc **regret**:

| Giá trị | Kết luận |
| --- | --- |
| `0` | Candidate không thua một cách đổi chiến lược đơn phương nào tại nhánh này |
| Dương | Có cách đổi effort/report/prediction để tăng utility |
| Âm | Là lỗi tính toán; không phải một kết quả hợp lệ |

**Delta dương chưa đủ kết luận candidate là cân bằng.** Candidate còn có thể đang dùng report không tối ưu dù effort H là tốt nhất. Regret mới so sánh cách làm thật của candidate với lựa chọn tốt nhất.

**Delta âm cũng không đồng nghĩa candidate thất bại.** Nếu candidate đã chọn L và report/prediction tối ưu thì regret vẫn bằng 0, như all-Z.

`max_regret` là regret lớn nhất trong sáu cặp. Cân bằng thuần được chấp nhận khi cả sáu regret chính xác bằng 0. Không đọc riêng A/Z=0 rồi kết luận cho toàn profile.

### 7.4. Các cột bên trong certificate

| Cột hoặc trường | Cách hiểu |
| --- | --- |
| `Observation` | Thông tin nhìn thấy: một số Z với L; cặp (Z,X_i) với H |
| `P(I\|Z)` / `probability_given_z` | Xác suất quan sát đó trong nhánh Z đang xét; hai quan sát H có xác suất cộng thành 1 |
| `Info r=0`, `Info r=1` | Information score kỳ vọng nếu chọn report tương ứng tại quan sát đó |
| `Optimal reports / ties` | Tất cả report cùng tối ưu; `0 / 1` nghĩa cả hai hòa nhau |
| `Optimal prediction` | Xác suất peer k báo 1 với thông tin này; là prediction tối ưu khi RBTS lambda>0 |
| `branch_probability` | Xác suất xuất hiện nhánh Z này trên toàn bộ claim |
| `prediction_optimum` | Cho biết prediction tối ưu được xác định duy nhất hay mọi p đều hòa |
| `report_optimum` | Cho biết report tối ưu theo danh sách hay mọi map đều hòa |
| `frozen_peer_tables` | Prediction của hai người kia được giữ nguyên trong phép kiểm tra lệch đơn phương |

Với fixed hoặc lambda=0, `any_in_unit_interval` nghĩa mọi p trong [0,1] đều hòa về utility; `any_admissible_map` nghĩa mọi report map hợp lệ đều hòa. Prediction hiển thị vẫn giúp xem một giá trị đại diện, không phải lựa chọn duy nhất.

### 7.5. Witness là bằng chứng gì?

**Deviation witness** chỉ ra một cách đổi cụ thể tạo lợi ích lớn hơn candidate:

| Trường | Nghĩa |
| --- | --- |
| `judge`, `z` | Ai đổi và đổi tại nhánh Z nào |
| `action` | Action mới của riêng người đó tại nhánh đó |
| `prediction_map` | Prediction của người đổi, theo từng quan sát được phép biết |
| `old_utility`, `new_utility` | Utility trước và sau khi đổi |
| `conditional_gain` | Mức lợi khi đã biết đang ở nhánh Z này |
| `ex_ante_gain` | Mức lợi tính từ trước khi biết Z: `P(Z=z)×conditional_gain` |

Trong phép kiểm tra đó, hai peer không đổi action hoặc tính lại prediction để phản ứng. Đây là điều kiện của phép kiểm tra lệch đơn phương.

Nút **Lấy deviation làm candidate mới** nạp action mới vào bản nháp. Bạn phải bấm chạy lại để phân tích profile mới. Run mới dựng lại prediction cho cả profile mới, nên gain hoặc regret của run mới không bắt buộc giống witness cũ. Witness cũ vẫn nói về peer tables của run gốc.

### 7.6. “Cân bằng thuần” không có nghĩa mọi người đều trung thực

Cách hiểu để dùng phần mềm: nếu hai người còn lại giữ nguyên chiến lược, không ai có thể tăng utility bằng cách tự đổi chiến lược của mình. “Thuần” nghĩa các lựa chọn hành vi được xác định theo thông tin, không trộn ngẫu nhiên các chiến lược.

Kết luận này không tự nói cân bằng có accuracy cao, là cân bằng duy nhất, sẽ được người thật chọn hoặc chịu được một nhóm phối hợp thay đổi. Search M1 cũng không liệt kê mọi mixed equilibrium.

## 8. Bốn ví dụ để nhìn thấy ý nghĩa của các chỉ số

### 8.1. G1: có lý do tài chính để dùng H, nhưng vẫn có cân bằng chất lượng thấp hơn

Giữ cùng cấu hình G1 và cơ chế RBTS, chạy hai profile:

| Đại lượng | All-H báo X | All-Z |
| --- | ---: | ---: |
| Effort | H của cả ba | L của cả ba |
| Score trung bình mỗi Judge | `≈1.54240885` | `2` |
| Reward trung bình mỗi Judge | `≈1.54240885` | `2` |
| Utility trung bình mỗi Judge | `≈1.49240885` | `2` |
| Accuracy | `89.6%` | `70%` |
| False approval | `10.4%` | `30%` |
| Wrong payout, V=1 | `0.052` | `0.15` |
| Tổng thưởng kỳ vọng | `≈4.62722654` | `6` |
| Tổng effort cost | `0.15` | `0` |
| Max regret | `0` | `0` |
| Cân bằng thuần? | Có | Có |

All-Z dự đoán được report của nhau hoàn hảo theo Z và đạt score tối đa. Nhưng Z vẫn sai 30% theo giả định. Cơ chế đang chấm các report/prediction với nhau, không đối chiếu trực tiếp với Y.

All-Z còn cho utility cao hơn all-H ở ví dụ này. Cần giữ kết quả đó khi đánh giá cơ chế; việc all-H tồn tại không trả lời người thật sẽ chọn cân bằng nào.

Preset **G2** trên giao diện nạp chính kiểu minh họa dùng tín hiệu chung này.

### 8.2. G3: thông tin riêng không bù được chi phí trong candidate đang xét

G3 đặt a=0.9, b=0.75, c=0.05, lambda=1 và profile all-H báo X.

```text
Score L tối ưu ≈ 1.49000000
Score H tối ưu ≈ 1.51996173
Lợi ích score  ≈ 0.02996173
Trừ cost 0.05 → Delta utility ≈ -0.02003827
```

All-H bị bác. Accuracy của profile đó vẫn tính được, bằng `84.375%`; còn all-Z ở phân phối này có accuracy `90%` vì D=Z. Việc có lấy thêm X không đảm bảo report và phép đa số đang dùng khai thác thông tin tốt nhất.

### 8.3. G4: nhìn trung bình có thể bỏ sót lý do đổi hành vi

G4 đổi pi thành 0.8, giữ a=0.7, b=0.8, c=0.05, lambda=1, all-H báo X.

| Nhánh | Xác suất nhánh | Delta H−L của A | Regret của A |
| --- | ---: | ---: | ---: |
| Z=0 | `0.38` | `+0.05276103` | `0` |
| Z=1 | `0.62` | `−0.00932008` | `+0.00932008` |

Trung bình Delta vẫn dương, nhưng khi thấy Z=1, Judge có lợi nếu chuyển sang L. Do effort được chọn sau Z, candidate luôn H không phải cân bằng.

Witness của A ở Z=1 chọn **L0**, với prediction `23/31`. L0 báo 0 ngay cả khi Z=1: tối ưu utility không đồng nghĩa cứ nhìn Z rồi báo giống Z. Gain có điều kiện khoảng 0.00932008; gain trước khi biết Z khoảng `0.62×0.00932008 = 0.00577845`.

### 8.4. Cùng G1 all-H, fixed và RBTS khác nhau ở incentive

Đặt F=f+2lambda=2 để hai cơ chế cùng trần tổng thưởng 6.

| Đại lượng | Fixed | RBTS |
| --- | ---: | ---: |
| Trần tổng thưởng | `6` | `6` |
| Tổng thưởng kỳ vọng | `6` | `≈4.62722654` |
| Accuracy của candidate | `89.6%` | `89.6%` |
| Wrong payout của candidate | `0.052` | `0.052` |
| Max regret | `0.05` | `0` |
| All-H có phải cân bằng? | Không | Có |

Accuracy và payout bằng nhau vì công cụ đang giữ nguyên hành vi all-H để so sánh hai cách thưởng. Fixed không tạo lý do tài chính duy trì H có cost; bảng không dự đoán người được trả fixed thật sự vẫn sẽ làm H.

## 9. Sáu trang trên giao diện: dùng trang nào khi nào?

### 9.1. Phân tích — Kiểm tra một cách làm cụ thể

Dùng khi hỏi: “Với bộ tham số và profile này, kết quả thế nào, ai muốn đổi hành vi?”. Chạy rồi đọc theo thứ tự: cân bằng/max regret → sáu best responses → chất lượng quyết định → thưởng và chi phí.

Các nhóm chi tiết giúp tra nguyên nhân:

- **Toàn bộ decision metrics và prediction tables:** xem false rejection, expected payout và prediction theo quan sát.
- **Best response theo từng Judge / Z:** xem L/H tối ưu, report ties và witness.
- **32 trạng thái:** lọc `y=0`, `decision=1` để nhìn các trường hợp giải ngân sai; có thể lọc thêm z.
- **Run …** ở cuối: tải artifact hoặc nạp input của run vào bản nháp.

### 9.2. Tìm cân bằng — Tìm các cách làm ổn định trong phạm vi thuần

Dùng khi hỏi: “Không chỉ profile tôi nghĩ ra, còn những profile cân bằng nào?”. Trang này dùng cấu hình và cơ chế hiện tại; nó tự tìm các action, không giới hạn vào profile bản nháp.

1. Nạp cấu hình, ví dụ G1, chọn RBTS.
2. Sang **Tìm cân bằng**, bấm **Tìm cân bằng**.
3. Khi hoàn thành, lọc theo Z, trạng thái, action hoặc effort để xem từng ứng viên.
4. Mở **Certificate** của ứng viên để xem chứng cứ.
5. Chọn một nhánh Z=0 và một nhánh Z=1, bấm **Mở tổ hợp để phân tích**.
6. Sang Phân tích, bấm **Chạy phân tích** để có accuracy/payout của full profile đó.

Cách đọc số lượng:

```text
Mỗi Judge có 6 action tại một Z
→ 6³ = 216 ứng viên cho mỗi nhánh
→ engine kiểm tra 432 branch candidates cho hai nhánh

Một full profile phải ghi hành vi ở cả hai Z
→ 216² = 46.656 profile effort/report đầy đủ
```

Ở G1 RBTS đã chạy lại cho hướng dẫn này, có **10 cân bằng mỗi nhánh**, ghép thành **100 tổ hợp đầy đủ**. Số 100 là số tổ hợp, không phải 100% đúng hoặc xác suất người chơi chọn all-H.

Khi fixed hoặc lambda=0, các số đếm là lớp effort/report với prediction tự do; không phải liệt kê hữu hạn mọi giá trị p có thể có.

### 9.3. Quét tham số — Đổi nhiều giá trị, giữ nguyên profile

Dùng khi hỏi: “Nếu lambda hoặc cost thay đổi, candidate này còn là cân bằng không?”.

Ví dụ đầu tiên:

1. Nạp lại G1, RBTS, all-H báo X.
2. Sang **Quét tham số**; chỉ tích axis `lambda`.
3. Điền `0, 1/2, 1, 2` vào danh sách lambda. Dấu phẩy ở đây ngăn các giá trị, không phải dấu thập phân.
4. Giữ B=6, f=0, bấm **Chạy quét**.

Kết quả từ lần chạy lại:

| Lambda | Trạng thái đầu vào | Delta A/Z=0 và A/Z=1 | Candidate all-H |
| ---: | --- | ---: | --- |
| `0` | valid | `−0.05` | Không cân bằng |
| `1/2` | valid | `≈−0.00099558` | Không cân bằng |
| `1` | valid | `≈+0.04800885` | Cân bằng |
| `2` | invalid_budget | Không có số liệu hợp lệ | Cần B>=12 |

Nếu muốn tính cả điểm lambda=2, sửa B thành 12 và chạy một run mới. Đừng coi hàng invalid là Delta=0 hoặc bằng chứng cơ chế thất bại về incentive: cấu hình đó chưa đủ budget.

Các axis được hỗ trợ:

| Axis | Thay đổi gì? |
| --- | --- |
| `pi` | Tỷ lệ nền claim đạt |
| `a` | Độ chính xác tín hiệu chung |
| `b` | Độ chính xác tín hiệu riêng |
| `c` | Đặt đồng thời c_A=c_B=c_C bằng giá trị đang quét |
| `lambda` | Hệ số thưởng RBTS |

Hai axis, mỗi axis ba giá trị tạo `3×3=9` điểm. Biểu đồ cho chọn trục X, metric, trục phân nhóm; các axis còn lại có ô chọn giá trị cố định.

Tên metric `A_z0_delta_utility` nghĩa là Delta của A khi Z=0; `A_z1_regret` nghĩa là regret của A khi Z=1. Bảng/biểu đồ mặc định tập trung A, không thay cho việc đọc B/C trong profile bất đối xứng; bấm **Phân tích điểm** rồi **Chạy phân tích** để xem đủ sáu cặp.

Sweep **không tự tìm lại mọi cân bằng** ở mỗi điểm. Trong ví dụ chỉ đổi lambda, profile và phân phối giữ nguyên nên wrong payout vẫn là 0.052 tại các điểm hợp lệ; cái đang đổi là reward và tính bền vững về lợi ích của profile đó.

### 9.4. So sánh — Đặt fixed và RBTS cạnh nhau

1. Chọn G1 và all-H báo X.
2. Sang **So sánh**.
3. Kiểm tra `F=f+2lambda`. Nếu cần, bấm **Đặt F=f+2λ bằng engine** để chủ động sửa F.
4. Bảo đảm B đủ trần của cả hai cơ chế, rồi bấm **Chạy so sánh**.

Đọc riêng trần và reward thực chi. Chức năng này so sánh **cùng một candidate**, không so sánh toàn bộ tập cân bằng của hai cơ chế. Nút đặt F không tự tăng B.

Có thể ghim hai run trong Lịch sử để đối chiếu. Nếu model/config/profile khác nhau, cần đọc khác biệt trước khi quy kết một kết quả tốt hơn cho cơ chế.

### 9.5. Kiểm thử — Kiểm tra chương trình tính đúng, không chấm cơ chế tốt/xấu

| Lựa chọn | Khi nào dùng? |
| --- | --- |
| `Reference` | Kiểm tra checker tham chiếu trên các profile mẫu mà checker hỗ trợ |
| `Golden G1–G4` | Kiểm tra engine khớp các ví dụ chuẩn |
| `Toàn bộ engine/API suite` | Kiểm tra rộng hơn, gồm các test chậm |
| `Nhóm T-ID được chọn` | Chọn các nhóm kiểm chứng cụ thể khi cần chẩn đoán |

Test pass nghĩa là các assertion tương ứng đã chạy và đạt. Một test có thể pass chính vì engine phát hiện G4 **không** phải cân bằng. Không được hiểu “test xanh” là “RBTS luôn tốt”.

Ô **Chạy thêm fixture failure công khai, tách khỏi engine** dùng để kiểm tra việc hiển thị lỗi thử nghiệm. Lần đầu sử dụng hãy để bỏ chọn.

`skipped`, `not_run` và `unavailable` không được tính là pass. Evidence browser B01–B09 là bằng chứng thao tác giao diện riêng; nút chạy Python suite không tự thay thế phần đó.

### 9.6. Lịch sử — Mở lại và tải kết quả

Mỗi lần chạy tạo một run ID và lưu đầu vào tại thời điểm bấm chạy. Trong **Lịch sử**, bấm **Mở** để xem lại; ở vùng run có các link tải và nút **Nạp input run vào bản nháp** khi run có đủ config/profile.

Sửa form sau khi chạy không sửa kết quả cũ. Thông báo “Bản nháp đã thay đổi” nhắc bạn đang nhìn kết quả của bộ đầu vào trước đó. Muốn kết quả cho form mới phải chạy một run mới.

## 10. Muốn khảo sát một vấn đề thì nên chỉnh gì?

Đầu tiên hãy nêu câu hỏi rồi chỉ đổi một nhóm giả định. Các ví dụ này là cách tổ chức thí nghiệm, không phải khẳng định số nào phản ánh thực tế.

| Câu hỏi bạn muốn đặt | Chỉnh hoặc thao tác | Nên đọc |
| --- | --- | --- |
| Thưởng bao nhiêu mới bù effort? | Quét lambda, giữ c và profile | Delta theo đủ i/Z, regret, budget, actual reward |
| Judge có cost cao hơn thì sao? | Chỉnh một c_i; hoặc quét c nếu muốn cả ba bằng nhau | Best response của từng người, không chỉ A |
| Thông tin chung đã rất tốt thì có cần lấy thêm X? | Thay a, giữ b/c/profile | Delta và accuracy; đối chiếu all-Z với all-H |
| Tín hiệu riêng có ích tới đâu? | Thay b | Chất lượng decision và regret của candidate |
| Claim không đạt xuất hiện nhiều hơn thì rủi ro thế nào? | Giảm pi | False approval riêng và wrong payout riêng |
| Giá trị giải ngân lớn hơn gây mất mát bao nhiêu? | Tăng V | Wrong payout value và expected payout |
| Còn cân bằng nào chất lượng thấp không? | Chạy Tìm cân bằng, chọn tổ hợp rồi Analyze | Accuracy/payout của từng profile được chọn |
| Tăng thưởng nền có giữ được H không? | Thay f, giữ lambda/c, bảo đảm B đủ | Reward/utility tăng nhưng Delta/regret không đổi trong M1 |

Nếu chưa biết giá trị thực của a/b/c, hãy ghi rõ chúng là giả định và thử vài mức. Một kết quả đẹp ở một điểm không chứng minh cơ chế tốt trên mọi môi trường. Không tự gắn các giá trị mặc định cho con người thật.

## 11. Trạng thái, lỗi nhập và các hiểu nhầm thường gặp

### 11.1. Trạng thái chạy khác với kết luận cân bằng

| Trạng thái | Nghĩa |
| --- | --- |
| `queued` | Tác vụ đang chờ bắt đầu |
| `running` | Engine đang thực thi |
| `succeeded` | Tác vụ hoàn thành thành công; candidate vẫn có thể không phải cân bằng |
| `failed` | Tác vụ lỗi; đọc thông báo/log |
| `cancelled` | Đã hủy; không dùng phần tính dở làm certificate hoàn chỉnh |
| `interrupted` | Bị gián đoạn; không tự coi là hoàn thành |
| `not_equilibrium` | Kết luận toán: candidate có deviation có lợi; không phải lỗi server |
| `exact_pure_equilibrium` | Candidate đạt điều kiện cân bằng thuần chính xác trong phạm vi đã khai báo |

Trang chỉ cho một tác vụ nặng tại một thời điểm. Nút **Hủy tác vụ** dùng để dừng worker của lần chạy đó; không tiếp tục dùng số liệu dở dang như một search hoàn chỉnh.

### 11.2. Một số thông báo thường gặp

| Gặp gì? | Hiểu và xử lý thế nào? |
| --- | --- |
| `invalid_budget` | Kiểm tra B với `3f+6lambda` hoặc `3F`; điều chỉnh chủ động rồi chạy mới |
| `Phải thuộc khoảng mở (0,1)` | pi/a/b không được bằng 0 hoặc 1; muốn tín hiệu vô thông tin thì dùng 1/2 |
| `Cần chuỗi thập phân hoặc tử số/mẫu số` | Với JSON, đặt số trong dấu nháy; không dùng %, dấu phẩy thập phân hoặc biểu thức tính |
| `Field không được hỗ trợ` | Có thể sai tên JSON, ví dụ phải dùng `lambda`, không dùng ký tự `λ` làm key |
| `Comparison cần F=f+2*lambda` | Đặt F đúng trước khi chạy so sánh |
| Không kết nối được engine | Kiểm tra server còn chạy và đang mở đúng địa chỉ/cổng |
| Output đã tồn tại khi chạy CLI | Đổi thư mục output; công cụ giữ kết quả cũ và từ chối ghi đè |
| Bản nháp đã thay đổi | Số đang xem thuộc input cũ; chạy lại cho input mới |

### 11.3. Những điều cần nhớ để tránh đọc sai

- **a/b là giả định về tín hiệu**, không phải accuracy đo được từ người thật.
- **p là dự đoán report của peer**, không phải xác suất claim đạt.
- **H là quyền quan sát thêm X**, không đảm bảo trung thực hoặc đúng tuyệt đối.
- **Score cao là điểm thưởng cao**, không đảm bảo accuracy cao.
- **Regret bằng 0 là không có lợi khi tự đổi**, không đảm bảo kết quả xã hội tốt.
- **Delta phải đọc từng Z** vì effort được chọn sau Z.
- **B là trần cho phép**, không phải số luôn chi hết.
- **V chỉ đổi thước đo payout trong M1**, không tạo trách nhiệm tài chính cho Judge khi sai.
- **Kết quả là kỳ vọng theo mô hình**, chưa phải hành vi người thật, giao dịch thật hoặc dự đoán cân bằng sẽ được chọn.

## 12. File kết quả và metadata dùng để làm gì?

### 12.1. Tải file nào để xem phần nào?

| File hoặc nhóm file | Dùng khi nào? |
| --- | --- |
| `report.md` | Đọc kết luận và giới hạn bằng văn bản |
| `summary.json` | Tra metrics chính, utility và trạng thái; với comparison chứa kết quả hai cơ chế |
| `best_responses.json` | Xem đủ sáu certificate, report ties và witness của analyze |
| `states.csv` | Kiểm tra đóng góp của 32 trạng thái vào kết quả analyze |
| `equilibria.json` | Xem ứng viên/certificate và cách ghép hai nhánh của search |
| `sweep.csv`, `sweep.json` | Xem mỗi điểm quét, gồm cả hàng lỗi |
| `test_results.json`, `test_log.txt` | Đọc các test đã chạy và lỗi thực tế |
| `manifest.json` | Xác định run đã dùng input, source và tài liệu phiên bản nào |
| `inputs/` | Bản input/source/tài liệu được pin cho lần chạy để truy vết |
| `fixed/`, `rbts/` | Hai bộ artifact analyze riêng bên trong một run comparison |

Không phải mỗi operation đều sinh mọi file trong bảng. Ví dụ sweep không xuất 32 states cho từng điểm; hãy Analyze một điểm nếu cần chi tiết đó.

### 12.2. Các cột của states.csv

| Cột hoặc hậu tố | Nghĩa |
| --- | --- |
| `state_id` | Số thứ tự trạng thái, không phải một claim thật |
| `y`, `z`, `x_A`, `x_B`, `x_C` | Các giá trị Y/Z/X của trạng thái đó |
| `probability_*` | Xác suất của trạng thái; tổng 32 hàng bằng 1 |
| `decision` | D=0/1 từ đa số report |
| `wrong_payout_contribution_*` | V nhân xác suất hàng nếu Y=0,D=1; bằng 0 ở hàng khác |
| `A_action`, `A_report`, `A_prediction_*` | Action, report và prediction của A tại hàng này; B/C tương tự |
| `A_reference_id`, `A_peer_id` | Chỉ số người tham chiếu và peer của A; `0=A,1=B,2=C` |
| `A_shadow_*` | Prediction đã dịch bằng report A để tính information score |
| `A_information_score_*`, `A_prediction_score_*` | Hai thành phần điểm tại trạng thái |
| `A_total_score_*`, `A_score_*` | Cùng tổng điểm trong output hiện tại |
| `A_reward_*`, `A_effort_cost_*`, `A_utility_*` | Thưởng, chi phí và utility tại trạng thái, chưa nhân xác suất |
| `_exact` | Giá trị phân số chính xác |
| `_decimal` | Bản thập phân để đọc/vẽ |

Tổng `wrong_payout_contribution_exact` bằng wrong payout value. Muốn tính reward trung bình từ các hàng thì phải nhân reward của từng hàng với probability tương ứng rồi cộng; không lấy trung bình đều 32 hàng.

### 12.3. Nhãn phiên bản và hash

| Tên | Mục đích |
| --- | --- |
| `run_id` | Phân biệt các lần chạy |
| `operation` | Loại tác vụ: analyze/equilibria/sweep/compare/tests |
| `mechanism` | Cơ chế thưởng fixed hay rbts |
| `model_version` | Phiên bản của game đang được tính |
| `engine_revision`, source hash | Nhận diện code đã chạy |
| `config_hash`, `profile_hash` | Nhận diện cấu hình và profile theo dạng chuẩn |
| Spec revision, `freeze_status`, documents | Truy vết tài liệu, snapshot và sự kiện đóng băng đã dùng |
| `duration_seconds` | Thời gian tính toán; không phải chi phí review con người |
| `arithmetic=rational_exact` | Tính toán bằng phân số chính xác |
| `randomness=none` | Không có bốc mẫu ngẫu nhiên trong phép enumeration |

Hash là dấu nhận diện dữ liệu/code, không phải điểm số chất lượng hoặc chứng minh toán đúng. `"0.5"` và `"1/2"` cùng giá trị nên có thể có cùng semantic config hash, trong khi raw bytes của hai file vẫn khác nhau.

## 13. Phụ lục công thức — Chỉ đọc khi muốn hiểu sâu hơn

### 13.1. Thưởng và utility

```text
Fixed:
  Reward_i  = F
  Utility_i = F - c_i × 1[e_i=H]

RBTS:
  Reward_i  = f + lambda × Score_i
  Utility_i = Reward_i - c_i × 1[e_i=H]
```

Các ký hiệu đã gặp: i là Judge đang xét; c_i là chi phí của người đó; e_i là effort; Score_i nằm trong [0,2].

### 13.2. Công thức điểm RBTS

```text
Q(p,1) = 2p - p²
Q(p,0) = 1 - p²

delta_j = min(p_j, 1-p_j)
shadow_i = p_j + (2r_i-1) × delta_j

InformationScore_i = Q(shadow_i, r_k)
PredictionScore_i  = Q(p_i, r_k)
Score_i = InformationScore_i + PredictionScore_i
```

| Ký hiệu | Vai trò |
| --- | --- |
| `Q(p,r)` | Hàm chấm một prediction p khi report đối chiếu là r; nằm trong [0,1] |
| `j`, `k` | Người tham chiếu và peer theo bảng vai trò ở mục 6 |
| `delta_j` | Bước dịch prediction tham chiếu, lấy phía nhỏ hơn của p_j và 1−p_j |
| `shadow_i` | p_j được dịch lên nếu r_i=1, xuống nếu r_i=0; vẫn nằm trong [0,1] |
| `r_k` | Report của peer được dùng để chấm cả hai thành phần |

Ví dụ p_j=0.7 thì delta_j=0.3: r_i=1 tạo shadow=1, r_i=0 tạo shadow=0.4. Đây là bước biến đổi trong scoring, không phải một quan sát mới về Y.

Ví dụ riêng cho Q: p=0.8, report đối chiếu=1 thì Q=0.96; report đối chiếu=0 thì Q=0.36. Điểm được tính theo report của peer, kể cả report đó sai về sự thật.

### 13.3. Các V_L/V_H trong best response không phải payout V

Các công thức U_L/U_H dưới đây dành cho RBTS. Với fixed, thay phần thưởng bằng F như mục 13.1.

```text
V_L,i(z) = Score kỳ vọng tối ưu khi i chọn L tại Z=z
V_H,i(z) = Score kỳ vọng tối ưu khi i chọn H tại Z=z, chưa trừ cost

U_L,i(z) = f + lambda×V_L,i(z)
U_H,i(z) = f + lambda×V_H,i(z) - c_i

Delta_i(z) = U_H,i(z)-U_L,i(z)
           = lambda×(V_H,i(z)-V_L,i(z)) - c_i

BR_i(z) = max(U_L,i(z), U_H,i(z))
Regret_i(z) = BR_i(z) - CandidateUtility_i(z)
```

`V_L`/`V_H` ở đây là **điểm tối ưu trước chi phí**. V trong `payout_value` là giá trị giải ngân. Chúng dùng chữ giống nhau nhưng có vai trò khác nhau.

H có thể lấy X rồi bỏ qua nó, nên điểm tối ưu trước cost của H không thấp hơn L. Sau khi trừ cost, utility H vẫn có thể thấp hơn.

`delta_j` trong scoring cũng khác `Delta_i(z)` về effort ở trên. Đừng dùng bước dịch prediction để đọc kết luận H/L.

### 13.4. Những ký hiệu khác khi đọc spec

| Ký hiệu trong spec | Đọc bằng lời |
| --- | --- |
| `w=(y,z,x_A,x_B,x_C)` | Một trạng thái cụ thể trong 32 tổ hợp |
| `L_t(s\|y)` | Xác suất tín hiệu s khi sự thật y: bằng t nếu s=y, bằng 1−t nếu khác |
| `q_i(I)` | Xác suất peer k báo 1 với thông tin I; là prediction tối ưu khi lambda>0 |
| `A_i(I,r)` | Information score kỳ vọng nếu i báo r với thông tin I; chữ A ở đây không chỉ Judge A |
| `v_i(I)` | Điểm tốt nhất tại quan sát I: chọn report tốt nhất và prediction tốt nhất |
| `m`, `mass` | Trọng số xác suất của một nhóm trạng thái/quan sát |
| `sigma_i` / `σ_i` | Toàn bộ chiến lược của i: effort map, report map, prediction map |
| `sigma_-i` / `σ_-i` | Chiến lược của những người còn lại |
| `argmax`, `tie` | Các lựa chọn đạt giá trị cao nhất; tie nghĩa có nhiều lựa chọn hòa nhau |
| `reachable observation` | Quan sát có thể gặp dưới effort/chiến lược đang xét |
| `ex ante` | Tính từ trước khi biết tín hiệu, có trọng số xác suất các nhánh |
| `conditional` | Tính sau khi đã giới hạn vào một nhánh hoặc quan sát |

## 14. Cơ sở và bằng chứng cho hướng dẫn này

Đây là file giải thích và cách sử dụng; không thay đổi game, engine, giao diện hoặc kết quả lịch sử. Khi cần định nghĩa chính xác, tra:

- [CEAV_M1_SPEC.md](CEAV_M1_SPEC.md), §4–11: biến, thông tin, scoring, best response, cân bằng và metrics; §18: giao diện.
- [ENGINE_DESIGN.md](ENGINE_DESIGN.md), §3–9: schema, prediction, certificate và output.
- [VERIFICATION_PLAN.md](VERIFICATION_PLAN.md): cách kiểm chứng thuật toán, T-ID và browser acceptance.
- [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md): trạng thái triển khai và evidence nghiệm thu đã ghi nhận.

Các số trong ví dụ đã được chạy lại bằng CLI hiện tại, không chỉ chép từ màn hình hoặc suy từ tên preset. Evidence mới được giữ riêng tại [results/guide-20261022T130759Z-18c2b8/](results/guide-20261022T130759Z-18c2b8/):

| Lần chạy | Input/chức năng | File để đối chiếu |
| --- | --- | --- |
| `g1` | G1 + all-H + rbts | [summary](results/guide-20261022T130759Z-18c2b8/g1/summary.json), [best responses](results/guide-20261022T130759Z-18c2b8/g1/best_responses.json) |
| `all-z` | G1 + all-Z + rbts | [summary](results/guide-20261022T130759Z-18c2b8/all-z/summary.json) |
| `g3` | G3 + all-H + rbts | [best responses](results/guide-20261022T130759Z-18c2b8/g3/best_responses.json) |
| `g4` | G4 + all-H + rbts | [best responses và witness](results/guide-20261022T130759Z-18c2b8/g4/best_responses.json) |
| `compare` | G1 + all-H, fixed/RBTS cùng trần | [summary](results/guide-20261022T130759Z-18c2b8/compare/summary.json) |
| `sweep` | G1 + all-H + rbts, lambda=0,1/2,1,2 | [sweep](results/guide-20261022T130759Z-18c2b8/sweep/sweep.json) |
| `search` | Tìm cân bằng thuần G1 + rbts | [equilibria](results/guide-20261022T130759Z-18c2b8/search/equilibria.json) |

Cả bảy lệnh hoàn thành với exit code 0. Điểm lambda=2 của sweep vẫn được lưu là invalid_budget đúng như mô tả. Các manifest chứa argv và inputs để truy vết. Các lần chạy này xác nhận ví dụ của hướng dẫn, không thay thế full suite hoặc tạo một nghiệm thu browser mới.

Các bước bấm nút trong hướng dẫn được đối chiếu với `web/index.html` và `web/app.js` hiện tại. Công thức được giải thích theo game M1 đã đặc tả, không mở rộng thành bảo đảm học thuật cho môi trường ngoài mô hình.
