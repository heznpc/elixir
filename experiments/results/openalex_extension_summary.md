# OpenAlex Extension — Summary

Pre-registered protocol: `experiments/openalex_extension/protocol.md`.

OpenAlex hits (pre-dedup): D2 = 200, D6 = 200.
Queries hash: `8b2dd4ac3192b085`.

Duplicates removed: pmid=1 | doi=0 | title jaccard≥0.85=0.

Novel records (surviving dedup): **399**.

## Per-domain decision-rule outcome

| Domain | Novel total | Heuristic Include | Heuristic Maybe | Heuristic Exclude | Decision-rule outcome |
|---|---|---|---|---|---|
| D2 | 199 | **6** | 87 | 106 | Evidence is sparse but the void claim is not supported. |
| D6 | 200 | **5** | 103 | 92 | Evidence is sparse but the void claim is not supported. |

## Heuristic-Include novel records (load-bearing for decision rule)

### D2: 6 record(s)

- **The balance between monetization and player retention for free-to-play real-time strategy mobile games** (2020, **)
  - OpenAlex ID: W3214209540; PMID: n/a; DOI: 10.17760/d20420747
  - Heuristic reason: Free-to-play game monetization research
- **Q-SLICE CCCE AI Containment Framework: Provably Beneficial AI Through Quantum-Grounded Negative Feedback** (2025, *Zenodo (CERN European Organization for Nuclear Research)*)
  - OpenAlex ID: W7115059379; PMID: n/a; DOI: 10.5281/zenodo.17918211
  - Heuristic reason: Player collecting/hoarding behavior in games
- **Q-SLICE CCCE AI Containment Framework: Provably Beneficial AI Through Quantum-Grounded Negative Feedback** (2025, *Zenodo (CERN European Organization for Nuclear Research)*)
  - OpenAlex ID: W7115073252; PMID: n/a; DOI: 10.5281/zenodo.17918210
  - Heuristic reason: Player collecting/hoarding behavior in games
- **Q-SLICE CCCE AI Containment Framework: Provably Beneficial AI Through Quantum-Grounded Negative Feedback** (2025, *Zenodo (CERN European Organization for Nuclear Research)*)
  - OpenAlex ID: W7115071661; PMID: n/a; DOI: 10.5281/zenodo.17918294
  - Heuristic reason: Player collecting/hoarding behavior in games
- **Q-SLICE CCCE AI Containment Framework: Provably Beneficial AI Through Quantum-Grounded Negative Feedback** (2025, *Zenodo (CERN European Organization for Nuclear Research)*)
  - OpenAlex ID: W7115071033; PMID: n/a; DOI: 10.5281/zenodo.17918293
  - Heuristic reason: Player collecting/hoarding behavior in games
- **"A Study on Establishing tariff and non-tariff barrier classifications for virtual goods and services"** (2026, *International Journal For Multidisciplinary Research*)
  - OpenAlex ID: W7130820856; PMID: n/a; DOI: 10.36948/ijfmr.2026.v08i01.69598
  - Heuristic reason: Virtual item ownership / psychological ownership in games

### D6: 5 record(s)

- **Game Production Studies** (2021, *Amsterdam University Press eBooks*)
  - OpenAlex ID: W4235707818; PMID: n/a; DOI: 10.1515/9789048551736
  - Heuristic reason: Game monetization research
- **“I’m not hoarding, I’m just stocking up before the hoarders get here.”** (2015, *Journal of Operations Management*)
  - OpenAlex ID: W1428487783; PMID: n/a; DOI: 10.1016/j.jom.2015.07.002
  - Heuristic reason: Player collecting/hoarding behavior in games
- **Game Production Studies** (2021, **)
  - OpenAlex ID: W3135872807; PMID: n/a; DOI: 10.5117/9789048551736
  - Heuristic reason: Game monetization research
- **'If you are feeling bold, ask for $3': Value Crafting and Indie Game Developers** (2018, *Transactions of the Digital Games Research Association*)
  - OpenAlex ID: W2904059041; PMID: n/a; DOI: 10.26503/todigra.v4i2.89
  - Heuristic reason: Microtransaction/in-game spending research
