#!/usr/bin/env python3
"""
GHI face-validity runner — 18 items x 3 criteria x 3 models = 162 calls.

Pre-registered: experiments/ghi_face_validity/protocol.md.

Quota-resilient (same pattern as experiments/llm_second_reviewer/run_self_consistency.py):
  - Persists per-call state to state.jsonl with success flag.
  - On restart, skips (item_id, criterion, tier) triples already recorded as success.
  - On a quota-style CLI error, sleeps until the next 5-hour KST window
    boundary (anchored at 2026-05-21 03:10 KST) + 30 s buffer, then retries.
  - Up to 8 quota-sleep cycles.

Outputs:
  experiments/ghi_face_validity/state.jsonl
  experiments/data/processed/ghi_face_validity_results.csv
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import datetime as dt
import hashlib
import json
import pathlib
import re
import subprocess
import threading
import time
import zoneinfo

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
EXP_DIR    = SCRIPT_DIR.parent
# Defaults; can be overridden via --items / --state / --out-csv
ITEMS_JSON = SCRIPT_DIR / "items_v1.json"
CRIT_TXT   = SCRIPT_DIR / "criteria_v1.txt"
PROMPT_TXT = SCRIPT_DIR / "prompt_v1.txt"
STATE_JSONL = SCRIPT_DIR / "state.jsonl"
OUT_CSV    = EXP_DIR / "data" / "processed" / "ghi_face_validity_results.csv"

TIERS = [
    ("haiku",  "claude-haiku-4-5"),
    ("sonnet", "claude-sonnet-4-6"),
    ("opus",   "claude-opus-4-7"),
]
CRITERIA = ["SCOPE", "LANGUAGE", "OVERPATHOLOGIZING"]

PER_CALL_TO    = 90
QUOTA_BUFFER_S = 30
WINDOW_S       = 5 * 3600
KST = zoneinfo.ZoneInfo("Asia/Seoul")
QUOTA_ANCHOR = dt.datetime(2026, 5, 21, 3, 10, tzinfo=KST)

CLI_SYSTEM_PROMPT = (
    "You output exactly one JSON object and nothing else. "
    "No prose, no preamble, no markdown code fence, no internal reasoning. "
    "Minimize tokens."
)

QUOTA_PATTERNS = [
    "rate_limit", "rate limit", "rate-limited", "rate-limit",
    "quota", "exceeded", "429",
    "usage_limit", "tokens_limit", "tokens exhausted",
    "limit reached", "too many requests",
]


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def next_window_start_utc() -> dt.datetime:
    now = dt.datetime.now(KST)
    if now <= QUOTA_ANCHOR:
        nxt = QUOTA_ANCHOR
    else:
        elapsed = (now - QUOTA_ANCHOR).total_seconds()
        n_windows = int(elapsed // WINDOW_S) + 1
        nxt = QUOTA_ANCHOR + dt.timedelta(seconds=WINDOW_S * n_windows)
    return nxt.astimezone(dt.timezone.utc)


def sleep_until_next_window(reason: str):
    nxt = next_window_start_utc() + dt.timedelta(seconds=QUOTA_BUFFER_S)
    now = dt.datetime.now(dt.timezone.utc)
    wait_s = max(60, int((nxt - now).total_seconds()))
    end_kst = nxt.astimezone(KST).strftime("%H:%M:%S KST")
    print(f"[quota-sleep] reason={reason!r}  sleeping {wait_s}s until {end_kst}", flush=True)
    while wait_s > 0:
        step = min(300, wait_s)
        time.sleep(step)
        wait_s -= step


def looks_like_quota(stderr: str, stdout: str, retcode: int) -> bool:
    blob = (stderr + " " + stdout).lower()
    return any(p in blob for p in QUOTA_PATTERNS)


def build_prompt(item: dict, criterion: str, criteria_text: str, template: str) -> str:
    return (template
            .replace("<<CRITERIA_VERBATIM>>", criteria_text)
            .replace("<<CRITERION_NAME>>", criterion)
            .replace("<<ITEM_ID>>", item["id"])
            .replace("<<ITEM_DOMAIN>>", item["domain"])
            .replace("<<ITEM_LABEL>>", item["label"])
            .replace("<<ITEM_STEM>>", item["stem"]))


def call_cli_once(model: str, prompt: str) -> tuple[dict | None, str, int]:
    cmd = [
        "claude", "--print", "--no-session-persistence",
        "--model", model,
        "--output-format", "json",
        "--system-prompt", CLI_SYSTEM_PROMPT,
        "--tools", "",
        "--disable-slash-commands",
        prompt,
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=PER_CALL_TO)
    except subprocess.TimeoutExpired:
        return None, "timeout", 124
    if r.returncode != 0:
        return None, r.stderr or r.stdout, r.returncode
    try:
        return json.loads(r.stdout), r.stderr, r.returncode
    except json.JSONDecodeError:
        return None, r.stdout[:500], r.returncode


def parse_verdict(text: str, criterion: str) -> dict:
    import sys as _sys, pathlib as _p
    _sys.path.insert(0, str(_p.Path(__file__).resolve().parent.parent))
    from _lib.parse_json import extract_first_balanced_object
    raw = extract_first_balanced_object(text or "")
    if not raw:
        return {"verdict": "", "criterion": criterion, "reason": "", "parse_error": "no_json"}
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as e:
        return {"verdict": "", "criterion": criterion, "reason": "", "parse_error": f"json_decode:{e}"}
    v = obj.get("verdict", "")
    if v not in ("violates", "ok"):
        return {"verdict": "", "criterion": criterion, "reason": obj.get("reason",""), "parse_error": f"verdict_not_in_set:{v}"}
    return {"verdict": v, "criterion": criterion, "reason": str(obj.get("reason",""))[:200]}


def load_done(state_path: pathlib.Path) -> set:
    done = set()
    if not state_path.exists():
        return done
    with state_path.open() as f:
        for line in f:
            if not line.strip(): continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError: continue
            if d.get("_header"): continue
            if d.get("verdict"):
                done.add((d["item_id"], d["criterion"], d["tier"]))
    return done


def main():
    global ITEMS_JSON, STATE_JSONL, OUT_CSV
    ap = argparse.ArgumentParser()
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--max-quota-retries", type=int, default=8)
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--items", default=str(ITEMS_JSON),
                    help="Path to items JSON (default: items_v1.json).")
    ap.add_argument("--state", default=str(STATE_JSONL),
                    help="Path to state JSONL (default: state.jsonl).")
    ap.add_argument("--out-csv", default=str(OUT_CSV),
                    help="Path to flat CSV output.")
    args = ap.parse_args()

    items_path = pathlib.Path(args.items)
    state_path = pathlib.Path(args.state)
    out_csv = pathlib.Path(args.out_csv)
    # Reassign module globals so the helper closures pick up the override
    ITEMS_JSON = items_path
    STATE_JSONL = state_path
    OUT_CSV = out_csv

    items_doc = json.loads(items_path.read_text())
    items = items_doc["items"]
    criteria_text = CRIT_TXT.read_text()
    template = PROMPT_TXT.read_text()
    prompt_hash = sha256(template)
    criteria_hash = sha256(criteria_text)
    items_hash = sha256(ITEMS_JSON.read_text())

    if args.fresh and STATE_JSONL.exists():
        STATE_JSONL.unlink()
    done = load_done(STATE_JSONL)
    n_total = len(items) * len(CRITERIA) * len(TIERS)
    print(f"[plan] items={len(items)} criteria={len(CRITERIA)} tiers={len(TIERS)}  total={n_total}")
    print(f"[plan] resuming with {len(done)} calls already completed")
    print(f"[plan] hashes: prompt={prompt_hash[:12]} criteria={criteria_hash[:12]} items={items_hash[:12]}")

    if not STATE_JSONL.exists():
        with STATE_JSONL.open("w") as f:
            f.write(json.dumps({
                "_header": True,
                "prompt_hash": prompt_hash,
                "criteria_hash": criteria_hash,
                "items_hash": items_hash,
                "tiers": TIERS,
                "criteria": CRITERIA,
                "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            }) + "\n")

    state_f = STATE_JSONL.open("a")
    state_lock = threading.Lock()
    quota_lock = threading.Lock()
    quota_retries = [0]
    cost_lock = threading.Lock()
    total_cost = [0.0]
    n_done = [0]
    n_skip = 0
    started = time.time()

    def write_state(rec: dict, cost_delta: float = 0.0):
        with state_lock:
            state_f.write(json.dumps(rec) + "\n"); state_f.flush()
        if cost_delta:
            with cost_lock: total_cost[0] += cost_delta
        with cost_lock:
            n_done[0] += 1
            if n_done[0] % 20 == 0:
                elapsed = time.time() - started
                print(f"  done={n_done[0]} skip={n_skip} total={n_total}  "
                      f"cost=${total_cost[0]:.3f}  elapsed={elapsed:.0f}s  "
                      f"quota_retries={quota_retries[0]}", flush=True)

    def maybe_quota_sleep(reason: str) -> bool:
        with quota_lock:
            if quota_retries[0] >= args.max_quota_retries:
                return False
            quota_retries[0] += 1
            n = quota_retries[0]
        sleep_until_next_window(f"quota_retry_{n}: {reason[:120]}")
        return True

    def do_one(item, criterion, tier, model):
        prompt = build_prompt(item, criterion, criteria_text, template)
        while True:
            call_started_utc = dt.datetime.now(dt.timezone.utc).isoformat()
            t0 = time.time()
            resp, stderr, rc = call_cli_once(model, prompt)
            latency = time.time() - t0
            if resp is None:
                if looks_like_quota(stderr, "", rc) and maybe_quota_sleep(f"rc={rc} stderr={stderr[:120]}"):
                    continue
                rec = {"item_id": item["id"], "criterion": criterion, "tier": tier, "model": model,
                       "prompt_hash": prompt_hash, "criteria_hash": criteria_hash,
                       "verdict": "", "reason": "", "parse_error": f"call_failed:rc={rc}",
                       "error": stderr[:200], "latency_s": round(latency,2),
                       "cost_usd": 0.0, "raw": "",
                       "call_started_utc": call_started_utc, "usage": {}}
                write_state(rec)
                return
            text = resp.get("result", "") or ""
            if resp.get("is_error"):
                err_obj = resp.get("error") or {}
                err_blob = json.dumps(err_obj).lower()
                if any(p in err_blob for p in QUOTA_PATTERNS) and maybe_quota_sleep(f"is_error err={err_blob[:120]}"):
                    continue
                rec = {"item_id": item["id"], "criterion": criterion, "tier": tier, "model": model,
                       "prompt_hash": prompt_hash, "criteria_hash": criteria_hash,
                       "verdict": "", "reason": "",
                       "parse_error": "is_error_true",
                       "error": json.dumps(err_obj)[:200],
                       "latency_s": round(latency,2),
                       "cost_usd": float(resp.get("total_cost_usd",0.0)), "raw": text[:500],
                       "call_started_utc": call_started_utc, "usage": resp.get("usage", {})}
                write_state(rec)
                return
            parsed = parse_verdict(text, criterion)
            cost = round(float(resp.get("total_cost_usd",0.0)),6)
            rec = {"item_id": item["id"], "criterion": criterion, "tier": tier, "model": model,
                   "prompt_hash": prompt_hash, "criteria_hash": criteria_hash,
                   **parsed,
                   "error": None,
                   "latency_s": round(latency,2),
                   "cost_usd": cost,
                   "usage": resp.get("usage", {}),
                   "raw": text[:1500],
                   "call_started_utc": call_started_utc}
            write_state(rec, cost_delta=cost)
            return

    tasks = []
    for item in items:
        for criterion in CRITERIA:
            for tier, model in TIERS:
                key = (item["id"], criterion, tier)
                if key in done:
                    n_skip += 1
                    continue
                tasks.append((item, criterion, tier, model))

    print(f"[plan] tasks to submit (after resume skip)={len(tasks)}  concurrency={args.concurrency}")
    if not tasks:
        print("[done] nothing to do")
    else:
        with cf.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            list(pool.map(lambda t: do_one(*t), tasks))

    state_f.close()
    print(f"[done] new calls={n_done[0]} skipped={n_skip} total_target={n_total} "
          f"cost(new)=${total_cost[0]:.3f} quota_retries={quota_retries[0]}")

    # Build flat CSV. Dedup on (item_id, criterion, tier) so a retry after an
    # error doesn't produce two rows for the same call.
    import sys as _sys, pathlib as _p
    _sys.path.insert(0, str(_p.Path(__file__).resolve().parent.parent))
    from _lib.jsonl_dedup import dedup_state_records, is_success_verdict, key_item_criterion_tier

    rows_raw = []
    with STATE_JSONL.open() as f:
        for line in f:
            if not line.strip(): continue
            try: d = json.loads(line)
            except json.JSONDecodeError: continue
            if d.get("_header"): continue
            rows_raw.append(d)
    rows = dedup_state_records(rows_raw, key_item_criterion_tier, is_success_verdict)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item_id","criterion","tier","model","verdict","reason",
                    "parse_error","error","latency_s","cost_usd"])
        for d in rows:
            w.writerow([
                d.get("item_id"), d.get("criterion"), d.get("tier"), d.get("model"),
                d.get("verdict",""), (d.get("reason") or "")[:300],
                d.get("parse_error") or "",
                (d.get("error") or "")[:200] if d.get("error") else "",
                d.get("latency_s",""), d.get("cost_usd",""),
            ])
    print(f"[done] wrote {OUT_CSV}")


if __name__ == "__main__":
    main()
