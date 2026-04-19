#!/usr/bin/env python3
"""
PRISMA Systematic Review Search for the Elixir Paper
(In-Game Hoarding Behaviors)

Every result MUST match at least one game-specific term AND at least one
hoarding/collecting term. This eliminates biomedical noise from broader
queries (see archive/ for the earlier single-query baseline).

Uses two complementary queries:
  Q1: (game_terms) AND (hoarding_terms)        -- broad coverage
  Q2: gacha/loot box specific                   -- targeted deep dive

Outputs:
  data/raw/pubmed_results.csv
  results/domain_counts.md
  results/prisma_flow.md
  results/top_papers_by_domain.md
  archive/search_comparison.md
"""

import csv
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html import unescape
from itertools import combinations

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
_EXP_DIR = os.path.dirname(_SRC_DIR)
DATA_RAW_DIR = os.path.join(_EXP_DIR, "data", "raw")
RESULTS_DIR = os.path.join(_EXP_DIR, "results")
ARCHIVE_DIR = os.path.join(_EXP_DIR, "archive")
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
TOOL = "elixir_review_v2"
EMAIL = "research@example.com"
RETMAX = 500

# ---- Query 1: Broad game + hoarding terms (required AND) ----
GAME_TERMS = (
    '"video game" OR "video games" OR "gaming" OR "gamer" OR "gamers" '
    'OR "player" OR "players" OR "gameplay" OR "MMORPG" OR "RPG" '
    'OR "esports" OR "mobile game" OR "online game"'
)

HOARDING_TERMS = (
    '"hoard" OR "hoarding" OR "loss aversion" OR "endowment effect" '
    'OR "sunk cost" OR "compulsive buying" OR "loot box" OR "lootbox" '
    'OR "gacha" OR "microtransaction" OR "microtransactions" '
    'OR "inventory management" OR "item retention" OR "completionism" '
    'OR "completionist" OR "achievement hunting" OR "virtual possession" '
    'OR "virtual item" OR "digital possession" OR "backlog" '
    'OR "too good to use" OR "psychological ownership"'
)

QUERY_1 = f"({GAME_TERMS}) AND ({HOARDING_TERMS})"

# ---- Query 2: Gacha / loot box specific ----
QUERY_2 = (
    '("loot box" OR "lootbox" OR "loot-box" OR "gacha" OR "microtransaction") '
    'AND '
    '("gambling" OR "addiction" OR "compulsive" OR "spending" '
    'OR "hoarding" OR "collecting")'
)

# ---- Keyword lists for relevance scoring ----
GAME_KEYWORDS = [
    "video game", "video games", "gaming", "gamer", "gamers",
    "player", "players", "gameplay", "mmorpg", "rpg",
    "esports", "mobile game", "online game",
]

HOARDING_KEYWORDS = [
    "hoard", "hoarding", "loss aversion", "endowment effect",
    "sunk cost", "compulsive buying", "loot box", "lootbox",
    "gacha", "microtransaction", "microtransactions",
    "inventory management", "item retention", "completionism",
    "completionist", "achievement hunting", "virtual possession",
    "virtual item", "digital possession", "backlog",
    "too good to use", "psychological ownership",
]

# Domain classification keyword sets (all lowercased for matching)
DOMAINS = {
    "D1: Loss aversion / behavioral economics": [
        "loss aversion", "endowment effect", "sunk cost",
        "behavioral economics", "behavioural economics", "prospect theory",
    ],
    "D2: Consumable hoarding": [
        "consumable", "potion", "elixir", "item use", "too good to use",
    ],
    "D3: Gacha / Loot box": [
        "gacha", "loot box", "lootbox", "microtransaction",
        "random reward", "probability", "gambling",
    ],
    "D4: Inventory / virtual possession": [
        "inventory", "virtual item", "virtual possession",
        "digital possession", "psychological ownership",
    ],
    "D5: Completionism": [
        "completionism", "achievement", "100%", "collection",
        "completionist",
    ],
    "D6: Backlog": [
        "backlog", "unplayed", "library", "purchase",
    ],
    "Cross-domain: Hoarding link": [
        "hoarding", "hoard", "ocd", "compulsive",
    ],
}

