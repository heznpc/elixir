#!/usr/bin/env python3
"""
Analyze LLM-second-reviewer results against the heuristic verdicts.

Inputs:
  experiments/data/processed/screening_results.csv          heuristic verdicts
  experiments/data/processed/llm_second_reviewer_results.csv (from run.py)
  experiments/data/raw/pubmed_results.csv                   for year-stratified subset

Outputs:
  experiments/results/llm_second_reviewer_summary.md
  experiments/results/llm_second_reviewer_confusion.csv

Reports per protocol §9:
  - Linear-weighted Cohen's kappa with 95% bootstrap CI (seed 20260521, 1000 resamples)
  - PABAK (Prevalence-Adjusted Bias-Adjusted Kappa)
  - Confusion matrix 3x3
  - 2025-2026 subset secondary analysis per §7
  - Pairwise model-vs-model kappa per §5
"""

from __future__ import annotations

import csv
import math
import pathlib
import random
from collections import Counter, defaultdict

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
EXP_DIR    = SCRIPT_DIR.parent
HEUR_CSV   = EXP_DIR / "data" / "processed" / "screening_results.csv"
LLM_CSV    = EXP_DIR / "data" / "processed" / "llm_second_reviewer_results.csv"
RAW_CSV    = EXP_DIR / "data" / "raw" / "pubmed_results.csv"
OUT_MD     = EXP_DIR / "results" / "llm_second_reviewer_summary.md"
OUT_CONF   = EXP_DIR / "results" / "llm_second_reviewer_confusion.csv"

LABELS = ["Include", "Maybe", "Exclude"]
LABEL_IDX = {l: i for i, l in enumerate(LABELS)}


def linear_weights(k: int) -> list[list[float]]:
    """Linear weights: w[i][j] = 1 - |i-j|/(k-1)."""
    return [[1 - abs(i - j) / (k - 1) for j in range(k)] for i in range(k)]


def weighted_kappa(rater_a: list[str], rater_b: list[str]) -> float:
    """Linear-weighted Cohen's kappa over LABELS."""
    k = len(LABELS)
    n = len(rater_a)
    if n == 0:
        return float("nan")
    obs = [[0] * k for _ in range(k)]
    for a, b in zip(rater_a, rater_b):
        if a in LABEL_IDX and b in LABEL_IDX:
            obs[LABEL_IDX[a]][LABEL_IDX[b]] += 1
    n = sum(sum(r) for r in obs)
    if n == 0:
        return float("nan")
    row = [sum(obs[i]) / n for i in range(k)]
    col = [sum(obs[i][j] for i in range(k)) / n for j in range(k)]
    w = linear_weights(k)
    po = sum(w[i][j] * obs[i][j] / n for i in range(k) for j in range(k))
    pe = sum(w[i][j] * row[i] * col[j] for i in range(k) for j in range(k))
    if pe == 1:
        return float("nan")
    return (po - pe) / (1 - pe)


def raw_cohen_kappa(rater_a: list[str], rater_b: list[str]) -> float:
    """Unweighted Cohen's kappa."""
    k = len(LABELS)
    obs = [[0] * k for _ in range(k)]
    for a, b in zip(rater_a, rater_b):
        if a in LABEL_IDX and b in LABEL_IDX:
            obs[LABEL_IDX[a]][LABEL_IDX[b]] += 1
    n = sum(sum(r) for r in obs)
    if n == 0:
        return float("nan")
    po = sum(obs[i][i] for i in range(k)) / n
    pe = sum((sum(obs[i]) / n) * (sum(obs[j][i] for j in range(k)) / n) for i in range(k))
    if pe == 1:
        return float("nan")
    return (po - pe) / (1 - pe)


