# The Elixir Problem: A Systematic Review of In-Game Hoarding-Related Behaviors Through a Hoarding Disorder Framework

> Working title: "The Elixir Problem: A Systematic Review of In-Game Hoarding-Related Behaviors Through a Hoarding Disorder Framework"
> Venue candidates: Journal of Behavioral Addictions (rolling), CHI PLAY 2027
> Paper type: PRISMA systematic review + theoretical framework

---

## 1. Core Claim

In-game item retention behavior -- RPG consumable hoarding ("too good to use"), gacha character collection, inventory paralysis, Steam backlog accumulation -- shares core psychological mechanisms with hoarding disorder (loss aversion, emotional attachment, decision avoidance, acquisition-driven positive affect). These mechanisms are documented in scattered literatures (behavioral economics, game studies, gambling research, consumer psychology, HCI) but have never been unified under a hoarding framework. The clinical boundary between collecting and hoarding (Nordsletten & Mataix-Cols, 2012) has never been systematically applied to game contexts. This paper conducts the first systematic review unifying scattered evidence on in-game hoarding-related behaviors across five domains under a hoarding disorder framework. We map the evidence base, identify critical gaps, and propose a theoretical framework for understanding in-game hoarding.

---

## 2. The Elixir Problem

The "elixir problem" (also: "too good to use" syndrome; Japanese: ラストエリクサー症候群 / "Last Elixir Syndrome") is the tendency to hoard consumable items in RPGs -- potions, elixirs, rare ammunition -- and finish the game without ever using them. The term originates from Final Fantasy VI's "Last Elixir" (Megalixir), a full-party HP/MP restore that players infamously never use. This is not a niche meme; it is a robust behavioral pattern with documented psychological mechanisms:

- **Loss aversion** (Phillips, Klarkowski & Vistisen, 2020): Players in a Zelda-style adventure game experiment (CHI PLAY 2020) exhibited strong loss aversion bias across 18 decision points involving gold wagers at varying win:loss ratios, despite the temporary, digital nature of the game world. This remains the only controlled experimental study of loss aversion in a commercial-style video game context.
- **Endowment effect** (Toh, 2021; Krauss & Wienrich, 2025): Once an item is in inventory, its subjective value increases simply by virtue of possession. Krauss & Wienrich (2025) found in a 21-paper systematic review (CHI 2025) that psychological ownership of virtual objects operates through the same three routes as physical ownership: control, identity transfer, and intimate knowledge.
- **Sunk cost** (Toh, 2021): Items acquired through effort (boss drops, quest rewards) are harder to use/discard than purchased items. The behavioral economics of game decisions mirror real-world sunk cost patterns.
- **Decision avoidance** (Schwartz, 2004): Using a consumable requires deciding THIS is the optimal moment -- easier to defer indefinitely. Schwartz's "maximizer" profile (seeking the provably best option) maps directly to players who cannot identify the "right" moment to use an elixir.
- **Scarcity psychology** (Japanese popular psychology: もったいない精神 / "mottainai spirit"): The cultural concept of "wastefulness aversion" has been explicitly connected to the Last Elixir Syndrome in Japanese game culture discourse, though not yet in academic literature.

**Evidence strength:** MODERATE. Phillips et al. (2020) provides experimental evidence for loss aversion in games. Toh (2021) provides theoretical behavioral economics analysis. Engelstein (2020) provides a book-length treatment via MIT Press. However, no replication of Phillips et al. exists, no study has tested loss aversion in mobile games specifically, and no study has measured the prevalence or correlates of consumable hoarding. The phenomenon is robustly documented in game design literature (Bycer, multiple Game Wisdom articles; Gamasutra/Game Developer articles) but academically understudied.

---

## 3. Method: PRISMA Systematic Review Protocol

### 3.1 Registration

PROSPERO pre-registration of the systematic review protocol prior to conducting the search.

### 3.2 Databases

PubMed, PsycINFO, ACM Digital Library, IEEE Xplore, Scopus, Web of Science

### 3.3 Search Strategy

Full search string:
(hoard* OR collect* OR "loss aversion" OR "endowment effect" OR "sunk cost" OR "compulsive buying" OR "compulsive acquisition" OR "item retention" OR "inventory management" OR "completionism" OR "achievement hunting" OR "digital possession*") AND (game* OR "video game" OR "virtual" OR "loot box" OR "gacha" OR "inventory" OR "digital possession" OR "virtual item*" OR "microtransaction*" OR "backlog")

The search string will be adapted for each database's syntax requirements.

### 3.4 Inclusion Criteria

1. Peer-reviewed empirical studies (quantitative, qualitative, or mixed methods), systematic reviews, or meta-analyses
2. Published in English or Japanese (with translation verification)
3. Studies examining any of: in-game item retention, virtual item hoarding, loot box/gacha collecting behavior, inventory management behavior, game completionism/achievement hunting, game backlog accumulation, psychological ownership of virtual game items, or loss aversion in game contexts
4. Studies connecting game behavior to hoarding, OCD, compulsive buying, loss aversion, or collecting constructs
5. No date restriction on publication year

### 3.5 Exclusion Criteria

1. Non-peer-reviewed sources (grey literature, conference abstracts without full papers, game design practitioner articles, blog posts) -- these will be cited in the Discussion as supplementary context but excluded from the formal review
2. Studies examining digital hoarding (emails, files, photos) without a game component
3. Studies examining gambling without a game mechanic component (i.e., pure gambling studies with no loot box/gacha connection)
4. Editorials, commentaries, and opinion pieces without original data
5. Studies focused exclusively on game monetization economics without behavioral/psychological measures

### 3.6 Screening Process

Two-phase screening:
1. **Title and abstract screening:** Independent screening by two reviewers with disagreements resolved by discussion or a third reviewer
2. **Full-text review:** Application of inclusion/exclusion criteria to full texts; data extraction using standardized forms

### 3.7 Quality Assessment

Quality assessment tools by study type:
- **Randomized controlled trials:** Cochrane Risk of Bias tool (RoB 2)
- **Observational studies (cross-sectional, cohort):** Newcastle-Ottawa Scale (NOS)
- **Qualitative studies:** Critical Appraisal Skills Programme (CASP) qualitative checklist
- **Systematic reviews/meta-analyses:** AMSTAR 2
- **Case reports:** Joanna Briggs Institute (JBI) checklist for case reports

