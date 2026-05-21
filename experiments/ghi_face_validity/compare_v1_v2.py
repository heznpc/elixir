#!/usr/bin/env python3
"""
Compare GHI v1 vs v2 face-validity audits.

Pre-registered: an item revised in v2 should drop from REVISE (≥6/9 flags)
to under-review (3-5/9) or retained (≤2/9). Items unchanged across versions
should have stable flag counts (sanity check).

Inputs:
  experiments/ghi_face_validity/items_v1.json
  experiments/ghi_face_validity/items_v2.json
  experiments/ghi_face_validity/state.jsonl       (v1 audit)
  experiments/ghi_face_validity/state_v2.jsonl    (v2 audit)

Outputs:
  experiments/results/ghi_face_validity_v1_v2_comparison.md
"""

from __future__ import annotations

import csv
import json
import pathlib
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent
EXP  = ROOT.parent
V1_ITEMS = ROOT / "items_v1.json"
V2_ITEMS = ROOT / "items_v2.json"
V1_STATE = ROOT / "state.jsonl"
V2_STATE = ROOT / "state_v2.jsonl"
OUT_MD   = EXP / "results" / "ghi_face_validity_v1_v2_comparison.md"

CRITERIA = ["SCOPE", "LANGUAGE", "OVERPATHOLOGIZING"]
TIERS    = ["haiku", "sonnet", "opus"]


def load_cells(path: pathlib.Path) -> dict[tuple[str, str, str], str]:
    """(item_id, criterion, tier) -> verdict"""
    if not path.exists():
        return {}
    out = {}
    for line in path.read_text().splitlines():
        if not line.strip(): continue
        try: d = json.loads(line)
        except json.JSONDecodeError: continue
        if d.get("_header"): continue
        if d.get("verdict"):
            out[(d["item_id"], d["criterion"], d["tier"])] = d["verdict"]
    return out


def per_item_flag(cells, item_ids) -> dict[str, dict]:
    """For each item return {n_flags, per_criterion: {SCOPE: n, ...}}"""
    res = {}
    for iid in item_ids:
        flags = 0
        per_c = {}
        for c in CRITERIA:
            cf = sum(1 for t in TIERS if cells.get((iid, c, t)) == "violates")
            per_c[c] = cf
            flags += cf
        res[iid] = {"flags": flags, "per_criterion": per_c}
    return res


def category(flags: int) -> str:
    if flags >= 6: return "REVISE"
    if flags >= 3: return "under review"
    return "retained"


