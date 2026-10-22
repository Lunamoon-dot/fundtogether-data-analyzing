# CEAV-M1 V2 — Kế hoạch kiểm chứng implementation

**Áp dụng:** `ceav-m1-v2.0`, spec `signal-heterogeneity-r1`, design `engine-design-v2-r1`

**Verification revision:** `verification-v2-r1`

**Trạng thái ban đầu:** kế hoạch trước implementation; snapshot freeze sẽ giữ trạng thái này.

## 1. Điều cần chứng minh

V2 chỉ được gọi là hoàn thành khi evidence chứng minh đồng thời:

1. Schema V2 được validate chính xác và không làm đổi semantics V1.
2. State distribution dùng đúng sensitivity/specificity của từng Judge bằng exact arithmetic.
3. Candidate prediction, scoring, best response và equilibrium dùng phân phối V2 thật.
4. V1 reduction cho cùng mathematical payload, không chỉ vài metrics.
5. Artifacts pin đúng model/spec/design/verification/scenario.
6. CLI, API và HTML cùng gọi engine, hỗ trợ import/export/history/sweep V2.
7. Toàn bộ V1 tests vẫn pass.
8. Browser flow V2 được thực thi, không suy từ HTTP 200 hoặc unittest.

## 2. Public seams được test

| Seam | Test quan sát | Không chứng minh một mình |
| --- | --- | --- |
| `validate_config` / `enumerate_states` | Schema, exact distribution, reduction | Payoff/search |
| `analyze` / `search_pure` | Predictions, metrics, BR, equilibria | Artifact provenance/UI |
| CLI `execute` và files | Hash, snapshot, replay, scenario, sweep | Browser behavior |
| Local JSON API | Validation parity, jobs/history/version | Visual/accessibility |
| Browser UI | Form, import/export, run, result/history | Mathematical correctness ngoài fixtures |

Tests gọi public seam. Oracle không import production state generator, evaluator hoặc signal helpers.

## 3. Oracle và fixtures trước production

### V2-F01 — Worked state asymmetry

Config:

```text
pi=1/2
Z sens=4/5, spec=3/5
A sens=9/10, spec=4/5
B sens=3/4, spec=19/20
C sens=13/20, spec=7/10
costs=(1/20,1/10,1/25)
```

Oracle ghi exact mass cho ít nhất tám state bao phủ `Y=0/1`, `Z=0/1` và bit private đảo. Tổng full 32 rows được tính trong checker độc lập chỉ từ raw fixture.

### V2-F02 — V1 reduction G1

V2 dùng public sens/spec `7/10`, mọi private sens/spec `4/5`, mọi cost `1/20`; reward/payout như G1. Expected lấy từ V1 oracle/fixture đã tồn tại và so full mathematical payload.

### V2-F03 — Side isolation

Hai config chỉ khác A sensitivity. Oracle chứng minh rows `Y=0` không đổi; tại `Y=1`, ratio thay đổi theo `X_A`. Fixture tương tự cho specificity tại `Y=0`.

### V2-F04 — Below-half channel

Một sensitivity hoặc specificity bằng `2/5`; state mass vẫn hợp lệ và diagnostics phản ánh false rate `3/5`.

### V2-F05 — Schema failures

Thiếu/dư Judge, typo nested field, numeric không phải string, endpoint 0/1, cost âm, mixed V1/V2 và invalid budget.

### V2-F06 — Scenario neutrality

Cùng config/profile chạy có và không scenario phải cùng mathematical summary/certificate; chỉ manifest/artifact provenance khác.

## 4. V2 test registry

