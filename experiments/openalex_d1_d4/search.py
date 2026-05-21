#!/usr/bin/env python3
"""
OpenAlex search for the D2/D6 evidence-void recheck.

Pre-registered: experiments/openalex_extension/protocol.md.
Stdlib only (urllib, json, csv). No API key required.

Outputs:
  experiments/openalex_extension/data/openalex_results.csv
  experiments/openalex_extension/data/queries.json     (frozen queries + hashes)
"""
from __future__ import annotations

import csv
import hashlib
import json
import pathlib
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
DATA_DIR   = SCRIPT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
OUT_CSV    = DATA_DIR / "openalex_results.csv"
Q_JSON     = DATA_DIR / "queries.json"

OPENALEX_BASE = "https://api.openalex.org/works"
POLITE_EMAIL  = "heznpc@gmail.com"
PER_PAGE      = 25
MAX_PER_QUERY = 200

QUERIES = {
    "D1": {
        "search": ('"loss aversion" OR "endowment effect" OR "sunk cost" OR '
                   '"prospect theory" OR "status quo bias" OR "framing effect"'),
        "filter": ('abstract.search:'
                   '"video game" OR "video games" OR "gaming" OR "gamer" OR '
                   '"rpg" OR "mmorpg" OR "online game" OR "gameplay" OR "in-game"'),
    },
    "D4": {
        "search": ('"inventory" OR "virtual item" OR "virtual good" OR '
                   '"psychological ownership" OR "virtual ownership" OR '
                   '"digital possession" OR "virtual possession" OR "extended self"'),
        "filter": ('abstract.search:'
                   '"video game" OR "video games" OR "gaming" OR "gamer" OR '
                   '"rpg" OR "mmorpg" OR "online game" OR "in-game"'),
    },
}


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def fetch_page(domain: str, query: dict, page: int) -> dict:
    """Single page of OpenAlex results."""
    params = {
        "search": query["search"],
        "filter": query["filter"],
        "per-page": str(PER_PAGE),
        "page": str(page),
        "mailto": POLITE_EMAIL,
    }
    url = OPENALEX_BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": f"heznpc-elixir/0.1 ({POLITE_EMAIL})"})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return json.loads(r.read())


def extract_abstract(inv_idx: dict | None) -> str:
    """OpenAlex provides abstract_inverted_index; reconstruct flat text."""
    if not inv_idx:
        return ""
    # inv_idx is {word: [positions...]} — invert to ordered list
    flat = {}
    for word, positions in inv_idx.items():
        for p in positions:
            flat[p] = word
    return " ".join(flat[k] for k in sorted(flat.keys()))


def extract_record(rec: dict) -> dict:
    title = rec.get("title") or ""
    abstract = extract_abstract(rec.get("abstract_inverted_index"))
    ids = rec.get("ids") or {}
    pmid = ""
    if ids.get("pmid"):
        # pmid stored as URL like https://pubmed.ncbi.nlm.nih.gov/12345/
        m = ids["pmid"].rstrip("/").split("/")[-1]
        pmid = m if m.isdigit() else ""
    doi = (ids.get("doi") or "").lower().replace("https://doi.org/", "")
    loc = rec.get("primary_location") or {}
    src = loc.get("source") or {}
    journal = src.get("display_name", "") if isinstance(src, dict) else ""
    return {
        "openalex_id": (rec.get("id", "") or "").split("/")[-1],
        "pmid": pmid,
        "doi": doi,
        "title": title,
        "abstract": abstract,
        "year": str(rec.get("publication_year") or ""),
        "journal": journal,
        "authors": "; ".join((a.get("author") or {}).get("display_name","")
                              for a in (rec.get("authorships") or [])[:5]),
        "type": rec.get("type", "") or "",
        "cited_by_count": rec.get("cited_by_count", 0),
    }


def main():
    rows = []
    counts = {}
    for domain, q in QUERIES.items():
        seen = 0
        page = 1
        while seen < MAX_PER_QUERY:
            try:
                data = fetch_page(domain, q, page)
            except urllib.error.HTTPError as e:
                print(f"[err] {domain} page {page}: HTTP {e.code} {e.read()[:200]!r}")
                break
            except Exception as e:
                print(f"[err] {domain} page {page}: {type(e).__name__}: {e}")
                break
            results = data.get("results", [])
            if not results:
                break
            for rec in results:
                row = extract_record(rec)
                row["domain_query"] = domain
                rows.append(row)
                seen += 1
                if seen >= MAX_PER_QUERY:
                    break
            print(f"  {domain} page {page} -> {len(results)} records (cumulative {seen})")
            if len(results) < PER_PAGE:
                break
            page += 1
            time.sleep(0.15)  # polite throttle
        counts[domain] = seen

    # Write CSV
    fields = ["openalex_id","pmid","doi","title","abstract","year","journal","authors","type","cited_by_count","domain_query"]
    with OUT_CSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow(row)

    # Write query freeze + hashes
    Q_JSON.write_text(json.dumps({
        "queries": QUERIES,
        "queries_hash": sha256(json.dumps(QUERIES, sort_keys=True)),
        "counts": counts,
        "total_rows": len(rows),
        "per_page": PER_PAGE,
        "max_per_query": MAX_PER_QUERY,
    }, indent=2))

    print(f"[done] wrote {OUT_CSV} ({len(rows)} rows). counts={counts}")


if __name__ == "__main__":
    main()
