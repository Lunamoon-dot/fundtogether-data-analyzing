"""Cross-check manuscript v0.2 metrics against the immutable boundary certificate."""

from fractions import Fraction as F
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CERT_PATH = ROOT / "results/dual-strategic-boundary-20261024T0524070523492Z/analysis/certificate.json"


def fraction(value):
    return F(value) if isinstance(value, str) else F(value)


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label}: {actual!r} != {expected!r}")


def main():
    cert_bytes = CERT_PATH.read_bytes()
    cert_hash = hashlib.sha256(cert_bytes).hexdigest()
    expected_cert_hash = "fde3ad4745b37e270469aaec2692a51c83cbcf5db7fcb0a16938296a6e25b7d5"
    assert_equal(cert_hash, expected_cert_hash, "immutable certificate hash")
    cert = json.loads(cert_bytes.decode("utf-8"))

    metric_rows = 0
    for mechanism, mechanism_data in cert["mechanisms"].items():
        for scenario, scenario_data in mechanism_data["scenarios"].items():
            for equilibrium in scenario_data["equilibria"]:
                metric_rows += 1
                metrics = equilibrium["metrics"]
                fa = fraction(metrics["fa"])
                fr = fraction(metrics["fr"])
                assert_equal(
                    fraction(metrics["wrong_payout"]), fa / 2,
                    f"{mechanism}/{scenario}/{equilibrium['id']} WrongPayout=FA/2",
                )
                assert_equal(
                    fraction(metrics["loss"]), fa + fr / 2,
                    f"{mechanism}/{scenario}/{equilibrium['id']} Loss=FA+FR/2",
                )

    neutral_expected = {
        "selective": {
            "fa": "43/1250", "fr": "481/3125", "loss": "348/3125",
            "wrong_payout": "43/2500", "cash": "46957/25000",
            "exposure": "2557/6250", "reserve": "6",
        },
        "uniform": {
            "fa": "328691/9765625", "fr": "3184297/19531250",
            "loss": "4499061/39062500", "wrong_payout": "328691/19531250",
            "cash": "46957/25000", "exposure": "2557/6250", "reserve": "6",
        },
    }
    witness_expected = {
        "selective": {
            "fa": "1391/6250", "fr": "313/3125", "loss": "852/3125",
            "wrong_payout": "1391/12500", "cash": "45357/25000",
            "exposure": "2557/6250", "reserve": "6",
        },
        "uniform": {
            "fa": "2148236/9765625", "fr": "8571103/78125000",
            "loss": "42942879/156250000", "wrong_payout": "1074118/9765625",
            "cash": "45357/25000", "exposure": "2557/6250", "reserve": "6",
        },
    }
    negative_expected = {
        "selective": {"cash": "7387/4000", "exposure": "411/1000"},
        "uniform": {"cash": "46157/25000", "exposure": "2557/6250"},
    }
    local_expected = {
        "selective": ("-70/633", "175/1102"),
        "uniform": ("-218750/2070709", "218750/1365587"),
    }
    safe_expected = {
        "selective": ("-70/633", "175/1922"),
        "uniform": ("-218750/2070709", "109375/1189451"),
    }

    for mechanism in ("selective", "uniform"):
        neutral = cert["mechanisms"][mechanism]["scenarios"]["neutral"]["equilibria"]
        neutral_rows = [
            row for row in neutral
            if row["profile"] == [["H01", "H01", "H01"], ["H01", "H01", "H01"]]
        ]
        assert_equal(len(neutral_rows), 1, f"{mechanism} neutral All-H row count")
        for key, expected in neutral_expected[mechanism].items():
            assert_equal(neutral_rows[0]["metrics"][key], expected, f"{mechanism} neutral {key}")

        symmetric = cert["mechanisms"][mechanism]["scenarios"]["symmetric"]
        witness_rows = [
            row for row in symmetric["equilibria"]
            if row["profile"] == [["H01", "H01", "H01"], ["L1", "L1", "H01"]]
        ]
        assert_equal(len(witness_rows), 1, f"{mechanism} positive witness row count")
        for key, expected in witness_expected[mechanism].items():
            assert_equal(witness_rows[0]["metrics"][key], expected, f"{mechanism} positive witness {key}")

        negative_rows = [
            row for row in symmetric["equilibria"]
            if row["profile"] == [["L0", "H01", "H01"], ["H01", "H01", "H01"]]
        ]
        assert_equal(len(negative_rows), 1, f"{mechanism} negative witness row count")
        for key, expected in negative_expected[mechanism].items():
            assert_equal(negative_rows[0]["metrics"][key], expected, f"{mechanism} negative witness {key}")

        local_interval = cert["mechanisms"][mechanism]["scenarios"]["symmetric"]["all_h01_closed_equilibrium_interval"]
        assert_equal(tuple(local_interval), local_expected[mechanism], f"{mechanism} local interval")
        safe = cert["mechanisms"][mechanism]["scenarios"]["symmetric"]["safe_component_containing_zero"]
        assert_equal((safe["lo"], safe["hi"]), safe_expected[mechanism], f"{mechanism} safe component")
        assert_equal((safe["lo_included"], safe["hi_included"]), (False, False), f"{mechanism} safe endpoint inclusion")

    print(json.dumps({
        "status": "PASS",
        "certificate_sha256": cert_hash,
        "metric_rows_checked": metric_rows,
        "conditional_definitions": {
            "FA": "P(D=1|Y=0)",
            "FR": "P(D=0|Y=1)",
            "WrongPayout": "V*P(Y=0,D=1)",
            "Loss": "C_FA*P(Y=0,D=1)+C_FR*P(Y=1,D=0)",
            "fixed_reduction": "pi=1/2,C_FA=2,C_FR=1,V=1 => WrongPayout=FA/2, Loss=FA+FR/2",
        },
    }, indent=2))


if __name__ == "__main__":
    main()
