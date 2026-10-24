# V6 RAVE Phase 0–1 — exact feasibility

Synthetic assumptions; exogenous H01 discovery is not equilibrium success.
Phase 2: **GO_candidate_discovery_only**. C/D remain not run.

## Matched-exposure comparison

| Fixture | Allocation | Exposure | Selective loss | Uniform loss | Selective cash | Uniform cash | Gates at H01 | Candidate |
|---|---|---:|---:|---:|---:|---:|---|---|
| F51-01 | Q1-zero | 12/25 | 441/12500 | 12129/312500 | 597/625 | 741/625 | True | True |
| F51-01 | Q1-floor | 61/100 | 1347/40000 | 181623/5000000 | 13339/10000 | 15067/10000 | False | False |
| F51-01 | Q2-z0 | 1/2 | 1061/25000 | 3843/100000 | 247/200 | 247/200 | True | False |
| F51-01 | Q2-z1 | 1/2 | 1721/50000 | 3843/100000 | 247/200 | 247/200 | True | True |
| F51-02 | Q1-zero | 12/25 | 219/3125 | 17151/156250 | 597/625 | 741/625 | True | True |
| F51-02 | Q1-floor | 61/100 | 219/3125 | 62403/625000 | 13339/10000 | 15067/10000 | False | False |
| F51-02 | Q2-z0 | 1/2 | 633/6250 | 1353/12500 | 247/200 | 247/200 | True | True |
| F51-02 | Q2-z1 | 1/2 | 72/625 | 1353/12500 | 247/200 | 247/200 | True | False |
| V3-HET | Q1-zero | 407/800 | 5819/100000 | 7166863/80000000 | 105193/80000 | 24743/16000 | False | False |
| V3-HET | Q1-floor | 2021/3200 | 5819/100000 | 26155789/320000000 | 535579/320000 | 118229/64000 | False | False |
| V3-HET | Q2-z0 | 2/5 | 10659/100000 | 12067/125000 | 323/250 | 32/25 | True | False |
| V3-HET | Q2-z1 | 3/5 | 737/10000 | 41877/500000 | 879/500 | 177/100 | False | False |

## Required Phase-1 answers

1. **Equal exposure:** see exact table and decision_loss_improvement in certificate; positive values are allocation benefits under calibrated exogenous reports only.
2. **Attribution:** no_audit_bayes vs B0_no_audit_majority isolates aggregation-rule benefit. Selective vs matched uniform uses identical g0/g1; their difference isolates allocation.
3. **Noisy T:** posterior odds multiply by sens_T/(1-spec_T) when T=1, or (1-sens_T)/spec_T when T=0 (here 9 or 1/9). Decisions change only when this crosses threshold 2/3. Unanimous evidence can rationally override T.
4. **Manipulation:** disagreement-only auditing with all-copy-Z has a profitable Low contrarian deviation. F51-02 gain=17/50 at mu=1,b=0; F51-01=7/50. This seeks an audit. Exposure changes for every six-action deviation are preserved.
5. **Copy-Z:** Q1-zero has exposure zero and retains unanimous-but-wrong cases (F51-02 FA=FR=3/10). It is not a neutral equilibrium there because dissent earns bonus. Its failure as an equilibrium does not remove the reporting-distortion concern; uniform/Q2 copy-Z witnesses are checked separately.
6. **Reporting bias:** paying only audited agreement can reward dissent even without private information. Certificates keep actual candidate utility and all deviations, rather than calling H01 truthful in equilibrium.
7. **Cash/payment:** costs include all reviewer bonuses and one kappa charge per claim audit, with undiscounted 3f+3mu reserve. Table reports positive/negative economic outcomes separately. Incentive-adjusted economic viability remains unproved.
8. **Candidate:** a candidate requires lower decision loss, no higher cash and all declared H01 gates; see meaningful_candidate fields. This is the sole Gate-B rule, fixed before output.
9. **Residual risks:** real auditor provenance/correlated error/capture, distribution estimation, strategic Creator evidence, reviewer participation, latency, coordinated/mixed/history strategies and calibration fixed points are not modeled. The labelled b=1/10 and copyZ-calibration diagnostics are not a robustness sweep.
10. **Decision:** GO_candidate_discovery_only; a future request may open only the justified strategic study. No Phase 2 ran here. The finite decision comparison and audit-seeking counterexample are reproducible in certificate.json.

## Strategic scope and failure witnesses

Each allocation and its matched uniform baseline has 5 targeted profiles, each checked against all 6 deviations for each Judge/Z (36 options/profile), first b=0 then the separate b=1/10 diagnostic. This is not 216-profile exhaustive search. Worst metrics/counts are explicitly limited to witnessed equilibria; overall equilibrium count and worst-equilibrium gates are not computed.

- F51-01: no-audit majority loss 39/250; no-audit Bayes loss 6/125; aggregation improvement 27/250.
  - Q1-zero / selective: 1 witnessed equilibria; total count not computed.
  - Q1-zero / matched_uniform: 1 witnessed equilibria; total count not computed.
  - Q1-floor / selective: 1 witnessed equilibria; total count not computed.
  - Q1-floor / matched_uniform: 1 witnessed equilibria; total count not computed.
  - Q2-z0 / selective: 2 witnessed equilibria; total count not computed.
  - Q2-z0 / matched_uniform: 1 witnessed equilibria; total count not computed.
  - Q2-z1 / selective: 2 witnessed equilibria; total count not computed.
  - Q2-z1 / matched_uniform: 1 witnessed equilibria; total count not computed.
- F51-02: no-audit majority loss 39/250; no-audit Bayes loss 183/1250; aggregation improvement 6/625.
  - Q1-zero / selective: 0 witnessed equilibria; total count not computed.
  - Q1-zero / matched_uniform: 1 witnessed equilibria; total count not computed.
  - Q1-floor / selective: 0 witnessed equilibria; total count not computed.
  - Q1-floor / matched_uniform: 1 witnessed equilibria; total count not computed.
  - Q2-z0 / selective: 0 witnessed equilibria; total count not computed.
  - Q2-z0 / matched_uniform: 1 witnessed equilibria; total count not computed.
  - Q2-z1 / selective: 0 witnessed equilibria; total count not computed.
  - Q2-z1 / matched_uniform: 1 witnessed equilibria; total count not computed.
- V3-HET: no-audit majority loss 18/125; no-audit Bayes loss 1221/10000; aggregation improvement 219/10000.
  - Q1-zero / selective: 0 witnessed equilibria; total count not computed.
  - Q1-zero / matched_uniform: 0 witnessed equilibria; total count not computed.
  - Q1-floor / selective: 0 witnessed equilibria; total count not computed.
  - Q1-floor / matched_uniform: 0 witnessed equilibria; total count not computed.
  - Q2-z0 / selective: 0 witnessed equilibria; total count not computed.
  - Q2-z0 / matched_uniform: 0 witnessed equilibria; total count not computed.
  - Q2-z1 / selective: 0 witnessed equilibria; total count not computed.
  - Q2-z1 / matched_uniform: 0 witnessed equilibria; total count not computed.
