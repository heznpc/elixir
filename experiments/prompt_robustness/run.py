#!/usr/bin/env python3
"""
Prompt-robustness run for the cross-model convergence.

Pre-registered: experiments/prompt_robustness/protocol.md.

Re-screens the 59 convergent-disagreement papers under two perturbed prompt
framings (reword = noise control; lenient = adversarial pro-inclusion),
holding criteria_v1.txt byte-identical, on haiku-4-5 + sonnet-4-6.
59 x 2 variants x 2 models = 236 calls.

Reuses PR #14 fixes (is_error record, balanced-brace parse, retry dedup) and
the standard quota-resilience + cost-ceiling enforcement.

Outputs:
  experiments/prompt_robustness/state.jsonl
  experiments/prompt_robustness/data/prompt_robustness_results.csv
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
CONV_CSV   = EXP_DIR / "llm_second_reviewer" / "convergent_disagreements.csv"
STATE      = SCRIPT_DIR / "state.jsonl"
OUT_CSV    = SCRIPT_DIR / "data" / "prompt_robustness_results.csv"

VARIANTS = {
    "reword":  SCRIPT_DIR / "prompt_reword.txt",
    "lenient": SCRIPT_DIR / "prompt_lenient.txt",
}
MODELS = [("haiku", "claude-haiku-4-5"), ("sonnet", "claude-sonnet-4-6")]
EXPECT_CRIT = "1b467a5dce41"

PER_CALL_TO = 90
WINDOW_S = 5 * 3600
KST = zoneinfo.ZoneInfo("Asia/Seoul")
ANCHOR = dt.datetime(2026, 5, 21, 3, 10, tzinfo=KST)
QP = ["rate_limit", "rate limit", "quota", "exceeded", "429",
      "usage_limit", "tokens_limit", "too many requests", "limit reached"]
CLI_SYS = ("You output exactly one JSON object and nothing else. "
           "No prose, no preamble, no markdown code fence, no internal reasoning. Minimize tokens.")

sys.path.insert(0, str(EXP_DIR))
from _lib.parse_json import extract_first_balanced_object  # noqa: E402
from _lib.jsonl_dedup import dedup_state_records  # noqa: E402

_VERDICTS = {"Include", "Maybe", "Exclude"}
_DOMAINS  = {"D1", "D2", "D3", "D4", "D5", "D6", "Cross-domain"}


def sha256(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()


def next_window_utc():
    now = dt.datetime.now(KST)
    if now <= ANCHOR:
        return ANCHOR.astimezone(dt.timezone.utc)
    el = (now - ANCHOR).total_seconds()
    n = int(el // WINDOW_S) + 1
    return (ANCHOR + dt.timedelta(seconds=WINDOW_S * n)).astimezone(dt.timezone.utc)


def sleep_until_next(reason):
    nxt = next_window_utc() + dt.timedelta(seconds=30)
    w = max(60, int((nxt - dt.datetime.now(dt.timezone.utc)).total_seconds()))
    print(f"[quota-sleep] {reason[:120]} sleeping {w}s", flush=True)
    while w > 0:
        time.sleep(min(300, w)); w -= min(300, w)


def is_quota(stderr): return any(p in (stderr or "").lower() for p in QP)


def build_prompt(paper, criteria, tmpl):
    return (tmpl.replace("<<CRITERIA_VERBATIM>>", criteria)
                .replace("<<PMID>>", paper["pmid"]).replace("<<YEAR>>", paper["year"])
                .replace("<<JOURNAL>>", paper["journal"]).replace("<<TITLE>>", paper["title"])
                .replace("<<ABSTRACT>>", (paper.get("abstract", "") or "")[:1800]))


def parse(text):
    raw = extract_first_balanced_object(text or "")
    if not raw:
        return {"verdict": "", "domains": [], "reason": "", "parse_error": "no_json"}
    try:
        o = json.loads(raw)
    except json.JSONDecodeError as e:
        return {"verdict": "", "domains": [], "reason": "", "parse_error": f"json:{e}"}
    v = o.get("verdict", ""); d = o.get("domains", []) or []; r = o.get("reason", "")
    if v not in _VERDICTS:
        return {"verdict": "", "domains": d, "reason": r, "parse_error": f"verdict_bad:{v}"}
    if not isinstance(d, list): d = []
    return {"verdict": v, "domains": [x for x in d if x in _DOMAINS], "reason": str(r)[:200]}


def call_one(model, prompt):
    cmd = ["claude", "--print", "--no-session-persistence", "--model", model,
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
        if not line.strip(): continue
        try: d = json.loads(line)
        except json.JSONDecodeError: continue
        if d.get("_header"): continue
        if d.get("verdict"):
            done.add((d["pmid"], d["variant"], d["tier"]))
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--concurrency", type=int, default=6)
    ap.add_argument("--max-quota-retries", type=int, default=8)
    ap.add_argument("--cost-ceiling", type=float, default=12.0)
    args = ap.parse_args()

    criteria = CRIT_TXT.read_text()
    crit_hash = sha256(criteria)
    if not crit_hash.startswith(EXPECT_CRIT):
        print(f"[abort] criteria hash drift {crit_hash[:12]} != {EXPECT_CRIT}", file=sys.stderr)
        sys.exit(3)
    prompts = {k: p.read_text() for k, p in VARIANTS.items()}
    prompt_hashes = {k: sha256(v) for k, v in prompts.items()}

    # 59 convergent papers joined to abstracts
    conv = {r["pmid"] for r in csv.DictReader(CONV_CSV.open())}
    raw = {r["pmid"]: r for r in csv.DictReader(RAW_CSV.open())}
    papers = [raw[p] for p in conv if p in raw]
    print(f"[plan] papers={len(papers)} variants={list(VARIANTS)} models={[m for _,m in MODELS]} "
          f"crit={crit_hash[:12]} prompt_hashes={ {k:h[:8] for k,h in prompt_hashes.items()} }")

    if args.fresh and STATE.exists():
        STATE.unlink()
    done = load_done()
    if not STATE.exists():
        STATE.write_text(json.dumps({
            "_header": True, "criteria_hash": crit_hash, "prompt_hashes": prompt_hashes,
            "models": MODELS, "variants": list(VARIANTS),
            "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        }) + "\n")

    sf = STATE.open("a")
    lock = threading.Lock(); qlock = threading.Lock()
    qretries = [0]; cost = [0.0]; n_done = [0]; stop = [False]
    started = time.time()

    def maybe_qsleep(reason):
        with qlock:
            if qretries[0] >= args.max_quota_retries:
                return False
            qretries[0] += 1; n = qretries[0]
        sleep_until_next(f"qretry_{n}: {reason}")
        return True

    def write(rec, dcost=0.0):
        with lock:
            sf.write(json.dumps(rec) + "\n"); sf.flush()
        with qlock:
            if dcost: cost[0] += dcost
            n_done[0] += 1
            if cost[0] > args.cost_ceiling and not stop[0]:
                stop[0] = True
                print(f"[stop §7] cost ceiling ${args.cost_ceiling} exceeded (${cost[0]:.2f})", flush=True)
            if n_done[0] % 20 == 0:
                print(f"  done={n_done[0]} cost=${cost[0]:.3f} elapsed={time.time()-started:.0f}s "
                      f"qretries={qretries[0]}", flush=True)

    def do_one(task):
        if stop[0]:
            return
        paper, variant, tier, model = task
        prompt = build_prompt(paper, criteria, prompts[variant])
        while True:
            su = dt.datetime.now(dt.timezone.utc).isoformat()
            t0 = time.time()
            resp, stderr, rc = call_one(model, prompt)
            lat = time.time() - t0
            base = {"pmid": paper["pmid"], "variant": variant, "tier": tier, "model": model,
                    "criteria_hash": crit_hash, "prompt_hash": prompt_hashes[variant],
                    "call_started_utc": su, "latency_s": round(lat, 2)}
            if resp is None:
                if is_quota(stderr) and maybe_qsleep(f"rc={rc}"):
                    continue
                write({**base, "verdict": "", "domains": [], "reason": "",
                       "parse_error": f"rc={rc}", "error": (stderr or "")[:200],
                       "cost_usd": 0.0, "usage": {}})
                return
            text = resp.get("result", "") or ""
            if resp.get("is_error"):
                eo = resp.get("error") or {}
                if any(p in json.dumps(eo).lower() for p in QP) and maybe_qsleep("is_err"):
                    continue
                write({**base, "verdict": "", "domains": [], "reason": "",
                       "parse_error": "is_error_true", "error": json.dumps(eo)[:300],
                       "cost_usd": float(resp.get("total_cost_usd", 0.0)), "usage": resp.get("usage", {})})
                return
            c = round(float(resp.get("total_cost_usd", 0.0)), 6)
            write({**base, **parse(text), "cost_usd": c,
                   "usage": resp.get("usage", {}), "raw": text[:1500]}, dcost=c)
            return

    tasks = []
    for paper in papers:
        for variant in VARIANTS:
            for tier, model in MODELS:
                if (paper["pmid"], variant, tier) in done:
                    continue
                tasks.append((paper, variant, tier, model))
    print(f"[plan] tasks={len(tasks)} (resume skip={len(papers)*len(VARIANTS)*len(MODELS)-len(tasks)}) "
          f"concurrency={args.concurrency}")
    if tasks:
        with cf.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            list(pool.map(do_one, tasks))
    sf.close()
    print(f"[done] new={n_done[0]} cost(new)=${cost[0]:.3f} qretries={qretries[0]}")

    # Flat CSV, dedup on (pmid, variant, tier)
    rows_raw = []
    for line in STATE.read_text().splitlines():
        if not line.strip(): continue
        try: d = json.loads(line)
        except json.JSONDecodeError: continue
        if d.get("_header"): continue
        rows_raw.append(d)
    rows = dedup_state_records(
        rows_raw,
        key_fn=lambda d: (d.get("pmid"), d.get("variant"), d.get("tier")),
        success_fn=lambda d: bool(d.get("verdict")),
    )
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pmid", "variant", "tier", "model", "verdict", "domains", "reason",
                    "parse_error", "latency_s", "cost_usd", "call_started_utc"])
        for d in rows:
            w.writerow([d.get("pmid"), d.get("variant"), d.get("tier"), d.get("model"),
                        d.get("verdict", ""), "|".join(d.get("domains") or []),
                        (d.get("reason") or "")[:300], d.get("parse_error") or "",
                        d.get("latency_s", ""), d.get("cost_usd", ""), d.get("call_started_utc", "")])
    print(f"[done] wrote {OUT_CSV} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
