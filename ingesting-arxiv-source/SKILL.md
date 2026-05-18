---
name: ingesting-arxiv-source
description: Download and extract one explicit arXiv paper source into paper/<arxiv_id>/. Use when the user gives an arXiv ID or arXiv source URL and wants the source fetched, unpacked, refreshed, or prepared for summary-paper.
---

# Ingesting arXiv Source

Purpose: fetch one named arXiv source archive and unpack it locally. This skill does not
summarize papers; use `summary-paper` after ingestion if needed.

## Rules

- Only process an arXiv ID or arXiv URL explicitly provided by the user.
- Store outputs under `paper/<arxiv_id>/`, using `/` -> `_` for old-style IDs in paths.
- Do not search for related papers or download unrelated papers.
- Do not overwrite existing source unless the user asks to refresh or force.

## Workflow

1. Normalize input:
   `2510.10125`, `arXiv:2510.10125`, `https://arxiv.org/abs/...`,
   `https://arxiv.org/pdf/...`, and `https://arxiv.org/src/...` all become the arXiv ID.
2. Run the bundled script:

```bash
python <skill_dir>/scripts/fetch_arxiv_source.py <arxiv_id> --paper-root paper
```

Use `--force` only when the user wants to refresh existing archive/source files.

3. Verify these exist:
   `paper/<arxiv_id>/source_archive`, `paper/<arxiv_id>/source/`,
   `paper/<arxiv_id>/extraction_report.json`.
   `source_archive/` should contain the original arXiv payload filename when arXiv
   provides one, commonly like `arXiv-2510.10125v3.tar.gz`.
   If the report says `has_tex: false` or `source_issue` is set, tell the user
   explicitly that no source TeX was available/found. This is expected for papers
   where arXiv only serves a PDF from the source endpoint, such as `1601.00991`.
4. If the user also asked for a summary, hand off the dossier or `source/` directory to
   `summary-paper`.

## Output

Report the dossier path, whether TeX files were found, and any source/extraction issue.
If `summary-paper` also ran, include the summary path.
