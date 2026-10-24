# CEAV-M1 V5.0 Phase 1 Feasibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freeze the V5.0 AGIIS research assumptions and produce an exact, independent feasibility certificate for shifted incremental Brier and direct Brier scoring without building a production engine.

**Architecture:** Keep the model in research documents and implement a standalone finite-sum oracle plus a small feasibility analyzer. The oracle imports no production evaluator; tests pin algebraic identities, exact fixtures, budget bounds, payment bounds, and failure witnesses. Results are written to a new immutable artifact directory with source/spec hashes.

**Tech Stack:** Python 3.12 standard library, `fractions.Fraction`, unittest, Markdown, JSON.

**Spec:** `CEAV_M1_V5_INFORMATION_SCORING_SPEC.md` and `CEAV_M1_V5_FEASIBILITY.md`.

## Global Constraints

- Use exact `Fraction` arithmetic; decimals are display-only.
- Do not import production evaluators into the independent oracle.
- Keep historical V3/V4 conclusions and artifacts unchanged.
- Do not build CLI/API/UI/blockchain integration in Phase 1.
- Preserve all negative feasibility witnesses; do not tune gates, budget, or costs to force a pass.
- Distinguish target-population and batch-average cost weights.
- Do not claim global optimality from a finite policy grid.

## Review Focus

- Posterior is for noisy `T`, and label orientation must be calibrated to `Y`; test both mappings.
- Strict high effort requires `mu*q*Delta > c`, with equality retaining Low/High tie.
- Shifted incremental and direct Brier have different reserve caps and cash floors.
- Noise attenuation must equal `d^2` exactly, including asymmetric sensitivity/specificity.
- `q=0`, `q=1`, `mu=0`, zero Delta, and invalid budget boundaries must remain explicit.

### Task 1: Freeze V5.0 research inputs and prior-art boundary

**Files:**
- Create: `spec_history/v5.0-agiis-phase1-implementation-start-20261024/` pinned spec/design/source copies and `MANIFEST.json`
- Create: `CEAV_M1_V5_INFORMATION_SCORING_SPEC.md`
- Create: `CEAV_M1_V5_FEASIBILITY.md`
- Create: `references/V5_INFORMATION_SCORING_SOURCES.md`

- [ ] Copy the pasted task into the repository’s V5 spec with explicit status `SPECIFIED`, model boundary, P5-1/P5-2 propositions, fixtures, payment variants, stop gates, and limitations.
- [ ] Record primary-source notes for proper scoring and information acquisition, separating known results from CEAV derivations.
- [ ] Pin raw bytes and SHA-256 hashes for spec, source note, relevant V4.1 inputs, and the task assumptions in the freeze manifest.
- [ ] Verify the manifest hashes against the copied bytes before coding.

### Task 2: Independent exact oracle

**Files:**
- Create: `verification/oracle_v5.py`
- Test: `tests/test_v5_feasibility.py`

Interfaces:
- `posterior_y(...) -> Fraction`
- `posterior_t(...) -> Fraction`
- `conditional_delta_y(...) -> Fraction`
- `conditional_delta_t(...) -> Fraction`
- `proper_score_expectation(...) -> Fraction`
- `payment_bounds(...) -> dict[str, Fraction]`
- `fixture_metrics(name: str) -> dict`

- [ ] Write failing tests for strict propriety, calibration/noise identity, exact F51-01/F51-02 values, and V3-HET branch values.
- [ ] Implement finite binary enumeration from primitive likelihoods only; do not import V4/V3 evaluators.
- [ ] Add direct Brier and shifted incremental effort-gain/cap calculations with exact boundaries.
- [ ] Run focused tests and retain a red/green record if applicable.

### Task 3: Feasibility analyzer and certificates

**Files:**
- Create: `verification/feasibility_v5.py`
- Modify: `tests/test_v5_feasibility.py`

- [ ] Test F51-01/F51-02 infeasibility under V5.0-A, direct-Brier cap differences, V3-HET per Judge×Z thresholds, and target/batch cost separation.
- [ ] Implement deterministic analyzer output for A and B, with no continuous grid claim.
- [ ] Add explicit witnesses for strict-H impossibility and equality ties.
- [ ] Validate with `python -m unittest discover -s tests -p 'test_v5_feasibility.py'`.

### Task 4: Immutable Phase 1 evidence

**Files:**
- Create: `results/v5-feasibility-<timestamp>/` reports, JSON certificates, command log, and manifest
- Create: `verification/mutation_probes_v5.py`
- Test: `tests/test_v5_mutations.py`

- [ ] Run the analyzer once into a fresh directory; reject overwrite if it exists.
- [ ] Add mutation probes for `d^2`, strict `>`, cost subtraction, cap coefficient, target weights, and baseline-vs-report posterior.
- [ ] Run focused tests, mutation probes, and `python -O` validation.
- [ ] Publish a Phase 1 conclusion: proceed only if a meaningful feasible candidate remains; otherwise stop V5.0-A and record the bounded negative result.
