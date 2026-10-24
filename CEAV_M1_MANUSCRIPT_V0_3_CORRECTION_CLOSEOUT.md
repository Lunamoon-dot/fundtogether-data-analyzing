# CEAV-M1 — Manuscript v0.3 Correction Closeout

Date: 2026-10-25 (Asia/Saigon). Branch: `research/v6-rave-phase01`.
Correction baseline: commit `15387a7b5606154e72739ff71cad45564b0a021b`.
Status: **VERIFIED editorial closeout; ready for external academic review
within the declared conditional research scope.**

## Scope and versioning

This closeout resolves only the confirmed F1–F5 findings and the requested
scope/Proposition 1 clarifications. The active draft is
[manuscript v0.3](CEAV_M1_MANUSCRIPT_V0_3.md), with the synchronized
[Research Brief v0.3](CEAV_M1_EXTERNAL_RESEARCH_BRIEF.md).
Manuscript v0.2, the domain audit, previous audit snapshots and all frozen
mathematical evidence remain historical records. No game, mechanism,
parameter, gate, strategy class or equilibrium study is changed.

## Finding disposition and prose inspection

The correction pass inspected the affected propositions, abstract, model,
verification section, bibliography, brief and active claim map. This is a
scoped agent inspection, not external human peer review or a new general audit.

| Requirement | Correction in active documents | Disposition |
|---|---|---|
| F1, T4 proof | Proposition 3 defines `Delta U=U(deviation)-U(H01)`. Weak stability requires every gain `<=0`; strictness requires every nonself gain `<0`. Both Selective displayed rows have the corrected sign and equivalent endpoint bounds. | RESOLVED; exact checks below. |
| F2, names | Reference 4: Xi Alice Gao. References 6–7: Yuqing Kong. Reference 6: Katrina Ligett. The primary-name addendum records the bylines and sources. | RESOLVED; primary records rechecked on 2026-10-25. |
| F3, T5 explanation | Brief §4 explains coexistence of three bad strict pure Nash equilibria and a locally strict All-H01 equilibrium at `b=1/10`. Each candidate is checked against unilateral deviations; no coordination process is inferred. | RESOLVED by scoped prose inspection. |
| F4, audit architecture | Abstract, model §3.3 and brief §3 state independent random draws, conditionally independent events given locked `(Z,r)`, common `T` on either event, final decision using `g1` on their union, and bonus eligibility only on `A_pay`. | RESOLVED; existing primitive oracle and focused regression remain the numerical evidence. |
| F5, attribution | Manuscript §8/§9, brief §6, package claim map and reproduction guide distinguish primitive calculations, supplied-row arithmetic, stored-certificate checks and prose inspection. | RESOLVED by source tracing and prose inspection. |
| General-purpose scope | Manuscript §1 and brief §1 define FundTogether's general-purpose decentralized crowdfunding scope, charity as optional, and the school-desk study as one physical-acceptance exemplar. | RESOLVED; no empirical or decentralization guarantee added. |
| Self-contained Proposition 1 | Reward formula, fixed coin law, joint independence from reporting information and future `T`, lock timing, randomization restriction, risk-neutral utility, effort information/cost and permitted report maps are explicit. | RESOLVED; the original factorization and effort threshold are unchanged. |

