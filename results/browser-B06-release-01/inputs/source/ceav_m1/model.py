"""Validated exact inputs and the information available to each player."""

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
import re

from . import MODEL_VERSION

F = Fraction
JUDGES = ("A", "B", "C")
MECHANISMS = ("fixed", "rbts")
NUMERIC_FIELDS = ("pi", "a", "b", "f", "lambda", "fixed_reward", "reward_budget", "payout_value", "operating_cost")


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


def validate_config(raw, mechanism="rbts"):
    if mechanism not in MECHANISMS:
        raise ValidationError("mechanism", "Chỉ hỗ trợ fixed hoặc rbts.")
    if not isinstance(raw, dict):
        raise ValidationError("config", "Cần JSON object.")
    allowed = set(NUMERIC_FIELDS) | {"costs", "model_version"}
    unknown = set(raw) - allowed
    missing = allowed - {"operating_cost"} - set(raw)
    if unknown:
        raise ValidationError(sorted(unknown)[0], "Field không được hỗ trợ.")
    if missing:
        raise ValidationError(sorted(missing)[0], "Thiếu field bắt buộc.")
    if raw["model_version"] != MODEL_VERSION:
        raise ValidationError("model_version", f"Cần {MODEL_VERSION}.")
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
    cap = 3 * values["fixed_reward"] if mechanism == "fixed" else 3 * values["f"] + 6 * values["lambda"]
    if cap > values["reward_budget"]:
        raise ValidationError("reward_budget", f"invalid_budget: cần ít nhất {cap} cho {mechanism}.")
    return Config(values["pi"], values["a"], values["b"], costs, values["f"], values["lambda"],
                  values["fixed_reward"], values["reward_budget"], values["payout_value"], values["operating_cost"])


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
        mass = config.pi if y else 1 - config.pi
        mass *= config.a if z == y else 1 - config.a
        for x in (xa, xb, xc):
            mass *= config.b if x == y else 1 - config.b
        result.append(WeightedState(index, y, z, (xa, xb, xc), mass))
    assert len(result) == 32 and all(row.probability > 0 for row in result)
    assert sum(row.probability for row in result) == 1
    return tuple(result)
