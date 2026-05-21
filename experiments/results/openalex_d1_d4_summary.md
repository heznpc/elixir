# OpenAlex D1 + D4 Recheck — Summary

Pre-registered protocol: `experiments/openalex_d1_d4/protocol.md`.

OpenAlex hits (pre-dedup): D1 = 200, D4 = 200.
Queries hash: `8057c2b37790c2d6`.

Duplicates removed: pmid=13, doi=0, title-jaccard=0.

## Domain D1

- Heuristic Include: **13**, Maybe: 69, Exclude: 113.

**Heuristic-Include records:**

- **Searching for the sunk cost fallacy** (2007, *Experimental Economics*)
  - OpenAlex: W1997517742; PMID: n/a; DOI: 10.1007/s10683-006-9134-0
  - Heuristic reason: Sunk cost research in game context
- **Framework for Designing and Evaluating Game Achievements** (2011, **)
  - OpenAlex: W161555447; PMID: n/a; DOI: 10.26503/dl.v2011i1.545
  - Heuristic reason: Game achievement/completionism research
- **Economic model of microtransactions in video games** (2019, *Journal of Economic Science Research*)
  - OpenAlex: W3183566438; PMID: n/a; DOI: 10.30564/jesr.v1i1.439
  - Heuristic reason: Microtransaction/in-game spending research
- **THE AMBIGUITY AVERSION LITERATURE: A CRITICAL ASSESSMENT** (2009, *Economics and Philosophy*)
  - OpenAlex: W2125674100; PMID: n/a; DOI: 10.1017/s026626710999023x
  - Heuristic reason: Sunk cost research in game context
- **Gaming disorder: A summary of its characteristics and aetiology** (2023, *Comprehensive Psychiatry*)
  - OpenAlex: W4318761566; PMID: 36764098; DOI: 10.1016/j.comppsych.2023.152376
  - Heuristic reason: Gaming disorder study with spending/purchasing component
- **Sunk Cost as a Self-Management Device** (2018, *Management Science*)
  - OpenAlex: W3124127077; PMID: n/a; DOI: 10.1287/mnsc.2018.3032
  - Heuristic reason: Sunk cost research in game context
- **EXPERIMENTAL EVIDENCE OF A SUNK‐COST PARADOX: A STUDY OF PRICING BEHAVIOR IN BERTRAND–EDGEWORTH DUOPOLY*** (2011, *International Economic Review*)
  - OpenAlex: W2123944148; PMID: n/a; DOI: 10.1111/j.1468-2354.2011.00630.x
  - Heuristic reason: Sunk cost research in game context
- **Free-to-Play Games: Professionals’ Perspectives** (2014, **)
  - OpenAlex: W148591480; PMID: n/a; DOI: 10.26503/dl.v2014i2.702
  - Heuristic reason: Free-to-play game monetization research
- **Achievement Relocked** (2020, *The MIT Press eBooks*)
  - OpenAlex: W4236371823; PMID: n/a; DOI: 10.7551/mitpress/12243.001.0001
  - Heuristic reason: Loss aversion in video game context
- **Experimental Investigation of the Subjective Value of Information in Trading** (2003, *Journal of the Association for Information Systems*)
  - OpenAlex: W3125195420; PMID: n/a; DOI: 10.17705/1jais.00032
  - Heuristic reason: Endowment effect in game/virtual context
- **Achievement Relocked: Loss Aversion and Game Design** (2020, *Architecture, Design and Conservation (Aarhus School of Architecture, Design School Kolding, The Royal Danish Academy of Fine Arts, Schools of Architecture, Design and Conservation (KADK))*)
  - OpenAlex: W3013771817; PMID: n/a; DOI: 10.7551/mitpress/12243.001.0001
  - Heuristic reason: Loss aversion in video game context
- **Credibilistic Loss Aversion Nash Equilibrium for Bimatrix Games with Triangular Fuzzy Payoffs** (2018, *Complexity*)
  - OpenAlex: W2905109362; PMID: n/a; DOI: 10.1155/2018/7143586
  - Heuristic reason: Loss aversion in game context
- **Zero-Zero Chance-Constrained Games** (1968, *Theory of Probability and Its Applications*)
  - OpenAlex: W1994737592; PMID: n/a; DOI: 10.1137/1113079
  - Heuristic reason: Loss aversion in game context

**LLM recheck verdicts (3 Claude models):**

