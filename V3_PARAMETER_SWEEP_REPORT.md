# CEAV-M1 V3 — Báo cáo quét động lực anchor

**Ngày:** 23/10/2026  
**Model:** `ceav-m1-v3.0`  
**Phạm vi:** synthetic heterogeneous signals, pure strategies, exact arithmetic

## 1. Câu hỏi

Tìm một phân bổ reward trong budget `B=6` làm cân bằng thực tế dùng thêm tín hiệu riêng và cải thiện decision accuracy, thay vì chỉ làm candidate all-High đẹp hơn.

Mỗi điểm hợp lệ được kiểm đủ `432` branch candidates. Accuracy của candidate cố định và accuracy của equilibrium được giữ tách biệt.

## 2. Sửa contract sweep trước khi nghiên cứu

Implementation cũ của operation `sweep` chỉ gọi `analyze` trên candidate cố định. Điều này không đáp ứng CEAV-M1 V3 spec §15, vì một điểm có candidate accuracy cao vẫn có thể rơi về Low Effort equilibrium.

Sau sửa đổi, mỗi điểm V3 hợp lệ chạy:

```text
candidate analyze
    +
432-candidate pure search
    +
equilibrium landscape classification
    +
exact metrics của mọi full pure equilibrium
```

Điểm invalid budget được giữ lại và không chạy search. Sweep V1/V2 vẫn giữ contract candidate-only cũ.

## 3. Kết quả biên budget

Giữ `f=1/10`, `B=6`, anchor sensitivity/specificity đều bằng `9/10`, đặt `q=1` và quét các phân bổ thỏa:

```text
3f + 6*lambda_peer + 3*anchor_weight = 6
```

| `lambda_peer` | `anchor_weight` | Full pure equilibria | Equilibrium chính |
| ---: | ---: | ---: | --- |
| `0` | `19/10` | 1 | A/B High dùng X; C Low dùng Z |
| `1/10` | `17/10` | 1 | A/B High dùng X; C Low dùng Z |
| `1/4` | `7/5` | 0 | Không có pure equilibrium trong reduced space |
| `1/2` | `9/10` | 0 | Không có pure equilibrium trong reduced space |
| `3/4` | `2/5` | 1 | Z=0 all-Low; Z=1 all-High dùng X |
| `9/10` | `1/10` | 1 | All-Low, decision theo Z |

Kết quả cho thấy tăng peer weight không đơn điệu cải thiện equilibrium. Ở instance này, anchor-dominant allocation tạo kết quả tốt nhất trong các điểm đã quét.

## 4. Ngưỡng audit exact

Với `lambda_peer=0`, `anchor_weight=19/10`, điều kiện để A và B tự nguyện dùng High trên mọi nhánh là:

```text
q > 25/57 ≈ 43,86%
```

Tại đúng `q=25/57`, tie tạo ra `8` pure equilibria cùng tồn tại. `q=11/25=44%` đã cho một equilibrium tốt duy nhất trong search, nhưng khoảng đệm quá nhỏ. Preset nghiên cứu dùng `q=1/2`.

## 5. Preset experimental được chọn

File: `configs/v3/anchor_dominant_q50.json`

```text
audit_probability = 1/2
lambda_peer       = 0
anchor_weight     = 19/10
reward cap        = 6
```

Exhaustive search giữ đúng một full pure equilibrium:

```text
Z=0: A=H01, B=H01, C=L0
Z=1: A=H01, B=H01, C=L1
```

| Metric tại equilibrium | Baseline V3 equilibrium | Experimental q=50% |
| --- | ---: | ---: |
| Accuracy | `7/10 = 70%` | `1813/2000 = 90,65%` |
| False approval | `2/5 = 40%` | `51/500 = 10,2%` |
| False rejection | `1/5 = 20%` | `17/200 = 8,5%` |
| Wrong payout value | `1/5 = 20%` | `51/1000 = 5,1%` |
| Expected Judge reward | — | `2409/1000 = 2,409` |
| Expected effort cost | `0` | `3/20 = 0,15` |
| Max regret | `0` | `0` |

Accuracy `90,65%` cao hơn candidate all-High `89,55%` vì tín hiệu riêng của Judge C yếu trong instance này. Cân bằng tối ưu động lực cho A/B dùng tín hiệu riêng và để C dùng tín hiệu chung.

Mức cải thiện đã kiểm bằng exact arithmetic:

