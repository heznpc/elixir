#!/usr/bin/env python3
"""
LLM recheck of heuristic-Include OpenAlex records (n=11 in current run).

Triggered by protocol §6 of `experiments/openalex_extension/protocol.md`:
"If novel records yield ≥ 5 heuristic-Include hits per domain, a follow-up
LLM screening pass is filed as a separate experiment."

Reuses the prompt + criteria from experiments/llm_second_reviewer/. Runs each
of the 11 Include records through Opus 4-7, Sonnet 4-6, Haiku 4-5 = 33 calls.

Outputs:
  experiments/openalex_extension/llm_recheck_state.jsonl
  experiments/openalex_extension/data/llm_recheck.csv
"""
from __future__ import annotations

import argparse, concurrent.futures as cf, csv, datetime as dt, hashlib, json
import pathlib, re, subprocess, threading, time, zoneinfo

ROOT = pathlib.Path(__file__).resolve().parent
EXP  = ROOT.parent
NOVEL_CSV = ROOT / "data" / "novel_records.csv"
CRIT_TXT  = EXP / "llm_second_reviewer" / "criteria_v1.txt"
PROMPT_TXT = EXP / "llm_second_reviewer" / "prompt_v1.txt"
STATE = ROOT / "llm_recheck_state.jsonl"
OUT_CSV = ROOT / "data" / "llm_recheck.csv"

TIERS = [("haiku", "claude-haiku-4-5"), ("sonnet", "claude-sonnet-4-6"), ("opus", "claude-opus-4-7")]

CLI_SYS = ("You output exactly one JSON object and nothing else. "
           "No prose, no preamble, no markdown code fence, no internal reasoning. Minimize tokens.")

KST = zoneinfo.ZoneInfo("Asia/Seoul")
ANCHOR = dt.datetime(2026,5,21,3,10,tzinfo=KST)
WINDOW_S = 5*3600
QP = ["rate_limit","rate limit","quota","exceeded","429","tokens_limit","too many requests","limit reached"]


def sha(s): return hashlib.sha256(s.encode()).hexdigest()


