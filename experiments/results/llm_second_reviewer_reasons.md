# Disagreement Reasoning Analysis

Subset: the 51-paper reaffirmed-disagreement set (unanimous 3-tier majority differs from heuristic; computed from `sc_state.jsonl` as in `analyze_self_consistency.py`).

All reasons below are model outputs from the Claude 4-5 / 4-6 / 4-7 family screeners (see protocol §5). Reasons are presented verbatim, capped at 25 words each by the prompt template (`prompt_v1.txt`).

## Axis distribution

| Disagreement axis | n papers |
|---|---|
| heuristic=Maybe → LLM consensus=Exclude | 36 |
| heuristic=Include → LLM consensus=Exclude | 13 |
| heuristic=Include → LLM consensus=Maybe | 2 |

## Axis: heuristic=Maybe → LLM consensus=Exclude (n=36)

Reasons collected: **432** (avg per paper: 12.0).

**Top 12 bigrams (after stopword removal):**

- loot boxes (101)
- loot box (70)
- behavioral addictions (70)
- virtual item (48)
- gaming disorder (39)
- loss aversion (39)
- compulsive buying (34)
- game mechanic (31)
- game component (28)
- focus loot (26)
- boxes inventory (26)
- inventory completionism (26)

**Top 8 trigrams:**

- focus loot boxes (26)
- loot boxes inventory (26)
- loot boxes completionism (22)
- game mechanic virtual (18)
- inventory loot box (17)
- mechanic virtual item (17)
- without original data (16)
- virtual item component (15)

**Representative papers (first 3 by PMID, with verbatim reasons):**

### PMID 18710846 — 2008, *BMJ (Clinical research ed.)*
> Ethnic stereotypes and the underachievement of UK medical students from ethnic minorities: qualitative study.