| ID | Seam / fixture | Acceptance |
| --- | --- | --- |
| V2-T01 | Config parser, V2-F05 | Canonical nested schema; đúng field errors; V1 vẫn parse |
| V2-T02 | State generator, V2-F01/F03/F04 | 32 rows, positive, sum 1, exact oracle equality |
| V2-T03 | Diagnostics | FNR/FPR/prior-weighted accuracy exact cho Z và A/B/C |
| V2-T04 | V1 reduction, V2-F02 | States, predictions, analyze payload exact match |
| V2-T05 | Candidate/evaluator heterogeneous | Mỗi Judge có prediction/metric từ kênh đúng; observation boundary giữ |
| V2-T06 | Best response | Đủ A/B/C × Z; candidate payoff thật; peer tables frozen; ties giữ |
| V2-T07 | Pure search | 432 branch candidates; direct oracle/set equality trên fixture chọn |
| V2-T08 | Scenario validation/neutrality | Hash/pin riêng; không đổi mathematical result |
| V2-T09 | Manifest/certificate | Đúng V2 freeze/documents/model/config/profile/scenario identity |
| V2-T10 | CLI analyze/compare | Exact parity với direct engine; equal cap và no-overwrite giữ |
| V2-T11 | V2 sweep | Nested axes, replay rows, invalid rows và base immutability |
| V2-T12 | API status/validate/run | Versions/presets/diagnostics; CLI parity; immutable snapshot |
| V2-T13 | History/import/export contract | V1/V2/scenario round-trip và differences chính xác |
| V2-T14 | Full V1 regression | T01–T32 vẫn discover/run/pass; G1–G4 unchanged mathematically |
| V2-T15 | Registry/completion audit | Mọi V2 ID/B/M có executed evidence; zero/skipped/not_run không pass |

Registry V2 nằm riêng hoặc mở rộng registry hiện tại nhưng không thay nghĩa T01–T32. Runner `all` phải chạy cả V1 và V2 Python tests sau khi V2 được release; runner `v2` chạy V2-T01–V2-T15.

## 5. Independent checks

### 5.1. Distribution oracle

Oracle đọc raw V2 JSON, tự parse Fraction và tự áp bảng bốn trường hợp:

```text
(Y=1,S=1)->sens
(Y=1,S=0)->1-sens
(Y=0,S=0)->spec
(Y=0,S=1)->1-spec
```

Nó không gọi `validate_config`, `likelihood`, `state_probability` hoặc `enumerate_states` production.

### 5.2. Reduction comparator

Comparator chuẩn hóa đúng các field versioned rồi so equality. Nếu comparator bỏ thêm một mathematical field, test phải fail. States so theo `state_id`; certificates so theo `(judge,z)`; branch candidates so theo action tuple và accepted flag.

### 5.3. Search oracle

Giữ direct enumeration độc lập như V1 T17, dùng V2 state table từ oracle. Không dùng boolean accepted của branch solver làm expected. Canceled/partial search không đạt V2-T07.

## 6. Mutation probes

| ID | Mutation phải bị phát hiện | Test chính |
| --- | --- | --- |
| V2-M01 | Dùng sensitivity tại `Y=0` | V2-T02/F01 |
| V2-M02 | Dùng specificity tại `Y=1` | V2-T02/F01 |
| V2-M03 | Dùng signal A cho B/C | V2-T02/T05 |
| V2-M04 | Dựa vào JSON key order để map Judge | V2-T01/T02 |
| V2-M05 | Tự lấp specificity thiếu bằng sensitivity | V2-T01/F05 |
| V2-M06 | Bỏ model version khỏi dispatch/hash | V2-T01/T09 |
| V2-M07 | Signal accuracy dùng `(sens+spec)/2` | V2-T03 với `pi != 1/2` |
| V2-M08 | Scenario làm thay state/result | V2-T08/F06 |
| V2-M09 | V2 path làm hỏng V1 state generator | V2-T04/T14 |

Probe chạy trên copy tạm, lưu patch/hash/log và giữ production bytes nguyên vẹn.

## 7. Browser scenarios

