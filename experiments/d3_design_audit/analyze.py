#!/usr/bin/env python3
"""
Analyze the D3 study-design audit.

Inputs:
  experiments/d3_design_audit/state.jsonl
  experiments/d3_design_audit/data/d3_corpus.csv

Outputs:
  experiments/results/d3_design_audit_summary.md

Reports per protocol §3:
  - 3-LLM verdicts per paper.
  - Majority design verdict per paper.
  - Aggregated counts (LLM majority) vs paper §3.3 claimed counts.
  - Per-category divergence band per pre-registered decision rule.
  - Load-bearing longitudinal-9 check: how many of any-LLM-longitudinal
    papers does each model confirm?
"""

from __future__ import annotations

import csv
import json
import pathlib
from collections import Counter, defaultdict

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
EXP_DIR    = SCRIPT_DIR.parent
STATE      = SCRIPT_DIR / "state.jsonl"
CORPUS     = SCRIPT_DIR / "data" / "d3_corpus.csv"
OUT_MD     = EXP_DIR / "results" / "d3_design_audit_summary.md"

TIERS = ["haiku", "sonnet", "opus"]

# Paper §3.3 claimed counts
PAPER_CLAIMS = {
    "cross_sectional":   43,
    "unspecified":       35,
    "longitudinal":       9,
    "systematic_review":  4,
    "scale_validation":   3,
    "review_commentary":  3,
    "experimental":       2,
    "qualitative":        2,
    "content_analysis":   1,
}
# Total in paper: 102 (43+35+9+4+3+3+2+2+1). Actual corpus: also 102 (per protocol §7 discrepancy).


def majority(verdicts):
    """Plurality verdict; ties returned as ('', 0)."""
    if not verdicts: return "", 0
    c = Counter(verdicts).most_common()
    if len(c) > 1 and c[0][1] == c[1][1]:
        return "", 0
    return c[0][0], c[0][1]