- **haiku** (verdicts: primary=Exclude, sc#0=Exclude, sc#2=Exclude, sc#1=Exclude)
  - `primary` → Exclude: "Examines ethnic stereotypes in medical student education; no gaming or hoarding content."
  - `sc#0` → Exclude: "Medical education study on ethnic stereotypes; no connection to digital games, gaming behaviors, or hoarding constructs."
  - `sc#2` → Exclude: "Examines ethnic stereotypes in medical education with no connection to games, hoarding, or digital contexts."
  - `sc#1` → Exclude: "Unrelated to digital games; concerns medical education and stereotype threat in medical school."

- **sonnet** (verdicts: primary=Exclude, sc#0=Exclude, sc#1=Exclude, sc#2=Exclude)
  - `primary` → Exclude: "Study concerns medical education and ethnic stereotypes with no game, hoarding, or virtual behavior component."
  - `sc#0` → Exclude: "Study examines ethnic stereotypes in medical education; no game behavior, hoarding, or related constructs."
  - `sc#1` → Exclude: "Medical education study on ethnic stereotypes; no game behavior or hoarding constructs involved."
  - `sc#2` → Exclude: "Study concerns ethnic stereotypes in medical education; no game behavior, hoarding, or virtual item constructs."

- **opus** (verdicts: primary=Exclude, sc#0=Exclude, sc#1=Exclude, sc#2=Exclude)
  - `primary` → Exclude: "Qualitative study on ethnic stereotypes and medical student achievement; no game or hoarding component."
  - `sc#0` → Exclude: "Qualitative study on ethnic stereotypes in medical education; no game or hoarding component."
  - `sc#1` → Exclude: "Qualitative study on ethnic stereotypes and medical student underachievement; unrelated to games or hoarding behaviors."
  - `sc#2` → Exclude: "Qualitative study on ethnic stereotypes and medical student underachievement; no game or hoarding component."

### PMID 19839446 — 2009, *Harvard business review*
> The five traps of performance measurement.

- **haiku** (verdicts: primary=Exclude, sc#0=Exclude, sc#2=Exclude, sc#1=Exclude)
  - `primary` → Exclude: "Non-game paper on business performance metrics; no gaming, hoarding, or psychology content."
  - `sc#0` → Exclude: "Business metrics commentary without game context, behavioral hoarding, or original empirical data."
  - `sc#2` → Exclude: "Business performance measurement practitioner article; no relevance to game behavior, hoarding, or any domain."
  - `sc#1` → Exclude: "Entirely about corporate performance measurement; contains no gaming, hoarding, or behavioral gaming content."

- **sonnet** (verdicts: primary=Exclude, sc#0=Exclude, sc#1=Exclude, sc#2=Exclude)
  - `primary` → Exclude: "Business performance measurement article with no game component, virtual items, or hoarding-related psychological constructs."
  - `sc#0` → Exclude: "Business performance measurement article with no game component, virtual items, or hoarding-related behavioral constructs."
  - `sc#1` → Exclude: "Business performance measurement paper with no game, hoarding, or psychological behavior component."
  - `sc#2` → Exclude: "Business performance measurement article with no game component, virtual items, or hoarding-related behavioral constructs."

- **opus** (verdicts: primary=Exclude, sc#0=Exclude, sc#1=Exclude, sc#2=Exclude)
  - `primary` → Exclude: "Business performance measurement article unrelated to digital games or hoarding behaviors."
  - `sc#0` → Exclude: "Business performance measurement article unrelated to digital games or hoarding behaviors."
  - `sc#1` → Exclude: "Business article on corporate performance measurement; no game context or hoarding-related behavior."
  - `sc#2` → Exclude: "Business article on corporate performance measurement; no game or hoarding behavior content."

### PMID 23604411 — 2013, *Der Nervenarzt*
> [The concept of behavioral addiction and limits of the term addiction].

- **haiku** (verdicts: primary=Exclude, sc#1=Exclude, sc#0=Exclude, sc#2=Exclude)
  - `primary` → Exclude: "Position paper on behavioral addiction nosology; lacks empirical data and game-specific behavioral analysis."
  - `sc#1` → Exclude: "German journal (not English/Japanese); conceptual discussion without empirical data; no game-behavior specificity."
  - `sc#0` → Exclude: "Conceptual discussion of behavioral addiction, not empirical research. Matches exclusion criterion 4 (opinion without original data)."
  - `sc#2` → Exclude: "Conceptual discussion of behavioral addiction; not game-specific empirical research on game hoarding behaviors."

- **sonnet** (verdicts: primary=Exclude, sc#0=Exclude, sc#1=Exclude, sc#2=Exclude)
  - `primary` → Exclude: "Conceptual/nosological discussion of behavioral addiction with no game-specific behavioral or psychological data."
  - `sc#0` → Exclude: "Conceptual/nosological piece on behavioral addiction without game-specific behavioral or psychological data on hoarding-related constructs."
  - `sc#1` → Exclude: "Conceptual/nosological piece on behavioral addiction categories; no game-specific behavioral or psychological data on hoarding-related constructs."
  - `sc#2` → Exclude: "Conceptual/nosological piece on behavioral addiction with no game-specific behavioral or psychological data relevant to review domains."

- **opus** (verdicts: primary=Exclude, sc#0=Exclude, sc#1=Exclude, sc#2=Exclude)
  - `primary` → Exclude: "Conceptual discussion of behavioral addiction nosology without original data or specific hoarding-related game behavior measures."
  - `sc#0` → Exclude: "Conceptual discussion of behavioral addiction nosology without empirical data on game hoarding, loot boxes, or related domain behaviors."
  - `sc#1` → Exclude: "Conceptual discussion of behavioral addiction nosology without empirical data on game hoarding, loot boxes, or related domains."
  - `sc#2` → Exclude: "Conceptual commentary on behavioral addiction nosology without original data on game hoarding behaviors."


## Axis: heuristic=Include → LLM consensus=Exclude (n=13)

Reasons collected: **172** (avg per paper: 13.2).

**Top 12 bigrams (after stopword removal):**

- original data (55)
- without original (53)
- behavioral psychological (48)
- psychological measures (41)
- loot box (26)
- excluded per (24)
- data excluded (21)
- loot boxes (19)
- piece without (16)
- without behavioral (16)
- measures collecting (14)
- exclusion criterion (14)

**Top 8 trigrams:**

- without original data (49)
- behavioral psychological measures (35)
- original data excluded (21)
- data excluded per (21)
- piece without original (16)
- without behavioral psychological (16)
- psychological measures collecting (14)
- commentary without original (14)

**Representative papers (first 3 by PMID, with verbatim reasons):**

### PMID 30110801 — 2018, *Physical review. E*
> Behavior analysis of virtual-item gambling.

- **haiku** (verdicts: primary=Exclude, sc#1=Exclude, sc#2=Exclude, sc#0=Maybe)
  - `primary` → Exclude: "Statistical physics analysis of gambling logs with no behavioral or psychological measures; disconnected from hoarding constructs."
  - `sc#1` → Exclude: "Mathematical analysis of virtual-item gambling using random walk theory; lacks behavioral or psychological measures of hoarding, collecting, or inventory behaviors."
  - `sc#2` → Exclude: "Mathematical analysis of gambling dynamics; lacks behavioral measures or item hoarding focus."
  - `sc#0` → Maybe: "Empirical gambling behavior analysis; unclear if addresses hoarding or loss-aversion psychological measures."

- **sonnet** (verdicts: primary=Exclude, sc#0=Exclude, sc#1=Exclude, sc#2=Exclude)
  - `primary` → Exclude: "Physics study analyzing gambling diffusion dynamics with no game mechanic, behavioral, or psychological hoarding construct."
  - `sc#0` → Exclude: "Statistical physics analysis of gambling logs with no behavioral/psychological measures and no game mechanic or loot box component."
  - `sc#1` → Exclude: "Statistical physics analysis of gambling logs with no behavioral/psychological measures and no game mechanic component."
  - `sc#2` → Exclude: "Statistical physics analysis of gambling logs; no game mechanic, behavioral, or psychological hoarding construct examined."

- **opus** (verdicts: primary=Exclude, sc#0=Exclude, sc#1=Exclude, sc#2=Exclude)
  - `primary` → Exclude: "Statistical physics analysis of online lottery gambling logs without game mechanic, psychological, or hoarding-related behavioral measures."
  - `sc#0` → Exclude: "Statistical physics analysis of online lottery gambling logs without behavioral/psychological measures or loot box/gacha game mechanic connection."
  - `sc#1` → Exclude: "Statistical physics analysis of online lottery gambling logs without behavioral/psychological measures or loot box/gacha game mechanic connection."
  - `sc#2` → Exclude: "Statistical physics analysis of gambling logs as random walks; no behavioral or psychological measures of hoarding, collecting, or loot box mechanics."

### PMID 34992568 — 2021, *Frontiers in psychology*
> Impact of Personality Traits on Knowledge Hiding: A Comparative Study on Technology-Based Online and Physical Education.

- **haiku** (verdicts: primary=Exclude, sc#0=Exclude, sc#1=Exclude, sc#2=Exclude)
  - `primary` → Exclude: "Studies organizational knowledge hiding; no digital games, virtual items, or gaming-related hoarding behavior examined."
  - `sc#0` → Exclude: "Paper concerns organizational knowledge hiding, not game-related hoarding behaviors. No game context present."
  - `sc#1` → Exclude: "Organizational knowledge hiding study; no game mechanics, behaviors, or game-related constructs examined."
  - `sc#2` → Exclude: "No game context, gaming behaviors, or game-related constructs examined. Study focuses on knowledge hiding in organizations. Out of scope."

- **sonnet** (verdicts: primary=Exclude, sc#0=Exclude, sc#1=Exclude, sc#2=Exclude)
  - `primary` → Exclude: "Studies organizational knowledge hiding in education contexts; no game component or hoarding-disorder connection."
  - `sc#0` → Exclude: "Study examines knowledge hiding in organizations, not game behavior or hoarding-related constructs in digital games."
  - `sc#1` → Exclude: "Study examines knowledge hiding in organizations, not game behavior or hoarding-related constructs in digital games."
  - `sc#2` → Exclude: "Study examines knowledge hiding in organizations; no game component, virtual items, or relevant behavioral domains."

- **opus** (verdicts: primary=Exclude, sc#0=Exclude, sc#2=Exclude, sc#1=Exclude)
  - `primary` → Exclude: "Study examines knowledge hiding among managers in organizations, not game behavior or virtual item hoarding."
  - `sc#0` → Exclude: "Study examines knowledge hiding in workplace organizations, not game behavior or hoarding-related constructs in digital games."
  - `sc#2` → Exclude: "Study examines knowledge hiding and personality traits in workplace organizations, with no game component or hoarding-related game behavior."
  - `sc#1` → Exclude: "Study examines knowledge hiding in organizational contexts, not games or any hoarding-related game behavior."

### PMID 35954678 — 2022, *International journal of environmental research and public health*
> Response to the Regulation of Video Games under the Youth Media Protection Act: A Public Health Perspective.

- **haiku** (verdicts: primary=Exclude, sc#2=Exclude, sc#0=Exclude, sc#1=Exclude)
  - `primary` → Exclude: "Policy commentary on game regulation without original empirical data on hoarding behaviors."
  - `sc#2` → Exclude: "Policy commentary on game regulation without original empirical data on player hoarding or collecting behavior."
  - `sc#0` → Exclude: "Policy commentary on regulation without empirical study or original behavioral data."
  - `sc#1` → Exclude: "Commentary on regulation without original empirical data on hoarding-related game behaviors."

- **sonnet** (verdicts: primary=Exclude, sc#0=Exclude, sc#1=Exclude, sc#2=Exclude)
  - `primary` → Exclude: "Policy/regulatory commentary on loot boxes without original behavioral or psychological empirical data; no hoarding-related measures."
  - `sc#0` → Exclude: "Policy/regulatory commentary without original behavioral or psychological data; focused on legislation, not empirical game behavior study."
  - `sc#1` → Exclude: "Policy/regulatory commentary on loot boxes without empirical behavioral or psychological data; no original data collected."
  - `sc#2` → Exclude: "Policy/regulatory commentary on loot boxes without behavioral or psychological measures; no original empirical data on hoarding-related behavior."

- **opus** (verdicts: primary=Exclude, sc#0=Exclude, sc#2=Exclude, sc#1=Exclude)
  - `primary` → Exclude: "Policy commentary on video game regulation without original empirical data or behavioral/psychological measures."
  - `sc#0` → Exclude: "Policy/regulatory commentary on video game legislation without original empirical data or behavioral measures."
  - `sc#2` → Exclude: "Policy/regulatory commentary on video game legislation and loot boxes without original empirical data or behavioral measures."
  - `sc#1` → Exclude: "Policy/regulatory commentary on video game legislation without original empirical data or behavioral measures."


## Axis: heuristic=Include → LLM consensus=Maybe (n=2)

Reasons collected: **28** (avg per paper: 14.0).

**Top 12 bigrams (after stopword removal):**

- loot box (14)
- gaming communities (10)
- full-text needed (9)
- box purchase (9)
- skin betting (9)
- gambling severity (8)
- monetary gaming (8)
- purchase skin (6)
- includes loot (6)
- problem gambling (5)
- primary focus (5)
- gambling gaming (5)

**Top 8 trigrams:**

- loot box purchase (9)
- box purchase skin (6)
- purchase skin betting (6)
- includes loot box (6)
- full-text needed assess (4)
- problem gambling severity (4)
- gambling severity without (4)
- collecting behavior directly (4)

**Representative papers (first 3 by PMID, with verbatim reasons):**

### PMID 32306232 — 2021, *Journal of gambling studies*
> The Role of Virtual Communities in Gambling and Gaming Behaviors: A Systematic Review.

- **haiku** (verdicts: primary=Maybe, sc#1=Maybe, sc#0=Maybe, sc#2=Maybe, sc#0=Maybe, sc#1=Maybe, sc#2=Maybe)
  - `primary` → Maybe: "Systematic review of gaming communities and monetary gaming; primary focus is community influence mechanisms, not hoarding-specific behaviors per protocol."
  - `sc#1` → Maybe: "Reviews gaming with monetary features and behavioral outcomes; full-text needed to verify studies examine hoarding/loss-aversion domains."
  - `sc#0` → Maybe: "Mixed review of gambling and gaming; loot box inclusion relevant but full-text needed to assess scope."
  - `sc#2` → Maybe: "Systematic review on gaming communities with monetary features; may discuss gacha/loot box communities; requires full-text assessment of behavioral focus."
  - `sc#0` → Maybe: "Systematic review of monetary gaming communities; explicitly mentions loot boxes, but primary focus on social influence mechanisms rather than hoarding-related behavioral outcomes."
  - `sc#1` → Maybe: "Systematic review on gaming communities and monetization; may discuss loot box/gacha but needs full-text to confirm."
  - `sc#2` → Maybe: "Systematic review on monetary gaming and online communities; requires full-text to confirm hoarding-behavioral domain focus."

- **sonnet** (verdicts: primary=Maybe, sc#0=Maybe, sc#1=Maybe, sc#2=Maybe, sc#0=Maybe)
  - `primary` → Maybe: "Reviews monetary gaming/microtransaction communities tangentially touching loot box behavior, but focuses on social influence rather than hoarding constructs."
  - `sc#0` → Maybe: "Covers monetary gaming and microtransactions but focuses on community/social factors, not collecting or hoarding behavior directly."
  - `sc#1` → Maybe: "Covers microtransactions and monetary gaming communities but focuses on social dynamics, not collecting/hoarding behavior directly; full-text needed."
  - `sc#2` → Maybe: "Covers monetary gaming and microtransactions but focuses on virtual communities and social influence, not collecting or hoarding behavior directly."
  - `sc#0` → Maybe: "Covers microtransactions and monetary gaming communities but focuses on social influence, not collecting or hoarding behavior directly."

- **opus** (verdicts: primary=Maybe, sc#0=Maybe, sc#1=Maybe, sc#2=Maybe)
  - `primary` → Maybe: "Systematic review of online gambling/gaming communities touches microtransactions and purchase intentions but focuses on community dynamics rather than hoarding behaviors directly."
  - `sc#0` → Maybe: "Systematic review of online gambling/gaming communities touches microtransactions and purchase intentions but focus is community influence, not hoarding behaviors directly."
  - `sc#1` → Maybe: "Systematic review of online gambling/gaming communities touches microtransactions and purchase intentions but focuses on community influence rather than hoarding behaviors directly."
  - `sc#2` → Maybe: "Systematic review of online gambling/gaming communities touches microtransactions and purchase intentions but focuses on community influence rather than hoarding behaviors directly."

### PMID 36606732 — 2023, *Addiction (Abingdon, England)*
> The relationship between problematic gambling severity and engagement with gambling products: Longitudinal analysis of the Emerging Adults Gambling Survey.

- **haiku** (verdicts: primary=Maybe, sc#2=Maybe, sc#0=Maybe, sc#1=Maybe)
  - `primary` → Maybe: "Examines loot boxes within broader gambling study; analysis doesn't emphasize game-specific hoarding behaviors."
  - `sc#2` → Maybe: "Paper examines loot boxes in games but primarily studies problem gambling; full-text needed to assess relevance to hoarding behaviors."
  - `sc#0` → Maybe: "Explicitly examines loot box purchase and skin betting in games linked to problem gambling severity, but primary focus is gambling severity across all modalities."
  - `sc#1` → Maybe: "Includes loot box purchase among studied gambling activities but primarily measures problem gambling severity; full-text review needed."

- **sonnet** (verdicts: primary=Maybe, sc#0=Maybe, sc#1=Maybe, sc#2=Maybe)
  - `primary` → Maybe: "Includes loot box purchase and skin betting as gambling-like game mechanics, but focus is gambling severity without clear game-behavior hoarding link."
  - `sc#0` → Maybe: "Covers loot box purchase and skin betting with psychological measures, but primary focus is general gambling severity without game mechanic emphasis."
  - `sc#1` → Maybe: "Includes loot box purchase and skin betting as gambling-like game mechanics, but focus is primarily pure gambling severity without game-behavioral measures."
  - `sc#2` → Maybe: "Includes loot box and skin betting as gambling-like game mechanics but focuses primarily on problem gambling severity without game-behavioral hoarding measures."

- **opus** (verdicts: primary=Maybe, sc#0=Maybe, sc#1=Maybe, sc#2=Maybe)
  - `primary` → Maybe: "Gambling survey includes loot box purchase and skin betting as activities linked to problem gambling severity; full-text needed to assess game-mechanic focus."
  - `sc#0` → Maybe: "Includes loot box purchase and skin betting as gambling activities linked to PGSI, but primary focus is gambling forms; full-text review needed."
  - `sc#1` → Maybe: "Includes skin betting and loot box purchase as gambling activities, but framed as gambling study; full-text needed to assess game-mechanic relevance."
  - `sc#2` → Maybe: "Includes skin betting and loot box purchase as gambling activities linked to PGSI, but primarily a gambling study; full-text review needed."


## Cross-LLM reason agreement on the same paper

For each reaffirmed-disagreement paper, we measure jaccard similarity of stopword-free token sets between the **primary-run reason** of each model pair, and report the mean across the 51-paper set.

| pair | mean jaccard | n papers |
|---|---|---|
| haiku ↔ sonnet | 0.209 | 51 |
| haiku ↔ opus | 0.260 | 51 |
| opus ↔ sonnet | 0.294 | 51 |

A mean jaccard of ~0.2-0.3 indicates the models name *different* specific evidence (words/phrases) even when they converge on the same verdict; a mean of ~0.5+ indicates they cite the same evidence. Either pattern is informative: the former shows three independent paths to the same verdict; the latter shows shared training-data fingerprints.

## Headline

- The largest reaffirmed-disagreement axis is **heuristic=Maybe → LLM consensus=Exclude** (36 papers).
- This axis matches the dominant pattern reported in the primary run and self-consistency follow-up: the heuristic's `Maybe` tier is the locus where automated screeners diverge most consistently.
- Top bigrams in the dominant axis's reasons: "loot boxes" (101), "loot box" (70), "behavioral addictions" (70)

**No new validity claim.** Lexical patterns describe *what the screeners said*, not whether they were right. Human triage on this 51-paper subset is the next step.