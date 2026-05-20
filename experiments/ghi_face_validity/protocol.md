# GHI Face-Validity Audit — Pre-registered Protocol

**Status:** Pre-registered before first LLM call.
**Date pinned:** 2026-05-21.
**Scope:** Three-model LLM face-validity check of an 18-item Game Hoarding Inventory (GHI) draft against the King et al. (2020) over-pathologization framework.

This protocol exists to constrain interpretation **before** results are observed. Any deviation must be recorded as an amendment in `planning/decisions.md`.

---

## 1. Scope limitation (load-bearing)

This audit is **not** a psychometric validation of the GHI. Psychometric validation requires (a) expert panel review, (b) cognitive interviews with target users, (c) EFA / CFA on a sample of n ≥ 300, (d) convergent / discriminant validity against established instruments (SI-R, DHQ, OCI-R), and (e) test-retest reliability. None of this is delivered here.

The audit is reported in the paper and supplementary materials as a **pre-emptive face-validity screen** that asks: given the King et al. (2020) over-pathologization criteria, do three independent Claude family models flag any of the 18 draft items as likely to pathologize normal gaming engagement? The output identifies items to revise before any human-subjects work; it does **not** establish that the un-flagged items are valid measures of hoarding.

The §11 GHI section of `paper/main.tex` is updated to (a) include the 18 draft items verbatim and (b) report the LLM-flag rate per item per criterion, framed strictly as "items to revise before Phase 2 expert panel review."

## 2. Hypotheses (descriptive, no point-null inference)

The audit is exploratory; no falsifiable point null. Reported descriptively per protocol §4:

- Per-item violation rate across 3 criteria × 3 models (9 judgments per item).
- Per-criterion violation rate across all 18 items × 3 models.
- Cross-model agreement on which items flag.

## 3. Sample and exposure

- **18 candidate items** (frozen at `experiments/ghi_face_validity/items_v1.json`).
  - 4 items each for primary domains D3 (gacha/loot box), D4 (inventory paralysis), D5 (completionism) — 12 items.
  - 2 items each for exploratory domains D2 (consumable hoarding), D6 (backlog accumulation) — 4 items.
  - 2 cross-domain items (loss aversion, emotional attachment) — 2 items.
  - All items are stem candidates only; response anchors and scoring are out of scope here.
- **3 criteria** from King et al. (2020) "Face validity evaluation of screening tools for gaming disorder: Scope, language, and overpathologizing issues" (*Journal of Behavioral Addictions*, 9(1), 1-13). Verbatim definitions are in `experiments/ghi_face_validity/criteria_v1.txt`.
- **3 models** (latest reachable per the 2026-05-21 endpoint probe in `planning/decisions.md`):
  - `claude-opus-4-7`
  - `claude-sonnet-4-6`
  - `claude-haiku-4-5`

Total calls = 18 × 3 × 3 = **162**.

## 4. Pre-registered decision rules

Per-item interpretation rules, fixed before observation:

| Flag count for item (out of 9 judgments) | Allowed claim |
|---|---|
| ≥ 6 / 9 flag the item on at least one criterion | "Item flagged for revision." Paper §11 lists the criterion text and at least one verbatim model reason. |
| 3-5 / 9 flag | "Item under review." Paper §11 notes the borderline status. |
| ≤ 2 / 9 flag | "Item provisionally retained." Paper §11 includes the item without flag. |

Per-criterion interpretation rule:

| Criterion-wide flag rate (flagged items / 18) | Interpretation |
|---|---|
| ≥ 50 % | The 18-item draft has a systemic problem with this criterion; redesign is needed before any human-subjects use. |
| 20-49 % | Significant criterion-specific revision needed. |
| < 20 % | Criterion handled adequately by the draft. |

No psychometric claim is allowed at any flag rate.

## 5. Model, prompt, and decoding pins

- **Invocation:** `claude --print --no-session-persistence --model <name> --output-format json` as a subprocess (consistent with `experiments/llm_second_reviewer/run.py`). Same CLI temperature default; reproducibility is internal (Claude Code OAuth session) not external.
- **Concurrency:** 4 (consistent with the self-consistency runner).
- **Max output tokens:** capped by `--max-budget-usd` flag.
- **Prompt hash + criteria hash** (SHA-256) recorded in the run JSONL header.

## 6. Quota resilience

The runner persists per-call state to `runs/sc_face_state.jsonl`. On a quota-style CLI error it sleeps until the next 5-hour KST window boundary (anchored at 2026-05-21 03:10 KST) plus a 30 s buffer, then resumes. Same logic as `experiments/llm_second_reviewer/run_self_consistency.py`.

## 7. Statistical reporting

- Per-item flag count (0-9).
- Per-criterion flag rate (flagged items / 18 × 3 models = / 54).
- Cross-model agreement: for each (item, criterion) cell, fraction of models flagging. A cell is "model-unanimous flag" if all 3 models flag; "majority flag" if 2 of 3; "minority flag" if 1 of 3.
- No bootstrap CI (n is small; the audit is descriptive).

## 8. Outputs

All committed to git:

- `experiments/ghi_face_validity/items_v1.json` — frozen 18-item draft.
- `experiments/ghi_face_validity/criteria_v1.txt` — verbatim King et al. (2020) criteria.
- `experiments/ghi_face_validity/prompt_v1.txt` — frozen prompt template.
- `experiments/ghi_face_validity/state.jsonl` — one line per call, with SHA-256 hashes in the header.
- `experiments/data/processed/ghi_face_validity_results.csv` — flat (item × criterion × model) table.
- `experiments/results/ghi_face_validity_summary.md` — analysis report.
- This protocol (`protocol.md`) — unchanged after first commit.

## 9. Stop conditions

- > 5 % malformed outputs after one retry → abort, report.
- Wall time > 30 min → abort, report.
- Estimated cost overruns $10 ceiling → abort.

## 10. Prior art

- King, D.~L., Chamberlain, S.~R., Carragher, N., Billieux, J., Stein, D., et al. (2020). Face validity evaluation of screening tools for gaming disorder: Scope, language, and overpathologizing issues. *Journal of Behavioral Addictions*, 9(1), 1-13. — Anchors all three criteria definitions.
- Bean, A.~M., et al. (2017). Video game addiction: The push to pathologize video games. *Professional Psychology: Research and Practice*, 48(5), 378-389. — Cited as the original overpathologization-warning paper; reasoning is included in the criteria text to ensure the LLM understands the historical concern.
- Aarseth, E., et al. (2017). Scholars' open debate paper on the WHO ICD-11 Gaming Disorder proposal. *Journal of Behavioral Addictions*, 6(3), 267-270. — Same.

Item generation grounded in:
- Frost & Hartl (1996), CBT model of hoarding (information processing deficits, emotional attachment, behavioral avoidance, erroneous beliefs).
- DSM-5 Hoarding Disorder criteria (APA, 2013).
- This paper's §3 evidence by domain (D1 loss aversion, D2 consumable, D3 gacha/loot box, D4 inventory paralysis, D5 completionism, D6 backlog accumulation).
