# CEAV-M1 V3 — Kế hoạch kiểm chứng hybrid anchor

**Áp dụng:** `ceav-m1-v3.0`, spec `verification-anchor-r1`, design `engine-design-v3-anchor-r1`

**Verification revision:** `verification-v3-anchor-r1`

**Trạng thái:** kế hoạch trước implementation; snapshot freeze phải giữ revision này.

## 1. Điều cần chứng minh

V3 chỉ được gọi là hoàn thành khi evidence chứng minh:

1. Schema/version/mechanism V3 được dispatch chính xác và V1/V2 không đổi.
2. Joint distribution 7 bit đúng exact và không lộ `A,T` cho strategy.
3. Hybrid accounting dùng `T`, chỉ trả anchor khi audit, và giữ worst-case budget.
4. Best response tối ưu đồng thời effort/report dưới hai reward components và giữ peer tables.
5. Exhaustive pure search kiểm tra đủ 432 branch candidates.
6. `q=0` hoặc `anchor_weight=0` quy hồi exact về V2 RBTS.
7. CLI/API/UI dùng cùng engine, pin đúng V3 freeze và artifacts.
8. Toàn bộ V1/V2/V2.1/V2.2 regression vẫn pass.

## 2. Independent assets trước production

### V3-F01 — Heterogeneous anchor

Config kế thừa V2 heterogeneous và dùng:

```text
q=1/5
sens_T=9/10
spec_T=9/10
f=1/10
lambda_peer=1/2
anchor_weight=4/5
B=6
```

`tests/oracle_v3.py` tự parse raw JSON, enumerate 128 state, dựng peer predictions, evaluate profile và direct branch best responses mà không import production model/signals/scoring/evaluate/best_response.

`tests/fixtures/v3_anchor_expected.json` pin state masses chọn lọc, totals candidate và retained branch equilibrium IDs từ oracle độc lập.

### V3-F02 — V2 reduction

Cùng inherited signals/profile, V3 đặt `anchor_weight=0`, `lambda_peer=lambda` V2. Expected states sau marginalize `A,T`, predictions, decision metrics, peer rewards, utility và equilibrium IDs phải bằng V2.

### V3-F03 — Perfect anchor

`q=1`, `sens_T=spec_T=1`; chỉ positive support có `T=Y`. Test không được giả 128 rows đều positive.

### V3-F04 — Pure anchor degeneration

`lambda_peer=0`, anchor active. Prediction arbitrary nhưng report/effort vẫn theo anchor payoff.

### V3-F05 — Invalid schemas

Missing/unknown anchor field, V2 `lambda` trộn với V3 `lambda_peer`, quality <=1/2 hoặc >1, q ngoài [0,1], reward âm, budget thiếu và mechanism mismatch.

## 3. Test registry

| ID | Seam / fixture | Acceptance |
| --- | --- | --- |
| `V3-T01` | Parser V3, F05 | Canonical schema, exact paths, version/mechanism mismatch rejected |
| `V3-T02` | Distribution, F01/F03 | 128 potential rows, exact oracle equality, support size, sum 1 |
| `V3-T03` | Observation boundary | L chỉ Z; H chỉ Z/X; A/T/Y không đi vào strategy |
| `V3-T04` | Candidate accounting, F01 | Peer/anchor/reward/cost/utility exact oracle equality |
| `V3-T05` | Best response, F01/F04 | Đủ 3×2, combined report optimum, prediction degeneration, peer freeze |
| `V3-T06` | V2 reduction, F02 | Marginal states, predictions, metrics, BR và equilibrium IDs exact equality |
| `V3-T07` | Pure search | 432 tested; direct oracle retained-set equality; ties giữ |
| `V3-T08` | Budget/accounting | Worst-case cap không nhân q; expected spend đúng; invalid budget giữ |
| `V3-T09` | Manifest/artifacts/CLI | V3 freeze, identity, no-overwrite, direct/CLI parity |
| `V3-T10` | API/server | Status/preset/validate/worker/history parity và request allowlist |
| `V3-T11` | Sweep | Nested V3 axes, replay valid, preserve invalid, base immutable |
| `V3-T12` | Registry/completion | IDs discovered/executed; zero/skipped/not_run không pass |

## 4. Oracle rules

Oracle không import production helpers. Nó phải:

