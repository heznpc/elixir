# elixir-review

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

**The Elixir Problem: A Systematic Review of Hoarding-Related Behaviors in Digital Games**

Players routinely finish RPGs with inventories full of unused potions. They spend hundreds of dollars chasing complete gacha character rosters. They maintain elaborate storage systems rather than discard a single item. They accumulate libraries of hundreds of unplayed games during digital sales. These behaviors share core psychological mechanisms with clinical hoarding disorder -- loss aversion, emotional attachment, decision avoidance, and acquisition-driven positive affect -- yet the relevant evidence is scattered across behavioral economics, game studies, gambling research, consumer psychology, and HCI. No prior review has unified this evidence under a hoarding framework.

This repository contains the PRISMA systematic review, search automation scripts, and manuscript source for the paper.

## Repository Structure

```
elixir/
  paper/                      Domain -- manuscript source of truth
    main.tex                  Manuscript (LaTeX)
    figures/                  Final figures
  experiments/                Application -- evidence generation
    src/                      prisma_search.py, screening.py
    data/raw/                 pubmed_results.csv (227 records)
    data/processed/           screening_results.csv (156 eligible)
    results/                  Regenerated analyses
    archive/                  Superseded v1 pipeline (audit trail)
  literature/                 Reading notes, gap analysis
  planning/                   TODO, review, decisions log
    drafts/                   Superseded manuscript.md, outline.md
  submissions/                Venue-specific adapters (when submitting)
```

## Method: PRISMA Systematic Review

The review follows PRISMA 2020 guidelines. Two complementary PubMed queries were executed:

- **Query 1 (broad):** Game-specific terms AND hoarding/collecting terms
- **Query 2 (targeted):** Gacha/loot-box terms AND gambling/addiction terms

Combined yield: **227 unique records**. After automated screening, **156 met eligibility criteria**.

Evidence is mapped across five behavioral domains:

| Domain | Description | Eligible papers |
|--------|-------------|-----------------|
| D1 | Loss aversion / behavioral economics | moderate |
| D2 | Consumable hoarding ("too good to use") | **0** (evidence void) |
| D3 | Gacha / loot box collection | 97 (strongest) |
| D4 | Inventory paralysis / virtual possession | moderate |
| D5 | Completionism / achievement hunting | moderate |
| D6 | Backlog accumulation | **0** (evidence void) |

## Reproducing the Literature Search

All scripts use Python standard library only. No third-party packages required.

```bash
# Run the PRISMA search (queries PubMed via Entrez E-utilities)
python experiments/src/prisma_search.py

# Run automated screening on the results
python experiments/src/screening.py
```

Raw records land in `experiments/data/raw/`; screening output goes to `data/processed/`; analyses to `results/`. The search is deterministic given the same PubMed database state, but results may vary over time as PubMed indexes new publications.

**Python >= 3.10 required.**

## Key Findings

- The gacha/loot-box domain (D3) has the strongest evidence base, with 97 eligible papers linking spending to problem gambling and OCD/hoarding symptomatology.
- Consumable hoarding (D2, "the elixir problem") and backlog accumulation (D6) are **complete evidence voids** -- robustly recognized in player communities and game design practice but absent from peer-reviewed literature.
- The paper proposes a five-domain theoretical framework and maps available evidence onto DSM-5 hoarding disorder criteria and the Frost-Hartl cognitive-behavioral model.

## Target Journal

*Games and Culture* (SAGE)

## License

CC-BY 4.0
