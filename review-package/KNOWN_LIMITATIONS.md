# Known limitations and unresolved concerns

## Mathematical scope

- T3 is conditional on known likelihoods, conditional independence, lottery
  timing, neutral utility, fixed calibration, and the declared six-action
  class.
- T4 freezes H01 peers and proves a local best-response interval. It is not a
  global equilibrium theorem.
- T5 is exhaustive only for pure stationary branch actions and the five
  declared preference vectors `000`, `100`, `010`, `001`, and `111`. It does
  not cover mixed, correlated, coalition-proof, sequential, participation,
  Sybil, or arbitrary heterogeneous `b in R^3` equilibria.
- Exact arithmetic establishes the result for the frozen finite model; it does
  not establish that the model describes a real milestone population.

## Empirical and operational scope

- `Z`, `X`, and `T` accuracies are synthetic assumptions. No 90% audit
  accuracy is presented as empirical evidence.
- Reviewer effort, audit cost, latency, conflicts of interest, collusion,
  creator evidence, and outside options have not been measured.
- The `b_i` interval is an analytical trust assumption. The mechanism does not
  enforce a bound on a reviewer’s external release preference.
- The frozen calibration table is not re-estimated under deviations or field
  distribution shift.
- The package has no blockchain, wallet, database, API, UI, settlement, or
  production integration.

## Novelty and review status

- The focused novelty audit finds adjacent prior art for each general
  ingredient. The separated dual-lottery architecture and exact gate boundary
  are candidate instance-level contributions; no priority claim is made.
- The package contains computationally independent checks, not an external
  human peer-review report.
- Submission readiness is not claimed. A broader literature search, author
  priority check, and independent mathematical referee review remain open.

## Reproducibility dependencies

- Central computations require only Python 3.12+ standard library and the
  files in this directory.
- Bibliography verification requires the primary URLs listed in
  `docs/CEAV_M1_BIBLIOGRAPHY_PRIMARY_CHECK.md`; network access is not needed
  for the numerical reproduction.
- The central dual-boundary certificate is duplicated under
  `frozen-boundary/certificate.json` and the historical path expected by the
  editorial audit. The package does not retrieve either copy from the parent
  checkout.
