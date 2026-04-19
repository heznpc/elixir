# PRISMA Flow Diagram Data

## Identification

- Records identified through PubMed (total ESearch count): **42,564**
- Records fetched with abstracts (retmax=500, most recent): **500**
- Records identified through ACM DL: **0** (HTTP 403 -- ACM blocks automated access; manual search required)
- **Total records retrieved for screening: 500**

## Screening

- Duplicate records removed: **0** (single-database batch, no de-dup needed within PubMed)
- Records with abstracts fetched (PubMed): **500**
- Records screened (title + abstract keyword match): **500**

## Eligibility (domain classification)

- Records matching at least one domain: **252**
- Records matching no domain keywords: **248**

## Important Observation: Query Noise

The broad PubMed query generates a very high total hit count (42,564) because
many terms overlap with biomedical vocabulary:

- **"collect*"** matches specimen/data collection studies
- **"game*"** matches game theory in medicine and gamete research
- **"inventory"** matches clinical inventories (Beck Depression Inventory, OCI-R, etc.)
- **"achievement"** matches clinical/educational achievement measures
- **"virtual"** matches virtual reality rehabilitation studies

Of the 500 most-recent results fetched, the vast majority are biomedical papers
with no relevance to video games or digital hoarding. The domain-classified
papers (252/500) are predominantly false positives matched on generic terms.

**Recommendation for the paper**: Either (a) add a filter term like
`"video game" OR "gaming" OR "player"` as a required AND clause, or (b) note
in the methods section that manual title/abstract screening was essential to
remove biomedical false positives, consistent with standard PRISMA practice.

## Domain Distribution

| Domain | n |
|--------|--:|
| D1: Loss aversion / behavioral economics | 1 |
| D2: Consumable hoarding | 0 |
| D3: Gacha / Loot box | 9 |
| D4: Inventory / virtual possession | 187 |
| D5: Completionism | 81 |
| D6: Backlog | 7 |
| Cross-domain: Hoarding link | 4 |

## Notes

- The PubMed search was conducted via NCBI Entrez E-utilities (esearch + efetch).
- ACM DL returned HTTP 403 for all automated requests (both urllib and WebFetch).
  ACM requires manual browser-based search or institutional API access.
- Domain classification is based on keyword matching in title + abstract text.
- Papers may appear in multiple domains.
- The high false-positive rate from PubMed is expected given the broad, multi-term
  query. Standard PRISMA practice requires manual title/abstract screening to
  remove irrelevant biomedical results.
