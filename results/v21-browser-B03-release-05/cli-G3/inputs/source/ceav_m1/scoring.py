"""RBTS Eq. (8). Scoring has no ground-truth or full-state argument."""

from fractions import Fraction as F


def quadratic(p, report):
    if not isinstance(p, F) or not 0 <= p <= 1 or type(report) is not int or report not in (0, 1):
        raise ValueError("Expected rational prediction in [0,1] and binary report")
    return 2 * p - p * p if report else 1 - p * p


def score_judge(reports, predictions, judge):
    if judge not in range(3) or len(reports) != 3 or len(predictions) != 3:
        raise ValueError("Expected three distinct cyclic roles")
    if any(type(r) is not int or r not in (0, 1) for r in reports):
        raise ValueError("Reports must be binary")
    if any(not isinstance(p, F) or not 0 <= p <= 1 for p in predictions):
        raise ValueError("Predictions must be rational and in [0,1]")
    j, k = (judge + 1) % 3, (judge + 2) % 3
    p = predictions[j]
    shadow = p + (2 * reports[judge] - 1) * min(p, 1 - p)
    information = quadratic(shadow, reports[k])
    prediction = quadratic(predictions[judge], reports[k])
    return {"reference_id": j, "peer_id": k, "shadow": shadow, "information_score": information,
            "prediction_score": prediction, "total_score": information + prediction}


def reward(score, mechanism, config):
    if mechanism == "fixed":
        return config.fixed_reward
    if mechanism == "rbts":
        return config.f + config.multiplier * score
    raise ValueError("Unknown mechanism")
