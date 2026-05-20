# OpenAlex Extension — Pre-registered Protocol

**Status:** Pre-registered before first OpenAlex query.
**Date pinned:** 2026-05-21.
**Scope:** One-sided supplementary check of the D2 (consumable hoarding) and D6 (backlog accumulation) evidence-void claim by querying OpenAlex.org with analogous keyword queries to the PubMed PRISMA pipeline (`experiments/src/prisma_search.py`).

This protocol exists to constrain interpretation **before** the OpenAlex queries are issued. Any deviation must be recorded as an amendment in `planning/decisions.md`.

---

## 1. Scope limitation (load-bearing)

This extension is **one-sided**: it can falsify the D2/D6 evidence-void claim by finding eligible records OpenAlex indexes but PubMed does not, but it cannot confirm the claim because absence of OpenAlex hits is consistent with both "no evidence exists" and "evidence exists in venues OpenAlex does not index well." OpenAlex coverage of game studies, HCI venues (ACM Digital Library, CHI Proceedings), and grey literature is broader than PubMed but is itself non-exhaustive. The extension is reported in the paper as a supplementary check, not as a comprehensive review.

The extension does **not** re-run the systematic review. It does not change the primary PRISMA workflow, eligible-paper count (156), or any kappa figure from the LLM second-reviewer audit. It only updates the §3.2 (D2) and §3.7 (D6) evidence-void claim with the OpenAlex result.

## 2. Hypotheses

- **H0 (D2):** OpenAlex queries targeting consumable hoarding in digital games return zero eligible records after deduplication against the PubMed corpus and after heuristic screening.
- **H0 (D6):** OpenAlex queries targeting digital game backlog accumulation return zero eligible records after deduplication and heuristic screening.

H1 in each case: ≥ 1 eligible novel record.

Pre-registered decision rule:

| Eligible novel records found per domain | Verbal claim allowed |
|---|---|
| 0 | "OpenAlex extension corroborates the evidence-void claim. The void survives a broader-database check." |
| 1-2 | "Evidence sparse but not absent. The void claim is downgraded to 'extremely thin literature.' Records are listed in supplementary." |
| 3-9 | "Evidence is sparse but the void claim is not supported. Records are listed in supplementary." |
| ≥ 10 | "The evidence-void claim is falsified for this domain. The paper §3 narrative must be revised. Recorded in `planning/decisions.md` as a finding requiring §3 rewrite." |

## 3. Source and queries

**Source:** OpenAlex.org public Works API. No API key needed; rate-limited to 10 req/s. Polite pool header `mailto=` set to `heznpc@gmail.com` per OpenAlex documentation. Endpoint: `https://api.openalex.org/works`.

**Queries** (frozen at run time; recorded verbatim in the run header):

- **D2 (consumable hoarding):** `(("consumable hoarding" OR "potion hoarding" OR "elixir" OR "too good to use" OR "item retention" OR "resource hoarding") AND ("video game" OR "video games" OR "gaming" OR "gamer" OR "rpg" OR "mmorpg" OR "online game"))`
- **D6 (backlog accumulation):** `(("backlog" OR "pile of shame" OR "unplayed games" OR "steam library" OR "game library") AND ("video game" OR "video games" OR "gaming" OR "gamer" OR "steam" OR "digital storefront"))`

Both queries are field-restricted to title + abstract (`abstract.search` and `title.search`).

**Inclusion period:** all publication years (consistent with the PubMed protocol).

**Retrieval cap:** 200 records per query (sufficient given expected hit count; OpenAlex returns 25 per page by default).

## 4. Deduplication

For each OpenAlex record, the following identifiers are checked against the PubMed corpus (`experiments/data/raw/pubmed_results.csv`):
- PMID (extracted from OpenAlex `ids.pmid` field if present)
- DOI (lowercased, stripped of `https://doi.org/` prefix)
- Title-token jaccard ≥ 0.85 as a soft match (catches DOI-less but obviously duplicate records)

Any of the above matches → **drop as duplicate**. Surviving records are written to `data/novel_records.csv`.

## 5. Heuristic screening

The existing rule-based heuristic in `experiments/src/screening.py` is applied to novel records (title + abstract only, OpenAlex provides both). Verdict distribution: Include / Maybe / Exclude.

For this extension, an "eligible record" is defined as a heuristic-Include record. Heuristic-Maybe is treated as borderline and reported separately. Heuristic-Exclude is dropped.

## 6. LLM follow-up (conditional, separate experiment)

If novel records yield ≥ 5 heuristic-Include hits per domain, a follow-up LLM screening pass (using the protocol from `experiments/llm_second_reviewer/protocol.md`) is filed as a separate experiment. The protocol pre-commitment is recorded here but the run is not part of this extension.

## 7. Statistical reporting

The extension is descriptive. Reported:
- Total OpenAlex hits per query (before dedup).
- Duplicates with PubMed corpus.
- Novel records.
- Heuristic verdict distribution on novel records.
- Per-domain decision-rule outcome (per §2).

No bootstrap CI or hypothesis test. n is small and the decision rule is categorical.

## 8. Outputs

All committed to git:

- `experiments/openalex_extension/data/openalex_results.csv` — all records returned, both domains.
- `experiments/openalex_extension/data/novel_records.csv` — surviving records after dedup, with heuristic screening verdicts.
- `experiments/openalex_extension/data/dedup_log.csv` — per-record dedup outcome with reason.
- `experiments/results/openalex_extension_summary.md` — analysis report.
- This protocol (`protocol.md`) — unchanged after first commit.

## 9. Stop conditions

- OpenAlex API HTTP errors >10 % of requests → abort, report.
- Wall time > 10 min → abort, report.
- No LLM calls in this extension; no cost ceiling other than 0.

## 10. Prior art / coverage acknowledgment

OpenAlex indexes 240M+ scholarly works, including ACM DL, IEEE Xplore, Google Scholar-discoverable preprints, and Crossref-registered DOIs. Coverage of game-studies and HCI venues is materially better than PubMed (which is biomedical-skewed). However, OpenAlex coverage of:
- Practitioner blog posts (Bycer, Game Wisdom, Game Developer)
- TV Tropes / Pixiv Dictionary cultural-literacy sources
- Japanese-language game research not indexed in Crossref

remains incomplete. The extension acknowledges this in the §3 / §3.7 paper narrative if the evidence-void claim is corroborated.
