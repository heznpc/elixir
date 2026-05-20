# Research Decisions Log

Records non-obvious choices with rationale. Append-only; don't rewrite history.

Format: `## YYYY-MM-DD — <short title>` followed by **Context**, **Decision**, **Why**.

---

## 2026-04-19 — Repository restructure to DDD-style layout

**Context**: Top level had manuscript.md (72KB), outline.md (52KB), paper/main.tex, TODO.md, review.md all co-located. experiments/ had v1/v2 duplicates distinguished by filename suffix.

**Decision**: Adopt bounded-context layout — `paper/` (domain), `experiments/` (application with src/data/results/archive), `planning/` (meta: TODO, review, decisions), `literature/` (external knowledge). v2 filenames collapse to canonical names; v1 moves to `experiments/archive/`.

**Why**: File proliferation was making it hard to find the current state of anything. Versioning is git's job; filename suffixes duplicate that job. Separation gives each concern one obvious home.

---

## OPEN — Extract bibliography to references.bib

**Context**: `paper/main.tex` uses inline `\begin{thebibliography}` rather than a separate `references.bib` + `\bibliography{references}`.

**Decision pending**: Extract once. Enables BibTeX workflow and shared bib across future related papers.

---

## 2026-05-21 — Pre-registered LLM-as-second-reviewer reproducibility audit

**Context**: `planning/review.md` §3.1 flagged single-reviewer + automated-heuristic screening as the largest single reject risk for the systematic review. A pre-execution design review (this session, see git log) identified four critical issues that, if unaddressed, would have made an LLM-second-reviewer experiment uninterpretable: (1) no falsifiable hypothesis or pre-registered cutoff, (2) no human ground-truth subset, (3) risk of misframing an LLM screener as a PRISMA-2020 dual reviewer, (4) no reproducibility pins (model, prompt, criteria text).

**Decision**:

1. Pre-register the audit as an **inter-rater reliability check between two automated screeners**, not as PRISMA-2020 dual screening or as validation of either screener. Full protocol committed at `experiments/llm_second_reviewer/protocol.md` and pinned at this commit hash.
2. Primary outcome is **linear-weighted Cohen's κ** with 95 % bootstrap CI (1 000 resamples, seed `20260521`). H0: κ ≤ 0.40; H1: κ > 0.40. Decision rules for verbal interpretation of κ are fixed in §4 of the protocol; verbal claims allowed at each band are listed exhaustively.
3. Model pinned: `claude-sonnet-4-5-20250929`, temperature 0, prompt SHA-256 and criteria-text SHA-256 recorded in the run JSONL header.
4. Human gold-standard subset (stratified n = 30, seed `20260521`) is **deferred, not blocking**. Until manual labels exist, the audit reports IRR only, never validity. The sample IDs are reproducible regardless of when labeling happens.
5. `paper/main.tex` amended: §Method "Screening Process" now states the heuristic was single rule-based (not human dual reviewers); §Limitations adds a "Screening methodology" paragraph framing the supplementary LLM audit as an IRR check, not PRISMA-2020 dual screening.

**Why**: A reviewer who reads "two independent reviewers, κ = 0.7" and then discovers one of them is an LLM that saw the same abstracts as the heuristic will reject for misrepresentation. Scope-limiting the claim before observation eliminates the post-hoc reframing temptation and addresses `review.md` §3.1 honestly. The protocol's decision-rule table converts a numeric κ into a fixed verbal claim, removing HARKing latitude.

**Contamination note (initial)**: 184 of 227 abstracts (81 %) are dated ≤ 2024 and may be in the model training corpora. 43 are 2025-2026.

---

## 2026-05-21 — LLM second-reviewer protocol amendments after Major-decision pass

**Context**: After the initial pre-registration (entry above), the design-review Major-decision pass (M-A through M-D) and a shell-environment probe produced four protocol amendments. Recorded here before any LLM call is issued.

**Decisions**:

