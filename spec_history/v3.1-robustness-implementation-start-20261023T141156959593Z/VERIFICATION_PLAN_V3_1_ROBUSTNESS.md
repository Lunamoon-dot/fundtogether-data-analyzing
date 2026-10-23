# CEAV-M1 V3.1 — Verification plan

**Analysis version:** `ceav-m1-v3.1-robustness`  
**Verification revision:** `verification-robustness-grid-r1`

## 1. Evidence principle

Oracle phải độc lập với `ceav_m1/robustness.py`. Expected không được sinh bằng production function. Mọi point tuyên bố equilibrium phải có search đủ 432 branch candidates.

## 2. Fixtures

| ID | Mục đích |
| --- | --- |
| `ROB-F01` | Study nhỏ có nhiều policy và hai uncertainty axes |
| `ROB-F02` | Independent oracle summary cho study nhỏ |
| `ROB-F03` | Invalid schema/path/gate cases |
| `ROB-F04` | Pareto tuples có dominance và tie |
| `ROB-F05` | Predeclared 108-point study |

## 3. Tests

| ID | Requirement |
| --- | --- |
| `ROB-T01` | Schema exact, version/model/provenance và allowlist |
| `ROB-T02` | Deterministic Cartesian expansion và pseudo-axis application |
| `ROB-T03` | Mỗi valid point hoàn tất 432 candidates; no-pure/invalid fail closed |
| `ROB-T04` | Worst-equilibrium metrics và all-reasons gates khớp oracle |
| `ROB-T05` | Policy aggregation và robust classification khớp fixture |
| `ROB-T06` | Exact Pareto frontier xử lý dominance/tie đúng |
| `ROB-T07` | Public-Z và forced-all-High references không bị gọi là equilibrium |
| `ROB-T08` | CLI artifacts, freeze provenance và no-overwrite |
| `ROB-T09` | Server validate/worker parity và UI render contract |
| `ROB-T10` | Registry/discovery đầy đủ; full legacy regression không giảm |

## 4. Independent oracle

`tests/oracle_v3_1.py` được viết trước production module. Nó dùng `tests/oracle_v3.py` để tự tìm branch equilibria và tự tính risk ranges. Phần aggregation/Pareto được viết riêng, không import production robustness code.

## 5. Browser scenario

`ROB-B01`:

1. Mở tab Robustness V3.1.
2. Xác nhận UI ghi model không đổi và range là assumption.
3. Chọn acceptance study nhỏ.
4. Validate grid count.
5. Chạy worker thật tới terminal success.
6. Đối chiếu robust classification, failure reasons, worst false approval/wrong payout và Pareto với artifact.
7. Xác nhận UI ghi `latency_not_modeled` và không gọi synthetic result là production.

## 6. Mutation probes

| ID | Mutation cần bị giết |
| --- | --- |
| `ROB-M01` | Dùng min false approval thay vì max equilibrium |
| `ROB-M02` | Bỏ no-pure failure |
| `ROB-M03` | Policy pass nếu bất kỳ scenario pass |
| `ROB-M04` | Wrong payout bỏ nhân `(1-pi)` trong public-Z reference |
| `ROB-M05` | Pareto cho phép equality toàn bộ thành dominance |
| `ROB-M06` | Cost multiplier chỉ áp dụng Judge A |

## 7. Gates

| Gate | Điều kiện |
| --- | --- |
| `ROB-GATE-0` | Freeze hợp lệ; red tests/oracle preexist |
| `ROB-GATE-1` | ROB-T01–ROB-T02 pass |
| `ROB-GATE-2` | ROB-T03–ROB-T07 pass |
| `ROB-GATE-3` | ROB-T08–ROB-T10 pass |
| `ROB-GATE-4` | ROB-B01 và ROB-M01–ROB-M06 pass |
| `ROB-GATE-5` | Full V1/V2/V2.1/V2.2/V3 regression pass; 108-point study complete |

## 8. Predeclared interpretation

Gates của study chuẩn là research thresholds, không phải quyết định production:

```text
FA <= 1/5
WP <= 3/20
FR <= 1/4
CC <= 4
```

Kết quả `no_robust_policy` không phải test failure. Nó là kết quả khoa học hợp lệ nếu run complete và calculations pass verification.

## 9. Completion record

Chỉ chuyển V3.1 thành `VERIFIED` sau khi ghi evidence paths cho tests, browser, mutations, full study và acceptance audit. Báo cáo cuối phải phân biệt:

- analyzer verified;
- study result;
- production readiness vẫn chưa được chứng minh.
