#!/usr/bin/env python3
"""
Analyze the Opus 4-8 cross-generation rater run vs pre-registered bands.

Pre-registered: experiments/opus48_crossgen/protocol.md.

Reads (does NOT modify):
  experiments/data/processed/llm_second_reviewer_results.csv  (original 3 tiers, deduped)
  experiments/opus48_crossgen/data/opus48_results.csv          (the new 4-8 verdicts)
  experiments/data/raw/pubmed_results.csv                      (years, for the DiD)
  experiments/llm_second_reviewer/convergent_disagreements.csv (59-paper A1 subset)

Writes:
  experiments/results/opus48_crossgen_summary.md

Computes:
  - weighted Cohen's kappa(4-8, heuristic) + PABAK + 95% bootstrap CI  -> H0-heuristic band
  - weighted kappa(4-8, each of haiku/sonnet/opus)                     -> H0-crossgen bands
  - A1: of 59 convergent-disagreement papers, how many 4-8 matches trio consensus
  - A2: Jaccard of disagreement-with-heuristic sets (4-8 vs trio-majority)
  - A3: difference-in-differences (4-8 post-pre) - (4-7 post-pre) vs heuristic, 2025+ split
"""

from __future__ import annotations

import csv
import math
import pathlib
import random
from collections import Counter, defaultdict

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
EXP_DIR    = SCRIPT_DIR.parent
ORIG_CSV   = EXP_DIR / "data" / "processed" / "llm_second_reviewer_results.csv"
OPUS48_CSV = SCRIPT_DIR / "data" / "opus48_results.csv"
RAW_CSV    = EXP_DIR / "data" / "raw" / "pubmed_results.csv"
CONV_CSV   = EXP_DIR / "llm_second_reviewer" / "convergent_disagreements.csv"
OUT_MD     = EXP_DIR / "results" / "opus48_crossgen_summary.md"

LABELS = ["Include", "Maybe", "Exclude"]
IDX = {l: i for i, l in enumerate(LABELS)}
SEED = 20260521


def _linw(k):
    return [[1 - abs(i - j) / (k - 1) for j in range(k)] for i in range(k)]


def weighted_kappa(a, b):
    k = len(LABELS)
    obs = [[0]*k for _ in range(k)]
    for x, y in zip(a, b):
        if x in IDX and y in IDX:
            obs[IDX[x]][IDX[y]] += 1
    n = sum(sum(r) for r in obs)
    if n == 0:
        return float("nan")
    row = [sum(obs[i])/n for i in range(k)]
    col = [sum(obs[i][j] for i in range(k))/n for j in range(k)]
    w = _linw(k)
    po = sum(w[i][j]*obs[i][j]/n for i in range(k) for j in range(k))
    pe = sum(w[i][j]*row[i]*col[j] for i in range(k) for j in range(k))
    return float("nan") if pe == 1 else (po - pe)/(1 - pe)


def pabak(a, b):
    k = len(LABELS)
    obs = sum(1 for x, y in zip(a, b) if x == y and x in IDX)
    n = sum(1 for x, y in zip(a, b) if x in IDX and y in IDX)
    if n == 0:
        return float("nan")
    return (k*(obs/n) - 1)/(k - 1)


def boot_ci(a, b, n_boot=1000, seed=SEED):
    rng = random.Random(seed)
    pairs = [(x, y) for x, y in zip(a, b) if x in IDX and y in IDX]
    n = len(pairs)
    if n == 0:
        return (float("nan"), float("nan"))
    samples = []
    for _ in range(n_boot):
        rs = [pairs[rng.randrange(n)] for _ in range(n)]
        kv = weighted_kappa([p[0] for p in rs], [p[1] for p in rs])
        if not math.isnan(kv):
            samples.append(kv)
    samples.sort()
    if not samples:
        return (float("nan"), float("nan"))
    return (samples[int(0.025*len(samples))], samples[int(0.975*len(samples))-1])


