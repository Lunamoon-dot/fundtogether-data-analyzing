# T3–T5 mathematical and domain-dependence audit

Date: 2026-10-25. Independently inspected checkout: `research/v6-rave-phase01`, HEAD `de9368c128c0c258cd2174f9958c771215596bb0`.

Scope: skeptical mathematical review of the theorem catalog, manuscript v0.2, frozen dual-boundary configuration/certificate, analyzer, potential-state oracle, and proof-review runner. This note is the only file created by this audit. No source, model, parameters, manuscript, or frozen evidence were modified. Existing domain-audit conclusions were not used as mathematical evidence.

## Verdict

**No fundamental mathematical flaw or counterexample to the stated T3/T4/T5 theorem conclusions was found within the declared game.** The analytic neutral region and finite boundary results survive direct exact recalculation. One concrete mathematical transcription error exists in the manuscript proof: its two local stability inequalities have the wrong comparison sign. This requires correction before publication, but does not invalidate the correctly signed catalog or implementation.

This verdict is conditional on the model's assumptions. It does not establish portability of numerical boundaries, real-world applicability, mixed-equilibrium guarantees, empirical validity, or priority over prior work.

## Concrete finding M1: reversed inequalities in manuscript Proposition 3

Location: `CEAV_M1_MANUSCRIPT_V0_2.md:308-320`, specifically lines 312–313.

The manuscript displays

```text
Z=0,L0: -7/500 -(633/5000)b_i >= 0,
Z=1,L1: -7/500 +(551/6250)b_i >= 0.
```

These expressions are **deviation utility minus H01 utility**. To certify H01 as a weak best response they must be `<= 0`; strict stability uses `< 0`. At `b_i=0`, both displayed expressions equal `-7/500`, contradicting the displayed `>= 0` while H01 is strictly optimal. Taken together, the manuscript's printed inequalities require both `b_i<=-70/633` and `b_i>=175/1102`, so their intersection is empty.

The catalog has the correct `<= 0` conditions at `CEAV_M1_THEOREM_AND_COUNTEREXAMPLE_CATALOG.md:358-374`. The implementation uses candidate-minus-deviation inequalities `>=0` at `verification/dual_boundary.py:127-150`; its signs are correct. The theorem's published numerical interval is also correct. Classification: a real proof-presentation error, with no detected error in the underlying finite theorem or certificate. No fix was applied because the requested audit is read-only outside this note.

## Independently checked mathematics

### T3a: general factorization, and the actual information incentive

For `R_i=f+mu*A_pay*1{r_i=T}`, conditional joint independence of the payment coin from the reporting information and future audit gives

```text
E[R_i | I,r] = f + mu*a*P(T=r | I).
```

The report must depend only on the permitted information and independent randomization. Optimizing the modal match probability gives `mu*a*(M_H-M_L)-c_i`, and High can ignore X, so `M_H-M_L>=0` before effort cost. The decision mechanism and peer reports drop out only when `b_i=0` and no other report-dependent utility is present. This validates the catalog's quantifiers at `CEAV_M1_THEOREM_AND_COUNTEREXAMPLE_CATALOG.md:196-231`.

The standalone Proposition 1 restatement at `CEAV_M1_MANUSCRIPT_V0_2.md:232-250` mentions independence from reporting information without restating independence from T. Independence from information alone would not prove factorization. However, the actual model explicitly requires independence from future T at manuscript lines 151–158, and the catalog requires it at lines 196–200. This is therefore an opportunity to make the restatement self-contained, not a counterexample to the specified game.

This is a modal-label incentive; it is not an elicitation theorem for subjective probabilities. The manuscript correctly limits that interpretation at lines 264–265.

### T3b: nonempty analytic region, not interpolation

Direct enumeration of `(Y,Z,X_A,X_B,X_C,T)` with exact `Fraction` weights, independently of analyzer payoff helpers, reproduced:

| Quantity | Exact result |
|---|---|
| Best Low match, both z branches | `33/50` |
| H01 match, both z branches | `37/50` |
| H10 match | `13/50` |
| Information value for the match payment | `2/25` |
| Minimum H01 neutral gap at `a=2/5,mu=2` | `7/500` |
| `P(S)` at H01 | `57/625` |
| Overall `E[VOI]` | `477/6250` |
| `VOI(S)` | `47/95` |

The full independent neutral gaps against `(L0,L1,H00,H10,H11)` are:

```text
z=0: (7/500, 27/100, 8/125, 48/125, 8/25)
z=1: (27/100, 7/500, 8/25, 48/125, 8/125)
```

These utilities are peer-independent. H01 is uniquely optimal for every Judge/branch when `a>5/16`; that proves uniqueness of the pure equilibrium without assuming truthful behavior. The posterior modal report really is X in this environment, including the X/Z disagreement cases. It would not hold for arbitrary signal likelihoods.

