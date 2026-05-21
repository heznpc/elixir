# D3 Study-Design Audit — Pre-registered Protocol

**Status:** Pre-registered before first LLM call.
**Date pinned:** 2026-05-21.
**Scope:** Three-model LLM re-classification of every D3-tagged paper's study design, to test whether `paper/main.tex` §3.3's design distribution table survives an independent reclassification.

This protocol exists to constrain interpretation **before** results are observed. Any deviation must be recorded as an amendment in `planning/decisions.md`.

---

## 1. Scope limitation (load-bearing)

This audit is **not** a re-screening of D3 — eligible/not is held constant per the primary heuristic. The audit asks only: of the papers the heuristic placed in D3, what study designs do the three Claude models assign?

The output answers one question: does the paper §3.3 sentence

> "Study design distribution: Cross-sectional surveys (n=43), unspecified designs (n=35), longitudinal studies (n=9), systematic reviews and meta-analyses (n=4), scale validation studies (n=3), reviews and commentaries (n=3), experimental studies (n=2), qualitative studies (n=2), and content analyses (n=1)."

survive an LLM re-classification? Specifically:
- The 9 longitudinal claim is load-bearing for the paper's "moderate-to-strong evidence" framing of D3.
- The 35 "unspecified designs" is heuristic-uncertain; we ask whether the LLMs assign these to a real category.

The audit does **not** validate the LLM verdicts — it only quantifies disagreement.

## 2. Sample

102 D3-tagged papers extracted from `experiments/data/processed/screening_results.csv` where `Screening_Decision ∈ {Include, Maybe}` and the `Domain(s)` field contains "D3". 102 papers vs the paper's reported 97 — the 5-paper discrepancy is recorded as a finding (see §7).

Subset frozen at `experiments/d3_design_audit/data/d3_corpus.csv` (title + abstract + journal + year per paper).

## 3. Hypotheses

Descriptive. For each design category, compare:
- Paper §3.3 claimed count (from heuristic + manual review)
- LLM-classified count (majority verdict across 3 models)

Pre-registered decision rule for each category:

| |LLM count − paper count| / paper count | Verbal claim allowed |
|---|---|
| < 20 % | Paper claim survives. |
| 20-50 % | Paper claim is approximate; revise count with ±range in §3.3. |
| > 50 % | Paper claim does not survive. §3.3 table requires line revision. |

For the load-bearing **longitudinal-9 claim**, a per-paper LLM majority must confirm at least 6 of the 9 papers as longitudinal for the claim to stand without revision.

## 4. Model, prompt, and decoding pins

- Models: `claude-opus-4-7`, `claude-sonnet-4-6`, `claude-haiku-4-5` (same triple as the primary IRR audit).
- Invocation: `claude --print --no-session-persistence --model <name> --output-format json` subprocess, same pattern as `experiments/llm_second_reviewer/run.py`.
- Concurrency: 4.
- Prompt hash + criteria hash recorded in JSONL header.
- Categories the LLM must select from (verbatim from paper §3.3, in the same order):
  - `cross_sectional` — Cross-sectional surveys
  - `unspecified` — Not clearly assignable from title+abstract
  - `longitudinal` — Longitudinal / prospective designs
  - `systematic_review` — Systematic reviews / meta-analyses
  - `scale_validation` — Scale validation / psychometric studies
  - `review_commentary` — Narrative reviews, commentaries, editorials
  - `experimental` — Experimental / quasi-experimental
  - `qualitative` — Qualitative interviews / focus groups / ethnography
  - `content_analysis` — Content analyses of game / loot-box patterns
- Each call returns one category + 1-sentence reason.

## 5. Quota resilience

Same pattern as `experiments/llm_second_reviewer/run_self_consistency.py`: state file at `experiments/d3_design_audit/state.jsonl`; on quota error sleep until next KST window + 30 s, up to 8 cycles.

## 6. Outputs

- `experiments/d3_design_audit/state.jsonl`
- `experiments/data/processed/d3_design_audit_results.csv`
- `experiments/results/d3_design_audit_summary.md`

## 7. Stop conditions / known discrepancies

- > 5 % malformed → abort.
- Wall > 30 min → abort.
- Cost > $20 → abort.

**Known discrepancy**: heuristic CSV gives 102 D3-tagged papers (92 Include + 10 Maybe) at this commit. Paper §3.3 reports 97 (91 + 6). The 5-paper gap is left as-is; the audit runs on the 102 actually present in the CSV. The finding will be reported as a §7 "paper count discrepancy" in `planning/decisions.md`.

## 8. Prior art

Same as `experiments/llm_second_reviewer/protocol.md` §12 — Landschaft et al. 2024, Khraisha et al. 2024. No protocol amendment driven by prior art for this audit specifically.
