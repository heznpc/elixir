"""
Shared dedup helpers for runner state JSONLs.

Background: runners append per-call records to a state.jsonl. When a call
fails (parse_error / call_failed / is_error), the record is written with
verdict='' (or design=''). On the next invocation, load_done() correctly
treats those records as not-yet-done and retries them. The retry, on
success, appends a SECOND record for the same key — so the JSONL now
contains both an error row and a success row for the same call.

If the CSV merge / dashboard / per-call dataset iterate the JSONL line by
line without dedup, they double-count the retry.

Shape of a "key" varies by experiment:
  llm_2rev_primary    : (pmid, tier)
  llm_2rev_sc         : (pmid, tier, sample_idx)
  ghi_face            : (item_id, criterion, tier)
  d3_design           : (pmid, tier)
  openalex_*_recheck  : (openalex_id, tier)

The helper takes a key extractor and a "success" predicate and returns the
deduped list of records — keep the last successful record per key; if no
success, keep the last record (the latest error attempt).

Usage:
    from experiments._lib.jsonl_dedup import dedup_state_records

    deduped = dedup_state_records(
        records,
        key_fn=lambda d: (d.get("pmid"), d.get("tier"), d.get("sample_idx")),
        success_fn=lambda d: bool(d.get("verdict")),
    )
"""

from __future__ import annotations

from typing import Callable, Iterable, Sequence


def dedup_state_records(
    records: Iterable[dict],
    key_fn: Callable[[dict], tuple],
    success_fn: Callable[[dict], bool],
) -> list[dict]:
    """Return list of records with at most one entry per key.

    Per key, prefer the last successful record (success_fn returns True).
    If no record for a key is successful, return the last record seen
    (which preserves the latest error context for debugging).
    Records whose key_fn raises or returns a key containing None in
    every position are passed through as-is (header rows / malformed
    entries — caller's responsibility to filter beforehand if desired).
    """
    success_by_key: dict[tuple, dict] = {}
    last_by_key: dict[tuple, dict] = {}
    order: list[tuple] = []
    for rec in records:
        try:
            k = key_fn(rec)
        except Exception:
            order.append(("__passthrough__", id(rec)))
            success_by_key[("__passthrough__", id(rec))] = rec
            last_by_key[("__passthrough__", id(rec))] = rec
            continue
        if k not in last_by_key:
            order.append(k)
        last_by_key[k] = rec
        if success_fn(rec):
            success_by_key[k] = rec
    out: list[dict] = []
    seen: set = set()
    for k in order:
        if k in seen:
            continue
        seen.add(k)
        out.append(success_by_key.get(k, last_by_key[k]))
    return out


def is_success_verdict(d: dict) -> bool:
    """Standard success predicate for runners writing a 'verdict' field."""
    return bool(d.get("verdict"))


def is_success_design(d: dict) -> bool:
    """Standard success predicate for runners writing a 'design' field."""
    return bool(d.get("design"))


def is_success_verdict_or_design(d: dict) -> bool:
    """Composite predicate covering both runner families."""
    return bool(d.get("verdict")) or bool(d.get("design"))


def key_pmid_tier(d: dict) -> tuple:
    return (d.get("pmid"), d.get("tier"))


def key_pmid_tier_sample(d: dict) -> tuple:
    return (d.get("pmid"), d.get("tier"), d.get("sample_idx"))


def key_item_criterion_tier(d: dict) -> tuple:
    return (d.get("item_id"), d.get("criterion"), d.get("tier"))


def key_openalex_tier(d: dict) -> tuple:
    return (d.get("openalex_id"), d.get("tier"))