def main():
    if not OPUS48_CSV.exists():
        OUT_MD.parent.mkdir(parents=True, exist_ok=True)
        OUT_MD.write_text("# Opus 4-8 cross-gen — no results yet\n")
        print("[analyze] no opus48 results")
        return

    # Original tiers: pmid -> {tier: llm_verdict}, plus heuristic
    orig = defaultdict(dict)
    heur = {}
    for r in csv.DictReader(ORIG_CSV.open()):
        orig[r["pmid"]][r["tier"]] = r["llm_verdict"]
        heur[r["pmid"]] = r["heuristic_verdict"]
    # 4-8 verdicts
    o48 = {}
    for r in csv.DictReader(OPUS48_CSV.open()):
        if r.get("verdict"):
            o48[r["pmid"]] = r["verdict"]
    # years
    years = {r["pmid"]: r.get("year", "") for r in csv.DictReader(RAW_CSV.open())}
    # convergent set (trio agreed among themselves, differ from heuristic)
    conv = {r["pmid"]: r["llm_consensus"] for r in csv.DictReader(CONV_CSV.open())}

    pmids = [p for p in o48 if p in heur]  # 4-8 has a verdict + heuristic exists

    out = ["# Opus 4-8 Cross-Generation Robustness — Summary",
           "",
           "Pre-registered: `experiments/opus48_crossgen/protocol.md`.",
           "Framing: cross-GENERATION agreement WITHIN the Claude family (not cross-vendor).",
           "",
           f"4-8 usable verdicts: {len(o48)} / 227. Pairs with heuristic: {len(pmids)}.",
           ""]

    # --- H0-heuristic: kappa(4-8, heuristic) ---
    hv = [heur[p] for p in pmids]
    lv = [o48[p] for p in pmids]
    wk = weighted_kappa(hv, lv)
    pk = pabak(hv, lv)
    lo, hi = boot_ci(hv, lv)
    out.append("## H0-heuristic: weighted kappa(4-8, heuristic)")
    out.append("")
    out.append(f"- weighted kappa = **{wk:.3f}** (95% CI [{lo:.3f}, {hi:.3f}]), PABAK = {pk:.3f}")
    if wk > 0.60:
        band_h = "kappa > 0.60 — 4-8 agrees with heuristic MORE than the trio (0.461-0.532). Check contamination (A3) before concluding 'better'."
    elif wk >= 0.40:
        band_h = "kappa in [0.40, 0.60] — consistent with the original trio band (moderate IRR)."
    else:
        band_h = "kappa < 0.40 — 4-8 is a weaker rater vs heuristic than the trio."
    out.append(f"- Band: {band_h}")
    out.append("")

    # --- H0-crossgen: kappa(4-8, each trio model) ---
    out.append("## H0-crossgen: weighted kappa(4-8, each original model)")
    out.append("")
    out.append("Original trio pairwise baseline: 0.812-0.857.")
    out.append("")
    out.append("| pair | n | weighted kappa | 95% CI | PABAK | band |")
    out.append("|---|---|---|---|---|---|")
    crossgen_kappas = {}
    for tier in ["haiku", "sonnet", "opus"]:
        sub = [(o48[p], orig[p][tier]) for p in pmids if tier in orig[p] and orig[p][tier]]
        a = [x[0] for x in sub]; b = [x[1] for x in sub]
        kv = weighted_kappa(a, b)
        cl, ch = boot_ci(a, b)
        pv = pabak(a, b)
        crossgen_kappas[tier] = kv
        if kv >= 0.75:
            bnd = "stable"
        elif kv >= 0.60:
            bnd = "mild drift"
        else:
            bnd = "**drift**"
        out.append(f"| 4-8 ↔ {tier} | {len(sub)} | {kv:.3f} | [{cl:.3f}, {ch:.3f}] | {pv:.3f} | {bnd} |")
    out.append("")
    worst = min(crossgen_kappas.values())
    if worst >= 0.75:
        crossgen_verdict = "**generation-stable** — 4-8 joins the intra-family convergence (all pairings ≥ 0.75)."
    elif worst >= 0.60:
        crossgen_verdict = "**mild drift** — at least one pairing in [0.60, 0.75); conditional self-consistency follow-up (protocol §7) is triggered."
    else:
        crossgen_verdict = "**generation drift** — at least one pairing < 0.60; the original convergence does not fully generalize to 4-8."
    out.append(f"- Cross-generation verdict: {crossgen_verdict}")
    out.append("")

    # --- A1: convergent-disagreement join test ---
    out.append("## A1 (primary discriminator): convergent-disagreement join")
    out.append("")
    conv_pmids = [p for p in conv if p in o48]
    match_trio = sum(1 for p in conv_pmids if o48[p] == conv[p])
    diff_heur = sum(1 for p in conv_pmids if o48[p] != heur.get(p, ""))
    n_conv = len(conv_pmids)
    out.append(f"- 59-paper convergent-disagreement set (trio agreed among themselves AND differed from heuristic).")
    out.append(f"- 4-8 verdict **matches the trio consensus exactly**: **{match_trio}/{n_conv}** ({match_trio/max(1,n_conv):.0%})")
    out.append(f"- 4-8 verdict merely **differs from heuristic** (weaker test): {diff_heur}/{n_conv} ({diff_heur/max(1,n_conv):.0%})")
    if match_trio >= 50:
        a1 = "**generation-stable** — 4-8 independently lands on the same off-heuristic verdict (≥50/59)."
    elif match_trio >= 35:
        a1 = "**partial** — convergence weakening across generations (35-49/59)."
    else:
        a1 = "**generation-specific** — the original convergence does not generalize to 4-8 (<35/59)."
    out.append(f"- A1 verdict: {a1}")
    out.append("")

    # --- A2: disagreement-set Jaccard ---
    out.append("## A2: disagreement-set Jaccard (4-8 vs trio-majority)")
    out.append("")
    def trio_majority(p):
        vs = [orig[p].get(t, "") for t in ["haiku", "sonnet", "opus"]]
        vs = [v for v in vs if v]
        if not vs:
            return ""
        c = Counter(vs).most_common()
        if len(c) > 1 and c[0][1] == c[1][1]:
            return ""
        return c[0][0]
    set_48 = {p for p in pmids if o48[p] != heur.get(p, "")}
    set_trio = {p for p in pmids if trio_majority(p) and trio_majority(p) != heur.get(p, "")}
    inter = len(set_48 & set_trio)
    union = len(set_48 | set_trio)
    jac = inter / union if union else float("nan")
    out.append(f"- |{{4-8 ≠ heuristic}}| = {len(set_48)}, |{{trio-majority ≠ heuristic}}| = {len(set_trio)}")
    out.append(f"- intersection = {inter}, union = {union}, **Jaccard = {jac:.3f}**")
    out.append(f"- High Jaccard ⇒ moderate kappa reflects disagreement on the SAME papers (real shared signal). "
               f"Low Jaccard at similar kappa ⇒ original convergence partly coincidental.")
    out.append("")

    # --- A3: contamination DiD ---
    out.append("## A3: contamination difference-in-differences")
    out.append("")
    def kappa_subset(verdict_map, subset_pmids):
        a = [heur[p] for p in subset_pmids if p in verdict_map and verdict_map[p]]
        b = [verdict_map[p] for p in subset_pmids if p in verdict_map and verdict_map[p]]
        return weighted_kappa(a, b), len(a)
    pre = [p for p in pmids if years.get(p, "") and years[p] <= "2024"]
    post = [p for p in pmids if years.get(p, "") >= "2025"]
    o47 = {p: orig[p].get("opus", "") for p in orig if orig[p].get("opus")}
    k48_pre, n48pre = kappa_subset(o48, pre)
    k48_post, n48post = kappa_subset(o48, post)
    k47_pre, n47pre = kappa_subset(o47, pre)
    k47_post, n47post = kappa_subset(o47, post)
    did = (k48_post - k48_pre) - (k47_post - k47_pre)
    out.append(f"- 4-8: kappa_pre(≤2024, n={n48pre}) = {k48_pre:.3f}, kappa_post(2025+, n={n48post}) = {k48_post:.3f}, delta = {k48_post-k48_pre:+.3f}")
    out.append(f"- 4-7: kappa_pre(≤2024, n={n47pre}) = {k47_pre:.3f}, kappa_post(2025+, n={n47post}) = {k47_post:.3f}, delta = {k47_post-k47_pre:+.3f}")
    out.append(f"- **DiD = {did:+.3f}**")
    if abs(did) < 0.15:
        a3 = "|DiD| < 0.15 — no contamination signature; 4-8's post/pre pattern matches 4-7's."
    elif did >= 0.15:
        a3 = "DiD ≥ +0.15 — 4-8 shows extra post-cutoff agreement consistent with later-cutoff contamination; any 'better screener' claim is downgraded."
    else:
        a3 = "DiD ≤ -0.15 — 4-8 agrees LESS on post-cutoff papers (not a contamination concern)."
    out.append(f"- A3 verdict: {a3}")
    out.append(f"- Caveat: n_post = {n48post} is small; post kappa and DiD have wide CIs. Descriptive/directional, not a significance test.")
    out.append("")

    # --- structural-limit + headline ---
    out.append("## Structural limit (A4)")
    out.append("")
    out.append("4-8 differs from 4-7 on TWO confounded axes: capability (newer) and contamination exposure "
               "(later cutoff). The DiD (A3) only partially isolates contamination. This design cannot fully "
               "separate the two; the result is reported with that limit explicit.")
    out.append("")
    out.append("## Headline")
    out.append("")
    out.append(f"- H0-heuristic: kappa(4-8, heuristic) = {wk:.3f} — {band_h.split(' — ')[0] if ' — ' in band_h else band_h}")
    out.append(f"- H0-crossgen: {crossgen_verdict}")
    out.append(f"- A1: 4-8 matches trio consensus on {match_trio}/{n_conv} convergent papers — {a1.split(' — ')[0].replace('**','')}")
    out.append(f"- A2: Jaccard = {jac:.3f}")
    out.append(f"- A3: DiD = {did:+.3f} — {a3.split(' — ')[0]}")
    out.append("")
    out.append("**This is footnote-scope supplementary evidence, not a headline result. "
               "It does not move the audit from inter-rater reliability toward validity "
               "(4-8 is also a non-validated rater). The original 2026-05-21 audit summary is unchanged.**")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(out))
    print(f"[analyze] wrote {OUT_MD}")
    # Console headline
    print(f"[headline] kappa(4-8,heur)={wk:.3f}  crossgen_min={worst:.3f}  "
          f"A1={match_trio}/{n_conv}  Jaccard={jac:.3f}  DiD={did:+.3f}")


if __name__ == "__main__":
    main()
