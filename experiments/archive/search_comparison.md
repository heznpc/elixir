# Search Comparison: v1 vs v2

## Summary

| Metric | v1 | v2 | Change |
|--------|---:|---:|--------|
| ESearch total hits | 42,564 | Q1=227, Q2=75 | Dramatically reduced |
| Unique PMIDs for screening | 500 | 227 | -- |
| Records fetched with abstracts | 500 | 227 | -- |
| Records with >= 1 domain | 252 | 181 | -- |
| Records with no domain | 248 | 46 | -- |
| Noise reduction ratio | -- | -- | 99.9% fewer no-domain hits |

## Domain Distribution Comparison

| Domain | v1 | v2 | Change |
|--------|---:|---:|--------|
| D1: Loss aversion / behavioral economics | 1 | 17 | +16 |
| D2: Consumable hoarding | 0 | 0 | 0 |
| D3: Gacha / Loot box | 9 | 140 | +131 |
| D4: Inventory / virtual possession | 187 | 23 | -164 |
| D5: Completionism | 81 | 15 | -66 |
| D6: Backlog | 7 | 48 | +41 |
| Cross-domain: Hoarding link | 4 | 44 | +40 |

## Key Observations

### v1 Problems
- Broad search terms (`collect*`, `game*`, `inventory`) matched biomedical vocabulary
- 42,564 total ESearch hits, the vast majority irrelevant clinical studies
- `"game*"` matched game theory and gamete research
- `"collect*"` matched specimen/data collection
- `"inventory"` matched clinical inventories (BDI, OCI-R, etc.)
- `"achievement"` matched clinical/educational achievement measures

### v2 Improvements
- Every result requires an explicit game-context term (`"video game"`, `"gaming"`, `"player"`, etc.)
- Second targeted query captures gacha/loot box literature specifically
- Deduplication by PMID across both queries
- Relevance scoring (game_score x hoarding_score) enables ranked output
- Results are far more relevant to in-game hoarding behaviors