| ID | Flow | Evidence |
| --- | --- | --- |
| V2-B01 | Mở app, chọn V2, chỉnh mọi public/Judge/reward field | Screenshot, DOM/input snapshot, API validation |
| V2-B02 | Đổi V1↔V2 và giữ hai draft; import/export V2 | Export round-trip, schema và values |
| V2-B03 | Analyze heterogeneous preset | Summary/API/CLI exact parity, diagnostics và 32 states |
| V2-B04 | Search V2, mở certificate và clone witness | 432 progress, selected profile, run IDs |
| V2-B05 | Sweep nested axis có invalid row; history/pin khác model/scenario | Table/chart/replay, warning dimensions |
| V2-B06 | Scenario JSON hợp lệ/sai; desktop 1366×768 và mobile 390×844 bằng keyboard | Field error, hash/artifact, screenshots, focus/scroll/contrast |

Các flow V1 B01–B09 vẫn phải pass. V2 browser flow chạy trên server/source hiện tại và lưu browser log/network/screenshot; ảnh đơn lẻ không đủ evidence.

## 8. Gates

| Gate | Điều kiện qua |
| --- | --- |
| V2-GATE-0 | Spec/design/verification freeze thật; oracle/fixtures/test plan preexist và có raw hash |
| V2-GATE-1 | V2-T01–T04; V2-F01–F05; V2-M01–M05/M07/M09 |
| V2-GATE-2 | V2-T05–T06; certificates replay; observation/peer-freeze/ties |
| V2-GATE-3 | V2-T07; direct set equality; benchmark; canceled không tính pass |
| V2-GATE-4 | V2-T08–T11; V2-M06/M08; CLI/artifacts/scenario/sweep |
| V2-GATE-5 | V2-T12–T15, V2-B01–B06, V1 T01–T32 và B01–B09, mọi mutations killed |

## 9. Evidence schema

Release evidence tối thiểu:

```text
results/v2-acceptance-release-01/
  acceptance.json
  report.md
  benchmark.json
  inputs/
  test_results.json
  test_log.txt

results/v2-mutations-release-04/
  manifest.json
  V2-M01/ ... V2-M09/

results/v2-browser-B01-release-02/ ... các release V2-B02–B06 được audit trong acceptance.json
```

`acceptance.json` ghi từng V2-T/B/M ID, trạng thái executed, evidence path/hash và source revision. Không dùng `planned`, `not_run`, skipped hoặc output từ source cũ làm pass.

## 10. Completion audit

Trước tag `v2.0.0`:

1. Đối chiếu từng requirement trong spec V2 với test/evidence trực tiếp.
2. Xác nhận V2 registry không thiếu ID và từng test thật sự được discover.
3. Xác nhận full V1 suite và browser flows chạy trên source cuối.
4. Xác nhận run V2 pin freeze V2 và run V1 pin freeze V1.
5. Xác nhận các dirty files ngoài scope được giữ nguyên hoặc được người dùng chủ động nhập vào release.
6. Xác nhận README/status nói đúng trạng thái và tag trỏ đúng commit.

Chỉ một full-suite pass, một browser screenshot hoặc một reduction fixture không đủ chứng minh toàn V2.

## 11. Evidence đã thực thi

- `results/v2-tests-release-01/`: V2-T01–V2-T15, 15 pass.
- `results/v2-all-release-01/`: V1+V2, 62 unittest methods pass.
- `results/v2-v1-regression-release-02/`: đủ T01–T32, 47 methods pass.
- `results/v2-mutations-release-04/`: V2-M01–V2-M09 đều killed, production bytes unchanged.
- `results/v2-browser-B01-release-02/` đến các run V2-B06 được ghi trong `results/v2-acceptance-release-01/acceptance.json`.
- `results/v2-acceptance-release-01/`: 26/26 checks pass và benchmark direct oracle 46.656 profiles, 5.038.848 deviations.

V2-GATE-0–V2-GATE-5 đạt trên local source được pin trong các manifest. Các run failed trước release vẫn được giữ ngoài curated evidence để truy vết, không đổi thành pass.
