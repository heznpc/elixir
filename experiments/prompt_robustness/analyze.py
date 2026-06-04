#!/usr/bin/env python3
"""
Analyze the prompt-robustness run vs pre-registered bands.

Pre-registered: experiments/prompt_robustness/protocol.md.

Reads (does NOT modify):
  experiments/data/processed/llm_second_reviewer_results.csv   (original per-tier verdicts)
  experiments/prompt_robustness/data/prompt_robustness_results.csv
  experiments/llm_second_reviewer/convergent_disagreements.csv

Writes:
  experiments/results/prompt_robustness_summary.md

Primary statistic: Δ = flip_rate(V_lenient) − flip_rate(V_reword), where a flip
is variant_verdict != that model's ORIGINAL (2026-05-21) verdict on the paper.
"""

from __future__ import annotations

import csv
import pathlib
from collections import defaultdict

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
EXP_DIR    = SCRIPT_DIR.parent
ORIG_CSV   = EXP_DIR / "data" / "processed" / "llm_second_reviewer_results.csv"
VAR_CSV    = SCRIPT_DIR / "data" / "prompt_robustness_results.csv"
CONV_CSV   = EXP_DIR / "llm_second_reviewer" / "convergent_disagreements.csv"
OUT_MD     = EXP_DIR / "results" / "prompt_robustness_summary.md"

TIERS = ["haiku", "sonnet"]
VARIANTS = ["reword", "lenient"]
INCLUSIVITY = {"Exclude": 0, "Maybe": 1, "Include": 2}  # higher = more inclusive


