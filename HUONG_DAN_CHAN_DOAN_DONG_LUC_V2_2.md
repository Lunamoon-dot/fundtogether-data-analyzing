# Hướng dẫn đọc Chẩn đoán động lực V2.2

## 1. V2.2 làm gì?

V2.2 không tăng reward hoặc ép Judge dùng High Effort. Nó chạy hai phép kiểm tra:

```text
Candidate hiện tại
  -> giữ hai Judge còn lại cố định
  -> xem từng Judge có lợi khi mua X_i không

Mỗi điểm tham số
  -> duyệt lại đủ 432 branch candidates
  -> xem những loại cân bằng nào thực sự tồn tại
```

## 2. Cách chạy

1. Chọn model V2 và config/profile ở cột **Kịch bản**.
2. Mở **Chẩn đoán động lực**.
3. Để trống mọi axis nếu chỉ kiểm tra config hiện tại; hoặc bật `lambda`, cost, signal quality hay budget cần quét.
4. Bấm **Chạy chẩn đoán**.

Mỗi điểm hợp lệ chạy exhaustive pure search nên chậm hơn màn hình Phân tích.

## 3. Đọc một card Judge × Z

| Tên | Ý nghĩa |
| --- | --- |
| `V_L` | Điểm RBTS tốt nhất khi Judge không mua tín hiệu riêng |
| `V_H` | Điểm tốt nhất khi Judge mua tín hiệu và được chọn bất kỳ `H00/H01/H10/H11` |
| `V_H_dep` | Điểm tốt nhất khi report bắt buộc phụ thuộc `X_i`: `H01` hoặc `H10` |
| Giá trị thông tin tốt nhất | `V_H - V_L` |
| Khoảng report bỏ qua X | `V_H - V_H_dep` |
| Động lực ròng High | `lambda × (V_H - V_L) - cost` |
| `lambda* conditional` | Mức lambda hòa vốn khi giữ nguyên strategy của peer |
| `lambda max` | Mức lớn nhất còn thỏa budget hiện tại |

### Kết luận effort

- `PREFERRED`: High cho utility lớn hơn Low ở branch này.
- `TIED`: hai effort hòa nhau.
- `NOT_PREFERRED`: Judge tự nguyện chọn Low.

### Kết luận report

- `SIGNAL_DEPENDENT_ONLY`: các High action tốt nhất là `H01/H10`.
- `SIGNAL_IGNORED_ONLY`: các High action tốt nhất là `H00/H11`; Judge có thể dùng `X_i` cho prediction nhưng report không đổi theo `X_i`.
- `TIE_DEPENDENT_AND_IGNORED`: cả hai loại cùng tối ưu.

`H01/H10` chỉ có nghĩa report phụ thuộc tín hiệu. Nó chưa chứng minh report đúng ground truth `Y`.

## 4. Vì sao lambda threshold chưa đủ?

Threshold trong card giữ chiến lược hai Judge khác cố định. Khi lambda thật sự thay đổi, họ cũng có thể đổi strategy.

Vì vậy phải đọc thêm **Equilibrium landscape**:

- `Có Low = true`: vẫn tồn tại full Low-Effort equilibrium.
- `Có all-High dùng X = true`: tồn tại full equilibrium mà cả ba report phụ thuộc tín hiệu ở cả hai nhánh Z.
- `Cùng tồn tại = true`: High equilibrium xuất hiện nhưng Low equilibrium chưa biến mất; cơ chế còn vấn đề lựa chọn cân bằng.

## 5. Các kết luận thường gặp

```text
Net High âm
→ reward hiện tại không bù cost ở branch đó

lambda* > lambda max
→ về cục bộ có thể bù bằng reward, nhưng budget hiện tại không cho phép

Best High là H00/H11
→ vấn đề nằm ở report incentive, không chỉ effort cost

Có High và Có Low cùng true
→ High tồn tại nhưng chưa giải quyết equilibrium selection

Mọi điểm chỉ có Low
→ trong miền đã quét, reward tuning chưa tạo được High equilibrium
```

## 6. Giới hạn

V2.2 chỉ phân tích model và dữ liệu/config đã nhập. Dataset synthetic vẫn chỉ kiểm tra pipeline. Kết quả không chứng minh Judge ngoài đời sẽ điều tra, không bao phủ mixed/coalition equilibrium và không tự tạo nguồn tín hiệu riêng đáng tin cậy.