Each included study will be rated as high, moderate, or low quality. Quality ratings will be reported alongside findings and used to weight conclusions in the narrative synthesis.

### 3.8 Data Extraction

Standardized extraction form capturing: author(s), year, country, study design, sample size, population characteristics, game type/genre, domain of hoarding-related behavior (mapped to the 5-domain framework), measures used, key findings, effect sizes where available, and limitations.

### 3.9 Synthesis Method

Narrative synthesis organized by the five domains of the proposed framework (3 primary + 2 exploratory). Quantitative meta-analysis will be conducted where sufficient homogeneous studies exist (anticipated for the gacha/loot box domain only; other domains likely lack sufficient comparable studies). For all domains, synthesis will map findings to the Frost-Hartl CBT model components and DSM-5 hoarding disorder criteria.

### 3.10 Expected Yield

40-70 relevant papers across scattered fields, based on preliminary literature mapping. The gacha/loot box domain is expected to yield the largest number; consumable hoarding and backlog accumulation are expected to yield very few or zero peer-reviewed results.

---

## 4. Literature Map: Evidence Base by Domain

### 4.1 Loss Aversion in Games

**Strong evidence for the mechanism; limited game-specific empirical work.**

| Study | Method | Key Finding | Limitation |
|-------|--------|-------------|------------|
| Phillips, Klarkowski & Vistisen (2020) | Experiment, Zelda-style game, n=? | Strong loss aversion across 18 decision points despite virtual stakes | Single study, no replication |
| Engelstein (2020) | Book (MIT Press, *Achievement Relocked*) | Comprehensive treatment of loss aversion in game design; endowment effect, framing, regret | Not empirical; draws on existing behavioral economics |
| Toh (2021) | Theoretical analysis (Game Studies) | Maps behavioral economics concepts (loss aversion, endowment effect, sunk cost) to video game decision-making | Theoretical, not empirical |
| Salakari (2024) | Thesis, consumer psychology | Sunk cost fallacy and loss aversion drive retention in free-to-play mobile games | Student thesis, not peer-reviewed |

**Replication gap:** Loss aversion may not materialize for small stakes. A 2022 study (Cambridge, Judgment and Decision Making) found loss aversion did not appear for losses under ~$40. This complicates claims about virtual items with zero real-world value. [NEEDS EMPIRICAL VALIDATION]

**Mobile games gap:** No study tests loss aversion specifically in mobile game contexts despite these being the largest market. [NEEDS EMPIRICAL VALIDATION]

### 4.2 Consumable Hoarding (The Elixir) [EXPLORATORY -- limited peer-reviewed evidence]

**Pattern:** Accumulate rare consumables, never use them, finish game with full inventory.
**Mechanism:** Loss aversion + decision avoidance + scarcity psychology. Using an item is irreversible; NOT using it preserves optionality.

**Note on evidence classification:** This domain is classified as EXPLORATORY because it has near-zero peer-reviewed empirical evidence directly measuring the behavior. The evidence below consists of indirect academic support and extensive game design practitioner literature. This domain requires foundational empirical work before strong theoretical claims can be made.

**Academic evidence (indirect):**
- Phillips et al. (2020): Loss aversion in adventure game (indirect evidence)
- Engelstein (2020): Loss aversion and game design (extensive analysis)
- Toh (2021): Behavioral economics of game decisions (theoretical)

**Non-academic evidence (game design literature):**
- Bycer, J. (multiple): "Combating the Hoarding Syndrome in Game Design," "How Hoarding Encourages Bad Game Design" (Game Wisdom)
- Gamasutra/Game Developer: "Avoiding the Hoarder Trap in Game Design," "How to Stop Making Hoarders in Video Games"
- TV Tropes: "Too Awesome to Use" (extensive documentation of the pattern)
- BantArcade: "The Elixir Problem -- How to Encourage Players to Use their Potions"
- Japanese sources: ラストエリクサー症候群 documented on Pixiv Dictionary, MAROGAMES, multiple Japanese game analysis sites

**Research gap:** COMPLETE VOID in peer-reviewed literature specifically measuring the prevalence, correlates, or psychological profile of consumable hoarding behavior. This domain requires foundational empirical work including prevalence studies, behavioral measurement paradigms, and psychometric development.

### 4.3 Gacha/Loot Box Collection [PRIMARY -- strong evidence]

**Pattern:** Compulsive spending to collect characters/items, especially limited-time or "complete the set" targets.
**Mechanism:** Variable-ratio reinforcement + FOMO + set-completion compulsion + acquisition-driven positive affect (Frost et al., 1998: ~85% of clinical hoarders report excessive acquisition with positive emotional reinforcement).

**Strong evidence base. This is the best-studied domain.**

| Study | Method | N | Key Finding |
|-------|--------|---|-------------|
| Zendle et al. (2023) | Cross-sectional survey (NZ, AU, US) | 1,049 | Moderate positive relationship between loot box spending and OCD/hoarding symptomatology; greater spending associated with consumer regret |
| Spicer et al. (2022) | Systematic review & meta-synthesis | 13 pubs | r = .27 (loot boxes & problem gambling); r = .40 (loot boxes & problem gaming) |
| Tang et al. (2022) | Cross-sectional survey, Chinese young adults | ~500 | 25% of gacha gamers at high problem gambling risk; 40% moderate risk. Female gacha gamers also at high risk |
| Tang et al. (2025) | Cross-sectional, Hong Kong young adults | -- | Gameplay frequency and duration directly influenced gambling severity; gacha spending directly influences gambling severity |
| Shibuya et al. (2019) | Longitudinal (6-month), Japanese youth | 948 | Players exposed to higher limited-time gacha spent more money 6 months later |
| Biegun (2023) | Analysis (MDPI Information) | -- | Variable-ratio reinforcement schedule underlies gacha addiction; FOMO and limited-time events create compulsion cycles |
| Inaguma et al. (2024) | Clinical case report (Japan) | 1 | Gaming disorder case with large financial burden from gacha (Psychiatry and Clinical Neurosciences Reports) |
| Drummond et al. (2025) | Reanalysis (Royal Society Open Science) | -- | Loot box spending associated with greater psychological distress when normalized to disposable income |
| Zendle et al. (2023b) | Longitudinal replication (Canada) | -- | Loot box purchasers more likely to participate in gambling 6 months later; direct-purchase microtransactions did NOT predict gambling |
| Lopez-Gonzalez et al. (2024) | Cross-sectional (Spain), SEM | 542 | Problematic loot box use mediates the relationship between IGD and Online Gambling Disorder (JMIR Serious Games) |
| Zendle (2025) | Longitudinal (UK compliance) | -- | UK industry self-regulation achieves only 64% compliance on probability disclosure vs. South Korea's legally mandated 84% |

