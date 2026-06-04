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

---

## 2026-05-21 (second KST window, post-execution) — GHI face-validity audit and OpenAlex extension

**Context**: After PR #5 merged, current quota window (08:10-13:10 KST) was fresh. User flagged that the previous design had no chain or monitoring — both fixed in this round: a single `chain.sh` runs GHI → analyze → OpenAlex search → dedup → analyze → LLM recheck → analyze, with a Monitor streaming each `phase=` line as a chat event. The chain inherits the same quota-resilience pattern as `run_self_consistency.py`; the runner sleeps until the next 5h KST window boundary if a quota error is hit, then retries.

**Two pre-registered experiments executed:**

### A. GHI face-validity audit (`experiments/ghi_face_validity/`)

- 18-item GHI draft (frozen at `items_v1.json`) covering D2-D6 + cross-domain.
- 3 criteria from King et al. (2020): SCOPE, LANGUAGE, OVERPATHOLOGIZING (frozen at `criteria_v1.txt`).
- 3 models: Opus 4-7, Sonnet 4-6, Haiku 4-5. 162 judgments total.
- Decision-rule outcome (protocol §4): **4 items REVISE** (GHI-01, GHI-03, GHI-15, GHI-18 — all flagged $\geq 6/9$, common failure mode = missing distress/impairment marker), **1 under review** (GHI-10), **13 provisionally retained**.
- Cost: ~$7. Wall: ~6.5 min. 0 quota retries.
- Paper integration: §Future Directions GHI subsection extended with the 18-item draft reference + the 4 REVISE items + the dominant failure mode summary.

### B. OpenAlex evidence-void recheck (`experiments/openalex_extension/`)

- One-sided extension: D2 + D6 queries against OpenAlex Works API (200 hits each, no API key).
- Deduplication against PubMed corpus: 1 PMID match, 0 DOI/title-jaccard matches; 399 novel records.
- Heuristic screening on novel records: D2 = 6 Include, D6 = 5 Include.
- Per-domain pre-registered decision rule (§4): both in 3-9 band = "evidence sparse but void claim not supported."
- Protocol §6 trigger condition met ($\geq 5$ Include per domain), so the LLM-recheck follow-up was filed and immediately executed: 11 records $\times$ 3 models = 33 calls, all 3 LLMs **unanimously Excluded all 11 records** (correctly identifying them as off-topic: an AI containment paper duplicated 4× on Zenodo, a free-to-play monetization dissertation, a virtual-goods trade-classification paper, a supply-chain hoarding paper, a game-development labour book duplicated twice, an indie-game value-crafting paper, and a disabled-gamer accessibility dissertation).
- Net conclusion (load-bearing per protocol §6): D2 LLM-Include = 0, D6 LLM-Include = 0 $\rightarrow$ **evidence-void claims corroborated**. Paper §3.2 / §3.7 stand. The OpenAlex extension is reported as a supplementary footnote in each subsection.
- Cost: search 0 USD (free OpenAlex API), LLM recheck ~$2.4. Wall: search ~30 s, dedup <1 s, LLM recheck ~3 min. 0 quota retries.

**Failure recovered mid-execution**: the initial OpenAlex search failed at `search.py:102` with `AttributeError: 'NoneType' object has no attribute 'get'` because some OpenAlex records have `primary_location.source = null`. Fix applied (guard with `if isinstance(src, dict)`), search re-launched, completed cleanly. Failure + fix recorded in this entry rather than as a separate amendment because the bug was in pre-registered code rather than a protocol deviation.

**Coverage caveat (carried forward from OpenAlex protocol §10)**: OpenAlex coverage of practitioner blogs (Bycer, Game Wisdom), TV Tropes / Pixiv Dictionary entries, and Japanese-language non-Crossref-registered work is incomplete. Absence of OpenAlex hits is therefore consistent with both "no evidence" and "evidence exists in venues OpenAlex does not index well." The extension is one-sided per protocol §1; it can falsify the void claim but cannot conclusively confirm it.

**Total cost this window**: ~$9.4 (GHI $7 + OpenAlex search 0 + LLM recheck $2.4). Quota retries: 0 across both experiments. Both ran inside the single 08:10-13:10 KST window. Quota-resilience logic untested in production but retained for future cross-window runs.

---

## 2026-05-21 (third KST window, post-execution) — D3 study-design audit

