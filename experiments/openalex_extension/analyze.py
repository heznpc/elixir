#!/usr/bin/env python3
"""
Analyze OpenAlex extension results vs the pre-registered D2/D6 decision rule.

Inputs:
  experiments/openalex_extension/data/novel_records.csv
  experiments/openalex_extension/data/dedup_log.csv
  experiments/openalex_extension/data/queries.json

Outputs:
  experiments/results/openalex_extension_summary.md
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
OUT_MD     = EXP_DIR / "results" / "openalex_extension_summary.md"

DECISION_RULE = [
    (0, 0,    "OpenAlex extension corroborates the evidence-void claim. The void survives a broader-database check."),
    (1, 2,    "Evidence sparse but not absent. The void claim is downgraded to 'extremely thin literature.'"),
    (3, 9,    "Evidence is sparse but the void claim is not supported."),
    (10, 10**9, "The evidence-void claim is FALSIFIED for this domain. Paper §3 narrative must be revised."),
]


def main():
    novel_rows = []
    if NOVEL_CSV.exists() and NOVEL_CSV.stat().st_size:
        novel_rows = list(csv.DictReader(NOVEL_CSV.open()))
    log_rows = list(csv.DictReader(LOG_CSV.open())) if LOG_CSV.exists() else []
    q_meta = json.loads(Q_JSON.read_text()) if Q_JSON.exists() else {}

    # Per-domain breakdown
    by_domain_total = defaultdict(int)
    by_domain_include = defaultdict(int)
    by_domain_maybe = defaultdict(int)
    by_domain_exclude = defaultdict(int)
    for r in novel_rows:
        d = r.get("domain_query","")
        by_domain_total[d] += 1
        v = r.get("screening_verdict","")
        if v == "Include": by_domain_include[d] += 1
        elif v == "Maybe": by_domain_maybe[d] += 1
        elif v == "Exclude": by_domain_exclude[d] += 1

    n_pmid_dup = sum(1 for r in log_rows if r["dedup_reason"]=="pmid_match")
    n_doi_dup  = sum(1 for r in log_rows if r["dedup_reason"]=="doi_match")
    n_title_dup = sum(1 for r in log_rows if r["dedup_reason"].startswith("title_jaccard"))

    out = ["# OpenAlex Extension — Summary",
           "",
           "Pre-registered protocol: `experiments/openalex_extension/protocol.md`.",
           ""]
    if q_meta:
        out.append(f"OpenAlex hits (pre-dedup): D2 = {q_meta.get('counts',{}).get('D2','?')}, D6 = {q_meta.get('counts',{}).get('D6','?')}.")
        out.append(f"Queries hash: `{q_meta.get('queries_hash','?')[:16]}`.")
    out.append("")
    out.append(f"Duplicates removed: pmid={n_pmid_dup} | doi={n_doi_dup} | title jaccard≥0.85={n_title_dup}.")
    out.append("")
    out.append(f"Novel records (surviving dedup): **{len(novel_rows)}**.")
    out.append("")
    out.append("## Per-domain decision-rule outcome")
    out.append("")
    out.append("| Domain | Novel total | Heuristic Include | Heuristic Maybe | Heuristic Exclude | Decision-rule outcome |")
    out.append("|---|---|---|---|---|---|")
    for d in ["D2","D6"]:
        n_inc = by_domain_include[d]
        n_may = by_domain_maybe[d]
        n_exc = by_domain_exclude[d]
        n_tot = by_domain_total[d]
        rule = next((v for lo, hi, v in DECISION_RULE if lo <= n_inc <= hi), "?")
        out.append(f"| {d} | {n_tot} | **{n_inc}** | {n_may} | {n_exc} | {rule} |")
    out.append("")

    # Verbose listing of Include hits per domain (the load-bearing evidence)
    out.append("## Heuristic-Include novel records (load-bearing for decision rule)")
    out.append("")
    found_any = False
    for d in ["D2","D6"]:
        rows = [r for r in novel_rows if r.get("domain_query")==d and r.get("screening_verdict")=="Include"]
        if not rows:
            out.append(f"### {d}: none (void corroborated by Include subset)")
            out.append("")
            continue
        found_any = True
        out.append(f"### {d}: {len(rows)} record(s)")
        out.append("")
        for r in rows[:15]:
            out.append(f"- **{r.get('title','')[:140]}** ({r.get('year','?')}, *{r.get('journal','')}*)")
            out.append(f"  - OpenAlex ID: {r.get('openalex_id','')}; PMID: {r.get('pmid','') or 'n/a'}; DOI: {r.get('doi','') or 'n/a'}")
            out.append(f"  - Heuristic reason: {r.get('screening_reason','')}")
        out.append("")

    # LLM recheck integration (protocol §6 follow-up)
    llm_verdicts: dict[str, dict[str, str]] = {}  # openalex_id -> {tier: verdict}
    if RECHECK_CSV.exists() and RECHECK_CSV.stat().st_size:
        for r in csv.DictReader(RECHECK_CSV.open()):
            llm_verdicts.setdefault(r["openalex_id"], {})[r["tier"]] = r["verdict"]
    if llm_verdicts:
        out.append("## LLM recheck on Heuristic-Include records (protocol §6)")
        out.append("")
        out.append("Three Claude models (Opus 4-7, Sonnet 4-6, Haiku 4-5) re-screened each Heuristic-Include record with the same criteria the LLM-second-reviewer audit used. Verdicts:")
        out.append("")
        out.append("| OpenAlex ID | Domain | Title (first 100c) | Haiku | Sonnet | Opus | LLM consensus |")
        out.append("|---|---|---|---|---|---|---|")
        llm_inc_count = {"D2":0, "D6":0}
        for r in novel_rows:
            if r["screening_verdict"] != "Include":
                continue
            v = llm_verdicts.get(r["openalex_id"], {})
            h = v.get("haiku","?"); s = v.get("sonnet","?"); o = v.get("opus","?")
            verdicts = [vv for vv in (h,s,o) if vv]
            if verdicts and all(x == verdicts[0] for x in verdicts):
                consensus = f"**{verdicts[0]}** (unanimous)"
            else:
                consensus = "split"
            if all(x == "Include" for x in (h,s,o)):
                llm_inc_count[r["domain_query"]] += 1
            out.append(f"| {r['openalex_id']} | {r['domain_query']} | {r['title'][:100]} | {h} | {s} | {o} | {consensus} |")
        out.append("")
        out.append(f"**LLM-Include after recheck:** D2 = **{llm_inc_count['D2']}**, D6 = **{llm_inc_count['D6']}** (unanimous Include across all 3 tiers).")
        out.append("")

    out.append("## Headline")
    out.append("")
    d2_inc = by_domain_include["D2"]
    d6_inc = by_domain_include["D6"]

    def band(n):
        for lo, hi, label in DECISION_RULE:
            if lo <= n <= hi:
                return label
        return "?"

    out.append(f"- D2 Heuristic-Include = **{d2_inc}** → {band(d2_inc)}")
    out.append(f"- D6 Heuristic-Include = **{d6_inc}** → {band(d6_inc)}")
    out.append("")
    if d2_inc == 0 and d6_inc == 0:
        out.append("- **Both D2 and D6 evidence-void claims corroborated by OpenAlex extension.** No novel Heuristic-Include records survived dedup + screening on either domain.")
        out.append("- The paper §3.2 (D2) and §3.7 (D6) narratives may stand as written; the OpenAlex check is added as a supplementary footnote.")
    elif max(d2_inc, d6_inc) >= 10:
        out.append(f"- **Per-domain evidence-void claim falsified for at least one domain** (D2 = {d2_inc}, D6 = {d6_inc}). Paper §3 narrative must be revised. See novel-records listing above.")
    else:
        out.append(f"- **Heuristic Includes are non-zero but neither domain reaches the falsify threshold (10).** Per-domain decision rules apply; see table above for the exact band per domain.")
        out.append("- Important caveat from the parallel LLM-second-reviewer audit: the heuristic systematically over-includes commentary, off-topic, and non-empirical papers (PR #5 result). The heuristic-Include count is therefore an upper bound on the actual evidence count.")
        if llm_verdicts:
            llm_d2 = sum(1 for r in novel_rows if r["screening_verdict"]=="Include" and r["domain_query"]=="D2"
                          and all(llm_verdicts.get(r["openalex_id"], {}).get(t)=="Include" for t in ["haiku","sonnet","opus"]))
            llm_d6 = sum(1 for r in novel_rows if r["screening_verdict"]=="Include" and r["domain_query"]=="D6"
                          and all(llm_verdicts.get(r["openalex_id"], {}).get(t)=="Include" for t in ["haiku","sonnet","opus"]))
            out.append(f"- **LLM recheck conclusion (load-bearing per protocol §6):** unanimous-Include after 3-model re-screening: D2 = **{llm_d2}**, D6 = **{llm_d6}**.")
            if llm_d2 == 0 and llm_d6 == 0:
                out.append("- Therefore **both D2 and D6 evidence-void claims are corroborated** when the heuristic's known over-inclusion bias is corrected via LLM re-screening. Paper §3.2 / §3.7 may stand. The OpenAlex extension is reported with this caveat and the LLM recheck as supplementary evidence.")
            else:
                out.append("- The LLM-recheck still surfaces evidence; paper §3 narrative requires revision for the affected domain.")
        else:
            out.append("- LLM recheck output not present yet; conclusion deferred until `experiments/openalex_extension/llm_recheck.py` completes.")
    out.append("")
    out.append("**Coverage caveat.** OpenAlex coverage of practitioner blogs (Bycer, Game Wisdom), TV Tropes / Pixiv Dictionary, and Japanese-language non-Crossref-registered work remains incomplete. Absence of OpenAlex hits is therefore consistent with both 'no evidence' and 'evidence exists in venues OpenAlex does not index well.' The extension is one-sided per protocol §1.")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(out))
    print(f"[analyze-c4] wrote {OUT_MD}")


if __name__ == "__main__":
    main()
