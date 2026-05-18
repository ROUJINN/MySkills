---
name: ingesting-arxiv-source
description: Download one explicit arXiv payload into paper/<arxiv_id>/, extract it when source files are available, and report whether the payload contains TeX or is PDF-only.
---

# Ingesting arXiv Source

Purpose: fetch one named arXiv payload and unpack it locally when it is source. This skill
does not summarize papers or plan downstream summarization.

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
4. Stop after reporting whether the downloaded arXiv payload contains TeX source or is
   PDF-only. If the local payload is a PDF and the task is only to inspect that PDF, use
   the `pdf` skill.

## Output

Report the dossier path, the downloaded payload path, whether TeX files were found, and
whether the payload is PDF-only. When no source TeX is available, explicitly say that
there is no source TeX for this arXiv item.
