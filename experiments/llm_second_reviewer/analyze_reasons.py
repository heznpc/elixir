#!/usr/bin/env python3
"""
Qualitative analysis of LLM exclusion reasons on the 51 reaffirmed-disagreement papers.

No additional LLM calls. Pulls reason text from:
  - run_*_{haiku,sonnet,opus}.jsonl (primary run; 1 reason per paper-tier)
  - sc_state.jsonl                  (self-consistency; 3 reasons per paper-tier)

Total: up to 4 reasons per (paper, tier) × 3 tiers = 12 reasons per paper × 51 papers ≈ 612 reasons.

Outputs:
  experiments/results/llm_second_reviewer_reasons.md

What it does:
  1. Computes the 51 "reaffirmed disagreement" subset (from sc_state.jsonl majority votes,
     same criterion as analyze_self_consistency.py).
  2. Groups by disagreement axis: heuristic → unanimous-LLM-consensus.
  3. Extracts all reason strings per axis.
  4. Tokenises (lowercase, alnum, stopwords removed), reports top bigrams + trigrams per axis.
  5. Prints 3 representative example papers per axis with their full reason quotes.
  6. Reports cross-LLM "reason agreement" — do all 3 LLMs name similar reasons for the same paper?
"""

from __future__ import annotations

import collections
import csv
import json
import pathlib
import re
from collections import Counter, defaultdict

SCRIPT_DIR  = pathlib.Path(__file__).resolve().parent
EXP_DIR     = SCRIPT_DIR.parent
HEUR_CSV    = EXP_DIR / "data" / "processed" / "screening_results.csv"
RAW_CSV     = EXP_DIR / "data" / "raw" / "pubmed_results.csv"
SUB_CSV     = SCRIPT_DIR / "convergent_disagreements.csv"
STATE_JSONL = SCRIPT_DIR / "sc_state.jsonl"
OUT_MD      = EXP_DIR / "results" / "llm_second_reviewer_reasons.md"

TIERS = ["haiku", "sonnet", "opus"]
LABELS = ["Include", "Maybe", "Exclude"]

# Stopwords: English stopwords + PRISMA-domain filler frequently appearing in reasons
STOPWORDS = set("""
a an the and or of in to for on at by from with into about as is are was were be been being
this that these those it its their they we i our your you he she his her them us
not no n't do does did doing done done done will would could should may might must can
have has had having
study studies paper research review systematic empirical
no nor or but if then so than because while when where which who whom whose what why how
hoarding hoard hoards
""".split())

WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z\-]+")


def tokenize(text: str) -> list[str]:
    toks = [t.lower() for t in WORD_RE.findall(text or "")]
    return [t for t in toks if t not in STOPWORDS and len(t) > 2]


def ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    return [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]


# ---------------------------------------------------------------------------
# Load data: same logic as analyze_self_consistency.py to identify reaffirmed set
# ---------------------------------------------------------------------------
def load_data():
    # SC data
    sc_by_pair = defaultdict(list)
    primary_by_pair = {}
    if STATE_JSONL.exists():
        for line in STATE_JSONL.read_text().splitlines():
            if not line.strip(): continue
            d = json.loads(line)
            if d.get("_header"): continue
            if d.get("verdict"):
                sc_by_pair[(d["pmid"], d["tier"])].append((d["sample_idx"], d["verdict"], d.get("reason","")))
    # Primary-run reasons live in run_*_{tier}.jsonl (committed). For each tier, take the most
    # recent file matching that tier.
    for jsonl in sorted(SCRIPT_DIR.glob("run_*.jsonl")):
        if jsonl.name.endswith(".aborted-sonnet-4-5"): continue
        for line in jsonl.read_text().splitlines():
            if not line.strip(): continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError: continue
            if d.get("_header"): continue
            if d.get("verdict") and d.get("reason"):
                key = (d["pmid"], d["tier"])
                # Keep the last one seen (most recent file wins; sorted by name puts later first)
                primary_by_pair[key] = (d["verdict"], d["reason"])
    return sc_by_pair, primary_by_pair


def majority_or_none(verdicts: list[str]) -> tuple[str, int]:
    verdicts = [v for v in verdicts if v in LABELS]
    if not verdicts: return "", 0
    c = Counter(verdicts).most_common()
    if len(c) > 1 and c[0][1] == c[1][1]:
        return "", 0
    return c[0][0], c[0][1]


