# V4 research closeout implementation plan

> **For agentic workers:** Execute the approved research closeout inline with `superpowers:executing-plans`; use independent review at the end. This is a reference oracle, not a production analyzer.

**Goal:** Finalize V4.0's negative result and begin V4.1 with feasibility statements.
**Architecture:** Amend the research spec, then check fixed instances using an independent standard-library oracle. Keep every `ceav_m1` runtime path and UI unchanged.
**Tech Stack:** Python 3.12+, `Fraction`, `unittest`, Markdown.
**Spec:** `CEAV_M1_V4_CONDITIONAL_SPEC.md`, plus the user's approved three amendments.

## Global constraints and rulings

- Work only in this workspace; preserve unrelated V3.3/browser edits.
- No general equilibrium engine, UI, runtime model registration, parameter sweep, or production verification claim.
- The oracle imports no production math; expected numbers are derived in spec F01.
- Every evidence run uses a new directory, pins source/spec bytes, and refuses overwrite.
- A research closeout snapshot made after the oracle is not implementation-start preregistration.
- Ruling: keep the supplied untracked spec and focused new reference files in the current checkout. This avoids relocating or integrating the user's unrelated dirty work; do not commit or push.

## Review focus

- Zero effort cost and zero lambda retain ties, not false strict equilibria.
- Flipping every report preserves reward but reverses decision quality.
- Imbalanced strata use `n_z-1` in finite scores and distinct population/batch weights.
- Oracle success must retain negative research results and finite-check scope.
- Existing output directories and pinned bytes must remain intact.

## Task 1 — Finalize the mathematical contract

- [ ] Amend `CEAV_M1_V4_CONDITIONAL_SPEC.md` to revision r2: quantified all-Low proposition, label-inversion proposition, and explicit batch/population cost formulas.
- [ ] Write `CEAV_M1_V4_1_FEASIBILITY.md`: define orientation target, scalar claim-level audit, necessary effort/budget/quality conditions and stop rules. No study grid or implementation.
- [ ] Verify equations and terminology against the existing model and original V4 source note.

## Task 2 — Independent fixed-fixture oracle

Files: `verification/oracle_v4.py`, `tests/test_v4_research_oracle.py`.
Interfaces: `realized_score(public, reports, judge, task)`, `branch(z, profile, lam=1, cost=1/20)`, `run_checks()`, `write_run(out)`.
`branch` integrates only the documented F01 signals; it is not a general config/analyzer API.

- [ ] Write tests first for finite score, six deviations/ties, F01 quality, inversion, import independence, and immutable pinned outputs.
- [ ] Run `python -m unittest tests.test_v4_research_oracle -v`; retain the expected RED log.
- [ ] Implement the minimum oracle with direct finite likelihood sums, no covariance shortcut for expected score.
- [ ] Run the same suite; require discovered tests, no skips, and zero failures.
- [ ] Run `python verification/oracle_v4.py --out results/<new-run>` and retain `all_low_persists_without_audit` with honest scope metadata.

## Task 3 — Evidence and closeout

- [ ] Obtain independent mathematical/code review; repair material findings and rerun affected checks.
- [ ] Record oracle scope in the spec separately from full-engine status; verify local Markdown links and source hashes.
- [ ] Create a fresh research closeout snapshot with actual UTC timestamp and raw hashes, explicitly `preregistered=false` and `implementation_start=false`.
- [ ] Check unchanged hashes for pre-existing dirty files. Report evidence paths and outstanding full-engine work as out of scope.

## Execution ledger

- Initial inspection: V4 r1 is untracked; V3.3/browser files have unrelated dirty edits. No V4 oracle exists.
