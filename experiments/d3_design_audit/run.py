#!/usr/bin/env python3
"""
D3 study-design audit runner.

Pre-registered: experiments/d3_design_audit/protocol.md.

For each D3-tagged paper, ask three Claude models (Opus 4-7, Sonnet 4-6,
Haiku 4-5) to classify the study design from a fixed taxonomy of 9 categories.
102 papers x 3 models = 306 calls.

Quota-resilient: same pattern as run_self_consistency.py.

Outputs:
  experiments/d3_design_audit/state.jsonl
  experiments/data/processed/d3_design_audit_results.csv
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
CORPUS_CSV = SCRIPT_DIR / "data" / "d3_corpus.csv"
STATE_JSONL = SCRIPT_DIR / "state.jsonl"
OUT_CSV    = EXP_DIR / "data" / "processed" / "d3_design_audit_results.csv"

TIERS = [
    ("haiku",  "claude-haiku-4-5"),
    ("sonnet", "claude-sonnet-4-6"),
    ("opus",   "claude-opus-4-7"),
]

CATEGORIES = [
    "cross_sectional", "unspecified", "longitudinal", "systematic_review",
    "scale_validation", "review_commentary", "experimental", "qualitative",
    "content_analysis",
]

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
    "quota", "exceeded", "429", "usage_limit", "tokens_limit",
    "tokens exhausted", "limit reached", "too many requests",
]

PROMPT_TEMPLATE = """You are classifying the study design of a single peer-reviewed paper based on its title and abstract. Apply the fixed taxonomy below and emit a single JSON object — nothing else, no prose, no markdown fence.

TAXONOMY (choose exactly one):
- cross_sectional: cross-sectional survey at a single time point
- unspecified: title+abstract do not give enough information to pick another category
- longitudinal: prospective / repeated-measures / cohort design across at least 2 time points
- systematic_review: PRISMA-style systematic review or meta-analysis with explicit search method
- scale_validation: psychometric instrument development or validation study (CFA, EFA, reliability)
- review_commentary: narrative review, commentary, editorial, opinion, or position paper (NOT systematic)
- experimental: experimental or quasi-experimental design with manipulated independent variable
- qualitative: interviews, focus groups, ethnography, thematic analysis, etc.
- content_analysis: structured coding of game content, loot-box mechanics, or product listings

PAPER:
PMID:     <<PMID>>
Year:     <<YEAR>>
Journal:  <<JOURNAL>>
Title:    <<TITLE>>
Abstract: <<ABSTRACT>>

INSTRUCTIONS:
Emit one JSON object with these keys:
  {"design": "<one of the taxonomy keys>",
   "confidence": "low" | "medium" | "high",
   "reason": "<one short sentence, <= 25 words, citing a specific feature of the abstract>"}