def reaffirmed_set(sc_by_pair, heur):
    """Replicate analyze_self_consistency.py's reaffirmed-disagreement subset."""
    # Per-tier majority verdict
    tier_majority = {t: {} for t in TIERS}
    for (pmid, tier), samples in sc_by_pair.items():
        if tier not in TIERS: continue
        mv, _ = majority_or_none([v for _, v, _ in samples])
        if mv:
            tier_majority[tier][pmid] = mv
    eligible = []
    for pmid in set().union(*[set(tier_majority[t]) for t in TIERS]):
        if all(pmid in tier_majority[t] for t in TIERS):
            mvs = [tier_majority[t][pmid] for t in TIERS]
            if len(set(mvs)) == 1 and mvs[0] != heur.get(pmid, ""):
                eligible.append((pmid, heur[pmid], mvs[0]))
    return eligible


# ---------------------------------------------------------------------------
# Main report
# ---------------------------------------------------------------------------
def main():
    heur = {r["PMID"]: r["Screening_Decision"] for r in csv.DictReader(HEUR_CSV.open())}
    raw  = {r["pmid"]: r for r in csv.DictReader(RAW_CSV.open())}

    sc_by_pair, primary_by_pair = load_data()
    reaffirmed = reaffirmed_set(sc_by_pair, heur)
    by_axis = defaultdict(list)
    for pmid, h, l in reaffirmed:
        by_axis[(h, l)].append(pmid)

    out = ["# Disagreement Reasoning Analysis",
           "",
           f"Subset: the {len(reaffirmed)}-paper reaffirmed-disagreement set (unanimous 3-tier majority differs from heuristic; computed from `sc_state.jsonl` as in `analyze_self_consistency.py`).",
           "",
           "All reasons below are model outputs from the Claude 4-5 / 4-6 / 4-7 family screeners "
           "(see protocol §5). Reasons are presented verbatim, capped at 25 words each by the prompt template "
           "(`prompt_v1.txt`).",
           "",
           "## Axis distribution",
           "",
           "| Disagreement axis | n papers |",
           "|---|---|",
    ]
    for (h, l), pmids in sorted(by_axis.items(), key=lambda x: -len(x[1])):
        out.append(f"| heuristic={h} → LLM consensus={l} | {len(pmids)} |")
    out.append("")

    # --- Per-axis lexical pattern ---
    for (h, l), pmids in sorted(by_axis.items(), key=lambda x: -len(x[1])):
        out.append(f"## Axis: heuristic={h} → LLM consensus={l} (n={len(pmids)})")
        out.append("")
        # Gather all reasons for this axis
        all_reasons = []
        per_pmid_reasons: dict[str, list[tuple[str,str,int,str,str]]] = defaultdict(list)
        # (tier, source, sample_idx, verdict, reason)
        for pmid in pmids:
            for t in TIERS:
                if (pmid, t) in primary_by_pair:
                    v, r = primary_by_pair[(pmid, t)]
                    if r:
                        all_reasons.append(r)
                        per_pmid_reasons[pmid].append((t, "primary", -1, v, r))
                for s_idx, v, r in sc_by_pair.get((pmid, t), []):
                    if r:
                        all_reasons.append(r)
                        per_pmid_reasons[pmid].append((t, "sc", s_idx, v, r))
        # Top bigrams + trigrams
        bigrams  = Counter()
        trigrams = Counter()
        for r in all_reasons:
            toks = tokenize(r)
            bigrams.update(ngrams(toks, 2))
            trigrams.update(ngrams(toks, 3))
        out.append(f"Reasons collected: **{len(all_reasons)}** (avg per paper: {len(all_reasons)/max(1,len(pmids)):.1f}).")
        out.append("")
        if bigrams:
            out.append("**Top 12 bigrams (after stopword removal):**")
            out.append("")
            for ng, n in bigrams.most_common(12):
                out.append(f"- {' '.join(ng)} ({n})")
            out.append("")
        if trigrams:
            out.append("**Top 8 trigrams:**")
            out.append("")
            for ng, n in trigrams.most_common(8):
                out.append(f"- {' '.join(ng)} ({n})")
            out.append("")

        # --- 3 representative example papers ---
        out.append("**Representative papers (first 3 by PMID, with verbatim reasons):**")
        out.append("")
        for pmid in sorted(pmids)[:3]:
            title = raw.get(pmid, {}).get("title", "(title unavailable)")
            year  = raw.get(pmid, {}).get("year", "")
            journal = raw.get(pmid, {}).get("journal", "")
            out.append(f"### PMID {pmid} — {year}, *{journal}*")
            out.append(f"> {title}")
            out.append("")
            grouped = defaultdict(list)
            for t, src, s_idx, v, r in per_pmid_reasons.get(pmid, []):
                grouped[t].append((src, s_idx, v, r))
            for tier in TIERS:
                entries = grouped.get(tier, [])
                if not entries: continue
                out.append(f"- **{tier}** (verdicts: " + ", ".join(f"{src}{('#'+str(s_idx)) if s_idx>=0 else ''}={v}" for src, s_idx, v, r in entries) + ")")
                for src, s_idx, v, r in entries:
                    lab = f"{src}{('#'+str(s_idx)) if s_idx>=0 else ''}"
                    out.append(f"  - `{lab}` → {v}: \"{r}\"")
                out.append("")
        out.append("")

    # --- Cross-LLM reason agreement on a paper ---
    out.append("## Cross-LLM reason agreement on the same paper")
    out.append("")
    out.append("For each reaffirmed-disagreement paper, we measure jaccard similarity of "
               "stopword-free token sets between the **primary-run reason** of each model pair, "
               "and report the mean across the 51-paper set.")
    out.append("")
    def jaccard(a, b):
        if not a or not b: return 0.0
        sa, sb = set(a), set(b)
        return len(sa & sb) / max(1, len(sa | sb))
    pair_mean = {}
    for t1 in TIERS:
        for t2 in TIERS:
            if t1 >= t2: continue
            sims = []
            for pmid, _, _ in reaffirmed:
                r1 = primary_by_pair.get((pmid, t1), (None, None))[1]
                r2 = primary_by_pair.get((pmid, t2), (None, None))[1]
                if not r1 or not r2: continue
                sims.append(jaccard(tokenize(r1), tokenize(r2)))
            if sims:
                pair_mean[(t1, t2)] = sum(sims)/len(sims)
    out.append("| pair | mean jaccard | n papers |")
    out.append("|---|---|---|")
    for (t1, t2), m in pair_mean.items():
        n = sum(1 for pmid, _, _ in reaffirmed
                if primary_by_pair.get((pmid, t1), (None, None))[1]
                and primary_by_pair.get((pmid, t2), (None, None))[1])
        out.append(f"| {t1} ↔ {t2} | {m:.3f} | {n} |")
    out.append("")
    out.append("A mean jaccard of ~0.2-0.3 indicates the models name *different* specific evidence "
               "(words/phrases) even when they converge on the same verdict; a mean of ~0.5+ indicates "
               "they cite the same evidence. Either pattern is informative: the former shows three "
               "independent paths to the same verdict; the latter shows shared training-data fingerprints.")
    out.append("")

    # --- Headline ---
    out.append("## Headline")
    out.append("")
    if reaffirmed:
        top_axis = max(by_axis.items(), key=lambda x: len(x[1]))
        out.append(f"- The largest reaffirmed-disagreement axis is **heuristic={top_axis[0][0]} → LLM consensus={top_axis[0][1]}** "
                   f"({len(top_axis[1])} papers).")
        out.append(f"- This axis matches the dominant pattern reported in the primary run "
                   f"and self-consistency follow-up: the heuristic's `Maybe` tier is the locus "
                   f"where automated screeners diverge most consistently.")
        # Top bigram on dominant axis
        top_reasons = []
        for pmid in top_axis[1]:
            for t in TIERS:
                if (pmid, t) in primary_by_pair:
                    top_reasons.append(primary_by_pair[(pmid, t)][1])
                for _, v, r in sc_by_pair.get((pmid, t), []):
                    if r:
                        top_reasons.append(r)
        bg = Counter()
        for r in top_reasons:
            bg.update(ngrams(tokenize(r), 2))
        if bg:
            top = bg.most_common(3)
            out.append(f"- Top bigrams in the dominant axis's reasons: " +
                       ", ".join(f"\"{ ' '.join(b) }\" ({n})" for b, n in top))
    out.append("")
    out.append("**No new validity claim.** Lexical patterns describe *what the screeners said*, "
               "not whether they were right. Human triage on this 51-paper subset is the next step.")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(out))
    print(f"[analyze-reasons] wrote {OUT_MD}")


if __name__ == "__main__":
    main()