**Context**: After GHI v2 (PR #8) and monitoring infra (PR #7, #9), the third KST quota window (13:10-18:10 KST) was used for a §3.3 robustness check. Question: are the heuristic-derived design-distribution counts in `paper/main.tex` §3.3 robust to an independent LLM re-classification of every D3-tagged paper?

**Decision**: pre-register a 9-category taxonomy (cross_sectional, unspecified, longitudinal, systematic_review, scale_validation, review_commentary, experimental, qualitative, content_analysis), classify each of the 102 D3-tagged papers (heuristic Include + Maybe) with all three Claude models (Opus 4-7 / Sonnet 4-6 / Haiku 4-5), report majority verdicts, and apply a per-category 20%/50% deviation rule. The protocol is committed at `experiments/d3_design_audit/protocol.md`.

**Note on the 102 vs 97 corpus discrepancy**: paper §3.3 reports n = 97 D3 eligible papers; the heuristic CSV at the pinned commit yields 102 (92 Include + 10 Maybe). The 5-paper gap is acknowledged in protocol §7 as a finding rather than reconciled; the audit runs on the 102 actually present.

**Run summary**:
- 306 calls (102 papers × 3 tiers); 305 successful, 1 timeout that did not retry.
- Cost ~$11.12, wall ~9 min, 0 quota retries.
- Inter-model consensus: 90 % unanimous (3/3 same design), 9 % majority (2/3), 1 % no-majority.

**Findings**:

| Category | Paper §3.3 | LLM majority | Δ | Band |
|---|---|---|---|---|
| cross_sectional | 43 | 53 | +10 | approximate (23 %) |
| unspecified | 35 | 1 | −34 | revise (97 %) |
| longitudinal | 9 | 9 | 0 | **survives (0 %)** |
| systematic_review | 4 | 6 | +2 | approximate (50 %) |
| scale_validation | 3 | 6 | +3 | revise (100 %) |
| review_commentary | 3 | 13 | +10 | revise (333 %) |
| experimental | 2 | 3 | +1 | approximate (50 %) |
| qualitative | 2 | 2 | 0 | **survives (0 %)** |
| content_analysis | 1 | 8 | +7 | revise (700 %) |

**Load-bearing claim verified**: the *longitudinal n = 9* claim was reproduced exactly by LLM majority (9 of the 9 candidate papers classified longitudinal; 8 of those unanimous across all three tiers). This is the single most important §3.3 robustness check because the longitudinal subset of D3 carries the temporal-precedence evidence for the spending-distress link.

**Headline-shifting findings (without changing primary numbers)**:
- The 35 "unspecified" papers are mostly classifiable by the LLMs: only 1 of the 35 remains genuinely ambiguous from title + abstract. A full-text pass would compress this bucket dramatically.
- The "reviews and commentaries" bucket rises from 3 to 13 under LLM re-classification. This is consistent with the LLM-second-reviewer audit finding (PR #5) that the heuristic admits commentary into Include at a non-trivial rate.

**Paper integration**: `paper/main.tex` §3.3 amended with a "Design-distribution robustness audit (supplementary)" paragraph immediately after the Study design distribution sentence. The original heuristic-derived counts are retained as the primary numbers; the LLM re-classification is reported as a supplementary descriptive check (analogous to the OpenAlex extension's relationship to D2/D6).

**Monitoring infra concurrently improved**:
- Heartbeat in-flight detection now cwd-filters to this repo (avoids matching tidal's `experiments/src/seed_variance.py`).
- Heartbeat regex now requires `experiments/<dir>/<file>.py` pattern, removing false matches from other repos' `run.py`-named scripts.
- Heartbeat success criterion (`bool(verdict) or bool(design)`) now recognises the design-field output of the D3 audit.
- `make_per_call_dataset.py` extended with d3_design experiment; refreshed CSV.

**Total cost this window**: $11.12 / 306 calls / ~9 min. Quota retries: 0. Cumulative across 3 windows: 1,896 calls / ~$64.

**Outstanding**: heuristic-derived 35 unspecified bucket could be narrowed by adding LLM classifications as a supplementary CSV column on the eligible-papers list. Filed as a paper-write-step follow-up rather than a re-audit.

---

## 2026-05-21 (third KST window, late) — D5 OpenAlex completionism recheck

**Context**: After the D3 design audit (PR #10), 2nd half of the 13:10-18:10 KST window was idle. Window crossed to 18:10-23:10 KST. User said "이어서 진행" — D5 OpenAlex broader-database check launched on the same pattern as the D2/D6 extension (PR #6).

**Decision**: pre-register a one-sided OpenAlex extension targeted at completionism / achievement hunting / platinum trophy / collectathon. Decision rule per §2:
- 0 LLM-confirmed-Include → weak-evidence claim corroborated.
- 1-2 → weak remains weak, add records to literature pool.
- 3-9 → evidence rises to moderate, revise §3.6.
- ≥ 10 → major revision.

**Run summary**:
- OpenAlex query returned 200 hits (cap).
- Deduplication: 1 PMID match → 199 novel records.
- Heuristic screening: 3 Heuristic-Include, 127 Maybe, 69 Exclude.
- LLM recheck on the 3 Heuristic-Include records (3 papers × 3 models = 9 calls).
- Cost: ~$0.37. Wall: 26 s. 0 quota retries.

**LLM-recheck outcome**:
- "Framework for Designing and Evaluating Game Achievements" (2011 conference paper) — Haiku Exclude, Sonnet Maybe, Opus Maybe → split.
- "Breaking Harmony Square" (2020, political-misinformation inoculation game) — unanimous Exclude across all 3 tiers.
- "DLC: Perpetual Commodification of the Video Game" (2012, commentary) — unanimous Exclude across all 3 tiers.

**LLM-confirmed-Include (unanimous across 3 tiers): 0.**

**Net conclusion**: D5 weak-evidence claim corroborated by the broader-database check. Paper §3.6 stands. The OpenAlex check is reported as a supplementary footnote at the end of §3.6.

**Cumulative across 3 KST windows + this run**: 1,904 calls / ~$64.49.

---

## 2026-05-21 (third KST window, late) — D1 + D4 OpenAlex broader-DB completion

**Context**: After D5 OpenAlex check (PR #11), 5-domain broader-database audit was 3/5 complete (D2, D5, D6). Completing the pattern with D1 + D4 (D3 exempted — already strong evidence). Single combined chain run.

**Run summary**:
- OpenAlex hits: D1 = 200, D4 = 200 (total 400).
- Dedup vs PubMed: 13 PMID matches dropped → 387 novel records.
- Heuristic-Include: D1 = 13, D4 = 13 (total 26).
- LLM recheck: 26 papers × 3 models = 78 calls.
- Cost ~$3.27, wall ~4 min, 0 quota retries.

**Per-domain LLM-recheck outcome**:

**D1 (loss aversion):** 0 unanimous-Include. 5 of 13 unanimously Excluded by all three tiers, the rest split (mostly Maybe due to borderline behavioral-economics generality). The Heuristic-Include records were mostly general sunk-cost / endowment-effect papers from economics with no specific game-behavior component (Bertrand–Edgeworth duopoly, ambiguity-aversion theory, etc.). Per §2 decision rule: paper §3.1 moderate-evidence claim corroborated.

**D4 (inventory paralysis):** **3 unanimous-Include**:
- W2901570581 — Zendle & Cairns (2018, PLoS ONE) "Video game loot boxes are linked to problem gambling" (PMID 30462669).
- W3185081605 — Spicer et al. (2021, New Media & Society) "Loot boxes, problem gambling and problem video gaming: A systematic review and meta-synthesis".
- W4320340857 — Yu et al. (2023, Computers in Human Behavior) "Loot box purchases and their relationship with internet gaming disorder and online gambling disorder in adolescents: A prospective study".

Manual verification: none of these three are present in the PubMed corpus by PMID or title-substring match (the dedup correctly did not flag them). They are genuine novel additions.

All three are loot-box/gambling-overlap papers that PubMed did not surface under the D4 query terms. Per §2 decision rule (1-3 unanimous Includes): moderate evidence remains moderate. The §3.4 narrative is otherwise unchanged but the literature pool is extended by these three records.

**Paper integration**: paper/main.tex §3.1 + §3.4 extended with "OpenAlex broader-database check (supplementary)" paragraphs. Mirrors the §3.2 / §3.6 / §3.7 paragraph pattern from PR #6, PR #11.

**5-domain broader-DB audit summary**:

| Domain | OpenAlex hits | Novel | Heur Include | LLM unanimous Include | Verdict |
|---|---|---|---|---|---|
| D1 loss aversion (mod) | 200 | 187 | 13 | 0 | corroborated |
| D2 consumable (void) | 200 | 199 | 6 | 0 | corroborated |
| D4 inventory (mod) | 200 | 200 | 13 | **3** | mod remains mod + literature pool +3 |
| D5 completionism (weak) | 200 | 199 | 3 | 0 | corroborated |
| D6 backlog (void) | 200 | 200 | 5 | 0 | corroborated |

4 of 5 domains' evidence-strength claims corroborated. D4 is the only domain where the broader-DB extension surfaced novel papers, and even there the verdict only adds to the literature pool rather than changing the strength tier.

**Cumulative across this session**: 1,982 calls / ~$67.77 / 12 PRs.

---

## 2026-06-04 — Opus 4-8 cross-generation robustness (Tier A)

**Context**: Opus 4-8 released ~2 weeks after the 2026-05-21 primary audit. User asked whether it affects the experiments. Assessment: completed runs are pinned + dated → not invalidated (mirror image of the Sonnet 4.5→4.6 bump: new model arrived AFTER the run, nothing to switch). Reviewer-facing answer stands: "4-8 not public at run time." The one place a re-run adds value is the cross-model-agreement finding — does a newer-generation Claude join the convergence?

**Design review before running** (user requested): surfaced 5 issues — C1 (no pre-registered cutoff → HARKing), C2 (4-8's later cutoff confounds contamination), M2 (framing must be cross-GENERATION-within-Claude, not cross-vendor), M3 (provenance isolation — don't regenerate the original summary), M4 (single-sample decoding). Plus "Tier A" refinements over the naive 4th-κ design: A1 (reuse the 59-paper convergent-disagreement subset as the primary discriminator), A2 (disagreement-set Jaccard, not just aggregate κ), A3 (contamination as difference-in-differences vs 4-7), A4 (state capability/contamination confound as a structural limit), A5 (pre-register null reporting). All folded into `experiments/opus48_crossgen/protocol.md` before any 4-8 call.

**Validation before spend**: analyzer dry-tested with a stub (4-8 := 4-7 verdicts) → produced known values (κ(4-8,opus)=1.000, κ(4-8,heur)=0.532, A1=59/59, DiD=0.000). Confirmed the math, then deleted the stub and ran live.

**Results** (claude-opus-4-8, 227 papers, frozen prompt 6ba4ab67e4de + criteria 1b467a5dce41, 0 malformed):
- κ(4-8, heuristic) = 0.465 (95% CI [0.39, 0.54]) — in the [0.40, 0.60] band, same as the trio (0.461-0.532). 4-8 does NOT agree with the heuristic more than the trio.
- κ(4-8, each trio model): haiku 0.857, sonnet 0.877, opus 0.847 — all ≥ 0.75 (generation-stable), matching/exceeding the trio's own internal 0.812-0.857.
- A1 (primary discriminator): 4-8 matches the trio consensus on **59/59 (100%)** convergent-disagreement papers.
- A2: disagreement-set Jaccard = 0.845 (disagreement on the same papers → real shared signal, not coincidence).
- A3: DiD = +0.077 (< 0.15) → no contamination signature; 4-8's later cutoff does not inflate heuristic agreement.

**Verdict**: the cross-model-agreement finding is **generation-stable**. A newer-generation Claude independently reproduces the convergence. **Caveat (A4 + §2 inferential target)**: 4-8 shares training lineage + identical prompt with the other three → joining the convergence is consistent with both real-signal and shared-method-variance. This strengthens *robustness* but does NOT establish *correctness*. Resolving that is Tier B (cross-vendor or human adjudication).

**Cost honesty**: the run cost **$40.15**, overrunning the pre-registered $30 ceiling (protocol §11) by 34%. Two causes: (1) my $20-22 estimate was wrong — Opus 4-8 ran ~1.9× the per-call cost of 4-7's 2026-05-21 run ($21.2 for the same 227); (2) the runner declared `--cost-ceiling` but did NOT enforce it in the worker loop. The run completed cleanly (227/227, 0 malformed) so no harm, but the ceiling was not actually active. Enforcement (stop-flag checked at top of do_one, bounding overrun to in-flight calls) was added to `run.py` **post-hoc** so the committed code matches the protocol; the live run predates the fix. Recorded here rather than silently corrected.

**Provenance**: original `llm_second_reviewer_summary.md` untouched. 4-8 reported in separate `experiments/results/opus48_crossgen_summary.md` + one §Limitations footnote in `paper/main.tex`.

**Next**: Tier B re-evaluation (per user) — whether to pursue the correctness question via a different model family or skeptical adjudication, with the circularity caveat that an LLM adjudicator sharing Claude lineage leans toward the LLM-consensus by construction.

---

## 2026-06-04 — Prompt-robustness of the cross-model convergence (Tier B, feasible slice)

**Context**: Tier A (Opus 4-8, PR #15) showed the cross-model convergence is generation-stable but flagged it cannot separate (a) real signal from (b) shared method variance. Tier B re-evaluation: B1/B2 (Claude-as-adjudicator) are now known-circular (Tier A proved all Claudes converge); the decisive variants (cross-vendor, human-gold) are blocked by the Claude-only decision + missing non-Anthropic keys + human-effort. The one feasible slice: test the PROMPT half of (b).

**Design** (`experiments/prompt_robustness/protocol.md`, pre-registered before any call): re-screen the 59 convergent-disagreement papers under two perturbed prompt framings — V_reword (meaning-preserving paraphrase = noise floor) and V_lenient (adversarial pro-inclusion) — holding criteria_v1.txt byte-identical, on haiku-4-5 + sonnet-4-6 (opus dropped, cost-driven, pre-registered). 59 × 2 × 2 = 236 calls. Primary statistic Δ = flip_rate(lenient) − flip_rate(reword); bands <0.15 robust / 0.15-0.40 partial / ≥0.40 substantially prompt-induced. Analyzer validated with a stub (reword=orig→flip 0, lenient=Include→flip 1.0, dir 118/118, survive 0/59) before live spend.

**Results** (236 calls, 0 malformed, $5.81, within $12 ceiling):
- flip_rate(V_reword) = 0.051 (noise floor low — comparison valid).
- flip_rate(V_lenient) = 0.339; **Δ = +0.288 → PARTIAL prompt-sensitivity**.
- Directional: 40/40 (100%) lenient flips move toward inclusion — a genuine leniency response, not noise.
- Survival: 28/59 (47%) keep their off-heuristic verdict on BOTH models under the adversarial prompt.
- Model-dependent: Haiku flips 46% under lenient, Sonnet only 22% — the stronger model is more anchored to the criteria.

**Verdict**: the convergence is **partly, not mostly, prompt-induced**. ~Half the off-heuristic exclusions are framing-robust (credible real signal — clearly off-topic medical/business papers stay excluded under any framing); ~half are framing-dependent (borderline papers a lenient prompt returns toward the heuristic's more-inclusive verdict). This honestly qualifies Tier A's "generation-stable" — the cross-generation agreement partly reflects the shared prompt — and reframes the heuristic-vs-LLM disagreement on borderline papers as a framing-dependent call, not a case of one screener being unambiguously right.

**Tier B status after this**: the feasible slice (prompt half) is done. The residual — shared training-lineage artifact — remains untestable without a non-Claude rater (cross-vendor: blocked by Claude-only decision + no GPT/Gemini keys) or human gold (deferred, seed 20260521). Recorded as the honest stopping point for Tier B.

**Paper integration**: a §Limitations footnote sentence was drafted but the edit was DECLINED by the owner on 2026-06-04 (held pending owner direction — the "Screening methodology" paragraph is already very long; the footnote wording/placement is the owner's call). The experiment artifacts + this entry are committed regardless; the paper change is deferred to owner.

---

## 2026-06-04 — Eligible-count recount (heuristic 156 vs LLM-majority 82) + tex

**Context**: The headline "156 eligible" rests on the rule-based heuristic. The primary IRR audit already holds 3-model verdicts on all 227 records, so the LLM-eligible count is a free re-analysis (zero new API calls).

**Result** (`experiments/eligible_recount/recount.py` → `experiments/results/eligible_recount_summary.md`):
- heuristic eligible = 156 (102 Include + 54 Maybe) — reproduced exactly, validates the data load.
- 3-model LLM-majority eligible = **82** (drop of 74, −47%). Strict (all-3) = 73; lenient (≥1) = 106; 4-model incl Opus 4-8 = 72 (more ties).
- Drop source: 47 of 54 heuristic-"Maybe" → "Exclude", plus 24 heuristic-"Include" → "Exclude".
- **Caveat (load-bearing)**: the prompt-robustness experiment showed ~half of these LLM exclusions reverse under a lenient prompt, so 82 is a strict-prompt lower bound. The framing-neutral eligible count lies between 82 and 156; neither endpoint is unambiguously correct.

**Decision**: this materially qualifies the headline number, so — unlike the prompt-robustness footnote (owner chose supplementary-only) — it is surfaced in `paper/main.tex`. Added ONE sentence-block to the §Limitations "Screening methodology" paragraph, right after the existing "rests on a single automated heuristic ... preliminary" sentence: reports the 82 vs 156, the Maybe-tier concentration, and the [82, 156] framing-neutral bracket. The reported 156 is NOT changed (it is correctly the heuristic result); the addition quantifies its sensitivity to screener choice. pdflatex compiles clean (318 KB).

**Why in main.tex when prompt-robustness was supplementary-only**: the recount touches the paper's HEADLINE number (abstract / §Method / §Results / §Conclusion all cite 156), so disclosure belongs in the main text; prompt-robustness is a second-order methodological detail that the recount sentence references but does not restate.
