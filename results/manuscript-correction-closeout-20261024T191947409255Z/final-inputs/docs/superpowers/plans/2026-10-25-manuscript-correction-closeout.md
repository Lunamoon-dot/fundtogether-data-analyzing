# Manuscript Correction Closeout Plan

> **For agentic workers:** Execute this limited editorial plan inline. The user has explicitly requested implementation and a resulting commit; no new model or general audit is authorized.

**Goal:** Resolve audit F1–F5 and the two requested scope/assumption clarifications in manuscript v0.3 and the active Research Brief.

**Architecture:** Preserve v0.2, the audit at commit `15387a7`, all snapshots and frozen evidence. Publish v0.3 and synchronize the package using only its existing relative-link adjustments.

**Tech Stack:** Markdown and Python 3.12 standard-library verification.

**Spec:** User's Manuscript Correction Closeout request; `CEAV_M1_DOMAIN_DEPENDENCE_AUDIT.md` §5 at commit `15387a7`.

## Global Constraints

- No change to game, mechanism, parameters, gates, strategy class or T3–T5 values.
- No V7, new mechanism, equilibrium expansion, production changes or general audit.
- Preserve raw bytes of historical audit snapshots and frozen certificates.
- Keep reviewer-package numerical execution independent of the parent checkout.
- Commit the scoped correction and report external-review readiness and open limitations.

## Review Focus

- Deviation-minus-base signs: weak `<=0`, strict `<0` for every nonself deviation; ties at endpoints.
- Payment-coin independence is joint with reporting information and future `T`.
- `T` informs the decision on the union, including payment-only audits.
- Hardcoded binding-row arithmetic and certificate metrics do not inspect prose or derive primitive payoffs.
- Historical v0.2 stays available; active reviewer links consistently select v0.3.

## Tasks

- [x] Create `CEAV_M1_MANUSCRIPT_V0_3.md`: correct F1/F2/F4/F5, self-contained Proposition 1, general-purpose scope and physical-study exemplar; preserve the result tables.
- [x] Update `CEAV_M1_EXTERNAL_RESEARCH_BRIEF.md`: version 0.3, F3/F4/F5 and scope; add primary-name addendum to bibliography note.
- [x] Synchronize manuscript/brief/bibliography package copies; update active READMEs, claim map and reproduction guide.
- [x] Add a narrowly scoped correction checker for neutral/endpoints, document conditions and copy synchronization. Use the existing independent primitive oracle; do not edit numerical analyzers.
- [x] Run existing metric checks, independent T3–T5 runner and focused tests normally/under `-O`; run packaged commands and local correction checker. Save logs in a new immutable run directory.
- [x] Write and package `CEAV_M1_MANUSCRIPT_V0_3_CORRECTION_CLOSEOUT.md`: map each finding, record evidence and readiness, retain unresolved empirical/novelty limits.
- [x] Inspect diff and raw-byte preservation; commit only the correction files. Stop after reporting the commit and review-readiness decision.
