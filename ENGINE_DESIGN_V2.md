# CEAV-M1 V2 — Thiết kế engine và hợp đồng triển khai

**Áp dụng:** `ceav-m1-v2.0`, spec revision `signal-heterogeneity-r1`

**Design revision:** `engine-design-v2-r1`

**Trạng thái ban đầu:** thiết kế trước implementation; snapshot freeze sẽ giữ trạng thái này.

## 1. Nguồn chuẩn và mục tiêu

[CEAV_M1_V2_SPEC.md](CEAV_M1_V2_SPEC.md) sở hữu phân phối tín hiệu, schema và acceptance V2. [CEAV_M1_SPEC.md](CEAV_M1_SPEC.md) sở hữu timing, strategy, scoring, best response, pure search và decision được V2 kế thừa. Tài liệu này sở hữu module boundaries, records, dispatch, artifacts và integration contract.

V2 phải thêm một seam phân phối tín hiệu sâu nhưng giữ interface toán đang dùng:

```text
raw JSON
  -> validate_config(raw, mechanism)
  -> V1Config | V2Config
  -> enumerate_states(config)
  -> tuple[WeightedState, ...]
  -> candidate/evaluator/best-response/search
```

Caller không tự đọc `a`, `b`, sensitivity hoặc specificity để dựng xác suất. Mọi khác biệt V1/V2 được giữ trong config parser và signal distribution module.

## 2. Module và interface

### 2.1. `ceav_m1.__init__`

Khai báo:

```python
V1_MODEL_VERSION = "ceav-m1-v1.0"
V2_MODEL_VERSION = "ceav-m1-v2.0"
SUPPORTED_MODEL_VERSIONS = (V1_MODEL_VERSION, V2_MODEL_VERSION)
DEFAULT_MODEL_VERSION = V2_MODEL_VERSION
ENGINE_VERSION = "ceav-m1-engine-v2.0"
```

Giữ alias `MODEL_VERSION = V1_MODEL_VERSION` trong giai đoạn tương thích để code/test V1 không âm thầm đổi semantics. Runtime và manifest không được dùng alias này để gán version cho run; phải lấy từ config thực tế.

### 2.2. `ceav_m1.model`

Public seam giữ:

```python
validate_config(raw, mechanism="rbts") -> Config | V2Config
enumerate_states(config) -> tuple[WeightedState, ...]
observe(state, judge, effort) -> LowObservation | HighObservation
signal_diagnostics(config) -> dict
validate_scenario(raw_or_none) -> dict | None
```

`Config` tiếp tục là record V1 để không phá imports hiện có. `V2Config` cung cấp cùng common interface:

```text
pi
costs[3]
f
multiplier
fixed_reward
reward_budget
payout_value
operating_cost
model_version
raw()
```

V2 thêm các field nội bộ:

```text
public_sensitivity
public_specificity
private_sensitivities[3]
private_specificities[3]
```

Không thêm optional `a/b` vào V2Config. Hai schema tách biệt để mixed schema bị lỗi thay vì được diễn giải ngầm.

### 2.3. `ceav_m1.signals`

Module mới sở hữu toàn bộ likelihood:

```python
likelihood(value, truth, sensitivity, specificity) -> Fraction
signal_parameters(config) -> (public_pair, private_pairs)
state_probability(config, y, z, signals) -> Fraction
```

Đây là Adapter seam có hai implementation thực:

- V1 chuyển `a -> (a,a)` và `b -> (b,b)` cho cả ba Judge.
- V2 dùng trực tiếp các pair theo schema mới.

Module không biết profile, scoring, reward hoặc decision.

### 2.4. Các module game

`strategies.py`, `scoring.py`, `best_response.py` và `equilibria.py` tiếp tục nhận config qua common interface và state rows qua `enumerate_states`. Không thêm branch theo model version trong các module này.