1. **M-B (multi-model, revised)**: user requested Claude-family multi-model with Opus 4.7 as primary. Protocol §5 amended from single-model (Sonnet 4.5) to three-model parallel: `claude-opus-4-7`, `claude-sonnet-4-5`, `claude-haiku-4-5`. All three verified reachable on the configured endpoint via `claude --print --model <name>` smoke test on 2026-05-21. `claude-sonnet-4-7` was probed and is not available; not used.
2. **M-C (2025+ secondary hypothesis)**: pre-registered. Protocol §7 amended. H0_2025: weighted κ on n=43 ≤ 0.40. Three interpretation branches documented.
3. **M-D (prior-art WebSearch front-loaded)**: completed before run. Two queries returned Landschaft et al. 2024 (PubMed 38943806; κ > 0.9 ceiling expectation) and Khraisha et al. 2024 (DOI 10.1002/jrsm.1715; PABAK adoption). Protocol §9 amended to add PABAK as co-primary alongside weighted Cohen's κ. Protocol §12 updated with verified citations.
4. **M-A (self-consistency)**: held as deferred per recommendation. No change.
5. **Environment substitution (Critical, emerged during fix-execution)**: `ANTHROPIC_API_KEY` is empty in the Claude Code shell (`printenv ANTHROPIC_API_KEY | wc -c = 1`). Direct Anthropic Messages API call via `urllib.request` is therefore not possible without user intervention. Substituted to `claude --print --no-session-persistence --model <name>` CLI subprocess, which uses the Claude Code OAuth session. **Trade-off**: CLI subprocess does not expose `--temperature`, so the protocol §5 temperature pin (`0.0`) is relaxed to "CLI default". This is an internal-reproducibility downgrade documented in protocol §5b. The audit is reported as IRR-only per §1, which makes the temperature relaxation a tolerable cost. A future re-run via direct API with `temperature=0` is filed as follow-up.

**Why**: The audit is meant to address `review.md` §3.1 (largest reject risk). Front-loading prior art (M-D) caught the PABAK improvement before observation, preventing post-hoc reframing. Multi-model (M-B) eliminates single-model dependency, the second-largest external-validity risk. Pre-registering H0_2025 (M-C) gives contamination a falsifiable test instead of a hand-wave. The CLI substitution is the smallest deviation that lets the experiment actually run today without blocking on env-key provisioning, and is recorded with the precise reason and consequence.

---

## 2026-05-21 (mid-execution) — Sonnet bump from 4.5 to 4.6

**Context**: After the haiku tier finished (κ_w = 0.487, moderate band) and while the sonnet tier was running on `claude-sonnet-4-5`, user flagged "opus 4.7 나왔는데 지금 너무 옛날 모델로만 돌리는 건 아닌지?" Re-probed the endpoint for newer dated aliases.

**Probe result (2026-05-21)**:
- Opus: 4-7 (newest), 4-6, 4-5 all reachable.
- Sonnet: **4-6 reachable**, 4-7 does not exist on this endpoint.
- Haiku: only 4-5 reachable (no 4-6, no 4-7).

**Decision**:
1. Aborted in-progress sonnet-4-5 run at ~53/227 records. Partial JSONL renamed to `*.aborted-sonnet-4-5` and **not** ingested by `analyze.py` (the JSONL glob is `run_*.jsonl`, suffixed file excluded). Sunk cost ≈ $2 (one-shot, accepted).
2. Updated `run.py` MODEL_TRY_ORDER so the sonnet tier preferentially resolves to `claude-sonnet-4-6` with `claude-sonnet-4-5` as fallback. Pricing table extended.
3. Updated protocol §5 model pin list. Haiku stays at 4-5 because no newer dated alias exists.

**Why**: The audit is reported as IRR; if reviewers later read "Sonnet 4.5" and ask "why not 4.6 which was already public on 2026-05-21," the answer must be "we used the latest available at run time." Sonnet 4.5 was outdated by exactly one minor version at run time and the cost of re-running was small. Haiku stays at 4-5 because the endpoint exposes no newer dated alias; this is documented rather than worked around.

---

## 2026-05-21 (post-execution) — Audit results and verbal-claim resolution

**Run summary (all per pre-registered protocol §3 sample = n = 227 PubMed abstracts):**

| Tier | Model | n usable | Weighted κ | 95 % bootstrap CI | PABAK | Cost (USD displayed) |
|---|---|---|---|---|---|---|
| haiku  | claude-haiku-4-5  | 225 | 0.487 | [0.404, 0.574] | 0.413 | ≈ $3.9 |
| sonnet | claude-sonnet-4-6 | 227 | 0.461 | [0.380, 0.545] | 0.352 | $2.93 |
| opus   | claude-opus-4-7   | 227 | 0.532 | [0.455, 0.606] | 0.399 | $21.25 |

Sunk cost from aborted sonnet-4-5 run: ≈ $2 (one-shot, accepted; partial JSONL renamed `*.aborted-sonnet-4-5`, not ingested by `analyze.py`).

**Pairwise model agreement:** weighted κ between any two of {haiku, sonnet, opus} ∈ [0.81, 0.86]. Substantially higher than heuristic-vs-model agreement. The three models encode something the heuristic does not.

**Pre-registered decision-rule resolution (protocol §4):** all three primary κ values fall in the band 0.40 < κ ≤ 0.60. The verbal claim allowed by the table:

> "Moderate IRR; the disagreement set is flagged for human triage and is enumerated in the supplementary CSV."

