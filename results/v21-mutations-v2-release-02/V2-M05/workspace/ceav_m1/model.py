"""Validated exact inputs and the information available to each player."""

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
import re

from . import MODEL_VERSION, SUPPORTED_MODEL_VERSIONS, V1_MODEL_VERSION, V2_MODEL_VERSION
from .signals import diagnostics as signal_diagnostics
from .signals import state_probability

F = Fraction
JUDGES = ("A", "B", "C")
MECHANISMS = ("fixed", "rbts")
NUMERIC_FIELDS = ("pi", "a", "b", "f", "lambda", "fixed_reward", "reward_budget", "payout_value", "operating_cost")
COMMON_NUMERIC_FIELDS = ("pi", "f", "lambda", "fixed_reward", "reward_budget", "payout_value", "operating_cost")


class ValidationError(ValueError):
    def __init__(self, field, message):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

    def as_dict(self):
        return {"field": self.field, "message": self.message}


def rational(value, field):
    if not isinstance(value, str) or not re.fullmatch(r"[+-]?(?:\d+/\d+|\d+(?:\.\d*)?|\.\d+)", value.strip()):
        raise ValidationError(field, "Cần chuỗi thập phân hoặc tử số/mẫu số.")
    try:
        return F(value.strip())
    except (ValueError, ZeroDivisionError):
        raise ValidationError(field, "Số hữu tỉ không hợp lệ; mẫu số phải khác 0.") from None


@dataclass(frozen=True, slots=True)
class Config:
    pi: F
    a: F
    b: F
    costs: tuple[F, F, F]
    f: F
    multiplier: F
    fixed_reward: F
    reward_budget: F
    payout_value: F
    operating_cost: F = F(0)
    model_version: str = MODEL_VERSION

    def raw(self):
        return {"model_version": self.model_version, "pi": str(self.pi), "a": str(self.a), "b": str(self.b),
                "costs": list(map(str, self.costs)), "f": str(self.f), "lambda": str(self.multiplier),
                "fixed_reward": str(self.fixed_reward), "reward_budget": str(self.reward_budget),
                "payout_value": str(self.payout_value), "operating_cost": str(self.operating_cost)}


@dataclass(frozen=True, slots=True)
class V2Config:
    pi: F
    public_sensitivity: F
    public_specificity: F
    private_sensitivities: tuple[F, F, F]
    private_specificities: tuple[F, F, F]
    costs: tuple[F, F, F]
    f: F
    multiplier: F
    fixed_reward: F
    reward_budget: F
    payout_value: F
    operating_cost: F = F(0)
    model_version: str = V2_MODEL_VERSION

    def raw(self):
        judges = {}
        for index, judge in enumerate(JUDGES):
            judges[judge] = {
                "private_signal": {
                    "sensitivity": str(self.private_sensitivities[index]),
                    "specificity": str(self.private_specificities[index]),
                },
                "high_effort_cost": str(self.costs[index]),
            }
        return {
            "model_version": self.model_version,
            "pi": str(self.pi),
            "public_signal": {"sensitivity": str(self.public_sensitivity), "specificity": str(self.public_specificity)},
            "judges": judges,
            "f": str(self.f),
            "lambda": str(self.multiplier),
            "fixed_reward": str(self.fixed_reward),
            "reward_budget": str(self.reward_budget),
            "payout_value": str(self.payout_value),
            "operating_cost": str(self.operating_cost),
        }


def _validate_budget(config, mechanism):
    cap = 3 * config.fixed_reward if mechanism == "fixed" else 3 * config.f + 6 * config.multiplier
    if cap > config.reward_budget:
        raise ValidationError("reward_budget", f"invalid_budget: cần ít nhất {cap} cho {mechanism}.")
    return config