def next_window_utc():
    now = dt.datetime.now(KST)
    if now <= ANCHOR: return ANCHOR.astimezone(dt.timezone.utc)
    elapsed = (now-ANCHOR).total_seconds()
    n = int(elapsed//WINDOW_S)+1
    return (ANCHOR + dt.timedelta(seconds=WINDOW_S*n)).astimezone(dt.timezone.utc)


def sleep_until_next(reason):
    nxt = next_window_utc() + dt.timedelta(seconds=30)
    now = dt.datetime.now(dt.timezone.utc)
    w = max(60, int((nxt-now).total_seconds()))
    print(f"[quota-sleep] {reason[:120]}  sleeping {w}s", flush=True)
    while w>0:
        time.sleep(min(300,w)); w -= min(300,w)


def is_quota(stderr, retcode):
    blob = stderr.lower()
    return any(p in blob for p in QP)


def build_prompt(rec, criteria, tmpl):
    return (tmpl.replace("<<CRITERIA_VERBATIM>>", criteria)
                .replace("<<PMID>>", rec.get("pmid","") or rec["openalex_id"])
                .replace("<<YEAR>>", rec.get("year",""))
                .replace("<<JOURNAL>>", rec.get("journal",""))
                .replace("<<TITLE>>", rec.get("title",""))
                .replace("<<ABSTRACT>>", (rec.get("abstract","") or "")[:1800]))


def parse(text):
    m = re.search(r"\{.*\}", text or "", re.DOTALL)
    if not m: return {"verdict":"","domains":[],"reason":"","parse_error":"no_json"}
    try: o = json.loads(m.group(0))
    except json.JSONDecodeError as e: return {"verdict":"","domains":[],"reason":"","parse_error":f"json:{e}"}
    v = o.get("verdict",""); d = o.get("domains",[]) or []; r = o.get("reason","")
    if v not in ("Include","Maybe","Exclude"):
        return {"verdict":"","domains":d,"reason":r,"parse_error":f"verdict_bad:{v}"}
    if not isinstance(d, list): d=[]
    return {"verdict":v,"domains":d,"reason":str(r)[:200]}


def call_one(model, prompt):
    cmd = ["claude","--print","--no-session-persistence","--model",model,
           "--output-format","json","--system-prompt",CLI_SYS,
           "--tools","","--disable-slash-commands", prompt]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    except subprocess.TimeoutExpired:
        return None, "timeout", 124
    if r.returncode != 0: return None, r.stderr or r.stdout, r.returncode
    try: return json.loads(r.stdout), r.stderr, 0
    except json.JSONDecodeError: return None, r.stdout[:500], r.returncode


def load_done():
    done = set()
    if not STATE.exists(): return done
    for line in STATE.read_text().splitlines():
        if not line.strip(): continue
        try: d = json.loads(line)
        except json.JSONDecodeError: continue
        if d.get("_header"): continue
        if d.get("verdict"): done.add((d["openalex_id"], d["tier"]))
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--max-quota-retries", type=int, default=8)
    args = ap.parse_args()

    rows = list(csv.DictReader(NOVEL_CSV.open()))
    targets = [r for r in rows if r["screening_verdict"] == "Include"]
    print(f"[plan] {len(targets)} Include records x {len(TIERS)} tiers = {len(targets)*len(TIERS)} calls")
    if not targets: print("nothing to do"); return

    criteria = CRIT_TXT.read_text()
    tmpl = PROMPT_TXT.read_text()
    prompt_hash = sha(tmpl); criteria_hash = sha(criteria)

    if args.fresh and STATE.exists(): STATE.unlink()
    done = load_done()
    if not STATE.exists():
        STATE.write_text(json.dumps({"_header":True,"prompt_hash":prompt_hash,
                                     "criteria_hash":criteria_hash,
                                     "started_utc":dt.datetime.now(dt.timezone.utc).isoformat()})+"\n")
    sf = STATE.open("a")
    lock = threading.Lock()
    qretries = [0]
    qlock = threading.Lock()

    def maybe_qsleep(reason):
        with qlock:
            if qretries[0] >= args.max_quota_retries: return False
            qretries[0] += 1; n = qretries[0]
        sleep_until_next(f"qretry_{n}: {reason}")
        return True

    def do_one(rec, tier, model):
        prompt = build_prompt(rec, criteria, tmpl)
        while True:
            call_started_utc = dt.datetime.now(dt.timezone.utc).isoformat()
            t0 = time.time()
            resp, stderr, rc = call_one(model, prompt)
            lat = time.time()-t0
            if resp is None:
                if is_quota(stderr, rc) and maybe_qsleep(f"rc={rc} {stderr[:80]}"):
                    continue
                rec_out = {"openalex_id":rec["openalex_id"],"tier":tier,"model":model,
                           "verdict":"","domains":[],"reason":"",
                           "parse_error":f"rc={rc}","error":stderr[:200],
                           "latency_s":round(lat,2),"cost_usd":0.0,
                           "call_started_utc": call_started_utc,
                           "usage": {}}
                with lock: sf.write(json.dumps(rec_out)+"\n"); sf.flush()
                return
            text = resp.get("result","") or ""
            if resp.get("is_error"):
                e = json.dumps(resp.get("error") or {}).lower()
                if any(p in e for p in QP) and maybe_qsleep(f"is_err {e[:80]}"): continue
            parsed = parse(text)
            cost = round(float(resp.get("total_cost_usd",0.0)),6)
            rec_out = {"openalex_id":rec["openalex_id"],"tier":tier,"model":model,
                       **parsed,"latency_s":round(lat,2),"cost_usd":cost,
                       "call_started_utc": call_started_utc,
                       "usage": resp.get("usage", {}),
                       "raw":text[:1500]}
            with lock: sf.write(json.dumps(rec_out)+"\n"); sf.flush()
            return

    tasks = []
    for rec in targets:
        for tier, model in TIERS:
            if (rec["openalex_id"], tier) in done: continue
            tasks.append((rec, tier, model))
    print(f"[plan] tasks to submit (after resume): {len(tasks)}")

    with cf.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        list(pool.map(lambda t: do_one(*t), tasks))
    sf.close()

    # Flat CSV
    rows_out = []
    for line in STATE.read_text().splitlines():
        if not line.strip(): continue
        try: d = json.loads(line)
        except json.JSONDecodeError: continue
        if d.get("_header"): continue
        rows_out.append(d)
    with OUT_CSV.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["openalex_id","tier","model","verdict","domains","reason",
                    "parse_error","latency_s","cost_usd"])
        for d in rows_out:
            w.writerow([d.get("openalex_id"), d.get("tier"), d.get("model"),
                        d.get("verdict",""), "|".join(d.get("domains") or []),
                        (d.get("reason") or "")[:300],
                        d.get("parse_error") or "",
                        d.get("latency_s",""), d.get("cost_usd","")])
    print(f"[done] wrote {OUT_CSV} ({len(rows_out)} rows)")


if __name__ == "__main__":
    main()
