#!/usr/bin/env python3
"""
Analyze the self-consistency follow-up run.

Inputs:
  experiments/llm_second_reviewer/sc_state.jsonl
  experiments/llm_second_reviewer/convergent_disagreements.csv
  experiments/data/processed/screening_results.csv          (heuristic verdicts)
  experiments/data/processed/llm_second_reviewer_results.csv (original single-sample LLM verdicts)

Outputs:
  experiments/results/llm_second_reviewer_sc_summary.md

Reports per protocol §6:
  - Per (pmid, tier): n_unique verdicts across 3 samples; majority verdict.
  - Stability rate: fraction of (pmid, tier) with unanimous 3/3 agreement.
  - Comparison: how often does the majority vote match the original single-sample verdict?
  - Per-tier stability + cross-tier consensus on majority verdicts.
  - If stability is high (>=80% unanimous) AND majority matches original, the original
    "convergent disagreement with heuristic" finding is robust to sampling variance.
"""

from __future__ import annotations

import collections
import csv
import json
import pathlib
from collections import Counter, defaultdict

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
EXP_DIR    = SCRIPT_DIR.parent
STATE_JSONL = SCRIPT_DIR / "sc_state.jsonl"
SUB_CSV    = SCRIPT_DIR / "convergent_disagreements.csv"
HEUR_CSV   = EXP_DIR / "data" / "processed" / "screening_results.csv"
ORIG_CSV   = EXP_DIR / "data" / "processed" / "llm_second_reviewer_results.csv"
OUT_MD     = EXP_DIR / "results" / "llm_second_reviewer_sc_summary.md"

LABELS = ["Include", "Maybe", "Exclude"]


def majority_or_none(samples: list[str]) -> tuple[str, int]:
    """Return (majority_label, count). For ties, return ('', 0)."""
    samples = [s for s in samples if s in LABELS]
    if not samples:
        return "", 0
    c = Counter(samples).most_common()
    if len(c) > 1 and c[0][1] == c[1][1]:
        return "", 0
    return c[0][0], c[0][1]


