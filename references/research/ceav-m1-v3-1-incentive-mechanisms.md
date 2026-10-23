# CEAV-M1 V3.1 — Nghiên cứu trade-off incentive của ba Judge

**Ngày đối chiếu nguồn:** 2026-10-24  
**Phạm vi:** nghiên cứu cơ chế, không sửa game/code và không phải bằng chứng production  
**Model đang xét:** `ceav-m1-v3.0`; V3.1 chỉ đánh giá robustness trên grid đã khai báo

## Kết luận nghiên cứu

Không có cơ chế nào trong các nguồn dưới đây đồng thời bảo đảm high-effort, truthfulness, chi phí thấp và false rejection thấp trong game một claim, ba Judge hiện tại. Trade-off của CEAV là có thật:

- Tăng trọng số reward có thể làm high-effort có lợi hơn chi phí, nhưng bị giới hạn bởi reward budget và có thể làm `cash_review_cost` tăng.
- Verification anchor tạo tín hiệu đối chiếu với `T`, nhưng `T` nhiễu có thể làm Judge học theo tín hiệu sai. Nó cũng không sửa `D` hay payout của claim hiện tại vì `D` đã được khóa trước audit.
- Peer prediction có thể duy trì incentive mà không cần ground truth, nhưng không tự loại bỏ cân bằng tín hiệu rẻ hoặc phối hợp báo cáo.
- Bayesian Truth Serum và Correlated Agreement có các bảo đảm riêng, nhưng đều cần thông tin/cấu trúc multi-task hoặc population khác với một claim và ba Judge của V3.
- Participation constraint có thể lọc Judge có chất lượng thấp, nhưng với đúng ba Judge sẽ tạo bài toán quorum/fallback mới.

Vì vậy, V3.1 nên dùng sweep exact với cùng budget, giữ các equilibrium bất lợi và báo cáo riêng effort margin, false approval, false rejection, wrong payout và cash review cost. Việc thay RBTS bằng BTS/CA, thêm `pass`, tournament hoặc audit chọn theo report phải là model version mới; không đưa vào V3.1 bằng cách đổi nghĩa của các field hiện có.

## 1. Game hiện tại và nơi trade-off xuất hiện

Các ràng buộc dưới đây lấy từ [đặc tả V3 anchor](../../CEAV_M1_V3_ANCHOR_SPEC.md), [thiết kế V3](../../ENGINE_DESIGN_V3_ANCHOR.md) và [đặc tả robustness V3.1](../../CEAV_M1_V3_1_ROBUSTNESS_SPEC.md):

| Thành phần | CEAV-M1 V3/V3.1 |
| --- | --- |
| Người chơi | Đúng ba Judge A/B/C; decision là majority 2/3 |
| Thông tin | Mọi Judge thấy public signal `Z`; chỉ High Effort mới thấy private signal `X_i` |
| Hành động | Mỗi nhánh `Z` có `L0`, `L1`, `H00`, `H01`, `H10`, `H11`; report là nhị phân và prediction nhắm vào report của peer |
| Reward | `f + lambda_peer * PeerScore + anchor_weight * AnchorScore`; peer score là RBTS, anchor score khớp report với `T` khi claim được audit |
| Audit | `A` được lấy ngẫu nhiên sau khi report khóa; `T` có sensitivity/specificity; `T` không đọc `Y` trong reward oracle và không sửa `D` |
| Chi phí | Judge trả `c_i` nếu mua High Effort; hệ thống có `cost_per_audit`; V3.1 có thêm uncertainty multiplier cho High Effort |
| Budget | Worst-case reward cap: `3f + 6*lambda_peer + 3*anchor_weight <= B` |
| Metrics | `FA`, `FR`, `WP`, accuracy, reward, effort cost, expected audit cost, cash review cost |
| Giới hạn | Pure-strategy reduced normal form; chưa có participation, non-reveal, timeout, correlation, collusion, Sybil, stake/slashing, appeal hay settlement |

Với peer strategy đã khóa, suy luận trực tiếp từ payoff V3 cho chênh lệch effort ở nhánh `z` có dạng:

