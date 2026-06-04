# Prompt-Robustness of the Cross-Model Convergence — Summary

Pre-registered: `experiments/prompt_robustness/protocol.md`.
Tests the PROMPT half of shared-method-variance (Tier B, feasible slice).

Convergent-disagreement papers: 59. Models: haiku, sonnet. Variants: reword, lenient.

## Flip rates (variant verdict ≠ original 2026-05-21 verdict)

| variant | tier | n | flips | flip_rate | toward-inclusion / flips |
|---|---|---|---|---|---|
| reword | haiku | 59 | 4 | 0.068 | 1/4 |
| reword | sonnet | 59 | 2 | 0.034 | 1/2 |
| lenient | haiku | 59 | 27 | 0.458 | 27/27 |
| lenient | sonnet | 59 | 13 | 0.220 | 13/13 |

## Primary statistic

- flip_rate(V_reword)  = **0.051** (6/118) — noise-floor control
- flip_rate(V_lenient) = **0.339** (40/118) — adversarial pro-inclusion
- **Δ = +0.288**

- Noise-floor check: noise floor acceptable (reword 0.051 < 0.40).

- Verdict: **0.15 ≤ Δ < 0.40 — partial prompt-sensitivity.** The convergence is partly, but not mostly, prompt-induced.

## Directional check (V_lenient flips)

- Of 40 lenient flips, **40 (100%) move toward MORE inclusion** (Exclude→Maybe/Include, Maybe→Include).
- A genuine leniency effect is near-100% directional. Non-directional flips are noise.

## Survival under adversarial prompt

- Papers where BOTH models keep their original off-heuristic verdict under V_lenient: **28/59** (47%).

## Structural limit (honest)

This tests ONLY the prompt component. Even a fully-robust result does not rule out shared training-lineage artifact — all conditions still use Claude models. Resolving that needs a non-Claude rater (cross-vendor, blocked by the Claude-only decision + missing keys) or human gold (deferred). Reported as the prompt-half of the shared-method-variance question only.

## Headline

- flip_rate reword=0.051, lenient=0.339, **Δ=+0.288** — 0.15 ≤ Δ < 0.40
- lenient flips toward inclusion: 40/40
- both-model survival under adversarial prompt: 28/59