def pabak(rater_a: list[str], rater_b: list[str]) -> float:
    """Prevalence-Adjusted Bias-Adjusted Kappa.
    PABAK = (k * p_o - 1) / (k - 1)  where k = num categories, p_o = observed agreement."""
    k = len(LABELS)
    obs = sum(1 for a, b in zip(rater_a, rater_b) if a == b and a in LABEL_IDX)
    n = sum(1 for a, b in zip(rater_a, rater_b) if a in LABEL_IDX and b in LABEL_IDX)
    if n == 0:
        return float("nan")
    po = obs / n
    return (k * po - 1) / (k - 1)


def bootstrap_kappa_ci(rater_a: list[str], rater_b: list[str],
                       n_boot: int = 1000, seed: int = 20260521,
                       weighted: bool = True) -> tuple[float, float]:
    """95% percentile bootstrap CI for kappa."""
    rng = random.Random(seed)
    pairs = list(zip(rater_a, rater_b))
    n = len(pairs)
    kfn = weighted_kappa if weighted else raw_cohen_kappa
    samples = []
    for _ in range(n_boot):
        resamp = [pairs[rng.randrange(n)] for _ in range(n)]
        a = [x[0] for x in resamp]
        b = [x[1] for x in resamp]
        k = kfn(a, b)
        if not math.isnan(k):
            samples.append(k)
    samples.sort()
    if not samples:
        return (float("nan"), float("nan"))
    lo = samples[int(0.025 * len(samples))]
    hi = samples[int(0.975 * len(samples)) - 1]
    return (lo, hi)


def confusion_matrix(rater_a: list[str], rater_b: list[str]) -> list[list[int]]:
    k = len(LABELS)
    obs = [[0] * k for _ in range(k)]
    for a, b in zip(rater_a, rater_b):
        if a in LABEL_IDX and b in LABEL_IDX:
            obs[LABEL_IDX[a]][LABEL_IDX[b]] += 1
    return obs


def mcnemar_bowker_p(obs: list[list[int]]) -> float | None:
    """McNemar-Bowker test of symmetry (3x3). Returns p-value or None if undefined."""
    k = len(obs)
    chi2 = 0.0
    df = 0
    for i in range(k):
        for j in range(i + 1, k):
            n_ij = obs[i][j]
            n_ji = obs[j][i]
            if n_ij + n_ji > 0:
                chi2 += (n_ij - n_ji) ** 2 / (n_ij + n_ji)
                df += 1
    if df == 0:
        return None
    # Approx p via chi^2 survival; use simple gamma series since stdlib lacks scipy.
    # 1-CDF of chi2(df). We approximate via the upper incomplete gamma function.
    def upper_gamma(s: float, x: float) -> float:
        # Regularized upper gamma Q(s, x) via continued fraction (Lentz)
        if x < s + 1.0:
            # series
            ap, val = s, 1.0 / s
            term = val
            for _ in range(200):
                ap += 1
                term *= x / ap
                val += term
                if abs(term) < abs(val) * 1e-12:
                    break
            return 1.0 - val * math.exp(-x + s * math.log(x) - math.lgamma(s))
        # continued fraction
        b = x + 1.0 - s
        c, d = 1e300, 1.0 / b
        h = d
        for i in range(1, 200):
            an = -i * (i - s)
            b += 2.0
            d = an * d + b
            if abs(d) < 1e-300: d = 1e-300
            c = b + an / c
            if abs(c) < 1e-300: c = 1e-300
            d = 1.0 / d
            delta = d * c
            h *= delta
            if abs(delta - 1.0) < 1e-12:
                break
        return math.exp(-x + s * math.log(x) - math.lgamma(s)) * h
    return upper_gamma(df / 2.0, chi2 / 2.0)


def load_data():
    with HEUR_CSV.open() as f:
        heur = {r["PMID"]: r["Screening_Decision"] for r in csv.DictReader(f)}
    llm_rows = []
    if LLM_CSV.exists():
        with LLM_CSV.open() as f:
            llm_rows = list(csv.DictReader(f))
    years = {}
    with RAW_CSV.open() as f:
        for r in csv.DictReader(f):
            years[r["pmid"]] = r.get("year", "")
    return heur, llm_rows, years