This is the only verbal claim that may be made in the paper. Disallowed: "the screening is validated", "two independent reviewers agree", or any claim that the 156-eligible figure has been confirmed by a second reviewer. The paper's §Limitations "Screening methodology" paragraph (lines 587-?) has been amended with the observed κ values, the pairwise-model κ pattern, and the contamination check; it does not upgrade the screening claim.

**Pre-registered H0_2025 resolution (protocol §7):** weighted κ on n=43 post-cutoff subset:
- haiku: 0.320 (95 % CI [0.175, 0.498])
- sonnet: 0.342 (95 % CI [0.192, 0.511])
- opus: 0.317 (95 % CI [0.153, 0.488])

All three: H0_2025 not rejected (κ ≤ 0.40 on the post-cutoff subset). Combined with full-corpus κ in 0.46-0.53, this matches the second protocol §7 branch: "Contamination plausibly inflates the full-corpus number; primary claim downgraded to 'agreement observed but contamination cannot be ruled out.'" The paper's §Limitations paragraph reflects this verbatim (`partly inflated by training-corpus exposure but is not entirely an artifact of it`).

**McNemar-Bowker symmetry test** (protocol §9): all three models show p < 1e-15 — strong systematic asymmetry between heuristic and LLM. The disagreement is not random; both screeners have systematic biases relative to each other. Dominant axis (consistent across all three models): heuristic "Maybe" → LLM "Exclude" (45-46 of 54 papers).

**0 % malformed-output rate** across 681 calls (3 tiers × 227 papers). Protocol §11.2 (>5% malformed) never triggered. Total wall time across the three live tiers: ≈ 11 minutes.

**Artefacts committed to git in this PR:**
- `experiments/llm_second_reviewer/run_*_haiku.jsonl` (the 2-paper smoke-test JSONL is retained as `run_20260520T175555Z_haiku.jsonl`; the canonical run is `run_20260520T175705Z_haiku.jsonl`)
- `experiments/llm_second_reviewer/run_20260520T181323Z_sonnet.jsonl`
- `experiments/llm_second_reviewer/run_20260520T181323Z_sonnet.jsonl.aborted-sonnet-4-5` (sunk-cost partial run, excluded from analysis but retained for reproducibility audit)
- `experiments/llm_second_reviewer/run_20260520T181629Z_opus.jsonl`
- `experiments/data/processed/llm_second_reviewer_results.csv` (merged across all 3 tiers, 681 rows)
- `experiments/results/llm_second_reviewer_summary.md`
- `experiments/results/llm_second_reviewer_confusion.csv`

**Outstanding (deferred per protocol §8)**: human-gold n=30 subset is not yet labelled. Until it is, the audit remains IRR-only.

---

## 2026-05-21 (post-execution) — Self-consistency follow-up activated and complete

**Context**: All three primary tiers landed in protocol §4's 0.40 < κ ≤ 0.60 band, triggering protocol §6 (M-A deferred). User flagged a 5-hour KST quota window (anchor 2026-05-21 03:10 KST) and requested a quota-resilient runner.

**Decision**: built `run_self_consistency.py` with these properties:
1. Sample: 59-paper convergent-disagreement subset (papers where all three primary-run models unanimously disagreed with the heuristic). The subset CSV is pinned at `experiments/llm_second_reviewer/convergent_disagreements.csv`.
2. 3 samples per (pmid, tier) at CLI default decoding = 531 calls total.
3. Persistent state at `experiments/llm_second_reviewer/sc_state.jsonl`; per-call write under a thread lock; auto-resume on restart skips completed `(pmid, tier, sample_idx)` triples.
4. Quota-error detection on patterns `rate_limit | quota | 429 | exceeded | too many requests` (case-insensitive in stderr + stdout). On hit, sleeps until the next 5-hour KST window boundary plus 30 s buffer, then retries the same call. Up to 8 retry cycles.
5. Concurrency 4 (one shared CLI subprocess per worker). Sequential first attempt was killed after observing ~6 s / call → switched to threaded for ~12 min total wall.

