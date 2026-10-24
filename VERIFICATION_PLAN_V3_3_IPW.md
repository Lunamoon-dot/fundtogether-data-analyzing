# CEAV-M1 V3.3 — Verification plan cho IPW audit reward

**Analysis version:** `ceav-m1-v3.3-ipw`  
**Trạng thái:** `VERIFIED` trên source pin local sau khi tất cả gate bắt buộc pass; phạm vi vẫn chỉ là model synthetic/assumption của workspace.

## 1. Preconditions

Trước implementation phải tạo freeze event mới chứa raw bytes/hash của:

- `CEAV_M1_V3_3_IPW_SPEC.md`;
- `ENGINE_DESIGN_V3_3_IPW.md`;
- file này;
- independent oracle;
- red fixtures.

Freeze V3.2 không bao phủ V3.3. Không ghi lùi implementation-start vào lịch sử.

## 2. Fixtures

| ID | Mục đích |
| --- | --- |
| `IPW-F01` | Một state/observation nhỏ có `q0 != q1`, kiểm tra exact cancellation |
| `IPW-F02` | Budget cap với `q_min` và case invalid `q=0` |
| `IPW-F03` | Causal decomposition có peer, anchor và effort cùng thay đổi |
| `IPW-F04` | Study gồm symmetric, report-1 và report-0 IPW policies |
| `IPW-F05` | 54-point predeclared study, giữ invalid/no-pure và worst equilibrium |
| `IPW-F06` | Reference comparison với V3.2 cùng budget và cùng uncertainty point |

Expected oracle phải được suy ra độc lập trước khi production implementation tồn tại.

## 3. Tests

| ID | Requirement |
| --- | --- |
| `IPW-T01` | Schema bắt buộc model V3.3 và `audit_reward_mode=ipw` |
| `IPW-T02` | `q0,q1` phải dương; scalar V3 input và field lạ bị reject |
| `IPW-T03` | IPW anchor expectation đúng `mu * P(T=r \| observation)` |
| `IPW-T04` | Expected audit cost vẫn là `kappa * E[q_r]` |
| `IPW-T05` | Realized reward và worst-case cap đúng với `mu/q_min` |
| `IPW-T06` | Second moment/variance exact, không coi T chung là ba draw độc lập |
| `IPW-T07` | Best response dùng expected IPW anchor và frozen peer tables |
| `IPW-T08` | Utility decomposition tái dựng exact với reconstruction error bằng 0 |
| `IPW-T09` | Expansion deterministic và đủ 54 points |
| `IPW-T10` | Worst-equilibrium gates giữ mọi reason và không pass theo best equilibrium |
| `IPW-T11` | Baseline comparison giữ cùng budget, input và Judge count |
| `IPW-T12` | CLI/API artifacts pin model, spec, source và không overwrite |
| `IPW-T13` | V1/V2/V2.1/V2.2/V3/V3.1/V3.2 regression không giảm |

## 4. Independent oracle

`tests/oracle_v3_3.py` không được import:

- `ceav_m1.ipw`;
- production `evaluate`;
- production `best_response`;
- production state enumerator.

Oracle phải tự tính likelihood, audit expectation, IPW cancellation, budget cap, moments và một deviation witness bằng finite sums.

## 5. Browser/API scenario

Nếu V3.3 được expose qua local UI, `IPW-B01` phải:

1. mở đúng operation/model V3.3;
2. hiển thị `q0`, `q1`, `q_min`, IPW mode và reward cap;
3. validate study 54 points;
4. chạy worker thật tới terminal success;
5. đối chiếu report bias, false approval, wrong payout, variance và failure witness với artifact;
6. xác nhận UI không gọi synthetic/assumption là dữ liệu thực;
7. xác nhận UI giữ invalid budget/no-pure results.

HTTP 200 hoặc status badge không đủ làm browser pass.

## 6. Mutation probes

| ID | Mutation phải bị giết |
| --- | --- |
| `IPW-M01` | Bỏ mẫu số `q_r` khỏi anchor reward |
| `IPW-M02` | Cho phép `q0=0` hoặc `q1=0` |
| `IPW-M03` | Dùng cap V3.2 `3f+6lambda+3mu` cho IPW |
| `IPW-M04` | Dùng `q_r*kappa` sai trong expected audit cost |
| `IPW-M05` | Tính T độc lập cho từng Judge khi tính variance |
| `IPW-M06` | Cho deviation nhìn thấy T hoặc audit |
| `IPW-M07` | Thay candidate bằng best response của focal trong candidate utility |
| `IPW-M08` | Gắn failure type bằng action change, bỏ decomposition |
| `IPW-M09` | Cho policy pass nếu chỉ một uncertainty point pass |
| `IPW-M10` | Tăng budget riêng cho IPW hoặc lọc invalid budget khỏi report |

## 7. Gates

| Gate | Điều kiện |
| --- | --- |
| `IPW-GATE-0` | Freeze, red fixtures và oracle tồn tại trước implementation |
| `IPW-GATE-1` | IPW-T01–T06 pass |
| `IPW-GATE-2` | IPW-T07–T10 pass |
| `IPW-GATE-3` | IPW-T11–T13 pass |
| `IPW-GATE-4` | IPW-B01 và IPW-M01–M10 pass nếu UI/API đã expose |
| `IPW-GATE-5` | 54-point study complete, mọi point có 432-candidate evidence và full regression pass |

Study có thể cho `no_robust_policy` mà vẫn pass verification; đó là kết quả về policy, không phải lỗi của analyzer.

## 8. Interpretation

Khi V3.3 pass verification, chỉ được kết luận:

- implementation tính đúng IPW payoff trong declared model;
- expected anchor reward không phụ thuộc `q_r` theo oracle;
- trade-off budget, variance, effort và report bias được đo trên declared assumption grid.

Không được kết luận Judge ngoài đời sẽ High effort, report truthful, chống collusion/Sybil hoặc sẵn sàng triển khai production.

## 9. Completion record

Completion report phải phân biệt:

- `SPECIFIED`: ba tài liệu và freeze;
- `IMPLEMENTED`: code, CLI/API/UI nếu có;
- `VERIFIED`: gates và evidence;
- `STUDY_RESULT`: policy comparison trên synthetic/assumption inputs.

V3.3 đã `IMPLEMENTED` và `VERIFIED` trong phạm vi các gate ở tài liệu này. Closeout giữ nguyên negative result `0/18` cho cả ba policy; verification không phải kết luận Judge ngoài đời sẽ truthful/high-effort hoặc hệ thống production chống collusion/Sybil.