**Important methodological critique:** Tang et al. (2022) modified the Problem Gambling Severity Index by replacing "gambling" with "spending money on gacha mechanics." Subsequent commentary (Frontiers in Psychiatry, 2025) argues this creates a novel construct that does not validly measure problem gambling. This is a significant methodological concern for the entire gacha-gambling literature.

**FOMO and gacha:** An Indonesian study found r = .575 (p < .05) correlation between FOMO and Internet Gaming Disorder in gacha players (n = 101). [Small sample; NEEDS REPLICATION]

**Research gap:** No study has applied full DSM-5 hoarding disorder criteria to gacha collection behavior. [NEEDS EMPIRICAL VALIDATION]

### 4.4 Inventory Paralysis (MMORPGs) [PRIMARY -- moderate evidence]

**Pattern:** Inability to discard items in inventory-limited games (WoW, FFXIV, Destiny). Players purchase additional storage, create mule characters, maintain elaborate organizational systems.
**Mechanism:** Emotional attachment to items with personal history + psychological ownership + identity extension + labor-investment overvaluation.

| Study | Method | Key Finding |
|-------|--------|-------------|
| Watkins & Molesworth (2012) | Qualitative (Emerald) | Players form genuine emotional attachments to "irreplaceable" digital virtual goods despite immaterial nature and lack of legal ownership; attachment mirrors physical possession attachment |
| Krauss & Wienrich (2025) | Systematic review, 21 papers (CHI 2025) | Psychological ownership of virtual objects operates through self-efficacy, self-identity, and belonging motives; control, identity transfer, intimate knowledge routes |
| Belk (2013) | Theoretical (Journal of Consumer Research) | Extended self incorporates virtual/digital objects through dematerialization, reembodiment, sharing, co-construction, distributed memory. Cited 800+ times |
| Honarvar & Sepehrinia (2025) | Systematic review (SAGE Open) | Reviews 25 papers using Belk's framework (2013-2023); proposes "datafication" as sixth dimension of digital extended self |
| Koles (2025) | Qualitative, 20 French players (JCB) | Even cosmetic items offer perceived competitive advantages; player personas include collectors with identity-attachment motives |
| Koklic (2025) | Survey (n=625) + experiment (n=177) (JCB) | Psychological ownership positively related to both digital hoarding and digital piracy; collectivism moderates the relationship |

**The IKEA effect as a mechanism for inventory attachment:** The IKEA effect (Norton, Mochon & Ariely, 2012) -- the tendency to overvalue items one has personally created or customized -- provides a specific mechanism for inventory attachment beyond general endowment. Players who craft, enhance, or upgrade items invest labor that inflates subjective value disproportionate to functional utility. This is distinct from mere ownership (endowment effect) because it adds the labor-investment dimension particularly relevant to crafting/enhancement systems in RPGs and MMORPGs. A player who spent hours gathering materials and crafting a piece of armor will overvalue it relative to an equivalent item obtained through a vendor purchase, even if the items are functionally identical. This mechanism helps explain why players resist discarding crafted or upgraded items even when superior replacements are available -- the invested labor creates a psychological premium that the endowment effect alone does not account for.

**Research gap:** No quantitative measurement of inventory management time or its relationship to hoarding symptomatology. Player forums and game design literature extensively discuss the problem (MMORPG.com forums; Massively Overpowered "The Soapbox: The 'problem' with MMO hoarding"), but no academic study has measured it. [NEEDS EMPIRICAL VALIDATION]

### 4.5 Completionism [PRIMARY -- moderate evidence, Ovsiankina reframe]

**Pattern:** Compulsive drive to achieve 100% completion -- all achievements, all collectibles, all characters.
**Mechanism:** Achievement motivation + Ovsiankina effect (behavioral drive to resume/complete interrupted tasks) + set-completion drive.

| Study | Key Finding |
|-------|-------------|
| Yee (2006) | Factor-analytic player motivation model: Achievement component (advancement, mechanics, competition) identified from 30,000 MMORPG players; 10 components, Cronbach's alpha > .70 for most |
| Bartle (1996) | Achiever player type: accumulating/collecting archetype in MUDs |
| Demetrovics et al. (2011) | MOGQ: 7-factor gaming motivation model (social, escape, competition, coping, skill development, fantasy, recreation) from 3,818 gamers |
| Gursesli et al. (2024) | PMPVGs: New gaming motivation scale, 2,641 Italian participants |
| MOPS (2024) | 10-factor Motivation to Play Scale including achievement factor, validated with 1,294 participants |
| Ghibellini & Meier (2025) | Meta-analysis (Nature HSSRC): NO memory advantage for unfinished tasks (Zeigarnik effect NOT supported), BUT the Ovsiankina effect (behavioral drive to resume/complete interrupted tasks) WAS supported |

**Zeigarnik-to-Ovsiankina reframe:** The completionism mechanism was previously theorized to operate through the Zeigarnik effect -- the idea that unfinished tasks are better remembered, creating intrusive thoughts that drive completion. However, a 2025 meta-analysis (Ghibellini & Meier, 2025) found no reliable memory advantage for unfinished tasks, undermining the Zeigarnik effect as traditionally formulated. Crucially, the same meta-analysis DID support the Ovsiankina effect: a behavioral drive to resume and complete interrupted tasks, independent of any memory advantage. This distinction matters for understanding completionism in games. The mechanism is not "players remember uncompleted achievements more vividly" but rather "players experience a behavioral compulsion to resume and finish tasks once started, regardless of whether those tasks are better remembered." This reframe actually strengthens the connection to hoarding: completionism is about compulsive behavioral resumption -- a behavioral avoidance of the unfinished state -- rather than merely enhanced memory salience. This aligns more closely with the behavioral avoidance component of the Frost-Hartl CBT model of hoarding.