**Results**:
- Total calls 531, completed 511 new (20 resumed from earlier sequential attempt), 0 malformed, **0 quota retries** (run finished within the same 5-hour window 03:10-08:10 KST).
- Wall ≈ 19 min (1166 s) at concurrency 4. Cost ≈ $13.4 (new) + ~$0.2 (resumed-from leftover) ≈ $13.6.
- Per-tier stability (unanimous 3/3): **Sonnet 4-6 95 %, Opus 4-7 93 %, Haiku 4-5 76 %**. Haiku is the noisiest sampler; Sonnet and Opus essentially deterministic at default decoding.
- Majority vote vs original primary-run single sample matches **100 %, 98 %, 90 %** (sonnet / opus / haiku). The primary-run verdicts were not lucky outliers.
- Cross-tier convergence on majority verdicts: 58/59 papers have a defined majority across all three tiers; **51/58 = 88 %** have all three tier majorities identical AND differing from the heuristic. **Zero** papers flipped back to agreement with the heuristic under resampling.
- Dominant reaffirmed axis: 36 of 40 original "Maybe → Exclude" papers, 13 of 14 "Include → Exclude" papers, and 2 of 5 "Include → Maybe" papers retained their three-LLM consensus under resampling.

**Paper integration**: §Limitations "Screening methodology" paragraph extended with one sentence reporting the 88 % robustness figure and the dominant reaffirmed axis. The sentence does not upgrade the primary-run verbal-claim band (§4); it only attests that the moderate-IRR finding is not driven by sampling noise.

**Artefacts committed in this PR**:
- `experiments/llm_second_reviewer/run_self_consistency.py` (resumable, quota-aware)
- `experiments/llm_second_reviewer/analyze_self_consistency.py`
- `experiments/llm_second_reviewer/convergent_disagreements.csv` (n = 59 subset)
- `experiments/llm_second_reviewer/sc_state.jsonl` (552 lines: header + 531 records)
- `experiments/data/processed/llm_second_reviewer_sc.csv` (flat, 531 rows)
- `experiments/results/llm_second_reviewer_sc_summary.md`
- `experiments/llm_second_reviewer/protocol.md` §6 amended

**Why this counts as a meaningful follow-up rather than redundant computation**: protocol §6 was pre-registered as conditional on the §4 band being hit. The condition was hit. The SC run answers the specific challenge: "could a single-sample LLM verdict happen to disagree with the heuristic just by chance at this decoding setting?" The answer for 88 % of the high-confidence subset is no — the disagreement reproduces unanimously under independent resampling. This is the strongest IRR-tier statement the audit can make without human gold labels.

---

## 2026-05-21 (post-execution) — Qualitative reason extraction on 51-paper reaffirmed subset

**Context**: User asked to extract value from the LLM "reason" field already captured in both the primary-run JSONLs and the self-consistency state file. No additional LLM calls.

**Decision**: built `experiments/llm_second_reviewer/analyze_reasons.py` — pure stdlib analysis. Pulls ~600 reason strings (12 per paper × 51 papers) and reports per-axis lexical patterns (bigrams + trigrams), 3 representative example papers per axis with verbatim reasons from all 3 tiers × 4 samples each, and cross-LLM token-set jaccard similarity to characterise whether the models cite shared or distinct evidence for the same verdict.

**Findings (committed to `experiments/results/llm_second_reviewer_reasons.md`)**:

- **Axis Maybe → Exclude (n=36 papers, 432 reasons)**: top bigrams "loot boxes" (101), "loot box" (70), "behavioral addictions" (70), "virtual item" (48). Most informative trigrams are template fragments like "focus loot boxes" (26), "loot boxes inventory" (26) — the LLMs are uniformly explaining what the paper *isn't* about. Representative examples include an unrelated medical-education paper (PMID 18710846), a Harvard Business Review performance-measurement piece (PMID 19839446), and a German-language behavioral addiction conceptual paper (PMID 23604411). The heuristic's "Maybe" tier in this audit is mostly populated by clearly off-topic papers that the LLMs identify unanimously across 4 samples each.

- **Axis Include → Exclude (n=13 papers, 172 reasons)**: dominant bigrams "original data" (55), "without original" (53), "behavioral psychological" (48), "psychological measures" (41). The LLMs uniformly diagnose the heuristic's misclassification as a violation of inclusion criterion 1 (peer-reviewed empirical studies) or 5 (excluded if monetization economics without behavioral measures). I.e. these 13 papers the heuristic admitted are commentaries / conceptual pieces, not empirical studies.

- **Axis Include → Maybe (n=2 papers)**: too small for lexical analysis; reasons reported verbatim in the md.

**Paper integration**: `paper/main.tex` §Limitations "Screening methodology" extended with one sentence summarising both failure modes (a) and (b) and quoting the "without original [data]" bigram count. The §4 verbal-claim band (`moderate IRR; disagreement set flagged for human triage`) is unchanged; the reason analysis sharpens *what* the heuristic gets wrong without claiming validity for the LLM screener.

**No additional cost**: stdlib analysis only; 0 LLM API calls; ~3 s wall.

**Outstanding**: the same 51-paper subset is the natural input for a future human-gold pass. Sample IDs and seed (20260521) for the stratified n=30 gold draw remain pinned in protocol §8.
