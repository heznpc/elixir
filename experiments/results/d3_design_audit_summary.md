# D3 Study-Design Audit — Summary

Pre-registered protocol: `experiments/d3_design_audit/protocol.md`.

Corpus: 102 D3-tagged papers (heuristic Include+Maybe).
Total LLM calls observed: 305 (expected 306).

## Per-paper consensus among the 3 LLMs

- Unanimous (3/3 same design): **92** (90%)
- Majority (2/3 same):        **9** (9%)
- No majority (1/1/1):        **1** (1%)

## Design-category counts: paper §3.3 vs LLM majority

| Category | Paper §3.3 | LLM majority | Δ (LLM − paper) | |Δ|/paper | Band |
|---|---|---|---|---|---|
| cross_sectional | 43 | 53 | +10 | 23% | approximate (20-50 %) |
| unspecified | 35 | 1 | -34 | 97% | **revise** (> 50 %) |
| longitudinal | 9 | 9 | +0 | 0% | **survives** (< 20 %) |
| systematic_review | 4 | 6 | +2 | 50% | approximate (20-50 %) |
| scale_validation | 3 | 6 | +3 | 100% | **revise** (> 50 %) |
| review_commentary | 3 | 13 | +10 | 333% | **revise** (> 50 %) |
| experimental | 2 | 3 | +1 | 50% | approximate (20-50 %) |
| qualitative | 2 | 2 | +0 | 0% | **survives** (< 20 %) |
| content_analysis | 1 | 8 | +7 | 700% | **revise** (> 50 %) |
| **total (categorised)** | 102 | 101 | -1 | | |
| no-majority papers | — | 1 | — | — | descriptive |

## Per-tier design-count breakdown

| Category | Haiku | Sonnet | Opus | Paper |
|---|---|---|---|---|
| cross_sectional | 54 | 51 | 55 | 43 |
| unspecified | 5 | 1 | 0 | 35 |
| longitudinal | 9 | 9 | 8 | 9 |
| systematic_review | 6 | 6 | 5 | 4 |
| scale_validation | 6 | 6 | 6 | 3 |
| review_commentary | 11 | 13 | 13 | 3 |
| experimental | 3 | 5 | 3 | 2 |
| qualitative | 2 | 3 | 3 | 2 |
| content_analysis | 6 | 8 | 8 | 1 |

## Load-bearing check: the longitudinal-9 claim

Per protocol §3 the longitudinal-9 claim is load-bearing. It stands if at least 6 of the 9 paper-claimed-longitudinal papers are LLM-majority-longitudinal.

- Papers any LLM classified as longitudinal: **9**
- Of these, papers with LLM majority = longitudinal: **9**
- Of these, papers with unanimous LLM = longitudinal: **8**

- LLM majority-longitudinal count = 9. **Within reach of the paper's claim of 9.** The specific identity of the 9 cannot be verified from this audit alone (the paper does not pin PMIDs), but the order of magnitude is consistent.

## 'Unspecified' category

Paper §3.3 lists 35 'unspecified' papers. LLM majority places 1 there.
- LLMs assigned 34 papers to a specific design category that the heuristic could not pin down. Re-running this audit at the paper-write step would reduce the unspecified bucket.

## Headline

- **4 category(ies) fail the 50 % band: unspecified, scale_validation, review_commentary, content_analysis**. Paper §3.3 table requires line revision before submission.

**No psychometric or design-quality claim is made.** The audit checks only whether the heuristic-derived counts in paper §3.3 are robust to an independent LLM re-classification.