- so với equilibrium baseline: `413/2000 = 20,65` điểm phần trăm;
- so với candidate all-High bị ép: `11/1000 = 1,10` điểm phần trăm;
- false approval giảm từ `40%` xuống `10,2%`, tức `-29,8` điểm phần trăm;
- false rejection giảm từ `20%` xuống `8,5%`, tức `-11,5` điểm phần trăm.

## 6. Robustness closeout r2

Các điểm dưới đây thay từng nhóm tham số một lần và đều chạy exhaustive search. Đây không phải full Cartesian robustness.

| Thay đổi so với preset q=50% | Pure equilibrium | Equilibrium accuracy | Kết luận |
| --- | ---: | ---: | --- |
| `q=2/5=40%` | 1 | `7/10 = 70%` | dưới ngưỡng, cải thiện mất |
| `q=11/25=44%` | 1 | `1813/2000 = 90,65%` | vừa trên ngưỡng exact |
| `q=3/5=60%` | 1 | `1813/2000 = 90,65%` | giữ kết quả |
| anchor quality `80%/80%` | 1 | `7/10 = 70%` | anchor chưa đủ tốt |
| anchor quality `95%/95%` | 1 | `1813/2000 = 90,65%` | giữ kết quả |
| Judge costs `×4/5` | 1 | `1813/2000 = 90,65%` | giữ kết quả |
| Judge costs `×6/5` | 1 | `7/10 = 70%` | effort đắt làm mất cải thiện |
| prior `3/10` | 1 | `22167/25000 = 88,668%` | profile cân bằng đổi theo nhánh Z |
| prior `7/10` | 1 | `42379/50000 = 84,758%` | profile cân bằng đổi theo nhánh Z |
| `lambda_peer=1/100`, `mu=47/25` | 1 | `1813/2000 = 90,65%` | hybrid dương rất nhỏ vẫn hoạt động |
| `lambda_peer=1/20`, `mu=9/5` | 0 | — | không có pure equilibrium |
| `lambda_peer=1/10`, `mu=17/10` | 0 | — | không có pure equilibrium |

Điểm `lambda_peer=1/100` cho thấy kết quả không chỉ tồn tại đúng tại biên `lambda_peer=0`. Tuy vậy miền peer weight ổn định hẹp trong grid đã tính; tăng lên `1/20` đã làm pure equilibrium biến mất.

## 7. Chi phí audit

V3 r2 thêm:

```text
expected_audit_cost = q * cost_per_audit
cash_review_cost = expected Judge reward + operating_cost + expected_audit_cost
```

Chi phí này không đi vào utility của Judge nên không thay equilibrium. Với `q=1/2`, nếu `cost_per_audit` lần lượt là `1/10`, `1/5`, `1/2`, expected audit cost là `1/20`, `1/10`, `1/4`. Preset vẫn để `0` vì chưa có dữ liệu chi phí thật; người dùng phải nhập assumption hoặc estimate có provenance.

## 8. Giới hạn

- Đây là synthetic instance; chưa phải bằng chứng hiệu năng ngoài đời.
- Preset dùng `lambda_peer=0`, tức là anchor-only ở biên của mechanism V3, không còn peer score trong payoff.
- Audit xảy ra với xác suất 50%; công thức chi phí đã có nhưng giá trị ngoài đời vẫn chưa biết.
- Chất lượng anchor `90%/90%` đang là assumption, chưa được ước lượng từ dataset thật.
- Kết quả chỉ chứng nhận pure equilibrium trong reduced strategy space; không chứng nhận mixed, coalition, Sybil resistance hoặc equilibrium selection ngoài model.

## 9. Evidence

- Frontier summaries: `results/v3-frontier-search/frontier_summary.json`
- Audit grid: `results/v3-frontier-search/q_grid_summary.json`
- Exact threshold derivation: `results/v3-frontier-search/q_threshold_derivation.json`
- Current-source exhaustive search: `results/v3-anchor-dominant-q50-search/`
- Current-source equilibrium analysis: `results/v3-anchor-dominant-q50-analysis/`
- Closeout robustness and exact equilibrium metrics: `results/v3-closeout-study-r2/`
- Current-source all-suite: `results/v3-all-tests-closeout-r2-final/` (`90/90`)
- Browser V3: `results/v3-browser-closeout-r2-02/` (`34/34`)
- Mutation probes: `results/v3-mutations-closeout-r2/` (`10/10` killed)
- Acceptance audit: `results/v3-acceptance-closeout-r2/` (`7/7`)

