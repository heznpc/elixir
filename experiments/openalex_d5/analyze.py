#!/usr/bin/env python3
"""
Analyze OpenAlex D5 (completionism) recheck.

Pre-registered: experiments/openalex_d5/protocol.md.

Reports:
  - OpenAlex hits, dedup yield, heuristic verdict distribution on novel records.
  - Heuristic-Include records listed with title/journal/year/heuristic reason.
  - LLM recheck verdicts (if data present), with per-record 3-LLM consensus.
  - Decision-rule outcome per protocol §2.

Inputs:
  experiments/openalex_d5/data/novel_records.csv
  experiments/openalex_d5/data/dedup_log.csv
  experiments/openalex_d5/data/queries.json
  experiments/openalex_d5/data/llm_recheck.csv  (optional)

Outputs:
  experiments/results/openalex_d5_summary.md
"""

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
OUT_MD     = EXP_DIR / "results" / "openalex_d5_summary.md"

DECISION_RULE = [
    (0, 0,    "Weak-evidence claim corroborated by broader DB."),
    (1, 2,    "Weak evidence remains weak; add records to literature pool."),
    (3, 9,    "Evidence rises from weak to moderate; revise paper §3.6 narrative."),
    (10, 10**9, "Evidence materially stronger than §3.6 claim. Major revision."),
]


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
    q_meta = json.loads(Q_JSON.read_text()) if Q_JSON.exists() else {}

    n_pmid_dup = sum(1 for r in log_rows if r.get("dedup_reason") == "pmid_match")
    n_doi_dup  = sum(1 for r in log_rows if r.get("dedup_reason") == "doi_match")
    n_title_dup = sum(1 for r in log_rows if (r.get("dedup_reason") or "").startswith("title_jaccard"))

    heur_inc = [r for r in novel_rows if r.get("screening_verdict") == "Include"]
    heur_may = [r for r in novel_rows if r.get("screening_verdict") == "Maybe"]
    heur_exc = [r for r in novel_rows if r.get("screening_verdict") == "Exclude"]

    out = ["# OpenAlex D5 Recheck — Summary",
           "",
           "Pre-registered protocol: `experiments/openalex_d5/protocol.md`.",
           ""]
    if q_meta:
        out.append(f"OpenAlex hits (pre-dedup): D5 = {q_meta.get('counts', {}).get('D5', '?')}.")
        out.append(f"Queries hash: `{q_meta.get('queries_hash', '?')[:16]}`.")
    out.append("")
    out.append(f"Duplicates removed: pmid={n_pmid_dup}, doi={n_doi_dup}, title-jaccard={n_title_dup}.")
    out.append("")
    out.append(f"Novel records (surviving dedup): **{len(novel_rows)}**.")
    out.append("")
    out.append("## Heuristic verdict distribution on novel records")
    out.append("")
    out.append(f"- **Include**: {len(heur_inc)}")
    out.append(f"- Maybe: {len(heur_may)}")
    out.append(f"- Exclude: {len(heur_exc)}")
    out.append("")

    # Listing Heuristic-Include
    if heur_inc:
        out.append("## Heuristic-Include records (candidate D5 additions)")
        out.append("")
        for r in heur_inc:
            out.append(f"- **{r.get('title','')[:140]}** ({r.get('year','?')}, *{r.get('journal','')}*)")
            out.append(f"  - OpenAlex: {r.get('openalex_id','')}; PMID: {r.get('pmid','') or 'n/a'}; DOI: {r.get('doi','') or 'n/a'}")
            out.append(f"  - Heuristic reason: {r.get('screening_reason','')}")
        out.append("")

    # LLM recheck integration
    llm_verdicts: dict[str, dict[str, str]] = {}
    if RECHECK_CSV.exists() and RECHECK_CSV.stat().st_size:
        for r in csv.DictReader(RECHECK_CSV.open()):
            llm_verdicts.setdefault(r["openalex_id"], {})[r["tier"]] = r["verdict"]
    llm_inc_count = 0
    if llm_verdicts:
        out.append("## LLM recheck on Heuristic-Include records (protocol §5)")
        out.append("")
        out.append("Three Claude models (Opus 4-7, Sonnet 4-6, Haiku 4-5) re-screened each Heuristic-Include record with the same criteria the LLM-second-reviewer audit used.")
        out.append("")
        out.append("| OpenAlex ID | Title (first 90c) | Haiku | Sonnet | Opus | Consensus |")
        out.append("|---|---|---|---|---|---|")
        for r in heur_inc:
            v = llm_verdicts.get(r["openalex_id"], {})
            h = v.get("haiku", "?"); s = v.get("sonnet", "?"); o = v.get("opus", "?")
            triplet = [h, s, o]
            if all(x == "Include" for x in triplet):
                consensus = "**Include** (unanimous)"
                llm_inc_count += 1
            elif all(x == triplet[0] for x in triplet):
                consensus = f"**{triplet[0]}** (unanimous)"
            else:
                consensus = "split"
            out.append(f"| {r['openalex_id']} | {r.get('title','')[:90]} | {h} | {s} | {o} | {consensus} |")
        out.append("")
        out.append(f"**LLM-confirmed-Include (unanimous across 3 tiers): {llm_inc_count}.**")
        out.append("")

    # Headline
    out.append("## Headline")
    out.append("")
    out.append(f"- Heuristic-Include count = {len(heur_inc)} → band: {band(len(heur_inc))}")
    if llm_verdicts:
        out.append(f"- LLM-confirmed-Include count = **{llm_inc_count}** (load-bearing per protocol §2)")
        out.append(f"- LLM band: {band(llm_inc_count)}")
        if llm_inc_count == 0:
            out.append("- **D5 weak-evidence claim corroborated.** No novel D5 papers survive both heuristic and LLM re-screening. Paper §3.6 stands; OpenAlex check added as supplementary footnote.")
        elif llm_inc_count <= 2:
            out.append(f"- Weak evidence remains weak; the {llm_inc_count} novel record(s) can be added to the literature pool but do not shift §3.6's verdict.")
        elif llm_inc_count <= 9:
            out.append(f"- Evidence rises from weak to moderate; paper §3.6 narrative requires revision. {llm_inc_count} novel records identified.")
        else:
            out.append(f"- Evidence is materially stronger than §3.6's weak-evidence claim. Major §3.6 revision required.")
    else:
        out.append("- LLM recheck pending. Will re-run analyzer after `llm_recheck.py` completes.")
    out.append("")
    out.append("**Coverage caveat.** OpenAlex coverage of HCI (CHI, CHI PLAY), game-studies, and grey-literature completionism discussions remains incomplete. The check is corroborative-only when the result is '0 novel'.")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(out))
    print(f"[analyze-d5] wrote {OUT_MD}")


if __name__ == "__main__":
    main()
