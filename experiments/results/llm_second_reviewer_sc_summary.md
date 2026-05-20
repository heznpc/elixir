# Self-Consistency Follow-up — Summary

Protocol §6 trigger: all three primary-run κ values landed in 0.40 < κ ≤ 0.60.

Subset: convergent-disagreement (n = 59 papers where the 3 LLMs in the primary run agreed with each other but disagreed with the heuristic).

Calls observed in state file: 551  (parse/error: 0).

## Per-tier stability

| Tier | n pairs | unanimous 3/3 | majority 2/3 | no majority | mean cost / call |
|---|---|---|---|---|---|
| haiku | 59 | 45 (76%) | 10 (17%) | 4 (7%) | — |
| sonnet | 59 | 56 (95%) | 0 (0%) | 3 (5%) | — |
| opus | 59 | 55 (93%) | 2 (3%) | 2 (3%) | — |

## Majority vs original single-sample LLM verdict

| Tier | n pairs with majority | majority == original | majority != original | original not in 3 samples |
|---|---|---|---|---|
| haiku | 58 | 52 (90%) | 6 | 1 |
| sonnet | 59 | 59 (100%) | 0 | 0 |
| opus | 59 | 58 (98%) | 1 | 1 |

## Cross-tier convergence on majority verdicts

Restricted to papers where every tier has a defined majority (i.e., no 1-1-1 ties).

- Papers with majority across all 3 tiers: **58** / 59
- All 3 tier majorities identical: **51** (88%)
  - Reaffirms the original cross-tier disagreement with heuristic: **51**
  - Now agrees with heuristic (original convergence was sampling-lucky): **0**

**Reaffirmed disagreement axes (heuristic → majority LLM consensus):**

- Maybe → Exclude: 36
- Include → Exclude: 13
- Include → Maybe: 2

## Headline interpretation

- The convergent-disagreement finding from the primary run is **robust** to sampling variance: 88% of eligible papers retain a unanimous 3-tier majority verdict that differs from the heuristic.
- This raises the bar for the heuristic on these papers: the LLM consensus is reproducible across both models and sampling.

**No validity claim is made.** Per protocol §1 and §4, this remains an inter-rater reliability + stability check between automated screeners.