- **Disabled Gamers: Accessibility in Video Games** (2018, **)
  - OpenAlex ID: W2900459466; PMID: n/a; DOI: 10.22215/etd/2018-12713
  - Heuristic reason: Microtransaction/in-game spending research

## LLM recheck on Heuristic-Include records (protocol §6)

Three Claude models (Opus 4-7, Sonnet 4-6, Haiku 4-5) re-screened each Heuristic-Include record with the same criteria the LLM-second-reviewer audit used. Verdicts:

| OpenAlex ID | Domain | Title (first 100c) | Haiku | Sonnet | Opus | LLM consensus |
|---|---|---|---|---|---|---|
| W3214209540 | D2 | The balance between monetization and player retention for free-to-play real-time strategy mobile gam | Exclude | Exclude | Exclude | **Exclude** (unanimous) |
| W7115059379 | D2 | Q-SLICE CCCE AI Containment Framework: Provably Beneficial AI Through Quantum-Grounded Negative Feed | Exclude | Exclude | Exclude | **Exclude** (unanimous) |
| W7115073252 | D2 | Q-SLICE CCCE AI Containment Framework: Provably Beneficial AI Through Quantum-Grounded Negative Feed | Exclude | Exclude | Exclude | **Exclude** (unanimous) |
| W7115071661 | D2 | Q-SLICE CCCE AI Containment Framework: Provably Beneficial AI Through Quantum-Grounded Negative Feed | Exclude | Exclude | Exclude | **Exclude** (unanimous) |
| W7115071033 | D2 | Q-SLICE CCCE AI Containment Framework: Provably Beneficial AI Through Quantum-Grounded Negative Feed | Exclude | Exclude | Exclude | **Exclude** (unanimous) |
| W7130820856 | D2 | "A Study on Establishing tariff and non-tariff barrier classifications for virtual goods and service | Exclude | Exclude | Exclude | **Exclude** (unanimous) |
| W4235707818 | D6 | Game Production Studies | Exclude | Exclude | Exclude | **Exclude** (unanimous) |
| W1428487783 | D6 | “I’m not hoarding, I’m just stocking up before the hoarders get here.” | Exclude | Exclude | Exclude | **Exclude** (unanimous) |
| W3135872807 | D6 | Game Production Studies | Exclude | Exclude | Exclude | **Exclude** (unanimous) |
| W2904059041 | D6 | 'If you are feeling bold, ask for $3': Value Crafting and Indie Game Developers | Exclude | Exclude | Exclude | **Exclude** (unanimous) |
| W2900459466 | D6 | Disabled Gamers: Accessibility in Video Games | Exclude | Exclude | Exclude | **Exclude** (unanimous) |

**LLM-Include after recheck:** D2 = **0**, D6 = **0** (unanimous Include across all 3 tiers).

## Headline

- D2 Heuristic-Include = **6** → Evidence is sparse but the void claim is not supported.
- D6 Heuristic-Include = **5** → Evidence is sparse but the void claim is not supported.

- **Heuristic Includes are non-zero but neither domain reaches the falsify threshold (10).** Per-domain decision rules apply; see table above for the exact band per domain.
- Important caveat from the parallel LLM-second-reviewer audit: the heuristic systematically over-includes commentary, off-topic, and non-empirical papers (PR #5 result). The heuristic-Include count is therefore an upper bound on the actual evidence count.
- **LLM recheck conclusion (load-bearing per protocol §6):** unanimous-Include after 3-model re-screening: D2 = **0**, D6 = **0**.
- Therefore **both D2 and D6 evidence-void claims are corroborated** when the heuristic's known over-inclusion bias is corrected via LLM re-screening. Paper §3.2 / §3.7 may stand. The OpenAlex extension is reported with this caveat and the LLM recheck as supplementary evidence.

**Coverage caveat.** OpenAlex coverage of practitioner blogs (Bycer, Game Wisdom), TV Tropes / Pixiv Dictionary, and Japanese-language non-Crossref-registered work remains incomplete. Absence of OpenAlex hits is therefore consistent with both 'no evidence' and 'evidence exists in venues OpenAlex does not index well.' The extension is one-sided per protocol §1.