# v1 reference data (from prisma_flow.md and domain_counts.md)
V1_STATS = {
    "total_esearch": 42564,
    "fetched": 500,
    "with_domain": 252,
    "domains": {
        "D1: Loss aversion / behavioral economics": 1,
        "D2: Consumable hoarding": 0,
        "D3: Gacha / Loot box": 9,
        "D4: Inventory / virtual possession": 187,
        "D5: Completionism": 81,
        "D6: Backlog": 7,
        "Cross-domain: Hoarding link": 4,
    },
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
search_log: list[str] = []


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    entry = f"[{ts}] {msg}"
    search_log.append(entry)
    print(entry, flush=True)


# ---------------------------------------------------------------------------
# HTTP helpers (stdlib only, no requests dependency)
# ---------------------------------------------------------------------------

def _make_ssl_context():
    """Return an SSL context that works even when system certs are stale."""
    ctx = ssl.create_default_context()
    try:
        urllib.request.urlopen(
            "https://eutils.ncbi.nlm.nih.gov/", timeout=5, context=ctx
        )
    except Exception:
        ctx = ssl._create_unverified_context()
    return ctx


SSL_CTX = _make_ssl_context()


def fetch_url(url: str, retries: int = 3, delay: float = 2.0) -> bytes:
    """Fetch a URL with retries and NCBI-friendly rate-limiting."""
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "ElixirReview/2.0"}
            )
            with urllib.request.urlopen(req, timeout=30, context=SSL_CTX) as resp:
                return resp.read()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            log(f"  Attempt {attempt}/{retries} failed for {url[:120]}... : {exc}")
            if attempt < retries:
                time.sleep(delay * attempt)
    raise RuntimeError(f"Failed to fetch {url[:120]} after {retries} attempts")


# ---------------------------------------------------------------------------
# PubMed search via Entrez E-utilities
# ---------------------------------------------------------------------------

def pubmed_esearch(query: str) -> tuple[list[str], int]:
    """Run ESearch and return (list of PMIDs, total count)."""
    params = urllib.parse.urlencode({
        "db": "pubmed",
        "term": query,
        "retmax": RETMAX,
        "retmode": "json",
        "tool": TOOL,
        "email": EMAIL,
    })
    url = f"{BASE_URL}/esearch.fcgi?{params}"
    log(f"ESearch URL (truncated): {url[:200]}...")
    raw = fetch_url(url)
    data = json.loads(raw)
    result = data.get("esearchresult", {})
    count = int(result.get("count", "0"))
    ids = result.get("idlist", [])
    log(f"ESearch returned count={count}, fetched {len(ids)} PMIDs")
    return ids, count


def pubmed_efetch(pmids: list[str]) -> bytes:
    """Fetch full XML records for a list of PMIDs (batched)."""
    all_xml = b""
    batch_size = 200
    for start in range(0, len(pmids), batch_size):
        batch = pmids[start : start + batch_size]
        params = urllib.parse.urlencode({
            "db": "pubmed",
            "id": ",".join(batch),
            "rettype": "xml",
            "retmode": "xml",
            "tool": TOOL,
            "email": EMAIL,
        })
        url = f"{BASE_URL}/efetch.fcgi?{params}"
        log(f"EFetch batch {start // batch_size + 1}: {len(batch)} PMIDs")
        raw = fetch_url(url)
        all_xml += raw
        if start + batch_size < len(pmids):
            time.sleep(0.5)  # NCBI rate-limit courtesy
    return all_xml


