"""Independent exact finite-sum oracle for CEAV-M1 V5 Phase 1.

The oracle constructs binary likelihood tables directly.  It deliberately does
not import the production CEAV evaluator or any V4/V3 analyzer.
"""

from dataclasses import dataclass
from fractions import Fraction as F
from itertools import product


JUDGES = ("A", "B", "C")


@dataclass(frozen=True)
class JudgeSpec:
    sensitivity: F
    specificity: F
    cost: F


@dataclass(frozen=True)
class Fixture:
    name: str
    prior: F
    public_sensitivity: F
    public_specificity: F
    judges: tuple[JudgeSpec, JudgeSpec, JudgeSpec]
    audit_sensitivity: F
    audit_specificity: F
    target_weights: tuple[F, F]
    batch_weights: tuple[F, F]
    batch_size: int = 4


def _likelihood(value, truth, sensitivity, specificity):
    if truth:
        return sensitivity if value else 1 - sensitivity
    return specificity if not value else 1 - specificity


def _fixture(name):
    if name == "F51-01":
        return Fixture(
            name=name, prior=F(1, 2), public_sensitivity=F(19, 20),
            public_specificity=F(19, 20),
            judges=tuple(JudgeSpec(F(4, 5), F(4, 5), F(1, 20)) for _ in JUDGES),
            audit_sensitivity=F(9, 10), audit_specificity=F(9, 10),
            target_weights=(F(1, 2), F(1, 2)), batch_weights=(F(1, 2), F(1, 2)))
    if name == "F51-02":
        return Fixture(
            name=name, prior=F(1, 2), public_sensitivity=F(7, 10),
            public_specificity=F(7, 10),
            judges=tuple(JudgeSpec(F(4, 5), F(4, 5), F(1, 20)) for _ in JUDGES),
            audit_sensitivity=F(9, 10), audit_specificity=F(9, 10),
            target_weights=(F(1, 2), F(1, 2)), batch_weights=(F(1, 2), F(1, 2)))
    if name == "V3-HET":
        return Fixture(
            name=name, prior=F(1, 2), public_sensitivity=F(4, 5),
            public_specificity=F(3, 5), judges=(
                JudgeSpec(F(9, 10), F(4, 5), F(1, 20)),
                JudgeSpec(F(3, 4), F(19, 20), F(1, 10)),
                JudgeSpec(F(13, 20), F(7, 10), F(1, 25)),
            ), audit_sensitivity=F(9, 10), audit_specificity=F(9, 10),
            target_weights=(F(2, 5), F(3, 5)), batch_weights=(F(1, 2), F(1, 2)))
    raise KeyError(name)


def _resolve_fixture(fixture):
    return _fixture(fixture) if isinstance(fixture, str) else fixture


def public_mass(fixture, z):
    fixture = _resolve_fixture(fixture)
    return sum((fixture.prior if y else 1 - fixture.prior)
               * _likelihood(z, y, fixture.public_sensitivity, fixture.public_specificity)
               for y in (0, 1))


def _conditional_rows(fixture, judge, z):
    fixture = _resolve_fixture(fixture)
    spec = fixture.judges[judge] if isinstance(judge, int) else fixture.judges[JUDGES.index(judge)]
    rows = []
    for y, x, t in product((0, 1), repeat=3):
        probability = (fixture.prior if y else 1 - fixture.prior)
        probability *= _likelihood(z, y, fixture.public_sensitivity, fixture.public_specificity)
        probability *= _likelihood(x, y, spec.sensitivity, spec.specificity)
        probability *= _likelihood(x * 0 + t, y, fixture.audit_sensitivity,
                                   fixture.audit_specificity)
        rows.append((probability, y, x, t))
    mass = sum(row[0] for row in rows)
    if mass <= 0:
        raise ValueError("conditional branch has no probability mass")
    return [(probability / mass, y, x, t) for probability, y, x, t in rows]


