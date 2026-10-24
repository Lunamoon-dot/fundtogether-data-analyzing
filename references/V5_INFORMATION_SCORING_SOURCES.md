# V5 information-scoring source boundary

This note records primary sources reviewed for Phase 1. It separates established results from CEAV-M1 derivations.

## Primary sources

1. Gao, Wright, and Leyton-Brown, *Incentivizing Evaluation with Peer Prediction and Limited Access to Ground Truth*, Artificial Intelligence 2019, DOI `10.1016/j.artint.2019.03.004`; author repository: <https://uwspace.uwaterloo.ca/items/19ea8bc1-f265-48d7-8ce4-8591b86a928a>. The paper studies costly evaluation, low-cost signal equilibria, and limited noisy ground truth. It motivates keeping all-Low/copy-signal counterexamples explicit; it does not prove the V5 quadratic formulas.
2. Witkowski, Atanasov, Ungar, and Krause, *Proper Proxy Scoring Rules*, AAAI 2017, DOI `10.1609/aaai.v31i1.10590`; <https://ojs.aaai.org/index.php/AAAI/article/view/10590>. The paper develops proxy scoring and a quadratic proxy rule. It is prior art for scoring with a proxy signal, not a novelty claim for Brier scoring or baseline subtraction here.
3. Chen, Wu, Wu, and Yang, *Learning to Incentivize Information Acquisition: Proper Scoring Rules Meet Principal-Agent Model*, ICML/PMLR 2023; <https://proceedings.mlr.press/v202/chen23ah.html>. The paper models an agent choosing costly information acquisition and reporting under a principal-chosen scoring rule. V5 uses its problem boundary as related work; the finite conditional-variance and budget certificates are CEAV derivations.
4. Gneiting and Raftery, *Strictly Proper Scoring Rules, Prediction, and Estimation*, JASA 2007, DOI `10.1198/016214506000001437`. This is the foundational reference for proper scoring rules. The binary Brier strict-propriety identity used by V5 is proved directly in the V5 oracle rather than imported as an engine assumption.

## What is known versus derived here

- Known: quadratic/Brier scores are strictly proper for the event being scored; proxy scoring can use an appropriate noisy proxy; costly information acquisition is a principal-agent problem; limited noisy ground truth can alter effort incentives.
- Derived for CEAV-M1: `E[S(p,T)|I]=constant-(p-p*)^2`, `Delta_i(z)=E[(p_H-p_L)^2|Z=z]`, the noisy-audit identity `Delta_T=d^2 Delta_Y`, the V5.0-A and Direct-Brier reserve caps, and all F51/V3-HET exact fractions.
- Not claimed: that any cited paper proves CEAV-M1 equilibrium selection, the FundTogether quality gates, label orientation for `Y`, or a global policy optimum.

