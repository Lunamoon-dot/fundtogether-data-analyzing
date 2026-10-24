# CEAV-M1 V3.3 final closeout

- **Scope:** CEAV-M1 V3.3 IPW audit reward only.
- **Verification status:** **VERIFIED** for the declared local verification plan and pinned synthetic/assumption model.
- **Mechanism/payoff scope:** no mechanism/payoff or research-gate criteria were changed during this closeout. Changes are acceptance routing, artifact rendering, mutation assertions, and release-evidence wiring.
- **Implementation/evidence commit:** `3ec3121`.
- **Evidence/report commit:** `7a48400197cfb5dc2a688d3ed075d4101dacdbf4`.

## Evidence gates

| Gate/evidence | Result |
| --- | --- |
| IPW-T01–T13 | 13/13 pass |
| IPW-B01 | pass; real browser flow, UI, worker run and artifact parity |
| IPW-M01–M10 | 10/10 killed; isolated mutation copies; production bytes unchanged |
| V1 regression | 47/47 pass |
| V2 regression | 15/15 pass |
| V3.3 regression | 13/13 pass |
| Full suite | 123 pass, 0 fail, 0 error, 0 skipped, 0 not_run |
| IPW study | 54/54 points complete; every point has 432/432 branch candidates |

The final full-suite artifact is [full-suite/test_results.json](full-suite/test_results.json). Its manifest pins the source files used by the run.

## IPW-B01 browser acceptance

Browser scenario: `IPW-B01`, Chromium 156.0.4314.42, local server port 8771.

The real Playwright flow selected `ceav-m1-v3.3`, checked the hybrid mechanism, exposed `q0`, `q1`, `q_min`, IPW mode and reward budget, reopened a succeeded worker run, fetched `/api/runs/run-20261023T233141-ee9de97be5/artifacts/ipw.json`, and compared UI values against the artifact. It checked 54 points, 3 policies × 18 points, 432 candidates per point, exact policy results, metrics, failure witness, disclaimer text and JavaScript errors.

Acceptance artifact: [browser-ipw/browser_results.json](browser-ipw/browser_results.json). The worker artifact was produced by the real UI worker path and is retained locally at `results/run-20261023T233141-ee9de97be5/ipw.json`; the raw file is too large for a normal GitHub file. The checked-in projection is [ipw_public.json](ipw_public.json).

## 54-point study and negative result

The declared grid has three policies: symmetric `q0=q1=1/2`, report-1 `q0=1/4,q1=3/4`, and report-0 `q0=3/4,q1=1/4`; pi is `{3/10, 1/2, 7/10}`, verification-anchor quality is `{4/5, 9/10, 19/20}`, and high-effort-cost multiplier is `{1, 6/5}`.

All three policies are exactly **0/18 robust**. This is a policy failure result, not an analyzer failure:

| Policy | Pass/total | Failure reasons over its 18 points | Worst accuracy | Worst false approval | Worst wrong payout | Worst false rejection | Worst cash review cost |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| symmetric | 0/18 | cash 18; false approval 6; false rejection 6 | 42379/50000 | 2237/5000 | 6711/50000 | 38/125 | 257829/50000 |
| report-1 | 0/18 | cash 18; false approval 6; false rejection 6 | 42379/50000 | 2237/5000 | 6711/50000 | 38/125 | 521183/100000 |
| report-0 | 0/18 | cash 18; false approval 6; false rejection 6 | 42379/50000 | 2237/5000 | 6711/50000 | 38/125 | 261799/50000 |

Study gates remain unchanged: max cash review cost 4, max false approval 1/5, max false rejection 1/4, max wrong payout 3/20. No policy passes the declared worst-case gate.

Raw worker artifact SHA-256: `c51009e33eded1942d19b00c132320ef88e2c705bf26a0bc78584b89919e9001`. Public projection SHA-256: `935e38fb19d8b1c17bded9521b00cd61ad4921892644057eef448e5221cdf9e0`.

## Historical six-failure investigation

The old all-suite run [results/v33-all-tests-20261024T055304](../v33-all-tests-20261024T055304) reported 117 pass / 6 fail:

- T32: no current-source B09 browser evidence;
- V2-T14: no current-source V1 regression evidence;
- V2-T15: no current-source browser/mutation registry evidence;
- CAL-T07: no current-source CAL-B01 evidence;
- CAL-T08: no current-source V1/V2 regression evidence;
- INC-T08: no current-source INC-B01 evidence.

These were stale or absent evidence manifests, not skipped tests and not V3.3 payoff failures. Browser scenarios and regression/mutation runs were regenerated on the clean pinned snapshot, their manifests were checked against current source hashes, and the full runner was rerun. The final full suite now passes 123/123 with no skipped or not-run records.

## Mutation evidence

V3.3 mutation results are in [v3_3-mutations/mutation_results.json](v3_3-mutations/mutation_results.json): IPW-M01 through IPW-M10 are all `killed`, including the closeout probes for “all uncertainty points are required” and “invalid-budget points remain visible”. V2 release mutation evidence is retained at [v2-mutations/mutation_results.json](v2-mutations/mutation_results.json), 9/9 killed.

## Known limitations

- `q0,q1` are per-Judge audit probabilities.
- Uncertainty ranges are assumptions, not confidence intervals.
- Only pure strategies are evaluated.
- Participation, collusion, Sybil concentration, stake/slashing and appeals are out of scope.
- Audit does not change the already computed decision or payout.
- V3.2 baseline comparison is marked same-budget rerun required/reference-only in the artifact.
- Latency is not modeled.
- The study is synthetic/assumption data and is not evidence about real Judges or production deployment.

`VERIFIED` here means all declared local gates and evidence checks passed. It does not mean the mechanism is economically successful: the exact result is that no tested IPW policy is robust on the declared grid.