The "design" field must be exactly one of the taxonomy keys (case-sensitive lowercase, underscores).
Output the JSON object and nothing else.
"""


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def next_window_utc():
    now = dt.datetime.now(KST)
    if now <= QUOTA_ANCHOR:
        return QUOTA_ANCHOR.astimezone(dt.timezone.utc)
    elapsed = (now - QUOTA_ANCHOR).total_seconds()
    n = int(elapsed // WINDOW_S) + 1
    return (QUOTA_ANCHOR + dt.timedelta(seconds=WINDOW_S * n)).astimezone(dt.timezone.utc)


def sleep_until_next(reason):
    nxt = next_window_utc() + dt.timedelta(seconds=QUOTA_BUFFER_S)
    now = dt.datetime.now(dt.timezone.utc)
    w = max(60, int((nxt - now).total_seconds()))
    print(f"[quota-sleep] {reason[:120]}  sleeping {w}s", flush=True)
    while w > 0:
        time.sleep(min(300, w)); w -= min(300, w)


def looks_like_quota(stderr, rc):
    return any(p in (stderr or "").lower() for p in QUOTA_PATTERNS)


def build_prompt(paper):
    return (PROMPT_TEMPLATE
            .replace("<<PMID>>",    paper.get("pmid", ""))
            .replace("<<YEAR>>",    paper.get("year", ""))
            .replace("<<JOURNAL>>", paper.get("journal", ""))
            .replace("<<TITLE>>",   paper.get("title", ""))
            .replace("<<ABSTRACT>>",(paper.get("abstract") or "")[:1800]))


def call_one(model, prompt):
    cmd = ["claude", "--print", "--no-session-persistence",
           "--model", model, "--output-format", "json",
           "--system-prompt", CLI_SYSTEM_PROMPT,
           "--tools", "", "--disable-slash-commands", prompt]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=PER_CALL_TO)
    except subprocess.TimeoutExpired:
        return None, "timeout", 124
    if r.returncode != 0:
        return None, r.stderr or r.stdout, r.returncode
    try:
        return json.loads(r.stdout), r.stderr, 0
    except json.JSONDecodeError:
        return None, r.stdout[:500], r.returncode


def parse(text):
    m = re.search(r"\{.*\}", text or "", re.DOTALL)
    if not m:
        return {"design": "", "confidence": "", "reason": "", "parse_error": "no_json"}
    try:
        o = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        return {"design": "", "confidence": "", "reason": "", "parse_error": f"json:{e}"}
    d = o.get("design", "")
    if d not in CATEGORIES:
        return {"design": "", "confidence": o.get("confidence",""),
                "reason": str(o.get("reason",""))[:200],
                "parse_error": f"design_not_in_set:{d}"}
    return {"design": d,
            "confidence": str(o.get("confidence",""))[:20],
            "reason": str(o.get("reason",""))[:200]}


def load_done(state_path):
    done = set()
    if not state_path.exists():
        return done
    for line in state_path.read_text().splitlines():
        if not line.strip(): continue
        try: d = json.loads(line)
        except json.JSONDecodeError: continue
        if d.get("_header"): continue
        if d.get("design"):
            done.add((d["pmid"], d["tier"]))
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--max-quota-retries", type=int, default=8)
    args = ap.parse_args()

    papers = list(csv.DictReader(CORPUS_CSV.open()))
    print(f"[plan] D3 papers={len(papers)}  tiers={len(TIERS)}  total={len(papers)*len(TIERS)}")

    prompt_hash = sha256(PROMPT_TEMPLATE)
    if args.fresh and STATE_JSONL.exists():
        STATE_JSONL.unlink()
    done = load_done(STATE_JSONL)
    if not STATE_JSONL.exists():
        STATE_JSONL.write_text(json.dumps({
            "_header": True,
            "prompt_hash": prompt_hash,
            "categories": CATEGORIES,
            "tiers": TIERS,
            "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        }) + "\n")

    sf = STATE_JSONL.open("a")
    lock = threading.Lock()
    qlock = threading.Lock()
    qretries = [0]
    cost_lock = threading.Lock()
    total_cost = [0.0]
    n_done = [0]
    n_skip = 0
    started = time.time()
    n_total = len(papers) * len(TIERS)

    def write_state(rec, cost_delta=0.0):
        with lock:
            sf.write(json.dumps(rec) + "\n"); sf.flush()
        if cost_delta:
            with cost_lock: total_cost[0] += cost_delta
        with cost_lock:
            n_done[0] += 1
            if n_done[0] % 20 == 0:
                elapsed = time.time() - started
                print(f"  done={n_done[0]} skip={n_skip} total={n_total}  "
                      f"cost=${total_cost[0]:.3f}  elapsed={elapsed:.0f}s  "
                      f"qretries={qretries[0]}", flush=True)

    def maybe_qsleep(reason):
        with qlock:
            if qretries[0] >= args.max_quota_retries: return False
            qretries[0] += 1; n = qretries[0]
        sleep_until_next(f"qretry_{n}: {reason}")
        return True

    def do_one(paper, tier, model):
        prompt = build_prompt(paper)
        while True:
            call_started_utc = dt.datetime.now(dt.timezone.utc).isoformat()
            t0 = time.time()
            resp, stderr, rc = call_one(model, prompt)
            lat = time.time() - t0
            if resp is None:
                if looks_like_quota(stderr, rc) and maybe_qsleep(f"rc={rc} {stderr[:80]}"):
                    continue
                rec = {"pmid": paper["pmid"], "tier": tier, "model": model,
                       "prompt_hash": prompt_hash,
                       "design": "", "confidence": "", "reason": "",
                       "parse_error": f"rc={rc}", "error": stderr[:200],
                       "latency_s": round(lat,2), "cost_usd": 0.0,
                       "call_started_utc": call_started_utc, "usage": {}}
                write_state(rec)
                return
            text = resp.get("result", "") or ""
            if resp.get("is_error"):
                e = json.dumps(resp.get("error") or {}).lower()
                if any(p in e for p in QUOTA_PATTERNS) and maybe_qsleep(f"is_err {e[:80]}"):
                    continue
            parsed = parse(text)
            cost = round(float(resp.get("total_cost_usd",0.0)), 6)
            rec = {"pmid": paper["pmid"], "tier": tier, "model": model,
                   "prompt_hash": prompt_hash,
                   **parsed,
                   "latency_s": round(lat,2), "cost_usd": cost,
                   "call_started_utc": call_started_utc,
                   "usage": resp.get("usage", {}),
                   "raw": text[:1500]}
            write_state(rec, cost_delta=cost)
            return

    tasks = []
    for paper in papers:
        for tier, model in TIERS:
            if (paper["pmid"], tier) in done:
                n_skip += 1; continue
            tasks.append((paper, tier, model))
    print(f"[plan] tasks to submit (after resume): {len(tasks)}  concurrency={args.concurrency}")

    if tasks:
        with cf.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            list(pool.map(lambda t: do_one(*t), tasks))
    sf.close()
    print(f"[done] new calls={n_done[0]} skipped={n_skip}  cost(new)=${total_cost[0]:.3f}  qretries={qretries[0]}")

    # Flat CSV
    rows = []
    for line in STATE_JSONL.read_text().splitlines():
        if not line.strip(): continue
        try: d = json.loads(line)
        except json.JSONDecodeError: continue
        if d.get("_header"): continue
        rows.append(d)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pmid","tier","model","design","confidence","reason",
                    "parse_error","latency_s","cost_usd","call_started_utc"])
        for d in rows:
            w.writerow([d.get("pmid"), d.get("tier"), d.get("model"),
                        d.get("design",""), d.get("confidence",""),
                        (d.get("reason") or "")[:300],
                        d.get("parse_error") or "",
                        d.get("latency_s",""), d.get("cost_usd",""),
                        d.get("call_started_utc","")])
    print(f"[done] wrote {OUT_CSV} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
