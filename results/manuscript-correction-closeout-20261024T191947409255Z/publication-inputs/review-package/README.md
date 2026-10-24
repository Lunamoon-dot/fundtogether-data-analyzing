# CEAV-M1 external academic review package

This directory is a self-contained reproduction bundle for the frozen
CEAV-M1 dual-purpose strategic-boundary study. It is an academic review
package, not a new mechanism, production implementation, or submission
decision.

The active reviewer draft is [manuscript v0.3](docs/CEAV_M1_MANUSCRIPT_V0_3.md),
with the synchronized [Research Brief](docs/CEAV_M1_EXTERNAL_RESEARCH_BRIEF.md).
The [v0.3 correction closeout](docs/CEAV_M1_MANUSCRIPT_V0_3_CORRECTION_CLOSEOUT.md)
resolves audit F1–F5 and records verification and remaining review limits.
`docs/CEAV_M1_MANUSCRIPT_V0_2.md` is retained as a historical draft with the
reported errors; use v0.3 for review.

The package preserves the certified values for:

- the neutral T3 effort gap `7/500`;
- the Selective and Uniform T4 local H01 intervals;
- the T5 symmetric all-pure quality components;
- the four pure equilibria at symmetric `b=1/10`, including three bad
  witnesses; and
- the neutral Selective-versus-Uniform baseline comparison.

All computation uses Python 3.12+ standard library and exact
`fractions.Fraction` arithmetic. No package dependency reaches into the
parent repository when commands are run from this directory.

## Contents

```text
configs/dual_boundary.json                 frozen study configuration
verification/                              analyzer, independent oracle, audits
tests/                                     focused 10-test verification suite
frozen-boundary/                           immutable certificate copies and hashes
figures/                                    four generated reviewer-facing PNG diagrams
docs/                                      brief, manuscript, theorem, novelty and limitation notes
```

`frozen-boundary/certificate.json` is the central immutable certificate. Its
SHA-256 is:

```text
fde3ad4745b37e270469aaec2692a51c83cbcf5db7fcb0a16938296a6e25b7d5
```

The copy under
`results/dual-strategic-boundary-20261024T0524070523492Z/analysis/` exists
only because the original editorial audit uses that historical path. The two
copies are byte-identical. The package also includes the parent synthesis and
V6 negative certificates referenced by the theorem catalog.

The three Markdown files at the package root are byte-identical compatibility
snapshots for `dual_boundary.py`'s historical source-hash routine. They are not
additional evidence and are not needed by the four standard replay commands;
the reviewer-facing, link-corrected copies are under `docs/`.

## Reproduce

Open a terminal in this directory and run:

```text
python -X utf8 -m verification.manuscript_editorial_audit
python -X utf8 -m verification.independent_t3_t5_review
python -X utf8 -m verification.review_summary
python -X utf8 -m unittest tests.test_dual_boundary -v
python -X utf8 -m verification.manuscript_correction_checks
```

Expected results are documented in
[`REPRODUCTION_GUIDE.md`](REPRODUCTION_GUIDE.md). The first command checks
all 80 equilibrium metric rows against the certificate and verifies the
conditional reductions; it does not read manuscript prose. The second derives
T3 from primitive probabilities, checks supplied hardcoded T4 binding rows,
and invokes the independent completeness audit for T5. DB01–DB03 compare
local boundaries, calibration and primitive-oracle branch payoffs. The summary
prints every pure equilibrium active at `b=1/10` and both neutral baselines.
The unittest command runs ten focused tests. The v0.3 correction command
checks local T4 neutral/endpoint conditions and selected editorial conditions;
it does not replace the numerical suite or prose inspection.

## Evidence and limitations

- [`CLAIM_EVIDENCE_MAP.md`](CLAIM_EVIDENCE_MAP.md) maps every central claim to
  a proof, source file, certificate JSON path, or independent audit.
- [`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md) records strategy-class,
  empirical, novelty, and environment limitations.
- The package does not claim that an external human review has occurred.
- External bibliography URLs are provided for source verification; the
  numerical reproduction itself does not require network access.
- The original historical certificates are copied without modification.
