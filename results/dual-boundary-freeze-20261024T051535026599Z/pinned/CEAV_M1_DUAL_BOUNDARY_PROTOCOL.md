# Dual-purpose strategic boundary: fixed study protocol

Status: SPECIFIED. This is a bounded extension of the parent research memo,
not a model version, parameter search, or change to historical evidence.
The configuration in `configs/dual_boundary.json` freezes the F51-02 point.
The protocol was written after the local affine calculation, before writing
the new interval analyzer; it is not retrospective preregistration.

## Fixed game and timing

Conditional on binary Y, Z, the three potential private X signals, and T are
independent, with symmetric accuracies 7/10, 4/5, and 9/10 respectively.
The prior is 1/2. Each Judge sees Z, chooses Low or pays 1/20 for X, then
locks a binary report. The six plans are L0,L1,H00,H01,H10,H11. No lottery
outcome or T is observed before locking. The independent A_pay coin has
probability 2/5. A_dec has probability 1/6 only on Z=0,sum(reports)=2 for
Selective, or 19/1250 everywhere for Uniform. Either coin reveals the same
T once. R_i=2*A_pay*1(report_i=T); utility also includes b_i*D_final.
The reward reserve is 6. All original gates and costs remain fixed.

H01 calibration is frozen at posterior release threshold 2/3. Bayes odds
before T are (3/7 if Z=0 else 7/3)*4**(2*k-3), k=sum(reports).
T=1 multiplies odds by 9; T=0 divides by 9. The stored tables are those
rules evaluated once, including the specified >= tie rule. Actual strategy
changes never recalibrate them. Quality gates constrain the designer, not
players' permitted deviations.

## Exact method and completeness contract

For each mechanism, Z and all 6**3=216 branch profiles, calculate the
conditional neutral utilities c_i and common release slope s. At scenario
vector v in {000,100,010,001,111}, the candidate defeats a focal deviation iff

    c_i(candidate)-c_i(deviation)
      + b*v_i*(s(candidate)-s(deviation)) >= 0.

Intersect all 18 closed half-lines (including each self deviation). Reject
an interval only for an exact contradiction. Retain singleton intervals,
all equalities, all six actions and asymmetric profiles. A full stationary
pure equilibrium exists exactly when the two branch equilibrium intervals
intersect: P(Z=z)>0 and each contingent branch action can deviate separately.
This product argument covers all 216**2=46,656 full profiles per scenario.
There are no cross-branch budget constraints on players.

Partition the entire real b line at all endpoints of nonempty full-profile
intervals. Report both singleton endpoints and intervening open intervals,
including unbounded tails. On each cell the complete equilibrium set is
constant by the affine-inequality proof. No dense numerical grid, truncation,
interpolation or floating-point tolerance is used. An empty equilibrium set
is explicitly NO_PURE_EQUILIBRIUM and never robustness success.

Metrics integrate actual equilibrium reports under the target distribution,
not calibration weights: FA=P(D=1|Y=0), FR=P(D=0|Y=1), wrong payout=FA/2,
loss=FA+FR/2, cash=expected total rewards+(1/4)*P(A_pay union A_dec).
Record metricwise maxima and their full-profile witnesses; maxima need not
come from the same equilibrium. Gate pass requires existence and every
equilibrium passing all six original gates. Local All-H01 stability is a
separate claim from uniqueness and from worst-equilibrium quality.

## Evidence plan

DB01: exact local gaps, slopes, breakpoints and all Judge positions.
DB02: independently derive frozen tables from primitive Bayes probabilities.
DB03: compare every branch profile's metrics and utilities with an independent
Fraction oracle enumerating potential X,T and the two separate audit coins.
DB04: all 216 candidates, all Judges and all six deviations in each branch;
closed interval intersections, singleton ties, tails and branch products.
DB05: original neutral witness and baseline numbers; endogenous exposure/cash.
DB06: direct oracle deviation checks at every cell, all intervals' boundaries,
and independent nearest-global-boundary derivation.
DB07: mutation probes for payment on union, double audit cost, recalibration,
peer changes, lost ties, skipped Low/asymmetry, or reversed b slope.
DB08: immutable new output directory, pinned raw inputs/source, source and
output hashes, normal/-O test discovery, deterministic pinned replay.

Focused tests and the oracle precede analyzer implementation. A dated freeze
event will identify the actual available bytes. Hash identity is distinct
from mathematical correctness. No V1-V6 source/result edits, new version,
merge, production implementation or broader uncertainty study is authorized.

## Scope of conclusions

All real b is a sensitivity parameter for the declared one-biased and
symmetric scenarios, not an empirical estimate. Strict response against
All-H01 does not prove unique equilibrium. Pure equilibrium enumeration does
not cover mixed strategies, correlated recommendations, collusion, Sybils,
participation, history-dependent behavior or auditor manipulation. T quality,
cost, lottery independence and unobservability before reporting are trust
assumptions. Distinguish STRATEGIC_FAILURE at modest b from a nonempty robust
neighborhood around zero, if both occur. Do not retune the witness.