def _exact_object(value, allowed, field):
    if not isinstance(value, dict):
        raise ValidationError(field, "Cần JSON object.")
    unknown = set(value) - set(allowed)
    missing = set(allowed) - set(value)
    if unknown:
        key = sorted(unknown)[0]
        raise ValidationError(f"{field}.{key}" if field else key, "Field không được hỗ trợ.")
    if missing:
        raise ValidationError(field, "Thiếu field bắt buộc.")
    return value


def _validate_v1(raw, mechanism):
    allowed = set(NUMERIC_FIELDS) | {"costs", "model_version"}
    unknown = set(raw) - allowed
    missing = allowed - {"operating_cost"} - set(raw)
    if unknown:
        raise ValidationError(sorted(unknown)[0], "Field không được hỗ trợ.")
    if missing:
        raise ValidationError(sorted(missing)[0], "Thiếu field bắt buộc.")
    values = {key: rational(raw.get(key, "0"), key) for key in NUMERIC_FIELDS}
    for key, value in values.items():
        if key in ("pi", "a", "b"):
            if not 0 < value < 1:
                raise ValidationError(key, "Phải thuộc khoảng mở (0,1).")
        elif value < 0:
            raise ValidationError(key, "Không được âm.")
    if not isinstance(raw["costs"], list) or len(raw["costs"]) != 3:
        raise ValidationError("costs", "Cần đúng ba chi phí A/B/C.")
    costs = tuple(rational(value, f"costs[{i}]") for i, value in enumerate(raw["costs"]))
    for i, value in enumerate(costs):
        if value < 0:
            raise ValidationError(f"costs[{i}]", "Không được âm.")
    config = Config(values["pi"], values["a"], values["b"], costs, values["f"], values["lambda"],
                    values["fixed_reward"], values["reward_budget"], values["payout_value"], values["operating_cost"])
    return _validate_budget(config, mechanism)


def _validate_v2(raw, mechanism):
    allowed = set(COMMON_NUMERIC_FIELDS) | {"model_version", "public_signal", "judges"}
    unknown = set(raw) - allowed
    missing = allowed - {"operating_cost"} - set(raw)
    if unknown:
        raise ValidationError(sorted(unknown)[0], "Field không được hỗ trợ.")
    if missing:
        raise ValidationError(sorted(missing)[0], "Thiếu field bắt buộc.")
    values = {key: rational(raw.get(key, "0"), key) for key in COMMON_NUMERIC_FIELDS}
    if not 0 < values["pi"] < 1:
        raise ValidationError("pi", "Phải thuộc khoảng mở (0,1).")
    for key in COMMON_NUMERIC_FIELDS[1:]:
        if values[key] < 0:
            raise ValidationError(key, "Không được âm.")

    if "specificity" not in raw["public_signal"]:
        raw["public_signal"]["specificity"] = raw["public_signal"]["sensitivity"]
    public = _exact_object(raw["public_signal"], ("sensitivity", "specificity"), "public_signal")
    public_values = tuple(rational(public[key], f"public_signal.{key}") for key in ("sensitivity", "specificity"))
    for key, value in zip(("sensitivity", "specificity"), public_values):
        if not 0 < value < 1:
            raise ValidationError(f"public_signal.{key}", "Phải thuộc khoảng mở (0,1).")

    judges = _exact_object(raw["judges"], JUDGES, "judges")
    sensitivities, specificities, costs = [], [], []
    for judge in JUDGES:
        item = _exact_object(judges[judge], ("private_signal", "high_effort_cost"), f"judges.{judge}")
        signal = _exact_object(item["private_signal"], ("sensitivity", "specificity"), f"judges.{judge}.private_signal")
        sensitivity = rational(signal["sensitivity"], f"judges.{judge}.private_signal.sensitivity")
        specificity = rational(signal["specificity"], f"judges.{judge}.private_signal.specificity")
        for key, value in (("sensitivity", sensitivity), ("specificity", specificity)):
            if not 0 < value < 1:
                raise ValidationError(f"judges.{judge}.private_signal.{key}", "Phải thuộc khoảng mở (0,1).")
        cost = rational(item["high_effort_cost"], f"judges.{judge}.high_effort_cost")
        if cost < 0:
            raise ValidationError(f"judges.{judge}.high_effort_cost", "Không được âm.")
        sensitivities.append(sensitivity)
        specificities.append(specificity)
        costs.append(cost)
    config = V2Config(values["pi"], *public_values, tuple(sensitivities), tuple(specificities), tuple(costs),
                      values["f"], values["lambda"], values["fixed_reward"], values["reward_budget"],
                      values["payout_value"], values["operating_cost"])
    return _validate_budget(config, mechanism)


