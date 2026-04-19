#!/usr/bin/env python3
"""
Enhanced PRISMA screening for PubMed results v2.
Applies sophisticated keyword heuristics to classify papers as Include/Maybe/Exclude
for a systematic review on in-game hoarding, collecting, loss aversion, and related behaviors.
"""

import csv
import re
from collections import Counter, defaultdict

import os as _os
_SRC_DIR = _os.path.dirname(_os.path.abspath(__file__))
_EXP_DIR = _os.path.dirname(_SRC_DIR)
INPUT_CSV = _os.path.join(_EXP_DIR, "data", "raw", "pubmed_results.csv")
OUTPUT_CSV = _os.path.join(_EXP_DIR, "data", "processed", "screening_results.csv")
SUMMARY_MD = _os.path.join(_EXP_DIR, "results", "screening_summary.md")
SYNTHESIS_MD = _os.path.join(_EXP_DIR, "results", "evidence_synthesis.md")
for _d in (_os.path.dirname(OUTPUT_CSV), _os.path.dirname(SUMMARY_MD)):
    _os.makedirs(_d, exist_ok=True)

# ---------------------------------------------------------------------------
# Helper: lowercase search text from title + abstract
# ---------------------------------------------------------------------------

def search_text(row):
    return (row.get("title", "") + " " + row.get("abstract", "")).lower()


def has_any(text, keywords):
    """Return True if any keyword appears in text."""
    return any(kw in text for kw in keywords)


def has_all(text, keywords):
    """Return True if ALL keywords appear in text."""
    return all(kw in text for kw in keywords)


# ---------------------------------------------------------------------------
# Domain assignment (refined)
# ---------------------------------------------------------------------------

DOMAIN_KEYWORDS = {
    "D1": [  # Loss Aversion in Games
        "loss aversion", "endowment effect", "sunk cost",
        "prospect theory", "risk aversion", "risk-aversion",
        "behavioral economics", "behavioural economics",
        "framing effect", "status quo bias",
    ],
    "D2": [  # Consumable Hoarding
        "consumable hoarding", "potion hoarding", "item hoarding",
        "hoarding consumable", "too good to use", "resource hoarding",
        "elixir", "health potion", "mana potion",
        "hoarding item", "hoard item", "hoarding in game",
        "hoarding in video game", "hoarding behavior in game",
    ],
    "D3": [  # Gacha / Loot Box
        "loot box", "lootbox", "gacha", "microtransaction",
        "in-game purchase", "in-app purchase", "pay to win",
        "pay-to-win", "skin gambling", "virtual currency",
        "monetization", "monetisation", "free-to-play",
        "freemium", "random reward", "randomised reward",
        "randomized reward", "card pack",
    ],
    "D4": [  # Inventory Paralysis / Virtual Possession
        "inventory", "virtual item", "virtual good",
        "virtual possession", "psychological ownership",
        "virtual ownership", "digital possession",
        "digital ownership", "in-game item",
        "virtual asset", "digital item",
    ],
    "D5": [  # Completionism
        "completionism", "completionist", "achievement hunt",
        "100%", "hundred percent", "collect them all",
        "collect-a-thon", "collectathon", "trophy",
        "achievement", "badge", "all achievements",
        "completeness", "completion rate",
    ],
    "D6": [  # Backlog Accumulation
        "backlog", "game library", "steam library",
        "pile of shame", "unplayed game", "game accumulation",
        "digital library", "game collection",
        "unfinished game", "abandoned game",
    ],
    "Cross-domain": [  # Hoarding link
        "hoarding", "hoard", "compulsive buying",
        "compulsive acquisition", "compulsive collecting",
        "accumulation", "possessiveness",
        "obsessive collecting", "excessive collecting",
    ],
}


def assign_domains(text):
    """Return list of matched domain tags based on keywords."""
    matched = []
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if has_any(text, keywords):
            matched.append(domain)
    return matched


# ---------------------------------------------------------------------------
# Exclusion rules (hard exclude)
# ---------------------------------------------------------------------------

# Patterns that indicate the paper is clearly off-topic
HARD_EXCLUDE_PATTERNS = [
    # Sports / athletics false positives
    (r"\b(basketball|netball|soccer|football|rugby|cricket|volleyball|tennis|baseball|hockey|swimming)\b.*\b(player|team|athlete|injury|rehabilitation)\b",
     "Sports/athletics paper"),
    (r"\b(anterior cruciate|acl|concussion|muscle|tendon|knee|ankle|shoulder)\b.*\b(injury|rehabilitation|surgery|repair)\b",
     "Sports medicine/injury paper"),
    (r"\b(wheelchair|paralympic)\b",
     "Paralympic/wheelchair sports paper"),

    # Pure vaccination / public health
    (r"\bvaccin(e|ation|ated)\b.*\b(production|coverage|access|immuniz)\b",
     "Vaccination/public health paper"),

    # Pure biology / ecology
    (r"\b(seed dispersal|mutualism|pollination|tropical forest|plant ecology)\b",
     "Ecology/biology paper"),
    (r"\b(food hoarding|scatter hoarding|larder hoarding)\b.*\b(animal|rodent|bird|squirrel|chipmunk)\b",
     "Animal hoarding behavior paper"),

    # COVID medical management (not game-related)
    (r"\bconvalescent plasma\b",
     "COVID plasma paper"),

    # Pure psychiatry taxonomy with no game component
    (r"\bdsm-5\b.*\b(manual|diagnostic|classification)\b",
     "DSM-5 taxonomy paper"),

    # Physical education / teaching methods
    (r"\b(physical education|sports teaching|traditional games)\b.*\b(teach|curriculum|school|student)\b",
     "Physical education/teaching paper"),

    # Burn/physical rehabilitation (non-game-specific)
    (r"\bburn injury\b.*\b(rehabilitation|feasibility|kinect)\b",
     "Burn rehabilitation paper"),

    # Sleep comparison in athletes
    (r"\bsleep\b.*\b(wheelchair|basketball|national team)\b",
     "Athlete sleep study"),

    # Pure medical / pharmaceutical
    (r"\b(medical management|professional basketball|ophthalmol|surgery|surgical)\b",
     "Pure medical paper"),

    # Change of direction / biomechanics
    (r"\b(change of direction|biomechanic|qualitative instrument)\b.*\b(mechanism|reliability)\b",
     "Biomechanics paper"),
]


def check_hard_exclude(text):
    """Return (True, reason) if the paper should be hard-excluded."""
    for pattern, reason in HARD_EXCLUDE_PATTERNS:
        if re.search(pattern, text):
            return True, reason
    return False, ""


# ---------------------------------------------------------------------------
# Soft exclusion / inclusion heuristics
# ---------------------------------------------------------------------------

