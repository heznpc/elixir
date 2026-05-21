#!/usr/bin/env python3
"""Analyze OpenAlex D1 + D4 recheck (moderate-evidence per-domain corroboration)."""

from __future__ import annotations

import csv
import json
import pathlib
from collections import defaultdict

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
EXP_DIR    = SCRIPT_DIR.parent
NOVEL_CSV  = SCRIPT_DIR / "data" / "novel_records.csv"
LOG_CSV    = SCRIPT_DIR / "data" / "dedup_log.csv"
Q_JSON     = SCRIPT_DIR / "data" / "queries.json"
RECHECK_CSV = SCRIPT_DIR / "data" / "llm_recheck.csv"
OUT_MD     = EXP_DIR / "results" / "openalex_d1_d4_summary.md"

DECISION_RULE = [
    (0, 0,    "Moderate-evidence claim corroborated by broader DB."),
    (1, 3,    "Moderate evidence remains moderate; add to literature pool."),
    (4, 10,   "Evidence rises from moderate to strong-adjacent; revise paragraph."),
    (11, 10**9, "Evidence materially stronger than the primary claim. Major revision."),
]

DOMAINS = ["D1", "D4"]
TIERS   = ["haiku", "sonnet", "opus"]


def band(n: int) -> str:
    for lo, hi, label in DECISION_RULE:
        if lo <= n <= hi:
            return label
    return "?"


def main():
    novel_rows = []
    if NOVEL_CSV.exists() and NOVEL_CSV.stat().st_size:
        novel_rows = list(csv.DictReader(NOVEL_CSV.open()))
    log_rows = list(csv.DictReader(LOG_CSV.open())) if LOG_CSV.exists() else []
    q_meta   = json.loads(Q_JSON.read_text()) if Q_JSON.exists() else {}

    # Heuristic verdict distribution by domain
    by_dom = defaultdict(lambda: {"Include": [], "Maybe": [], "Exclude": []})
    for r in novel_rows:
        d = r.get("domain_query", "")
        v = r.get("screening_verdict", "")
        if d in DOMAINS and v in by_dom[d]:
            by_dom[d][v].append(r)

    # LLM recheck verdicts by openalex_id
    llm_verdicts: dict[str, dict[str, str]] = {}
    if RECHECK_CSV.exists() and RECHECK_CSV.stat().st_size:
        for r in csv.DictReader(RECHECK_CSV.open()):
            llm_verdicts.setdefault(r["openalex_id"], {})[r["tier"]] = r["verdict"]

    n_pmid = sum(1 for r in log_rows if r.get("dedup_reason") == "pmid_match")
    n_doi  = sum(1 for r in log_rows if r.get("dedup_reason") == "doi_match")
    n_tjac = sum(1 for r in log_rows if (r.get("dedup_reason") or "").startswith("title_jaccard"))

    out = ["# OpenAlex D1 + D4 Recheck — Summary",
           "",
           "Pre-registered protocol: `experiments/openalex_d1_d4/protocol.md`.",
           ""]
    if q_meta:
        out.append(f"OpenAlex hits (pre-dedup): D1 = {q_meta.get('counts',{}).get('D1','?')}, D4 = {q_meta.get('counts',{}).get('D4','?')}.")
        out.append(f"Queries hash: `{q_meta.get('queries_hash','?')[:16]}`.")
    out.append("")
    out.append(f"Duplicates removed: pmid={n_pmid}, doi={n_doi}, title-jaccard={n_tjac}.")
    out.append("")

    # Per-domain pipeline
    for dom in DOMAINS:
        out.append(f"## Domain {dom}")
        out.append("")
        inc = by_dom[dom]["Include"]
        may = by_dom[dom]["Maybe"]
        exc = by_dom[dom]["Exclude"]
        out.append(f"- Heuristic Include: **{len(inc)}**, Maybe: {len(may)}, Exclude: {len(exc)}.")
        out.append("")

        if inc:
            out.append("**Heuristic-Include records:**")
            out.append("")
            for r in inc:
                out.append(f"- **{r.get('title','')[:140]}** ({r.get('year','?')}, *{r.get('journal','')}*)")
                out.append(f"  - OpenAlex: {r.get('openalex_id','')}; PMID: {r.get('pmid','') or 'n/a'}; DOI: {r.get('doi','') or 'n/a'}")
                out.append(f"  - Heuristic reason: {r.get('screening_reason','')}")
            out.append("")

        # LLM recheck table if present
        if inc and llm_verdicts:
            out.append("**LLM recheck verdicts (3 Claude models):**")
            out.append("")
            out.append("| OpenAlex ID | Title (first 90c) | Haiku | Sonnet | Opus | Consensus |")
            out.append("|---|---|---|---|---|---|")
            n_unan_inc = 0
            for r in inc:
                v = llm_verdicts.get(r["openalex_id"], {})
                h = v.get("haiku","?"); s = v.get("sonnet","?"); o = v.get("opus","?")
                triplet = [h, s, o]
                if all(x == "Include" for x in triplet):
                    consensus = "**Include** (unanimous)"
                    n_unan_inc += 1
                elif all(x == triplet[0] for x in triplet):
                    consensus = f"**{triplet[0]}** (unanimous)"
                else:
                    consensus = "split"
                out.append(f"| {r['openalex_id']} | {r.get('title','')[:90]} | {h} | {s} | {o} | {consensus} |")
            out.append("")
            out.append(f"- LLM-confirmed-Include (unanimous): **{n_unan_inc}** → band: {band(n_unan_inc)}")
        out.append("")

    # Headline
    out.append("## Headline")
    out.append("")
    for dom in DOMAINS:
        inc = by_dom[dom]["Include"]
        n_unan_inc = 0
        for r in inc:
            v = llm_verdicts.get(r["openalex_id"], {})
            if all(v.get(t) == "Include" for t in TIERS):
                n_unan_inc += 1
        section_ref = "3.1" if dom == "D1" else "3.4"
        if n_unan_inc == 0:
            out.append(f"- **{dom}**: paper §{section_ref} moderate-evidence claim corroborated. No unanimous-Include novel records.")
        elif n_unan_inc <= 3:
            out.append(f"- **{dom}**: moderate evidence remains moderate; {n_unan_inc} novel record(s) to add. §{section_ref} narrative unchanged.")
        elif n_unan_inc <= 10:
            out.append(f"- **{dom}**: evidence rises to strong-adjacent ({n_unan_inc} novel). §{section_ref} requires revision.")
        else:
            out.append(f"- **{dom}**: evidence materially stronger ({n_unan_inc} novel). §{section_ref} major revision.")
    out.append("")
    out.append("**Coverage caveat.** OpenAlex coverage of HCI, game-studies, and Japanese-language non-Crossref-registered work remains incomplete. Corroboration is one-sided.")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(out))
    print(f"[analyze-d1d4] wrote {OUT_MD}")


if __name__ == "__main__":
    main()