def main():
    if not VAR_CSV.exists():
        OUT_MD.parent.mkdir(parents=True, exist_ok=True)
        OUT_MD.write_text("# Prompt-robustness — no results yet\n")
        print("[analyze] no results")
        return

    # original per-(pmid,tier) verdict + heuristic
    orig = defaultdict(dict)
    heur = {}
    for r in csv.DictReader(ORIG_CSV.open()):
        orig[r["pmid"]][r["tier"]] = r["llm_verdict"]
        heur[r["pmid"]] = r["heuristic_verdict"]
    conv = {r["pmid"]: r["llm_consensus"] for r in csv.DictReader(CONV_CSV.open())}
    # variant verdicts: (pmid, variant, tier) -> verdict
    var = {}
    for r in csv.DictReader(VAR_CSV.open()):
        if r.get("verdict"):
            var[(r["pmid"], r["variant"], r["tier"])] = r["verdict"]

    conv_pmids = list(conv)

    out = ["# Prompt-Robustness of the Cross-Model Convergence — Summary",
           "",
           "Pre-registered: `experiments/prompt_robustness/protocol.md`.",
           "Tests the PROMPT half of shared-method-variance (Tier B, feasible slice).",
           "",
           f"Convergent-disagreement papers: {len(conv_pmids)}. "
           f"Models: {', '.join(TIERS)}. Variants: {', '.join(VARIANTS)}.",
           ""]

    # flip rates per variant per tier
    out.append("## Flip rates (variant verdict ≠ original 2026-05-21 verdict)")
    out.append("")
    out.append("| variant | tier | n | flips | flip_rate | toward-inclusion / flips |")
    out.append("|---|---|---|---|---|---|")
    flip_rate = defaultdict(dict)  # variant -> tier -> rate
    for variant in VARIANTS:
        for tier in TIERS:
            n = flips = incl = 0
            for p in conv_pmids:
                o = orig.get(p, {}).get(tier, "")
                v = var.get((p, variant, tier), "")
                if not o or not v:
                    continue
                n += 1
                if v != o:
                    flips += 1
                    if INCLUSIVITY.get(v, -1) > INCLUSIVITY.get(o, -1):
                        incl += 1
            rate = flips / n if n else float("nan")
            flip_rate[variant][tier] = rate
            incl_str = f"{incl}/{flips}" if flips else "0/0"
            out.append(f"| {variant} | {tier} | {n} | {flips} | {rate:.3f} | {incl_str} |")
    out.append("")

    # pooled flip rates
    def pooled(variant):
        n = flips = 0
        for p in conv_pmids:
            for tier in TIERS:
                o = orig.get(p, {}).get(tier, "")
                v = var.get((p, variant, tier), "")
                if not o or not v:
                    continue
                n += 1
                if v != o:
                    flips += 1
        return (flips / n if n else float("nan")), n, flips
    rw_rate, rw_n, rw_f = pooled("reword")
    ln_rate, ln_n, ln_f = pooled("lenient")
    delta = ln_rate - rw_rate

    out.append("## Primary statistic")
    out.append("")
    out.append(f"- flip_rate(V_reword)  = **{rw_rate:.3f}** ({rw_f}/{rw_n}) — noise-floor control")
    out.append(f"- flip_rate(V_lenient) = **{ln_rate:.3f}** ({ln_f}/{ln_n}) — adversarial pro-inclusion")
    out.append(f"- **Δ = {delta:+.3f}**")
    out.append("")
    if rw_rate >= 0.40:
        floor = ("⚠️ noise floor is high (reword flips ≥ 0.40) — the models are unstable to "
                 "meaning-preserving rewording; the Δ comparison is weakened. Interpret with caution.")
    else:
        floor = f"noise floor acceptable (reword {rw_rate:.3f} < 0.40)."
    out.append(f"- Noise-floor check: {floor}")
    out.append("")
    if delta < 0.15:
        verdict = ("**Δ < 0.15 — the off-heuristic verdicts are ROBUST to directional prompt pressure.** "
                   "The convergence is NOT a prompt artifact (prompt-half of shared-method-variance ruled out).")
    elif delta < 0.40:
        verdict = ("**0.15 ≤ Δ < 0.40 — partial prompt-sensitivity.** The convergence is partly, "
                   "but not mostly, prompt-induced.")
    else:
        verdict = ("**Δ ≥ 0.40 — the convergence is SUBSTANTIALLY prompt-induced.** The Tier A "
                   "'generation-stable' finding is downgraded: stability across Claude generations "
                   "partly reflects the shared prompt, not independent signal.")
    out.append(f"- Verdict: {verdict}")
    out.append("")

    # directional check under lenient
    tot_flips = tot_incl = 0
    for p in conv_pmids:
        for tier in TIERS:
            o = orig.get(p, {}).get(tier, "")
            v = var.get((p, "lenient", tier), "")
            if not o or not v or v == o:
                continue
            tot_flips += 1
            if INCLUSIVITY.get(v, -1) > INCLUSIVITY.get(o, -1):
                tot_incl += 1
    out.append("## Directional check (V_lenient flips)")
    out.append("")
    if tot_flips:
        out.append(f"- Of {tot_flips} lenient flips, **{tot_incl} ({tot_incl/tot_flips:.0%}) move toward MORE inclusion** "
                   "(Exclude→Maybe/Include, Maybe→Include).")
        out.append("- A genuine leniency effect is near-100% directional. Non-directional flips are noise.")
    else:
        out.append("- No lenient flips at all — the off-heuristic verdicts are fully stable under adversarial pressure.")
    out.append("")

    # survival: how many of the 59 original off-heuristic verdicts survive on BOTH models under lenient
    survive_both = 0
    eval_n = 0
    for p in conv_pmids:
        os_ = [orig.get(p, {}).get(t, "") for t in TIERS]
        vs = [var.get((p, "lenient", t), "") for t in TIERS]
        if all(os_) and all(vs):
            eval_n += 1
            if all(vs[i] == os_[i] for i in range(len(TIERS))):
                survive_both += 1
    out.append("## Survival under adversarial prompt")
    out.append("")
    out.append(f"- Papers where BOTH models keep their original off-heuristic verdict under V_lenient: "
               f"**{survive_both}/{eval_n}** ({survive_both/max(1,eval_n):.0%}).")
    out.append("")

    out.append("## Structural limit (honest)")
    out.append("")
    out.append("This tests ONLY the prompt component. Even a fully-robust result does not rule out shared "
               "training-lineage artifact — all conditions still use Claude models. Resolving that needs a "
               "non-Claude rater (cross-vendor, blocked by the Claude-only decision + missing keys) or human "
               "gold (deferred). Reported as the prompt-half of the shared-method-variance question only.")
    out.append("")
    out.append("## Headline")
    out.append("")
    out.append(f"- flip_rate reword={rw_rate:.3f}, lenient={ln_rate:.3f}, **Δ={delta:+.3f}** — {verdict.split('—')[0].strip().replace('**','')}")
    out.append(f"- lenient flips toward inclusion: {tot_incl}/{tot_flips}")
    out.append(f"- both-model survival under adversarial prompt: {survive_both}/{eval_n}")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(out))
    print(f"[analyze] wrote {OUT_MD}")
    print(f"[headline] reword={rw_rate:.3f} lenient={ln_rate:.3f} delta={delta:+.3f} "
          f"dir={tot_incl}/{tot_flips} survive={survive_both}/{eval_n}")


if __name__ == "__main__":
    main()