The direct state calculation also independently derived all affine coefficients in `(1,a,u)`:

```text
FA       = 23/625   - (24/3125)*a  + (21/3125)*u
FR       = 137/625  - (429/3125)*a - (324/3125)*u
Loss     = 183/1250 - (477/6250)*a - (141/3125)*u
Exposure = a + (57/625)*u
```

Thus `5/16<a<1/2`, `0<t<=(1/2-a)/(1-a)`, and `u=(1-a)t` imply pointwise union exposure at most `1/2`, reserve `3*mu=6`, expected cash `(111/25)*a+Exposure/4<469/200<4`, and the catalog's conservative FA/FR/wrong-payout bounds. These are algebraic inequalities throughout the displayed region; they are not extrapolations from the named point. Sources: catalog lines 233–288; parent synthesis memo lines 195–245.

At matched union exposure and the same H01 reports, the Uniform decision coin is `d_uniform=t*P(S)`. The directly derived loss advantage is

```text
Loss_Uniform-Loss_Selective
 = u*(57/625)*(47/95-477/6250)
 = u*(149061/3906250) > 0.
```

At the excluded boundary `a=5/16`, Low-copy-Z and H01 tie; the all-copy-Z profile indeed has `FA=FR=3/10` because the frozen tables ignore T at `(z=0,k=0)` and `(z=1,k=3)`. This validates the strictness counterexample in catalog lines 303–310. It is already part of the stated analysis, not a newly introduced mechanism.

### T4: local best response, including heterogeneous interests

The analyzer enumerates every Judge, branch, and retained action at `verification/dual_boundary.py:97-106`; all 864 branch metric tables across both mechanisms match the independent potential-state oracle. Intersecting the five nonself deviations in both branches reproduces:

| Mechanism | Exact strict local interval for each `b_i` |
|---|---|
| Selective | `(-70/633,175/1102)` |
| Uniform | `(-218750/2070709,218750/1365587)` |

All-H01 is therefore strict when all coordinates lie in that mechanism's interval. Other Judges' interests do not enter a focal best response once their H01 strategies are fixed. Endpoint ties and immediate profitable deviations outside are retained. This is a local result; it does not imply uniqueness or quality at other equilibria. Catalog lines 337–391 states this distinction correctly.

The smaller all-peer bound `|b_i|<7/500` is valid: the neutral gap is at least `7/500` against all peer profiles, and any unilateral release-probability difference has absolute value at most one. This is a sufficient dominance box, not an exact heterogeneous global boundary.

### T5: all-real scalar coverage of the declared scenarios

In addition to running the supplied audit, I reconstructed equilibrium intervals using **only** `dual_boundary_oracle.evaluate` as the primitive evaluator and separately written bound collection, branch products, gate calculation, and nearest-bad-interval logic. That independent reconstruction did not call the subject analyzer's solver, full-equilibrium builder, cell builder, or safe-component routine. Results:

| Mechanism/scenario | Profiles ever NE over all b | Open safe component containing zero |
|---|---:|---|
| Selective neutral | 1 | all real b |
| Selective one_A/one_B/one_C, each | 5 | `(-70/633,+infinity)` |
| Selective symmetric | 24 | `(-70/633,175/1922)` |
| Uniform neutral | 1 | all real b |
| Uniform one_A/one_B/one_C, each | 5 | `(-218750/2070709,+infinity)` |
| Uniform symmetric | 24 | `(-218750/2070709,109375/1189451)` |

The union of equilibrium intervals covers all real b in every scenario. Every finite safe endpoint has an existing bad weak equilibrium, so exclusion is justified. At symmetric `b=1/10`, both mechanisms have four pure equilibria and all four are strict; Selective has three bad equilibria plus All-H01. The catalog's explicit counterexample and distinction between local truthfulness and global quality are valid (catalog lines 403–490).

Branch factorization is justified by positive branch probabilities and independently permitted contingent choices, with no player-level cross-branch constraint. Solving 4,320 branch candidate systems therefore covers 466,560 full profiles algebraically; it does not mean 466,560 full payoff tables were independently evaluated. All six deterministic plans are necessary and sufficient for a best response with a binary private signal and the specified observations. A randomized unilateral mixture cannot improve on every pure plan because expected utility is linear in that mixture. **This does not enumerate mixed-strategy equilibria**, which remain outside the theorem.

## M / P / A / G / E separation

