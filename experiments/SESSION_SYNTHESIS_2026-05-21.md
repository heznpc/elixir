# Supplementary Audits Synthesis — 2026-05-21

This document consolidates the LLM-assisted supplementary audits run across the 2026-05-21 session into one reference. Twelve PRs landed on `main` between the design review (PR #2) and the final broader-database completion (PR #12). Each audit was pre-registered before any LLM call, scope-limited to descriptive / inter-rater claims (not validity), and reported with a fixed verbal-claim band per its protocol §4.

The session was driven by `planning/review.md` §3.1's flag: *single-reviewer + automated-heuristic screening is the largest single reject risk for the systematic review*. The audits below address that risk and document the systematic over-inclusion bias of the rule-based heuristic.

---

## Headline numbers

- **PRs merged**: 12.
- **LLM calls**: 1,982 across 3 KST quota windows (03:10-08:10, 08:10-13:10, 13:10-18:10 + late 18:10-23:10).
- **Cost (displayed)**: ~$67.77 across all audits.
- **Quota retries**: 0. The runners' resilience logic (sleep to next 5-h KST boundary) was never triggered.
- **Malformed-output rate**: 2 of 1,982 = 0.10 %.
- **Heuristic-LLM IRR**: linear-weighted Cohen's κ = 0.46-0.53 (moderate band) for all three Claude tiers on the primary 227-paper screening.
- **Cross-LLM agreement**: pairwise weighted κ 0.81-0.86 (substantial band) — the LLMs converge among themselves but only moderately with the heuristic.

---

## §1. Primary IRR audit (PRs #2-#3)

**Setup**: Pre-registered protocol committed before observation. 227 PubMed abstracts × 3 Claude models (Opus 4-7, Sonnet 4-6, Haiku 4-5) = 681 calls. Linear-weighted Cohen's κ + bootstrap 95 % CI + PABAK as co-primary.

**Result**: all three tiers fall in the pre-registered 0.40 < κ ≤ 0.60 "moderate IRR" band:

| Tier | weighted κ | 95 % CI | PABAK |
|---|---|---|---|
| Opus 4-7 | 0.532 | [0.455, 0.606] | 0.399 |
| Haiku 4-5 | 0.487 | [0.404, 0.574] | 0.413 |
| Sonnet 4-6 | 0.461 | [0.380, 0.545] | 0.352 |

Pairwise model-vs-model κ ∈ [0.81, 0.86] — substantial. The three LLMs encode the same screening signal the heuristic doesn't.

**Verbal-claim band** (protocol §4): "Moderate IRR; disagreement set flagged for human triage."

**Contamination check (protocol §7)**: weighted κ on the 2025-2026 subset (n = 43, post-cutoff) drops to 0.32-0.34, suggesting the full-corpus number is partly inflated by training-corpus exposure but not entirely an artifact (κ does not collapse to 0).

---

## §2. Self-consistency follow-up (PR #4)

**Trigger condition**: protocol §6 was conditional on the §4 band being hit. All three primary tiers hit the moderate band, so SC was activated.

**Subset**: 59 papers where the three primary-run LLMs agreed with each other but disagreed with the heuristic (the convergent-disagreement set).

**Setup**: 59 papers × 3 models × 3 samples = 531 calls.

**Result**: 88 % (51 / 58 papers with defined majorities) retained an identical 3-tier LLM majority verdict differing from the heuristic. **Zero** papers flipped back to agreement with the heuristic under resampling.

Per-tier stability:

| Tier | unanimous (3/3) | majority (2/3) | no majority |
|---|---|---|---|
| Sonnet 4-6 | 95 % | 0 % | 5 % |
| Opus 4-7 | 93 % | 3 % | 3 % |
| Haiku 4-5 | 76 % | 17 % | 7 % |

Match between SC majority and original single-sample LLM verdict: 100 % (Sonnet), 98 % (Opus), 90 % (Haiku). The original verdicts were not lucky outliers.

**Conclusion**: the heuristic-LLM disagreement is robust to decoding-time sampling variance.

---

## §3. Qualitative reason analysis (PR #5)

**Setup**: pure-stdlib analysis of the ~600 reason strings already captured during the primary run + SC (no new LLM calls). 12 reasons per paper × 51 reaffirmed-disagreement papers.

**Two heuristic failure modes identified**:

1. **Heuristic "Maybe" tier → LLM "Exclude" (36 papers, 432 reasons)**: top bigrams "loot boxes" (101), "behavioral addictions" (70). Trigrams like "focus loot boxes" (26) reveal that the LLMs uniformly describe what the paper *isn't* about. Representative excluded papers: a UK medical-education paper on ethnic stereotypes, a Harvard Business Review piece on performance measurement, a German-language behavioral-addiction conceptual paper — all clearly off-topic, unanimously Excluded by all 3 tiers × 4 samples.

2. **Heuristic "Include" tier → LLM "Exclude" (13 papers, 172 reasons)**: dominant bigrams *"original data"* (55), *"without original"* (53). The LLMs uniformly diagnose these 13 records as violating inclusion criterion 1 (peer-reviewed empirical studies) or 5 (monetization economics without behavioural measures). The heuristic's Include tier therefore admits commentary / conceptual pieces at a non-trivial rate.

---

## §4. GHI face-validity audit v1 → v2 (PRs #6, #8)

**Setup v1**: 18-item GHI draft × 3 King et al. (2020) criteria (SCOPE, LANGUAGE, OVERPATHOLOGIZING) × 3 Claude models = 162 judgments.

**Result v1**:

| Triage | n items |
|---|---|
| REVISE (≥ 6/9 flags) | 4 |
| under review (3-5/9) | 1 |
| provisionally retained (≤ 2/9) | 13 |

The 4 REVISE items (GHI-01, 03, 15, 18) shared the same failure mode: missing distress / impairment / escalation / loss-of-control markers. The LANGUAGE criterion was clean across all 18 items.

**v2 rewrite + re-audit**: 5 items rewritten (the 4 REVISE + GHI-10 under-review) with explicit markers, other 13 held constant. Same 162-judgment protocol.

**Result v2**: REVISE 4 → 0, under review 1 → 1, retained 13 → 17. **All 5 revised items dropped to 0/9 flags.** Per-criterion drops were uniform across all three tiers. Sanity check: zero unrevised items showed |Δ| ≥ 3 between v1 and v2, confirming the LLM judge baseline is stable and the v2 drops are attributable to the rewrites.

---

## §5. D3 study-design distribution audit (PR #10)

**Setup**: 102 D3-tagged papers × 3 Claude models = 306 calls, classifying each paper into a 9-category study-design taxonomy.

**Cross-LLM consensus on design**: 90 % unanimous (3/3), 9 % majority (2/3), 1 % no-majority.

**Per-category counts: paper §3.3 vs LLM majority**:

| Category | Paper | LLM | Δ | Band |
|---|---|---|---|---|
| longitudinal | 9 | 9 | 0 | **survives** |
| qualitative | 2 | 2 | 0 | survives |
| cross_sectional | 43 | 53 | +10 | approximate |
| systematic_review | 4 | 6 | +2 | approximate |
| experimental | 2 | 3 | +1 | approximate |
| scale_validation | 3 | 6 | +3 | revise |
| review_commentary | 3 | 13 | +10 | revise |
| content_analysis | 1 | 8 | +7 | revise |
| **unspecified** | **35** | **1** | **-34** | **revise** |

**Load-bearing claim verified**: the paper's *longitudinal n = 9* is reproduced exactly by LLM majority. 8 of the 9 are unanimous across all three tiers. This is the load-bearing claim for the D3 temporal-precedence argument.

**Two headline-shifting findings (primary counts retained)**:
- The 35 "unspecified" bucket collapses to 1 under LLM classification — only 1 paper is truly ambiguous from title + abstract.
- "Reviews and commentaries" rises from 3 to 13 — consistent with the §3 finding that the heuristic over-admits commentary.

---

## §6. OpenAlex broader-database extension — 5-domain pattern (PRs #6, #11, #12)

**Setup**: targeted OpenAlex Works API queries for each domain, 200-hit cap per query, deduplication against the 227-paper PubMed corpus, heuristic screening on novel records, 3-Claude-model LLM recheck on Heuristic-Include records.

| Domain | OpenAlex hits | Novel | Heur Inc | **LLM unanimous Inc** | Verdict |
|---|---|---|---|---|---|
| D1 loss aversion (moderate) | 200 | 187 | 13 | **0** | corroborated |
| D2 consumable hoarding (void) | 200 | 199 | 6 | **0** | void corroborated |
| D4 inventory paralysis (moderate) | 200 | 200 | 13 | **3** | mod + literature pool +3 |
| D5 completionism (weak) | 200 | 199 | 3 | **0** | corroborated |
| D6 backlog accumulation (void) | 200 | 200 | 5 | **0** | void corroborated |

**4 / 5 domains' evidence-strength claims corroborated.** D4 is the only domain where OpenAlex surfaces genuinely novel papers; the 3 unanimous-Include records (Zendle & Cairns 2018 PMID 30462669, Spicer et al. 2021, Yu et al. 2023) are loot-box / gambling overlap papers PubMed did not surface under D4 query terms. All three verified novel vs PubMed by PMID + title substring.

The **same heuristic over-inclusion bias** identified in PR #5 is corroborated across all five domain OpenAlex extensions: Heuristic-Include counts (6 + 5 + 3 + 13 + 13 = 40 total) collapse to 3 unanimous-Includes after LLM recheck (7.5 % retention).

---

## §7. Monitoring infrastructure (PR #7, #9)

Built mid-session after the user flagged that monitoring was missing and that token / time were not surfaced as variables.

- **`experiments/_monitoring/dashboard.py`** — single-shot aggregator over every state JSONL.
- **`experiments/_monitoring/heartbeat.sh`** — persistent monitor body. Emits on calls / cost / inflight change OR every `HEARTBEAT_EVERY_N` ticks. Filters in-flight processes by cwd-under-`/Paper/elixir/` via `lsof` (avoids picking up other repos' `experiments/*.py` scripts).
- **`experiments/_monitoring/make_per_call_dataset.py`** — unified 22-column per-call CSV. Surfaces `input_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`, `output_tokens`, `total_tokens`, `call_started_utc`, `call_started_kst`, `kst_window_idx`, `kst_window_offset_s`, `timestamp_source`.
- All 4 runners (`llm_second_reviewer/run.py`, `run_self_consistency.py`, `ghi_face_validity/run.py`, `openalex_extension/llm_recheck.py`) patched to record `call_started_utc` and the full `usage` dict in every JSONL record going forward. Pre-patch records back-fill timestamps from file mtime (marked `timestamp_source = file_mtime_fallback`).

---

## §8. Paper integration

`paper/main.tex` amended at the following anchors with one supplementary paragraph each:

- §Method "Screening Process" — single-rule-based-heuristic acknowledgment.
- §Limitations "Screening methodology" — IRR + SC + reason-analysis figures, with `\citep{Khraisha2024}` for PABAK.
- §3.1 (D1 Loss Aversion) — OpenAlex corroboration.
- §3.2 (D2 Consumable Hoarding) — OpenAlex + LLM recheck void corroboration.
- §3.3 (D3 Gacha / Loot Box) — design-distribution robustness audit, longitudinal-9 verified.
- §3.4 (D4 Inventory Paralysis) — OpenAlex +3 novel records, literature pool extension.
- §3.6 (D5 Completionism) — OpenAlex corroboration.
- §3.7 (D6 Backlog Accumulation) — OpenAlex + LLM recheck void corroboration.
- §Future Directions GHI subsection — 18-item v2 draft, 4 REVISE → 0 after marker addition, scope-limit reminder.

Bibliography entry added for Khraisha et al.\ 2024 (`{Khraisha2024}`).

---

## §9. Outstanding (deferred, paper-write-step or future-work follow-ups)

- **Human-gold n = 30 stratified subset.** Sample IDs reproducible via seed `20260521`. Until labelled, all audits report inter-rater reliability only, never validity.
- **PROSPERO amendment.** If the systematic review is PROSPERO-registered before publication, the LLM-assisted audits must be filed as a protocol amendment referencing `experiments/llm_second_reviewer/protocol.md`.
- **Direct-API re-run with `temperature=0`** for external reproducibility. The current CLI-subprocess path is internally reproducible only.
- **Bibliography extraction to `references.bib`** (decisions.md OPEN entry).
- **Cross-LLM-family robustness** (GPT-4o, Gemini). Currently scope-limited to Claude family per user decision on 2026-05-21.
- **Unspecified-bucket compression for §3.3**: the LLM audit found 34 of 35 unspecified papers are classifiable. A paper-write-step pass can re-attach them to specific categories.

---

## §10. PR ledger

| PR | Title | Cost |
|---|---|---|
| #2 | pre-register LLM-as-second-reviewer audit + scope-limit screening claims | 0 |
| #3 | LLM-as-second-reviewer audit results — 3 Claude models × 227 abstracts | ~$28 |
| #4 | self-consistency follow-up — 88 % of convergent disagreements robust | ~$13.4 |
| #5 | qualitative reason analysis on 51-paper reaffirmed-disagreement subset | 0 |
| #6 | GHI face-validity audit + OpenAlex evidence-void recheck (D2/D6) | ~$9.4 |
| #7 | monitoring infrastructure: persistent heartbeat + per-call token/time | 0 |
| #8 | GHI v2 audit — 4 REVISE → 0 after marker-addition rewrite | ~$3.1 |
| #9 | heartbeat: emit on change + idle every 5 min | 0 |
| #10 | D3 study-design audit — longitudinal-9 verified, unspecified 35 → 1 | ~$11.1 |
| #11 | D5 OpenAlex completionism recheck — weak-evidence corroborated | ~$0.4 |
| #12 | D1+D4 OpenAlex broader-DB — completes 5-domain audit | ~$3.3 |
| **Total** | | **~$67.8** |

All PRs squash-merged to `main`. Branches deleted on merge.
