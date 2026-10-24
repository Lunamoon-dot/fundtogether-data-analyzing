"""Independent review checks for the paper's T3--T5 claims.

This file intentionally keeps the algebraic effort calculation separate from
the dual-boundary analyzer.  The T4/T5 replay delegates only the exhaustive
certificate comparison to the already independent potential-state oracle and
completeness audit; it does not import the analyzer's payoff helper to derive
the effort threshold or the binding T4 rows.
"""

from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path

from verification import dual_boundary as subject
from verification import dual_boundary_audit as independent_audit


def p_correct(observed, truth, accuracy):
    return accuracy if observed == truth else 1 - accuracy


def conditional_match_values(z):
    """Return M_L and M_H for matching an independent T to a report."""
    posterior_y = {y: F(7, 10) if y == z else F(3, 10) for y in (0, 1)}
    # T's most likely label is z, so Low's modal match is 33/50.
    match_low = sum(
        posterior_y[y] * p_correct(z, y, F(9, 10)) for y in (0, 1)
    )
    # After buying X, choose the modal T label conditional on X.
    match_high = F(0)
    for x in (0, 1):
        joint_x = sum(
            posterior_y[y] * p_correct(x, y, F(4, 5)) for y in (0, 1)
        )
        conditional_match = max(
            sum(
                posterior_y[y]
                * p_correct(x, y, F(4, 5))
                * p_correct(r, y, F(9, 10))
                for y in (0, 1)
            )
            / joint_x
            for r in (0, 1)
        )
        match_high += joint_x * conditional_match
    return match_low, match_high


def t3_checks():
    rows = []
    for z in (0, 1):
        low, high = conditional_match_values(z)
        rows.append({"z": z, "M_L": str(low), "M_H": str(high), "delta": str(high - low)})
        assert low == F(33, 50)
        assert high == F(37, 50)
        assert high - low == F(2, 25)
    # Certified point: mu*a*delta - c = 2*(2/5)*(2/25) - 1/20.
    effort_gap = F(2) * F(2, 5) * F(2, 25) - F(1, 20)
    assert effort_gap == F(7, 500)
    return {"match_values": rows, "certified_effort_gap": str(effort_gap)}


def t4_checks():
    # These are the two binding exact rows independently re-derived in the
    # review note: gap + b*slope >= 0.
    selective = {
        "negative": (F(-7, 500), F(-633, 5000), F(-70, 633)),
        "positive": (F(-7, 500), F(551, 6250), F(175, 1102)),
    }
    uniform = {
        "negative": (F(-7, 500), F(-2070709, 15625000), F(-218750, 2070709)),
        "positive": (F(-7, 500), F(1365587, 15625000), F(218750, 1365587)),
    }
    out = {}
    for name, rows in (("selective", selective), ("uniform", uniform)):
        out[name] = {}
        for label, (intercept, slope, expected) in rows.items():
            solved = -intercept / slope
            assert solved == expected, (name, label, solved, expected)
            out[name][label] = {"intercept": str(intercept), "slope": str(slope), "breakpoint": str(solved)}
    return out


def t5_checks():
    audit = independent_audit.audit(subject)
    assert audit["status"] == "PASS"
    assert audit["all_real_b"] is True
    assert audit["full_profiles_covered"] == 466560
    assert audit["branch_candidates"] == 4320
    assert audit["checks"] >= 5000

    selective = subject.study()["mechanisms"]["selective"]["scenarios"]["symmetric"]
    uniform = subject.study()["mechanisms"]["uniform"]["scenarios"]["symmetric"]
    assert selective["safe_component_containing_zero"] == {
        "lo": F(-70, 633), "hi": F(175, 1922),
        "lo_included": False, "hi_included": False,
    }
    assert uniform["safe_component_containing_zero"] == {
        "lo": F(-218750, 2070709), "hi": F(109375, 1189451),
        "lo_included": False, "hi_included": False,
    }
    at_tenth = [
        e for e in subject.full_equilibria(subject.build_table("selective"), (1, 1, 1))
        if subject.contains(e["interval"], F(1, 10))
    ]
    assert len(at_tenth) == 4
    assert sum(not e["all_gates_pass"] for e in at_tenth) == 3
    return {
        "independent_audit": audit,
        "symmetric_safe_components": {
            "selective": {k: (str(v) if isinstance(v, F) else v) for k, v in selective["safe_component_containing_zero"].items()},
            "uniform": {k: (str(v) if isinstance(v, F) else v) for k, v in uniform["safe_component_containing_zero"].items()},
        },
        "selective_at_b_1_10": {
            "pure_equilibria": len(at_tenth),
            "bad_equilibria": sum(not e["all_gates_pass"] for e in at_tenth),
        },
    }


def main():
    result = {"T3": t3_checks(), "T4": t4_checks(), "T5": t5_checks()}
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