```text
DeltaU_i,z = lambda_peer * DeltaPeer_i,z
           + anchor_weight * q * DeltaAnchor_i,z
           - c_i
```

Trong đó mỗi `Delta` phải được tính sau khi focal Judge tối ưu report/prediction hợp lệ cho effort thử; peer tables và distribution của `A,T` vẫn giữ nguyên. Đây là công thức phân tích cho CEAV, không phải định lý được kế thừa từ các bài nghiên cứu. Nếu lợi ích thông tin của một thành phần bằng không hoặc âm, tăng trọng số thành phần đó không tự tạo ra high-effort incentive. Nếu lợi ích dương nhưng ngưỡng cần vượt `B`, kết quả là `BUDGET_INFEASIBLE`, không phải bằng chứng cơ chế thất bại về mặt toán học.

`D` được tính trước audit. Vì vậy, với một strategy profile cố định, thay `q`, `T` hoặc `anchor_weight` không trực tiếp đổi `D`, `FA`, `FR` hay `WP`. Nếu các metric này đổi giữa policy, nguyên nhân là tập equilibrium hoặc strategy profile thay đổi do payoff; cần báo cáo witness và không mô tả đó là anchor đã sửa payout.

## 2. Nguồn chính và claim có thể dùng

### 2.1 Peer prediction và RBTS

