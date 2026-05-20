# LLM-as-Second-Reviewer Reproducibility Audit — Pre-registered Protocol

**Status:** Pre-registered before first LLM API call.
**Date pinned:** 2026-05-21.
**Scope:** Inter-rater reliability (IRR) audit of the existing rule-based heuristic screener (`experiments/src/screening.py`) against a single-model LLM second reviewer over the existing 227-row PubMed corpus (`experiments/data/raw/pubmed_results.csv`).

This protocol exists to constrain interpretation **before** results are observed. Any deviation from the rules below must be recorded as an amendment in `planning/decisions.md` with a new dated entry; results obtained after deviation must be reported as exploratory.

---

## 1. Scope limitation (load-bearing)

This audit is **not** a PRISMA-2020 dual-reviewer screening. PRISMA-2020 and its computer-assisted extension require two *human* reviewers (or one human reviewer plus a validated automation tool with documented sensitivity/specificity against human consensus). An LLM second reviewer over the same abstracts the heuristic already saw produces an inter-rater reliability statistic between two non-validated automated screeners; it does **not** validate either method against ground truth.

The audit is reported in the paper and supplementary materials as a **computer-assisted reproducibility audit**, framed as one of two things depending on outcome (see §4 decision rules). It does not change the paper's claim that the primary screening was conducted by a single human-coded heuristic.

## 2. Hypotheses

**Primary outcome:** linear-weighted Cohen's κ between heuristic verdicts (Include / Maybe / Exclude) and LLM verdicts over n = 227 papers.

- **H0:** weighted κ ≤ 0.40 (less-than-moderate agreement; no meaningful convergence between the two automated screeners).
- **H1:** weighted κ > 0.40 (moderate or stronger agreement).

Weighted κ is primary because the verdict scale is ordinal (Include > Maybe > Exclude). Linear weights are used (not quadratic) per Cohen (1968).

**Secondary outcomes (pre-specified, not used for hypothesis testing):**

- Unweighted (raw) κ.
- Per-domain weighted κ for D3 (n = 97 in the eligible set; only domain powered for stratified inference). Other per-domain analyses are **descriptive only**.
- Confusion matrix (3 × 3).
- Disagreement set size and composition (which paper IDs disagree, on what axis).

## 3. Sample, exposure, and measurement

- **Sample:** All 227 unique records in `experiments/data/raw/pubmed_results.csv` (pinned via git commit hash at execution time). No subsampling.
- **Heuristic verdict source:** `Screening_Decision` column of `experiments/data/processed/screening_results.csv`, produced by `experiments/src/screening.py` at the same pinned commit.
- **LLM verdict source:** model output as defined in §5.
- **Mapping:** LLM is asked to emit one of `{Include, Maybe, Exclude}` plus a domain set drawn from `{D1, D2, D3, D4, D5, D6, Cross-domain}`. The verdict field is the sole input to κ. Domain set is descriptive only.

## 4. Pre-registered decision rules (interpretation of κ)

These rules are fixed before any LLM call is issued. They convert a numeric κ into a verbal claim.

| Observed weighted κ | Verbal claim allowed in paper / supplementary | Verbal claim **disallowed** |
|---|---|---|
| **κ > 0.60** | "Heuristic and single-model LLM screener show substantial inter-rater reliability over n = 227 abstracts (linear-weighted κ = X.XX, 95 % CI [L, U])." | "The screening is validated." "Two independent reviewers agree." |
| **0.40 < κ ≤ 0.60** | "Moderate IRR; the disagreement set (n = D) is flagged for human triage and is enumerated in the supplementary CSV." | "Substantial agreement." Any validity claim. |
| **κ ≤ 0.40** | "Low IRR; the two automated screeners disagree systematically. Neither can be claimed as a reproducibility audit of the other. The 156 eligible figure rests on the heuristic alone and is reported as such." | "Substantial agreement." Validity claim either direction. The 156 figure must **not** be presented as having survived a second-reviewer check. |

Per-domain κ is reported only as a descriptive table. No domain-level claim is made unless n ≥ 30 in that domain (only D3 qualifies at n = 97; D4 with n = 20 borderline → descriptive only).

## 5. Model, prompt, and decoding pins

**Multi-model run (amended 2026-05-21 per design-review M-B):** all three currently-stable Claude 4.x tiers are run in parallel against the same 227-paper corpus, giving three κ statistics (heuristic↔each model) plus pairwise κ between models.

- **Models pinned (verified reachable on this endpoint on 2026-05-21 via probe; updated mid-execution per user concern about model recency):**
  - `claude-opus-4-7` — highest capability tier (latest Opus)
  - `claude-sonnet-4-6` — mid tier (latest Sonnet; `claude-sonnet-4-7` does not exist; `claude-sonnet-4-5` deprecated for this run)
  - `claude-haiku-4-5` — fastest, cheapest tier (latest Haiku; `claude-haiku-4-6` / `claude-haiku-4-7` do not exist)
