#!/usr/bin/env python3
"""
Analyze the GHI face-validity audit.

Inputs:
  experiments/ghi_face_validity/state.jsonl
  experiments/ghi_face_validity/items_v1.json

Outputs:
  experiments/results/ghi_face_validity_summary.md

Reports per protocol §4 + §7:
  - Per-item flag count (0-9) and category (revise / under review / retained).
  - Per-criterion flag rate (flagged items / 18 across all 3 models).
  - Cross-model agreement: model-unanimous vs majority vs minority flags.
  - Top reasons per flagged item.
"""

from __future__ import annotations

import csv
import json
import pathlib
from collections import Counter, defaultdict

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
EXP_DIR    = SCRIPT_DIR.parent
STATE_JSONL = SCRIPT_DIR / "state.jsonl"
ITEMS_JSON  = SCRIPT_DIR / "items_v1.json"
OUT_MD      = EXP_DIR / "results" / "ghi_face_validity_summary.md"

CRITERIA = ["SCOPE", "LANGUAGE", "OVERPATHOLOGIZING"]
TIERS    = ["haiku", "sonnet", "opus"]


def main():
    if not STATE_JSONL.exists():
        OUT_MD.parent.mkdir(parents=True, exist_ok=True)
        OUT_MD.write_text("# GHI face-validity — no results yet\n")
        print("[analyze-ghi] no state file; wrote placeholder")
        return

    items_doc = json.loads(ITEMS_JSON.read_text())
    items = items_doc["items"]
    items_by_id = {it["id"]: it for it in items}

    # cell[(item_id, criterion, tier)] = (verdict, reason)
    cell = {}
    for line in STATE_JSONL.read_text().splitlines():
        if not line.strip(): continue
        d = json.loads(line)
        if d.get("_header"): continue
        if d.get("verdict"):
            cell[(d["item_id"], d["criterion"], d["tier"])] = (d["verdict"], d.get("reason",""))

    out = ["# GHI Face-Validity Audit — Summary",
           "",
           "Pre-registered protocol: `experiments/ghi_face_validity/protocol.md`.",
           "",
           f"Items audited: **{len(items)}** (`items_v1.json`).  Criteria: **{', '.join(CRITERIA)}** (King et al. 2020).  Models: **{', '.join(TIERS)}**.",
           "",
           f"Cells observed: {len(cell)} / {len(items)*len(CRITERIA)*len(TIERS)}",
           "",
           "## Per-item flag counts (9 judgments per item: 3 criteria × 3 models)",
           "",
           "Per protocol §4: ≥6/9 → revise; 3-5/9 → under review; ≤2/9 → provisionally retained.",
           "",
           "| Item | Domain | Label | Flags / 9 | Category |",
           "|---|---|---|---|---|",
    ]

    item_flags: dict[str, int] = {}
    item_by_criterion_flags: dict[str, dict[str, int]] = defaultdict(dict)
    for item in items:
        flags = 0
        for c in CRITERIA:
            c_flags = 0
            for t in TIERS:
                v, _ = cell.get((item["id"], c, t), ("",""))
                if v == "violates":
                    flags += 1
                    c_flags += 1
            item_by_criterion_flags[item["id"]][c] = c_flags
        item_flags[item["id"]] = flags
        if flags >= 6: cat = "**REVISE**"
        elif flags >= 3: cat = "under review"
        else: cat = "provisionally retained"
        out.append(f"| {item['id']} | {item['domain']} | {item['label']} | {flags} | {cat} |")
    out.append("")

    n_revise   = sum(1 for v in item_flags.values() if v >= 6)
    n_review   = sum(1 for v in item_flags.values() if 3 <= v < 6)
    n_retain   = sum(1 for v in item_flags.values() if v < 3)
    out.append(f"**Item triage:** revise = **{n_revise}** | under review = **{n_review}** | provisionally retained = **{n_retain}**")
    out.append("")

    # Per-criterion totals
    out.append("## Per-criterion flag rates")
    out.append("")
    out.append("Per protocol §4: ≥50% systemic; 20-49% significant; <20% adequate.")
    out.append("")
    out.append("| Criterion | Items flagged ≥1 (of 18) | Items flagged by ≥2/3 models (of 18) | Cells flagged (of 54) | % of cells |")
    out.append("|---|---|---|---|---|")
    for c in CRITERIA:
        any_flag = 0
        maj_flag = 0
        cell_flag = 0
        for item in items:
            t_flags = sum(1 for t in TIERS if cell.get((item["id"], c, t), ("",""))[0] == "violates")
            if t_flags >= 1: any_flag += 1
            if t_flags >= 2: maj_flag += 1
            cell_flag += t_flags
        pct = cell_flag / max(1, 3*len(items)) * 100
        verdict = "**systemic**" if pct >= 50 else ("significant" if pct >= 20 else "adequate")
        out.append(f"| {c} | {any_flag} | {maj_flag} | {cell_flag} / 54 | {pct:.1f}% ({verdict}) |")
    out.append("")

    # Cross-model agreement on flags
    out.append("## Cross-model flag agreement")
    out.append("")
    out.append("For each (item, criterion) cell where at least one model flagged, how many models agreed?")
    out.append("")
    agree = Counter()
    for item in items:
        for c in CRITERIA:
            flags = [cell.get((item["id"], c, t), ("",""))[0] == "violates" for t in TIERS]
            n = sum(flags)
            if n > 0:
                if n == 3: agree["unanimous 3/3"] += 1
                elif n == 2: agree["majority 2/3"] += 1
                else: agree["minority 1/3"] += 1
    out.append("| agreement | count |")
    out.append("|---|---|")
    for k in ["unanimous 3/3", "majority 2/3", "minority 1/3"]:
        out.append(f"| {k} | {agree.get(k,0)} |")
    out.append("")

    # Detailed flagged items with model reasons
    revise_items = sorted([(item_flags[it["id"]], it) for it in items if item_flags[it["id"]] >= 6], reverse=True, key=lambda x: x[0])
    review_items = sorted([(item_flags[it["id"]], it) for it in items if 3 <= item_flags[it["id"]] < 6], reverse=True, key=lambda x: x[0])

    if revise_items:
        out.append("## Items marked REVISE (≥6/9 flags) — per-criterion model reasons")
        out.append("")
        for _, item in revise_items:
            out.append(f"### {item['id']} — {item['label']} ({item['domain']})")
            out.append(f"> \"{item['stem']}\"")
            out.append("")
            for c in CRITERIA:
                cflags = item_by_criterion_flags[item["id"]][c]
                if cflags == 0: continue
                out.append(f"- **{c}** ({cflags}/3 flag):")
                for t in TIERS:
                    v, r = cell.get((item["id"], c, t), ("",""))
                    marker = "🚩 violates" if v == "violates" else ("ok" if v == "ok" else "—")
                    out.append(f"  - {t}: {marker}: \"{r}\"")
                out.append("")
    if review_items:
        out.append("## Items under review (3-5/9 flags) — summary")
        out.append("")
        for _, item in review_items:
            out.append(f"### {item['id']} — {item['label']} ({item['domain']})")
            out.append(f"> \"{item['stem']}\"")
            triggering = []
            for c in CRITERIA:
                if item_by_criterion_flags[item["id"]][c] > 0:
                    triggering.append(f"{c}({item_by_criterion_flags[item['id']][c]}/3)")
            out.append(f"- Triggering criteria: {', '.join(triggering) or 'none'}")
            for c in CRITERIA:
                cflags = item_by_criterion_flags[item["id"]][c]
                if cflags == 0: continue
                for t in TIERS:
                    v, r = cell.get((item["id"], c, t), ("",""))
                    if v == "violates":
                        out.append(f"  - {c}/{t}: \"{r}\"")
            out.append("")

    out.append("## Headline interpretation")
    out.append("")
    out.append(f"- The 18-item GHI draft yields {n_revise} item(s) flagged for revision (≥6/9), "
               f"{n_review} item(s) under review (3-5/9), and {n_retain} provisionally retained (≤2/9).")
    most_problematic_c = max(CRITERIA, key=lambda c: sum(1 for it in items
                                                          for t in TIERS
                                                          if cell.get((it["id"], c, t), ("",""))[0] == "violates"))
    out.append(f"- The criterion most often invoked across the 18 items is **{most_problematic_c}** "
               "— see the per-criterion table above for the per-cell rate.")
    out.append("")
    out.append("**No psychometric claim is made.** Per protocol §1, this audit identifies items to revise "
               "before Phase 2 expert panel review; it does not establish that the un-flagged items measure "
               "what they purport to measure.")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(out))
    print(f"[analyze-ghi] wrote {OUT_MD}")


if __name__ == "__main__":
    main()
