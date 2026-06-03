#!/usr/bin/env python3
"""
Opus 4-8 cross-generation rater run.

Pre-registered: experiments/opus48_crossgen/protocol.md.

Adds claude-opus-4-8 as a fourth rater over the SAME 227-paper corpus,
reusing the BYTE-IDENTICAL frozen prompt_v1.txt + criteria_v1.txt from the
primary IRR audit (hash-verified) so the comparison is model-only.

Provenance-isolated: writes only under experiments/opus48_crossgen/.
Incorporates the PR #14 fixes: is_error records the real error (no
fall-through to parse), balanced-brace JSON extraction, CSV dedup on retry.

Outputs:
  experiments/opus48_crossgen/state.jsonl
  experiments/opus48_crossgen/data/opus48_results.csv
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import datetime as dt
import hashlib
import json
import pathlib
import subprocess
import sys
import threading
import time
import zoneinfo

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
EXP_DIR    = SCRIPT_DIR.parent
RAW_CSV    = EXP_DIR / "data" / "raw" / "pubmed_results.csv"
CRIT_TXT   = EXP_DIR / "llm_second_reviewer" / "criteria_v1.txt"
PROMPT_TXT = EXP_DIR / "llm_second_reviewer" / "prompt_v1.txt"
STATE      = SCRIPT_DIR / "state.jsonl"
OUT_CSV    = SCRIPT_DIR / "data" / "opus48_results.csv"

MODEL = "claude-opus-4-8"
TIER  = "opus48"
PER_CALL_TO = 90
WINDOW_S = 5 * 3600
KST = zoneinfo.ZoneInfo("Asia/Seoul")
ANCHOR = dt.datetime(2026, 5, 21, 3, 10, tzinfo=KST)
QP = ["rate_limit", "rate limit", "quota", "exceeded", "429",
      "usage_limit", "tokens_limit", "too many requests", "limit reached"]
CLI_SYS = ("You output exactly one JSON object and nothing else. "
           "No prose, no preamble, no markdown code fence, no internal reasoning. "
           "Minimize tokens.")

sys.path.insert(0, str(EXP_DIR))
from _lib.parse_json import extract_first_balanced_object  # noqa: E402
from _lib.jsonl_dedup import dedup_state_records, is_success_verdict, key_pmid_tier  # noqa: E402

_VERDICTS = {"Include", "Maybe", "Exclude"}
_DOMAINS  = {"D1", "D2", "D3", "D4", "D5", "D6", "Cross-domain"}


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def next_window_utc():
    now = dt.datetime.now(KST)
    if now <= ANCHOR:
        return ANCHOR.astimezone(dt.timezone.utc)
    elapsed = (now - ANCHOR).total_seconds()
    n = int(elapsed // WINDOW_S) + 1
    return (ANCHOR + dt.timedelta(seconds=WINDOW_S * n)).astimezone(dt.timezone.utc)


def sleep_until_next(reason):
    nxt = next_window_utc() + dt.timedelta(seconds=30)
    now = dt.datetime.now(dt.timezone.utc)
    w = max(60, int((nxt - now).total_seconds()))
    print(f"[quota-sleep] {reason[:120]} sleeping {w}s", flush=True)
    while w > 0:
        time.sleep(min(300, w)); w -= min(300, w)


def is_quota(stderr):
    return any(p in (stderr or "").lower() for p in QP)


def build_prompt(paper, criteria, tmpl):
    return (tmpl.replace("<<CRITERIA_VERBATIM>>", criteria)
                .replace("<<PMID>>", paper["pmid"])
                .replace("<<YEAR>>", paper["year"])
                .replace("<<JOURNAL>>", paper["journal"])
                .replace("<<TITLE>>", paper["title"])
                .replace("<<ABSTRACT>>", (paper.get("abstract", "") or "")[:1800]))


def parse(text):
    raw = extract_first_balanced_object(text or "")
    if not raw:
        return {"verdict": "", "domains": [], "reason": "", "parse_error": "no_json"}
    try:
        o = json.loads(raw)
    except json.JSONDecodeError as e:
        return {"verdict": "", "domains": [], "reason": "", "parse_error": f"json:{e}"}
    v = o.get("verdict", "")
    d = o.get("domains", []) or []
    r = o.get("reason", "")
    if v not in _VERDICTS:
        return {"verdict": "", "domains": d, "reason": r, "parse_error": f"verdict_bad:{v}"}
    if not isinstance(d, list):
        d = []
    d = [x for x in d if x in _DOMAINS]
    return {"verdict": v, "domains": d, "reason": str(r)[:200]}


def call_one(prompt):
    cmd = ["claude", "--print", "--no-session-persistence", "--model", MODEL,
           "--output-format", "json", "--system-prompt", CLI_SYS,
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


def load_done():
    done = set()
    if not STATE.exists():
        return done
    for line in STATE.read_text().splitlines():
        if not line.strip():
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("_header"):
            continue
        if d.get("verdict"):
            done.add(d["pmid"])
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--concurrency", type=int, default=6)
    ap.add_argument("--max-quota-retries", type=int, default=8)
    ap.add_argument("--cost-ceiling", type=float, default=30.0)
    args = ap.parse_args()

    criteria = CRIT_TXT.read_text()
    tmpl = PROMPT_TXT.read_text()
    prompt_hash = sha256(tmpl)
    criteria_hash = sha256(criteria)
    # Guard: confirm frozen inputs still match the original audit hashes.
    EXPECT_PROMPT = "6ba4ab67e4de"
    EXPECT_CRIT   = "1b467a5dce41"
    if not (prompt_hash.startswith(EXPECT_PROMPT) and criteria_hash.startswith(EXPECT_CRIT)):
        print(f"[abort] frozen prompt/criteria hash drift: prompt={prompt_hash[:12]} "
              f"criteria={criteria_hash[:12]} (expected {EXPECT_PROMPT}/{EXPECT_CRIT}). "
              "Comparison would confound model with prompt.", file=sys.stderr)
        sys.exit(3)

    papers = list(csv.DictReader(RAW_CSV.open()))
    print(f"[plan] model={MODEL} papers={len(papers)} prompt={prompt_hash[:12]} criteria={criteria_hash[:12]}")

    if args.fresh and STATE.exists():
        STATE.unlink()
    done = load_done()
    if not STATE.exists():
        STATE.write_text(json.dumps({
            "_header": True, "tier": TIER, "model": MODEL,
            "prompt_hash": prompt_hash, "criteria_hash": criteria_hash,
            "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        }) + "\n")

    sf = STATE.open("a")
    lock = threading.Lock()
    qlock = threading.Lock()
    qretries = [0]
    cost = [0.0]
    n_done = [0]
    n_skip = 0
    started = time.time()
    stop_flag = [False]  # set once cost ceiling exceeded; checked at top of do_one

    def maybe_qsleep(reason):
        with qlock:
            if qretries[0] >= args.max_quota_retries:
                return False
            qretries[0] += 1
            n = qretries[0]
        sleep_until_next(f"qretry_{n}: {reason}")
        return True

    def write(rec, dcost=0.0):
        with lock:
            sf.write(json.dumps(rec) + "\n"); sf.flush()
        with qlock:
            if dcost:
                cost[0] += dcost
            n_done[0] += 1
            # Protocol §11: abort once cost ceiling exceeded. Bounds overrun to
            # in-flight calls (concurrency) since pool.map tasks already submitted
            # check stop_flag at the top of do_one before issuing a new API call.
            if cost[0] > args.cost_ceiling and not stop_flag[0]:
                stop_flag[0] = True
                print(f"[stop §11] cost ceiling exceeded: ${cost[0]:.2f} > ${args.cost_ceiling} "
                      "— remaining queued calls will be skipped.", flush=True)
            if n_done[0] % 20 == 0:
                print(f"  done={n_done[0]} skip={n_skip} cost=${cost[0]:.3f} "
                      f"elapsed={time.time()-started:.0f}s qretries={qretries[0]}", flush=True)

    def do_one(paper):
        if stop_flag[0]:  # cost ceiling already hit — skip without billing
            return
        prompt = build_prompt(paper, criteria, tmpl)
        while True:
            started_utc = dt.datetime.now(dt.timezone.utc).isoformat()
            t0 = time.time()
            resp, stderr, rc = call_one(prompt)
            lat = time.time() - t0
            if resp is None:
                if is_quota(stderr) and maybe_qsleep(f"rc={rc} {stderr[:80]}"):
                    continue
                write({"pmid": paper["pmid"], "tier": TIER, "model": MODEL,
                       "prompt_hash": prompt_hash, "criteria_hash": criteria_hash,
                       "verdict": "", "domains": [], "reason": "",
                       "parse_error": f"rc={rc}", "error": (stderr or "")[:200],
                       "latency_s": round(lat, 2), "cost_usd": 0.0,
                       "call_started_utc": started_utc, "usage": {}})
                return
            text = resp.get("result", "") or ""
            if resp.get("is_error"):
                err_obj = resp.get("error") or {}
                e = json.dumps(err_obj).lower()
                if any(p in e for p in QP) and maybe_qsleep(f"is_err {e[:80]}"):
                    continue
                write({"pmid": paper["pmid"], "tier": TIER, "model": MODEL,
                       "prompt_hash": prompt_hash, "criteria_hash": criteria_hash,
                       "verdict": "", "domains": [], "reason": "",
                       "parse_error": "is_error_true", "error": json.dumps(err_obj)[:300],
                       "latency_s": round(lat, 2),
                       "cost_usd": float(resp.get("total_cost_usd", 0.0)),
                       "call_started_utc": started_utc, "usage": resp.get("usage", {})})
                return
            parsed = parse(text)
            c = round(float(resp.get("total_cost_usd", 0.0)), 6)
            write({"pmid": paper["pmid"], "tier": TIER, "model": MODEL,
                   "prompt_hash": prompt_hash, "criteria_hash": criteria_hash,
                   **parsed, "latency_s": round(lat, 2), "cost_usd": c,
                   "call_started_utc": started_utc, "usage": resp.get("usage", {}),
                   "raw": text[:1500]}, dcost=c)
            return

    tasks = [p for p in papers if p["pmid"] not in done]
    n_skip = len(papers) - len(tasks)
    print(f"[plan] tasks={len(tasks)} (resume skip={n_skip}) concurrency={args.concurrency}")
    if tasks:
        with cf.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            list(pool.map(do_one, tasks))
    sf.close()
    print(f"[done] new={n_done[0]} skip={n_skip} cost(new)=${cost[0]:.3f} qretries={qretries[0]}")

    # Flat CSV with retry-dedup on pmid (single tier so key = pmid+tier).
    rows_raw = []
    for line in STATE.read_text().splitlines():
        if not line.strip():
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("_header"):
            continue
        rows_raw.append(d)
    rows = dedup_state_records(rows_raw, key_pmid_tier, is_success_verdict)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pmid", "tier", "model", "verdict", "domains", "reason",
                    "parse_error", "error", "latency_s", "cost_usd", "call_started_utc"])
        for d in rows:
            w.writerow([d.get("pmid"), d.get("tier"), d.get("model"),
                        d.get("verdict", ""), "|".join(d.get("domains") or []),
                        (d.get("reason") or "")[:300], d.get("parse_error") or "",
                        (d.get("error") or "")[:200] if d.get("error") else "",
                        d.get("latency_s", ""), d.get("cost_usd", ""),
                        d.get("call_started_utc", "")])
    print(f"[done] wrote {OUT_CSV} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