The [bibliography addendum](CEAV_M1_BIBLIOGRAPHY_PRIMARY_CHECK.md#v03-byline-correction-addendum--2026-10-25)
cites the [Gao accepted manuscript](https://dspacemainprd01.lib.uwaterloo.ca/server/api/core/bitstreams/2cf2eab2-324c-402f-98eb-ee05f2a446f4/content),
the [Kong–Ligett–Schoenebeck author record](https://mail.schoeneb.people.si.umich.edu/papers/PeerFocal.html)
and the [Kong–Schoenebeck official publisher record](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITCS.2018.13).
Only the identified metadata was rechecked; no broader priority search was opened.

## T4 neutral and boundary checks

For every Judge in both frozen mechanisms, the correction checker obtains
deviation-minus-H01 intercepts/slopes from the existing independent
potential-state oracle. It checks all five nonself actions in both branches,
compares the displayed Selective rows with those calculations, and intersects
the local linear constraints. The existing result intervals remain:

| Mechanism | Strict interval | Neutral maximum nonself gain | Gain maximum at either endpoint |
|---|---|---:|---:|
| Selective | `(-70/633,175/1102)` | `-7/500` | `0` |
| Uniform | `(-218750/2070709,218750/1365587)` | `-7/500` | `0` |

Thus neutral H01 is strict; at either endpoint it is weak with a binding tie.
At a rational point immediately outside each endpoint, a positive gain
confirms loss of the best-response property. These are 30 declared local
diagnostic cases across both mechanisms and all three Judges, not a new
global equilibrium study. T3's `7/500`, T5's safe components, negative
witnesses and every baseline/witness metric table are preserved.

## Verification attribution and evidence

- `dual_boundary_oracle.py` calculates primitive signal/audit payoffs; DB02
  derives calibration and DB03 compares 864 branch utility/metric rows.
- `independent_t3_t5_review.py` derives T3 modal matches, divides hardcoded
  T4 binding rows, then invokes the independent completeness audit for T5.
  Its supplied-row division alone is not a derivation or proof inspection.
- `manuscript_editorial_audit.py` checks the frozen hash, 80 stored metric
  reductions and named expected values; it does not read manuscript prose.
- `manuscript_correction_checks.py` checks the displayed T4 signs against
  primitive utilities and selected editorial conditions. The root invocation
  compares active manuscript/brief/bibliography package copies after only
  relative-link adjustments. It does not certify arbitrary prose proofs.
- This closeout's scoped inspection checks the mathematical sign convention,
  self-comparison exception, independence statement, unilateral-equilibrium
  explanation, bylines and evidence attribution in context.

New evidence is stored in
[the closeout run](results/manuscript-correction-closeout-20261024T191947409255Z/manifest.json).
Historical certificates are read-only; no certificate regeneration is required.

Fresh execution results (Python 3.12.10):

| Check | Result |
|---|---|
| Existing certificate metric checker, root and standalone package | PASS; 80 stored equilibrium rows each. |
| Existing independent T3–T5 runner, root and standalone package | PASS; 5,590 checks, 4,320 branch candidates and declared coverage of 466,560 full profiles; exact values unchanged. |
| Existing focused suite, root normal and `-O` | 10 tests discovered and executed in each run; 10/10 pass in each. |
| Existing focused suite, standalone package | 10 tests discovered and executed; 10/10 pass. |
| Scoped correction checker, root normal and `-O` | 88 checks each; all 30 local boundary cases pass; active manuscript/brief/bibliography copies agree after relative-link adjustment. |
| Scoped correction checker, standalone package | 85 checks; PASS. The three root/package comparisons apply only to the root invocation. |
| Standalone source origins and reviewer summary | Imports resolve inside the copied package with `PYTHONPATH` removed; summary preserves four pure equilibria, three bad, at `b=1/10`. |
| Historical preservation | All 8,084 protected tracked source/evidence files retain their baseline raw hashes. |

All 12 recorded commands exited zero. The central certificate remains
`fde3ad4745b37e270469aaec2692a51c83cbcf5db7fcb0a16938296a6e25b7d5`.
The final document checks, source identities and link results are recorded in
[final validation](results/manuscript-correction-closeout-20261024T191947409255Z/publication-validation.json).
No full V1–V6 regression suite, browser flow, empirical study or new equilibrium
study is claimed by this editorial closeout.

## Remaining findings and review readiness

**No F1–F5 finding remains unresolved in the active v0.3 documents.** The
reported errors remain visible in preserved historical v0.2 and audit snapshots;
those are not the active reviewer draft. No mathematical contradiction was
discovered that requires a mechanism change.
The pre-existing limits remain: synthetic likelihoods and conditional
independence, trusted noisy `T`, unmeasured cost/participation/interests,
pure stationary equilibrium scope, no creator/settlement guarantees, and open
novelty priority. These are not claimed resolved by an editorial correction.

**External academic review readiness: YES**, for a conditional finite-game
theory/counterexample paper with the stated limitations. Submission
novelty, empirical validation, production readiness and external human review
remain unestablished. This task stops at the correction and its commit; it
does not authorize V7 or another mechanism study.