`evaluate.py` thêm `signal_diagnostics` vào analyze/search output nhưng giữ toàn bộ metric cũ. Diagnostics không nằm trong Judge utility.

### 2.5. `ceav_m1.output`

Public seam giữ `new_run`, `write_analysis`, `write_search`, `finish_run`. Thay đổi:

- chọn freeze bundle bằng `config.model_version`;
- manifest lấy `model_version` từ config;
- pin đúng spec/design/verification của version;
- khi có scenario, ghi `scenario.json` và `scenario_hash` riêng;
- research context mô tả miền input đúng version;
- source hash bao gồm config V2 và tests V2 như mọi source khác.

V1 run tiếp tục pin freeze V1. V2 run phải pin freeze V2; không dùng snapshot V1 để công bố V2 đã preregister.

## 3. Validation và canonical records

### 3.1. Dispatch

`validate_config` kiểm tra `raw` là object và đọc `model_version` trước. Version thiếu/không hỗ trợ trả `ValidationError("model_version", ...)`. Sau đó gọi parser đúng version.

Mỗi parser dùng exact allowed/missing set riêng. V2 không chấp nhận `a`, `b`, `costs`; V1 không chấp nhận `public_signal`, `judges`.

### 3.2. V2 nested validation

Field path trong lỗi phải cụ thể:

```text
public_signal.sensitivity
judges.A.private_signal.specificity
judges.B.high_effort_cost
```

Key sets:

```text
public_signal = {sensitivity, specificity}
judges = {A, B, C}
judges.i = {private_signal, high_effort_cost}
private_signal = {sensitivity, specificity}
```

Unknown key được báo trước missing key cùng cấp để typo hiện rõ. Mọi rational đi qua cùng parser V1. Budget check dùng common helper sau khi config record được dựng.

### 3.3. Canonical serialization

`V2Config.raw()` luôn xuất:

- top-level theo schema spec;
- Judges theo thứ tự A, B, C;
- mọi Fraction ở dạng tối giản do `str(Fraction)`;
- `operating_cost`, kể cả khi input bỏ qua và dùng mặc định 0.

`semantic_hash` tiếp tục sort keys; canonical record bảo đảm hai JSON khác key order nhưng cùng semantics có cùng hash.

### 3.4. Scenario validation

Scenario là optional object đúng schema spec §10. Tất cả leaf hiện tại là string; `judges` phải đúng A/B/C. `parameter_provenance.status` thuộc:

```text
assumption | pilot_estimate | historical_estimate
```

Scenario không được truyền vào state generator/evaluator. Test phải chứng minh cùng config/profile có và không có scenario tạo cùng mathematical summary.

## 4. State generator và diagnostics

`enumerate_states` giữ thứ tự `product((0,1), repeat=5)` trên `(y,z,x_A,x_B,x_C)`. State ID và CSV order V1 không đổi.

Mỗi mass:

```text
prior(y)
* likelihood(z, y, public_sensitivity, public_specificity)
* product_i likelihood(x_i, y, private_sensitivity_i, private_specificity_i)
```

Assertions sau enumeration:

```text
len(rows) == 32
all(probability > 0)
sum(probability) == 1
```

`signal_diagnostics` trả cấu trúc:

```json
{
  "public_signal": {
    "sensitivity": "Fraction",
    "specificity": "Fraction",
    "false_negative_rate": "Fraction",
    "false_positive_rate": "Fraction",
    "prior_weighted_accuracy": "Fraction"
  },
  "judges": {
    "A": {"private_signal": {"...": "Fraction"}},
    "B": {"private_signal": {"...": "Fraction"}},
    "C": {"private_signal": {"...": "Fraction"}}
  }
}
```

Diagnostics được serialize exact/decimal như các kết quả khác.

## 5. V1 reduction

Fixture reduction dựng một V1 config và V2 config theo spec §9.1. Public checks so:

