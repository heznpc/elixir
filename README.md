# The Elixir Problem

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

Research Program: 4 (AI-Mediated Accumulation)
Status: Reproducible artifact
Relationship to other work: Companion to tidal (Program 4 anchor)

---

**A Systematic Review of Hoarding-Related Behaviors in Digital Games.** This PRISMA review maps in-game accumulation behaviors -- unused consumables, gacha rosters, inventory paralysis, completionism, backlog hoarding -- onto clinical hoarding disorder constructs (DSM-5; Frost-Hartl CBT model). Evidence is scattered across behavioral economics, game studies, gambling research, consumer psychology, and HCI; no prior review has unified it under a hoarding framework. The repository ships the search automation, the screened dataset (156 records), and the manuscript source.

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

Evidence is mapped across six behavioral domains:

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

Raw records land in `experiments/data/raw/`; screening output in `experiments/data/processed/`; analyses in `experiments/results/`. The search is deterministic given the same PubMed database state, but results may shift over time as PubMed indexes new publications.

**Python >= 3.10 required.**

## Key Findings

- **Currently implemented**: PRISMA search automation (Entrez E-utilities), automated screening on 227 records yielding 156 eligible, six-domain mapping with regenerable summaries in `experiments/results/`, and the manuscript in `paper/main.tex`.
- **Planned**: extract inline `\begin{thebibliography}` to `references.bib` to enable a shared bib across Program 4 companions (see `planning/decisions.md`).
- **Design intent**: DDD-style layout -- `paper/` is the single source of truth; `experiments/` regenerates evidence; `planning/` carries meta-work and rationale. Versioning is git's job, so filenames do not carry `_v2`/`_v3` suffixes; `experiments/archive/` retains the v1 pipeline as a reproducibility audit trail.
- **Non-goals**: not a meta-analysis (effect sizes are not pooled across the heterogeneous designs); not a clinical instrument (no diagnostic claim about individual players); not a venue-locked artifact (venue adapters belong in `submissions/<venue>/`, not in `main.tex`).
- The gacha/loot-box domain (D3) carries the strongest evidence base, with 97 eligible papers linking spending to problem-gambling and OCD/hoarding symptomatology.
- Consumable hoarding (D2, "the elixir problem") and backlog accumulation (D6) are **complete evidence voids** -- robustly recognized in player communities and design practice but absent from peer-reviewed literature.

## Target Journal

*Games and Culture* (SAGE)

## License

CC-BY 4.0