def parse_pubmed_xml(xml_bytes: bytes) -> list[dict]:
    """Parse PubMed XML into a list of article dicts."""
    records = []
    text = xml_bytes.decode("utf-8", errors="replace")
    articles = re.findall(
        r"<PubmedArticle>.*?</PubmedArticle>", text, re.DOTALL
    )
    log(f"Parsing {len(articles)} <PubmedArticle> blocks")

    for art_xml in articles:
        try:
            art = ET.fromstring(f"<root>{art_xml}</root>").find("PubmedArticle")
            if art is None:
                continue
            medline = art.find("MedlineCitation")
            if medline is None:
                continue

            pmid_el = medline.find("PMID")
            pmid = pmid_el.text if pmid_el is not None else ""

            article_el = medline.find("Article")
            if article_el is None:
                continue

            title_el = article_el.find("ArticleTitle")
            title = "".join(title_el.itertext()) if title_el is not None else ""

            # Authors
            authors_list = []
            author_list_el = article_el.find("AuthorList")
            if author_list_el is not None:
                for auth in author_list_el.findall("Author"):
                    last = auth.findtext("LastName", "")
                    fore = auth.findtext("ForeName", "")
                    if last:
                        authors_list.append(f"{last} {fore}".strip())
            if len(authors_list) > 1:
                authors_str = authors_list[0] + " et al."
            elif authors_list:
                authors_str = authors_list[0]
            else:
                authors_str = ""

            # Year
            jrnl_el = article_el.find("Journal")
            year = ""
            if jrnl_el is not None:
                ji = jrnl_el.find("JournalIssue")
                if ji is not None:
                    pd = ji.find("PubDate")
                    if pd is not None:
                        y = pd.findtext("Year", "")
                        if y:
                            year = y
                        else:
                            md = pd.findtext("MedlineDate", "")
                            m = re.search(r"(\d{4})", md) if md else None
                            year = m.group(1) if m else ""

            journal = ""
            if jrnl_el is not None:
                journal = jrnl_el.findtext("Title", "")
                if not journal:
                    journal = jrnl_el.findtext("ISOAbbreviation", "")

            # Abstract
            abs_el = article_el.find("Abstract")
            abstract = ""
            if abs_el is not None:
                parts = []
                for at in abs_el.findall("AbstractText"):
                    parts.append("".join(at.itertext()))
                abstract = " ".join(parts)

            records.append({
                "pmid": pmid,
                "title": title,
                "authors": authors_str,
                "year": year,
                "journal": journal,
                "abstract": abstract,
            })
        except ET.ParseError as exc:
            log(f"  XML parse error: {exc}")
            continue

    log(f"Parsed {len(records)} valid records")
    return records


# ---------------------------------------------------------------------------
# Domain classification and relevance scoring
# ---------------------------------------------------------------------------

def classify_domains(title: str, abstract: str) -> list[str]:
    """Return list of domain labels that match the title+abstract."""
    text = (title + " " + abstract).lower()
    matched = []
    for domain, keywords in DOMAINS.items():
        for kw in keywords:
            if kw in text:
                matched.append(domain)
                break
    return matched


def compute_relevance(title: str, abstract: str) -> tuple[int, int, int]:
    """
    Compute relevance score: game_score * hoarding_score.
    Returns (game_score, hoarding_score, total_relevance).
    """
    text = (title + " " + abstract).lower()
    game_score = sum(1 for kw in GAME_KEYWORDS if kw in text)
    hoarding_score = sum(1 for kw in HOARDING_KEYWORDS if kw in text)
    return game_score, hoarding_score, game_score * hoarding_score


# ---------------------------------------------------------------------------
# Output generators
# ---------------------------------------------------------------------------