**Safe In Our World (2023):** "Obsessive Completionist Disorder" article explicitly examines the link between OCD and achievement hunting, noting the connection exists on a spectrum.

**Players' perceptions study (Kruse, 2016):** Self-described completionists are more likely to return to games they did not enjoy to finish achievements. Published in Computers in Human Behavior.

**Research gaps:**
- No validated scale specifically for gaming completionism exists. [NEEDS EMPIRICAL VALIDATION]
- No study examines when completionism becomes pathological by hoarding criteria. [NEEDS EMPIRICAL VALIDATION]
- Link between completionism and OCD measures is theorized but not empirically established in a game-specific context. [NEEDS EMPIRICAL VALIDATION]

### 4.6 Backlog Accumulation [EXPLORATORY -- very limited peer-reviewed evidence]

**Pattern:** Purchasing games (especially during sales) without playing them. Steam users report backlogs of hundreds of unplayed games.
**Mechanism:** Compulsive buying (Frost et al., 1998: 61% of clinical hoarders meet compulsive buying criteria) + scarcity effect of time-limited sales + perceived low price (Vinoi et al., 2024) + acquisition as end in itself.

**Note on evidence classification:** This domain is classified as EXPLORATORY because it has very limited peer-reviewed evidence directly examining game backlog accumulation as a psychological phenomenon. The evidence below draws primarily on adjacent literatures (compulsive buying, digital hoarding, virtual goods purchasing) that provide theoretical but not direct empirical support. This domain requires foundational empirical work.

| Study | Method | Key Finding |
|-------|--------|-------------|
| Frost et al. (1998) | Clinical study | 61% of clinical hoarders meet compulsive buying criteria; acquisition associated with positive affect |
| Vinoi et al. (2024) | Survey (J. Retailing & Consumer Services) | Perceived low price has positive impact on digital hoarding; discarding difficulty mediates between perceived low price and hoarding behavior |
| Hamari & Keronen (2017) | Meta-analysis, 24 studies (CHB) | 10 psychological constructs of virtual goods purchase: enjoyment, subjective norm, flow, attitude, service use intention, perceived ease of use, network size, perceived value, self-presentation, social presence |
| Impulse buying in games (2024) | Survey, n=389 | Mobile game use affects impulse buying; flow experience and virtual item drivers positively related to impulse buying tendency |

**Non-academic evidence:**
- Steam's own data (SteamSpy, SteamDB): Publicly available data on library sizes vs. hours played
- Game design journalism: The Game Crater, Ganker, Odyssey Online -- all analyze "backlog psychology" drawing on Schwartz (choice paralysis), scarcity effect, and social comparison

**Research gap:** COMPLETE VOID in peer-reviewed academic literature on game backlog accumulation as hoarding behavior. No academic study has examined Steam backlog, game library hoarding, or compulsive game buying specifically. This domain requires foundational empirical work including prevalence studies, behavioral characterization, and assessment of whether backlog accumulation constitutes a meaningful behavioral pattern or simply reflects rational consumer behavior in the context of aggressive digital sales.

---

## 5. Cross-Domain Evidence: Game Hoarding to Digital Hoarding to Physical Hoarding

**This is critical for the paper's clinical relevance.**

| Study | Method | Key Finding |
|-------|--------|-------------|
| Thorpe, Bolster & Neave (2019) | Survey, n=282 (Digital Health) | Physical hoarding and digital hoarding correlated at r = .55 (p < .001). OCD correlated with digital hoarding at r = .58. Only OCD and physical hoarding predicted digital hoarding in regression |
| Luxon, Hamilton, Bates & Chasson (2019) | Experiment, n=101 Pinterest users (JOCRD) | Electronic object attachment mediated the relationship between hoarding severity and distress when asked to discard electronic possessions |
| Neave et al. (2019) | Scale development, 2 samples (CHB) | Digital Hoarding Questionnaire (DHQ): 10-item measure of accumulation and difficulty deleting; digital hoarding was common (emails most hoarded) |
| Chinese college students (2024) | Survey (Frontiers in Psychology) | Digital hoarding linked to cognitive failures; predicts academic burnout |
| Koklic (2025) | Survey (n=625) + experiment (n=177) | Psychological ownership positively predicts digital hoarding; cultural factors (collectivism, uncertainty avoidance) moderate |

**Key finding:** Thorpe et al. (2019) provides the strongest evidence that digital and physical hoarding share psychological mechanisms (r = .55) and that OCD symptomatology predicts both. However, NO study has tested whether IN-GAME hoarding (as opposed to general digital hoarding of files/emails) predicts either digital hoarding or physical hoarding.

