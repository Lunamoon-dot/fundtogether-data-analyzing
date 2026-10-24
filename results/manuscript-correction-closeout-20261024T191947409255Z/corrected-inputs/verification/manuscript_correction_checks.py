"""Scoped v0.3 editorial checks; no new game, parameters or equilibrium search."""
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import re

from verification import dual_boundary_oracle as oracle

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = "CEAV_M1_MANUSCRIPT_V0_3.md"
BRIEF = "CEAV_M1_EXTERNAL_RESEARCH_BRIEF.md"


def document(name):
    direct = ROOT / name
    return (direct if direct.exists() else ROOT / "docs" / name).read_text(encoding="utf-8")


def packaged(text):
    return (text.replace("](figures/", "](../figures/")
            .replace("](verification/", "](../verification/")
            .replace("](review-package/README.md)", "](../README.md)"))


def main():
    checks = 0

    def check(condition, label):
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(label)

    manuscript, brief = document(MANUSCRIPT), document(BRIEF)
    prop1 = manuscript.split("### Proposition 1", 1)[1].split("### Proposition 2", 1)[0]
    prop3 = manuscript.split("### Proposition 3", 1)[1].split("### Proposition 4", 1)[0]
    flat1, flat3 = " ".join(prop1.split()), " ".join(prop3.split())
    for token in ("jointly independent", "future audit signal `T`", "locked before", "risk-neutral utility", "no other report-dependent payoff", "cost `c>0`"):
        check(token in flat1, "Proposition 1 assumption: " + token)
    for token in ("Delta U_i(a_i,z;b_i) = U_i(a_i,H01_-i | Z=z) - U_i(H01,H01_-i | Z=z)", "`Delta U_i<=0`", "`Delta U_i<0`", "nonself action", "self comparison is always zero"):
        check(token in flat3, "Proposition 3 convention: " + token)

    parsed = {}
    for z, action, intercept, sign, magnitude in re.findall(
        r"Z=(\d),(L[01]): (-?\d+/\d+) ([+-])\((\d+/\d+)\)b_i <= 0", prop3
    ):
        parsed[int(z), action] = (F(intercept), F(magnitude) * (1 if sign == "+" else -1))
    check(set(parsed) == {(0, "L0"), (1, "L1")}, "both corrected displayed weak inequalities")

    expected = {"selective": (F(-70, 633), F(175, 1102)),
                "uniform": (F(-218750, 2070709), F(218750, 1365587))}
    boundary_cases = []
    h01 = ("H01",) * 3
    for mechanism, (lo, hi) in expected.items():
        rows = {i: [] for i in range(3)}
        for z in (0, 1):
            base = oracle.evaluate(z, h01, mechanism)
            for i in range(3):
                for action in oracle.ACTIONS:
                    if action == "H01":
                        continue
                    changed = list(h01)
                    changed[i] = action
                    dev = oracle.evaluate(z, changed, mechanism)
                    c = dev["utility"][i] - base["utility"][i]
                    s = dev["release"] - base["release"]
                    rows[i].append((z, action, c, s))
                    if mechanism == "selective" and (z, action) in parsed:
                        check((c, s) == parsed[z, action], "printed row equals primitive deviation utility")
        for i, deviations in rows.items():
            lower = max(-c / s for _, _, c, s in deviations if s < 0)
            upper = min(-c / s for _, _, c, s in deviations if s > 0)
            check((lower, upper) == (lo, hi), "unchanged exact endpoints for each Judge")
            check(all(c <= 0 for _, _, c, s in deviations if s == 0), "zero-slope constraints")
            for label, b in (("neutral", F(0)), ("lower", lo), ("upper", hi),
                             ("below_lower", lo - F(1, 1000000)),
                             ("above_upper", hi + F(1, 1000000))):
                maximum = max(c + b * s for _, _, c, s in deviations)
                check(maximum < 0 if label == "neutral" else maximum == 0 if label in ("lower", "upper") else maximum > 0,
                      mechanism + " " + label + " weak/strict/profitable-deviation condition")
                boundary_cases.append({"mechanism": mechanism, "judge": i, "case": label,
                                       "b": str(b), "max_nonself_deviation_gain": str(maximum)})
        for text in (manuscript, brief):
            check(f"{lo} < b_i < {hi}" in text, "published strict interval unchanged")

    for text in (manuscript, brief):
        flat = " ".join(text.split())
        check("general-purpose decentralized crowdfunding protocol" in flat, "general-purpose scope")
        check("Charity is one optional use case" in flat, "charity optional")
        check("independent random draws" in flat, "lottery draws")
        check("payment-only audit" in flat or "only `A_pay` fires" in flat, "payment-only observation")
        check("global deviations can coordinate" not in text, "no unsupported coordination explanation")
        for token in ("hardcoded binding rows", "primitive", "prose"):
            check(token in flat, "verification attribution: " + token)
    for good, bad in (("Gao, Xi Alice,", "Gao, Siyu,"), ("Kong, Yuqing, Katrina Ligett,", "Jennifer Ligett"),
                      ("Kong, Yuqing, and Grant Schoenebeck.", "Kong, Yiling")):
        check(good in manuscript and bad not in manuscript, "corrected byline: " + good)

    old = document("CEAV_M1_MANUSCRIPT_V0_2.md")
    tables = lambda text: [line for line in text.split("## 6. Exact baseline and strategic witnesses", 1)[1].split("## 7.", 1)[0].splitlines() if line.startswith("|")]
    check(tables(old) == tables(manuscript), "all baseline/witness metric table rows unchanged")
    old_t4 = old.split("### Proposition 3", 1)[1].split("**Proof.**", 1)[0]
    check([line for line in old_t4.splitlines() if line.startswith("|")] ==
          [line for line in prop3.split("**Proof.**", 1)[0].splitlines() if line.startswith("|")], "T4 result table unchanged")
    synchronized = None
    if (ROOT / "review-package").exists():
        synchronized = True
        for name in (MANUSCRIPT, BRIEF, "CEAV_M1_BIBLIOGRAPHY_PRIMARY_CHECK.md"):
            check(packaged(document(name)) == (ROOT / "review-package/docs" / name).read_text(encoding="utf-8"),
                  "root/package agree after relative-link adjustment: " + name)
    print(json.dumps({"status": "PASS", "checks": checks, "boundary_cases": boundary_cases,
                      "root_package_synchronized": synchronized,
                      "manuscript_text_sha256": sha256(manuscript.encode()).hexdigest(),
                      "scope": "fixed T4 neutral/boundary and selected editorial conditions, not a general prose-proof verifier"}, indent=2))


if __name__ == "__main__":
    main()