**Claim từ nguồn.** Miller, Resnick và Zeckhauser xây dựng peer prediction trong đó mỗi rater báo signal và được chấm bằng proper scoring rule trên posterior về report của rater khác; bài chứng minh honest reporting là một Nash equilibrium trong mô hình của họ và nêu việc scale scoring để khuyến khích effort. [Bài gốc, Management Science, DOI 10.1287/mnsc.1050.0379](https://pubsonline.informs.org/doi/10.1287/mnsc.1050.0379)

Witkowski và Parkes đưa ra Robust Bayesian Truth Serum cho population nhỏ; bản tóm tắt nguồn của CEAV ghi rõ Theorem 9/10 chỉ bảo đảm trong mô hình tín hiệu và common prior của bài, không bảo đảm effort tối ưu, equilibrium duy nhất, chống liên minh hay majority đúng. [PDF AAAI chính thức](https://cdn.aaai.org/ojs/8261/8261-13-11789-1-2-20201228.pdf) và [bản ghi nguồn CEAV](../PRIMARY_SOURCES.md).

**Suy luận cho CEAV.** RBTS là baseline hợp lý cho `lambda_peer`, nhưng guarantee của RBTS không tự chuyển sang game có `Z`, effort sau `Z`, chi phí `c_i`, ba Judge và majority. Đặc biệt, V3 vẫn giữ các action bỏ qua `X_i`; reward peer cao có thể làm Judge tối ưu agreement/prediction mà không mua thông tin. Điều này khớp với việc V2.2 phải tách `V_H`, `V_H_dep`, effort margin và report utilization thay vì chỉ nhìn điểm score.

**Thử nghiệm.** Giữ policy `anchor_weight=0` làm ablation peer-only; chạy toàn bộ 432 candidates/point và ghi:

- effort margin của từng `Judge × Z`, gồm cả `H00/H11`;
- số equilibrium low-effort, high-effort, mixed-effort và report-ignored;
- score peer, utility sau trừ cost, `FA/FR/WP/CC` và witness của equilibrium xấu nhất.

**Rủi ro.** Peer agreement có thể thưởng một profile cùng báo sai hoặc profile dựa vào public signal. Existence của một truthful/high-effort equilibrium không chứng minh hệ thống sẽ chọn nó; đó là lý do V3.1 phải lấy worst-case trên mọi pure equilibrium.

### 2.2 Bayesian Truth Serum (BTS)

**Claim từ nguồn.** Prelec đề xuất Bayesian Truth Serum cho dữ liệu chủ quan khi không có tiêu chuẩn công khai để kiểm tra truthfulness. Cơ chế kết hợp câu trả lời của cá nhân với dự đoán về phân phối câu trả lời của người khác, từ đó tạo information score và prediction score. [Bài gốc, Science, DOI 10.1126/science.1102081](https://pubmed.ncbi.nlm.nih.gov/15486294/)

**Suy luận cho CEAV.** BTS cần một population statistic hoặc nhiều respondent/task để so sánh câu trả lời cá nhân với dự đoán về tần suất của người khác. Một claim với đúng ba Judge không cho cùng thông tin như mô hình population của BTS; dùng lại `p_i` hiện tại mà không đổi nghĩa sẽ không phải BTS. Prior `pi` của CEAV cũng không đồng nhất với tần suất report của Judge, vì `D` là majority còn `Y` là ground truth ẩn.

**Thử nghiệm đề xuất cho version sau.** Tạo một game multi-task độc lập: mỗi Judge trả lời nhiều claim, thêm forecast về tỷ lệ câu trả lời của nhóm, rồi so sánh BTS với RBTS dưới cùng reward cap và cùng chi phí High Effort. Giữ một oracle synthetic để đo `FA/FR/WP`; kiểm tra riêng calibration của forecast và accuracy của majority. Không đưa kết quả đó vào V3.1 vì nó thay information structure và payoff.

**Rủi ro.** Với nhóm chỉ có ba Judge, tần suất thực nghiệm có variance lớn; Judge có thể tối ưu dự đoán group frequency thay vì report có ích cho claim. BTS cũng không cung cấp ground truth cho từng claim, nên không tự giải quyết false approval.

### 2.3 Correlated Agreement (CA) và informed truthfulness

**Claim từ nguồn.** Shnayder, Agarwal, Frongillo và Parkes giới thiệu Correlated Agreement cho nhiều signal và định nghĩa informed truthfulness: không strategy profile nào có expected payment cao hơn truthful reporting ở equilibrium, còn truthful equilibrium cao hơn mọi strategy không dùng thông tin. Bản detail-free dùng nhiều task để học statistics và chỉ đạt epsilon-informed truthfulness trong setting tương ứng. [Bài EC16 trên trang tác giả](https://parkes.seas.harvard.edu/publications/informed-truthfulness-multi-task-peer-predictions), [preprint](https://arxiv.org/abs/1603.03151), [DOI ACM 10.1145/2940716.2940790](https://doi.org/10.1145/2940716.2940790)

**Suy luận cho CEAV.** CA là ứng viên trực tiếp nhất nếu mục tiêu là đẩy profile không dùng `X_i` xuống, nhưng claim của bài gắn với signal distribution và multi-task. V3 có một claim, một report/Judge và public signal chung; thay scoring bằng CA sẽ cần định nghĩa task overlap, correlation matrix và cách xử lý ba Judge. Không thể gọi một sweep `anchor_weight` là CA.

**Thử nghiệm đề xuất cho version sau.** Dùng batch `m` claim độc lập với cùng ba Judge, trong đó một số task chồng lấn giữa các cặp Judge. So sánh:

1. RBTS hiện tại trên từng task;
2. CA với cùng tổng reward reserve;
3. CA cộng anchor spot-check trên một subset task.

Đo high-effort rate từng Judge, truthful/report-dependent rate, số equilibrium không dùng private signal, variance reward và các metric claim-level. Sweep `m`, correlation quality và cost; không dùng kết quả đầu tiên của một equilibrium để kết luận.

**Rủi ro.** CA có thể cần biết joint signal distribution; detail-free learning cần nhiều task và có sai số thống kê. Correlation giữa các claim hoặc shared public Z có thể làm tín hiệu rẻ trông như thông tin riêng. Với ba Judge, một collusive profile vẫn cần được kiểm tra riêng; informed truthfulness trong mô hình bài không phải coalition-proofness của CEAV.

### 2.4 Proper scoring rules

**Claim từ nguồn.** Gneiting và Raftery định nghĩa scoring rule là proper khi expected score đạt cực đại khi forecast đúng với phân phối của outcome; strict propriety làm forecast đúng là nghiệm duy nhất. Bài phân tích quadratic/Brier, logarithmic và nhiều scoring rule khác. [Bài gốc, JASA, DOI 10.1198/016214506000001437](https://doi.org/10.1198/016214506000001437)

**Suy luận cho CEAV.** Properness chỉ nói forecast trung thực với outcome được chấm. Trong CEAV, `p_i` đang dự đoán report của peer `k`, không phải `Y` và không phải `T`; đây là điểm cần giữ để không biến scoring thành ground-truth reward. Nếu đổi outcome sang anchor `T`, forecast có thể proper với `T` nhưng vẫn lệch khỏi `Y` khi anchor noisy. Proper scoring cũng không tự trả chi phí mua `X_i`; high-effort chỉ được khuyến khích khi signal làm expected score tăng đủ lớn so với `c_i`.

**Thử nghiệm trong V3.1.** Giữ quadratic score hiện tại để duy trì exact `Fraction`; so sánh peer-only, anchor-only và hybrid bằng cùng budget cap. Kiểm tra `DeltaPeer` và `DeltaAnchor` trước khi sweep reward. Log score không nên đưa vào V3.1 vì cần xử lý số thực/log và tạo model/verification contract mới.

**Rủi ro.** Một scoring rule proper theo report của peer hoặc T có thể làm forecast đẹp hơn nhưng không cải thiện decision majority. Không được dùng điểm score cao làm proxy cho accuracy, false approval hoặc tiền trả sai.

### 2.5 Selective verification và ground truth hạn chế

**Claim từ nguồn.** Gao, Wright và Leyton-Brown chỉ ra rằng peer prediction có thể có equilibrium không trả chi phí để đánh giá chính xác khi tồn tại tín hiệu chất lượng thấp/rẻ; họ nghiên cứu spot-check với ground truth hạn chế và cho thấy cơ chế đơn giản chấm report với trusted ground truth ở một số task có thể có guarantee incentive mạnh hơn một lớp lớn cơ chế peer prediction. [Bài AIJ 2019, DOI 10.1016/j.artint.2019.03.004](https://doi.org/10.1016/j.artint.2019.03.004), [bản extended abstract IJCAI chính thức](https://www.ijcai.org/proceedings/2020/0723.pdf)

Witkowski, Bachrach, Key và Parkes phân tích effort/participation với quality oracle hoặc outside option `pass`; họ báo cáo rằng cấm negative payment có thể làm expected cost tăng 2–5 lần trong mô hình của họ. [Bài HCOMP/AAAI chính thức, DOI 10.1609/hcomp.v1i1.13089](https://ojs.aaai.org/index.php/HCOMP/article/view/13089)

**Suy luận cho CEAV.** V3 anchor là một dạng selective verification claim-level: audit ngẫu nhiên sau khi report khóa, chấm match với `T`, nhưng không đưa `T` vào `D`. Đây là thiết kế sạch để tách incentive khỏi settlement; đổi lại nó chỉ tác động FR/FA gián tiếp qua strategy/equilibrium. Anchor quality thấp và `anchor_weight` cao có thể làm Judge nghiêng theo `T` sai. Audit chọn sau khi nhìn report hoặc report-sensitive audit có thể tiết kiệm cost, nhưng tạo một game khác vì Judge sẽ tối ưu cả report và xác suất bị kiểm tra.

**Thử nghiệm trong V3.1.** Giữ audit ngẫu nhiên làm baseline; sweep độc lập `q`, `sens_T`, `spec_T`, `anchor_weight` và `cost_per_audit`. Báo cáo thêm `P(r_i=T | A=1)`, expected anchor reward, audit cost và thay đổi effort margin. Dùng hai ablation:

- `q=0` hoặc `anchor_weight=0`: hồi quy exact về peer-only;
- `lambda_peer=0`: đo xem anchor đơn độc có tạo report-dependent high effort hay chỉ trả reward theo noise.

**Rủi ro.** Trusted ground truth/anchor trong bài nghiên cứu không đồng nghĩa CEAV đã có auditor production. `T` phải có provenance độc lập; synthetic sensitivity/specificity chỉ là assumption. V3.1 không được gọi anchor là cơ chế sửa payout trực tiếp.

### 2.6 Contest/tournament

**Claim từ nguồn.** Lazear và Rosen phân tích rank-order tournament, trong đó trả công theo thứ hạng có thể tạo allocation effort hiệu quả như trả theo output cá nhân trong các điều kiện của mô hình; bài cũng chỉ ra vấn đề heterogeneity và handicap. [Bài gốc, Journal of Political Economy, DOI 10.1086/261010](https://doi.org/10.1086/261010)

**Suy luận cho CEAV.** Tournament có thể được hiểu là trả reward dựa trên rank của peer/anchor score giữa ba Judge. Tuy nhiên, trong CEAV các Judge cùng chịu `Z` và có thể cùng gặp noise; rank không đo được đóng góp cận biên. Với ba người, tie thường xuyên và relative payment tạo zero-sum pressure. Judge có thể tối ưu đánh bại peer thay vì giảm false approval; shared public-signal profile và collusion cũng chưa được giải quyết.

**Thử nghiệm đề xuất cho version sau.** Chỉ dựng một counterfactual tournament với cùng tổng reward cap: thưởng theo rank của score đã khóa, xử lý tie deterministic và ghi rõ utility transfer. So sánh với hybrid reward trên cùng signal/effort config. Gate phải gồm high-effort rate, `FA`, `FR`, `WP`, reward variance và số profile coordinated; tournament chỉ được xem là ứng viên nếu không làm xấu tail metrics.

**Rủi ro.** Relative reward có thể làm một Judge nhận ít hơn dù report đúng; nếu cho negative payment sẽ phát sinh liability/participation constraint chưa có trong V3. Không nên thêm tournament vào V3.1 vì nó đổi payoff và có thể đổi cả equilibrium set.

### 2.7 Participation constraints và outside option

**Claim từ nguồn.** Witkowski et al. mô hình hóa action `pass` với utility ngoài cơ chế bằng 0; payment có thể được thiết kế để agent chất lượng thấp pass, còn agent chất lượng đủ cao tham gia và mua effort. Kết quả này gắn với quality distribution, payment cho phép và matching assumptions của bài; nó không phải guarantee cho CEAV.

**Suy luận cho CEAV.** V3 hiện bắt cả ba Judge gửi report. Thêm `pass` sẽ làm majority 2/3 không còn luôn xác định; cần quyết định quorum, fallback `D`, refund/payout và cách chấm Judge không reveal. Nếu một Judge pass, hai report còn lại có thể hòa hoặc tạo quyết định hình thức; đó là state machine mới, không phải field policy hiện tại.

**Thử nghiệm đề xuất cho version sau.** Mở rộng action space thành `{pass, L0, L1, H00, H01, H10, H11}`; thử các policy quorum riêng, ví dụ yêu cầu đủ hai report hoặc chuyển `INCONCLUSIVE`. Đo coverage/quorum failure cùng `FA/FR/WP`, cost và expected utility. Chỉ so sánh với V3 khi fallback policy, payout safety và budget đã được pin trước.

**Rủi ro.** Participation có thể giảm false approval bằng cách bỏ Judge yếu nhưng đồng thời làm tăng false rejection hoặc số claim không quyết định. Negative payment có thể giảm cost theo nguồn, nhưng không tự phù hợp với safety/solvency của CEAV.

### 2.8 Reward học tuần tự và posted price

**Claim từ nguồn.** Liu và Chen nghiên cứu cơ chế peer prediction tuần tự, trong đó requester học mức reward qua nhiều vòng để cân bằng chất lượng thông tin và tổng payment; trong mô hình của họ, effort theo threshold và truthful reporting tạo một equilibrium dưới các điều kiện riêng. [Bài AAAI chính thức, DOI 10.1609/aaai.v31i1.10619](https://ojs.aaai.org/index.php/AAAI/article/view/10619)

**Suy luận cho CEAV.** V3/V3.1 là one-shot static game: policy và reward được công bố trước khi Judge gửi report. Cho worker học `q`, `lambda_peer` hoặc `anchor_weight` qua nhiều claim sẽ thêm state, belief về các vòng sau và khả năng thao túng dữ liệu học; không thể dùng threshold guarantee của bài như guarantee cho ba Judge hiện tại.

**Thử nghiệm đề xuất cho version sau.** Chỉ sau khi có game repeated rõ ràng, thử posted price theo batch với budget per claim và cap tổng. Đo regret so với oracle policy, effort rate, quality drift, false approval/rejection theo thời gian và khả năng Judge báo sai để làm lệch giá vòng sau.

**Rủi ro.** Adaptive reward có thể làm mất tính reproducible của một claim, tạo incentive ngắn hạn và phá giả định peer freeze. Nó cũng làm metric của V3.1 không còn so sánh cùng một payoff ở mọi point.

## 3. Thiết kế thử nghiệm nên chạy

Các thử nghiệm đầu tiên dưới đây nằm trong semantics V3.1 nếu chỉ thay ba policy fields và uncertainty axes đã allowlist. Chúng không thay code trong nghiên cứu này.

| ID | Câu hỏi | Thiết kế | Bằng chứng cần giữ |
| --- | --- | --- | --- |
| V31-I0 | Baseline hiện tại có high-effort equilibrium không? | `anchor_weight=0`, sweep `lambda_peer`; giữ V2/V3 known cases và all-low/all-Z baselines | 432 candidates/point, branch margins, retained equilibrium IDs |
| V31-I1 | Anchor có tạo effort margin thật không? | `lambda_peer=0`, sweep `q × anchor_weight × anchor quality`; giữ reward cap | `DeltaAnchor`, report maps, `P(r=T)`, FR/FA/WP/CC |
| V31-I2 | Peer và anchor phân bổ budget thế nào? | So sánh các cặp thỏa cùng `3f+6lambda_peer+3anchor_weight`; không so policy khác reserve mà gọi là cost-neutral | worst metrics, expected reward components, effort cost, audit cost |
| V31-I3 | Tăng audit có đáng với cost không? | Giữ `anchor_weight` và quality, sweep `q` và `cost_per_audit`; ghi rõ cap không chứa q nhưng cash cost có `q*kappa_audit` | Pareto `(worst_FA, worst_WP, worst_FR, worst_CC)` và witness |
| V31-I4 | Anchor noise đẩy FR hay FA? | Sweep riêng `sens_T` và `spec_T` khi schema cho phép; thêm quality equalized làm control | Strategy change so với fixed-profile counterfactual; không gán thay đổi FR trực tiếp cho T |
| V31-I5 | Có còn low-cost/all-Z equilibrium? | Giữ cùng config, tăng quality/cost multiplier và reward; không bỏ profile bất lợi | equilibrium taxonomy, low-effort count, worst-equilibrium gate |
| V31-I6 | Policy có robust trên uncertainty grid không? | Chạy toàn bộ predeclared 108 points, không nội suy và không chọn best equilibrium | `failure_map`, `policy_summary`, `pareto_frontier`, report giữ failure reasons |

Trước khi gọi một policy “tăng high-effort”, cần đặt điều kiện tối thiểu là: high-effort được preferred tại cả hai `Z` cho từng Judge trong witness equilibrium đang xét, không chỉ có utility trung bình ex ante cao hơn. Khi có nhiều equilibrium, phải báo cả trường hợp high-effort tồn tại và trường hợp low-effort tồn tại; V3.1 chỉ dùng worst-case cho gate.

## 4. Thứ tự ưu tiên cho model tương lai

1. **Giữ hybrid anchor ngẫu nhiên làm baseline V3.1.** Đây là thay đổi tối thiểu và đã có semantics rõ: audit sau commit, `T` không sửa settlement, reward budget pin theo worst case. Tập trung vào phân tích margin và robust grid trước khi thử cơ chế mới.
2. **Nếu có thể thu thập nhiều task độc lập, thử CA multi-task trước BTS.** CA nhắm trực tiếp vào informed truthfulness, nhưng phải pin task overlap, signal correlation và cách học statistics.
3. **Nếu có auditor đáng tin với capacity hữu hạn, thử spot-check đơn giản.** So sánh trực tiếp anchor match với peer-only, tách incentive benefit khỏi audit cost và false-negative/false-positive của anchor.
4. **Chỉ thêm participation khi đã chốt quorum và fallback payout.** Nó có thể lọc quality thấp nhưng làm thay đổi coverage và state machine của claim.
5. **Để tournament ở mức counterfactual cuối.** Relative scoring khó phù hợp với mục tiêu giảm false approval/false rejection khi chỉ có ba Judge và shared noise.

## 5. Rủi ro diễn giải

- `SPECIFIED`, `IMPLEMENTED`, `VERIFIED` và kết quả study phải giữ riêng. Bài nghiên cứu không chứng minh analyzer CEAV đúng; analyzer vẫn cần oracle, exhaustive search và V3.1 gates.
- “Truthful equilibrium tồn tại” không đồng nghĩa equilibrium được chọn trong runtime. Không dùng best equilibrium để cấp pass.
- `Y` chỉ là ground truth evaluator; không đưa `Y` vào reward để làm cho kết quả đẹp hơn.
- Accuracy không thay thế false approval, false rejection hoặc wrongly paid value. Với payout bất đối xứng, cần giữ `WP` cùng `FA`.
- Tín hiệu `T` có thể là anchor noisy, không phải auditor đã được kiểm chứng. `sens_T/spec_T` là provenance-bearing assumptions.
- CA/BTS/participation/tournament cần model version, freeze event, oracle và regression riêng. Không đổi semantics V3.1 để “fit” một theorem của nguồn.
- Các kết quả dưới đây không nói về mixed equilibrium, coalition, collusion, Sybil, bribery, sequential learning hoặc blockchain readiness.

## Tài liệu nguồn chính

1. [Miller, Resnick & Zeckhauser (2005), *Eliciting Informative Feedback: The Peer-Prediction Method*, Management Science, DOI 10.1287/mnsc.1050.0379](https://pubsonline.informs.org/doi/10.1287/mnsc.1050.0379)
2. [Prelec (2004), *A Bayesian Truth Serum for Subjective Data*, Science, DOI 10.1126/science.1102081](https://doi.org/10.1126/science.1102081)
3. [Shnayder, Agarwal, Frongillo & Parkes (2016), *Informed Truthfulness in Multi-Task Peer Prediction*, EC16, DOI 10.1145/2940716.2940790](https://doi.org/10.1145/2940716.2940790)
4. [Gneiting & Raftery (2007), *Strictly Proper Scoring Rules, Prediction, and Estimation*, JASA, DOI 10.1198/016214506000001437](https://doi.org/10.1198/016214506000001437)
5. [Gao, Wright & Leyton-Brown (2019), *Incentivizing Evaluation with Peer Prediction and Limited Access to Ground Truth*, Artificial Intelligence, DOI 10.1016/j.artint.2019.03.004](https://doi.org/10.1016/j.artint.2019.03.004)
6. [Witkowski, Bachrach, Key & Parkes (2013), *Dwelling on the Negative: Incentivizing Effort in Peer Prediction*, HCOMP, DOI 10.1609/hcomp.v1i1.13089](https://doi.org/10.1609/hcomp.v1i1.13089)
7. [Lazear & Rosen (1981), *Rank-Order Tournaments as Optimum Labor Contracts*, Journal of Political Economy, DOI 10.1086/261010](https://doi.org/10.1086/261010)
8. [Liu & Chen (2017), *Sequential Peer Prediction: Learning to Elicit Effort using Posted Prices*, AAAI, DOI 10.1609/aaai.v31i1.10619](https://ojs.aaai.org/index.php/AAAI/article/view/10619)

Các tài liệu local sở hữu semantics CEAV là [CEAV_M1_V3_1_ROBUSTNESS_SPEC.md](../../CEAV_M1_V3_1_ROBUSTNESS_SPEC.md), [ENGINE_DESIGN_V3_1_ROBUSTNESS.md](../../ENGINE_DESIGN_V3_1_ROBUSTNESS.md), [CEAV_M1_V3_ANCHOR_SPEC.md](../../CEAV_M1_V3_ANCHOR_SPEC.md), [ENGINE_DESIGN_V3_ANCHOR.md](../../ENGINE_DESIGN_V3_ANCHOR.md) và [PRIMARY_SOURCES.md](../PRIMARY_SOURCES.md).
