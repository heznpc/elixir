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
