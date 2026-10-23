# V3.2 report-sensitive implementation plan

## Goal

Add a versioned report-sensitive spot-checking model while preserving V3.1 behavior and evidence.

## Steps and verification

1. Add the V3.2 spec, design, and verification plan; prepare an independent oracle, fixture, and red tests. Verify the red test fails because `ceav-m1-v3.2` is not yet supported.
2. Create the immutable implementation-start freeze containing the three docs plus the preexisting oracle, fixture, and red tests. Verify all manifest hashes.
3. Add `V32Config`, strict `q0/q1` validation, 64-state likelihoods, and model/version exports. Run V32-T01–T05.
4. Update evaluator and best-response logic to apply `q_r` analytically per Judge; add failure-witness decomposition. Run V32-T06–T08.
5. Expose a CLI study operation and run provenance; add API/UI wiring only where the existing V3.1 path requires it. Run V32-T10 and browser acceptance if exposed.
6. Run the complete V1/V2/V3/V3.1 regression suites and the V3.2 suite. Preserve logs and report exact metrics, failed gates, and limitations.

