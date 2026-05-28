#!/usr/bin/env python3
"""
Dedup OpenAlex hits against the PubMed corpus and apply heuristic screening.

Pre-registered: experiments/openalex_extension/protocol.md §4-5.

Inputs:
  experiments/openalex_extension/data/openalex_results.csv
  experiments/data/raw/pubmed_results.csv

Outputs:
  experiments/openalex_extension/data/novel_records.csv
  experiments/openalex_extension/data/dedup_log.csv

Reuses experiments/src/screening.py's classify_paper for heuristic verdicts.
"""

from __future__ import annotations

import csv
import pathlib
import re
import sys

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
EXP_DIR    = SCRIPT_DIR.parent
OA_CSV     = SCRIPT_DIR / "data" / "openalex_results.csv"
PUBMED_CSV = EXP_DIR / "data" / "raw" / "pubmed_results.csv"
NOVEL_CSV  = SCRIPT_DIR / "data" / "novel_records.csv"
LOG_CSV    = SCRIPT_DIR / "data" / "dedup_log.csv"

# Path-anchored import — unaffected by cwd or stray sys.path entries.
sys.path.insert(0, str(EXP_DIR))
from _lib.import_screening import get_classify_paper  # type: ignore
classify_paper = get_classify_paper()


def norm_doi(s: str) -> str:
    return (s or "").lower().replace("https://doi.org/", "").strip().strip("/")


_WORD = re.compile(r"[a-z0-9]+")
def title_tokens(s: str) -> set[str]:
    return set(_WORD.findall((s or "").lower()))


def jaccard(a: set, b: set) -> float:
    if not a or not b: return 0.0
    return len(a & b) / len(a | b)


def main():
    pubmed = list(csv.DictReader(PUBMED_CSV.open()))
    pubmed_pmids = {r["pmid"].strip() for r in pubmed if r.get("pmid")}
    pubmed_dois  = {norm_doi(r.get("doi","")) for r in pubmed if r.get("doi","").strip()}
    pubmed_titles = [(title_tokens(r["title"]), r["pmid"], r["title"]) for r in pubmed]
    # Note: PubMed CSV may not have a doi column. Check column names.
    has_doi_col = "doi" in (pubmed[0].keys() if pubmed else set())
    if not has_doi_col:
        pubmed_dois = set()

    oa_rows = list(csv.DictReader(OA_CSV.open()))
    novel = []
    log_rows = []
    n_dupe_pmid = n_dupe_doi = n_dupe_title = 0

    for row in oa_rows:
        oa_pmid = row.get("pmid", "").strip()
        oa_doi  = norm_doi(row.get("doi", ""))
        oa_title_toks = title_tokens(row.get("title", ""))

        reason = None
        match_pmid = ""
        if oa_pmid and oa_pmid in pubmed_pmids:
            reason = "pmid_match"; n_dupe_pmid += 1; match_pmid = oa_pmid
        elif oa_doi and oa_doi in pubmed_dois:
            reason = "doi_match"; n_dupe_doi += 1
        else:
            # title token jaccard soft match
            best_j = 0.0
            best_pmid = ""
            best_title = ""
            for ptok, ppmid, ptitle in pubmed_titles:
                j = jaccard(oa_title_toks, ptok)
                if j > best_j:
                    best_j = j; best_pmid = ppmid; best_title = ptitle
            if best_j >= 0.85:
                reason = f"title_jaccard={best_j:.2f}"
                n_dupe_title += 1
                match_pmid = best_pmid

        log_rows.append({
            "openalex_id": row.get("openalex_id",""),
            "title": row.get("title","")[:120],
            "dedup_reason": reason or "novel",
            "match_pmid": match_pmid,
        })
        if reason:
            continue

        # Heuristic screening
        screen_row = {"title": row.get("title",""), "abstract": row.get("abstract","")}
        verdict, why, domains, score = classify_paper(screen_row)
        novel.append({
            **row,
            "screening_verdict": verdict,
            "screening_reason": why,
            "screening_domains": "; ".join(domains),
            "screening_score": score,
        })

    NOVEL_CSV.parent.mkdir(parents=True, exist_ok=True)
    if novel:
        with NOVEL_CSV.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(novel[0].keys()))
            w.writeheader()
            for r in novel:
                w.writerow(r)
    else:
        NOVEL_CSV.write_text("")

    with LOG_CSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["openalex_id","title","dedup_reason","match_pmid"])
        w.writeheader()
        for r in log_rows:
            w.writerow(r)

    # Distribution per domain
    by_domain = {}
    for r in novel:
        d = r["domain_query"]
        by_domain.setdefault(d, {"Include":0,"Maybe":0,"Exclude":0})
        by_domain[d][r["screening_verdict"]] += 1

    print(f"[dedup] openalex_total={len(oa_rows)}")
    print(f"[dedup] duplicates: pmid={n_dupe_pmid} doi={n_dupe_doi} title_jaccard={n_dupe_title}")
    print(f"[dedup] novel={len(novel)}")
    print(f"[dedup] novel distribution by query domain:")
    for d, counts in by_domain.items():
        print(f"  {d}: {counts}")


if __name__ == "__main__":
    main()