| OpenAlex ID | Title (first 90c) | Haiku | Sonnet | Opus | Consensus |
|---|---|---|---|---|---|
| W1997517742 | Searching for the sunk cost fallacy | Exclude | Maybe | Exclude | split |
| W161555447 | Framework for Designing and Evaluating Game Achievements | Maybe | Maybe | Maybe | **Maybe** (unanimous) |
| W3183566438 | Economic model of microtransactions in video games | Exclude | Exclude | Exclude | **Exclude** (unanimous) |
| W2125674100 | THE AMBIGUITY AVERSION LITERATURE: A CRITICAL ASSESSMENT | Exclude | Exclude | Exclude | **Exclude** (unanimous) |
| W4318761566 | Gaming disorder: A summary of its characteristics and aetiology | Exclude | Exclude | Maybe | split |
| W3124127077 | Sunk Cost as a Self-Management Device | Exclude | Maybe | Exclude | split |
| W2123944148 | EXPERIMENTAL EVIDENCE OF A SUNK‐COST PARADOX: A STUDY OF PRICING BEHAVIOR IN BERTRAND–EDGE | Exclude | Exclude | Exclude | **Exclude** (unanimous) |
| W148591480 | Free-to-Play Games: Professionals’ Perspectives | Exclude | Exclude | Exclude | **Exclude** (unanimous) |
| W4236371823 | Achievement Relocked | Exclude | Exclude | Maybe | split |
| W3125195420 | Experimental Investigation of the Subjective Value of Information in Trading | Maybe | Exclude | Exclude | split |
| W3013771817 | Achievement Relocked: Loss Aversion and Game Design | Exclude | Exclude | Exclude | **Exclude** (unanimous) |
| W2905109362 | Credibilistic Loss Aversion Nash Equilibrium for Bimatrix Games with Triangular Fuzzy Payo | Exclude | Exclude | Exclude | **Exclude** (unanimous) |
| W1994737592 | Zero-Zero Chance-Constrained Games | Exclude | Exclude | Exclude | **Exclude** (unanimous) |

- LLM-confirmed-Include (unanimous): **0** → band: Moderate-evidence claim corroborated by broader DB.

## Domain D4

- Heuristic Include: **13**, Maybe: 114, Exclude: 65.

**Heuristic-Include records:**

- **Video game loot boxes are linked to problem gambling: Results of a large-scale survey** (2018, *PLoS ONE*)
  - OpenAlex: W2901570581; PMID: 30462669; DOI: 10.1371/journal.pone.0206767
  - Heuristic reason: Loot box/gacha research with game connection
- **Why people buy virtual items in virtual worlds with real money** (2007, *ACM SIGMIS Database the DATABASE for Advances in Information Systems*)
  - OpenAlex: W2106293368; PMID: n/a; DOI: 10.1145/1314234.1314247
  - Heuristic reason: Virtual item ownership / psychological ownership in games
- **Player Commitment to Massively Multiplayer Online Role-Playing Games (MMORPGs): An Integrated Model** (2013, *International Journal of Electronic Commerce*)
  - OpenAlex: W2015258583; PMID: n/a; DOI: 10.2753/jec1086-4415170401
  - Heuristic reason: Virtual item ownership / psychological ownership in games
- **Cash Trade in Free-to-Play Online Games** (2010, *Games and Culture*)
  - OpenAlex: W2135693853; PMID: n/a; DOI: 10.1177/1555412010364981
  - Heuristic reason: Virtual item ownership / psychological ownership in games
- **Psychometric validation of the Persian nine-item Internet Gaming Disorder Scale – Short Form: Does gender and hours spent online gaming affe** (2017, *Journal of Behavioral Addictions*)
  - OpenAlex: W2620820165; PMID: 28571474; DOI: 10.1556/2006.6.2017.025
  - Heuristic reason: Gaming disorder study with spending/purchasing component
- **The association between problematic online gaming and perceived stress: The moderating effect of psychological resilience** (2019, *Journal of Behavioral Addictions*)
  - OpenAlex: W2906683871; PMID: 30739461; DOI: 10.1556/2006.8.2019.01
  - Heuristic reason: Gaming disorder study with spending/purchasing component
- **Predatory Monetisation? A Categorisation of Unfair, Misleading and Aggressive Monetisation Techniques in Digital Games from the Player Persp** (2021, *Journal of Business Ethics*)
  - OpenAlex: W3208693143; PMID: n/a; DOI: 10.1007/s10551-021-04970-6
  - Heuristic reason: Microtransaction/in-game spending research