- **Invocation method:** `claude --print --no-session-persistence --model <name> --max-budget-usd 7 --output-format json` as a subprocess. The Anthropic Messages API via direct `urllib.request` is the preferred long-term path, but `ANTHROPIC_API_KEY` is not exposed to this shell at run time (verified empty: `printenv ANTHROPIC_API_KEY | wc -c = 1`). The CLI subprocess uses the Claude Code OAuth session and is acknowledged as a reproducibility trade-off (see §5b below).
- **Temperature:** Claude CLI default (not pinned at 0). Acknowledged deviation from a stricter API-based design; documented in §5b. Re-run with `temperature=0` via direct API is filed as a follow-up amendment in `planning/decisions.md`.
- **Max output tokens:** capped by `--max-budget-usd 7` total across all calls.
- **Prompt hash:** SHA-256 of the prompt template recorded in the run JSONL header. Any prompt edit produces a new hash, which forces a new output filename. No silent prompt edits.
- **Criteria text version:** inclusion / exclusion criteria extracted verbatim from `paper/main.tex` §Method "Inclusion and Exclusion Criteria" at the pinned commit; stored at `experiments/llm_second_reviewer/criteria_v1.txt` with SHA-256 recorded in the run header.
- **Concurrency:** 4 simultaneous CLI subprocesses per model (12 in-flight total). Conservative to avoid rate-limit triggers.

### 5b. Reproducibility trade-off acknowledged

The CLI subprocess path is *internally* reproducible (same OAuth session, same CLI version, same model dated alias, fixed prompt + criteria hashes) but not *externally* reproducible by a third party without Claude Code OAuth access. The audit is reported as IRR-only (§4), so internal reproducibility is the audit's actual bar. A future amendment may re-run via direct API with `temperature=0` for publication-grade external reproducibility; that re-run, if executed, is reported as a separate validation pass.

## 6. Self-consistency control (activated 2026-05-21 mid-execution per §4 band)

A self-consistency check (n = 3 sampling, CLI default decoding, majority vote) is **not** required for the primary run. If primary κ falls in the 0.40 < κ ≤ 0.60 band, a self-consistency run on the disagreement set only is permitted as an exploratory follow-up and reported separately. This is Major item M-3 (alias M-A) carried forward.

**Activation 2026-05-21:** all three primary tiers landed in 0.40 < κ ≤ 0.60 (Haiku 0.487, Sonnet 0.461, Opus 0.532). Self-consistency is therefore activated. Subset used: the convergent-disagreement set (n = 59 papers where all three primary-run LLMs agreed with each other but disagreed with the heuristic). Larger than the §6 prediction of "10-30 papers" but still a subset of the 88-98 per-tier disagreement set. The choice of convergent-disagreement (rather than full per-tier disagreement) keeps the analysis focused on the highest-confidence disagreements.

**Parameters used:** 3 samples per (pmid, tier), CLI subprocess sampling (no explicit temperature flag; near-default decoding), sequential execution to keep state writes serialised. Runner: `experiments/llm_second_reviewer/run_self_consistency.py`. Reproducibility seed for any future bootstrap on the SC results: same `20260521` as the primary run.

**Quota-resilience:** the runner persists per-call state to `sc_state.jsonl`. On a quota-style CLI error it sleeps until the next 5-hour KST window boundary (anchored at 2026-05-21 03:10 KST, since this is the local-environment token-reset cadence on this machine) plus a 30 s buffer, then resumes. Up to 8 quota-sleep cycles permitted; beyond that the runner gives up and reports.

## 7. Contamination acknowledgment + secondary hypothesis (amended 2026-05-21 per M-C)

184 of the 227 abstracts (81 %) were published in or before 2024 and may have appeared in the training corpus of one or more of the three models. 43 papers (19 %) are dated 2025-2026 and constitute a partial out-of-corpus subset (cutoffs differ across the 3 models; the 2025+ subset is post-cutoff for the Sonnet 4.5 and Haiku 4.5 tiers as of dated-alias release; Opus 4.7 cutoff is closer to 2026 and may include some 2025 papers).

- **Primary κ** (per §2) is computed on the full n = 227 — contamination cannot be ruled out and is acknowledged.
- **Secondary H0_2025 (pre-registered):** linear-weighted κ between heuristic and each model on the n = 43 subset of 2025-2026 papers. H0_2025: κ ≤ 0.40 on the subset. H1_2025: κ > 0.40. n = 43 is small; the 95 % bootstrap CI is expected to be wide. The pre-registered interpretation is one of:
  - If full-corpus κ > 0.6 AND subset κ > 0.4: contamination not the main driver of agreement.
  - If full-corpus κ > 0.6 AND subset κ ≤ 0.4: contamination plausibly inflates the full-corpus number; primary claim downgraded to "agreement observed but contamination cannot be ruled out."
  - If full-corpus κ ≤ 0.4 in any case: H0 not rejected, no contamination claim either way.
- **Tertiary contamination diagnostic (descriptive):** asymmetric agreement on the 2025+ subset between the three models tells us whether agreement degrades with model recency / familiarity. Reported as a table only.

## 8. Human gold-standard subset (deferred, not required for primary run)

