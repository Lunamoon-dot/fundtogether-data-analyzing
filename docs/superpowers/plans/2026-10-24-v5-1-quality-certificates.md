# CEAV-M1 V5.1 Phase 1.5 Quality Certificates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Certify the exact decision quality, expected cash cost, best responses, and budget lower bound for the declared Direct Brier witnesses against a strong binary audit-only baseline.

**Architecture:** Add a standalone finite-state oracle that reconstructs the F51-02 and V3-HET signal distributions independently from the Phase 1 evaluator. It enumerates effort ties, proper probability forecasts, deterministic votes, majority metrics, rewards, and target-population cash costs; it does not modify Phase 1 code or build an engine.

**Tech Stack:** Python 3.12 standard library, `fractions.Fraction`, unittest, JSON/Markdown artifacts, SHA-256 manifests.

**Spec:** User-provided V5 Phase 1.5 task and `CEAV_M1_V5_INFORMATION_SCORING_SPEC.md`.

## Global Constraints

- Preserve commit `2835559` and all existing V5 Phase 1 artifacts.
- Use exact `Fraction` arithmetic and independent finite-state enumeration.
- Keep historical quality gates and target-population cash accounting unchanged.
- Include every optimal-response tie; equality is not strict induction.
- Do not build full V5 engine, API, UI, or production integration.
- Scope impossibility claims to Direct Brier on the fixed V3-HET assumptions.

## Review Focus

- Forecasts are posteriors for noisy `T`, while votes are deterministic calibrated posteriors for `Y`.
- Direct and binary payments have the same realized cap here but different expected payout formulas.
- Conditional FA/FR and unconditional wrong-payout probability must not be conflated.
- The B threshold `s=155/98` is a weak tie; strict induction requires `s>155/98`.
- The V3-HET lower bound must choose the cheapest tie resolution before claiming impossibility.

### Task 1: Freeze Phase 1.5 assumptions and certificate contract

**Files:**
- Create: `CEAV_M1_V5_1_DECISION_QUALITY_CERTIFICATES.md`
- Create: `spec_history/v5.1-phase1.5-implementation-start-20261024/` with pinned inputs and `MANIFEST.json`

- [x] Record the three certificates, fixed policies, gates, tie rules, and bounded conclusion.
- [x] Pin commit hash, Phase 1 spec, V3-HET config, and source assumptions with raw SHA-256 hashes.
- [x] Verify freeze hashes before implementation.

### Task 2: Independent finite-state quality oracle

**Files:**
- Create: `verification/oracle_v5_1_quality.py`
- Test: `tests/test_v5_1_quality_certificates.py`

- [x] Write failing tests for F51-02 forecasts/votes/efforts/costs, V3-HET efforts/decision/cost, and the B threshold.
- [x] Enumerate `(Y,Z,X_A,X_B,X_C,T)` directly from likelihoods; do not import production evaluators.
- [x] Implement direct-Brier and binary-audit reward expectations, all effort ties, calibrated votes, and majority metrics.

### Task 3: Immutable certificate runner

**Files:**
- Create: `verification/v5_1_quality_certificates.py`
- Create: `verification/mutation_probes_v5_1.py`
- Create: `results/v5-1-quality-certificates-<timestamp>/`
- Create: `results/v5-1-quality-mutations-<timestamp>/`

- [x] Produce exact JSON/Markdown certificates and the V3-HET lower-bound witness.
- [x] Add mutations for the majority threshold, forecast target, error-side, and reward expectation.
- [x] Hash all inputs/outputs and reject artifact overwrite.

### Task 4: Verification and decision

- [x] Run focused tests in normal and optimized Python modes.
- [x] Verify every artifact hash and preserve unrelated dirty work.
- [x] Report GO/NO-GO for Direct Brier Phase 2; propose larger screening only if a real unresolved opportunity remains.
