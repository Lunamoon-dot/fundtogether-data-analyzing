# CEAV-M1 V4.1 — Audit-Cost Sensitivity Study

**Ngày:** 2026-10-24.  
**Revision:** `audit-cost-sensitivity-r1`.  
**Trạng thái:** `SPECIFIED`; fixed-pair economic sensitivity, chưa phải full frontier engine.  
**Model:** `ceav-m1-v4.1-audit-cost-sensitivity`.  

## 1. Mục tiêu và giới hạn

Nghiên cứu hẹp liệu audit cost dương có làm trade-off giảm audit exposure của Hybrid tại V3-HET trở nên có giá trị kinh tế hay không. Nghiên cứu giữ nguyên reward rule, signal model, equilibrium records và quality gates của V4.1 screening; chỉ thay `kappa`, chi phí cho mỗi audit.

Đây là sensitivity study cho một cặp policy đã pin, không phải re-optimization toàn bộ policy frontier và không phải bằng chứng Hybrid strict-dominates Audit-only.

## 2. Cặp policy đã pin

Từ artifact screening V4.1 đã commit:

```text
Audit-only A: lambda=0,   mu=3/2, q=5/8
Hybrid H:     lambda=1/4, mu=5/4, q=1/2
Fixture:      V3-HET
```

Cả hai policy phải robust tại `kappa=0`. Các quality metrics được giữ nguyên khi chỉ thay `kappa`; chỉ cash review cost thay đổi.

## 3. Công thức

Gọi `C_A(0)` và `C_H(0)` là worst-equilibrium target-population cash cost trong screening baseline. Với audit cost `kappa`:

```text
C_A(kappa) = C_A(0) + (5/8) * kappa
C_H(kappa) = C_H(0) + (1/2) * kappa
```

Ngưỡng crossover được tính exact:

```text
kappa* = (C_H(0) - C_A(0)) / ((5/8) - (1/2))
       = 8 * (C_H(0) - C_A(0))
```

Hybrid chỉ rẻ hơn cặp Audit-only sau `kappa > kappa*`. Tie tại `kappa=kappa*` không được gọi là advantage.

Cash gate vẫn là `C_target_population <= 4`; quality gates giữ nguyên `FA <= 1/5`, `FR <= 1/4`, `wrong_payout_value <= 3/20`. Không đổi gate sau khi thấy output.

## 4. Điểm sensitivity

Phải báo cáo các điểm exact:

```text
K = {0, 1/4, kappa*, 3/8, 1/2, 1, kappa_H_gate}
```

Trong đó `kappa_H_gate` là nghiệm của `C_H(kappa)=4`. Mỗi điểm lưu cash cost của A/H, policy nào rẻ hơn, quality metrics, cash-gate status và interval status.

## 5. Acceptance

Artifact đạt khi:

1. Independent derivation khớp `C_A(0)`, `C_H(0)`, `kappa*` và gate bounds từ screening evidence.
2. Có miền exact trong đó Hybrid rẻ hơn cặp A và vẫn qua cash/quality gates, hoặc chứng minh không có miền như vậy.
3. Nếu có miền, kết luận phải gọi đây là fixed-pair economic trade-off; không gọi là global frontier advantage.
4. Không re-run hay thay reward rule để tạo kết quả pass.
5. Source hashes và baseline screening artifact được pin; không ghi đè artifact đã tồn tại.

## 6. Giới hạn diễn giải

Nghiên cứu không tối ưu lại `mu`, `q`, `lambda`, không định giá effort cost ngoài reward/cash model, không mô hình hóa human labor trực tiếp và không mở rộng sang engine/UI. Nếu Hybrid chỉ thắng ở cash sau khi chấp nhận quality trade-off, đó là tín hiệu để cân nhắc tiếp chứ chưa phải lý do triển khai production.
