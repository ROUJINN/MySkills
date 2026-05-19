---
name: summarize-reference
description: Summarize one saved reference by id or name from references/, reading TeX or Markdown files from original/ and writing summary/summary.md. Use when asked to summarize, understand, or make notes for a saved reference, paper, arXiv entry, or MinerU-parsed PDF.
---

# Summarize Reference

Input is `<id-or-name>`. Locate `references/<id-or-name>/original/`.

## Rules

- Prefer `.tex` files in `original/`; otherwise use MinerU `.md` files.
- Decide whether the material is an academic paper.
- If it is a paper, use the paper template below; otherwise choose a concise structure.
- Write `references/<id-or-name>/summary/summary.md`; ensure `summary/` and `original/` are siblings.
- Read any existing `summary/summary.md` before overwriting.
- Do not invent metadata; use `Unknown` when needed.

## Paper Summary Template

```markdown
# <Paper Title>

## Metadata
- **Source**: <path, URL, arXiv ID, or PDF filename>
- **Authors**: <authors or Unknown>
- **Year**: <year or Unknown>

## 一句话总结本文

## 1. 这篇论文试图解决什么问题？

## 2. 有哪些相关研究？

## 3. 论文如何解决这个问题？

## 4. 论文做了哪些实验？

## 5. 有什么可以进一步探索的点？
```

Write in the user's preferred language.

## Output

Report the summary path, whether it used TeX or Markdown, and any important uncertainty.
Do not paste the full summary unless asked.
