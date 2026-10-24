"""Print the reviewer-facing central results from the frozen package."""

from fractions import Fraction as F
import json

from verification import dual_boundary as subject


def _jsonable(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def main():
    print("T3 effort gap: 7/500")
    for mechanism in ("selective", "uniform"):
        table = subject.build_table(mechanism)
        scenario = subject.full_equilibria(table, (1, 1, 1))
        active = [e for e in scenario if subject.contains(e["interval"], F(1, 10))]
        print(f"{mechanism} T4 local interval: {subject.study()['mechanisms'][mechanism]['scenarios']['symmetric']['all_h01_closed_equilibrium_interval']}")
        print(f"{mechanism} T5 symmetric safe component: {subject.safe_component(subject.cells(scenario))}")
        print(f"{mechanism} pure equilibria at b=1/10: {len(active)}")
        for e in active:
            print(json.dumps(_jsonable({"profile": e["profile"], "metrics": e["metrics"], "all_gates_pass": e["all_gates_pass"]}), sort_keys=True))

    for mechanism in ("selective", "uniform"):
        neutral = subject.full_equilibria(subject.build_table(mechanism), (0, 0, 0))[0]["metrics"]
        print(json.dumps(_jsonable({"mechanism": mechanism, "neutral_metrics": neutral}), sort_keys=True))


if __name__ == "__main__":
    main()
