"""Read-only independent arithmetic review of the supplied G1-G4 release bundle.

Run from any directory: python <this file> > <new review result path>.
No production/test oracle imports; no input artifact writes.
"""

import csv
import hashlib
import json
import math
import re
from fractions import Fraction as F
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "results/case-evaluation-release-01"
ACTIONS = ("L0", "L1", "H00", "H01", "H10", "H11")
failures = []
counts = {}


def check(group, name, actual, expected):
    counts[group] = counts.get(group, 0) + 1
    if actual != expected:
        failures.append({"group": group, "name": name,
                         "actual": str(actual), "expected": str(expected)})


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fraction(value):
    return F(value["exact"] if isinstance(value, dict) else value)


def world(config):
    pi, a, b = (F(config[key]) for key in ("pi", "a", "b"))
    rows = []
    for s in product((0, 1), repeat=5):
        y, z, *xs = s
        weight = pi if y else 1 - pi
        weight *= a if z == y else 1 - a
        for x in xs:
            weight *= b if x == y else 1 - b
        rows.append((s, weight))
    return rows


def report(state, judge, action):
    return int(action[1 + state[2 + judge]]) if action[0] == "H" else int(action[1])


def observation(state, judge, action):
    return (state[1], state[judge + 2]) if action[0] == "H" else (state[1],)


def forecast(rows, profile, judge, z, trial_action):
    peer = (judge + 2) % 3
    table = {}
    for x in ((0, 1) if trial_action[0] == "H" else (None,)):
        group = [(s, w) for s, w in rows if s[1] == z and (x is None or s[judge + 2] == x)]
        mass = sum(w for s, w in group)
        table[(z, x) if x is not None else (z,)] = sum(
            w * report(s, peer, profile[z][peer]) for s, w in group) / mass
    return table


def local_values(config, state, profile, tables, judge, action=None, own_table=None):
    i, z = judge, state[1]
    j, k = (i + 1) % 3, (i + 2) % 3
    action = profile[z][i] if action is None else action
    own_table = tables[i] if own_table is None else own_table
    r = report(state, i, action)
    peer_r = report(state, k, profile[z][k])
    p = own_table[observation(state, i, action)]
    pj = tables[j][observation(state, j, profile[z][j])]
    shadow = pj + (2 * r - 1) * min(pj, 1 - pj)
    # Alternative equivalent binary quadratic formula, independent of engine.
    info, prediction = 1 - (shadow - peer_r) ** 2, 1 - (p - peer_r) ** 2
    score = info + prediction
    reward = F(config["f"]) + F(config["lambda"]) * score
    cost = F(config["costs"][i]) if action[0] == "H" else F(0)
    return {"action": action, "report": r, "prediction": p, "reference_id": j,
            "peer_id": k, "shadow": shadow, "information_score": info,
            "prediction_score": prediction, "total_score": score, "score": score,
            "reward": reward, "effort_cost": cost, "utility": reward - cost}


manifest = read_json(BUNDLE / "manifest.json")
for item in manifest["generated_files"]:
    path = BUNDLE / item["name"]
    check("bundle_integrity", item["name"] + " bytes", path.stat().st_size, item["bytes"])
    check("bundle_integrity", item["name"] + " sha256", digest(path), item["sha256"])
for item in read_csv(BUNDLE / "provenance.csv"):
    path = ROOT / item["path"]
    check("provenance", item["path"] + " bytes", path.stat().st_size, int(item["bytes"]))
    check("provenance", item["path"] + " sha256", digest(path), item["sha256"])
for link in re.findall(r"\]\(([^)]+)\)", (BUNDLE / "REPORT.md").read_text(encoding="utf-8-sig")):
    check("report_links", link, (BUNDLE / link).exists(), True)