def posterior_y(fixture, judge, z, x=None):
    rows = _conditional_rows(fixture, judge, z)
    if x is not None:
        rows = [(p, y, x0, t) for p, y, x0, t in rows if x0 == x]
        mass = sum(p for p, *_ in rows)
        rows = [(p / mass, y, x0, t) for p, y, x0, t in rows]
    return sum(p for p, y, _, _ in rows if y == 1)


def posterior_t(fixture, judge, z, x=None):
    rows = _conditional_rows(fixture, judge, z)
    if x is not None:
        rows = [(p, y, x0, t) for p, y, x0, t in rows if x0 == x]
        mass = sum(p for p, *_ in rows)
        rows = [(p / mass, y, x0, t) for p, y, x0, t in rows]
    return sum(p for p, _, _, t in rows if t == 1)


def conditional_delta_y(fixture, judge, z):
    fixture = _resolve_fixture(fixture)
    low = posterior_y(fixture, judge, z)
    return sum(
        sum(p for p, _, x0, _ in _conditional_rows(fixture, judge, z) if x0 == x)
        * (posterior_y(fixture, judge, z, x) - low) ** 2
        for x in (0, 1)
    )


def conditional_delta_t(fixture, judge, z):
    low = posterior_t(fixture, judge, z)
    return sum(
        sum(p for p, _, x0, _ in _conditional_rows(fixture, judge, z) if x0 == x)
        * (posterior_t(fixture, judge, z, x) - low) ** 2
        for x in (0, 1)
    )


def score(p, t):
    return 1 - (p - t) ** 2


def proper_score_expectation(forecast, event_probability):
    return event_probability * score(forecast, 1) + (1 - event_probability) * score(forecast, 0)


def payment_bounds(mechanism, f, mu):
    if mechanism == "incremental":
        return {"minimum": f, "maximum": f + 2 * mu, "cap_total": 3 * f + 6 * mu}
    if mechanism == "direct":
        return {"minimum": f, "maximum": f + mu, "cap_total": 3 * f + 3 * mu}
    raise KeyError(mechanism)


def expected_low_reward(fixture, judge, z, mechanism, f, mu, q):
    low = posterior_t(fixture, judge, z)
    if mechanism == "incremental":
        score_value = F(1)
    elif mechanism == "direct":
        score_value = proper_score_expectation(low, low)
    else:
        raise KeyError(mechanism)
    return f + mu * q * score_value


def expected_high_reward(fixture, judge, z, mechanism, f, mu, q):
    return expected_low_reward(fixture, judge, z, mechanism, f, mu, q) \
        + mu * q * conditional_delta_t(fixture, judge, z)


def fixture_metrics(name):
    fixture = _fixture(name)
    delta_y_by_judge = tuple(tuple(conditional_delta_y(fixture, i, z) for z in (0, 1))
                             for i in range(3))
    delta_t_by_judge = tuple(tuple(conditional_delta_t(fixture, i, z) for z in (0, 1))
                             for i in range(3))
    return {
        "fixture": fixture,
        "delta_y_by_judge": delta_y_by_judge,
        "delta_t_by_judge": delta_t_by_judge,
        "delta_y": delta_y_by_judge[0],
        "delta_t": delta_t_by_judge[0],
        "public_masses": tuple(public_mass(fixture, z) for z in (0, 1)),
        "target_weights": fixture.target_weights,
        "batch_weights": fixture.batch_weights,
        "audit_sensitivity": fixture.audit_sensitivity,
        "audit_specificity": fixture.audit_specificity,
        "p_l_t": tuple(posterior_t(fixture, 0, z) for z in (0, 1)),
        "p_l_y": tuple(posterior_y(fixture, 0, z) for z in (0, 1)),
    }


def all_fixture_metrics():
    return {name: fixture_metrics(name) for name in ("F51-01", "F51-02", "V3-HET")}