def report():
    heur, llm_rows, years = load_data()
    if not llm_rows:
        OUT_MD.parent.mkdir(parents=True, exist_ok=True)
        OUT_MD.write_text("# LLM second reviewer audit — no results yet\n\n"
                          "`experiments/data/processed/llm_second_reviewer_results.csv` is missing or empty. "
                          "Run `python experiments/llm_second_reviewer/run.py` first.\n")
        print(f"[analyze] no LLM results found; wrote placeholder {OUT_MD}")
        return

    tiers = sorted(set(r["tier"] for r in llm_rows if r["tier"]))
    out = ["# LLM-as-Second-Reviewer Audit — Summary",
           "",
           "Pre-registered protocol: `experiments/llm_second_reviewer/protocol.md`.",
           "",
           f"Tiers analyzed: {', '.join(tiers)}.",
           ""]

    # Per-tier (LLM vs heuristic)
    for tier in tiers:
        rows = [r for r in llm_rows if r["tier"] == tier]
        out.append(f"## Tier: {tier} (model: {rows[0]['model']})")
        out.append("")
        hv = [heur.get(r["pmid"], "") for r in rows]
        lv = [r["llm_verdict"] for r in rows]
        # Drop rows where either is missing/empty
        pairs = [(a, b) for a, b in zip(hv, lv) if a and b]
        a, b = [x[0] for x in pairs], [x[1] for x in pairs]
        n = len(a)
        if n == 0:
            out.append(f"- No usable pairs (heuristic+LLM both present).")
            out.append("")
            continue
        wk = weighted_kappa(a, b)
        rk = raw_cohen_kappa(a, b)
        pk = pabak(a, b)
        ci_lo, ci_hi = bootstrap_kappa_ci(a, b, weighted=True)
        cm = confusion_matrix(a, b)
        out.append(f"- n usable pairs: **{n}** (of {len(rows)} total tier records)")
        out.append(f"- Weighted Cohen's κ: **{wk:.3f}** (95% bootstrap CI [{ci_lo:.3f}, {ci_hi:.3f}], 1000 resamples, seed 20260521)")
        out.append(f"- Unweighted Cohen's κ: {rk:.3f}")
        out.append(f"- PABAK (per Khraisha et al. 2024): **{pk:.3f}**")
        # Pre-registered decision-rule outcome
        if wk > 0.60:
            band = "κ > 0.60 → substantial IRR. Allowed claim: \"Heuristic and single-model LLM screener show substantial inter-rater reliability over n abstracts.\""
        elif wk > 0.40:
            band = "0.40 < κ ≤ 0.60 → moderate IRR. Allowed claim: \"Moderate IRR; disagreement set flagged for human triage.\""
        else:
            band = "κ ≤ 0.40 → low IRR. The 156 eligible figure rests on the heuristic alone."
        out.append(f"- Pre-registered band (§4): {band}")
        # McNemar-Bowker
        p = mcnemar_bowker_p(cm)
        if p is not None:
            out.append(f"- McNemar-Bowker symmetry test: p ≈ {p:.4g} ({'asymmetric' if p < 0.05 else 'consistent with symmetry'})")
        out.append("")
        # Confusion matrix
        out.append(f"**Confusion matrix (rows = heuristic, cols = {tier} LLM)**")
        out.append("")
        out.append("| h \\ L | " + " | ".join(LABELS) + " | row total |")
        out.append("|---" * (len(LABELS) + 2) + "|")
        for i, lab in enumerate(LABELS):
            rowsum = sum(cm[i])
            out.append(f"| **{lab}** | " + " | ".join(str(x) for x in cm[i]) + f" | {rowsum} |")
        coltot = [sum(cm[i][j] for i in range(len(LABELS))) for j in range(len(LABELS))]
        out.append(f"| **col total** | " + " | ".join(str(x) for x in coltot) + f" | {sum(coltot)} |")
        out.append("")

        # Secondary analysis: 2025+ subset (§7)
        sub_pairs = []
        for r in rows:
            y = years.get(r["pmid"], "")
            h = heur.get(r["pmid"], "")
            l = r["llm_verdict"]
            if h and l and y >= "2025":
                sub_pairs.append((h, l))
        if sub_pairs:
            sa = [x[0] for x in sub_pairs]; sb = [x[1] for x in sub_pairs]
            swk = weighted_kappa(sa, sb)
            spk = pabak(sa, sb)
            sci = bootstrap_kappa_ci(sa, sb, weighted=True)
            out.append(f"**Secondary (2025+ subset, contamination-robustness per §7):** "
                       f"n = {len(sub_pairs)}, weighted κ = {swk:.3f} "
                       f"(95% CI [{sci[0]:.3f}, {sci[1]:.3f}]), PABAK = {spk:.3f}")
            # H0_2025 decision
            if swk > 0.40:
                out.append(f"- H0_2025: rejected (κ > 0.40 on post-cutoff subset). Contamination not the main driver of full-corpus agreement.")
            else:
                out.append(f"- H0_2025: not rejected (κ ≤ 0.40 on post-cutoff subset). Contamination may inflate full-corpus number.")
            out.append("")

    # Pairwise model-vs-model
    if len(tiers) >= 2:
        out.append("## Pairwise model-vs-model agreement")
        out.append("")
        by_pmid = defaultdict(dict)
        for r in llm_rows:
            by_pmid[r["pmid"]][r["tier"]] = r["llm_verdict"]
        for i in range(len(tiers)):
            for j in range(i + 1, len(tiers)):
                t1, t2 = tiers[i], tiers[j]
                pairs = [(by_pmid[p][t1], by_pmid[p][t2])
                         for p in by_pmid
                         if t1 in by_pmid[p] and t2 in by_pmid[p]
                         and by_pmid[p][t1] and by_pmid[p][t2]]
                if not pairs:
                    continue
                a = [x[0] for x in pairs]; b = [x[1] for x in pairs]
                wk = weighted_kappa(a, b)
                ci = bootstrap_kappa_ci(a, b, weighted=True)
                pk = pabak(a, b)
                out.append(f"- **{t1} ↔ {t2}**: n = {len(pairs)}, weighted κ = {wk:.3f} "
                           f"(95% CI [{ci[0]:.3f}, {ci[1]:.3f}]), PABAK = {pk:.3f}")
        out.append("")

    # Disagreement set summary
    out.append("## Disagreement set")
    out.append("")
    for tier in tiers:
        rows = [r for r in llm_rows if r["tier"] == tier]
        disagrees = []
        for r in rows:
            h = heur.get(r["pmid"], "")
            l = r["llm_verdict"]
            if h and l and h != l:
                disagrees.append((r["pmid"], h, l))
        out.append(f"- {tier}: **{len(disagrees)}** disagreements / {len(rows)} pairs")
        if disagrees:
            cnt = Counter((h, l) for _, h, l in disagrees)
            for (h, l), n in cnt.most_common():
                out.append(f"  - heuristic={h} → LLM={l}: {n}")
    out.append("")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(out))
    print(f"[analyze] wrote {OUT_MD}")

    # Long-format confusion CSV
    with OUT_CONF.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tier", "heuristic_verdict", "llm_verdict", "count"])
        for tier in tiers:
            rows = [r for r in llm_rows if r["tier"] == tier]
            hv = [heur.get(r["pmid"], "") for r in rows]
            lv = [r["llm_verdict"] for r in rows]
            cm = confusion_matrix(hv, lv)
            for i, lh in enumerate(LABELS):
                for j, ll in enumerate(LABELS):
                    w.writerow([tier, lh, ll, cm[i][j]])
    print(f"[analyze] wrote {OUT_CONF}")


if __name__ == "__main__":
    report()
