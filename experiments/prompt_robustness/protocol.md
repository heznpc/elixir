# Prompt-Robustness of the Cross-Model Convergence — Pre-registered Protocol

**Status:** Pre-registered before the first call.
**Date pinned:** 2026-06-04.
**Scope:** Tier B (feasible slice). Test whether the cross-model convergence — the 59 papers where all Claude models agreed with each other AND were more exclusionary than the heuristic — survives a deliberately adversarial change to the *prompt framing*, holding the criteria byte-identical.

This addresses the **prompt half** of the shared-method-variance concern that Tier A (Opus 4-8 cross-generation, PR #15) explicitly could not resolve. It does NOT address the lineage half (that needs a different model family — blocked by the Claude-only decision + missing non-Anthropic keys) nor validity (needs human gold — deferred).

---

## 1. The question

Tier A showed four Claude generations converge on the same off-heuristic verdicts (κ 0.85+, 59/59 consensus match). Two interpretations survive: (a) real signal, or (b) shared method variance. (b) has two components: shared *training lineage* and shared *prompt*. This experiment isolates and tests the **prompt** component.

If the off-heuristic exclusions were induced by the specific wording of `prompt_v1.txt`, then changing the framing — especially pushing toward inclusion — should flip them back toward the heuristic. If they hold under an adversarial pro-inclusion prompt, the convergence is not a prompt artifact.

## 2. Design (within-subjects, with a noise-floor control)

- **Papers:** the 59 in `experiments/llm_second_reviewer/convergent_disagreements.csv`. All 59 are cases where the Claude consensus was MORE exclusionary than the heuristic (Maybe→Exclude 40, Include→Exclude 14, Include→Maybe 5). The adversarial direction is therefore pro-inclusion.
- **Criteria:** byte-identical `criteria_v1.txt` (sha256 `1b467a5dce41…`) in every condition. Only the prompt wrapper changes.
- **Two perturbed prompts:**
  - **V_reword** (`prompt_reword.txt`): a meaning-preserving paraphrase of `prompt_v1.txt`. Same instructions, different words. This is the **noise-floor control** — it absorbs decoding noise + "any wording change flips it."
  - **V_lenient** (`prompt_lenient.txt`): an adversarial pro-inclusion framing — "high-recall posture; Exclude only if clearly outside every domain; when uncertain choose the more inclusive verdict." This is the **real test**.
- **Models:** `claude-haiku-4-5` + `claude-sonnet-4-6` (two of the original convergent trio). Opus is dropped to control cost — the question is prompt-sensitivity (framing), not capability, and two independent models suffice to measure consensus-under-perturbation. This choice is pre-registered, not post-hoc; both models are reported in full.
- **Total calls:** 59 papers × 2 variants × 2 models = 236.

## 3. Estimand + pre-registered bands

Per (paper, model) cell, the **original verdict** is that model's verdict from the 2026-05-21 run (`llm_second_reviewer_results.csv`). A **flip** = the variant verdict differs from the original.

- `flip_rate(V_reword)` = noise floor. Expected low (< 0.15). If high, the models are simply unstable and the whole comparison is uninformative (reported as such).
- `flip_rate(V_lenient)` = directional sensitivity.
- **Primary statistic:** `Δ = flip_rate(V_lenient) − flip_rate(V_reword)`.
  - **Δ < 0.15:** off-heuristic verdicts robust to directional prompt pressure → the convergence is NOT a prompt artifact (real-signal evidence, prompt half).
  - **0.15 ≤ Δ < 0.40:** partial prompt-sensitivity.
  - **Δ ≥ 0.40:** the convergence is substantially prompt-induced; the Tier A "generation-stable" finding is downgraded — stability across Claude generations would partly reflect the shared prompt.
- **Secondary (directional check):** among V_lenient flips, the fraction that move toward MORE inclusion (Exclude→Maybe/Include, Maybe→Include). A genuine leniency effect should be near-100% directional; non-directional flips are noise. If V_lenient flips are mostly directional AND Δ is high, that's clean evidence of prompt-induced strictness in the original.

## 4. Model / decoding pins

- Models above; CLI subprocess, default temperature (consistent with all prior runs; internal-reproducible only).
- `criteria_v1.txt` reused verbatim; the runner records its sha256 and aborts if it drifts from `1b467a5dce41`.
- Each perturbed prompt's sha256 is recorded in the run header.
- Concurrency 6. Quota-resilient (sleep to next 5-h KST window; same pattern).
- Single sample per cell (consistent with the original primary verdicts being single-sample; V_reword is the noise control for that).

## 5. Confound / limit (honest)

This tests ONLY the prompt component of shared-method-variance. Even a clean "Δ < 0.15, convergence robust" result does NOT rule out shared *training-lineage* artifact — all conditions still use Claude models. A reviewer can still say "you only perturbed the prompt; same-family models could share a lineage bias the prompt change can't reach." That residual is acknowledged; resolving it needs a non-Claude rater (Tier B cross-vendor, blocked) or human gold (deferred).

## 6. Outputs

- `experiments/prompt_robustness/state.jsonl`
- `experiments/prompt_robustness/data/prompt_robustness_results.csv`
- `experiments/results/prompt_robustness_summary.md`

## 7. Stop conditions

- > 5 % malformed after one retry → abort.
- Wall > 30 min → abort.
- Cost > $12 → abort (enforced in-loop; expected ~$3-6 with haiku+sonnet, no opus).
- Quota error → sleep to next KST window + 30 s, resume.

## 8. Reporting (no file-drawer)

Every outcome reported, including "convergence robust, nothing changes." Result becomes a one-paragraph supplementary in `experiments/results/prompt_robustness_summary.md` and at most a clause appended to the existing §Limitations footnote. The original audit summaries are not modified.
