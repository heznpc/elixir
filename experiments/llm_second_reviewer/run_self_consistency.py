#!/usr/bin/env python3
"""
Self-consistency follow-up run on the convergent-disagreement subset.

Pre-registered: protocol.md §6 (M-A deferred) — triggered because all three
primary tiers landed in the 0.40 < kappa <= 0.60 moderate-IRR band.

Sample: 59 papers in experiments/llm_second_reviewer/convergent_disagreements.csv
        — the subset where all three LLMs (Haiku 4-5, Sonnet 4-6, Opus 4-7)
        agree among themselves but disagree with the heuristic.

Calls: 59 papers x 3 tiers x 3 samples = 531.

Quota resilience: this runner persists per-call state to
`sc_state.jsonl`. On a fresh start it skips (pmid, tier, sample_idx)
triples already recorded as success. On a quota-style CLI error it sleeps
until the next 5-hour KST window boundary (anchored at 2026-05-21 03:10
KST) plus a 30 s buffer, then resumes.

Outputs:
  experiments/llm_second_reviewer/sc_state.jsonl              one line per call (header + records)
  experiments/data/processed/llm_second_reviewer_sc.csv       flat per-(pmid,tier,sample) table

Usage:
  python3 experiments/llm_second_reviewer/run_self_consistency.py
  python3 experiments/llm_second_reviewer/run_self_consistency.py --resume   # default behaviour
  python3 experiments/llm_second_reviewer/run_self_consistency.py --fresh    # ignore prior state
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import threading
import time
import zoneinfo

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
EXP_DIR    = SCRIPT_DIR.parent
RAW_CSV    = EXP_DIR / "data" / "raw" / "pubmed_results.csv"
SUB_CSV    = SCRIPT_DIR / "convergent_disagreements.csv"
CRIT_TXT   = SCRIPT_DIR / "criteria_v1.txt"
PROMPT_TXT = SCRIPT_DIR / "prompt_v1.txt"
STATE_JSONL = SCRIPT_DIR / "sc_state.jsonl"
OUT_CSV    = EXP_DIR / "data" / "processed" / "llm_second_reviewer_sc.csv"

TIERS = [
    ("haiku",  "claude-haiku-4-5"),
    ("sonnet", "claude-sonnet-4-6"),
    ("opus",   "claude-opus-4-7"),
]
N_SAMPLES   = 3
PER_CALL_TO = 90    # seconds
QUOTA_BUFFER_S = 30
WINDOW_S    = 5 * 3600
# Quota window anchor: 2026-05-21 03:10 KST. Windows reset at anchor + 5h * k.
KST = zoneinfo.ZoneInfo("Asia/Seoul")
QUOTA_ANCHOR = dt.datetime(2026, 5, 21, 3, 10, tzinfo=KST)

CLI_SYSTEM_PROMPT = (
    "You output exactly one JSON object and nothing else. "
    "No prose, no preamble, no markdown code fence, no internal reasoning. "
    "Minimize tokens."
)

# Patterns that indicate a quota / rate-limit failure (case-insensitive in stderr+stdout).
QUOTA_PATTERNS = [
    "rate_limit", "rate limit", "rate-limited", "rate-limit",
    "quota", "exceeded", "429",
    "usage_limit", "tokens_limit", "tokens exhausted",
    "limit reached", "too many requests",
]


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Quota window helper
# ---------------------------------------------------------------------------
def next_window_start_utc() -> dt.datetime:
    """Return the next quota window boundary in UTC."""
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
    print(f"[quota-sleep] reason={reason!r}  sleeping {wait_s}s until {end_kst}",
          flush=True)
    while wait_s > 0:
        step = min(300, wait_s)
        time.sleep(step)
        wait_s -= step


# ---------------------------------------------------------------------------
# Prompt assembly + parsing (mirrors run.py)
# ---------------------------------------------------------------------------
def build_prompt(paper: dict, criteria: str, prompt_template: str) -> str:
    return (prompt_template
            .replace("<<CRITERIA_VERBATIM>>", criteria)
            .replace("<<PMID>>",     paper["pmid"])
            .replace("<<YEAR>>",     paper["year"])
            .replace("<<JOURNAL>>",  paper["journal"])
            .replace("<<TITLE>>",    paper["title"])
            .replace("<<ABSTRACT>>", paper.get("abstract", "")[:1800]))


_VERDICTS = {"Include", "Maybe", "Exclude"}
_DOMAINS  = {"D1","D2","D3","D4","D5","D6","Cross-domain"}

def parse_verdict(text: str) -> dict:
    m = re.search(r"\{[^{}]*\"verdict\".*?\}", text, re.DOTALL) or re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return {"verdict":"","domains":[],"reason":"","parse_error":"no_json_object"}
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        return {"verdict":"","domains":[],"reason":"","parse_error":f"json_decode:{e}"}
    v = obj.get("verdict","")
    d = obj.get("domains",[]) or []
    r = obj.get("reason","")
    if v not in _VERDICTS:
        return {"verdict":"","domains":d,"reason":r,"parse_error":f"verdict_not_in_set:{v}"}
    if not isinstance(d, list): d = []
    d = [x for x in d if x in _DOMAINS]
    return {"verdict":v,"domains":d,"reason":str(r)[:200]}


def looks_like_quota(stderr: str, stdout: str, retcode: int) -> bool:
    blob = (stderr + " " + stdout).lower()
    if any(p in blob for p in QUOTA_PATTERNS):
        return True
    # Some CLI quota failures bubble up via stdout JSON
    if "\"is_error\":true" in stdout.replace(" ", "").lower() and "rate" in blob:
        return True
    return False


def call_cli_once(model: str, prompt: str) -> tuple[dict | None, str, int]:
    """Return (parsed_json_or_None, stderr_text, returncode)."""
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


# ---------------------------------------------------------------------------
# State persistence
# ---------------------------------------------------------------------------
def load_done(state_path: pathlib.Path) -> set:
    done = set()
    if not state_path.exists():
        return done
    with state_path.open() as f:
        for line in f:
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("_header"):
                continue
            if d.get("verdict"):  # success only
                done.add((d["pmid"], d["tier"], d["sample_idx"]))
    return done


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fresh", action="store_true", help="Ignore prior state file (default: resume).")
    ap.add_argument("--max-quota-retries", type=int, default=8,
                    help="Maximum number of quota-sleep cycles before giving up.")
    ap.add_argument("--concurrency", type=int, default=4,
                    help="Worker threads (each issues independent CLI subprocess).")
    args = ap.parse_args()

    criteria        = CRIT_TXT.read_text()
    prompt_template = PROMPT_TXT.read_text()
    prompt_hash     = sha256(prompt_template)
    criteria_hash   = sha256(criteria)

    # Load paper metadata for the subset
    sub = {r["pmid"]: r for r in csv.DictReader(SUB_CSV.open())}
    raw = {r["pmid"]: r for r in csv.DictReader(RAW_CSV.open())}
    papers = []
    for pmid in sub:
        if pmid not in raw:
            print(f"[warn] subset pmid {pmid} not in raw CSV; skipping")
            continue
        papers.append(raw[pmid])
    print(f"[plan] subset n_papers={len(papers)}  tiers={[t for t,_ in TIERS]}  samples={N_SAMPLES}")
    print(f"[plan] total calls expected={len(papers)*len(TIERS)*N_SAMPLES}")

    if args.fresh and STATE_JSONL.exists():
        STATE_JSONL.unlink()
    done = load_done(STATE_JSONL)
    print(f"[plan] resuming with {len(done)} calls already completed")

    # Append-mode state file; write header if fresh
    if not STATE_JSONL.exists():
        with STATE_JSONL.open("w") as f:
            f.write(json.dumps({
                "_header": True,
                "prompt_hash": prompt_hash,
                "criteria_hash": criteria_hash,
                "tiers": TIERS,
                "n_samples": N_SAMPLES,
                "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            }) + "\n")

    state_f = STATE_JSONL.open("a")
    state_lock = threading.Lock()
    quota_retries = [0]  # boxed to mutate from threads
    quota_lock = threading.Lock()
    total_cost = [0.0]
    cost_lock = threading.Lock()
    n_done = [0]
    n_skip = 0
    n_total = len(papers) * len(TIERS) * N_SAMPLES
    started = time.time()

    def write_state(rec: dict, cost_delta: float = 0.0):
        with state_lock:
            state_f.write(json.dumps(rec) + "\n"); state_f.flush()
        if cost_delta:
            with cost_lock:
                total_cost[0] += cost_delta
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

    def do_one(paper, tier, model, s):
        prompt = build_prompt(paper, criteria, prompt_template)
        while True:
            call_started_utc = dt.datetime.now(dt.timezone.utc).isoformat()
            t0 = time.time()
            resp, stderr, rc = call_cli_once(model, prompt)
            latency = time.time() - t0
            if resp is None:
                if looks_like_quota(stderr, "", rc) and maybe_quota_sleep(f"rc={rc} stderr={stderr[:120]}"):
                    continue
                rec = {"pmid": paper["pmid"], "tier": tier, "model": model,
                       "sample_idx": s, "prompt_hash": prompt_hash,
                       "criteria_hash": criteria_hash,
                       "verdict": "", "domains": [], "reason": "",
                       "parse_error": f"call_failed:rc={rc}",
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
                rec = {"pmid": paper["pmid"], "tier": tier, "model": model,
                       "sample_idx": s, "prompt_hash": prompt_hash,
                       "criteria_hash": criteria_hash,
                       "verdict": "", "domains": [], "reason": "",
                       "parse_error": "is_error_true",
                       "error": json.dumps(err_obj)[:200],
                       "latency_s": round(latency,2),
                       "cost_usd": float(resp.get("total_cost_usd",0.0)), "raw": text[:500],
                       "call_started_utc": call_started_utc, "usage": resp.get("usage", {})}
                write_state(rec)
                return
            parsed = parse_verdict(text)
            cost = round(float(resp.get("total_cost_usd",0.0)),6)
            rec = {"pmid": paper["pmid"], "tier": tier, "model": model,
                   "sample_idx": s, "prompt_hash": prompt_hash,
                   "criteria_hash": criteria_hash,
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
    for paper in papers:
        for tier, model in TIERS:
            for s in range(N_SAMPLES):
                key = (paper["pmid"], tier, s)
                if key in done:
                    n_skip += 1
                    continue
                tasks.append((paper, tier, model, s))

    print(f"[plan] tasks to submit (after resume skip)={len(tasks)}  concurrency={args.concurrency}")
    with cf.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        list(pool.map(lambda t: do_one(*t), tasks))

    state_f.close()
    print(f"[done] new calls={n_done[0]} skipped={n_skip} total_target={n_total} "
          f"cost(new)=${total_cost[0]:.3f} quota_retries={quota_retries[0]}")

    # Build flat CSV from state file
    rows = []
    with STATE_JSONL.open() as f:
        for line in f:
            if not line.strip(): continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("_header"): continue
            rows.append(d)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pmid","tier","model","sample_idx","verdict","domains","reason",
                    "parse_error","error","latency_s","cost_usd"])
        for d in rows:
            w.writerow([
                d.get("pmid"), d.get("tier"), d.get("model"),
                d.get("sample_idx"), d.get("verdict",""),
                "|".join(d.get("domains") or []),
                (d.get("reason") or "")[:300],
                d.get("parse_error") or "",
                (d.get("error") or "")[:200] if d.get("error") else "",
                d.get("latency_s",""), d.get("cost_usd",""),
            ])
    print(f"[done] wrote {OUT_CSV} (n={len(rows)} rows)")


if __name__ == "__main__":
    main()
