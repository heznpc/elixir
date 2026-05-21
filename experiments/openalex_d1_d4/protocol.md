# OpenAlex D1 + D4 Recheck — Pre-registered Protocol

**Status:** Pre-registered before first OpenAlex query.
**Date pinned:** 2026-05-21.
**Scope:** One-sided supplementary broader-database check of `paper/main.tex` §3.1 (D1 Loss Aversion, 6 papers / Moderate) and §3.4 (D4 Inventory Paralysis, 20 papers / Moderate). Same pattern as the D2/D6 extension (PR #6) and the D5 recheck (PR #11).

Completes the 5-domain broader-database audit cross-check; only D3 (gacha, 97 papers / Strong) is exempt because the evidence is already strong and OpenAlex extension would add marginal value.

---

## 1. Scope limitation

One-sided. OpenAlex hits can shift the moderate-evidence framing by surfacing peer-reviewed work PubMed missed; absence is consistent with both "no further evidence" and "evidence exists in venues OpenAlex does not index well."

Not a re-screen. Primary counts (D1=6, D4=20) stand; audit reports a supplementary footnote in each §3 subsection.

## 2. Hypothesis (descriptive, per-domain)

For each of D1 and D4, the heuristic-Include count and the LLM-confirmed-unanimous-Include count after dedup-vs-PubMed determine the verbal claim:

| LLM-confirmed-Include n | Verbal claim |
|---|---|
| 0   | Moderate-evidence claim corroborated by broader DB. |
| 1-3 | Moderate evidence remains moderate; add records to the literature pool. |
| 4-10 | Evidence rises from moderate to strong-adjacent; revise paragraph. |
| ≥11 | Evidence is materially stronger than the primary claim. Major revision. |

## 3. Queries

**D1** (loss aversion in games):
- search: `"loss aversion" OR "endowment effect" OR "sunk cost" OR "prospect theory" OR "status quo bias" OR "framing effect"`
- filter: `abstract.search:"video game" OR "video games" OR "gaming" OR "gamer" OR "rpg" OR "mmorpg" OR "online game" OR "gameplay" OR "in-game"`

**D4** (inventory paralysis / virtual possession):
- search: `"inventory" OR "virtual item" OR "virtual good" OR "psychological ownership" OR "virtual ownership" OR "digital possession" OR "virtual possession" OR "extended self"`
- filter: same game-context terms

Per-query cap 200 results.

## 4. Dedup + heuristic + LLM recheck

Identical to `experiments/openalex_d5/`: PMID match → DOI match → title-token jaccard ≥ 0.85, then heuristic `classify_paper` from `experiments/src/screening.py`, then 3-model LLM recheck on any Heuristic-Include.

## 5. Outputs

- `experiments/openalex_d1_d4/data/openalex_results.csv`
- `experiments/openalex_d1_d4/data/novel_records.csv`
- `experiments/openalex_d1_d4/data/dedup_log.csv`
- `experiments/openalex_d1_d4/data/queries.json`
- `experiments/openalex_d1_d4/llm_recheck_state.jsonl`
- `experiments/openalex_d1_d4/data/llm_recheck.csv`
- `experiments/results/openalex_d1_d4_summary.md`

## 6. Stop conditions

OpenAlex HTTP >10 % errors abort; wall > 10 min abort; LLM cost > $5 abort.

## 7. Coverage caveat

OpenAlex coverage of HCI (CHI, CHI PLAY), game-studies, consumer-behavior, and Japanese-language non-Crossref-registered work remains incomplete. The check is corroborative-only when the result is "0 unanimous-Include."
