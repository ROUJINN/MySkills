---
name: summary-paper
description: Summarize one academic paper from local TeX source, an extracted arXiv source folder, a paper dossier, or a user-provided PDF. Use when the user asks to read, understand, summarize, or make project notes for a specific paper.
---

# Summary Paper

Purpose: write a focused summary for one paper from TeX and/or PDF. This skill does not
download arXiv source or do broad literature search.
For PDF reading, extraction, rendering, OCR-like visual checks, or layout-sensitive review,
use the `pdf` skill and incorporate its extracted/verified content into the summary.

## Inputs

- `.tex` file or extracted TeX directory
- paper dossier such as `paper/<arxiv_id>/`
- user-provided PDF
- optional project context from the user

Prefer TeX when both TeX and PDF exist, unless the user says the PDF is authoritative.
When TeX is unavailable but a PDF exists, use the `pdf` skill rather than ad hoc PDF
handling.

## Rules

- Summarize only the provided paper.
- Do not invent metadata; use `Unknown` when needed.
- Read an existing summary before editing it.
- Mark unreadable PDF pages or weak extraction clearly, based on the `pdf` skill's
  extraction/rendering results.

## Workflow

1. Gather metadata, abstract, intro, method, experiments, related work, limitations,
   conclusion, appendix, and figure/table captions.
2. For TeX, identify the main file by `\documentclass` or `\begin{document}`; follow
   `\input{}` / `\include{}` and inspect `.bib` / `.bbl` when citations matter.
3. For PDF, invoke the `pdf` skill. Prefer its rendered-page inspection when layout,
   figures, tables, equations, or extraction quality matter; use its text extraction output
   for quick reading.
4. Write the summary beside the input, or as `paper/<arxiv_id>/<arxiv_id_with_underscores>.md`
   for a dossier.

## Summary Template

```markdown
# <Paper Title>

## Metadata
- **Source**: <path, URL, arXiv ID, or PDF filename>
- **Authors**: <authors or Unknown>
- **Year**: <year or Unknown>
- **Venue**: <venue or Unknown>

## 1. 这篇论文试图解决什么问题？

## 2. 有哪些相关研究？

## 3. 论文如何解决这个问题？

## 4. 论文做了哪些实验？

## 5. 有什么可以进一步探索的点？

## Notes for Our Project
```

Write in the user's preferred language.

## Output

Report the summary path, whether it used TeX/PDF/both, and any important uncertainty.
Do not paste the full summary unless asked.
