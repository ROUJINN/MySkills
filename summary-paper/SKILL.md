---
name: summary-paper
description: Summarizes an academic paper from local TeX source files, an extracted arXiv source folder, or a user-provided PDF. Use when the user asks to read, understand, summarize, or make project notes for one specific paper from TeX, LaTeX source, PDF, or an existing paper folder.
---

# Summary Paper

This skill creates a focused paper summary from either TeX source or a PDF supplied by
the user. It does not download papers, search for related work broadly, or create arXiv
source dossiers. Use `ingesting-arxiv-source` first when the user gives only an arXiv ID
and wants the source fetched.

## Inputs

Accept any of these:

- a `.tex` file;
- a directory containing extracted TeX source;
- a paper dossier such as `paper/<arxiv_id>/source/`;
- a user-provided PDF;
- project context plus one of the above.

If both TeX and PDF are available, prefer TeX for structure and citations unless the user
explicitly says the PDF is the authoritative version.

## Hard Boundaries

- Summarize only the specific paper or files the user provided.
- Do not download arXiv source archives.
- Do not search for additional papers unless the user explicitly asks.
- Do not invent citation metadata. Mark missing metadata as `Unknown`.
- Do not overwrite an existing summary without reading it first.
- Preserve user notes and merge improvements instead of replacing useful content.

## Reading TeX

When given a TeX source tree, identify the main file in this order:

1. `.tex` files containing `\documentclass`.
2. `.tex` files containing `\begin{document}`.
3. Files referenced by `\input{...}` or `\include{...}` from the main file.
4. `.bbl` and `.bib` files for citation titles and related work.
5. Appendix `.tex` files with experiments, proofs, limitations, or extra results.

Read for structure:

- title, authors, abstract;
- introduction problem framing;
- method sections;
- experiment sections;
- related work and citations;
- limitations, discussion, conclusion, and appendix;
- figure and table captions.

## Reading PDFs

When given a PDF, extract text with the best local tool available. If extraction quality
is poor, say so and base conclusions only on readable content. Inspect figures, tables,
captions, and appendices when they are visible or extractable.

For scanned PDFs or image-heavy papers, use available OCR or visual inspection tools when
the runtime supports them. Mark any uncertainty caused by unreadable pages.

## Summary File

If the paper lives in a dossier such as `paper/2510.10125/`, write:

```text
paper/2510.10125/2510_10125.md
```

If there is no dossier, write the summary beside the input file or in the location the
user requested. Choose a clear filename based on the paper title or input filename.

Use this structure:

```markdown
# <Paper Title>

## Metadata
- **Source**: <path, URL, arXiv ID, or PDF filename>
- **Authors**: <authors or Unknown>
- **Year**: <year or Unknown>
- **Venue**: <venue or Unknown>

## 1. 这篇论文试图解决什么问题？
<Summarize the problem, motivation, and why prior approaches are insufficient.>

## 2. 有哪些相关研究？
<Group related work by theme. Include citation keys or paper names found in the source when available.>

## 3. 论文如何解决这个问题？
<Explain the method, model, algorithm, system, or theoretical idea.>

## 4. 论文做了哪些实验？
<Summarize datasets, baselines, metrics, ablations, main results, and appendix evidence.>

## 5. 有什么可以进一步探索的点？
<List concrete follow-up ideas, limitations, missing ablations, and project-relevant questions.>

## Notes for Our Project
<If the user provided project context, connect the paper to that context. Otherwise say what context is needed.>
```

Write in the user's preferred language. If the user asks in Chinese, write the summary in
Chinese while preserving technical terms and paper titles where useful.

## Quality Check

Before finishing, verify:

- the summary file exists when the user asked for a file;
- all five required questions are answered;
- related work is grouped by theme, not just listed paper-by-paper;
- evidence source is clear: TeX, PDF, or both;
- any uncertainty is marked explicitly as `Unknown` or `Needs verification`.

## Output to User

After finishing, report only:

- the summary file path, if created;
- whether the summary came from TeX, PDF, or both;
- any important uncertainty or unreadable-source issue.

Do not paste the full summary unless the user asks.
