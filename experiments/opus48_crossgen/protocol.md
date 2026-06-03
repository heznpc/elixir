# Opus 4.8 Cross-Generation Robustness — Pre-registered Protocol

**Status:** Pre-registered before the first Opus 4-8 call.
**Date pinned:** 2026-06-04 (model availability verified this session: `claude-opus-4-8` reachable 2026-06-04 07:33 KST; the primary IRR audit ran 2026-05-21, ~2 weeks before 4-8 released).
**Scope:** Add Claude Opus 4-8 as a fourth rater to the primary IRR audit corpus and test whether the *cross-model agreement* finding is stable across a Claude model generation.

This protocol is a follow-up to `experiments/llm_second_reviewer/protocol.md`. It does NOT re-run or modify that audit. It does NOT touch `experiments/results/llm_second_reviewer_summary.md` (provenance isolation — see §M3). All outputs land under `experiments/opus48_crossgen/`.

---

## 0. Why this is not a correction

The primary audit (PRs #2–#3) pinned dated model aliases and reported every result as "what model X said at run time." Opus 4-7 was the newest Opus on 2026-05-21. Opus 4-8 released ~2 weeks later. Nothing in the completed audit is invalidated; this is additive evidence. A reviewer's "why not 4-8?" has the standing answer: "4-8 was not public at run time." This experiment exists only to *strengthen or qualify* the cross-model-agreement claim, never to fix it.

## 1. Framing (M2 — load-bearing)

This is a **cross-GENERATION agreement test WITHIN the Claude family**, not "cross-model robustness." It adds a fourth Claude from a newer generation; it does NOT add a different model family (GPT / Gemini). The Claude-only scope is a deliberate prior decision (2026-05-21). Any write-up must use "cross-generation within Claude" language and must not imply cross-vendor robustness.

## 2. The inferential target (why a 4th κ alone is insufficient)

The primary finding was: three models agreed strongly among themselves (pairwise weighted κ 0.812–0.857) but only moderately with the heuristic (κ 0.461–0.532). Two interpretations survive that aggregate:

- (a) the models independently detect a real signal the heuristic misses, or
- (b) the models share a prompt-induced artifact.

A fourth model's aggregate κ does not separate (a) from (b). The discriminating tests are the **per-paper overlap** measures (§A1, §A2), not another κ. Aggregate κ is reported but is not load-bearing on its own.

## 3. Model, prompt, decoding pins

- **Model:** `claude-opus-4-8` (bare alias; no dated alias used, consistent with all prior runs). Recorded in the run header.
- **Prompt + criteria:** the FROZEN `experiments/llm_second_reviewer/prompt_v1.txt` (sha256 `6ba4ab67e4de…`) and `criteria_v1.txt` (sha256 `1b467a5dce41…`), byte-identical to the original 3-model run (verified 2026-06-04). The runner records both hashes; post-hoc they MUST match the original headers or the comparison is void (confounds model with prompt).
- **Corpus:** the same 227 papers in `experiments/data/raw/pubmed_results.csv`.
- **Decoding:** CLI subprocess, default temperature (consistent with all prior CLI runs; internal-reproducible only — see §M-caveats).
- **Concurrency:** 4–6.

## 4. Pre-registered hypotheses + decision bands (C1)

Fixed before any 4-8 call:

**H0-heuristic:** weighted κ(4-8, heuristic) ∈ [0.40, 0.60] — i.e., 4-8 lands in the same "moderate IRR" band as the original trio (0.461–0.532).
- κ > 0.60: 4-8 agrees with the heuristic MORE than the trio did → must check contamination (§A3) before concluding "newer model is better."
- κ ∈ [0.40, 0.60]: consistent with the trio.
- κ < 0.40: 4-8 is a weaker rater than the trio against the heuristic.

**H0-crossgen:** weighted κ(4-8, each of {haiku-4-5, sonnet-4-6, opus-4-7}) lands in the substantial-or-higher band consistent with the existing trio (0.812–0.857).
- κ ≥ 0.75 for all three: **generation-stable** — 4-8 joins the intra-family convergence.
- 0.60 ≤ κ < 0.75 for any: **mild drift** — substantial (Landis–Koch) but materially below the trio.
- κ < 0.60 for any: **generation drift** — 4-8 breaks the convergence.

**A1 — convergent-disagreement join test (primary discriminator).** On the 59 papers in `experiments/llm_second_reviewer/convergent_disagreements.csv` (where all three original models agreed with each other AND differed from the heuristic), count how many 4-8's verdict **exactly matches the trio consensus**:
- ≥ 50/59 (≥85%): generation-stable — 4-8 independently lands on the same off-heuristic verdict.
- 35–49/59 (59–83%): partial — convergence weakening across generations.
- < 35/59 (<59%): generation-specific — the original convergence does not generalize to 4-8.
A secondary, weaker count (4-8 merely *differs from heuristic*, not necessarily matching the trio) is also reported.

**A2 — disagreement-set Jaccard.** Jaccard of {papers where 4-8 ≠ heuristic} and {papers where trio-majority ≠ heuristic}, over the full 227. High Jaccard ⇒ the moderate κ reflects disagreement on the SAME papers (real shared signal); low Jaccard at similar κ ⇒ the original convergence was partly coincidental.

## 5. Contamination as difference-in-differences (A3 / C2)

4-8's training cutoff is later than 4-7's, so 4-8 may have memorised more of the 43 papers dated 2025–2026. To detect whether higher 4-8↔heuristic agreement is contamination-driven rather than capability-driven, compute a difference-in-differences:

```
DiD = (κ_4-8,post − κ_4-8,pre) − (κ_4-7,post − κ_4-7,pre)
```

where pre = 184 papers dated ≤2024, post = 43 papers dated 2025–2026; κ is weighted κ vs the heuristic. The 4-7 terms are computed from existing data (`llm_second_reviewer_results.csv`).

- |DiD| < 0.15: no contamination signature — 4-8's post/pre pattern matches 4-7's.
- DiD > +0.15: 4-8 shows extra post-cutoff agreement consistent with later-cutoff contamination; any "4-8 is a better screener" claim is downgraded.

n_post = 43 is small → the post κ and the DiD have wide CIs. This is **descriptive / directional**, not a significance test. Reported with that caveat.

## 6. Confound acknowledgment (A4 — structural limit)

4-8 differs from 4-7 on TWO axes simultaneously: capability (newer/stronger) AND contamination exposure (later cutoff). These are perfectly confounded in this comparison; the DiD (§5) only partially isolates the contamination axis. The write-up must state plainly that this design **cannot fully separate capability from contamination**. It is not pretended to.

## 7. Conditional self-consistency (M4)

Primary κ uses a single sample per paper (consistent with the original primary κ). If H0-crossgen lands in the **mild-drift** band (0.60–0.75) for any pairing — i.e., ambiguous — a 3-sample self-consistency pass on the disagreement subset only is run as a follow-up (mirrors PR #4), to check whether the ambiguity is decoding noise vs real drift. Not run otherwise.

## 8. Reporting commitment (A5 — no file-drawer)

Every outcome is reported, including the null ("4-8 joins the convergence, nothing changes"). The result becomes a one-paragraph supplementary in `experiments/results/opus48_crossgen_summary.md` and at most a one-sentence §Limitations footnote in `paper/main.tex`. This is footnote-scope evidence, not a headline result; effort is right-sized accordingly.

## 9. Provenance isolation (M3)

The original `experiments/results/llm_second_reviewer_summary.md` is NOT regenerated or modified. The 4-8 run writes only to `experiments/opus48_crossgen/`. The dedicated analyzer READS the original tier verdicts from `experiments/data/processed/llm_second_reviewer_results.csv` (the deduped canonical artifact) but writes a SEPARATE summary. This keeps the "as-run on 2026-05-21" record clean and frames 4-8 unambiguously as a dated follow-up.

## 10. Outputs

- `experiments/opus48_crossgen/state.jsonl` — per-call records (verdict, usage, call_started_utc, hashes).
- `experiments/opus48_crossgen/data/opus48_results.csv` — deduped flat table.
- `experiments/results/opus48_crossgen_summary.md` — κ(4-8, heuristic), κ(4-8, each trio model), A1 join count, A2 Jaccard, A3 DiD, all vs pre-registered bands.

## 11. Stop conditions

- > 5 % malformed after one retry → abort.
- Wall > 30 min → abort.
- Cost > $30 → abort (expected ~$20–22 at Opus pricing).
- Quota error → sleep to next 5-h KST window + 30 s, resume (reuses the standard runner resilience).
