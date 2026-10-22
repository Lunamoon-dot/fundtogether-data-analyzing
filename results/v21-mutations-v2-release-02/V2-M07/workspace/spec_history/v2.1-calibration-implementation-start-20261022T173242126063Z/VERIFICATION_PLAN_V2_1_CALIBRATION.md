# CEAV-M1 V2.1 — Kế hoạch kiểm chứng calibration

**Verification revision:** `calibration-verification-r1`

## 1. Fixtures độc lập

`datasets/synthetic_v2_calibration.csv` có 40 case: 20 `Y=1`, 20 `Y=0`. Expected được đếm tay và lưu trước production code trong `tests/fixtures/calibration_expected.json`:

```text
pi=1/2
Z: sensitivity=4/5, specificity=3/5
A: sensitivity=9/10, specificity=4/5, cost=1/20
B: sensitivity=3/4, specificity=19/20, cost=1/10
C: sensitivity=13/20, specificity=7/10, cost=1/25
```

Expected không được sinh bằng calibrator production.

## 2. Test IDs

- `CAL-T01`: fixture khớp expected counts và exact estimates.
- `CAL-T02`: parser từ chối missing/unknown column, duplicate ID, invalid binary, negative cost, thiếu một lớp Y và degenerate V2 channel.
- `CAL-T03`: semantic hash bất biến theo row order/line endings; raw hash phản ánh bytes.
- `CAL-T04`: generated config giữ economic fields, qua V2 validator và analyzer dùng được.
- `CAL-T05`: CLI tạo immutable artifacts, pin raw dataset/config/calibration freeze và từ chối overwrite.
- `CAL-T06`: API worker parity với direct calibrator; invalid CSV trả field/row cụ thể.
- `CAL-T07`: UI upload sample, render counts/estimates và chỉ nạp config sau hành động rõ ràng.
- `CAL-T08`: full V1+V2 regression đạt trên current source.

## 3. Gates

- **CAL-GATE-0:** spec/design/plan và expected fixture được freeze trước production module.
- **CAL-GATE-1:** CAL-T01–T04 pass.
- **CAL-GATE-2:** CAL-T05–T06 pass.
- **CAL-GATE-3:** CAL-T07 browser acceptance pass trên desktop và mobile.
- **CAL-GATE-4:** CAL-T08 cùng source checks pass.
- **CAL-GATE-5:** acceptance audit đối chiếu manifests, hashes, test discovery và evidence current-source.

Không gọi V2.1 verified nếu chỉ unit tests pass hoặc browser chỉ trả HTTP 200.