summaries = read_csv(BUNDLE / "case_summary.csv")
branches = read_csv(BUNDLE / "branch_details.csv")
predictions = read_csv(BUNDLE / "predictions.csv")
check("coverage", "cases", [r["case"] for r in summaries], ["G1", "G2", "G3", "G4"])
check("coverage", "branch rows", len(branches), 24)
check("coverage", "prediction rows", len(predictions), 42)
case_results = {}
for line in summaries:
    case = line["case"]
    run = ROOT / "results" / manifest["source_runs"][case]
    source = read_json(run / "manifest.json")
    config = source["config"]
    profile = tuple(tuple(source["profile"][str(z)]) for z in (0, 1))
    check(case + "_source", "status", source["status"], "succeeded")
    for item in source["artifacts"]:
        path = run / item["name"]
        check(case + "_source", item["name"] + " sha256", digest(path), item["sha256"])
    for key in ("pi", "a", "b", "f", "lambda", "reward_budget", "payout_value"):
        check(case + "_inputs", key, F(line[key]), F(config[key]))
    for i, label in enumerate("ABC"):
        check(case + "_inputs", "cost_" + label, F(line["cost_" + label]), F(config["costs"][i]))
    rows = world(config)
    masses = [sum(w for s, w in rows if s[1] == z) for z in (0, 1)]
    check(case + "_distribution", "mass", sum(w for s, w in rows), 1)
    tables = [forecast(rows, profile, i, 0, profile[0][i]) |
              forecast(rows, profile, i, 1, profile[1][i]) for i in range(3)]
    for i, label in enumerate("ABC"):
        matching = [r for r in predictions if r["case"] == case and r["judge"] == label]
        check(case + "_predictions", label + " observation set",
              {tuple(map(int, r["observation"].split("|"))) for r in matching}, set(tables[i]))
        for r in matching:
            key = tuple(map(int, r["observation"].split("|")))
            check(case + "_predictions", label + str(key), F(r["prediction_exact"]), tables[i][key])
    state_records = read_csv(run / "states.csv")
    check(case + "_states", "row count", len(state_records), 32)
    totals = [{k: F(0) for k in ("reward", "effort_cost", "utility")} for i in range(3)]
    accuracy = fp = fn = payout = F(0)
    for index, (state, weight) in enumerate(rows):
        record = state_records[index]
        y, z, xa, xb, xc = state
        observed = tuple(int(record[k]) for k in ("y", "z", "x_A", "x_B", "x_C"))
        check(case + "_states", str(index) + " state", observed, state)
        check(case + "_states", str(index) + " mass", F(record["probability_exact"]), weight)
        values = [local_values(config, state, profile, tables, i) for i in range(3)]
        decision = int(sum(v["report"] for v in values) >= 2)
        check(case + "_states", str(index) + " decision", int(record["decision"]), decision)
        check(case + "_states", str(index) + " loss", F(record["wrong_payout_contribution_exact"]),
              F(config["payout_value"]) * weight * (y == 0 and decision == 1))
        for i, label in enumerate("ABC"):
            for key, value in values[i].items():
                name = label + "_" + key
                actual = F(record[name + "_exact"]) if isinstance(value, F) else record[name] if key == "action" else int(record[name])
                check(case + "_states", str(index) + " " + name, actual, value)
            for key in totals[i]:
                totals[i][key] += weight * values[i][key]
        accuracy += weight * (decision == y)
        fp += weight * (decision == 1 and y == 0)
        fn += weight * (decision == 0 and y == 1)
        payout += weight * decision
    metric = {"accuracy": accuracy, "false_approval_rate": fp / (1 - F(config["pi"])),
              "false_rejection_rate": fn / F(config["pi"]), "wrong_payout_probability": fp,
              "wrong_payout_value": fp * F(config["payout_value"]),
              "expected_payout": payout * F(config["payout_value"]),
              "expected_reward_total": sum(t["reward"] for t in totals),
              "expected_effort_cost": sum(t["effort_cost"] for t in totals)}
    metric["cash_review_cost"] = metric["expected_reward_total"] + F(config["operating_cost"])
    expected = dict(metric)
    expected.update({"judge_utility_" + label: totals[i]["utility"] for i, label in enumerate("ABC")})
    expected.update({"branch_mass_z" + str(z): masses[z] for z in (0, 1)})
    regrets, deltas = [], {}
    for i, z in product(range(3), (0, 1)):
        label = "ABC"[i]
        matching = [r for r in branches if (r["case"], r["judge"], int(r["z"])) == (case, label, z)]
        check(case + "_branch", label + str(z) + " multiplicity", len(matching), 1)
        r = matching[0]
        options = {}
        for action in ACTIONS:
            own = forecast(rows, profile, i, z, action)
            options[action] = sum(w * local_values(config, s, profile, tables, i, action, own)["utility"]
                                  for s, w in rows if s[1] == z) / masses[z]
        candidate = sum(w * local_values(config, s, profile, tables, i)["utility"]
                        for s, w in rows if s[1] == z) / masses[z]
        low, high = max(options[a] for a in ACTIONS[:2]), max(options[a] for a in ACTIONS[2:])
        best = max(options.values()); regret = best - candidate
        regrets.append(regret); deltas[label + str(z)] = high - low
        numbers = {"branch_probability": masses[z], "candidate_utility": candidate,
                   "low_utility": low, "high_utility": high, "best_utility": best,
                   "regret": regret, "high_minus_low": high - low}
        for key, value in numbers.items():
            check(case + "_branch", label + str(z) + " " + key, F(r[key + "_exact"]), value)
        for key, acts, maximum in (("low_best_actions", ACTIONS[:2], low),
                                  ("high_best_actions", ACTIONS[2:], high),
                                  ("overall_best_actions", ACTIONS, best)):
            check(case + "_branch", label + str(z) + key, r[key], "|".join(a for a in acts if options[a] == maximum))
        if regret:
            witness = r["witness_action"]
            check(case + "_branch", label + str(z) + " witness gain", options[witness] - candidate, regret)
            check(case + "_branch", label + str(z) + " conditional gain", F(r["witness_conditional_gain_exact"]), regret)
            check(case + "_branch", label + str(z) + " ex ante gain", F(r["witness_ex_ante_gain_exact"]), regret * masses[z])
        else:
            check(case + "_branch", label + str(z) + " no witness", r["witness_action"], "")
    expected["max_regret"] = max(regrets)
    for key, value in expected.items():
        check(case + "_summary", key, F(line[key + "_exact"]), value)
    source_summary = read_json(run / "summary.json")
    for key, value in metric.items():
        check(case + "_summary", "source " + key, fraction(source_summary["metrics"][key]), value)
    check(case + "_summary", "equilibrium", line["equilibrium_status"],
          "exact_pure_equilibrium" if max(regrets) == 0 else "not_equilibrium")
    case_results[case] = {k: str(v) for k, v in expected.items()}
    case_results[case]["deltas"] = {k: str(v) for k, v in deltas.items()}

for name in ("case_summary.csv", "branch_details.csv", "predictions.csv"):
    for index, row in enumerate(read_csv(BUNDLE / name)):
        for key in row:
            if key.endswith("_exact") and row[key] and key[:-6] + "_decimal" in row:
                decimal = float(row[key[:-6] + "_decimal"])
                check("decimal_display", name + str(index) + key,
                      math.isfinite(decimal) and math.isclose(decimal, float(F(row[key])), rel_tol=1e-14, abs_tol=1e-15), True)

print(json.dumps({"scope": "Four supplied cases and their source states, not a complete software audit",
                  "production_imports": False, "bundle_manifest_sha256": digest(BUNDLE / "manifest.json"),
                  "checks_by_group": counts, "failures": failures, "cases": case_results}, indent=2))
raise SystemExit(bool(failures))