**Gap:** The transfer chain game hoarding --> digital hoarding --> physical hoarding is entirely untested. [NEEDS EMPIRICAL VALIDATION -- this is the paper's most important empirical hypothesis for future research]

---

## 6. Theoretical Framework

### 6.1 Mapping to DSM-5 Hoarding Disorder Criteria

DSM-5 Hoarding Disorder (300.3) requires:
1. Persistent difficulty discarding possessions
2. Perceived need to save items; distress at discarding
3. Accumulation of possessions that congest living areas
4. Clinically significant distress or impairment
5. Not attributable to another medical condition
6. Not better explained by another mental disorder

#### Applied to In-Game Context

| Criterion | Physical Hoarding | In-Game Adaptation | Evidence Available? |
|-----------|------------------|-------------------|---------------------|
| 1. Difficulty discarding | Cannot throw away objects | Cannot sell/destroy/consume items; inventory full, still won't discard | Qualitative: Watkins & Molesworth (2012). Quantitative: None for games specifically |
| 2. Perceived need to save | "I might need it someday" | "I might need this potion in a harder fight" / "This item might become rare" | Theoretical: Toh (2021), Engelstein (2020). Empirical: Phillips et al. (2020) for loss aversion |
| 3. Congestion | Cluttered living space | Full inventory, multiple mule characters, paid storage expansions | Anecdotal: Forum/community evidence extensive. Academic: None |
| 4. Distress/impairment | Functional impairment in daily life | Time impairment (hours managing inventory), financial impairment (gacha spending), gameplay impairment (unused resources) | Financial: Tang et al. (2022), Inaguma (2024). Time: [NEEDS EMPIRICAL VALIDATION] |
| 5. Medical exclusion | Brain injury, etc. | N/A in game context | N/A |
| 6. Differential diagnosis | Not better explained by OCD, depression | Distinguish from gambling disorder (gacha), Internet Gaming Disorder, normal collecting | Zendle et al. (2023): OCD/hoarding linked to loot box spending. Lopez-Gonzalez et al. (2024): Loot boxes mediate IGD-gambling link |

#### The Boundary Problem: Collecting vs. Hoarding

Nordsletten & Mataix-Cols (2012) criteria for distinguishing collecting from hoarding, applied to games:

| Feature | Collectors | Hoarders | In-Game Pattern |
|---------|-----------|----------|-----------------|
| Organization | Organized, curated | Chaotic accumulation | Both patterns exist; some players meticulously organize, others pile |
| Emotional valence | Pride, pleasure | Distress, anxiety | Gacha players report both acquisition pleasure AND missing-item distress |
| Trading willingness | Willing to trade/upgrade | Resist discarding at all costs | Varies by domain; completionists resist removing anything from collection |
| Value congruence | Subjective value matches community value | Value incongruent with actual worth | "This level-1 sword has sentimental value" -- classic incongruent valuation |
| Impairment | Life enriched | Life impaired | Time/financial costs cross this line for some players |

### 6.2 Frost-Hartl CBT Model Applied to Games

Frost & Hartl (1996) proposed the most influential CBT model of hoarding, with four components. Here we map each to in-game behavior:

| Frost-Hartl Component | Physical Hoarding | In-Game Hoarding Manifestation |
|----------------------|------------------|-------------------------------|
| **Information processing deficits** | Difficulty categorizing, deciding what to keep | Inventory paralysis; inability to assess which items are truly needed |
| **Emotional attachment** | Objects as extensions of self; safety/comfort | Items with personal history (first rare drop, gift from guildmate); Watkins & Molesworth (2012); IKEA effect inflates value of crafted/upgraded items (Norton et al., 2012) |
| **Behavioral avoidance** | Avoiding the distress of discarding | Avoiding inventory management entirely; creating overflow storage rather than deciding; Ovsiankina-driven compulsion to finish incomplete sets rather than accept incompleteness |
| **Erroneous beliefs about possessions** | "I might need this"; "Wasteful to throw away" | "I might need this elixir in the final boss"; "This item might become rare/valuable" |

**Additional mechanism for games:** Frost et al. (1998) found ~85% of clinical hoarders report excessive acquisition with positive emotional reinforcement. In games, acquisition mechanisms (gacha pulls, loot drops, achievement unlocks, sale purchases) are explicitly designed to maximize positive affect. Game designers have optimized the acquisition-pleasure loop far beyond what occurs naturally with physical possessions.

---

## 7. Regulatory Landscape (2025-2026)

| Jurisdiction | Status | Key Mechanism | Enforcement |
|-------------|--------|---------------|-------------|
| **Belgium** | Loot boxes banned (2018 ruling; 2023 Antwerp Court) | All paid loot boxes classified as illegal gambling | Active; games have removed loot boxes for Belgian market |
| **Netherlands** | Paid loot boxes with real-money advancement unlawful | Kansspelautoriteit enforcement | Active; Dutch minister proposes EU-wide ban via Digital Fairness Act |
| **EU (Digital Fairness Act)** | Proposed; consultation launched July 2025; expected adoption 2026+ | Ban on near-miss animations; real-currency price display for virtual items; consumer opt-out of loot boxes/pay-to-win | Pending; industry pushback active |
| **South Korea** | Probability disclosure law (March 2024); amended GIPA (Jan 2025) | Mandatory probability disclosure; burden of proof on game companies; punitive damages; proposed 3% revenue fines (Sept 2025 bill) | 84% compliance (Zendle 2025 study); strongest enforcement globally |
| **Japan** | Complete gacha (コンプガチャ) banned since 2012; 2025 updated transparency guidelines | Probability disclosure; ban on combination prize mechanics; minor access restrictions | Consumer Affairs Agency enforcement; but no upper payment limits |
| **Australia** | New classification rules (Sept 2024) | Paid loot boxes = mandatory M rating; simulated gambling = mandatory R18+ | Australian Classification Board + ACMA monitoring; not retroactive but applies to updates |
| **Brazil** | Lei Felca (Law 15.211/2025), effective March 17, 2026 | Loot boxes prohibited in games accessible to minors (under 18) | Active enforcement beginning; companies replacing loot boxes with Battle Passes |
| **UK** | No legal regulation; industry self-regulation (Ukie, 2023) | Voluntary probability disclosure; age restrictions | WEAK: <10% ad compliance (social media); ASA enforcement limited to advertising. "UK industry FAILS to self-regulate" (Royal Society, 2025) |
| **US** | No federal regulation | No federal classification or disclosure requirements | Weakest among major markets |

**Academic regulatory research:**
- Zendle (2025): "Better than industry self-regulation" -- comparative study showing South Korea's legally enforced 84% compliance vs. UK's voluntary 64% and Netherlands' 35%
- Xiao et al. (various): Multiple papers on probability disclosure compliance across jurisdictions

**Relevance to this paper:** Regulatory attention validates the clinical significance of loot box/gacha mechanics. The paper's hoarding framework provides additional justification for regulation beyond gambling parallels: loot box mechanics exploit hoarding vulnerabilities (set completion compulsion, acquisition-driven affect, FOMO) that are distinct from gambling mechanisms.

---

## 8. Over-Pathologization: Risks and Safeguards

**This section must be prominent and honest. The paper must not overstate clinical claims.**

### The Over-Pathologization Debate in Gaming

| Source | Position |
|--------|----------|
| Aarseth et al. (2017) | Open letter signed by 36 scholars opposing WHO ICD-11 Gaming Disorder classification; argued low quality evidence base, heavy reliance on substance use criteria, risk of "tsunami of false positive referrals" |
| King et al. (2020) | Face validity review of 29 GD screening tools (417 items): 56 items across 20 tests risk overpathologizing normal gaming behavior; items pathologize mood changes, desire to play, and immersion |
| Oxford Internet Institute | "We shouldn't be pathologizing online gaming before the evidence is in" -- argued for caution before medicalization |
| Bean et al. (2017) | IGD criteria too borrowed from substance use; "applying symptoms reminiscent of substance use disorders to gaming behaviors too often pathologizes normal thoughts, feelings and behavior" |
| Przybylski & Weinstein (2017) | Very low prevalence (0.3-1.0%) of IGD in general population; no clear link between IGD and health outcomes corroborated |
| Frontiers in Psychiatry (2025) | Qualitative study: problematic gaming better conceptualized as coping mechanism or expression of underlying psychosocial distress rather than independent disorder |

### Specific Over-Pathologization Risks for This Paper

1. **Most in-game hoarding is normatively rational.** Saving consumables for harder fights is good strategy when information is incomplete. The paper must not frame all item retention as pathological.
2. **Game designers create the conditions.** Limited inventory, artificial scarcity, FOMO timers, and set-completion designs are deliberate. Blaming players for responding to designed incentives is victim-blaming.
3. **Virtual items have zero physical storage cost.** A key criterion of physical hoarding (cluttered living space) does not translate directly. "Congestion" in games is a design constraint, not a health hazard.
4. **Cultural framing matters.** Collecting and completionism are socially rewarded in gaming communities. "Hoarding" pathologizes behavior that communities celebrate. The Japanese ラストエリクサー症候群 is treated as humorous, not clinical.
5. **A systematic review risks overstating coherence.** By organizing scattered evidence under a "hoarding framework," the paper imposes a clinical lens that may not be warranted by the evidence. The review must explicitly note where evidence is absent or where alternative (non-pathological) explanations are more parsimonious.
6. **The boundary between engagement and pathology is contested.** The paper should adopt a dimensional rather than categorical approach, acknowledging that most hoarding-like behaviors in games are normative and that only extreme manifestations involving genuine distress or impairment warrant clinical attention.

### Paper's Position

This paper does NOT argue that in-game hoarding IS hoarding disorder. It argues that:
(a) In-game hoarding behavior shares documented psychological mechanisms with clinical hoarding.
(b) For a subset of players, these behaviors may cause genuine distress and impairment (financial, temporal, social).
(c) Game design mechanics can exploit hoarding vulnerabilities.
(d) The evidence base is fragmented and requires systematic organization before empirical claims can be tested.
(e) The relationship between in-game hoarding and real-world hoarding is an empirical question for future research, not a foregone conclusion.

---

## 9. Evidence Strength Assessment by Domain

| Domain | Classification | Academic Evidence | Evidence Quality | Key Gaps |
|--------|---------------|-----------------|-----------------|----------|
| **Loss aversion in games** | Cross-cutting mechanism | Moderate (1 experimental study + theoretical work) | Phillips et al. is strong but unreplicated | No replication; no mobile game study; small-stakes concern |
| **Consumable hoarding** | EXPLORATORY | WEAK (theoretical only; no empirical measurement) | Game design literature extensive but not academic | Complete void -- no prevalence, correlates, or profiles. Requires foundational empirical work |
| **Gacha/loot box** | PRIMARY | STRONG (multiple large-N studies, systematic reviews, meta-analyses, longitudinal evidence) | Tang et al. methodology controversial; Zendle work robust | No study applies full hoarding criteria to gacha; FOMO-gacha link understudied |
| **Inventory paralysis** | PRIMARY | Moderate (qualitative evidence strong; quantitative absent) | Watkins & Molesworth qualitative is compelling; IKEA effect (Norton et al., 2012) provides mechanism | No time measurement; no hoarding symptom correlation |
| **Completionism** | PRIMARY | WEAK-MODERATE (motivation taxonomies exist; no completionism-specific measure; Ovsiankina reframe strengthens mechanism) | Yee/Bartle foundational but not hoarding-focused; Ghibellini & Meier (2025) meta-analysis provides updated mechanism | No validated completionism scale; no OCD-completionism empirical link in games |
| **Backlog accumulation** | EXPLORATORY | VERY WEAK (no game-specific academic study) | Related digital hoarding and compulsive buying literature exists | Complete void -- requires foundational empirical work |
| **Cross-domain transfer** | Cross-cutting question | Moderate for digital-physical (r = .55); ABSENT for game-specific | Thorpe et al. (2019) strong for digital-physical | Game hoarding --> real hoarding entirely untested |
| **Over-pathologization** | Safeguard | STRONG (well-developed debate; validated concerns) | King et al. (2020) provides concrete screening criteria | Must be addressed proactively in all future measurement work |

---

## 10. Discussion, Implications, and Future Directions

### Implications

#### For Game Design
- **Ethical design:** Games that exploit hoarding psychology (artificial scarcity, FOMO timers, limited inventory forcing paid expansion, incomplete-set pressure) are exploiting a documented clinical vulnerability. The EU Digital Fairness Act (2026+) is beginning to address this.
- **Design solutions documented in practitioner literature:** Recoverable consumables (Dark Souls estus flask model), abundant item design, removing inventory limits, guaranteed pity systems in gacha, expiring consumable timers
- **Player wellbeing metrics:** In-game hoarding severity (unused items, inventory fullness, discard rate) could serve as behavioral telemetry markers for player wellbeing monitoring

#### For Clinical Practice
- In-game hoarding behavior MAY be an early, low-stakes indicator of hoarding tendencies -- but this is an empirical hypothesis, not an established finding [NEEDS EMPIRICAL VALIDATION]
- Gacha spending should be screened alongside gambling behavior (Lopez-Gonzalez et al., 2024)
- Clinicians treating hoarding disorder should ask about digital and in-game hoarding behavior (Thorpe et al., 2019)

#### For Hoarding Theory
- Virtual possessions as a test case: digital items have no physical storage cost, isolating psychological mechanisms from practical constraints
- Games as natural experiments: designers control scarcity, replaceability, and item properties -- enabling controlled study of hoarding triggers impossible with real-world possessions
- Frost-Hartl model application: All four components (information processing deficits, emotional attachment, behavioral avoidance, erroneous beliefs) map to game contexts, suggesting the model's mechanisms are domain-general

#### For Regulation
- Hoarding framework provides additional justification beyond gambling parallels for loot box/gacha regulation
- Set-completion compulsion, FOMO exploitation, and acquisition-driven affect are exploitable vulnerabilities distinct from gambling

### Future Directions

#### Game Hoarding Inventory (GHI) Development

The evidence synthesis presented here provides the theoretical foundation for developing a Game Hoarding Inventory (GHI), which we propose as a follow-up psychometric study. The five-domain framework (consumable hoarding, gacha/loot box collection, inventory paralysis, completionism, backlog accumulation) and the mechanistic mapping to Frost-Hartl CBT components provide the conceptual basis for item generation. Such a measure would require:
1. Expert panel item generation (game researchers + clinical psychologists + game designers)
2. Exploratory factor analysis (EFA) to determine factor structure
3. Confirmatory factor analysis (CFA) on an independent sample
4. Convergent and discriminant validity testing against existing measures

Relevant existing scales that a GHI should be validated against:

| Scale | Authors | Items | Relevance |
|-------|---------|-------|-----------|
| **SI-R** (Saving Inventory-Revised) | Frost et al., 2004 | 23 | Gold standard physical hoarding measure; convergent validity target |
| **DHQ** (Digital Hoarding Questionnaire) | Neave et al., 2019 | 10 | Closest existing measure; convergent validity target |
| **OCI-R** Hoarding subscale | Foa et al., 2002 | 3 (of 18) | Brief hoarding measure; convergent validity target |
| **IGDS9-SF** | Pontes & Griffiths, 2015 | 9 | Discriminant validity: GHI should NOT be the same as IGD |
| **PGSI** | Ferris & Wynne, 2001 | 9 | Discriminant validity for gacha subscale |
| **OASM** (Object Attachment Security Measure) | 2022 (JBA) | 25 | Tests emotional attachment component |

#### Cross-Domain Transfer Testing

The most important empirical hypothesis arising from this review is whether in-game hoarding predicts real-world digital and physical hoarding. A large-scale cross-sectional survey (n >= 1,000, multi-country) administering a validated GHI alongside the SI-R, DHQ, and relevant moderators would test this hypothesis directly.

#### Behavioral Experiments

Controlled experiments using custom game environments could test the causal effects of scarcity, reversibility, and item investment on hoarding behavior, enabling isolation of mechanisms that observational studies cannot provide.

---

## 11. Limitations (Anticipated)

1. **Over-pathologization risk:** "Hoarding" in games may not produce real-world functional impairment for most players. The review must avoid framing normal game behavior as clinical.
2. **Cross-domain transfer is entirely untested:** The hypothesis that in-game hoarding predicts real-world hoarding is central to the framework's clinical relevance but remains an empirical question for future research.
3. **Two of five domains have near-zero peer-reviewed evidence:** Consumable hoarding and backlog accumulation rest on game design practitioner knowledge and theoretical inference. The systematic review may yield very few or zero results for these domains, and the review must be transparent about this.
4. **Cultural differences in gaming ecosystems:** Gacha-heavy Asian markets (Japan, South Korea, China) vs. loot-box-regulated Western markets (EU, Australia) may limit generalizability of findings across the review.
5. **Differential diagnosis complexity:** Distinguishing game hoarding from Internet Gaming Disorder and gambling disorder is conceptually complex. Lopez-Gonzalez et al. (2024) show loot boxes mediate IGD-gambling -- the constructs may be more intertwined than distinct.
6. **Game designer intent:** The paper frames some game mechanics as "exploiting hoarding vulnerabilities." Designers may argue these mechanics serve legitimate engagement and business purposes. The paper should avoid moralistic framing.
7. **Methodological concerns in existing literature:** Tang et al. (2022) modified PGSI controversy raises questions about measurement validity across the gacha-gambling literature. The review should acknowledge this when synthesizing findings.
8. **Narrative synthesis limitations:** Given the heterogeneity of study designs, populations, and constructs across the five domains, quantitative meta-analysis will likely be feasible only for the gacha/loot box domain. The narrative synthesis approach for remaining domains is inherently more subjective and less replicable.
9. **Publication bias:** The systematic review is susceptible to publication bias, particularly for the emerging domains where the literature is thin. Null findings on hoarding-like behaviors in games may go unpublished.

---

## 12. References

### Hoarding Theory and Clinical
- Frost, R. O., & Hartl, T. L. (1996). A cognitive-behavioral model of compulsive hoarding. Behaviour Research and Therapy, 34(4), 341-350.
- Frost, R. O., Steketee, G., & Williams, L. (1998). Hoarding: A community health problem. Health & Social Care in the Community, 6, 229-234.
- Frost, R. O., Steketee, G., & Grisham, J. (2004). Measurement of compulsive hoarding: Saving Inventory-Revised. Behaviour Research and Therapy, 42(10), 1163-1182.
- Nordsletten, A. E., & Mataix-Cols, D. (2012). Hoarding versus collecting: Where does pathology diverge from play? Clinical Psychology Review, 32(3), 165-176.
- Foa, E. B., Huppert, J. D., Leiberg, S., Langner, R., Kichic, R., Hajcak, G., & Salkovskis, P. M. (2002). The Obsessive-Compulsive Inventory: Development and validation of a short version. Psychological Assessment, 14(4), 485-496.
- Object Attachment Security Measure (2022). Development and validation. Journal of Behavioral Addictions.

### Digital Hoarding
- Neave, N., Briggs, P., McKellar, K., & Sherlock, L. (2019). Digital hoarding behaviours: Measurement and evaluation. Computers in Human Behavior, 96, 72-77.
- Thorpe, S., Bolster, A., & Neave, N. (2019). Exploring aspects of the cognitive-behavioural model of physical hoarding in relation to digital hoarding behaviours. Digital Health, 5.
- Luxon, A. M., Hamilton, K. A., Bates, K. E., & Chasson, G. S. (2019). Pinning our possessions: Associations between digital hoarding and symptoms of hoarding disorder. Journal of Obsessive-Compulsive and Related Disorders, 21, 60-68.
- Vinoi, R., et al. (2024). Enablers and inhibitors of digital hoarding. Journal of Retailing & Consumer Services.
- Koklic, M. K. (2025). Psychological ownership predicts digital hoarding and piracy. Journal of Consumer Behaviour.
- Chinese college students study (2024). Digital hoarding linked to cognitive failures. Frontiers in Psychology.

### Loss Aversion in Games
- Phillips, C., Klarkowski, M., & Vistisen, P. (2020). Risking treasure: Testing loss aversion in an adventure game. CHI PLAY 2020, ACM.
- Engelstein, G. (2020). Achievement Relocked: Loss Aversion and Game Design. MIT Press.
- Toh, W. (2021). The economics of decision-making in video games. Game Studies.
- Schwartz, B. (2004). The Paradox of Choice. Harper Perennial.

### Virtual Ownership and Attachment
- Watkins, R., & Molesworth, M. (2012). Attachment to digital virtual possessions in videogames. Research in Consumer Behavior, Emerald.
- Belk, R. W. (2013). Extended self in a digital world. Journal of Consumer Research, 40(3), 477-500.
- Krauss, A., & Wienrich, C. (2025). Systematic review of psychological ownership of virtual objects, 21 papers. CHI 2025, ACM.
- Honarvar, H., & Sepehrinia, F. (2025). Refashioning Belk's digital extended self for datafied society. SAGE Open.
- Koles, B. (2025). Cosmetic items in video games: A persona approach. Journal of Consumer Behaviour.
- Norton, M. I., Mochon, D., & Ariely, D. (2012). The IKEA effect: When labor leads to love. Journal of Consumer Psychology, 22(3), 453-460.

### Loot Boxes and Gacha
- Zendle, D., Meyer, R., & Ballou, N. (2023). Loot box spending, problem gambling, and OCD/hoarding. Journal of Behavioral Addictions.
- Spicer, S. G., et al. (2022). Systematic review and meta-synthesis of loot box research. New Media & Society.
- Tang, W. Y., et al. (2022). Problem gambling in Chinese gacha gamers. Frontiers in Psychiatry.
- Tang, W. Y., et al. (2025). Gacha gaming and life quality shape problem gambling risk. Frontiers in Psychiatry.
- Shibuya, A., et al. (2019). Long-term effects of limited-time gacha on Japanese youth spending. Simulation & Gaming.
- Biegun, K. (2023). Addiction and spending in gacha games. MDPI Information.
- Inaguma, Y., et al. (2024). Case report: Gaming disorder with high loot box charges. Psychiatry and Clinical Neurosciences Reports.
- Lopez-Gonzalez, H., et al. (2024). Problematic loot box use mediates IGD-gambling link. JMIR Serious Games.
- Drummond, A., et al. (2025). Loot box spending and distress normalized to income. Royal Society Open Science.
- Zendle, D. (2025). South Korea compliance study: Legal enforcement vs. self-regulation. PMC.
- Zendle, D., et al. (2023b/2025). Longitudinal replication: Loot box purchases predict gambling initiation. BMC Psychology.

### Player Motivation
- Bartle, R. (1996). Hearts, clubs, diamonds, spades: Players who suit MUDs. Journal of MUD Research.
- Yee, N. (2006). Motivations for play in online games. CyberPsychology & Behavior, 9(6), 772-775.
- Demetrovics, Z., et al. (2011). MOGQ: Motives for online gaming questionnaire. Behavior Research Methods, 43(3), 814-825.
- Gursesli, M. C., et al. (2024). PMPVGs: New gaming motivation scale. Simulation & Gaming.
- MOPS (2024). Motivation to Play Scale. Current Psychology.
- GMI (2023). Gaming Motivation Inventory. PMC.

### Virtual Economies
- Lehdonvirta, V. (2009). Virtual consumption. Electronic Commerce Research.
- Lehdonvirta, V., & Castronova, E. (2014). Virtual Economies. MIT Press.
- Hamari, J., & Keronen, L. (2017). Why do people buy virtual goods: A meta-analysis. Computers in Human Behavior, 71, 59-69.

### Dark Patterns and Ethical Game Design
- Zagal, J. P., Bjork, S., & Lewis, C. (2013). Dark patterns in the design of games.
- Ballou, N., et al. (2022). A game of dark patterns. CHI 2022, ACM.
- CHI 2023 Workshop: Behavioural design in video games.
- Springer (2025): From understanding to intervention -- countering dark patterns in games.
- ACM ECCE 2024: Beyond predatory practices.
- ACM Games: Research and Practice (2024): Behavioral design in video games.
- ACM Games: Research and Practice (2024): Ethical games.
- ACM Games: Research and Practice (2024): Ask the players!

### Over-Pathologization
- Aarseth, E., et al. (2017). Scholars' open debate on WHO ICD-11 Gaming Disorder. Journal of Behavioral Addictions, 6(3), 267-270.
- King, D. L., et al. (2020). Face validity of gaming disorder screening tools. Journal of Behavioral Addictions, 9(1), 1-13.
- Przybylski, A. K., & Weinstein, N. (2017). IGD prevalence study. American Journal of Psychiatry.
- Bean, A. M., et al. (2017). Video game addiction: The push to pathologize video games. Professional Psychology: Research and Practice, 48(5), 378-389.
- Pontes, H. M., & Griffiths, M. D. (2015). IGDS9-SF. Psychology of Addictive Behaviors.

### Completionism Mechanism (Zeigarnik/Ovsiankina)
- Ghibellini, R., & Meier, B. (2025). Interruption, recall and resumption: A meta-analysis of the Zeigarnik and Ovsiankina effects. Humanities and Social Sciences Communications, 12, 962.
- Kruse, Y. (2016). Players' perceptions of completionism. Computers in Human Behavior.

### Impulse Buying
- Impulse buying in games (2024). Survey, n=389.
- Salakari (2024). Consumer psychology thesis.

---

## Notes on Terminology

- **"Game hoarding"** is used throughout as a working term. The paper explicitly does NOT claim that in-game item retention constitutes clinical hoarding disorder. It claims that shared psychological mechanisms exist and that the evidence base requires systematic organization.
- **"Elixir problem"** is retained as the paper's organizing metaphor because it is recognized across gaming cultures (English, Japanese, Korean), captures the core mechanism (loss aversion + decision avoidance), and has clear popular-culture resonance.
- **"Domain"** rather than "subtype" is used for the five categories to avoid implying clinical categorization.
- **"Primary" vs. "Exploratory"** domain classification reflects the quantity and quality of peer-reviewed evidence available, not the theoretical importance of the domain.
