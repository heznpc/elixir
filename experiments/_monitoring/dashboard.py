#!/usr/bin/env python3
"""
Single-shot dashboard summary for the LLM-experiment infrastructure.

Reads every `state.jsonl`, `sc_state.jsonl`, `llm_recheck_state.jsonl`, and
`run_*_<tier>.jsonl` under `experiments/`, extracts token usage and absolute
timestamps (where available), and emits one summary line per experiment plus
a global rollup.

Designed to be safe to call from a `while true; sleep N` Monitor loop —
exits 0 on every call, emits to stdout only.

Output format:
  <ISO timestamp>  exp=<name>  calls=<n>  in=<sum_in>k  cache_r=<sum_cr>k  out=<sum_out>k  cost=$<sum>  q_retries=<n>  ages=<oldest..newest>
  <ISO timestamp>  global  calls=<n>  tokens=<sum>k  cost=$<sum>  window=<idx>  in_window_s=<s>  remain_s=<s>
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys
import zoneinfo
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
KST = zoneinfo.ZoneInfo("Asia/Seoul")
ANCHOR = dt.datetime(2026, 5, 21, 3, 10, tzinfo=KST)
WINDOW_S = 5 * 3600


def window_state(now_kst: dt.datetime | None = None):
    """Return (window_idx, in_window_s, remain_s)."""
    if now_kst is None:
        now_kst = dt.datetime.now(KST)
    if now_kst < ANCHOR:
        return -1, 0, int((ANCHOR - now_kst).total_seconds())
    elapsed = (now_kst - ANCHOR).total_seconds()
    idx = int(elapsed // WINDOW_S)
    in_w = int(elapsed % WINDOW_S)
    return idx, in_w, WINDOW_S - in_w


def scan_jsonl(path: pathlib.Path) -> dict:
    """Aggregate one JSONL file: total calls (with verdict), token sums, cost, latency range."""
    s = {
        "path": str(path.relative_to(ROOT)),
        "calls": 0,
        "errored": 0,
        "input_tokens": 0,
        "cache_read_tokens": 0,
        "cache_create_tokens": 0,
        "output_tokens": 0,
        "cost_usd": 0.0,
        "latency_sum_s": 0.0,
        "header_started_utc": None,
        "started_utcs": [],   # if call_started_utc is present
        "models": defaultdict(int),
        "verdicts": defaultdict(int),
    }
    try:
        with path.open() as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if d.get("_header"):
                    s["header_started_utc"] = d.get("started_utc")
                    continue
                # Success only:
                ok = bool(d.get("verdict"))
                if not ok:
                    s["errored"] += 1
                    continue
                s["calls"] += 1
                u = d.get("usage") or {}
                s["input_tokens"]      += int(u.get("input_tokens", 0) or 0)
                s["cache_read_tokens"] += int(u.get("cache_read_input_tokens", 0) or 0)
                s["cache_create_tokens"] += int(u.get("cache_creation_input_tokens", 0) or 0)
                s["output_tokens"]     += int(u.get("output_tokens", 0) or 0)
                s["cost_usd"]          += float(d.get("cost_usd", 0.0) or 0)
                s["latency_sum_s"]     += float(d.get("latency_s", 0.0) or 0)
                if d.get("call_started_utc"):
                    s["started_utcs"].append(d["call_started_utc"])
                if d.get("model"):
                    s["models"][d["model"]] += 1
                v = d.get("verdict", "")
                if v:
                    s["verdicts"][v] += 1
    except OSError:
        pass
    return s


def fmt_k(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}k"
    return str(n)


def main():
    exps = {
        "llm_2rev_primary": list((ROOT/"llm_second_reviewer").glob("run_*.jsonl")),
        "llm_2rev_sc":      [ROOT/"llm_second_reviewer"/"sc_state.jsonl"],
        # Glob ghi_face state files so future versioned re-audits (state_v2.jsonl, ...) are
        # picked up automatically without code edits.
        "ghi_face":         list((ROOT/"ghi_face_validity").glob("state*.jsonl")),
        "openalex_recheck": [ROOT/"openalex_extension"/"llm_recheck_state.jsonl"],
    }
    # Filter the primary-run list to exclude aborted/sidecar files
    exps["llm_2rev_primary"] = [
        p for p in exps["llm_2rev_primary"]
        if p.suffix == ".jsonl" and "aborted" not in p.name
    ]

    now_kst = dt.datetime.now(KST)
    now_iso = now_kst.strftime("%H:%M:%S")
    w_idx, in_w, remain = window_state(now_kst)
    window_start = (ANCHOR + dt.timedelta(seconds=WINDOW_S*w_idx)).strftime("%H:%M") if w_idx >= 0 else "—"
    window_end   = (ANCHOR + dt.timedelta(seconds=WINDOW_S*(w_idx+1))).strftime("%H:%M") if w_idx >= 0 else "—"

    global_calls = 0
    global_input = 0
    global_cr = 0
    global_cc = 0
    global_out = 0
    global_cost = 0.0
    global_errored = 0

    for exp_name, paths in exps.items():
        e_calls = e_in = e_cr = e_cc = e_out = e_err = 0
        e_cost = 0.0
        for p in paths:
            if not p.exists():
                continue
            s = scan_jsonl(p)
            e_calls += s["calls"]
            e_in    += s["input_tokens"]
            e_cr    += s["cache_read_tokens"]
            e_cc    += s["cache_create_tokens"]
            e_out   += s["output_tokens"]
            e_cost  += s["cost_usd"]
            e_err   += s["errored"]
        global_calls += e_calls
        global_input += e_in
        global_cr    += e_cr
        global_cc    += e_cc
        global_out   += e_out
        global_cost  += e_cost
        global_errored += e_err
        if e_calls > 0 or e_err > 0:
            total = e_in + e_cr + e_cc + e_out
            print(f"{now_iso}KST  exp={exp_name:<20}  calls={e_calls}  err={e_err}  "
                  f"in={fmt_k(e_in)}  cache_r={fmt_k(e_cr)}  cache_c={fmt_k(e_cc)}  "
                  f"out={fmt_k(e_out)}  tot={fmt_k(total)}  cost=${e_cost:.3f}",
                  flush=True)

    g_total = global_input + global_cr + global_cc + global_out
    print(f"{now_iso}KST  global   calls={global_calls}  err={global_errored}  "
          f"tokens={fmt_k(g_total)}  cost=${global_cost:.3f}  "
          f"window=[{w_idx}] {window_start}->{window_end}  "
          f"in_window={in_w//60}m  remain={remain//60}m",
          flush=True)


if __name__ == "__main__":
    main()
