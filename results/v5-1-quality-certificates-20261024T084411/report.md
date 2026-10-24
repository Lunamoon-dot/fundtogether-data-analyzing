# CEAV-M1 V5.1 — Phase 1.5 certificates

Parent commit: 2835559652b912536439c5b504da30ba68c91436

All values below were computed with exact Fraction arithmetic by the independent finite-state oracle.

## F51-02 baseline comparison

| Policy | Equilibrium effort/action | Accuracy | FA | FR | Wrong payout | Cap | Audit exposure | Expected cash |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Direct Brier | (('H', 'H'), ('H', 'H'), ('H', 'H')) | 112/125 | 13/125 | 13/125 | 13/250 | 6 | 3/5 | 434007/147250 |
| Binary audit-only | (('H01', 'H01'), ('H01', 'H01'), ('H01', 'H01')) | 112/125 | 13/125 | 13/125 | 13/250 | 6 | 1/2 | 111/50 |

Finding: Direct Brier is strictly dominated by binary audit-only on the declared exposure and cash metrics, with identical decision quality.

## V3-HET Direct Brier witness

Equilibrium effort: (('H', 'H'), ('L', 'L'), ('L', 'L')); decision rule: {0: 'Z', 1: 'Z'}.
Accuracy 7/10, FA 2/5, FR 1/5, wrong payout 1/5, expected cash 4609871/1171875.
The witness has D=Z, but its quality values are not a quality-gate pass.

## Budget-feasibility bound

B at Z=0 needs s >= 155/98 for weak high-effort optimality; equality is the tie ('L', 'H') and strict induction needs s > 155/98.
Cheapest threshold tie resolution (('H', 'H'), ('L', 'L'), ('L', 'L')) costs 14998033/3675000 > cash gate 4. Resolving B high at the tie costs 15145033/3675000.
This lower bound is scoped to the fixed V3-HET Direct Brier environment and does not rule out other scoring rules or environments.

## Decision

NO-GO for Direct Brier Phase 2. No larger Direct Brier screening study is justified by these certificates; future work would need a different incentive/scoring hypothesis or an explicitly changed environment.