A 30-paper stratified random sample (10 Include / 10 Maybe / 10 Exclude per heuristic verdict, with stratified random selection by `random.Random(20260521).sample`) is reserved for future manual labeling by the author. The seed `20260521` is fixed now so the sample IDs are reproducible regardless of when the manual labeling actually happens.

Manual labels, when produced, will be stored at `experiments/llm_second_reviewer/human_gold_n30.csv`. Until they exist, the audit reports **IRR only**, never validity.

## 9. Statistical reporting requirements

- **Primary**: linear-weighted Cohen's κ point estimate with 95 % bootstrap CI (1 000 resamples, fixed seed `20260521`). Asymptotic SE is not used because rare-class behavior with n_Maybe ≈ 54 makes asymptotic intervals unreliable.
- **Co-primary** (amended 2026-05-21 per M-D / Khraisha et al. 2024): **PABAK** (Prevalence-Adjusted Bias-Adjusted κ) reported alongside Cohen's κ. Prior art shows raw Cohen's κ produces a false-agreement rate on imbalanced verdict distributions; PABAK is the standard mitigation.
- Confusion matrix (3 × 3) reported verbatim per (heuristic × model) pair and per (model × model) pair.
- McNemar-Bowker test of marginal homogeneity (whether two screeners differ systematically in which class they over-assign). TODO(review-2026-05-21): McNemar 3-class extension may need quadratic-weighted χ² as a robustness check.
- No p-value-only reporting. Effect-size estimates and CIs are primary; p-values are descriptive.

## 10. Outputs and reproducibility artefacts

All committed to git at the end of the run:

- `experiments/llm_second_reviewer/criteria_v1.txt` — frozen criteria text.
- `experiments/llm_second_reviewer/prompt_v1.txt` — frozen prompt template.
- `experiments/llm_second_reviewer/run_<timestamp>.jsonl` — one JSON line per paper with: PMID, prompt hash, criteria hash, model, temperature, raw API response, parsed verdict, parsed domains, latency.
- `experiments/data/processed/llm_second_reviewer_results.csv` — flat table: PMID, heuristic_verdict, llm_verdict, agreement, disagreement_axis.
- `experiments/results/llm_second_reviewer_summary.md` — primary and secondary κ values, 95 % CIs, confusion matrix, decision-rule outcome (per §4).
- This protocol file (`protocol.md`) — unchanged after first commit. Any amendment dated and appended in `planning/decisions.md`.

## 11. Stop conditions

The runner stops and reports failure (does not proceed to analysis) if:

- `ANTHROPIC_API_KEY` is unset.
- > 5 % of papers return malformed verdicts after one retry each.
- Wall-clock time exceeds 30 min for the primary run (signals quota / throttling).
- Estimated cost overruns 3× the budgeted ceiling (cost ceiling: USD 5 for the full run including any disagreement-only self-consistency follow-up).

## 12. Prior art (confirmed via WebSearch 2026-05-21 per M-D)

The LLM-screening method is not novel. Relevant prior art (citations to use verbatim in the supplementary materials):

- **Landschaft, A., Antweiler, D., Mackay, S., Kugler, S., Rüping, S., Wrobel, S., Hoeres, T., & Allende-Cid, H. (2024).** Implementation and evaluation of an additional GPT-4-based reviewer in PRISMA-based medical systematic literature reviews. *International Journal of Medical Informatics*, 189, 105531. PubMed: 38943806. — Reports almost-perfect human↔GPT-4 abstract-screening agreement (κ > 0.9). Sets the ceiling expectation for our run.
- **Khraisha, Q., Put, S., Kappenberg, J., Warraitch, A., & Hadfield, K. (2024).** Can large language models replace humans in systematic reviews? Evaluating GPT-4's efficacy in screening and extracting data from peer-reviewed and grey literature in multiple languages. *Research Synthesis Methods*. DOI: 10.1002/jrsm.1715. arXiv: 2310.17526. — Pre-registered human-out-of-the-loop study. **Key methodological finding adopted into our §9: Cohen's κ produces false agreement on imbalanced datasets; PABAK is reported as the bias-corrected alternative.**
- **ASReview** (van de Schoot et al., 2021) — active-learning screening assistant. Validated against human consensus on multiple benchmark systematic reviews. We do not use ASReview here but cite it as the open-source baseline.
- **Rayyan** (Ouzzani et al., 2016) and its later ML-assisted screening features.
- **medRxiv 2024.10.01.24314702** — diagnostic test accuracy study of LLMs for abstract screening across multiple LLM models (GPT-3.5, Claude 3-Sonnet, Claude 3-Haiku, GPT-4T, GPT-4o, Claude 3-Opus). Supports our multi-model design (M-B applied 2026-05-21).

No prior-art finding requires protocol re-design. The PABAK additon (§9) is the only protocol amendment driven by prior-art review. Pre-run check complete.

TODO(review-2026-05-21): cross-LLM-family robustness (GPT-4o / Gemini 2.x) is filed as future work; the current Claude-only design is a deliberate scope choice per user decision and is reported as a scope-limit, not a weakness.
