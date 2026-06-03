# Opus 4-8 Cross-Generation Robustness — Summary

Pre-registered: `experiments/opus48_crossgen/protocol.md`.
Framing: cross-GENERATION agreement WITHIN the Claude family (not cross-vendor).

4-8 usable verdicts: 227 / 227. Pairs with heuristic: 227.

## H0-heuristic: weighted kappa(4-8, heuristic)

- weighted kappa = **0.465** (95% CI [0.395, 0.543]), PABAK = 0.339
- Band: kappa in [0.40, 0.60] — consistent with the original trio band (moderate IRR).

## H0-crossgen: weighted kappa(4-8, each original model)

Original trio pairwise baseline: 0.812-0.857.

| pair | n | weighted kappa | 95% CI | PABAK | band |
|---|---|---|---|---|---|
| 4-8 ↔ haiku | 225 | 0.857 | [0.801, 0.907] | 0.820 | stable |
| 4-8 ↔ sonnet | 227 | 0.877 | [0.821, 0.926] | 0.855 | stable |
| 4-8 ↔ opus | 227 | 0.847 | [0.796, 0.897] | 0.802 | stable |

- Cross-generation verdict: **generation-stable** — 4-8 joins the intra-family convergence (all pairings ≥ 0.75).

## A1 (primary discriminator): convergent-disagreement join

- 59-paper convergent-disagreement set (trio agreed among themselves AND differed from heuristic).
- 4-8 verdict **matches the trio consensus exactly**: **59/59** (100%)
- 4-8 verdict merely **differs from heuristic** (weaker test): 59/59 (100%)
- A1 verdict: **generation-stable** — 4-8 independently lands on the same off-heuristic verdict (≥50/59).

## A2: disagreement-set Jaccard (4-8 vs trio-majority)

- |{4-8 ≠ heuristic}| = 100, |{trio-majority ≠ heuristic}| = 90
- intersection = 87, union = 103, **Jaccard = 0.845**
- High Jaccard ⇒ moderate kappa reflects disagreement on the SAME papers (real shared signal). Low Jaccard at similar kappa ⇒ original convergence partly coincidental.

## A3: contamination difference-in-differences

- 4-8: kappa_pre(≤2024, n=184) = 0.505, kappa_post(2025+, n=43) = 0.311, delta = -0.193
- 4-7: kappa_pre(≤2024, n=184) = 0.588, kappa_post(2025+, n=43) = 0.317, delta = -0.271
- **DiD = +0.077**
- A3 verdict: |DiD| < 0.15 — no contamination signature; 4-8's post/pre pattern matches 4-7's.
- Caveat: n_post = 43 is small; post kappa and DiD have wide CIs. Descriptive/directional, not a significance test.

## Structural limit (A4)

4-8 differs from 4-7 on TWO confounded axes: capability (newer) and contamination exposure (later cutoff). The DiD (A3) only partially isolates contamination. This design cannot fully separate the two; the result is reported with that limit explicit.

## Headline

- H0-heuristic: kappa(4-8, heuristic) = 0.465 — kappa in [0.40, 0.60]
- H0-crossgen: **generation-stable** — 4-8 joins the intra-family convergence (all pairings ≥ 0.75).
- A1: 4-8 matches trio consensus on 59/59 convergent papers — generation-stable
- A2: Jaccard = 0.845
- A3: DiD = +0.077 — |DiD| < 0.15

**This is footnote-scope supplementary evidence, not a headline result. It does not move the audit from inter-rater reliability toward validity (4-8 is also a non-validated rater). The original 2026-05-21 audit summary is unchanged.**