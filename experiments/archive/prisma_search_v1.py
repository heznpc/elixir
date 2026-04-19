#!/usr/bin/env python3
"""
PRISMA Systematic Review Search for the Elixir Paper
(In-Game Hoarding Behaviors)

Databases: PubMed (via NCBI Entrez E-utilities), ACM Digital Library
Outputs:   pubmed_results.csv, domain_counts.md, prisma_flow.md,
           top_papers_by_domain.md, search_log.md
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
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
TOOL = "elixir_review"
EMAIL = "research@example.com"
RETMAX = 500

PUBMED_QUERY = (
    '(hoard* OR collect* OR "loss aversion" OR "endowment effect" '
    'OR "sunk cost" OR "compulsive buying" OR "compulsive acquisition" '
    'OR "item retention" OR "inventory management" OR "completionism" '
    'OR "achievement hunting" OR "digital possession") '
    'AND '
    '(game* OR "video game" OR "virtual" OR "loot box" OR "gacha" '
    'OR "inventory" OR "digital possession" OR "virtual item" '
    'OR "microtransaction" OR "backlog")'
)

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
# HTTP helpers  (stdlib only, no requests dependency)
# ---------------------------------------------------------------------------

def _make_ssl_context():
    """Return an SSL context that works even when system certs are stale."""
    ctx = ssl.create_default_context()
    try:
        urllib.request.urlopen("https://eutils.ncbi.nlm.nih.gov/", timeout=5, context=ctx)
    except Exception:
        ctx = ssl._create_unverified_context()
    return ctx

SSL_CTX = _make_ssl_context()

def fetch_url(url: str, retries: int = 3, delay: float = 2.0) -> bytes:
    """Fetch a URL with retries and NCBI-friendly rate-limiting."""
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ElixirReview/1.0"})
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

def pubmed_esearch(query: str) -> list[str]:
    """Run ESearch and return list of PMIDs."""
    params = urllib.parse.urlencode({
        "db": "pubmed",
        "term": query,
        "retmax": RETMAX,
        "retmode": "json",
        "tool": TOOL,
        "email": EMAIL,
    })
    url = f"{BASE_URL}/esearch.fcgi?{params}"
    log(f"ESearch URL: {url}")
    raw = fetch_url(url)
    data = json.loads(raw)
    result = data.get("esearchresult", {})
    count = result.get("count", "0")
    ids = result.get("idlist", [])
    log(f"ESearch returned count={count}, fetched {len(ids)} PMIDs")
    return ids


def pubmed_efetch(pmids: list[str]) -> bytes:
    """Fetch full XML records for a list of PMIDs (batched)."""
    all_xml = b""
    batch_size = 200
    for start in range(0, len(pmids), batch_size):
        batch = pmids[start:start + batch_size]
        params = urllib.parse.urlencode({
            "db": "pubmed",
            "id": ",".join(batch),
            "rettype": "xml",
            "retmode": "xml",
            "tool": TOOL,
            "email": EMAIL,
        })
        url = f"{BASE_URL}/efetch.fcgi?{params}"
        log(f"EFetch batch {start//batch_size + 1}: {len(batch)} PMIDs")
        raw = fetch_url(url)
        all_xml += raw
        if start + batch_size < len(pmids):
            time.sleep(0.5)          # NCBI rate-limit courtesy
    return all_xml


def parse_pubmed_xml(xml_bytes: bytes) -> list[dict]:
    """Parse PubMed XML into a list of article dicts."""
    records = []
    # Handle multiple concatenated XML documents
    text = xml_bytes.decode("utf-8", errors="replace")
    # Extract all <PubmedArticle> blocks
    articles = re.findall(r"<PubmedArticle>.*?</PubmedArticle>", text, re.DOTALL)
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
# Domain classification
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


def keyword_density(title: str, abstract: str, keywords: list[str]) -> int:
    """Count total keyword occurrences in title+abstract (for ranking)."""
    text = (title + " " + abstract).lower()
    return sum(text.count(kw) for kw in keywords)

# ---------------------------------------------------------------------------
# ACM Digital Library search  (HTML scraping, best-effort)
# ---------------------------------------------------------------------------

def acm_search(query: str, max_results: int = 50) -> list[dict]:
    """Scrape ACM DL search results page for titles, years, venues."""
    encoded = urllib.parse.quote_plus(query)
    url = f"https://dl.acm.org/action/doSearch?AllField={encoded}&pageSize={max_results}"
    log(f"ACM DL search URL: {url}")
    results = []
    try:
        raw = fetch_url(url, retries=2, delay=3.0)
        html = raw.decode("utf-8", errors="replace")

        # Extract search result entries using regex on the HTML
        # ACM DL wraps titles in <h5 class="issue-item__title"><a ...>TITLE</a></h5>
        title_pattern = re.compile(
            r'class="issue-item__title"[^>]*>\s*<[^>]+>([^<]+)<', re.IGNORECASE
        )
        # Year often appears in <span class="dot-separator"><span>MONTH YEAR</span>
        year_pattern = re.compile(
            r'class="dot-separator"[^>]*>[^<]*<span>\s*\w+\s+(\d{4})', re.IGNORECASE
        )
        # Venue / proceeding
        venue_pattern = re.compile(
            r'class="issue-item__detail"[^>]*>\s*<[^>]+>([^<]+)<', re.IGNORECASE
        )

        titles = [unescape(m.strip()) for m in title_pattern.findall(html)]
        years = year_pattern.findall(html)
        venues = [unescape(m.strip()) for m in venue_pattern.findall(html)]

        for i, t in enumerate(titles):
            results.append({
                "title": t,
                "year": years[i] if i < len(years) else "",
                "venue": venues[i] if i < len(venues) else "",
            })
        log(f"ACM DL: extracted {len(results)} results")
    except Exception as exc:
        log(f"ACM DL search failed: {exc}")
    return results

# ---------------------------------------------------------------------------
# Output generators
# ---------------------------------------------------------------------------

def write_pubmed_csv(records: list[dict], filepath: str) -> None:
    fieldnames = ["pmid", "title", "authors", "year", "journal", "abstract", "domains"]
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

    lines = ["# Domain Counts\n"]
    lines.append(f"Total papers with at least one domain: "
                 f"{sum(1 for r in records if r['domains'])}\n")
    lines.append("| Domain | Count |")
    lines.append("|--------|------:|")
    for d in domain_names:
        lines.append(f"| {d} | {counts.get(d, 0)} |")
    lines.append("")

    lines.append("## Domain Overlap Matrix\n")
    # Header
    short = {d: f"D{i+1}" if i < 6 else "Cross" for i, d in enumerate(domain_names)}
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

    # Legend
    lines.append("### Legend")
    for d in domain_names:
        lines.append(f"- **{short[d]}**: {d}")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    log(f"Wrote {filepath}")


def write_prisma_flow(records: list[dict], acm_results: list[dict],
                      total_identified: int, filepath: str) -> None:
    n_with_domain = sum(1 for r in records if r["domains"])
    domain_names = list(DOMAINS.keys())
    counts = Counter()
    for rec in records:
        for d in rec["domains"].split("; "):
            if d:
                counts[d] += 1

    lines = [
        "# PRISMA Flow Diagram Data\n",
        "## Identification\n",
        f"- Records identified through PubMed: **{total_identified}**",
        f"- Records identified through ACM DL: **{len(acm_results)}**",
        f"- **Total records identified: {total_identified + len(acm_results)}**\n",
        "## Screening\n",
        f"- Duplicate records removed: **0** (single-database batches, no de-dup needed within PubMed)",
        f"- Records with abstracts fetched (PubMed): **{len(records)}**",
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
    lines.append("- The PubMed search was conducted via NCBI Entrez E-utilities (esearch + efetch).")
    lines.append("- ACM DL results were obtained via HTML scraping of the search results page.")
    lines.append("- Domain classification is based on keyword matching in title + abstract text.")
    lines.append("- Papers may appear in multiple domains.")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    log(f"Wrote {filepath}")


def write_top_papers(records: list[dict], filepath: str) -> None:
    lines = ["# Top 5 Most Relevant Papers per Domain\n",
             "Ranked by keyword density (total keyword occurrences in title + abstract).\n"]

    for domain, keywords in DOMAINS.items():
        lines.append(f"## {domain}\n")
        scored = []
        for rec in records:
            if domain in rec["domains"]:
                score = keyword_density(rec["title"], rec["abstract"], keywords)
                scored.append((score, rec))
        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:5]
        if not top:
            lines.append("_No papers matched this domain._\n")
            continue
        for rank, (score, rec) in enumerate(top, 1):
            lines.append(f"### {rank}. {rec['title']}")
            lines.append(f"- **PMID**: {rec['pmid']}")
            lines.append(f"- **Authors**: {rec['authors']}")
            lines.append(f"- **Year**: {rec['year']}")
            lines.append(f"- **Journal**: {rec['journal']}")
            lines.append(f"- **Keyword density**: {score}")
            abs_preview = rec["abstract"][:300]
            if len(rec["abstract"]) > 300:
                abs_preview += "..."
            lines.append(f"- **Abstract excerpt**: {abs_preview}\n")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    log(f"Wrote {filepath}")


def write_search_log(filepath: str) -> None:
    lines = [
        "# Search Log (Reproducibility Record)\n",
        f"**Date**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n",
        "## PubMed Query\n",
        "```",
        PUBMED_QUERY,
        "```\n",
        f"- Endpoint: `{BASE_URL}/esearch.fcgi` + `{BASE_URL}/efetch.fcgi`",
        f"- Parameters: retmax={RETMAX}, rettype=xml, tool={TOOL}, email={EMAIL}\n",
        "## ACM DL Query\n",
        "```",
        PUBMED_QUERY,
        "```\n",
        "- Endpoint: `https://dl.acm.org/action/doSearch`\n",
        "## Execution Log\n",
    ]
    for entry in search_log:
        lines.append(f"- {entry}")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    log(f"Wrote {filepath}")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    log("=== PRISMA Systematic Review Search START ===")
    log(f"Output directory: {OUTPUT_DIR}")

    # ---- PubMed Search ----
    records = []
    total_identified = 0
    try:
        log("--- PubMed ESearch ---")
        pmids = pubmed_esearch(PUBMED_QUERY)
        total_identified = len(pmids)

        if pmids:
            fetch_count = min(len(pmids), 500)  # fetch up to 500
            log(f"--- PubMed EFetch ({fetch_count} records) ---")
            xml_data = pubmed_efetch(pmids[:fetch_count])
            records = parse_pubmed_xml(xml_data)
        else:
            log("No PMIDs returned; skipping EFetch.")
    except Exception as exc:
        log(f"PubMed search FAILED: {exc}")

    # ---- Classify domains ----
    log("--- Domain Classification ---")
    for rec in records:
        doms = classify_domains(rec["title"], rec["abstract"])
        rec["domains"] = "; ".join(doms)
    n_classified = sum(1 for r in records if r["domains"])
    log(f"Papers with >= 1 domain: {n_classified}/{len(records)}")

    # ---- ACM DL Search ----
    log("--- ACM Digital Library Search ---")
    acm_query_short = (
        '("loss aversion" OR "loot box" OR "gacha" OR "hoarding" '
        'OR "completionism" OR "digital possession") AND "video game"'
    )
    acm_results = acm_search(acm_query_short)

    # ---- Write outputs ----
    log("--- Writing output files ---")
    write_pubmed_csv(records, os.path.join(OUTPUT_DIR, "pubmed_results.csv"))
    write_domain_counts(records, os.path.join(OUTPUT_DIR, "domain_counts.md"))
    write_prisma_flow(records, acm_results, total_identified,
                      os.path.join(OUTPUT_DIR, "prisma_flow.md"))
    write_top_papers(records, os.path.join(OUTPUT_DIR, "top_papers_by_domain.md"))

    # Write ACM results as a small supplementary CSV
    if acm_results:
        acm_path = os.path.join(OUTPUT_DIR, "acm_results.csv")
        with open(acm_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["title", "year", "venue"])
            w.writeheader()
            w.writerows(acm_results)
        log(f"Wrote {acm_path} ({len(acm_results)} rows)")

    write_search_log(os.path.join(OUTPUT_DIR, "search_log.md"))
    log("=== PRISMA Systematic Review Search COMPLETE ===")


if __name__ == "__main__":
    main()
