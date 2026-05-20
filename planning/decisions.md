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