def main():
    if not STATE_JSONL.exists():
        OUT_MD.parent.mkdir(parents=True, exist_ok=True)
        OUT_MD.write_text("# Self-consistency analysis — no state file yet\n")
        print(f"[analyze-sc] no state file; wrote placeholder")
        return

    # Load samples: by_pair[(pmid, tier)] -> list[(sample_idx, verdict, reason)]
    by_pair: dict[tuple[str, str], list] = defaultdict(list)
    n_calls = 0
    n_parse_err = 0
    for line in STATE_JSONL.read_text().splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        if d.get("_header"):
            continue
        n_calls += 1
        if d.get("verdict"):
            by_pair[(d["pmid"], d["tier"])].append((d["sample_idx"], d["verdict"], d.get("reason","")))
        elif d.get("parse_error") or d.get("error"):
            n_parse_err += 1

    # Subset metadata
    sub = {r["pmid"]: r for r in csv.DictReader(SUB_CSV.open())}
    heur = {r["PMID"]: r["Screening_Decision"] for r in csv.DictReader(HEUR_CSV.open())}
    orig = {(r["pmid"], r["tier"]): r["llm_verdict"] for r in csv.DictReader(ORIG_CSV.open())}

    tiers = ["haiku", "sonnet", "opus"]
    out = ["# Self-Consistency Follow-up — Summary",
           "",
           f"Protocol §6 trigger: all three primary-run κ values landed in 0.40 < κ ≤ 0.60.",
           "",
           f"Subset: convergent-disagreement (n = {len(sub)} papers where the 3 LLMs in the primary run agreed with each other but disagreed with the heuristic).",
           "",
           f"Calls observed in state file: {n_calls}  (parse/error: {n_parse_err}).",
           "",
           "## Per-tier stability",
           "",
           "| Tier | n pairs | unanimous 3/3 | majority 2/3 | no majority | mean cost / call |",
           "|---|---|---|---|---|---|",
    ]

    tier_summary = {}
    for tier in tiers:
        pairs = [(pmid, samples) for (pmid, t), samples in by_pair.items() if t == tier]
        unan = maj = none = 0
        majority_verdicts: dict[str, str] = {}
        for pmid, samples in pairs:
            verdicts = [v for _, v, _ in samples]
            mv, mc = majority_or_none(verdicts)
            majority_verdicts[pmid] = mv
            if mc == 3:
                unan += 1
            elif mc == 2:
                maj += 1
            else:
                none += 1
        tier_summary[tier] = {
            "n_pairs": len(pairs),
            "unan": unan, "maj": maj, "none": none,
            "majority_verdicts": majority_verdicts,
        }
        if pairs:
            out.append(f"| {tier} | {len(pairs)} | {unan} ({unan/len(pairs):.0%}) | {maj} ({maj/len(pairs):.0%}) | {none} ({none/len(pairs):.0%}) | — |")
    out.append("")

    # How often does majority verdict match the ORIGINAL single-sample LLM verdict on this paper?
    out.append("## Majority vs original single-sample LLM verdict")
    out.append("")
    out.append("| Tier | n pairs with majority | majority == original | majority != original | original not in 3 samples |")
    out.append("|---|---|---|---|---|")
    for tier in tiers:
        s = tier_summary.get(tier)
        if not s: continue
        n_with_maj = sum(1 for v in s["majority_verdicts"].values() if v)
        match = 0
        diff = 0
        orig_missing = 0
        for pmid, mv in s["majority_verdicts"].items():
            if not mv: continue
            ov = orig.get((pmid, tier), "")
            if not ov:
                continue
            samples = [v for _, v, _ in by_pair[(pmid, tier)] if v]
            if mv == ov:
                match += 1
            else:
                diff += 1
                if ov not in samples:
                    orig_missing += 1
        out.append(f"| {tier} | {n_with_maj} | {match} ({match/max(1,n_with_maj):.0%}) | {diff} | {orig_missing} |")
    out.append("")

    # Cross-tier convergence on MAJORITY verdicts
    out.append("## Cross-tier convergence on majority verdicts")
    out.append("")
    out.append("Restricted to papers where every tier has a defined majority (i.e., no 1-1-1 ties).")
    out.append("")
    cross_rows = []
    eligible_pmids = set()
    for pmid in sub:
        if all(tier_summary.get(t,{}).get("majority_verdicts",{}).get(pmid,"") for t in tiers):
            eligible_pmids.add(pmid)
    for pmid in sorted(eligible_pmids):
        h = heur.get(pmid, "")
        mvs = [tier_summary[t]["majority_verdicts"][pmid] for t in tiers]
        all_same = len(set(mvs)) == 1
        agree_with_h = (mvs[0] == h) if all_same else False
        cross_rows.append({"pmid": pmid, "heur": h, "haiku": mvs[0], "sonnet": mvs[1], "opus": mvs[2],
                           "all_same": all_same, "agree_with_h": agree_with_h})
    n_elig = len(eligible_pmids)
    n_same = sum(1 for r in cross_rows if r["all_same"])
    n_reaffirms_disagreement = sum(1 for r in cross_rows if r["all_same"] and not r["agree_with_h"])
    n_flips_to_h = sum(1 for r in cross_rows if r["all_same"] and r["agree_with_h"])

    if n_elig:
        out.append(f"- Papers with majority across all 3 tiers: **{n_elig}** / {len(sub)}")
        out.append(f"- All 3 tier majorities identical: **{n_same}** ({n_same/n_elig:.0%})")
        out.append(f"  - Reaffirms the original cross-tier disagreement with heuristic: **{n_reaffirms_disagreement}**")
        out.append(f"  - Now agrees with heuristic (original convergence was sampling-lucky): **{n_flips_to_h}**")
        out.append("")
        # Per-axis breakdown for reaffirmed disagreements
        axis = Counter()
        for r in cross_rows:
            if r["all_same"] and not r["agree_with_h"]:
                axis[(r["heur"], r["haiku"])] += 1
        if axis:
            out.append("**Reaffirmed disagreement axes (heuristic → majority LLM consensus):**")
            out.append("")
            for (h,l),n in axis.most_common():
                out.append(f"- {h} → {l}: {n}")
            out.append("")

    # Headline interpretation
    out.append("## Headline interpretation")
    out.append("")
    if n_elig == 0:
        out.append("- Run not yet complete or no eligible majorities; rerun analyze_self_consistency.py later.")
    else:
        reaffirm_rate = n_reaffirms_disagreement / n_elig
        if reaffirm_rate >= 0.75:
            out.append(f"- The convergent-disagreement finding from the primary run is **robust** to sampling variance: "
                       f"{reaffirm_rate:.0%} of eligible papers retain a unanimous 3-tier majority verdict that differs from the heuristic.")
            out.append(f"- This raises the bar for the heuristic on these papers: the LLM consensus is reproducible across both models and sampling.")
        elif reaffirm_rate >= 0.50:
            out.append(f"- The convergent-disagreement finding is **partially robust**: {reaffirm_rate:.0%} of eligible papers retain the disagreement under resampling. The remainder lose either model-wise unanimity or directional consistency.")
        else:
            out.append(f"- The convergent-disagreement finding is **fragile** under resampling: only {reaffirm_rate:.0%} of eligible papers retain a unanimous 3-tier majority that disagrees with the heuristic. Much of the original convergence is attributable to sampling luck rather than a real LLM-vs-heuristic gap on these specific papers.")
    out.append("")
    out.append("**No validity claim is made.** Per protocol §1 and §4, this remains an inter-rater reliability + stability check between automated screeners.")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(out))
    print(f"[analyze-sc] wrote {OUT_MD}")


if __name__ == "__main__":
    main()
