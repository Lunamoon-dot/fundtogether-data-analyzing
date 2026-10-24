# CEAV-M1 manuscript v0.2 editorial and consistency closeout

Date: 2026-10-24

Branch: `research/v6-rave-phase01`

Frozen study: `dual-purpose-strategic-boundary-r1`
Decision: **editorial correction complete; evidence and model unchanged**

This report reviews manuscript v0.1, records the metric and bibliography
corrections, and maps v0.2 claims to immutable evidence. It does not create a
mechanism version, alter frozen parameters, rerun historical studies, or
expand the equilibrium grid.

## 1. Scope and immutable inputs

The reviewed baseline is commit `58f2e0d`, containing manuscript v0.1,
theorem catalog, novelty audit, and the exact dual-boundary certificate. The
certificate is read-only in this closeout.

| Input | Identity |
|---|---|
| frozen configuration | `configs/dual_boundary.json`; SHA-256 `17001d4aabcc971bd29b68a690d5d6b26e0c4c9c41be5670d60e1cac19d9cce5` |
| exact certificate | `results/dual-strategic-boundary-20261024T0524070523492Z/analysis/certificate.json`; SHA-256 `fde3ad4745b37e270469aaec2692a51c83cbcf5db7fcb0a16938296a6e25b7d5` |
| boundary analyzer | `verification/dual_boundary.py`; SHA-256 `8c943bb2f6f23c5032768dd60834f9e926a1d6aa3f83205482b54f4a645d6d0b` |
| independent potential-state oracle | `verification/dual_boundary_oracle.py`; SHA-256 `bab19a553f73be9d843c0e199dd66b3ef2d0c25ab918f2e9b81dc8d9e4e4d3a9` |
| independent completeness audit | `verification/dual_boundary_audit.py`; SHA-256 `35dcbcf243ba20ba4d2f3fe0d7258de73667f5c012bc6b2807d271d916c0a6e9` |

The new editorial audit is
[`verification/manuscript_editorial_audit.py`](verification/manuscript_editorial_audit.py).
It asserts the certificate hash before reading metrics.

## 2. Priority 1: metric definition correction

### Finding in v0.1

The manuscript correctly stated `FA=P(D=1|Y=0)` and `FR=P(D=0|Y=1)`, but
then wrote “Decision loss is `2*FA+FR`.” That expression treats conditional
probabilities as joint probabilities and is inconsistent with the declared
prior `pi=1/2`.

### Correct definitions in v0.2

```text
FA = P(D=1 | Y=0)
FR = P(D=0 | Y=1)
WrongPayout = V * P(Y=0,D=1)
Loss = C_FA * P(Y=0,D=1) + C_FR * P(Y=1,D=0)
```

With `pi=P(Y=1)=1/2`, `C_FA=2`, `C_FR=1`, and `V=1`:

```text
P(Y=0,D=1) = FA/2
P(Y=1,D=0) = FR/2
WrongPayout = FA/2
Loss = 2*(FA/2) + 1*(FR/2) = FA + FR/2
```

The historical theorem catalog already used the corrected form. No
certificate or historical report was changed.

### Full metric audit

The audit iterates every equilibrium row in both mechanisms and all five
declared scenarios. It checked 80 rows:

```text
WrongPayout == FA/2
Loss == FA + FR/2
```

All 80 rows pass exactly as `Fraction` values. It then checks every numerical
table reproduced in v0.2 against the immutable certificate:

| v0.2 table or claim | Immutable location | Result |
|---|---|---|
| frozen `g0/g1` calibration table | `configs/dual_boundary.json:g0_by_z_and_report_sum`, `g1_by_z_and_report_sum` | match |
| neutral Selective and Uniform baseline | `certificate.json:mechanisms.{selective,uniform}.scenarios.neutral.equilibria`, All-H01 profile | match |
| positive `b=1/10` witness | `certificate.json:mechanisms.{selective,uniform}.scenarios.symmetric.equilibria`, `(H01,H01,H01)/(L1,L1,H01)` | match |
| negative boundary witness | same symmetric equilibrium arrays, `(L0,H01,H01)/(H01,H01,H01)` | match |
| local H01 intervals | `scenarios.symmetric.all_h01_closed_equilibrium_interval` | match |
| all-pure safe components | `scenarios.symmetric.safe_component_containing_zero` | match |
| 4,320 branch candidates, 466,560 profiles, 5,590 checks | `manifest.json:independent_audit` and certificate scope | match |

