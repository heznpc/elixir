# Eligible-Count Recount — heuristic 156 vs LLM-majority

No new API calls; re-analysis of the primary IRR audit verdicts (`llm_second_reviewer_results.csv`, 3 tiers x 227).

Records: 227.

## Eligible counts (Include + Maybe)

| screener / rule | eligible | % of 227 |
|---|---|---|
| heuristic (paper headline) | **156** | 69% |
| 3-model LLM majority | **82** | 36% |
| LLM strict (all 3 eligible) | 73 | 32% |
| LLM lenient (>=1 eligible) | 106 | 47% |
| 4-model majority (incl Opus 4-8) | 72 | 32% |

- Heuristic breakdown: {'Include': 102, 'Exclude': 71, 'Maybe': 54}
- 3-model majority breakdown: {'Include': 59, 'Maybe': 23, 'Exclude': 141, '(tie)': 4} (ties = 4)

- 4-model majority: 72 eligible, ties = 20 (more ties — even splits possible with 4 raters)

## Where the drop comes from (heuristic verdict -> LLM majority)

| heuristic | LLM-majority | n |
|---|---|---|
| Exclude | Exclude | 70 |
| Include | Include | 58 |
| Maybe | Exclude | 47 ← eligibility lost |
| Include | Exclude | 24 ← eligibility lost |
| Include | Maybe | 17 |
| Maybe | Maybe | 5 |
| Include | (tie) | 3 |
| Exclude | Maybe | 1 |
| Maybe | Include | 1 |
| Maybe | (tie) | 1 |

## Headline

- Under a 3-model LLM-majority screen, **82 of 227** records are eligible vs the heuristic's **156** — a drop of **74** (47%).
- The drop is concentrated in the heuristic's `Maybe` tier (the LLMs reclassify most `Maybe` papers as `Exclude`), consistent with the primary audit's dominant disagreement axis.
- **Caveat (load-bearing):** the prompt-robustness experiment (`experiments/prompt_robustness/`) showed roughly half of these LLM exclusions reverse under a more lenient prompt framing. The LLM-majority 82 is therefore a strict-prompt lower bound, not a framing-neutral truth. The framing-neutral eligible count is best regarded as lying between 82 and 156; neither endpoint is unambiguously correct.
- This does NOT change the paper's reported 156 (correctly the heuristic result). It quantifies how sensitive the headline is to the choice of screener.
