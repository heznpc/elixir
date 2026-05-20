# LLM-as-Second-Reviewer Audit — Summary

Pre-registered protocol: `experiments/llm_second_reviewer/protocol.md`.

Tiers analyzed: haiku, opus, sonnet.

## Tier: haiku (model: claude-haiku-4-5)

- n usable pairs: **225** (of 227 total tier records)
- Weighted Cohen's κ: **0.487** (95% bootstrap CI [0.404, 0.574], 1000 resamples, seed 20260521)
- Unweighted Cohen's κ: 0.403
- PABAK (per Khraisha et al. 2024): **0.413**
- Pre-registered band (§4): 0.40 < κ ≤ 0.60 → moderate IRR. Allowed claim: "Moderate IRR; disagreement set flagged for human triage."
- McNemar-Bowker symmetry test: p ≈ 2.457e-17 (asymmetric)

**Confusion matrix (rows = heuristic, cols = haiku LLM)**

| h \ L | Include | Maybe | Exclude | row total |
|---|---|---|---|---|
| **Include** | 60 | 10 | 31 | 101 |
| **Maybe** | 1 | 7 | 45 | 53 |
| **Exclude** | 0 | 1 | 70 | 71 |
| **col total** | 61 | 18 | 146 | 225 |

**Secondary (2025+ subset, contamination-robustness per §7):** n = 43, weighted κ = 0.320 (95% CI [0.175, 0.498]), PABAK = 0.267
- H0_2025: not rejected (κ ≤ 0.40 on post-cutoff subset). Contamination may inflate full-corpus number.

## Tier: opus (model: claude-opus-4-7)

- n usable pairs: **227** (of 227 total tier records)
- Weighted Cohen's κ: **0.532** (95% bootstrap CI [0.455, 0.606], 1000 resamples, seed 20260521)
- Unweighted Cohen's κ: 0.394
- PABAK (per Khraisha et al. 2024): **0.399**
- Pre-registered band (§4): 0.40 < κ ≤ 0.60 → moderate IRR. Allowed claim: "Moderate IRR; disagreement set flagged for human triage."
- McNemar-Bowker symmetry test: p ≈ 1.471e-15 (asymmetric)

**Confusion matrix (rows = heuristic, cols = opus LLM)**

| h \ L | Include | Maybe | Exclude | row total |
|---|---|---|---|---|
| **Include** | 61 | 27 | 14 | 102 |
| **Maybe** | 1 | 8 | 45 | 54 |
| **Exclude** | 1 | 3 | 67 | 71 |
| **col total** | 63 | 38 | 126 | 227 |

**Secondary (2025+ subset, contamination-robustness per §7):** n = 43, weighted κ = 0.317 (95% CI [0.153, 0.488]), PABAK = 0.128
- H0_2025: not rejected (κ ≤ 0.40 on post-cutoff subset). Contamination may inflate full-corpus number.

## Tier: sonnet (model: claude-sonnet-4-6)

- n usable pairs: **227** (of 227 total tier records)
- Weighted Cohen's κ: **0.461** (95% bootstrap CI [0.380, 0.545], 1000 resamples, seed 20260521)
- Unweighted Cohen's κ: 0.351
- PABAK (per Khraisha et al. 2024): **0.352**
- Pre-registered band (§4): 0.40 < κ ≤ 0.60 → moderate IRR. Allowed claim: "Moderate IRR; disagreement set flagged for human triage."
- McNemar-Bowker symmetry test: p ≈ 1.934e-19 (asymmetric)

**Confusion matrix (rows = heuristic, cols = sonnet LLM)**

| h \ L | Include | Maybe | Exclude | row total |
|---|---|---|---|---|
| **Include** | 52 | 23 | 27 | 102 |
| **Maybe** | 1 | 7 | 46 | 54 |
| **Exclude** | 0 | 1 | 70 | 71 |
| **col total** | 53 | 31 | 143 | 227 |

**Secondary (2025+ subset, contamination-robustness per §7):** n = 43, weighted κ = 0.342 (95% CI [0.192, 0.511]), PABAK = 0.198
- H0_2025: not rejected (κ ≤ 0.40 on post-cutoff subset). Contamination may inflate full-corpus number.

## Pairwise model-vs-model agreement

- **haiku ↔ opus**: n = 225, weighted κ = 0.824 (95% CI [0.761, 0.878]), PABAK = 0.780
- **haiku ↔ sonnet**: n = 225, weighted κ = 0.857 (95% CI [0.799, 0.906]), PABAK = 0.827
- **opus ↔ sonnet**: n = 227, weighted κ = 0.812 (95% CI [0.752, 0.866]), PABAK = 0.756

## Disagreement set

- haiku: **88** disagreements / 227 pairs
  - heuristic=Maybe → LLM=Exclude: 45
  - heuristic=Include → LLM=Exclude: 31
  - heuristic=Include → LLM=Maybe: 10
  - heuristic=Exclude → LLM=Maybe: 1
  - heuristic=Maybe → LLM=Include: 1
- opus: **91** disagreements / 227 pairs
  - heuristic=Maybe → LLM=Exclude: 45
  - heuristic=Include → LLM=Maybe: 27
  - heuristic=Include → LLM=Exclude: 14
  - heuristic=Exclude → LLM=Maybe: 3
  - heuristic=Exclude → LLM=Include: 1
  - heuristic=Maybe → LLM=Include: 1
- sonnet: **98** disagreements / 227 pairs
  - heuristic=Maybe → LLM=Exclude: 46
  - heuristic=Include → LLM=Exclude: 27
  - heuristic=Include → LLM=Maybe: 23
  - heuristic=Exclude → LLM=Maybe: 1
  - heuristic=Maybe → LLM=Include: 1
