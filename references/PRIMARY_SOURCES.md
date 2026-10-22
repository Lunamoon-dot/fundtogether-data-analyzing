# Nguồn gốc và phạm vi bảo đảm của CEAV-M1

Đối chiếu nguồn sơ cấp ngày 2026-10-22. Đây là ghi chú nguồn cho nghiên cứu độc lập; không phụ thuộc mã, baseline hoặc chính sách kinh tế của hệ thống FundTogether cũ.

## 1. RBTS: cơ chế chấm điểm, không phải bảo đảm thu thập thông tin

**Witkowski, J.; Parkes, D. C. (2012). _A Robust Bayesian Truth Serum for Small Populations_. AAAI.**

[Bài gốc, PDF chính thức](https://cdn.aaai.org/ojs/8261/8261-13-11789-1-2-20201228.pdf)

Tóm tắt: Eq. (7) định nghĩa quadratic score; Eq. (8) kết hợp information score và prediction score. Reference là `j=i+1`, peer là `k=i+2`, theo modulo n. Theorem 9 bảo đảm strict Bayes–Nash incentive compatibility với `n>=3`, common prior admissible và mô hình tín hiệu của bài. Theorem 10 cho score trong `[0,2]`. Bảo đảm nói về báo cáo khi peer trung thực, không chứng minh effort tối ưu, cân bằng duy nhất, chống liên minh hay độ đúng của majority. CEAV-M1 dùng công thức gốc làm đối chứng và tự phân tích game có public signal, effort và chi phí.

Định vị: trang in 1493, Definition 1; trang 1495, Eq. (7)–(8); trang 1497–1498, Theorem 9–10.

## 2. Tín hiệu rẻ: giới hạn của lựa chọn cân bằng

**Gao, X. A.; Wright, J. R.; Leyton-Brown, K. (2019). _Incentivizing Evaluation with Peer Prediction and Limited Access to Ground Truth_. Artificial Intelligence 275, 618–638.**

[Bài 2019, trang nhà xuất bản](https://www.sciencedirect.com/science/article/pii/S0004370219301559) · [DOI](https://doi.org/10.1016/j.artint.2019.03.004) · [Bản tóm lược của chính tác giả, IJCAI Journal Track 2020](https://www.ijcai.org/proceedings/2020/0723.pdf)

Tóm tắt: Bản IJCAI xác nhận là extended abstract của bài 2019. Theorem 1: với một universal mechanism chỉ dùng report, tồn tại môi trường nhiều tín hiệu khiến cân bằng báo cáo tín hiệu chất lượng cao không Pareto dominant khi lấy thông tin tốn thêm chi phí. Kết quả không nói effort luôn bất khả thi trong mọi môi trường. Phần giải pháp nghiên cứu trusted reports; CEAV-M1 không nhập vai trò này vào protocol. Nguồn dùng để giải thích cần kiểm tra cân bằng tín hiệu rẻ và tách existence khỏi equilibrium selection. Mệnh đề all-PASS/all-Z cụ thể của M1 phải được chứng minh trực tiếp.

Định vị nguồn đã đọc: IJCAI2020, trang 5142, Definition 1 và Theorem 1. Không trình bày bản tóm lược như toàn văn bài 2019.

## 3. Effort và reward learning đã có tiền lệ

**Liu, Y.; Chen, Y. (2017). _Sequential Peer Prediction: Learning to Elicit Effort using Posted Prices_. AAAI.**

[Trang bài và DOI](https://ojs.aaai.org/index.php/AAAI/article/view/10619) · [PDF chính thức](https://ojs.aaai.org/index.php/AAAI/article/view/10619/10478)

Tóm tắt: Bài nghiên cứu học mức thưởng qua nhiều vòng để cân bằng chất lượng thông tin và payment. Mô hình có `N>=4`, nhiều task, cơ chế nền DG13, expertise đồng nhất và chi phí effort i.i.d. khác nhau; phân tích threshold effort và truthful reporting theo các điều kiện riêng. Vì vậy, không thể coi effort incentive hoặc tối ưu mức thưởng tự thân là đóng góp mới. Cũng không thể chuyển bảo đảm của bài sang một claim, ba Judge và RBTS. CEAV-M1 chỉ dùng nguồn này để định vị prior work; chưa triển khai DG13 hay thuật toán học tuần tự.

Định vị: PDF trang in 608–609, Problem Formulation và Task assignment; trang 610 trở đi, Sequential Peer Prediction.

## 4. Quy tắc kiểm chứng riêng của CEAV-M1

Các công thức và yêu cầu dưới đây là suy luận cho mô hình M1, không phải định lý được kế thừa từ ba bài trên.

- Khi xét lệch đơn phương của Judge i, giữ nguyên toàn bộ bảng chiến lược `r_j,p_j,r_k,p_k` của peer. Không cập nhật dự đoán peer để thích ứng với effort mới của i.
- Prediction tối ưu nhắm vào **report của peer k**, không phải ground truth Y hoặc nhãn private signal: `q(h)=P(r_k=1 | h)`, với h là thông tin Judge i thực sự biết. Prediction liên tục tối ưu là `p_i=q(h)`, và expected prediction score là `1-q(h)+q(h)^2`.
- Tối ưu report nhị phân bằng so sánh hai expected information score có điều kiện trên h. Phải giữ joint distribution của `p_j,r_k`; không thay chúng bằng tích các biên vì hai biến có thể tương quan.
- Nếu effort được chọn sau khi thấy public signal Z, kiểm tra điều kiện effort tại từng `z` có xác suất dương: `lambda * (V_H(z)-V_L(z)) - c`. Trung bình ex ante dương chưa đủ chứng nhận chiến lược luôn H.
- H được phép bỏ qua X sau khi đã quan sát X. Giá trị H phải tối ưu trên report/prediction theo `(Z,X)`, thay vì bắt buộc báo `r=X`.
- Có 4 bảng report tất định `Z -> r` cho L, 16 bảng `(Z,X) -> r` cho H, và 4 chính sách effort `Z -> {L,H}`. Liệt kê bảng tất định đủ tìm một best response khi peer cố định và utility tuyến tính theo phân phối hành động; không đủ tìm mọi mixed equilibrium.
- Với `lambda>0`, có thể liệt kê theo từng nhánh public Z: mỗi Judge có 6 hành động `L0,L1,H00,H01,H10,H11`, tức 216 profile/nhánh. Dựng prediction Bayesian của candidate rồi giữ cố định prediction peer khi kiểm tra deviation. Ghép hai nhánh cho 36 behavior map/Judge, 46.656 profile đầy đủ khi không có ràng buộc nối hai nhánh. Hằng số H00/H11 vẫn cần giữ vì X có thể cải thiện prediction. Đây là liệt kê cân bằng thuần trong game rút gọn, không phải sequential refinement; `lambda=0` phải xử lý riêng. Chỉ gán prediction có điều kiện tại thông tin có xác suất dương.
- Tối ưu prediction bằng giải tích, không lưới hóa rồi gọi kết quả là tối ưu chính xác. Duy trì endpoint `p=0,1` của RBTS gốc; clipping tạo một biến thể cần định danh riêng.
- Ground truth Y của bộ sinh chỉ phục vụ phân phối và metric; reward oracle không được đọc Y. Accuracy, false approval và tiền giải ngân sai phải được tính tách khỏi score và effort incentive.

Các giá trị số, cân bằng, miền best response và tác động tiền giải ngân trong báo cáo phải gắn với cấu hình M1 cùng kết quả chạy tái lập; dẫn nguồn học thuật không thay thế bước kiểm chứng này.
