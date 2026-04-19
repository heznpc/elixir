# Search Log (Reproducibility Record)

**Date**: 2026-03-28 03:46:27 UTC

## PubMed Query

```
(hoard* OR collect* OR "loss aversion" OR "endowment effect" OR "sunk cost" OR "compulsive buying" OR "compulsive acquisition" OR "item retention" OR "inventory management" OR "completionism" OR "achievement hunting" OR "digital possession") AND (game* OR "video game" OR "virtual" OR "loot box" OR "gacha" OR "inventory" OR "digital possession" OR "virtual item" OR "microtransaction" OR "backlog")
```

- Endpoint: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi` + `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi`
- Parameters: retmax=500, rettype=xml, tool=elixir_review, email=research@example.com

## ACM DL Query

```
(hoard* OR collect* OR "loss aversion" OR "endowment effect" OR "sunk cost" OR "compulsive buying" OR "compulsive acquisition" OR "item retention" OR "inventory management" OR "completionism" OR "achievement hunting" OR "digital possession") AND (game* OR "video game" OR "virtual" OR "loot box" OR "gacha" OR "inventory" OR "digital possession" OR "virtual item" OR "microtransaction" OR "backlog")
```

- Endpoint: `https://dl.acm.org/action/doSearch`

## Execution Log

- [2026-03-28 03:46:14 UTC] === PRISMA Systematic Review Search START ===
- [2026-03-28 03:46:14 UTC] Output directory: /Users/ren/IdeaProjects/Paper/elixir/experiments
- [2026-03-28 03:46:14 UTC] --- PubMed ESearch ---
- [2026-03-28 03:46:14 UTC] ESearch URL (full query with retmax=500, retmode=json)
- [2026-03-28 03:46:15 UTC] ESearch returned count=42564, fetched 500 PMIDs (most recent)
- [2026-03-28 03:46:15 UTC] --- PubMed EFetch (500 records, batched 200+200+100) ---
- [2026-03-28 03:46:15 UTC] EFetch batch 1: 200 PMIDs
- [2026-03-28 03:46:18 UTC] EFetch batch 2: 200 PMIDs
- [2026-03-28 03:46:22 UTC] EFetch batch 3: 100 PMIDs
- [2026-03-28 03:46:24 UTC] Parsing 500 PubmedArticle XML blocks
- [2026-03-28 03:46:24 UTC] Parsed 500 valid records with abstracts
- [2026-03-28 03:46:24 UTC] --- Domain Classification ---
- [2026-03-28 03:46:24 UTC] Papers with >= 1 domain: 252/500
- [2026-03-28 03:46:24 UTC] --- ACM Digital Library Search ---
- [2026-03-28 03:46:24 UTC] Attempt via urllib: HTTP 403 Forbidden (2 retries)
- [2026-03-28 03:46:27 UTC] Attempt via WebFetch tool: HTTP 403 Forbidden
- [2026-03-28 03:46:27 UTC] ACM DL blocks all automated/scripted access; manual browser search required
- [2026-03-28 03:46:27 UTC] --- Writing output files ---
- [2026-03-28 03:46:27 UTC] Wrote pubmed_results.csv (500 rows)
- [2026-03-28 03:46:27 UTC] Wrote domain_counts.md
- [2026-03-28 03:46:27 UTC] Wrote prisma_flow.md
- [2026-03-28 03:46:27 UTC] Wrote top_papers_by_domain.md
- [2026-03-28 03:46:27 UTC] Wrote search_log.md

## Key Finding: High False-Positive Rate

The PubMed query matched 42,564 total records. Inspection of the 500 most-recent
results revealed that the vast majority are biomedical papers unrelated to video
games. Terms like "collect*", "game*", "inventory", "achievement", and "virtual"
have extensive biomedical usage (specimen collection, game theory, clinical
inventories, VR rehabilitation). This is consistent with known challenges of
broad systematic review queries on PubMed and underscores the necessity of
manual title/abstract screening in the PRISMA workflow.