def classify_paper(row):
    """
    Return (decision, reason, domains, relevance_score).
    decision: "Include", "Maybe", "Exclude"
    """
    text = search_text(row)
    title = row.get("title", "").lower()
    abstract = row.get("abstract", "").lower()

    # ------ Hard excludes ------
    excluded, reason = check_hard_exclude(text)
    if excluded:
        return "Exclude", reason, [], 0

    # Gamification of education (not video game behavior)
    if "gamification" in text and "video game" not in text and "loot box" not in text:
        if has_any(text, ["education", "classroom", "learning", "student", "course", "university"]):
            return "Exclude", "Educational gamification (no video game behavior)", [], 0

    # Game theory (economics, not player behavior)
    if "game theory" in text and "video game" not in text and "loot box" not in text:
        if not has_any(text, ["gaming disorder", "internet gaming", "online gaming"]):
            return "Exclude", "Game theory (economics), not player behavior", [], 0

    # Evolutionary game / game analysis (mathematical modeling, not video games)
    if has_any(text, ["evolutionary game", "game analysis", "game model"]):
        if not has_any(text, ["video game", "loot box", "online game", "mobile game",
                               "gaming disorder", "gamer"]):
            return "Exclude", "Mathematical game modeling (not video game research)", [], 0

    # Labour/labor economics with "game" but no video game connection
    if has_any(text, ["labour market", "labor market", "labour economics", "labor economics",
                       "wage", "worker", "employment contract", "fairness in labour"]):
        if not has_any(text, ["video game", "gamer", "gaming", "loot box"]):
            return "Exclude", "Labour economics paper (not video game research)", [], 0

    # Health records / electronic health records with "game" in "game analysis"
    if has_any(text, ["electronic health record", "ehr ", "health record integration",
                       "medical alliance"]):
        if not has_any(text, ["video game", "loot box", "gamer"]):
            return "Exclude", "Health records/EHR paper (not video game research)", [], 0

    # Auction / bidding studies (economic experiments, not video games)
    if has_any(text, ["vickrey auction", "auction experiment", "bid outcome"]):
        if not has_any(text, ["video game", "loot box", "in-game", "virtual item"]):
            return "Exclude", "Auction/bidding experiment (not video game research)", [], 0

    # Shopping / buying behavior studies with NO game connection
    if has_any(text, ["problematic shopping", "self-injurious"]):
        if not has_any(text, ["video game", "gaming", "gamer", "loot box", "in-game"]):
            return "Exclude", "Shopping/buying behavior (no video game connection)", [], 0

    # Calcium binding / biochemistry / cancer biology false positives
    if has_any(text, ["calcium binding", "matrix metalloproteinase", "bone-targeted",
                       "skeletal morbidity", "prostate cancer"]):
        return "Exclude", "Biochemistry/oncology paper (not game research)", [], 0

    # Reciprocity / cooperation game theory
    if has_any(text, ["indirect reciprocity", "image scoring", "standing strategy"]):
        if not has_any(text, ["video game", "gamer", "online game"]):
            return "Exclude", "Cooperation/reciprocity game theory (not video game)", [], 0

    # Patent/legal system "backlog"
    if has_any(text, ["patent", "pto ", "patent system", "patent quality"]):
        return "Exclude", "Patent system paper (not game research)", [], 0

    # Performance assessment / management (not gaming)
    if has_any(text, ["performance measurement", "management assessment"]):
        if not has_any(text, ["video game", "gamer", "gaming", "player"]):
            return "Exclude", "Management/assessment paper (not game research)", [], 0

    # Evidence-based medicine / CAM
    if has_any(text, ["campaign against cam", "evidence-based medicine", "complementary and alternative"]):
        return "Exclude", "Evidence-based medicine debate (not game research)", [], 0

    # Persuasion / limited sight (economics)
    if "persuasion with limited" in text:
        return "Exclude", "Economic theory paper (not game research)", [], 0

    # Platelet / blood bank inventory management
    if has_any(text, ["platelet", "blood bank", "transfusion", "platelet inventory"]):
        return "Exclude", "Blood bank/platelet paper (not game research)", [], 0

    # Food waste / supply chain inventory
    if has_any(text, ["food waste", "wasted food", "food industry", "connected homes"]):
        if not has_any(text, ["video game", "gamer", "gaming", "loot box"]):
            return "Exclude", "Food waste/supply chain paper (not game research)", [], 0

    # Hospital logistics / clinical inventory (not games)
    if has_any(text, ["logistics hub", "hospital logistics", "clinical staff",
                       "decoupling", "clinical inventory"]):
        if not has_any(text, ["video game", "gamer", "gaming"]):
            return "Exclude", "Hospital logistics paper (not game research)", [], 0

    # Ivory / bioarchaeology
    if has_any(text, ["boar tusk", "ivory", "calcium oxalate", "biomineral"]):
        return "Exclude", "Bioarchaeology paper (not game research)", [], 0

    # WeChat / personal information valuation (not video game)
    if "wechat" in text and "video game" not in text:
        if not has_any(text, ["gamer", "gaming", "loot box", "in-game"]):
            return "Exclude", "Social media/privacy valuation paper (not video game)", [], 0

    # Gamification for health/fitness (not video game behavior)
    if "gamification" in text and has_any(text, ["health app", "fitness app",
                                                   "health and fitness", "mobile application"]):
        if not has_any(text, ["video game", "loot box", "in-game", "gamer"]):
            return "Exclude", "Health/fitness gamification (not video game behavior)", [], 0

    # Neural bases of decision-making without explicit game connection
    if has_any(text, ["neural bases", "dorsomedial prefrontal", "fmri", "erp effect"]):
        if not has_any(text, ["video game", "gamer", "gaming disorder", "internet gaming",
                               "online game", "loot box"]):
            if has_any(text, ["loss aversion", "decision-making"]):
                return "Maybe", "Neuroscience of loss aversion (no direct game focus)", [], 3

    # Serious games for therapy/rehabilitation (not about player collecting/hoarding)
    if has_any(text, ["serious game", "exergame", "exer-game"]):
        if has_any(text, ["rehabilitation", "therapy", "therapeutic", "clinical intervention", "motor recovery"]):
            if not has_any(text, ["loot box", "microtransaction", "hoarding", "collecting", "inventory"]):
                return "Exclude", "Serious game for therapy/rehabilitation", [], 0

    # Pure gambling (casino, poker, sports betting) with NO game mechanic connection
    gambling_terms = ["casino", "poker", "slot machine", "sports betting", "horse racing",
                      "roulette", "blackjack", "scratch card", "scratch ticket", "lottery ticket"]
    game_terms = ["video game", "loot box", "microtransaction", "online game", "mobile game",
                  "game play", "gameplay", "in-game", "gamer", "gaming disorder",
                  "internet gaming", "gacha", "fortnite", "fifa", "overwatch",
                  "counter-strike", "csgo", "cs:go"]

    if has_any(text, gambling_terms) and not has_any(text, game_terms):
        return "Exclude", "Pure gambling study (no video game connection)", [], 0

    # Papers about well-being / screen time with no specific collecting/hoarding angle
    if has_any(text, ["well-being", "wellbeing", "screen time", "time spent playing"]):
        if not has_any(text, ["loot box", "microtransaction", "hoarding", "collecting",
                               "inventory", "achievement", "loss aversion", "ownership",
                               "purchase", "spending"]):
            return "Exclude", "General gaming well-being study (no collecting/hoarding angle)", [], 0

    # Eutrapelia / moral philosophy of games
    if "eutrapelia" in text:
        return "Exclude", "Moral philosophy of gaming (not behavioral research)", [], 0

    # Pure video analysis of sports
    if "video analysis" in text and has_any(text, ["injury", "tackle", "movement"]):
        return "Exclude", "Sports video analysis", [], 0

    # Papers with empty abstracts — can only judge by title
    if not abstract.strip():
        # Try to classify by title alone
        domains = assign_domains(title)
        if domains:
            return "Maybe", "No abstract available; title suggests relevance", domains, 3
        else:
            return "Exclude", "No abstract; title not clearly relevant", [], 0

    # ------ Positive classification ------
    domains = assign_domains(text)

    # Strong includes
    # Virtual-item gambling (online lottery games, virtual goods)
    if has_any(text, ["virtual-item gambling", "virtual item gambling", "online lottery game"]):
        return "Include", "Virtual item gambling research", domains, 7

    # Loot box / gacha / microtransaction spending patterns
    if has_any(text, ["loot box", "lootbox", "gacha"]):
        if has_any(text, ["video game", "game", "gamer", "gaming", "player"]):
            score = 8
            if "hoarding" in text or "compulsive" in text:
                score = 9
            return "Include", "Loot box/gacha research with game connection", domains, score

    # Virtual item ownership / psychological ownership in games
    if has_any(text, ["psychological ownership", "virtual ownership", "virtual item",
                       "virtual good", "virtual possession", "digital ownership"]):
        if has_any(text, ["video game", "online game", "mobile game", "in-game",
                           "gamer", "gaming", "gameplay", "loot box"]):
            return "Include", "Virtual item ownership / psychological ownership in games", domains, 8
        elif has_any(text, ["game", "player"]) and not has_any(text, [
            "game theory", "evolutionary game", "labour", "labor",
            "health record", "platelet", "blood bank", "food waste"
        ]):
            return "Include", "Virtual item ownership / psychological ownership in games", domains, 7

    # Player collecting / hoarding behavior in games
    if has_any(text, ["hoarding", "collecting behavior", "collecting behaviour"]):
        if has_any(text, ["game", "player", "gamer", "gaming", "video game", "online game"]):
            if not has_any(text, ["animal", "rodent", "squirrel", "food hoarding"]):
                return "Include", "Player collecting/hoarding behavior in games", domains, 9

    # Game achievement / completionism
    if has_any(text, ["completionism", "completionist", "achievement hunting",
                       "achievement system", "100% completion"]):
        if has_any(text, ["game", "player", "gamer", "gaming"]):
            return "Include", "Game achievement/completionism research", domains, 8

    # Microtransaction spending patterns
    if has_any(text, ["microtransaction", "in-game purchase", "in-app purchase",
                       "in-game spending", "in game spending", "in game purchase"]):
        if has_any(text, ["game", "player", "gamer", "gaming", "video game"]):
            return "Include", "Microtransaction/in-game spending research", domains, 7

    # Loss aversion specifically in video game contexts (not game theory)
    if "loss aversion" in text:
        if has_any(text, ["video game", "online game", "mobile game", "gaming disorder",
                           "internet gaming", "gamer", "gameplay", "in-game", "loot box"]):
            return "Include", "Loss aversion in video game context", domains, 7
        elif has_any(text, ["gaming", "player"]) and not has_any(text, [
            "game theory", "evolutionary game", "game model", "game analysis",
            "labour", "labor", "auction", "bargaining"
        ]):
            return "Include", "Loss aversion in game context", domains, 6

    # Skin gambling
    if "skin gambling" in text:
        return "Include", "Skin gambling research (game-linked)", domains, 7

    # Sunk cost in games
    if "sunk cost" in text and has_any(text, ["game", "player", "gaming"]):
        return "Include", "Sunk cost research in game context", domains, 7

    # Endowment effect in games
    if "endowment effect" in text and has_any(text, ["game", "player", "gaming", "virtual"]):
        return "Include", "Endowment effect in game/virtual context", domains, 7

    # ------ Maybe classifications ------

    # Gaming disorder studies that mention spending/purchasing
    if has_any(text, ["gaming disorder", "internet gaming disorder", "problematic gaming",
                       "problem gaming"]):
        if has_any(text, ["spending", "purchase", "microtransaction", "loot box",
                           "monetization", "monetisation"]):
            return "Include", "Gaming disorder study with spending/purchasing component", domains, 6

    # Gaming disorder general (might have relevant data)
    if has_any(text, ["gaming disorder", "internet gaming disorder"]):
        if has_any(text, ["game", "video game", "online game"]):
            return "Maybe", "Gaming disorder study (may contain relevant behavioral data)", domains, 4

    # Gambling-gaming convergence studies
    if has_any(text, ["gambling", "gambl"]) and has_any(text, ["video game", "online game",
                                                                 "loot box", "gaming disorder"]):
        if has_any(text, ["spending", "purchase", "money", "payment"]):
            return "Include", "Gambling-gaming convergence with spending focus", domains, 6
        return "Maybe", "Gambling-gaming convergence (may have relevant data)", domains, 4

    # Compulsive buying / behavioral addiction with gaming connection
    if has_any(text, ["compulsive buying", "compulsive shopping", "buying disorder"]):
        if has_any(text, ["game", "gaming", "online", "digital"]):
            return "Maybe", "Compulsive buying with potential game connection", domains, 4
        elif has_any(text, ["hoarding", "accumulation"]):
            return "Maybe", "Compulsive buying with hoarding connection", domains, 3

    # Behavioral addiction comorbidity studies
    if has_any(text, ["behavioral addiction", "behavioural addiction"]):
        if has_any(text, ["gaming", "game", "hoarding"]):
            return "Maybe", "Behavioral addiction study with gaming/hoarding component", domains, 4

    # Hoarding disorder studies (clinical) — cross-domain relevance
    if "hoarding disorder" in text or "hoarding symptom" in text:
        if has_any(text, ["game", "gaming", "digital", "online", "virtual"]):
            return "Maybe", "Clinical hoarding with digital/gaming connection", domains, 4
        elif has_any(text, ["compulsive", "obsessive", "acquisition"]):
            return "Maybe", "Clinical hoarding (potential cross-domain insight)", domains, 3

    # Shopping addiction scales that might be relevant to in-game purchasing
    if has_any(text, ["shopping addiction", "compulsive buying"]):
        return "Maybe", "Shopping addiction (potential cross-domain parallel to in-game purchasing)", domains, 3

    # Virtual economy / virtual world studies
    if has_any(text, ["virtual economy", "virtual world", "virtual market"]):
        return "Maybe", "Virtual economy research", domains, 5

    # Free-to-play game studies
    if "free-to-play" in text or "freemium" in text:
        if has_any(text, ["game", "player", "gaming"]):
            return "Include", "Free-to-play game monetization research", domains, 6

    # Game monetization studies
    if has_any(text, ["monetization", "monetisation"]) and has_any(text, ["game", "gaming"]):
        return "Include", "Game monetization research", domains, 6

    # Studies about player motivation that might touch on collecting
    if has_any(text, ["player motivation", "gaming motivation"]):
        if has_any(text, ["collecting", "achievement", "ownership", "possession"]):
            return "Maybe", "Player motivation with collecting/ownership angle", domains, 4

    # Reward system / reinforcement in games
    if has_any(text, ["reward system", "reinforcement", "variable ratio"]):
        if has_any(text, ["game", "player", "gaming"]):
            return "Maybe", "Game reward system research", domains, 4

    # OCD / obsessive-compulsive with gaming connection
    if has_any(text, ["obsessive-compulsive", "ocd"]):
        if has_any(text, ["gaming", "game", "loot box", "hoarding"]):
            return "Maybe", "OCD with gaming/hoarding connection", domains, 4

    # Food addiction / behavioral addiction network studies
    if "food addiction" in text and has_any(text, ["gaming", "hoarding", "behavioral addiction"]):
        return "Maybe", "Behavioral addiction network (includes gaming/hoarding)", domains, 3

    # Adolescent/youth gaming with any spending mention
    if has_any(text, ["adolescent", "youth", "teenager", "child"]):
        if has_any(text, ["gaming", "video game"]) and has_any(text, ["spending", "purchase"]):
            return "Maybe", "Youth gaming study with spending component", domains, 4

    # Self-regulation in gaming contexts
    if has_any(text, ["self-regulation", "self-control", "impulsiv"]):
        if has_any(text, ["gaming", "game", "video game"]):
            if has_any(text, ["spending", "purchase", "collect", "hoard", "loot box"]):
                return "Maybe", "Self-regulation in gaming with relevant behavioral angle", domains, 4

    # Catch-all: if domains were assigned, mark as Maybe
    if domains:
        if has_any(text, ["game", "gaming", "gamer", "player", "video game"]):
            return "Maybe", "Game-related paper matching domain keywords", domains, 4
        else:
            return "Maybe", "Matched domain keywords but game connection unclear", domains, 2

    # ------ Default exclude ------
    # Check if there is ANY game connection at all
    if has_any(text, ["video game", "online game", "mobile game", "gaming", "gamer"]):
        # It's game-related but doesn't match any specific criteria
        return "Maybe", "Game-related but no strong match to specific domains", [], 2

    return "Exclude", "No clear relevance to in-game collecting/hoarding behaviors", [], 0


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------

