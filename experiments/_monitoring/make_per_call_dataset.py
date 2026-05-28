#!/usr/bin/env python3
"""
Per-call unified dataset extractor.

Scans every state-style JSONL under experiments/ and emits a single flat CSV
with one row per LLM call. Surface every variable that should be available
for later covariate analysis:

  experiment, file, model, tier, item_key,
  call_started_utc, call_started_kst,
  kst_window_idx, kst_window_offset_s,
  latency_s, cost_usd,
  input_tokens, cache_read_input_tokens, cache_creation_input_tokens, output_tokens,
  total_tokens, verdict, parse_error, error_short

For JSONL rows that pre-date the runner patch (no call_started_utc, no usage
fields surfaced), this script back-fills what it can:
  - call_started_utc inferred via the file's mtime if unavailable
    (approximate; better than nothing)
  - usage left at 0 if not in the record

Output:
  experiments/_monitoring/per_call_dataset.csv
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import pathlib
import zoneinfo

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT  = ROOT / "_monitoring" / "per_call_dataset.csv"
KST  = zoneinfo.ZoneInfo("Asia/Seoul")
ANCHOR = dt.datetime(2026, 5, 21, 3, 10, tzinfo=KST)
WINDOW_S = 5 * 3600


def window_info(utc_iso: str | None, mtime_fallback_utc: dt.datetime | None):
    """Return (kst_iso, window_idx, in_window_s) from a UTC ISO timestamp."""
    if utc_iso:
        try:
            t = dt.datetime.fromisoformat(utc_iso.replace("Z", "+00:00"))
        except ValueError:
            t = None
    else:
        t = None
    if t is None and mtime_fallback_utc is not None:
        t = mtime_fallback_utc
    if t is None:
        return "", -1, -1
    if t.tzinfo is None:
        t = t.replace(tzinfo=dt.timezone.utc)
    kst_t = t.astimezone(KST)
    kst_iso = kst_t.strftime("%Y-%m-%dT%H:%M:%S")
    if kst_t < ANCHOR:
        return kst_iso, -1, -1
    elapsed = (kst_t - ANCHOR).total_seconds()
    idx = int(elapsed // WINDOW_S)
    return kst_iso, idx, int(elapsed % WINDOW_S)


def each_jsonl():
    """Yield (experiment_name, file_path) tuples."""
    yield "llm_2rev_primary", ROOT/"llm_second_reviewer"   # dir; glob below
    yield "llm_2rev_sc",      ROOT/"llm_second_reviewer"/"sc_state.jsonl"
    # ghi_face glob below; sentinel here is the dir
    yield "ghi_face",         ROOT/"ghi_face_validity"
    yield "openalex_recheck", ROOT/"openalex_extension"/"llm_recheck_state.jsonl"
    yield "d3_design",        ROOT/"d3_design_audit"/"state.jsonl"
    yield "openalex_d5",      ROOT/"openalex_d5"/"llm_recheck_state.jsonl"
    yield "openalex_d1_d4",   ROOT/"openalex_d1_d4"/"llm_recheck_state.jsonl"


def extract_item_key(d: dict) -> str:
    for k in ("pmid", "openalex_id", "item_id"):
        if d.get(k):
            return str(d[k])
    return ""


def extract_tier_and_sample(d: dict) -> tuple[str, str]:
    t = d.get("tier", "")
    s = d.get("sample_idx", "")
    if s == "" or s is None:
        s_str = ""
    else:
        s_str = str(s)
    return t, s_str


def extract_criterion(d: dict) -> str:
    return d.get("criterion", "")


def file_mtime_utc(path: pathlib.Path) -> dt.datetime:
    return dt.datetime.fromtimestamp(path.stat().st_mtime, tz=dt.timezone.utc)


def collect_files():
    files = []
    primary_dir = ROOT / "llm_second_reviewer"
    for p in sorted(primary_dir.glob("run_*.jsonl")):
        if "aborted" in p.name:
            continue
        files.append(("llm_2rev_primary", p))
    # ghi_face: glob every state*.jsonl
    ghi_dir = ROOT / "ghi_face_validity"
    for p in sorted(ghi_dir.glob("state*.jsonl")):
        files.append(("ghi_face", p))
    for exp, target in each_jsonl():
        if exp in ("llm_2rev_primary", "ghi_face"):
            continue
        if target.is_file():
            files.append((exp, target))
    return files


def _call_key(d: dict) -> tuple:
    """Identify a unique call across the runner families."""
    pmid = d.get("pmid")
    if pmid is not None:
        return ("pmid", pmid, d.get("tier"), d.get("sample_idx"))
    if d.get("openalex_id") is not None:
        return ("oa", d.get("openalex_id"), d.get("tier"))
    if d.get("item_id") is not None:
        return ("ghi", d.get("item_id"), d.get("criterion"), d.get("tier"))
    return ("anon", id(d))


def main():
    rows = []
    for exp_name, path in collect_files():
        mt = file_mtime_utc(path)
        # Per-file dedup: a retry produces two records for the same key (error
        # then success). Keep the most recent successful record per key; if
        # none succeeded, keep the latest record (preserves last error context).
        latest_by_key: dict[tuple, dict] = {}
        succ_by_key: dict[tuple, dict] = {}
        order: list[tuple] = []
        with path.open() as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if d.get("_header"):
                    continue
                k = _call_key(d)
                if k not in latest_by_key:
                    order.append(k)
                latest_by_key[k] = d
                if bool(d.get("verdict")) or bool(d.get("design")):
                    succ_by_key[k] = d
        for k in order:
            d = succ_by_key.get(k, latest_by_key[k])
            kst_iso, w_idx, w_off = window_info(d.get("call_started_utc"), mt)
            u = d.get("usage") or {}
            in_t = int(u.get("input_tokens", 0) or 0)
            cr_t = int(u.get("cache_read_input_tokens", 0) or 0)
            cc_t = int(u.get("cache_creation_input_tokens", 0) or 0)
            out_t = int(u.get("output_tokens", 0) or 0)
            ts_src = "call_started_utc" if d.get("call_started_utc") else "file_mtime_fallback"
            # When backfilling from mtime, blank the window-position columns to
            # avoid suggesting that every pre-patch row landed at the same
            # window offset. timestamp_source still records that mtime was used.
            if ts_src == "file_mtime_fallback":
                kst_iso_out = ""
                w_idx_out = ""
                w_off_out = ""
            else:
                kst_iso_out = kst_iso
                w_idx_out = w_idx
                w_off_out = w_off
            rows.append({
                "experiment": exp_name,
                "file": str(path.relative_to(ROOT)),
                "model": d.get("model", ""),
                "tier": d.get("tier", ""),
                "item_key": extract_item_key(d),
                "criterion": extract_criterion(d),
                "sample_idx": d.get("sample_idx", ""),
                "call_started_utc": d.get("call_started_utc", ""),
                "call_started_kst": kst_iso_out,
                "kst_window_idx": w_idx_out,
                "kst_window_offset_s": w_off_out,
                "latency_s": d.get("latency_s", ""),
                "cost_usd": d.get("cost_usd", 0.0),
                "input_tokens": in_t,
                "cache_read_input_tokens": cr_t,
                "cache_creation_input_tokens": cc_t,
                "output_tokens": out_t,
                "total_tokens": in_t + cr_t + cc_t + out_t,
                "verdict": d.get("verdict", "") or d.get("design", ""),
                "parse_error": d.get("parse_error") or "",
                "error_short": (d.get("error") or "")[:120] if d.get("error") else "",
                "timestamp_source": ts_src,
            })

    fields = ["experiment","file","model","tier","item_key","criterion","sample_idx",
              "call_started_utc","call_started_kst","kst_window_idx","kst_window_offset_s",
              "latency_s","cost_usd",
              "input_tokens","cache_read_input_tokens","cache_creation_input_tokens","output_tokens","total_tokens",
              "verdict","parse_error","error_short","timestamp_source"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # Quick summary to stdout
    from collections import Counter, defaultdict
    by_exp = defaultdict(lambda: {"n":0, "tokens":0, "cost":0.0, "approx":0})
    for r in rows:
        e = r["experiment"]
        by_exp[e]["n"] += 1
        by_exp[e]["tokens"] += r["total_tokens"]
        by_exp[e]["cost"] += float(r["cost_usd"] or 0)
        if r["timestamp_source"] != "call_started_utc":
            by_exp[e]["approx"] += 1
    print(f"[per-call] wrote {len(rows)} rows to {OUT}")
    for e, s in by_exp.items():
        print(f"  {e}: n={s['n']}  tokens={s['tokens']:,}  cost=${s['cost']:.3f}  "
              f"timestamps_inferred={s['approx']}/{s['n']}")


if __name__ == "__main__":
    main()