- **Framework for Designing and Evaluating Game Achievements** (2011, **)
  - OpenAlex: W161555447; PMID: n/a; DOI: 10.26503/dl.v2011i1.545
  - Heuristic reason: Game achievement/completionism research
- **Loot boxes, problem gambling and problem video gaming: A systematic review and meta-synthesis** (2021, *New Media & Society*)
  - OpenAlex: W3185081605; PMID: n/a; DOI: 10.1177/14614448211027175
  - Heuristic reason: Loot box/gacha research with game connection
- **Towards an Ethical Game Design Solution to Loot Boxes: a Commentary on King and Delfabbro** (2019, *International Journal of Mental Health and Addiction*)
  - OpenAlex: W2996631257; PMID: n/a; DOI: 10.1007/s11469-019-00164-4
  - Heuristic reason: Loot box/gacha research with game connection
- **Game Design as Marketing: How Game Mechanics Create Demand for Virtual Goods** (2010, *Econstor (Econstor)*)
  - OpenAlex: W3125924051; PMID: n/a; DOI: n/a
  - Heuristic reason: Virtual item ownership / psychological ownership in games
- **The Industry of Landlords: Exploring the Assetization of the Triple-A Game** (2021, *Games and Culture*)
  - OpenAlex: W3157054077; PMID: n/a; DOI: 10.1177/15554120211014151
  - Heuristic reason: Free-to-play game monetization research
- **Loot box purchases and their relationship with internet gaming disorder and online gambling disorder in adolescents: A prospective study** (2023, *Computers in Human Behavior*)
  - OpenAlex: W4320340857; PMID: n/a; DOI: 10.1016/j.chb.2023.107685
  - Heuristic reason: Loot box/gacha research with game connection

**LLM recheck verdicts (3 Claude models):**

| OpenAlex ID | Title (first 90c) | Haiku | Sonnet | Opus | Consensus |
|---|---|---|---|---|---|
| W2901570581 | Video game loot boxes are linked to problem gambling: Results of a large-scale survey | Include | Include | Include | **Include** (unanimous) |
| W2106293368 | Why people buy virtual items in virtual worlds with real money | Maybe | Exclude | Maybe | split |
| W2015258583 | Player Commitment to Massively Multiplayer Online Role-Playing Games (MMORPGs): An Integra | Exclude | Maybe | Maybe | split |
| W2135693853 | Cash Trade in Free-to-Play Online Games | Exclude | Exclude | Maybe | split |
| W2620820165 | Psychometric validation of the Persian nine-item Internet Gaming Disorder Scale – Short Fo | Exclude | Exclude | Exclude | **Exclude** (unanimous) |
| W2906683871 | The association between problematic online gaming and perceived stress: The moderating eff | Exclude | Exclude | Exclude | **Exclude** (unanimous) |
| W3208693143 | Predatory Monetisation? A Categorisation of Unfair, Misleading and Aggressive Monetisation | Maybe | Exclude | Maybe | split |
| W161555447 | Framework for Designing and Evaluating Game Achievements | Maybe | Maybe | Maybe | **Maybe** (unanimous) |
| W3185081605 | Loot boxes, problem gambling and problem video gaming: A systematic review and meta-synthe | Include | Include | Include | **Include** (unanimous) |
| W2996631257 | Towards an Ethical Game Design Solution to Loot Boxes: a Commentary on King and Delfabbro | Exclude | Exclude | Exclude | **Exclude** (unanimous) |
| W3125924051 | Game Design as Marketing: How Game Mechanics Create Demand for Virtual Goods | Exclude | Exclude | Exclude | **Exclude** (unanimous) |
| W3157054077 | The Industry of Landlords: Exploring the Assetization of the Triple-A Game | Exclude | Exclude | Exclude | **Exclude** (unanimous) |
| W4320340857 | Loot box purchases and their relationship with internet gaming disorder and online gamblin | Include | Include | Include | **Include** (unanimous) |

- LLM-confirmed-Include (unanimous): **3** → band: Moderate evidence remains moderate; add to literature pool.

## Headline

- **D1**: paper §3.1 moderate-evidence claim corroborated. No unanimous-Include novel records.
- **D4**: moderate evidence remains moderate; 3 novel record(s) to add. §3.4 narrative unchanged.

**Coverage caveat.** OpenAlex coverage of HCI, game-studies, and Japanese-language non-Crossref-registered work remains incomplete. Corroboration is one-sided.