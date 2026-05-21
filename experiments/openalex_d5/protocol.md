# OpenAlex D5 Completionism Recheck — Pre-registered Protocol

**Status:** Pre-registered before first OpenAlex query.
**Date pinned:** 2026-05-21.
**Scope:** One-sided supplementary check of `paper/main.tex` §3.6 (Completionism — PRIMARY, 5 papers, Weak evidence) by querying OpenAlex with completionism-targeted queries.

This protocol mirrors the structure of `experiments/openalex_extension/protocol.md` (which targeted D2 / D6). Same one-sidedness, same dedup + heuristic + LLM-recheck pipeline, same decision rule.

---

## 1. Scope limitation

One-sided. OpenAlex hits can falsify the "weak evidence" framing by surfacing peer-reviewed completionism work PubMed missed; absence of OpenAlex hits is consistent with both "no further evidence exists" and "evidence exists in venues OpenAlex does not index well."

This is **not** a re-screen of the PRISMA pipeline. The 156-eligible count and the 5-D5 count stand as primary; the audit reports a supplementary footnote in §3.6.

## 2. Hypothesis

H0: OpenAlex queries targeting completionism in digital games return 0 novel eligible records after dedup vs the PubMed corpus and LLM re-screening.

Pre-registered decision rule (per heuristic-Include count after dedup, then LLM-confirmed-Include count):

| LLM-confirmed-Include n | Verbal claim |
|---|---|
| 0   | Weak-evidence claim corroborated by broader DB. |
| 1-2 | Weak evidence remains weak; add records to literature pool. |
| 3-9 | Evidence rises from weak to moderate; revise paper §3.6 narrative. |
| ≥10 | Evidence is materially stronger than the §3.6 claim. Major revision. |

## 3. Source and queries

OpenAlex Works API, no key, polite-pool header `mailto=heznpc@gmail.com`. Endpoint: `https://api.openalex.org/works`.

**D5 query:**
- search: `"completionism" OR "completionist" OR "achievement hunting" OR "achievement hunter" OR "100% completion" OR "platinum trophy" OR "collect them all" OR "collectathon"`
- abstract.search filter: `"video game" OR "video games" OR "gaming" OR "gamer" OR "rpg" OR "mmorpg" OR "online game" OR "achievement" OR "trophy"`

Per-query cap 200 results.

## 4. Deduplication

Same as `experiments/openalex_extension/dedup.py`: PMID match → DOI match → title-token jaccard ≥ 0.85.

## 5. Heuristic + LLM recheck

Heuristic: reuse `experiments/src/screening.py::classify_paper`.
LLM recheck: identical to `experiments/openalex_extension/llm_recheck.py`, 3 models per Heuristic-Include record.

## 6. Outputs

- `experiments/openalex_d5/data/openalex_results.csv`
- `experiments/openalex_d5/data/novel_records.csv`
- `experiments/openalex_d5/data/dedup_log.csv`
- `experiments/openalex_d5/data/queries.json`
- `experiments/openalex_d5/llm_recheck_state.jsonl`
- `experiments/openalex_d5/data/llm_recheck.csv`
- `experiments/results/openalex_d5_summary.md`

## 7. Stop conditions

Same as openalex_extension §9: OpenAlex HTTP >10 % errors abort; wall > 10 min abort; LLM cost > $5 abort.

## 8. Coverage caveat

OpenAlex coverage of HCI (CHI, CHI PLAY), game-studies, and grey-literature completionism discussions remains incomplete. The check is corroborative-only when the result is "0 novel"; it cannot prove the absence of evidence.