| Axis | Supported conclusion | Boundary |
|---|---|---|
| M — mathematical validity | T3 factorization and neutral-region proof are valid under their assumptions; T4/T5 exact finite conclusions independently reproduce. | Correct manuscript proof signs; no proof-assistant certification or external human review was conducted. |
| P — portability | The factorization and affine-deviation method can apply to another domain with the same information/payoff structure. | Fractions, thresholds, risk class, posterior modes, frozen decisions, and gates are specific to the declared signal model. They do not transfer merely by renaming escrow milestones as another task. |
| A — applicability | The model cleanly distinguishes independent payment eligibility from decision-audit selection. | An application must substantiate trusted T, likelihoods/conditional independence, lottery secrecy/independence, effort cost, commitment to the fixed decision table, and its chosen external-interest utility. `b_i` here values any release, not a state-contingent fraud payoff. |
| G — generality | An analytic `(a,t)` neutral region and all-real scalar b results for five specified vectors are proved. | Not arbitrary heterogeneous `b in R^3`, mixed/correlated equilibria, collusion, participation, adaptive calibration, auditor manipulation, or mechanism-wide impossibility. |
| E — empirical validity | Exact synthetic calculations and reproducibility are established. | No reviewer/auditor measurements, estimated b distribution, real-world error calibration, or field equilibrium selection is established by these artifacts. |

The source itself declares synthetic signal assumptions (`CEAV_M1_MANUSCRIPT_V0_2.md:112-115`), external-interest interpretation (lines 178–185), exclusions (lines 366–367), and the absence of empirical/production proof (lines 452–454). Domain dependence limits transport and interpretation; it is not by itself a refutation of a correctly quantified conditional mathematical result.

The implementation is intentionally fixed-instance code: it assumes the symmetric prior in conditional weights (`verification/dual_boundary.py:57-65`), uses half weights and literal reserve six in aggregation (lines 158–165), and the independent oracle hardcodes the frozen probabilities and coins (`verification/dual_boundary_oracle.py:35-58`). This is appropriate for the frozen certificate; changing a JSON field alone would not establish a valid new model analysis.

## Commands, results, and provenance

Executed read-only commands:

```text
git status --short
git branch --show-current
git rev-parse HEAD
python -B -X utf8 -m verification.independent_t3_t5_review
python -B -X utf8 -m unittest tests.test_dual_boundary -v
python -B -X utf8 -   [two inline exact-recalculation scripts described below]
```

- Proof-review runner: exit 0; effort gap `7/500`; expected local and global fractions; independent audit **5,590 checks**, 4,320 branch candidates, declared 466,560 full-profile coverage, 864 oracle branch tables.
- Focused unittest suite: exit 0; **10 tests discovered and executed, 10 passed**, approximately 9.1 seconds. No zero-test or skipped-suite claim was used.
- Inline script 1: loaded the frozen manifest/certificate, SHA-256 checked it, compared all 12 manifest-pinned current source files with their expected hashes, and compared `subject.serial(subject.study())` against the entire frozen certificate object. All matched. The same inline calculation independently integrated the 64 binary signal states and derived all T3 coefficients and gaps above without calling subject payoff helpers.
- Inline script 2: rebuilt all interval bounds, full profile pairs, quality/resource gates, existence cells, nearest bad endpoints, and `b=1/10` strictness from `dual_boundary_oracle.evaluate` alone. All ten scenarios matched the table above; exit 0.
- All scripts used exact `fractions.Fraction`; no floats, stochastic sampling, clipping, or tolerance were used. `-B` prevented bytecode writes. No analyzer output directory was created.

Frozen certificate: `results/dual-strategic-boundary-20261024T0524070523492Z/analysis/certificate.json`.

```text
SHA-256 fde3ad4745b37e270469aaec2692a51c83cbcf5db7fcb0a16938296a6e25b7d5
Entire regenerated certificate JSON object equals frozen JSON object: True
All 12 source/config hashes listed in manifest equal current source bytes: True
```

The owning hashes are at the same directory's `manifest.json:3-21`; configuration and scope are at `configs/dual_boundary.json:5-18`. Hash equality establishes identity, while the independent derivations/oracle checks support correctness.

## Verification shortcomings and work not performed

- `verification/independent_t3_t5_review.py:64-82` hardcodes the two binding intercepts/slopes and verifies their division. Its T4 subsection alone is not a derivation from primitive probabilities, despite the manuscript's broad phrasing at lines 318–320. The actual independent arithmetic coverage comes from the oracle table comparison and the separate focused local-boundary test (`tests/test_dual_boundary.py:16-36`); these were run in this audit.
- That runner's T3 subsection (`verification/independent_t3_t5_review.py:50-61`) tests the named effort gap, not every analytic-region gate formula. The direct coefficient derivation in this audit addresses that gap.
- The supplied completeness audit compares fresh source calculations, not the frozen certificate bytes (`verification/dual_boundary_audit.py:25-69`). The complete object/hash replay above addresses possible stale evidence for this checkout.
- No full V1–V6 regression, browser acceptance, empirical audit, literature novelty audit, or independent human referee review was performed. None is necessary to establish the narrowly inspected T3–T5 arithmetic, and none is claimed by this note.
- No theorem is inferred for excluded assumptions or new mechanisms, and no parameter was retuned to make a gate pass.
