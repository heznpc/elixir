#!/usr/bin/env python3
"""
Eligible-count recount: heuristic 156 vs LLM-majority eligible.

No new API calls — pure re-analysis of the verdicts already captured in the
primary IRR audit (experiments/data/processed/llm_second_reviewer_results.csv,
681 rows = 3 tiers x 227) plus the Opus 4-8 cross-gen run if present.

The paper's headline number is "156 met eligibility criteria" (Include+Maybe
under the rule-based heuristic). This script asks: under an independent
LLM-majority screen of the same 227 records, how many are eligible?

Output:
  experiments/results/eligible_recount_summary.md
"""

from __future__ import annotations

import collections
import csv
import pathlib

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
EXP_DIR    = SCRIPT_DIR.parent
ORIG_CSV   = EXP_DIR / "data" / "processed" / "llm_second_reviewer_results.csv"
O48_CSV    = EXP_DIR / "opus48_crossgen" / "data" / "opus48_results.csv"
OUT_MD     = EXP_DIR / "results" / "eligible_recount_summary.md"

TIERS3 = ["haiku", "sonnet", "opus"]
ELIGIBLE = {"Include", "Maybe"}


def majority(verds):
    verds = [v for v in verds if v]
    if not verds:
        return ""
    c = collections.Counter(verds).most_common()
    if len(c) > 1 and c[0][1] == c[1][1]:
        return ""  # tie / no majority
    return c[0][0]


def main():
    by = collections.defaultdict(dict)
    heur = {}
    for r in csv.DictReader(ORIG_CSV.open()):
        by[r["pmid"]][r["tier"]] = r["llm_verdict"]
        heur[r["pmid"]] = r["heuristic_verdict"]
    o48 = {}
    if O48_CSV.exists():
        for r in csv.DictReader(O48_CSV.open()):
            if r.get("verdict"):
                o48[r["pmid"]] = r["verdict"]

    n = len(by)
    h_elig = sum(1 for p in by if heur[p] in ELIGIBLE)
    h_break = collections.Counter(heur[p] for p in by)

    maj3 = {p: majority([by[p].get(t, "") for t in TIERS3]) for p in by}
    llm3_elig = sum(1 for p in by if maj3[p] in ELIGIBLE)
    ties3 = sum(1 for p in by if not maj3[p])
    maj3_break = collections.Counter(maj3[p] or "(tie)" for p in by)

    unan_elig = sum(1 for p in by if all(by[p].get(t, "") in ELIGIBLE for t in TIERS3))
    any_elig = sum(1 for p in by if any(by[p].get(t, "") in ELIGIBLE for t in TIERS3))

    # 4-model (incl Opus 4-8) if present
    has48 = bool(o48)
    if has48:
        def maj4(p):
            return majority([by[p].get(t, "") for t in TIERS3] + ([o48[p]] if p in o48 else []))
        maj4m = {p: maj4(p) for p in by}
        llm4_elig = sum(1 for p in by if maj4m[p] in ELIGIBLE)
        ties4 = sum(1 for p in by if not maj4m[p])

    # Where does the heuristic->LLM drop come from? cross-tab heuristic vs LLM-majority
    crosstab = collections.Counter((heur[p], maj3[p] or "(tie)") for p in by)

    out = ["# Eligible-Count Recount — heuristic 156 vs LLM-majority",
           "",
           "No new API calls; re-analysis of the primary IRR audit verdicts "
           "(`llm_second_reviewer_results.csv`, 3 tiers x 227).",
           "",
           f"Records: {n}.",
           "",
           "## Eligible counts (Include + Maybe)",
           "",
           "| screener / rule | eligible | % of 227 |",
           "|---|---|---|",
           f"| heuristic (paper headline) | **{h_elig}** | {h_elig/n:.0%} |",
           f"| 3-model LLM majority | **{llm3_elig}** | {llm3_elig/n:.0%} |",
           f"| LLM strict (all 3 eligible) | {unan_elig} | {unan_elig/n:.0%} |",
           f"| LLM lenient (>=1 eligible) | {any_elig} | {any_elig/n:.0%} |"]
    if has48:
        out.append(f"| 4-model majority (incl Opus 4-8) | {llm4_elig} | {llm4_elig/n:.0%} |")
    out += ["",
            f"- Heuristic breakdown: {dict(h_break)}",
            f"- 3-model majority breakdown: {dict(maj3_break)} (ties = {ties3})",
            ""]
    if has48:
        out.append(f"- 4-model majority: {llm4_elig} eligible, ties = {ties4} (more ties — even splits possible with 4 raters)")
        out.append("")

    out += ["## Where the drop comes from (heuristic verdict -> LLM majority)",
            "",
            "| heuristic | LLM-majority | n |",
            "|---|---|---|"]
    for (h, l), c in sorted(crosstab.items(), key=lambda x: -x[1]):
        flag = ""
        if h in ELIGIBLE and l not in ELIGIBLE and l != "(tie)":
            flag = " ← eligibility lost"
        out.append(f"| {h} | {l} | {c}{flag} |")
    out.append("")

    drop = h_elig - llm3_elig
    out += ["## Headline",
            "",
            f"- Under a 3-model LLM-majority screen, **{llm3_elig} of {n}** records are eligible "
            f"vs the heuristic's **{h_elig}** — a drop of **{drop}** ({drop/h_elig:.0%}).",
            "- The drop is concentrated in the heuristic's `Maybe` tier (the LLMs reclassify most "
            "`Maybe` papers as `Exclude`), consistent with the primary audit's dominant disagreement axis.",
            "- **Caveat (load-bearing):** the prompt-robustness experiment "
            "(`experiments/prompt_robustness/`) showed roughly half of these LLM exclusions reverse "
            "under a more lenient prompt framing. The LLM-majority 82 is therefore a strict-prompt "
            "lower bound, not a framing-neutral truth. The framing-neutral eligible count is best "
            f"regarded as lying between {llm3_elig} and {h_elig}; neither endpoint is unambiguously correct.",
            "- This does NOT change the paper's reported 156 (correctly the heuristic result). It "
            "quantifies how sensitive the headline is to the choice of screener.",
            ""]

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(out))
    print(f"[recount] wrote {OUT_MD}")
    print(f"[headline] heuristic={h_elig} llm3_majority={llm3_elig} "
          f"strict={unan_elig} lenient={any_elig} drop={drop}")


if __name__ == "__main__":
    main()