The T3 values `M_L=33/50`, `M_H=37/50`, `delta=2/25`, and effort gap
`7/500` are algebraic Fraction results from the independent proof-review
runner; they are not empirical measurements and are not altered by this
editorial pass.

## 3. Priority 2: bibliography integrity

The corrected metadata is recorded in
[`CEAV_M1_BIBLIOGRAPHY_PRIMARY_CHECK.md`](CEAV_M1_BIBLIOGRAPHY_PRIMARY_CHECK.md)
and used in v0.2.

| Entry | Correct metadata | Primary verification |
|---|---|---|
| Boutilier 2012 | Craig Boutilier. “Eliciting Forecasts from Self-interested Experts: Scoring Rules for Decision Makers.” AAMAS 2012, pp. 737–744. | [author PDF](https://www.cs.toronto.edu/~cebly/Papers/Boutilier_aamas12.pdf) |
| Chen et al. 2023 | Siyu Chen, Jibang Wu, Yifan Wu, Zhuoran Yang. “Learning to Incentivize Information Acquisition: Proper Scoring Rules Meet Principal-Agent Model.” ICML 2023, PMLR 202, pp. 5194–5218. | [PMLR record](https://proceedings.mlr.press/v202/chen23ah.html) |
| Zarkoob et al. 2020 | Hedayat Zarkoob, Hu Fu, Kevin Leyton-Brown. “Report-Sensitive Spot-Checking in Peer-Grading Systems.” AAMAS 2020, pp. 1593–1601. | [primary PDF](https://www.ifaamas.org/Proceedings/aamas2020/pdfs/p1593.pdf) |

The v0.1 errors were editorial only: Boutilier’s title was wrong, Chen et
al.’s title and author initials were wrong, and Zarkoob et al.’s title was
shortened. No unsupported DOI was added.

## 4. Claim-to-evidence map

| Claim family | v0.2 location | Proof or certificate | Independent computational check |
|---|---|---|---|
| conditional metric identities | §4 | algebra from the declared `pi`, `C_FA`, `C_FR`, `V` | `manuscript_editorial_audit.py`, 80 rows |
| payment factorization and effort threshold | Proposition 1 | complete proof in v0.2; theorem catalog §4 | `independent_t3_t5_review.py` T3 |
| neutral feasibility | Proposition 2 | theorem catalog §4 and synthesis memo §6 | proof-review runner; fixed parameter tests |
| local external-interest boundary | Proposition 3 | certificate `local_deviations` and interval report | proof-review runner T4; `tests.test_dual_boundary` |
| pure-equilibrium quality boundary | Proposition 4 | certificate scenario intervals and safe components | 5,590-check independent audit; 466,560 profiles |
| positive and negative witnesses | §6 | certificate symmetric equilibrium rows | editorial audit exact witness assertions |
| novelty and bibliographic claims | §§2, References | primary-source notes and URLs | human-source metadata check; not a mechanism certificate |

The computational checks are independent source-code checks, not external
human peer review. No external human reviewer has reviewed this manuscript.
The repository’s `verification/DUAL_BOUNDARY_INDEPENDENT_REVIEW.md` is an
independent computational derivation, not a human referee report.

## 5. Editorial changes in v0.2

- Added conditional definitions of FA and FR.
- Added joint-probability definitions for wrong payout and decision loss.
- Derived `WrongPayout=FA/2` and `Loss=FA+FR/2` for the frozen prior and loss
  weights.
- Replaced the incorrect v0.1 loss expression.
- Re-stated the frozen action class, calibration, lottery timing, and gates.
- Added proposition numbering and complete finite proofs or exact certificate
  references for the T3–T5 claims.
- Added exact neutral, positive-witness, and negative-witness tables.
- Corrected the three bibliography entries from primary records.
- Added a claim-to-evidence map and separated computational checks from human
  peer review.

The original `CEAV_M1_MANUSCRIPT_V0_1.md` remains unchanged for comparison.
The new draft is [`CEAV_M1_MANUSCRIPT_V0_2.md`](CEAV_M1_MANUSCRIPT_V0_2.md).

## 6. Verification commands and stop-condition result

```text
python -X utf8 -m verification.manuscript_editorial_audit
python -X utf8 -m verification.independent_t3_t5_review
python -X utf8 -m unittest tests.test_dual_boundary -v
```

The editorial audit passes, the independent proof runner passes, and the
focused ten-test boundary suite passes. No V7, parameter retuning, historical
study rerun, new synthetic finding, or equilibrium-grid expansion was made.

The closeout result is **editorially consistent draft v0.2; submission
readiness remains unclaimed**.