def validate_config(raw, mechanism="rbts"):
    if mechanism not in MECHANISMS:
        raise ValidationError("mechanism", "Chỉ hỗ trợ fixed hoặc rbts.")
    if not isinstance(raw, dict):
        raise ValidationError("config", "Cần JSON object.")
    version = raw.get("model_version")
    if version not in SUPPORTED_MODEL_VERSIONS:
        raise ValidationError("model_version", f"Cần một trong: {', '.join(SUPPORTED_MODEL_VERSIONS)}.")
    return _validate_v1(raw, mechanism) if version == V1_MODEL_VERSION else _validate_v2(raw, mechanism)


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(field, "Cần chuỗi không rỗng.")
    return value


def validate_scenario(raw):
    if raw is None:
        return None
    scenario = _exact_object(raw, ("scenario_version", "scenario_id", "claim", "public_signal", "judges", "parameter_provenance"), "scenario")
    if scenario["scenario_version"] != "ceav-scenario-v1":
        raise ValidationError("scenario.scenario_version", "Cần ceav-scenario-v1.")
    _text(scenario["scenario_id"], "scenario.scenario_id")
    claim = _exact_object(scenario["claim"], ("text", "y_equals_1_when", "truth_resolution"), "scenario.claim")
    for key in ("text", "y_equals_1_when", "truth_resolution"):
        _text(claim[key], f"scenario.claim.{key}")
    public = _exact_object(scenario["public_signal"], ("meaning_of_1", "source"), "scenario.public_signal")
    for key in ("meaning_of_1", "source"):
        _text(public[key], f"scenario.public_signal.{key}")
    judges = _exact_object(scenario["judges"], JUDGES, "scenario.judges")
    for judge in JUDGES:
        item = _exact_object(judges[judge], ("private_check",), f"scenario.judges.{judge}")
        _text(item["private_check"], f"scenario.judges.{judge}.private_check")
    provenance = _exact_object(scenario["parameter_provenance"], ("status", "notes"), "scenario.parameter_provenance")
    if provenance["status"] not in ("assumption", "pilot_estimate", "historical_estimate"):
        raise ValidationError("scenario.parameter_provenance.status", "Cần assumption, pilot_estimate hoặc historical_estimate.")
    _text(provenance["notes"], "scenario.parameter_provenance.notes")
    return raw


@dataclass(frozen=True, slots=True)
class WeightedState:
    state_id: int
    y: int
    z: int
    signals: tuple[int, int, int]
    probability: F


@dataclass(frozen=True, slots=True)
class LowObservation:
    z: int


@dataclass(frozen=True, slots=True)
class HighObservation:
    z: int
    x: int


def observe(state, judge, effort):
    if judge not in range(3) or effort not in ("L", "H"):
        raise ValueError("Invalid judge or effort")
    return LowObservation(state.z) if effort == "L" else HighObservation(state.z, state.signals[judge])


def enumerate_states(config):
    result = []
    for index, (y, z, xa, xb, xc) in enumerate(product((0, 1), repeat=5)):
        mass = state_probability(config, y, z, (xa, xb, xc))
        result.append(WeightedState(index, y, z, (xa, xb, xc), mass))
    assert len(result) == 32 and all(row.probability > 0 for row in result)
    assert sum(row.probability for row in result) == 1
    return tuple(result)