def main():
    if not STATE.exists():
        OUT_MD.parent.mkdir(parents=True, exist_ok=True)
        OUT_MD.write_text("# D3 study-design audit — no results yet\n")
        print("[analyze-d3] no state file")
        return

    # Load cells
    by_paper = defaultdict(dict)
    for line in STATE.read_text().splitlines():
        if not line.strip(): continue
        try: d = json.loads(line)
        except json.JSONDecodeError: continue
        if d.get("_header"): continue
        if d.get("design"):
            by_paper[d["pmid"]][d["tier"]] = (d["design"], d.get("confidence",""), d.get("reason",""))

    # Compute majority per paper
    paper_majority = {}
    n_unanimous = n_majority = n_no_majority = 0
    for pmid, tier_map in by_paper.items():
        designs = [v[0] for v in tier_map.values() if v[0]]
        mv, mc = majority(designs)
        paper_majority[pmid] = mv
        if mc == 3: n_unanimous += 1
        elif mc == 2: n_majority += 1
        else: n_no_majority += 1

    # Aggregated counts by majority verdict
    llm_counts = Counter(v for v in paper_majority.values() if v)
    no_majority_count = sum(1 for v in paper_majority.values() if not v)

    # Per-tier counts (independent of majority)
    per_tier_counts = {t: Counter() for t in TIERS}
    for pmid, tier_map in by_paper.items():
        for t, (d, _, _) in tier_map.items():
            if d:
                per_tier_counts[t][d] += 1

    out = ["# D3 Study-Design Audit — Summary",
           "",
           "Pre-registered protocol: `experiments/d3_design_audit/protocol.md`.",
           "",
           f"Corpus: {len(by_paper)} D3-tagged papers (heuristic Include+Maybe).",
           f"Total LLM calls observed: {sum(len(t) for t in by_paper.values())} (expected {len(by_paper)*len(TIERS)}).",
           "",
           "## Per-paper consensus among the 3 LLMs",
           "",
           f"- Unanimous (3/3 same design): **{n_unanimous}** ({n_unanimous/max(1,len(by_paper)):.0%})",
           f"- Majority (2/3 same):        **{n_majority}** ({n_majority/max(1,len(by_paper)):.0%})",
           f"- No majority (1/1/1):        **{n_no_majority}** ({n_no_majority/max(1,len(by_paper)):.0%})",
           "",
           "## Design-category counts: paper §3.3 vs LLM majority",
           "",
           "| Category | Paper §3.3 | LLM majority | Δ (LLM − paper) | |Δ|/paper | Band |",
           "|---|---|---|---|---|---|"]

    def band(delta, claim):
        if claim == 0:
            return "n/a (paper claim = 0)"
        ratio = abs(delta) / claim
        if ratio < 0.2: return "**survives** (< 20 %)"
        if ratio <= 0.5: return "approximate (20-50 %)"
        return "**revise** (> 50 %)"

    total_paper = total_llm = 0
    for cat in PAPER_CLAIMS:
        p = PAPER_CLAIMS[cat]
        l = llm_counts.get(cat, 0)
        total_paper += p; total_llm += l
        ratio_str = f"{abs(l-p)/p:.0%}" if p else "n/a"
        out.append(f"| {cat} | {p} | {l} | {l-p:+d} | {ratio_str} | {band(l-p, p)} |")
    out.append(f"| **total (categorised)** | {total_paper} | {total_llm} | {total_llm-total_paper:+d} | | |")
    out.append(f"| no-majority papers | — | {no_majority_count} | — | — | descriptive |")
    out.append("")

    # Per-tier per-category breakdown
    out.append("## Per-tier design-count breakdown")
    out.append("")
    out.append("| Category | Haiku | Sonnet | Opus | Paper |")
    out.append("|---|---|---|---|---|")
    for cat in PAPER_CLAIMS:
        out.append(f"| {cat} | {per_tier_counts['haiku'].get(cat,0)} | {per_tier_counts['sonnet'].get(cat,0)} | {per_tier_counts['opus'].get(cat,0)} | {PAPER_CLAIMS[cat]} |")
    out.append("")

    # Load-bearing longitudinal-9 check
    out.append("## Load-bearing check: the longitudinal-9 claim")
    out.append("")
    out.append("Per protocol §3 the longitudinal-9 claim is load-bearing. It stands if at least 6 of the 9 paper-claimed-longitudinal papers are LLM-majority-longitudinal.")
    out.append("")
    # The paper doesn't tell us WHICH 9 are longitudinal. Approximate: take papers any-LLM-classified
    # as longitudinal and check how many LLMs agree per paper.
    any_long = [pmid for pmid, tm in by_paper.items()
                if any(v[0] == "longitudinal" for v in tm.values())]
    out.append(f"- Papers any LLM classified as longitudinal: **{len(any_long)}**")
    out.append(f"- Of these, papers with LLM majority = longitudinal: **{sum(1 for p in any_long if paper_majority.get(p)=='longitudinal')}**")
    out.append(f"- Of these, papers with unanimous LLM = longitudinal: "
               f"**{sum(1 for p in any_long if all(by_paper[p].get(t,('',))[0]=='longitudinal' for t in TIERS))}**")
    out.append("")
    longitudinal_majority_count = llm_counts.get("longitudinal", 0)
    if longitudinal_majority_count >= 6:
        out.append(f"- LLM majority-longitudinal count = {longitudinal_majority_count}. "
                   "**Within reach of the paper's claim of 9.** The specific identity of the 9 cannot be verified from this audit alone (the paper does not pin PMIDs), but the order of magnitude is consistent.")
    else:
        out.append(f"- LLM majority-longitudinal count = {longitudinal_majority_count}. "
                   "**Below the paper's claim of 9.** The §3.3 claim may overcount longitudinal designs from title+abstract alone; revise to '≤ {N}' or add full-text confirmation.".format(N=longitudinal_majority_count))
    out.append("")

    # Cross-tier divergence drilldown for the 'unspecified' category
    if llm_counts.get("unspecified", 0) > 0:
        out.append("## 'Unspecified' category")
        out.append("")
        out.append(f"Paper §3.3 lists {PAPER_CLAIMS['unspecified']} 'unspecified' papers. LLM majority places {llm_counts.get('unspecified',0)} there.")
        if llm_counts.get("unspecified", 0) < PAPER_CLAIMS["unspecified"]:
            diff = PAPER_CLAIMS["unspecified"] - llm_counts.get("unspecified", 0)
            out.append(f"- LLMs assigned {diff} papers to a specific design category that the heuristic could not pin down. "
                       "Re-running this audit at the paper-write step would reduce the unspecified bucket.")
        out.append("")

    # Headline
    out.append("## Headline")
    out.append("")
    revise = []
    approximate = []
    for cat in PAPER_CLAIMS:
        p = PAPER_CLAIMS[cat]; l = llm_counts.get(cat, 0)
        if not p: continue
        r = abs(l-p)/p
        if r > 0.5: revise.append(cat)
        elif r >= 0.2: approximate.append(cat)
    if not revise and not approximate:
        out.append("- All design-category counts survive the LLM re-classification within ±20 %. Paper §3.3 table needs no revision.")
    elif not revise:
        out.append(f"- {len(approximate)} category(ies) need ±range qualifier: {', '.join(approximate)}. "
                   "Paper §3.3 may add a ± range to those counts but the categorical claims stand.")
    else:
        out.append(f"- **{len(revise)} category(ies) fail the 50 % band: {', '.join(revise)}**. "
                   "Paper §3.3 table requires line revision before submission.")
    out.append("")
    out.append("**No psychometric or design-quality claim is made.** The audit checks only whether the heuristic-derived counts in paper §3.3 are robust to an independent LLM re-classification.")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(out))
    print(f"[analyze-d3] wrote {OUT_MD}")


if __name__ == "__main__":
    main()
