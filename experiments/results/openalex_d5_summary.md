# OpenAlex D5 Recheck — Summary

Pre-registered protocol: `experiments/openalex_d5/protocol.md`.

OpenAlex hits (pre-dedup): D5 = 200.
Queries hash: `80aacac1592fdf38`.

Duplicates removed: pmid=1, doi=0, title-jaccard=0.

Novel records (surviving dedup): **199**.

## Heuristic verdict distribution on novel records

- **Include**: 3
- Maybe: 127
- Exclude: 69

## Heuristic-Include records (candidate D5 additions)

- **Framework for Designing and Evaluating Game Achievements** (2011, **)
  - OpenAlex: W161555447; PMID: n/a; DOI: 10.26503/dl.v2011i1.545
  - Heuristic reason: Game achievement/completionism research
- **Breaking Harmony Square: A game that “inoculates” against political misinformation** (2020, *Harvard Kennedy School Misinformation Review*)
  - OpenAlex: W3096296182; PMID: n/a; DOI: 10.37016/mr-2020-47
  - Heuristic reason: Free-to-play game monetization research
- **DLC: Perpetual Commodification of the Video Game** (2012, *Scholarworks (University of Massachusetts Amherst)*)
  - OpenAlex: W1847083306; PMID: n/a; DOI: 10.7275/democratic-communique.278
  - Heuristic reason: Microtransaction/in-game spending research

## LLM recheck on Heuristic-Include records (protocol §5)

Three Claude models (Opus 4-7, Sonnet 4-6, Haiku 4-5) re-screened each Heuristic-Include record with the same criteria the LLM-second-reviewer audit used.

| OpenAlex ID | Title (first 90c) | Haiku | Sonnet | Opus | Consensus |
|---|---|---|---|---|---|
| W161555447 | Framework for Designing and Evaluating Game Achievements | Exclude | Maybe | Maybe | split |
| W3096296182 | Breaking Harmony Square: A game that “inoculates” against political misinformation | Exclude | Exclude | Exclude | **Exclude** (unanimous) |
| W1847083306 | DLC: Perpetual Commodification of the Video Game | Exclude | Exclude | Exclude | **Exclude** (unanimous) |

**LLM-confirmed-Include (unanimous across 3 tiers): 0.**

## Headline

- Heuristic-Include count = 3 → band: Evidence rises from weak to moderate; revise paper §3.6 narrative.
- LLM-confirmed-Include count = **0** (load-bearing per protocol §2)
- LLM band: Weak-evidence claim corroborated by broader DB.
- **D5 weak-evidence claim corroborated.** No novel D5 papers survive both heuristic and LLM re-screening. Paper §3.6 stands; OpenAlex check added as supplementary footnote.

**Coverage caveat.** OpenAlex coverage of HCI (CHI, CHI PLAY), game-studies, and grey-literature completionism discussions remains incomplete. The check is corroborative-only when the result is '0 novel'.