"""Deliberately fail on the manuscript's printed T4 stability condition."""
from fractions import Fraction as F
from pathlib import Path

root = Path(__file__).resolve().parents[2]
for name in ("CEAV_M1_MANUSCRIPT_V0_2.md", "review-package/docs/CEAV_M1_MANUSCRIPT_V0_2.md"):
    text = (root / name).read_text(encoding="utf-8")
    printed = (
        "Z=0,L0: -7/500 -(633/5000)b_i >= 0,",
        "Z=1,L1: -7/500 +(551/6250)b_i >= 0.",
    )
    if not all(row in text for row in printed):
        raise RuntimeError("The reviewed proof bytes changed: " + name)
    # At b=0 both printed gains equal -7/500. H01 is stable precisely when
    # a deviation cannot improve utility, hence gain <= 0, strictly < 0 here.
    gain = -F(7, 500)
    print(f"{name}: b=0, deviation_gain={gain}, printed_gain_ge_0={gain >= 0}, correct_gain_lt_0={gain < 0}")
raise AssertionError("Confirmed proof transcription error: both stability inequalities must use <= 0 (strict < 0 in the interior)")