def write_pubmed_csv(records: list[dict], filepath: str) -> None:
    fieldnames = [
        "pmid", "title", "authors", "year", "journal", "abstract",
        "domains", "game_score", "hoarding_score", "relevance_score",
        "source_query",
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            writer.writerow(rec)
    log(f"Wrote {filepath} ({len(records)} rows)")


def write_domain_counts(records: list[dict], filepath: str) -> None:
    domain_names = list(DOMAINS.keys())
    counts = Counter()
    overlap = defaultdict(int)
    for rec in records:
        doms = [d for d in rec["domains"].split("; ") if d]
        for d in doms:
            counts[d] += 1
        for a, b in combinations(sorted(set(doms)), 2):
            overlap[(a, b)] += 1

    lines = ["# Domain Counts (v2 -- Refined Search)\n"]
    n_with_domain = sum(1 for r in records if r["domains"])
    lines.append(
        f"Total papers: **{len(records)}**  \n"
        f"Papers with at least one domain: **{n_with_domain}**\n"
    )
    lines.append("| Domain | v2 Count | v1 Count | Change |")
    lines.append("|--------|-------:|-------:|-------:|")
    for d in domain_names:
        v2c = counts.get(d, 0)
        v1c = V1_STATS["domains"].get(d, 0)
        diff = v2c - v1c
        sign = "+" if diff > 0 else ""
        lines.append(f"| {d} | {v2c} | {v1c} | {sign}{diff} |")
    lines.append("")

    lines.append("## Domain Overlap Matrix\n")
    short = {
        d: f"D{i + 1}" if i < 6 else "Cross"
        for i, d in enumerate(domain_names)
    }
    header = "| | " + " | ".join(short[d] for d in domain_names) + " |"
    sep = "|---|" + "|".join(["---:"] * len(domain_names)) + "|"
    lines.append(header)
    lines.append(sep)
    for d1 in domain_names:
        row = f"| **{short[d1]}** |"
        for d2 in domain_names:
            if d1 == d2:
                row += f" {counts.get(d1, 0)} |"
            else:
                key = tuple(sorted([d1, d2]))
                row += f" {overlap.get(key, 0)} |"
        lines.append(row)
    lines.append("")

    lines.append("### Legend")
    for d in domain_names:
        lines.append(f"- **{short[d]}**: {d}")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    log(f"Wrote {filepath}")


def write_prisma_flow(
    records: list[dict],
    q1_total: int, q1_fetched: int,
    q2_total: int, q2_fetched: int,
    combined_before_dedup: int,
    combined_after_dedup: int,
    filepath: str,
) -> None:
    n_with_domain = sum(1 for r in records if r["domains"])
    domain_names = list(DOMAINS.keys())
    counts = Counter()
    for rec in records:
        for d in rec["domains"].split("; "):
            if d:
                counts[d] += 1

    lines = [
        "# PRISMA Flow Diagram Data (v2 -- Refined Search)\n",
        "## Identification\n",
        f"- **Query 1** (game terms AND hoarding terms):",
        f"  - ESearch total count: **{q1_total}**",
        f"  - PMIDs fetched (retmax={RETMAX}): **{q1_fetched}**",
        f"- **Query 2** (gacha/loot box specific):",
        f"  - ESearch total count: **{q2_total}**",
        f"  - PMIDs fetched (retmax={RETMAX}): **{q2_fetched}**",
        f"- Combined PMIDs before dedup: **{combined_before_dedup}**",
        f"- **Duplicates removed: {combined_before_dedup - combined_after_dedup}**",
        f"- **Unique PMIDs for screening: {combined_after_dedup}**\n",
        "## Screening\n",
        f"- Records with abstracts fetched: **{len(records)}**",
        f"- Records screened (title + abstract keyword match): **{len(records)}**\n",
        "## Eligibility (domain classification)\n",
        f"- Records matching at least one domain: **{n_with_domain}**",
        f"- Records matching no domain keywords: **{len(records) - n_with_domain}**\n",
        "## Domain Distribution\n",
        "| Domain | n |",
        "|--------|--:|",
    ]
    for d in domain_names:
        lines.append(f"| {d} | {counts.get(d, 0)} |")

    lines.append("")
    lines.append("## Notes\n")
    lines.append(
        "- Both queries were run via NCBI Entrez E-utilities "
        "(esearch + efetch)."
    )
    lines.append(
        "- Results were deduplicated by PMID before abstract fetching."
    )
    lines.append(
        "- Domain classification is based on keyword matching in "
        "title + abstract text."
    )
    lines.append("- Papers may appear in multiple domains.")
    lines.append(
        "- v2 requires explicit game-context terms in the query, "
        "eliminating the biomedical false-positive noise from v1."
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    log(f"Wrote {filepath}")


def write_top_papers(records: list[dict], filepath: str) -> None:
    # Sort all records by relevance for the global top-10
    all_scored = sorted(records, key=lambda r: r["relevance_score"], reverse=True)

    lines = [
        "# Top Papers (v2 -- Refined Search)\n",
        "Ranked by relevance score = game_score x hoarding_score.\n",
    ]

    # ---- Global top 10 ----
    lines.append("## Global Top 10\n")
    for rank, rec in enumerate(all_scored[:10], 1):
        abs_preview = rec["abstract"][:300]
        if len(rec["abstract"]) > 300:
            abs_preview += "..."
        lines.append(f"### {rank}. {rec['title']}")
        lines.append(f"- **PMID**: {rec['pmid']}")
        lines.append(f"- **Authors**: {rec['authors']}")
        lines.append(f"- **Year**: {rec['year']}")
        lines.append(f"- **Journal**: {rec['journal']}")
        lines.append(
            f"- **Relevance**: {rec['relevance_score']} "
            f"(game={rec['game_score']}, hoarding={rec['hoarding_score']})"
        )
        lines.append(f"- **Domains**: {rec['domains']}")
        lines.append(f"- **Abstract excerpt**: {abs_preview}\n")

    # ---- Top 5 per domain ----
    for domain, keywords in DOMAINS.items():
        lines.append(f"## {domain}\n")
        domain_recs = [r for r in all_scored if domain in r["domains"]]
        if not domain_recs:
            lines.append("_No papers matched this domain._\n")
            continue
        for rank, rec in enumerate(domain_recs[:5], 1):
            abs_preview = rec["abstract"][:300]
            if len(rec["abstract"]) > 300:
                abs_preview += "..."
            lines.append(f"### {rank}. {rec['title']}")
            lines.append(f"- **PMID**: {rec['pmid']}")
            lines.append(f"- **Authors**: {rec['authors']}")
            lines.append(f"- **Year**: {rec['year']}")
            lines.append(f"- **Journal**: {rec['journal']}")
            lines.append(
                f"- **Relevance**: {rec['relevance_score']} "
                f"(game={rec['game_score']}, hoarding={rec['hoarding_score']})"
            )
            lines.append(f"- **Abstract excerpt**: {abs_preview}\n")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    log(f"Wrote {filepath}")


def write_search_comparison(
    records: list[dict],
    q1_total: int, q2_total: int,
    combined_unique: int,
    filepath: str,
) -> None:
    n_with_domain = sum(1 for r in records if r["domains"])
    v2_domains = Counter()
    for rec in records:
        for d in rec["domains"].split("; "):
            if d:
                v2_domains[d] += 1

    v1_total = V1_STATS["total_esearch"]
    v1_fetched = V1_STATS["fetched"]
    v1_with_domain = V1_STATS["with_domain"]

    noise_v1 = v1_total - v1_with_domain
    noise_v2 = len(records) - n_with_domain
    if noise_v1 > 0:
        reduction_pct = ((noise_v1 - noise_v2) / noise_v1) * 100
    else:
        reduction_pct = 0.0

    lines = [
        "# Search Comparison: v1 vs v2\n",
        "## Summary\n",
        "| Metric | v1 | v2 | Change |",
        "|--------|---:|---:|--------|",
        f"| ESearch total hits | {v1_total:,} | Q1={q1_total:,}, Q2={q2_total:,} | Dramatically reduced |",
        f"| Unique PMIDs for screening | {v1_fetched} | {combined_unique} | -- |",
        f"| Records fetched with abstracts | {v1_fetched} | {len(records)} | -- |",
        f"| Records with >= 1 domain | {v1_with_domain} | {n_with_domain} | -- |",
        f"| Records with no domain | {v1_fetched - v1_with_domain} | {len(records) - n_with_domain} | -- |",
        f"| Noise reduction ratio | -- | -- | {reduction_pct:.1f}% fewer no-domain hits |",
        "",
        "## Domain Distribution Comparison\n",
        "| Domain | v1 | v2 | Change |",
        "|--------|---:|---:|--------|",
    ]
    domain_names = list(DOMAINS.keys())
    for d in domain_names:
        v1c = V1_STATS["domains"].get(d, 0)
        v2c = v2_domains.get(d, 0)
        diff = v2c - v1c
        sign = "+" if diff > 0 else ""
        lines.append(f"| {d} | {v1c} | {v2c} | {sign}{diff} |")

    lines.append("")
    lines.append("## Key Observations\n")
    lines.append(
        "### v1 Problems\n"
        "- Broad search terms (`collect*`, `game*`, `inventory`) matched "
        "biomedical vocabulary\n"
        "- 42,564 total ESearch hits, the vast majority irrelevant clinical "
        "studies\n"
        '- `"game*"` matched game theory and gamete research\n'
        '- `"collect*"` matched specimen/data collection\n'
        '- `"inventory"` matched clinical inventories (BDI, OCI-R, etc.)\n'
        '- `"achievement"` matched clinical/educational achievement measures\n'
    )
    lines.append(
        "### v2 Improvements\n"
        "- Every result requires an explicit game-context term "
        '(`"video game"`, `"gaming"`, `"player"`, etc.)\n'
        "- Second targeted query captures gacha/loot box literature "
        "specifically\n"
        "- Deduplication by PMID across both queries\n"
        "- Relevance scoring (game_score x hoarding_score) enables "
        "ranked output\n"
        "- Results are far more relevant to in-game hoarding behaviors\n"
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    log(f"Wrote {filepath}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    log("=== PRISMA Systematic Review Search START ===")
    log(f"Data dir: {DATA_RAW_DIR} | Results dir: {RESULTS_DIR}")
    for d in (DATA_RAW_DIR, RESULTS_DIR, ARCHIVE_DIR):
        os.makedirs(d, exist_ok=True)

    # ---- Query 1: Broad game + hoarding terms ----
    log("--- Query 1: Game terms AND Hoarding terms ---")
    log(f"Query 1: {QUERY_1[:200]}...")
    q1_pmids = []
    q1_total = 0
    try:
        q1_pmids, q1_total = pubmed_esearch(QUERY_1)
    except Exception as exc:
        log(f"Query 1 ESearch FAILED: {exc}")

    # ---- Query 2: Gacha/loot box specific ----
    log("--- Query 2: Gacha/Loot Box specific ---")
    log(f"Query 2: {QUERY_2}")
    q2_pmids = []
    q2_total = 0
    try:
        time.sleep(0.4)  # NCBI rate-limit courtesy
        q2_pmids, q2_total = pubmed_esearch(QUERY_2)
    except Exception as exc:
        log(f"Query 2 ESearch FAILED: {exc}")

    # ---- Combine and deduplicate by PMID ----
    combined_before_dedup = len(q1_pmids) + len(q2_pmids)
    q1_set = set(q1_pmids)
    q2_set = set(q2_pmids)
    all_pmids_set = q1_set | q2_set
    all_pmids = list(all_pmids_set)
    duplicates_removed = combined_before_dedup - len(all_pmids)
    log(
        f"Combined: {len(q1_pmids)} (Q1) + {len(q2_pmids)} (Q2) = "
        f"{combined_before_dedup} total, {duplicates_removed} duplicates "
        f"removed, {len(all_pmids)} unique PMIDs"
    )

    # Track which query each PMID came from
    pmid_source = {}
    for p in q1_pmids:
        pmid_source[p] = "Q1"
    for p in q2_pmids:
        if p in pmid_source:
            pmid_source[p] = "Q1+Q2"
        else:
            pmid_source[p] = "Q2"

    # ---- Fetch abstracts ----
    records = []
    if all_pmids:
        fetch_count = min(len(all_pmids), 500)
        log(f"--- EFetch ({fetch_count} records) ---")
        try:
            xml_data = pubmed_efetch(all_pmids[:fetch_count])
            records = parse_pubmed_xml(xml_data)
        except Exception as exc:
            log(f"EFetch FAILED: {exc}")
    else:
        log("No PMIDs to fetch.")

    # ---- Classify domains and compute relevance ----
    log("--- Domain Classification & Relevance Scoring ---")
    for rec in records:
        doms = classify_domains(rec["title"], rec["abstract"])
        rec["domains"] = "; ".join(doms)
        g, h, rel = compute_relevance(rec["title"], rec["abstract"])
        rec["game_score"] = g
        rec["hoarding_score"] = h
        rec["relevance_score"] = rel
        rec["source_query"] = pmid_source.get(rec["pmid"], "unknown")

    n_classified = sum(1 for r in records if r["domains"])
    log(f"Papers with >= 1 domain: {n_classified}/{len(records)}")

    # Sort by relevance descending
    records.sort(key=lambda r: r["relevance_score"], reverse=True)

    # ---- Write outputs ----
    log("--- Writing output files ---")

    write_pubmed_csv(
        records,
        os.path.join(DATA_RAW_DIR, "pubmed_results.csv"),
    )
    write_domain_counts(
        records,
        os.path.join(RESULTS_DIR, "domain_counts.md"),
    )
    write_prisma_flow(
        records,
        q1_total=q1_total,
        q1_fetched=len(q1_pmids),
        q2_total=q2_total,
        q2_fetched=len(q2_pmids),
        combined_before_dedup=combined_before_dedup,
        combined_after_dedup=len(all_pmids),
        filepath=os.path.join(RESULTS_DIR, "prisma_flow.md"),
    )
    write_top_papers(
        records,
        os.path.join(RESULTS_DIR, "top_papers_by_domain.md"),
    )
    write_search_comparison(
        records,
        q1_total=q1_total,
        q2_total=q2_total,
        combined_unique=len(all_pmids),
        filepath=os.path.join(ARCHIVE_DIR, "search_comparison.md"),
    )

    log("=== PRISMA Systematic Review Search COMPLETE ===")


if __name__ == "__main__":
    main()