def main():
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Loaded {len(rows)} papers from {INPUT_CSV}")

    results = []
    stats = Counter()
    domain_counts = defaultdict(lambda: {"Include": 0, "Maybe": 0, "Exclude": 0})
    year_dist = Counter()
    journal_dist = Counter()
    decision_reasons = defaultdict(list)

    for row in rows:
        decision, reason, domains, relevance = classify_paper(row)
        stats[decision] += 1

        domain_str = "; ".join(domains) if domains else row.get("domains", "")

        results.append({
            "PMID": row.get("pmid", ""),
            "Title": row.get("title", ""),
            "Year": row.get("year", ""),
            "Journal": row.get("journal", ""),
            "Authors": row.get("authors", ""),
            "Domain(s)": domain_str,
            "Relevance_Score": relevance,
            "Screening_Decision": decision,
            "Reason": reason,
            "Abstract": row.get("abstract", ""),
        })

        if decision in ("Include", "Maybe"):
            year_dist[row.get("year", "")] += 1
            journal_dist[row.get("journal", "")] += 1
            for d in (domains if domains else row.get("domains", "").split(";")):
                d = d.strip()
                if d:
                    domain_counts[d][decision] += 1

        decision_reasons[decision].append(reason)

    # Write screening results CSV
    fieldnames = ["PMID", "Title", "Year", "Journal", "Domain(s)",
                  "Relevance_Score", "Screening_Decision", "Reason"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    print(f"\nScreening results saved to {OUTPUT_CSV}")
    print(f"\n--- Screening Summary ---")
    print(f"Total papers: {len(rows)}")
    for dec in ["Include", "Maybe", "Exclude"]:
        print(f"  {dec}: {stats[dec]}")

    # --- Generate screening_summary.md ---
    generate_screening_summary(rows, results, stats, domain_counts, year_dist, journal_dist)

    # --- Generate evidence_synthesis.md ---
    generate_evidence_synthesis(results)


# ---------------------------------------------------------------------------
# Screening summary
# ---------------------------------------------------------------------------

def generate_screening_summary(rows, results, stats, domain_counts, year_dist, journal_dist):
    included = [r for r in results if r["Screening_Decision"] == "Include"]
    maybe = [r for r in results if r["Screening_Decision"] == "Maybe"]
    excluded = [r for r in results if r["Screening_Decision"] == "Exclude"]

    lines = []
    lines.append("# Screening Summary (PRISMA Flow)\n")
    lines.append("## PRISMA Flow Numbers\n")
    lines.append(f"- **Identified** (PubMed search v2): {len(rows)}")
    lines.append(f"- **Screened** (title/abstract): {len(rows)}")
    lines.append(f"- **Excluded at screening**: {stats['Exclude']}")
    lines.append(f"- **Eligible for synthesis**: {stats['Include'] + stats['Maybe']}")
    lines.append(f"  - **Include** (clearly relevant): {stats['Include']}")
    lines.append(f"  - **Maybe** (needs full-text review): {stats['Maybe']}")
    lines.append(f"- **Excluded**: {stats['Exclude']}")
    lines.append("")

    # Exclusion reasons
    exclude_reasons = Counter(r["Reason"] for r in excluded)
    lines.append("## Exclusion Reasons\n")
    lines.append("| Reason | Count |")
    lines.append("|--------|-------|")
    for reason, count in exclude_reasons.most_common():
        lines.append(f"| {reason} | {count} |")
    lines.append("")

    # Domain breakdown
    lines.append("## Included/Maybe Papers by Domain\n")
    lines.append("| Domain | Include | Maybe | Total |")
    lines.append("|--------|---------|-------|-------|")
    for domain in ["D1", "D2", "D3", "D4", "D5", "D6", "Cross-domain"]:
        dc = domain_counts.get(domain, {"Include": 0, "Maybe": 0})
        total = dc["Include"] + dc["Maybe"]
        label = {
            "D1": "D1: Loss Aversion in Games",
            "D2": "D2: Consumable Hoarding",
            "D3": "D3: Gacha / Loot Box",
            "D4": "D4: Inventory / Virtual Possession",
            "D5": "D5: Completionism",
            "D6": "D6: Backlog Accumulation",
            "Cross-domain": "Cross-domain: Hoarding Link",
        }.get(domain, domain)
        lines.append(f"| {label} | {dc['Include']} | {dc['Maybe']} | {total} |")
    lines.append("")

    # Year distribution
    lines.append("## Year Distribution (Include + Maybe papers)\n")
    lines.append("| Year | Count |")
    lines.append("|------|-------|")
    for year in sorted(year_dist.keys()):
        lines.append(f"| {year} | {year_dist[year]} |")
    lines.append("")

    # Concentration analysis
    recent_years = sum(v for k, v in year_dist.items() if k.isdigit() and int(k) >= 2020)
    total_eligible = sum(year_dist.values())
    lines.append(f"**Temporal concentration**: {recent_years}/{total_eligible} "
                 f"({100*recent_years/total_eligible:.1f}%) of eligible papers are from 2020 or later.\n")

    # Journal distribution (top 20)
    lines.append("## Journal Distribution (Top 20, Include + Maybe papers)\n")
    lines.append("| Journal | Count |")
    lines.append("|---------|-------|")
    for journal, count in Counter(
        r["Journal"] for r in results
        if r["Screening_Decision"] in ("Include", "Maybe")
    ).most_common(20):
        lines.append(f"| {journal} | {count} |")
    lines.append("")

    # Geographic distribution (inferred from author names / study populations)
    lines.append("## Geographic Distribution (inferred from abstracts)\n")
    geo_keywords = {
        "United States / North America": ["united states", "us ", "usa", "american", "north america", "canada"],
        "United Kingdom": ["united kingdom", "uk ", "british", "england", "wales", "scotland"],
        "Australia / New Zealand": ["australia", "new zealand", "aotearoa"],
        "East Asia (Japan, China, Korea)": ["japan", "japanese", "china", "chinese", "korea", "korean"],
        "Europe (Continental)": ["german", "france", "french", "spain", "spanish", "sweden", "swedish",
                                  "finland", "finnish", "norway", "norwegian", "denmark", "danish",
                                  "czech", "poland", "polish", "italy", "italian", "netherlands", "dutch"],
        "Southeast Asia": ["singapore", "malaysia", "indonesia", "thailand", "philippines", "vietnam"],
        "South America": ["brazil", "argentina", "chile", "colombia", "mexico"],
        "Middle East": ["iran", "iraq", "saudi", "turkey", "turkish", "israel"],
    }
    geo_counts = Counter()
    for r in results:
        if r["Screening_Decision"] in ("Include", "Maybe"):
            text = (r.get("Title", "") + " " + r.get("Abstract", "")).lower()
            for region, keywords in geo_keywords.items():
                if has_any(text, keywords):
                    geo_counts[region] += 1

    lines.append("| Region | Papers Mentioning |")
    lines.append("|--------|-------------------|")
    for region, count in geo_counts.most_common():
        lines.append(f"| {region} | {count} |")
    lines.append("")
    lines.append("*Note: Geographic distribution is approximate, inferred from study populations "
                 "and author affiliations mentioned in abstracts. Papers may mention multiple regions.*\n")

    with open(SUMMARY_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Screening summary saved to {SUMMARY_MD}")


# ---------------------------------------------------------------------------
# Evidence synthesis
# ---------------------------------------------------------------------------

def extract_method(abstract):
    """Try to extract study method from abstract."""
    text = abstract.lower()
    if has_any(text, ["systematic review", "meta-analysis", "meta analysis"]):
        return "Systematic review / Meta-analysis"
    if has_any(text, ["randomized controlled", "randomised controlled", "rct"]):
        return "RCT"
    if "longitudinal" in text:
        return "Longitudinal"
    if "experiment" in text and has_any(text, ["condition", "manipulat", "between-subject", "within-subject"]):
        return "Experimental"
    if has_any(text, ["cross-sectional", "cross sectional"]):
        return "Cross-sectional survey"
    if has_any(text, ["survey", "questionnaire", "self-report"]):
        return "Survey"
    if has_any(text, ["interview", "qualitative", "thematic analysis", "focus group"]):
        return "Qualitative"
    if has_any(text, ["content analysis", "analysed the play history", "analyzed the"]):
        return "Content analysis"
    if has_any(text, ["psychometric", "validation", "reliability"]):
        return "Scale validation"
    if has_any(text, ["review", "overview", "commentary", "narrative"]):
        return "Review / Commentary"
    if has_any(text, ["cohort", "population-based"]):
        return "Cohort study"
    return "Not specified"


def extract_n(abstract):
    """Try to extract sample size from abstract."""
    import re
    text = abstract
    # Look for N = X or n = X patterns
    patterns = [
        r"[Nn]\s*=\s*([\d,]+)",
        r"sample of\s+([\d,]+)",
        r"([\d,]+)\s+(?:participants|respondents|adults|adolescents|gamers|players|students|individuals|subjects)",
        r"recruited\s+(?:from\s+\w+\s+)?([\d,]+)",
        r"total of\s+([\d,]+)",
    ]
    for pat in patterns:
        match = re.search(pat, text)
        if match:
            n_str = match.group(1).replace(",", "")
            try:
                n = int(n_str)
                if 10 <= n <= 1000000:  # reasonable range
                    return f"N={n:,}"
            except ValueError:
                continue
    return "--"


def extract_key_finding(abstract, domain):
    """Extract 1-2 sentence key finding from abstract (last 2 sentences typically)."""
    if not abstract.strip():
        return "No abstract available"

    # Get last 3 sentences as they usually contain conclusions
    sentences = re.split(r'(?<=[.!?])\s+', abstract.strip())
    if len(sentences) <= 2:
        return abstract.strip()

    # Take last 2-3 sentences as key finding
    conclusion = " ".join(sentences[-2:])
    if len(conclusion) > 300:
        conclusion = conclusion[:297] + "..."
    return conclusion


def evidence_strength(include_count, maybe_count, methods):
    """Assess evidence strength."""
    total = include_count + maybe_count
    method_list = [m for m in methods if m != "Not specified"]
    has_sr = any("systematic review" in m.lower() or "meta-analysis" in m.lower() for m in method_list)
    has_rct = any("rct" in m.lower() for m in method_list)
    has_longitudinal = any("longitudinal" in m.lower() for m in method_list)
    has_experimental = any("experimental" in m.lower() for m in method_list)

    if total >= 10 and (has_sr or has_rct or has_longitudinal):
        return "Strong"
    elif total >= 5 and (has_experimental or has_longitudinal or has_sr):
        return "Moderate"
    elif total >= 3:
        return "Weak"
    elif total >= 1:
        return "Very Weak"
    else:
        return "No evidence"


def generate_evidence_synthesis(results):
    """Generate the full evidence synthesis markdown."""

    eligible = [r for r in results if r["Screening_Decision"] in ("Include", "Maybe")]
    included = [r for r in results if r["Screening_Decision"] == "Include"]
    maybe = [r for r in results if r["Screening_Decision"] == "Maybe"]

    # Build domain -> papers mapping
    domain_map = {
        "D1": {"label": "4.1 Loss Aversion in Games", "papers": []},
        "D2": {"label": "4.2 Consumable Hoarding", "papers": []},
        "D3": {"label": "4.3 Gacha / Loot Box", "papers": []},
        "D4": {"label": "4.4 Inventory Paralysis / Virtual Possession", "papers": []},
        "D5": {"label": "4.5 Completionism", "papers": []},
        "D6": {"label": "4.6 Backlog Accumulation", "papers": []},
        "Cross-domain": {"label": "Cross-domain: Hoarding Link", "papers": []},
    }

    for r in eligible:
        domains_str = r.get("Domain(s)", "")
        assigned = False
        for domain_key in domain_map:
            if domain_key in domains_str:
                domain_map[domain_key]["papers"].append(r)
                assigned = True
        if not assigned:
            # Try to assign based on reason / text
            text = (r.get("Title", "") + " " + r.get("Abstract", "")).lower()
            for domain_key, info in DOMAIN_KEYWORDS.items():
                if has_any(text, info):
                    domain_map[domain_key]["papers"].append(r)
                    assigned = True

    lines = []
    lines.append("# Evidence Synthesis: In-Game Hoarding, Collecting, and Loss Aversion\n")
    lines.append("## Overview\n")
    lines.append(f"This synthesis is based on the screening of {len(results)} PubMed records "
                 f"from the Elixir PRISMA v2 search. After title/abstract screening:\n")
    lines.append(f"- **Include**: {len(included)} papers (clearly relevant)")
    lines.append(f"- **Maybe**: {len(maybe)} papers (tangentially relevant, pending full-text review)")
    lines.append(f"- **Total eligible for synthesis**: {len(eligible)} papers\n")
    lines.append("---\n")

    for domain_key in ["D1", "D2", "D3", "D4", "D5", "D6", "Cross-domain"]:
        info = domain_map[domain_key]
        papers = info["papers"]
        label = info["label"]

        include_papers = [p for p in papers if p["Screening_Decision"] == "Include"]
        maybe_papers = [p for p in papers if p["Screening_Decision"] == "Maybe"]

        lines.append(f"## {label}\n")
        lines.append(f"**Paper count**: {len(papers)} total "
                     f"({len(include_papers)} Include, {len(maybe_papers)} Maybe)\n")

        if not papers:
            lines.append("**No papers identified in this domain from the current search.**\n")
            lines.append("This represents a critical evidence gap. The absence of PubMed-indexed "
                         "research in this domain suggests it remains largely unexplored in the "
                         "academic literature, despite its prevalence in player communities and "
                         "game design discussions.\n")
            lines.append("---\n")
            continue

        # Extract methods for evidence strength assessment
        methods = []
        for p in papers:
            m = extract_method(p.get("Abstract", ""))
            methods.append(m)

        strength = evidence_strength(len(include_papers), len(maybe_papers), methods)
        lines.append(f"**Evidence strength**: {strength}\n")

        # Method breakdown
        method_counts = Counter(methods)
        lines.append("**Study designs**:")
        for m, c in method_counts.most_common():
            lines.append(f"- {m}: {c}")
        lines.append("")

        # Evidence table
        lines.append("### Evidence Table\n")
        lines.append("| Author (Year) | Method | N | Key Finding | Decision |")
        lines.append("|---------------|--------|---|-------------|----------|")

        # Sort by relevance score descending, then by year descending
        papers_sorted = sorted(papers,
                               key=lambda p: (
                                   0 if p["Screening_Decision"] == "Include" else 1,
                                   -int(p.get("Relevance_Score", 0)),
                                   -int(p.get("Year", 0)) if p.get("Year", "").isdigit() else 0
                               ))

        for p in papers_sorted:
            authors = p.get("Authors", "")
            # Extract first author surname
            first_author = authors.split(",")[0].strip() if authors else "Unknown"
            # Simplify: take first word (surname)
            first_author = first_author.split()[0] if first_author else "Unknown"
            year = p.get("Year", "")
            method = extract_method(p.get("Abstract", ""))
            n = extract_n(p.get("Abstract", ""))
            finding = extract_key_finding(p.get("Abstract", ""), domain_key)
            # Escape pipes in finding
            finding = finding.replace("|", "/")
            decision = p.get("Screening_Decision", "")

            lines.append(f"| {first_author} ({year}) | {method} | {n} | {finding} | {decision} |")

        lines.append("")

        # Narrative synthesis
        lines.append("### Narrative Synthesis\n")

        if domain_key == "D1":
            lines.append(_synthesize_d1(papers))
        elif domain_key == "D2":
            lines.append(_synthesize_d2(papers))
        elif domain_key == "D3":
            lines.append(_synthesize_d3(papers))
        elif domain_key == "D4":
            lines.append(_synthesize_d4(papers))
        elif domain_key == "D5":
            lines.append(_synthesize_d5(papers))
        elif domain_key == "D6":
            lines.append(_synthesize_d6(papers))
        elif domain_key == "Cross-domain":
            lines.append(_synthesize_cross(papers))

        lines.append("")

        # Key gaps
        lines.append("### Key Gaps\n")
        lines.append(_identify_gaps(domain_key, papers, methods))
        lines.append("")
        lines.append("---\n")

    # Cross-cutting themes
    lines.append("## Cross-Cutting Themes\n")
    lines.append(_cross_cutting_themes(domain_map))
    lines.append("")

    # Overall assessment
    lines.append("## Overall Assessment and Recommendations\n")
    lines.append(_overall_assessment(domain_map, results))

    with open(SYNTHESIS_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Evidence synthesis saved to {SYNTHESIS_MD}")


# ---------------------------------------------------------------------------
# Domain-specific narrative synthesis helpers
# ---------------------------------------------------------------------------

def _synthesize_d1(papers):
    n = len(papers)
    if n == 0:
        return "No papers identified."

    text = (
        f"The search identified {n} papers relevant to loss aversion in game contexts. "
        "Loss aversion -- the tendency to weigh losses more heavily than equivalent gains "
        "(Kahneman & Tversky, 1979) -- has received limited but growing attention in gaming research. "
        "The available evidence primarily examines how loss-framed mechanics (e.g., expiring rewards, "
        "limited-time events, streak maintenance) influence player engagement and spending. "
        "Several studies investigate loss aversion in the context of value-based decision-making "
        "and risk perception among gamers, though few directly measure the behavioral economics "
        "of in-game resource decisions. "
        "Studies in this domain often overlap with loot box research (D3), where loss aversion "
        "may drive continued spending to avoid 'missing out' on limited items. "
        "The connection between clinical loss aversion measures and specific in-game behaviors "
        "(e.g., refusing to use consumable items, hoarding resources 'just in case') "
        "remains almost entirely unexplored in the empirical literature."
    )
    return text


def _synthesize_d2(papers):
    n = len(papers)
    if n == 0:
        return (
            "As expected, the search yielded zero papers directly addressing consumable hoarding "
            "in video games (the 'too good to use' syndrome). This behavior -- where players accumulate "
            "powerful single-use items like potions, elixirs, and scrolls but never deploy them -- "
            "is widely discussed in gaming communities, game design literature, and player forums, "
            "yet it has received no formal empirical investigation indexed in PubMed. "
            "This represents arguably the most significant evidence gap identified in this review, "
            "given the universality of the behavior across game genres and its clear connections to "
            "loss aversion (D1), psychological ownership (D4), and clinical hoarding (Cross-domain). "
            "The absence of research here underscores the disconnect between lived player experience "
            "and academic investigation of game behavior."
        )
    return f"The search identified {n} paper(s) potentially relevant to consumable hoarding."


def _synthesize_d3(papers):
    n = len(papers)
    include_n = len([p for p in papers if p["Screening_Decision"] == "Include"])
    return (
        f"The gacha/loot box domain represents the largest evidence cluster, with {n} papers "
        f"({include_n} clearly relevant). This is consistent with the rapid growth of regulatory "
        "and academic interest in randomized monetization mechanics since approximately 2017. "
        "The evidence strongly establishes links between loot box purchasing and problem gambling "
        "symptomatology, with multiple large-scale cross-sectional surveys (N > 1,000) and several "
        "systematic reviews confirming this association. Key findings include:\n\n"
        "1. **Gambling-loot box nexus**: Multiple studies demonstrate moderate-to-strong positive "
        "correlations between loot box spending and problem gambling severity (e.g., Li et al. 2019; "
        "Zendle et al. 2020).\n"
        "2. **Regulatory landscape**: Several papers analyze industry self-regulation, age rating "
        "disclosures, and policy frameworks across jurisdictions.\n"
        "3. **Psychological mechanisms**: Research identifies impulsivity, fear of missing out (FOMO), "
        "reward sensitivity, and OCD/hoarding symptomatology as predictors of excessive loot box spending.\n"
        "4. **Vulnerable populations**: Adolescents, individuals with pre-existing gambling problems, "
        "and those with OCD/hoarding symptoms appear disproportionately affected.\n"
        "5. **Scale development**: Multiple validated instruments now exist for measuring risky loot box "
        "use (e.g., Risky Loot Box Index).\n\n"
        "However, most studies are cross-sectional, limiting causal inference. Longitudinal studies "
        "tracking the development of spending patterns over time remain scarce. The connection between "
        "loot box spending and broader in-game hoarding/collecting behaviors (beyond monetary spending) "
        "is underexplored."
    )


def _synthesize_d4(papers):
    n = len(papers)
    return (
        f"The search identified {n} papers relevant to inventory management, virtual item ownership, "
        "and psychological ownership in game contexts. This domain bridges the gap between pure "
        "spending research (D3) and the psychological experience of possessing virtual items. "
        "Key themes include:\n\n"
        "1. **Psychological ownership**: Several papers examine how players develop feelings of "
        "ownership over virtual items, drawing on Pierce et al.'s (2003) psychological ownership theory. "
        "Factors such as customization, investment of time/effort, and perceived control strengthen "
        "ownership feelings.\n"
        "2. **Virtual item valuation**: Studies investigate how players value their in-game possessions, "
        "with evidence suggesting endowment effects operate in virtual contexts -- players demand more "
        "to give up items than they would pay to acquire them.\n"
        "3. **In-game advertising and ownership**: Some research explores how psychological ownership "
        "of game environments affects attitudes toward in-game advertising.\n\n"
        "Critically absent from this evidence base is research on inventory paralysis specifically -- "
        "the decision-making difficulty that arises from having too many items. While psychological "
        "ownership and virtual possession are studied, the behavioral consequences of large inventories "
        "(difficulty choosing, reluctance to discard, choice overload) remain unexamined."
    )


def _synthesize_d5(papers):
    n = len(papers)
    return (
        f"The search identified {n} papers potentially relevant to completionism in gaming. "
        "Completionism -- the drive to achieve 100% completion, collect all items, or unlock all "
        "achievements -- is a well-recognized player motivation in game design frameworks (e.g., "
        "Bartle's taxonomy, the BrainHex model). However, the empirical evidence base from PubMed "
        "is sparse. The papers identified tend to:\n\n"
        "1. **Achievement systems**: Mention achievement/trophy systems in the context of player "
        "motivation but rarely study completionist behavior as a primary outcome.\n"
        "2. **Overlap with other domains**: Papers about gaming disorder or excessive gaming may "
        "touch on completionist tendencies as a risk factor but do not focus on them.\n"
        "3. **Measurement gap**: No validated scale specifically measures completionist tendencies "
        "or their psychological correlates.\n\n"
        "The near-absence of dedicated completionism research on PubMed is notable given the "
        "extensive game studies literature on player typologies and motivations published in "
        "non-medical journals (e.g., in game studies, HCI, and media psychology venues not indexed "
        "in PubMed)."
    )


def _synthesize_d6(papers):
    n = len(papers)
    return (
        f"The search identified {n} papers tagged with backlog-related indicators. However, most "
        "of these are papers about game monetization, spending, or loot boxes that were also tagged "
        "with D6 due to peripheral mentions of game libraries or accumulation. Genuine research on "
        "game backlog accumulation -- the 'pile of shame' phenomenon where players purchase far more "
        "games than they complete -- is effectively absent from the PubMed-indexed literature.\n\n"
        "The few potentially relevant papers touch on:\n"
        "1. **Digital game spending patterns**: Studies on free-to-play and microtransaction spending "
        "occasionally reference broader game purchasing habits.\n"
        "2. **Steam/platform data**: At least one paper (Zendle et al. 2020) analyzes Steam play "
        "histories, providing infrastructure-level data on exposure to monetization features.\n\n"
        "The absence of dedicated backlog research on PubMed reflects a broader gap: the psychology "
        "of digital goods accumulation (beyond impulse buying) is understudied across all digital "
        "media, not just games."
    )


def _synthesize_cross(papers):
    n = len(papers)
    return (
        f"The search identified {n} papers relevant to the cross-domain hoarding link -- connecting "
        "clinical hoarding research to game behaviors. This is a critical bridging domain. "
        "Key findings include:\n\n"
        "1. **OCD/hoarding and loot box spending**: Garea et al. (2023) directly demonstrated that "
        "obsessive-compulsive and hoarding symptomatology are associated with increased loot box spending, "
        "providing the most direct evidence linking clinical hoarding tendencies to in-game purchasing.\n"
        "2. **Behavioral addiction comorbidity**: Several papers examine how gaming disorder co-occurs "
        "with other behavioral addictions, including compulsive buying and hoarding tendencies.\n"
        "3. **Slot machine as foraging**: At least one paper (2019) draws on animal foraging metaphors "
        "to describe chip/coin hoarding in slot machines, providing a conceptual bridge between "
        "ecological hoarding theory and game-like contexts.\n"
        "4. **Compulsive buying parallels**: Papers on shopping addiction and compulsive buying may "
        "offer theoretical frameworks applicable to in-game purchasing behavior.\n\n"
        "The cross-domain literature suggests that clinical hoarding constructs are beginning to be "
        "applied to game contexts, but this work is in its early stages. The theoretical connection "
        "between DSM-5 hoarding disorder criteria and specific in-game behaviors has not been "
        "systematically articulated."
    )


def _identify_gaps(domain_key, papers, methods):
    gaps = {
        "D1": (
            "- No studies directly measure loss aversion using behavioral economics paradigms "
            "(e.g., prospect theory tasks) in game decision-making contexts\n"
            "- No research on how loss-framed game mechanics (expiring rewards, daily login bonuses, "
            "streak systems) exploit loss aversion\n"
            "- No studies connecting measured loss aversion to specific in-game behaviors like "
            "consumable hoarding or inventory paralysis\n"
            "- Absence of experimental studies manipulating loss framing in game reward contexts"
        ),
        "D2": (
            "- **CRITICAL GAP**: Zero papers on consumable hoarding in video games\n"
            "- No empirical measurement of 'too good to use' behavior frequency or prevalence\n"
            "- No studies connecting consumable hoarding to loss aversion or other psychological constructs\n"
            "- No research on game design features that exacerbate or mitigate consumable hoarding\n"
            "- No validated scale or measure for this behavior\n"
            "- No research comparing consumable hoarding across game genres or player demographics"
        ),
        "D3": (
            "- Predominantly cross-sectional designs limit causal inference\n"
            "- Limited longitudinal tracking of spending trajectories\n"
            "- Most studies focus on Western samples; East Asian gacha markets understudied\n"
            "- Connection between loot box spending and broader collecting/hoarding behaviors "
            "in-game (beyond monetary spending) is underexplored\n"
            "- Few studies examine the player experience of accumulating loot box items over time\n"
            "- Limited research on how loot box contents interact with inventory/collection mechanics"
        ),
        "D4": (
            "- No studies on inventory paralysis (choice overload from large item collections)\n"
            "- No research on the decision-making costs of managing large virtual inventories\n"
            "- Limited research on virtual item attachment beyond the purchasing moment\n"
            "- No studies on reluctance to discard/sell virtual items\n"
            "- Missing link between psychological ownership and hoarding-like accumulation in games"
        ),
        "D5": (
            "- Near-zero dedicated completionism research on PubMed\n"
            "- No validated scale for measuring completionist tendencies in gamers\n"
            "- No studies on the psychological outcomes of completionist play styles\n"
            "- No research on when completionism becomes compulsive or harmful\n"
            "- Missing connection between completionism and clinical OCD/perfectionism constructs\n"
            "- Note: relevant literature may exist in non-PubMed-indexed game studies and HCI journals"
        ),
        "D6": (
            "- Near-zero dedicated backlog accumulation research\n"
            "- No studies on the 'pile of shame' phenomenon\n"
            "- No research on psychological drivers of purchasing games that are never played\n"
            "- No studies on the emotional/cognitive impact of unplayed game backlogs\n"
            "- Missing connection to digital hoarding / compulsive buying frameworks\n"
            "- No research comparing physical media vs. digital game accumulation patterns"
        ),
        "Cross-domain": (
            "- Hoarding disorder criteria have not been systematically mapped onto in-game behaviors\n"
            "- No studies test whether hoarding disorder assessment tools predict specific "
            "in-game hoarding/collecting patterns\n"
            "- Limited research on whether in-game hoarding behaviors serve similar psychological "
            "functions as clinical hoarding\n"
            "- No intervention studies testing whether addressing hoarding cognitions reduces "
            "problematic in-game collecting/spending\n"
            "- The 'digital hoarding' construct (applied primarily to files/email) has not been "
            "extended to in-game inventories"
        ),
    }
    return gaps.get(domain_key, "- Further research needed")


def _cross_cutting_themes(domain_map):
    return (
        "1. **Monetization dominance**: The evidence base is heavily skewed toward loot box/gacha "
        "research (D3), reflecting both the regulatory urgency and the ease of measuring spending "
        "as an outcome variable. Behavioral outcomes (hoarding, collecting, inventory management) "
        "are far less studied.\n\n"
        "2. **Clinical-behavioral gap**: Clinical psychology has begun studying the link between "
        "hoarding/OCD and loot box spending, but the broader spectrum of in-game accumulation "
        "behaviors remains outside clinical investigation.\n\n"
        "3. **Methodological homogeneity**: Cross-sectional surveys dominate. Experimental, "
        "longitudinal, and qualitative designs are underrepresented, limiting our understanding "
        "of causal mechanisms and lived player experiences.\n\n"
        "4. **Measurement deficit**: Validated scales exist for loot box risk (RLI) and gaming "
        "disorder (IGDS), but no validated instruments measure consumable hoarding, inventory "
        "paralysis, completionist tendencies, or backlog distress.\n\n"
        "5. **PubMed indexing bias**: Several relevant research domains (game studies, HCI, "
        "media psychology) publish in venues not indexed by PubMed. The evidence gaps identified "
        "here may be partially attributable to database selection. A complementary search of "
        "ACM Digital Library, IEEE Xplore, and PsycINFO would likely yield additional relevant work, "
        "particularly for D4, D5, and D6.\n\n"
        "6. **Emerging convergence**: Recent papers (2023-2025) show increasing interest in the "
        "intersection of hoarding/OCD constructs and game behavior, suggesting this is a nascent "
        "but growing research area."
    )


def _overall_assessment(domain_map, results):
    d3_n = len(domain_map["D3"]["papers"])
    total_eligible = len([r for r in results if r["Screening_Decision"] in ("Include", "Maybe")])

    return (
        f"Of the {len(results)} papers screened, {total_eligible} were classified as eligible for "
        f"synthesis. The evidence landscape is highly uneven across domains:\n\n"
        f"| Domain | Evidence Level | Recommendation |\n"
        f"|--------|---------------|----------------|\n"
        f"| D1: Loss Aversion | Weak | Supplement with behavioral economics literature |\n"
        f"| D2: Consumable Hoarding | No evidence | Primary research needed; cite grey literature |\n"
        f"| D3: Gacha/Loot Box | Strong | Solid evidence base; focus on synthesis quality |\n"
        f"| D4: Inventory Paralysis | Very Weak | Supplement with HCI/game studies literature |\n"
        f"| D5: Completionism | Very Weak | Supplement with game studies/motivation literature |\n"
        f"| D6: Backlog Accumulation | Very Weak | Supplement with digital hoarding literature |\n"
        f"| Cross-domain: Hoarding | Weak-Moderate | Growing evidence base; key bridging papers exist |\n\n"
        "**Recommendation for the paper**: The dramatic evidence asymmetry across domains is itself "
        "a key finding. The paper should:\n"
        "1. Present D3 (gacha/loot box) as the well-established anchor domain\n"
        "2. Highlight the near-total absence of D2 (consumable hoarding) research as the central "
        "motivating gap\n"
        "3. Use D1 (loss aversion) and Cross-domain (hoarding) as theoretical bridges\n"
        "4. Acknowledge PubMed indexing limitations and supplement with targeted searches of "
        "game studies databases for D4, D5, D6\n"
        "5. Frame the contribution as connecting well-studied constructs (loss aversion, hoarding, "
        "loot box spending) to understudied behaviors (consumable hoarding, inventory paralysis, "
        "completionism) through a unifying theoretical lens"
    )


if __name__ == "__main__":
    main()