- dùng `Fraction` trực tiếp;
- tự định nghĩa likelihood bốn trường hợp;
- tự enumerate canonical 7-bit product;
- tự dựng report/prediction tables;
- tự tính RBTS quadratic/shadow và anchor match;
- tự enumerate `L0,L1,H00,H01,H10,H11` cho deviation;
- tự enumerate 216 profiles mỗi branch cho retained set fixture.

Fixture expected được tạo trước production support và pin trong freeze. Sau freeze không đổi expected để làm test xanh nếu chưa có derivation/review mới được version hóa.

## 5. Reduction comparator

V3 states được marginalize theo key `(y,z,x_A,x_B,x_C)`. Comparator so 32 masses với V2. Các field V3-only được loại đúng allowlist:

```text
audit, verification, anchor score/reward, V3 model/mechanism metadata
```

Không được loại decision, prediction, peer score/reward, effort cost, utility, certificates hoặc equilibrium IDs.

## 6. Mutation probes

| ID | Mutation phải bị phát hiện | Test chính |
| --- | --- | --- |
| `V3-M01` | Strategy quan sát T trước report | V3-T03 |
| `V3-M02` | Anchor score dùng Y thay T | V3-T04/F01 |
| `V3-M03` | Trả anchor khi A=0 | V3-T04 |
| `V3-M04` | Budget cap nhân anchor_weight với q | V3-T08 |
| `V3-M05` | Audit probability phụ thuộc report/Y | V3-T02/T04 |
| `V3-M06` | Bỏ effort cost ở hybrid | V3-T04/T05 |
| `V3-M07` | Tối ưu report chỉ theo RBTS, bỏ anchor | V3-T05 |
| `V3-M08` | Rebuild peer predictions khi deviation | V3-T05 |
| `V3-M09` | V3 làm sai V2 reduction | V3-T06 |
| `V3-M10` | UI tự tính reward khác artifact | V3-B01 |

Mutation chạy trong temporary copy, lưu patch/hash/log và không sửa production/golden.

## 7. Browser scenario

### V3-B01 — Full hybrid flow

Trên source cuối:

1. Chọn V3 và thấy đúng field groups/reward fields.
2. Validate preset; diagnostics hiện anchor quality/audit probability.
3. Analyze all-High; UI/API/CLI numeric artifacts khớp.
4. Accounting hiển thị peer reward và anchor reward tách riêng.
5. State table có 128 potential rows và không lộ T trong input strategy.
6. Search hoàn tất 432 branch candidates; mở certificate.
7. Sweep ít nhất hai `anchor_weight` point, gồm một invalid budget row.
8. Import/export V3 exact rational round-trip.
9. Desktop 1366×768 và mobile 390×844, keyboard focus và không page-wide overflow.
10. Không JavaScript error; history pin đúng V3 freeze/model/mechanism.

Evidence: browser log, network, screenshots, exported input, run IDs, API artifacts, CLI parity hashes.

## 8. Gates

| Gate | Điều kiện qua |
| --- | --- |
| `V3-GATE-0` | Spec/design/plan/oracle/config/expected fixture frozen before production V3 |
| `V3-GATE-1` | V3-T01–T03, F01/F03/F05, M01/M05 |
| `V3-GATE-2` | V3-T04–T05, F04, M02/M03/M06/M07/M08 |
| `V3-GATE-3` | V3-T06–T07, F02, direct retained-set equality, M09 |
| `V3-GATE-4` | V3-T08–T11, artifacts/CLI/API/sweep, M04 |
| `V3-GATE-5` | V3-T12, V3-B01, M10 và full V1/V2/V2.1/V2.2 regression |

## 9. Evidence layout

```text
results/v3-tests-release-01/
results/v3-browser-V3-B01-release-01/
results/v3-mutations-release-01/
results/v3-acceptance-release-01/
```

Acceptance record phải map từng requirement/T/B/M sang evidence path/hash. Chỉ `executed+passed` tính pass.

## 10. Completion audit

Trước khi đổi trạng thái V3 thành VERIFIED:

1. Đối chiếu từng mục spec §19 và test registry.
2. Xác nhận current source khớp source hash của mọi evidence dùng.
3. Xác nhận freeze V3 raw bytes/hash và preexisting assets.
4. Xác nhận exhaustive search completed, không canceled/partial.
5. Xác nhận full legacy test runner và browser regression trên current source.
6. Xác nhận README/status không gọi synthetic anchor là dữ liệu thực hoặc production oracle.

Revision này chưa chứng minh implementation tồn tại.
