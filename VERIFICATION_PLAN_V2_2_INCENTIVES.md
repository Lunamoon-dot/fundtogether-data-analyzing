# CEAV-M1 V2.2 — Kế hoạch kiểm chứng incentive diagnostics

**Verification revision:** `incentive-diagnostics-verification-r1`

## 1. Fixtures

### INC-F01 — Hand-computed decomposition

Fixture có `V_L=1`, bốn High action scores `6/5, 11/10, 9/10, 4/5`, `c=1/20`, `lambda=3/4`, `f=1/10`, `B=6`.

Expected độc lập:

```text
V_H=6/5
V_H_dep=11/10
best gain=1/5
dependent gain=1/10
report gap=1/10
best net=1/10
dependent net=1/40
best lambda*=1/4
dependent lambda*=1/2
lambda_max=19/20
```

Fixture cũng có zero-gain positive-cost case để yêu cầu `UNATTAINABLE_BY_LAMBDA`.

### INC-F02 — Synthetic V2.1 config

Dùng generated values đã pin trong calibration fixture, all-H `H01` candidate. Expected mới không được sinh bằng module diagnostics đang test. Kiểm tra identities toán từ `analyze` và preserved negative results.

### INC-F03 — G1 coexistence

Config `configs/v2/symmetric_g1.json` phải cho landscape có cả full all-low và full all-high signal-dependent equilibrium. Đây là existence/coexistence, không phải selection.

## 2. Test IDs

- `INC-T01`: hand-computed score decomposition, gains, report gap và exact arithmetic.
- `INC-T02`: threshold edge cases, budget status và hierarchical diagnoses.
- `INC-T03`: synthetic candidate đủ sáu `Judge × Z`, peer-fixed identities và signal-dependent/report-ignored distinction.
- `INC-T04`: landscape classifier giữ exact retained IDs/counts; G1 coexistence và heterogeneous negative result.
- `INC-T05`: global sweep gọi exhaustive search tại từng valid point; invalid budget được giữ; config base không mutate.
- `INC-T06`: CLI artifacts, V2.2 freeze pin, JSON/CSV parity và no-overwrite.
- `INC-T07`: API validation/worker/history/direct parity.
- `INC-T08`: browser view render sáu branch diagnostics, conditional warning và landscape counts trên desktop/mobile.

## 3. Independent checks

- INC-F01 expected được lưu trước production module và tính trực tiếp từ hai observation rows.
- Tại integration seam, kiểm tra identities `net=lambda*gain-cost` và `lambda*=cost/gain`; không dùng cùng helper để sinh expected.
- Landscape expected lấy từ retained set của exhaustive solver và được phân loại lại bằng test-only classifier đơn giản dựa trên action prefixes/maps.
- Mỗi valid sweep point phải ghi `branch_candidate_count=432`, `enumeration_completed=true` và retained IDs. Chỉ candidate analyze không đạt INC-T05.

## 4. Browser scenario

`INC-B01`:

1. mở view Chẩn đoán động lực;
2. xác nhận default V2/all-H và lambda sweep values;
3. chạy một base point hoặc grid nhỏ qua worker thật;
4. xác nhận sáu rows/cards và exact/decimal;
5. xác nhận text phân biệt conditional threshold với global equilibrium;
6. xác nhận landscape công bố 432 branch candidates/point;
7. kiểm tra desktop 1366×768 và mobile 390×844, keyboard và không JavaScript error.

## 5. Gates

- **INC-GATE-0:** spec/design/plan/fixture freeze trước production module.
- **INC-GATE-1:** INC-T01–T03 pass.
- **INC-GATE-2:** INC-T04–T05 pass với exhaustive evidence.
- **INC-GATE-3:** INC-T06–T07 pass; artifacts immutable và CLI/API parity.
- **INC-GATE-4:** INC-B01 và INC-T08 pass trên current source.
- **INC-GATE-5:** V1, V2 và V2.1 regression current-source pass; acceptance audit không có skipped/not_run.

Targeted unit/integration pass chỉ cho phép ghi `IMPLEMENTED` và phạm vi test tương ứng. Chỉ sau INC-GATE-0–5 mới ghi `VERIFIED` cho toàn V2.2.