def main():
    v1_items = json.loads(V1_ITEMS.read_text())["items"]
    v2_items = json.loads(V2_ITEMS.read_text())["items"]
    v1_by_id = {it["id"]: it for it in v1_items}
    v2_by_id = {it["id"]: it for it in v2_items}

    v1_cells = load_cells(V1_STATE)
    v2_cells = load_cells(V2_STATE)
    ids = sorted(set(list(v1_by_id) + list(v2_by_id)),
                 key=lambda x: int(x.split("-")[-1]))

    v1_flags = per_item_flag(v1_cells, ids)
    v2_flags = per_item_flag(v2_cells, ids)

    out = ["# GHI v1 → v2 Comparison",
           "",
           f"v1 cells observed: {len(v1_cells)}. v2 cells observed: {len(v2_cells)}.",
           ""]

    revised_ids = [it["id"] for it in v2_items if "revised_from_v1" in it]
    out.append(f"Items revised in v2 ({len(revised_ids)}): {', '.join(revised_ids)}")
    out.append("")

    out.append("## Per-item flag count (out of 9) and category")
    out.append("")
    out.append("| Item | Domain | v1 flags / cat | v2 flags / cat | Δ (v2 − v1) | Revised? |")
    out.append("|---|---|---|---|---|---|")
    for iid in ids:
        dom = v2_by_id.get(iid, v1_by_id.get(iid, {})).get("domain","?")
        v1n = v1_flags.get(iid, {}).get("flags", 0)
        v2n = v2_flags.get(iid, {}).get("flags", 0)
        delta = v2n - v1n
        v1c = category(v1n); v2c = category(v2n)
        revised = "**yes**" if iid in revised_ids else ""
        out.append(f"| {iid} | {dom} | {v1n} ({v1c}) | {v2n} ({v2c}) | {delta:+d} | {revised} |")
    out.append("")

    # Per-criterion comparison on revised items only
    out.append("## Per-criterion comparison on revised items")
    out.append("")
    out.append("| Item | Criterion | v1 flags | v2 flags | Δ |")
    out.append("|---|---|---|---|---|")
    for iid in revised_ids:
        for c in CRITERIA:
            v1n = v1_flags.get(iid, {}).get("per_criterion", {}).get(c, 0)
            v2n = v2_flags.get(iid, {}).get("per_criterion", {}).get(c, 0)
            d = v2n - v1n
            out.append(f"| {iid} | {c} | {v1n}/3 | {v2n}/3 | {d:+d} |")
    out.append("")

    # Sanity check: unrevised items
    unrevised = [iid for iid in ids if iid not in revised_ids]
    out.append("## Sanity check: unrevised items")
    out.append("")
    out.append("Items NOT revised between v1 and v2 should have nearly identical flag counts; "
               "any large divergence indicates LLM-judge instability rather than item-level signal.")
    out.append("")
    out.append("| Item | v1 flags | v2 flags | Δ |")
    out.append("|---|---|---|---|")
    instability_flagged = 0
    for iid in unrevised:
        v1n = v1_flags.get(iid, {}).get("flags", 0)
        v2n = v2_flags.get(iid, {}).get("flags", 0)
        d = v2n - v1n
        if abs(d) >= 3:
            instability_flagged += 1
        out.append(f"| {iid} | {v1n} | {v2n} | {d:+d} |")
    out.append("")
    out.append(f"Items with |Δ| ≥ 3 among unrevised: **{instability_flagged}** of {len(unrevised)}.")
    out.append("")

    # Triage summary
    out.append("## Triage summary")
    out.append("")
    out.append("| Category | v1 | v2 | Δ |")
    out.append("|---|---|---|---|")
    for cat in ("REVISE", "under review", "retained"):
        n1 = sum(1 for iid in ids if category(v1_flags.get(iid, {}).get("flags", 0)) == cat)
        n2 = sum(1 for iid in ids if category(v2_flags.get(iid, {}).get("flags", 0)) == cat)
        out.append(f"| {cat} | {n1} | {n2} | {n2-n1:+d} |")
    out.append("")

    # Headline
    out.append("## Headline")
    out.append("")
    n_revise_v1 = sum(1 for iid in ids if category(v1_flags.get(iid, {}).get("flags", 0)) == "REVISE")
    n_revise_v2 = sum(1 for iid in ids if category(v2_flags.get(iid, {}).get("flags", 0)) == "REVISE")
    n_revised_dropped = sum(1 for iid in revised_ids
                              if category(v1_flags.get(iid, {}).get("flags", 0)) == "REVISE"
                              and category(v2_flags.get(iid, {}).get("flags", 0)) != "REVISE")
    out.append(f"- v1 had {n_revise_v1} items in REVISE; v2 has {n_revise_v2}. Net drop: {n_revise_v1 - n_revise_v2:+d}.")
    out.append(f"- Of the {len(revised_ids)} items rewritten with explicit distress/impairment/escalation/loss-of-control markers, "
               f"**{n_revised_dropped} dropped out of the REVISE category** in v2.")
    if n_revised_dropped == len(revised_ids):
        out.append("- The marker-addition fix works for every revised item. The remaining v2 REVISE items (if any) are different items, not the same five.")
    elif n_revised_dropped >= len(revised_ids) // 2:
        out.append("- The marker-addition fix works for most revised items but not all. Items that did not drop need different revision strategies (e.g., LANGUAGE criterion may also be involved).")
    else:
        out.append("- The marker-addition fix is insufficient. Even with explicit distress/impairment/escalation markers, the revised stems still cluster in REVISE; the SCOPE+OVERPATHOLOGIZING criteria may require a fundamentally different framing approach.")
    out.append("")
    out.append("**No psychometric claim is made**, per protocol §1.")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(out))
    print(f"[compare] wrote {OUT_MD}")


if __name__ == "__main__":
    main()