- `enumerate_states` row-by-row;
- `build_candidate` predictions;
- `analyze` mathematical payload;
- `search_pure` branch candidates/equilibrium IDs.

Khi so analyze, loại đúng các field versioned: `config` và metadata manifest. Không loại metrics, states, predictions, certificates hoặc equilibrium status.

## 6. Sweep

Sweep parser chọn axis set theo config version.

V1 giữ `pi,a,b,c,lambda`. V2 hỗ trợ exact paths trong spec §12.2. Helper duy nhất:

```python
set_axis(raw_config, axis_path, rational_string) -> new_raw_config
```

Helper clone nested dict, không mutate base config. `config_json` của mỗi row chứa full canonical config tại điểm đó. Row cũng chứa axis values dưới chính key path để UI chart không phải suy từ schema.

## 7. CLI/API và scenario

CLI thêm optional `--scenario PATH` cho `analyze`, `equilibria`, `sweep`, `compare`. File được parse/validate trước khi tạo run. `tests` không nhận scenario.

Server request của các operation toán cho phép optional `scenario`. Request allowlist vẫn chặn field khác. `/api/validate` trả:

```text
canonical config
canonical profile
canonical scenario hoặc null
signal diagnostics
comparison fixed reward
```

`/api/status` trả `supported_model_versions`, `default_model_version`, V1/V2 presets và freeze status từng version.

## 8. HTML interface

Form có model selector. Hai draft config được giữ riêng trong memory:

```text
drafts["ceav-m1-v1.0"]
drafts["ceav-m1-v2.0"]
```

Đổi selector render đúng field group mà không chuyển schema ngầm. V2 form gồm public sensitivity/specificity và ba card Judge có private sensitivity/specificity/cost. Reward fields dùng chung.

Scenario nhập bằng JSON textarea tùy chọn. Import wrapper cho phép `config`, `profile`, `mechanism`, `scenario`; export giữ round-trip. Raw config import không có scenario vẫn hợp lệ.

Input validation gọi API và render diagnostics. Kết quả analyze hiển thị signal diagnostics trước decision metrics. History/metadata hiển thị model/scenario hash. Pinned comparison coi `scenario_hash` là một dimension khác biệt.

## 9. Artifacts và certificates

Artifact names V1 giữ nguyên. V2 thêm `scenario.json` khi có. `summary.json` có `signal_diagnostics`.

Certificate identity giữ:

```text
model_version
engine_revision
spec
documents
config_hash
profile_hash khi có
mechanism
scenario_hash khi có
```

Certificate verifier V2 phải đọc config theo version và kiểm tra identity từ manifest. V1 verifier tiếp tục chạy trên V1 artifacts.

## 10. Failure và security behavior

- Invalid V2 input bị từ chối trước `new_run`.
- Output tồn tại bị từ chối như V1.
- Scenario path chỉ do CLI đọc; browser gửi object đã parse, không gửi filesystem path.
- Scenario không mở thêm artifact route hoặc shell argument.
- Job snapshot bất biến và cancel semantics không đổi.
- Model version không được dùng để import module hoặc ghép path tùy ý; dispatch bằng allowlist.

## 11. Trình tự xây

1. Oracle/fixtures và failing seam tests.
2. Version constants, V2 parser, signals adapter, diagnostics.
3. V1 reduction qua analyze/search.
4. Freeze-aware output, scenario và CLI.
5. API/status/presets.
6. Dynamic form, import/export/history/sweep.
7. Full engine tests, mutation probes, browser flows và release evidence.

Mỗi bước chỉ qua khi test seam của bước đó xanh. Full V1 suite phải chạy sau những thay đổi output/API/UI vì đây là vùng dùng chung.

## 12. Trạng thái thiết kế

Revision này là implementation contract đã được thực thi và kiểm chứng local. Bằng chứng nằm tại [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) và `results/v2-acceptance-release-01/`; trạng thái không được suy từ riêng file design.
