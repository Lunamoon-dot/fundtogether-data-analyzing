# V6 Phase 1 — final negative certificates

**NO-GO_declared_phase1_candidates**

Four exogenous Gate-B winners each have a certified bad pure equilibrium.
These are post-discovery targeted counterexamples; no exhaustive search ran.

| Fixture | Policy | Maximum regret | Exposure | FA | FR | Cash | Failure |
|---|---|---:|---:|---:|---:|---:|---|
| F51-01 | Q1-zero | 0 | 1 | 1/20 | 1/20 | 211/100 | exposure |
| F51-01 | Q2-z1 | 0 | 1/2 | 1 | 0 | 283/200 | fa, wrong_payout |
| F51-02 | Q1-zero | 0 | 1 | 11/250 | 77/500 | 199/100 | exposure |
| F51-02 | Q2-z0 | 0 | 1/2 | 77/6250 | 2321/3125 | 247/200 | fr |

Each witness checks 36 unilateral actions with frozen peers/policy and the independent potential-state oracle. One bad NE refutes an all-NE requirement; it does not determine the total equilibrium count or worst metric over the whole class.

The primary GO_candidate_discovery_only remains a truthful decision-feasibility result. This negative certificate supersedes its recommendation for further screening. No game/policy/gate was tuned, no historical artifact was changed, and no general RAVE impossibility is claimed.
