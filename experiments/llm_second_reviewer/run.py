#!/usr/bin/env python3
"""
LLM-as-second-reviewer runner for the Elixir PRISMA audit.

Pre-registered protocol: experiments/llm_second_reviewer/protocol.md.
Uses Anthropic Messages API directly (stdlib urllib only), with prompt-caching
of the criteria + prompt template across all calls for each model.

Inputs:
  experiments/data/raw/pubmed_results.csv          227 papers
  experiments/data/processed/screening_results.csv heuristic verdicts
  experiments/llm_second_reviewer/criteria_v1.txt
  experiments/llm_second_reviewer/prompt_v1.txt

Outputs:
  experiments/llm_second_reviewer/run_<timestamp>_<model>.jsonl
  experiments/data/processed/llm_second_reviewer_results.csv

Auth precedence (highest to lowest):
  1. $ANTHROPIC_API_KEY env var
  2. ~/.cache/anthropic_key file (chmod 600 expected)
  3. ~/.anthropic/credentials (legacy)
  4. abort with §11 stop condition

Stop conditions per protocol §11:
  - No API key resolvable          -> exit code 2
  - > 5% malformed after retry     -> exit code 3
  - Wall time > 30 min             -> exit code 4
  - Estimated cost > $7 ceiling    -> exit code 5
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import hashlib
import json
import os
import pathlib
import re
import ssl
import sys
import time
import urllib.error
import urllib.request

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
EXP_DIR    = SCRIPT_DIR.parent
ROOT_DIR   = EXP_DIR.parent
RAW_CSV    = EXP_DIR / "data" / "raw" / "pubmed_results.csv"
HEUR_CSV   = EXP_DIR / "data" / "processed" / "screening_results.csv"
CRIT_TXT   = SCRIPT_DIR / "criteria_v1.txt"
PROMPT_TXT = SCRIPT_DIR / "prompt_v1.txt"
OUT_CSV    = EXP_DIR / "data" / "processed" / "llm_second_reviewer_results.csv"

# Per-protocol §5
MODELS = [
    "claude-opus-4-5",     # Will try opus-4-7 first; fall back to 4-5 if 4-7 not reachable
    "claude-sonnet-4-5",
    "claude-haiku-4-5",
]
MODEL_TRY_ORDER = {
    # Updated 2026-05-21 after endpoint probe: opus-4-7 + sonnet-4-6 are newest reachable.
    # haiku-4-6/4-7 do not exist yet; haiku-4-5 is the latest haiku.
    "opus":   ["claude-opus-4-7",   "claude-opus-4-6",   "claude-opus-4-5"],
    "sonnet": ["claude-sonnet-4-6", "claude-sonnet-4-5"],
    "haiku":  ["claude-haiku-4-5"],
}

API_BASE       = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com").rstrip("/")
API_VERSION    = "2023-06-01"
TEMPERATURE    = 0.0       # protocol §5
MAX_TOKENS     = 200       # response is one small JSON object
PER_CALL_TO    = 60        # seconds
CONCURRENCY    = 4         # protocol §5 last bullet
WALL_BUDGET_S  = 30 * 60   # protocol §11
COST_CEILING   = 7.00      # USD, protocol §11

# Per-MTok pricing as of 2026-05 (display only; abort if exceeded)
PRICE_PER_MTOK = {
    # input, cached_read, output  (USD)
    "claude-opus-4-7":   (15.0,  1.50, 75.0),
    "claude-opus-4-6":   (15.0,  1.50, 75.0),
    "claude-opus-4-5":   (15.0,  1.50, 75.0),
    "claude-sonnet-4-6": ( 3.0,  0.30, 15.0),
    "claude-sonnet-4-5": ( 3.0,  0.30, 15.0),
    "claude-haiku-4-5": ( 1.0,  0.10,  5.0),
}

# ---------------------------------------------------------------------------
# Auth resolution
# ---------------------------------------------------------------------------
def resolve_api_key() -> str | None:
    env = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if env:
        return env
    for p in (
        pathlib.Path.home() / ".cache" / "anthropic_key",
        pathlib.Path.home() / ".anthropic" / "credentials",
    ):
        if p.exists():
            try:
                txt = p.read_text().strip()
                # naive parse: first sk-ant-... token wins
                m = re.search(r"sk-ant-[A-Za-z0-9_\-]+", txt)
                if m:
                    return m.group(0)
                if txt.startswith("sk-"):
                    return txt
            except OSError:
                continue
    return None


# ---------------------------------------------------------------------------
# Prompt assembly + hashing
# ---------------------------------------------------------------------------
def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def build_request_body(model: str, paper: dict, criteria: str, prompt_template: str) -> tuple[dict, str, str]:
    """Return (body_dict, prompt_hash, criteria_hash)."""
    # TODO(review-2026-05-21): consider two-step prompting — Phase 1 emits domain set only,
    # Phase 2 takes domains + criteria and emits Include/Maybe/Exclude. Improves interpretability
    # and likely reduces verdict-prior bias from domain assignment.
    prompt = (
        prompt_template
        .replace("<<CRITERIA_VERBATIM>>", criteria)
        .replace("<<PMID>>",     paper["pmid"])
        .replace("<<YEAR>>",     paper["year"])
        .replace("<<JOURNAL>>",  paper["journal"])
        .replace("<<TITLE>>",    paper["title"])
        .replace("<<ABSTRACT>>", paper.get("abstract", "")[:1800])
    )
    prompt_hash   = sha256(prompt_template)
    criteria_hash = sha256(criteria)
    # Split prompt into a cacheable preamble (criteria + instructions) and a per-paper tail
    cache_anchor = "PAPER TO SCREEN:"
    idx = prompt.find(cache_anchor)
    if idx <= 0:
        # fallback: no cache; single content
        body = {
            "model": model,
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "system": "You output exactly one JSON object and nothing else. No prose, no markdown fence.",
            "messages": [{"role": "user", "content": prompt}],
        }
        return body, prompt_hash, criteria_hash
    preamble = prompt[:idx]
    tail     = prompt[idx:]
    body = {
        "model": model,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "system": [
            {"type": "text",
             "text": "You output exactly one JSON object and nothing else. No prose, no markdown fence.",
             "cache_control": {"type": "ephemeral"}},
        ],
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": preamble, "cache_control": {"type": "ephemeral"}},
                {"type": "text", "text": tail},
            ],
        }],
    }
    return body, prompt_hash, criteria_hash


# ---------------------------------------------------------------------------
# API call
# ---------------------------------------------------------------------------
def call_anthropic(api_key: str, body: dict, timeout: int = PER_CALL_TO) -> tuple[dict | None, str | None]:
    req = urllib.request.Request(
        API_BASE + "/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": API_VERSION,
            "content-type": "application/json",
        },
        method="POST",
    )
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return json.loads(r.read()), None
    except urllib.error.HTTPError as e:
        body_bytes = e.read()[:600]
        return None, f"HTTPError {e.code}: {body_bytes.decode('utf-8','replace')}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------
_VERDICTS = {"Include", "Maybe", "Exclude"}
_DOMAINS  = {"D1", "D2", "D3", "D4", "D5", "D6", "Cross-domain"}

def parse_verdict(text: str) -> dict:
    """Extract {verdict, domains, reason} from model output text. Robust to code fences."""
    # Strip code fences if present
    m = re.search(r"\{[^{}]*\"verdict\".*?\}", text, re.DOTALL)
    if not m:
        # try greedy
        m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return {"verdict": "", "domains": [], "reason": "", "parse_error": "no_json_object"}
    raw = m.group(0)
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as e:
        return {"verdict": "", "domains": [], "reason": "", "parse_error": f"json_decode: {e}"}
    v = obj.get("verdict", "")
    d = obj.get("domains", []) or []
    r = obj.get("reason", "")
    if v not in _VERDICTS:
        return {"verdict": "", "domains": d, "reason": r, "parse_error": f"verdict_not_in_set:{v}"}
    if not isinstance(d, list):
        d = []
    d = [x for x in d if x in _DOMAINS]
    return {"verdict": v, "domains": d, "reason": str(r)[:200]}


# ---------------------------------------------------------------------------
# Cost accounting
# ---------------------------------------------------------------------------
def cost_for_usage(model: str, usage: dict) -> float:
    pin = PRICE_PER_MTOK.get(model)
    if not pin:
        # default to opus pricing as upper bound
        pin = (15.0, 1.50, 75.0)
    in_t   = usage.get("input_tokens", 0)
    cache_r = usage.get("cache_read_input_tokens", 0)
    cache_c = usage.get("cache_creation_input_tokens", 0)
    out_t   = usage.get("output_tokens", 0)
    # Anthropic cache pricing: writes ~1.25x base input, reads ~0.1x base input
    return (
        in_t   * pin[0] / 1_000_000
        + cache_c * pin[0] * 1.25 / 1_000_000
        + cache_r * pin[1] / 1_000_000
        + out_t  * pin[2] / 1_000_000
    )


# ---------------------------------------------------------------------------
# Model fallback resolution
# ---------------------------------------------------------------------------
def resolve_model(api_key: str, tier: str) -> str | None:
    """Try preferred model names in order; return the first that succeeds a probe."""
    probe = {
        "model": "",
        "max_tokens": 8,
        "messages": [{"role": "user", "content": "Reply: OK"}],
    }
    for name in MODEL_TRY_ORDER[tier]:
        probe["model"] = name
        resp, err = call_anthropic(api_key, probe, timeout=15)
        if resp and not err:
            return name
        if err and "not_found" not in err and "model" not in err.lower():
            # transient — try anyway by returning the first option
            return name
    return None


# ---------------------------------------------------------------------------
# Main worker
# ---------------------------------------------------------------------------
def run_one(api_key: str, model: str, paper: dict, criteria: str, prompt_template: str) -> dict:
    body, prompt_hash, criteria_hash = build_request_body(model, paper, criteria, prompt_template)
    t0 = time.time()
    resp, err = call_anthropic(api_key, body)
    latency = time.time() - t0
    if err and not resp:
        # one retry
        time.sleep(1.5)
        t0 = time.time()
        resp, err = call_anthropic(api_key, body)
        latency = time.time() - t0
    rec = {
        "pmid": paper["pmid"],
        "model": model,
        "prompt_hash": prompt_hash,
        "criteria_hash": criteria_hash,
        "latency_s": round(latency, 2),
        "error": err,
    }
    if not resp:
        rec.update(verdict="", domains=[], reason="", parse_error="no_response", cost_usd=0.0,
                   raw="", usage={})
        return rec
    # Extract text block
    text = ""
    for block in resp.get("content", []):
        if block.get("type") == "text":
            text += block.get("text", "")
    usage = resp.get("usage", {})
    parsed = parse_verdict(text)
    rec.update(parsed)
    rec["cost_usd"] = round(cost_for_usage(model, usage), 6)
    rec["usage"]    = usage
    rec["raw"]      = text[:2000]
    return rec


# ---------------------------------------------------------------------------
# CLI subprocess path (no API key needed; uses Claude Code OAuth)
# ---------------------------------------------------------------------------
import subprocess

CLI_SYSTEM_PROMPT = (
    "You output exactly one JSON object and nothing else. "
    "No prose, no preamble, no markdown code fence, no internal reasoning. "
    "Minimize tokens."
)

def build_cli_prompt(paper: dict, criteria: str, prompt_template: str) -> str:
    return (prompt_template
            .replace("<<CRITERIA_VERBATIM>>", criteria)
            .replace("<<PMID>>",     paper["pmid"])
            .replace("<<YEAR>>",     paper["year"])
            .replace("<<JOURNAL>>",  paper["journal"])
            .replace("<<TITLE>>",    paper["title"])
            .replace("<<ABSTRACT>>", paper.get("abstract", "")[:1800]))


def run_one_cli(model: str, paper: dict, criteria: str, prompt_template: str) -> dict:
    prompt_hash   = sha256(prompt_template)
    criteria_hash = sha256(criteria)
    prompt = build_cli_prompt(paper, criteria, prompt_template)
    cmd = [
        "claude", "--print", "--no-session-persistence",
        "--model", model,
        "--output-format", "json",
        "--system-prompt", CLI_SYSTEM_PROMPT,
        "--tools", "",
        "--disable-slash-commands",
        prompt,
    ]
    rec = {
        "pmid": paper["pmid"],
        "model": model,
        "prompt_hash": prompt_hash,
        "criteria_hash": criteria_hash,
    }
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=PER_CALL_TO)
        latency = time.time() - t0
        rec["latency_s"] = round(latency, 2)
        if r.returncode != 0:
            rec.update(verdict="", domains=[], reason="",
                       parse_error=f"cli_returncode={r.returncode}",
                       error=r.stderr[:300], cost_usd=0.0, raw="", usage={})
            return rec
        try:
            j = json.loads(r.stdout)
        except json.JSONDecodeError as e:
            rec.update(verdict="", domains=[], reason="",
                       parse_error=f"cli_json_decode:{e}",
                       error=r.stdout[:300], cost_usd=0.0, raw=r.stdout[:1000], usage={})
            return rec
        text = j.get("result", "") or ""
        usage = j.get("usage", {})
        cost = float(j.get("total_cost_usd", 0.0))
        parsed = parse_verdict(text)
        rec.update(parsed)
        rec["cost_usd"] = round(cost, 6)
        rec["usage"]    = usage
        rec["raw"]      = text[:2000]
        rec["error"]    = None
        return rec
    except subprocess.TimeoutExpired:
        rec.update(verdict="", domains=[], reason="", parse_error="timeout",
                   error="subprocess.TimeoutExpired", cost_usd=0.0, raw="", usage={},
                   latency_s=PER_CALL_TO)
        return rec
    except Exception as e:
        rec.update(verdict="", domains=[], reason="", parse_error=f"{type(e).__name__}",
                   error=str(e)[:300], cost_usd=0.0, raw="", usage={},
                   latency_s=time.time() - t0)
        return rec


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Parse inputs, print plan, do not call API.")
    ap.add_argument("--tier", choices=["opus","sonnet","haiku","all"], default="all")
    ap.add_argument("--limit", type=int, default=0, help="Process first N papers only.")
    ap.add_argument("--via", choices=["api","cli"], default="api",
                    help="api = direct Anthropic Messages API (needs ANTHROPIC_API_KEY). "
                         "cli = `claude --print` subprocess (uses Claude Code OAuth).")
    ap.add_argument("--cost-ceiling", type=float, default=COST_CEILING,
                    help="USD ceiling for total displayed cost; protocol §11.4")
    ap.add_argument("--concurrency", type=int, default=CONCURRENCY)
    args = ap.parse_args()

    # Load inputs
    criteria        = CRIT_TXT.read_text()
    prompt_template = PROMPT_TXT.read_text()
    with RAW_CSV.open() as f:
        papers = list(csv.DictReader(f))
    with HEUR_CSV.open() as f:
        heur = {r["PMID"]: r for r in csv.DictReader(f)}

    if args.limit > 0:
        papers = papers[:args.limit]

    tiers = ["opus", "sonnet", "haiku"] if args.tier == "all" else [args.tier]

    print(f"[plan] n_papers={len(papers)}  tiers={tiers}  concurrency={CONCURRENCY}")
    print(f"[plan] prompt_hash={sha256(prompt_template)[:16]}  criteria_hash={sha256(criteria)[:16]}")
    print(f"[plan] cost_ceiling=${COST_CEILING}  wall_budget_s={WALL_BUDGET_S}")

    if args.dry_run:
        # Show first paper's prompt shape
        body, ph, ch = build_request_body("claude-haiku-4-5", papers[0], criteria, prompt_template)
        sysblk = body.get("system")
        usr = body.get("messages", [{}])[0].get("content", "")
        print(f"[dry-run] system_pin: {sysblk[0]['text'][:80] if isinstance(sysblk, list) else sysblk[:80]}")
        if isinstance(usr, list):
            for i, c in enumerate(usr):
                cc = c.get("cache_control")
                print(f"[dry-run] msg part {i} cache={'yes' if cc else 'no'} bytes={len(c.get('text',''))}")
        return

    api_key = None
    if args.via == "api":
        api_key = resolve_api_key()
        if not api_key:
            print("[stop §11.1] no API key resolvable; switch with --via cli to use Claude Code OAuth", file=sys.stderr)
            sys.exit(2)
        # Resolve actual model dated alias per tier
        resolved = {}
        for t in tiers:
            m = resolve_model(api_key, t)
            if not m:
                print(f"[stop] could not resolve any model for tier={t}", file=sys.stderr)
                sys.exit(2)
            resolved[t] = m
    else:
        # CLI path uses the first preferred dated alias per tier directly
        resolved = {t: MODEL_TRY_ORDER[t][0] for t in tiers}
    print(f"[plan] via={args.via}  resolved models: {resolved}")

    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    total_cost  = 0.0
    malformed   = 0
    started     = time.time()
    all_records = []

    for tier in tiers:
        model = resolved[tier]
        jsonl_path = SCRIPT_DIR / f"run_{ts}_{tier}.jsonl"
        print(f"[run] tier={tier} model={model} -> {jsonl_path.name}")
        with jsonl_path.open("w") as jf:
            header = {
                "_header": True,
                "tier": tier,
                "model": model,
                "n_papers": len(papers),
                "prompt_hash":   sha256(prompt_template),
                "criteria_hash": sha256(criteria),
                "temperature":   TEMPERATURE,
                "max_tokens":    MAX_TOKENS,
                "concurrency":   CONCURRENCY,
                "started_utc":   ts,
            }
            header["via"] = args.via
            jf.write(json.dumps(header) + "\n")
            worker = (lambda p: run_one(api_key, model, p, criteria, prompt_template)) \
                     if args.via == "api" else \
                     (lambda p: run_one_cli(model, p, criteria, prompt_template))
            with cf.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
                futs = {pool.submit(worker, p): p["pmid"] for p in papers}
                done_count = 0
                for fut in cf.as_completed(futs):
                    rec = fut.result()
                    rec["tier"] = tier
                    all_records.append(rec)
                    jf.write(json.dumps(rec) + "\n"); jf.flush()
                    total_cost += rec.get("cost_usd", 0.0)
                    if rec.get("parse_error") or rec.get("error"):
                        malformed += 1
                    done_count += 1
                    if done_count % 20 == 0:
                        elapsed = time.time() - started
                        print(f"  [{tier}] {done_count}/{len(papers)}  "
                              f"cost=${total_cost:.3f}  malformed={malformed}  "
                              f"elapsed={elapsed:.0f}s")
                    # Stop checks per protocol §11
                    if total_cost > args.cost_ceiling:
                        print(f"[stop §11.4] cost ceiling exceeded: ${total_cost:.2f} > ${args.cost_ceiling}", file=sys.stderr)
                        pool.shutdown(wait=False, cancel_futures=True)
                        break
                    if time.time() - started > WALL_BUDGET_S:
                        print(f"[stop §11.3] wall budget exceeded", file=sys.stderr)
                        pool.shutdown(wait=False, cancel_futures=True)
                        break
        malformed_rate = malformed / max(1, len(all_records))
        if malformed_rate > 0.05:
            print(f"[stop §11.2] malformed rate {malformed_rate:.1%} > 5%", file=sys.stderr)
            break

    # Flat CSV merge
    print(f"[done] total_cost=${total_cost:.3f}  n_records={len(all_records)}  malformed={malformed}")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pmid", "tier", "model", "heuristic_verdict", "llm_verdict",
                    "llm_domains", "agreement", "parse_error", "error", "latency_s", "cost_usd"])
        for rec in all_records:
            hv = heur.get(rec["pmid"], {}).get("Screening_Decision", "")
            lv = rec.get("verdict", "")
            agreement = "yes" if hv == lv and hv else ("no" if (hv and lv) else "missing")
            w.writerow([
                rec["pmid"], rec.get("tier",""), rec.get("model",""),
                hv, lv, "|".join(rec.get("domains") or []),
                agreement,
                rec.get("parse_error") or "",
                (rec.get("error") or "")[:200],
                rec.get("latency_s",""),
                rec.get("cost_usd",""),
            ])
    print(f"[done] wrote {OUT_CSV}")


if __name__ == "__main__":
    main()
