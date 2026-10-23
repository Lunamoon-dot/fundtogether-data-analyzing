"""Effort/report maps and immutable candidate forecasts."""

from dataclasses import dataclass
from fractions import Fraction as F

from .model import HighObservation, LowObservation, ValidationError, enumerate_states, observe

ACTIONS = ("L0", "L1", "H00", "H01", "H10", "H11")


@dataclass(frozen=True, slots=True)
class Profile:
    branches: tuple[tuple[str, str, str], tuple[str, str, str]]

    def raw(self):
        return {str(z): list(self.branches[z]) for z in (0, 1)}


def validate_profile(raw):
    if not isinstance(raw, dict) or set(raw) != {"0", "1"}:
        raise ValidationError("profile", 'Cần đúng hai keys "0" và "1".')
    branches = []
    for z in (0, 1):
        row = raw[str(z)]
        if not isinstance(row, list) or len(row) != 3:
            raise ValidationError(f"profile.{z}", "Cần đúng ba action A/B/C.")
        for i, action in enumerate(row):
            if action not in ACTIONS:
                raise ValidationError(f"profile.{z}[{i}]", "Action không hợp lệ.")
        branches.append(tuple(row))
    return Profile(tuple(branches))


def report_for(action, observation):
    if action not in ACTIONS:
        raise ValueError("Unknown action")
    if action[0] == "L":
        if not isinstance(observation, LowObservation):
            raise TypeError("L requires LowObservation")
        return int(action[1])
    if not isinstance(observation, HighObservation):
        raise TypeError("H requires HighObservation, including H00/H11")
    return int(action[1 + observation.x])


def observation_key(observation):
    return (observation.z, observation.x) if isinstance(observation, HighObservation) else (observation.z,)


@dataclass(frozen=True, slots=True)
class Candidate:
    profile: Profile
    predictions: tuple
    rows: tuple
    prediction_semantics: str

    def prediction(self, judge, observation):
        for key, value in self.predictions[judge]:
            if key == observation:
                return value
        raise ValueError("Missing reachable candidate prediction")


def build_candidate(config, profile, rows=None, mechanism="rbts"):
    rows = enumerate_states(config) if rows is None else rows
    tables = []
    for i in range(3):
        groups = {}
        k = (i + 2) % 3
        for state in rows:
            actions = profile.branches[state.z]
            own = observe(state, i, actions[i][0])
            peer = report_for(actions[k], observe(state, k, actions[k][0]))
            mass, ones = groups.get(own, (F(0), F(0)))
            groups[own] = (mass + state.probability, ones + state.probability * peer)
        tables.append(tuple((key, ones / mass) for key, (mass, ones) in groups.items()))
    semantics = "unique_on_reachable_observations" if mechanism in ("rbts", "hybrid_anchor") and config.multiplier > 0 else "arbitrary_reachable_predictions"
    return Candidate(profile, tuple(tables), rows, semantics)


def realized(candidate, state):
    actions = candidate.profile.branches[state.z]
    observations = tuple(observe(state, i, action[0]) for i, action in enumerate(actions))
    reports = tuple(report_for(action, obs) for action, obs in zip(actions, observations))
    predictions = tuple(candidate.prediction(i, obs) for i, obs in enumerate(observations))
    return reports, predictions
