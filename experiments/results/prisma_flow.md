# PRISMA Flow Diagram Data (v2 -- Refined Search)

## Identification

- **Query 1** (game terms AND hoarding terms):
  - ESearch total count: **227**
  - PMIDs fetched (retmax=500): **227**
- **Query 2** (gacha/loot box specific):
  - ESearch total count: **75**
  - PMIDs fetched (retmax=500): **75**
- Combined PMIDs before dedup: **302**
- **Duplicates removed: 75**
- **Unique PMIDs for screening: 227**

## Screening

- Records with abstracts fetched: **227**
- Records screened (title + abstract keyword match): **227**

## Eligibility (domain classification)

- Records matching at least one domain: **181**
- Records matching no domain keywords: **46**

## Domain Distribution

| Domain | n |
|--------|--:|
| D1: Loss aversion / behavioral economics | 17 |
| D2: Consumable hoarding | 0 |
| D3: Gacha / Loot box | 140 |
| D4: Inventory / virtual possession | 23 |
| D5: Completionism | 15 |
| D6: Backlog | 48 |
| Cross-domain: Hoarding link | 44 |

## Notes

- Both queries were run via NCBI Entrez E-utilities (esearch + efetch).
- Results were deduplicated by PMID before abstract fetching.
- Domain classification is based on keyword matching in title + abstract text.
- Papers may appear in multiple domains.
- v2 requires explicit game-context terms in the query, eliminating the biomedical false-positive noise from v1.
