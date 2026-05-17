---
name: ingesting-arxiv-source
description: Downloads and extracts an explicit arXiv paper's source into a local paper dossier under paper/arxiv_id. Use when the user gives an arXiv ID or arXiv source URL and wants the source fetched, unpacked, refreshed, or prepared for later summarization. Use summary-paper after this skill when the user wants a paper summary.
---

# Ingesting arXiv Source

This skill turns one explicit arXiv paper into a local source dossier. It downloads the
paper's source from `https://arxiv.org/src/<arxiv_id>` and extracts it into
`paper/<arxiv_id>/source/`.

Use this only when the user provides a specific arXiv ID or arXiv source URL. Do not use
this skill for broad literature discovery; use `surveying-related-work` for that. If the
user wants the paper summarized after ingestion, continue with `summary-paper`.

## Hard Boundaries

- Only ingest papers the user explicitly names by arXiv ID or arXiv source URL.
- Always store outputs under `paper/<arxiv_id>/`.
- Do not summarize the paper in this skill; use `summary-paper`.
- Do not turn this into an autonomous research loop.
- Do not download unrelated papers while processing the target paper.
- Do not overwrite a user's existing dossier files unless the user requests refresh or
  `--force` behavior.

## Folder Contract

For arXiv ID `2510.10125`, create:

```text
paper/
  2510.10125/
    source_archive              # raw downloaded response from arXiv
    source/                     # extracted TeX source tree
    extraction_report.json      # script output and extraction metadata
```

Optional files may be created when useful:

```text
paper/2510.10125/
  notes.md                      # scratch notes, only if needed
  2510_10125.md                 # created later by summary-paper, not by this skill
```

## Quick Start

Run the bundled script from the repository or project root:

```bash
python 20-ml-paper-writing/ingesting-arxiv-source/scripts/fetch_arxiv_source.py 2510.10125 --paper-root paper
```

If the skill is installed outside this repository, resolve the script path from the skill
directory:

```bash
python <skill_dir>/scripts/fetch_arxiv_source.py 2510.10125 --paper-root paper
```

The script prints JSON containing the destination folder and extracted files. After the
script succeeds, stop unless the user also asked for a summary. For summary requests,
invoke `summary-paper` on the extracted `source/` directory or dossier folder.

## Workflow

### Step 1: Normalize the Input

Accept any of these forms:

```text
2510.10125
arXiv:2510.10125
https://arxiv.org/abs/2510.10125
https://arxiv.org/pdf/2510.10125
https://arxiv.org/src/2510.10125
```

Normalize to the canonical ID without prefixes or URL parts:

```text
2510.10125
```

For old-style IDs such as `hep-th/9901001`, preserve the slash in API requests but make a
filesystem-safe slug by replacing `/` with `_` for filenames when necessary.

### Step 2: Download and Extract Source

Use `scripts/fetch_arxiv_source.py` unless there is a strong reason not to. The script:

- creates `paper/<arxiv_id>/`;
- downloads from `https://arxiv.org/src/<arxiv_id>`;
- writes the raw response as `source_archive`;
- extracts tar, gzip, zip, or plain TeX payloads into `source/`;
- prints a JSON report.

If network access is blocked, request the required network permission through the active
runtime's approval flow. Do not silently fabricate source content.

### Step 3: Verify the Extracted Files

After extraction, inspect the source tree if needed:

```bash
find paper/2510.10125/source -maxdepth 3 -type f
```

The script's JSON report includes `tex_files` and `suggested_summary_path` to make the
handoff to `summary-paper` easy.

### Step 4: Handoff to Summary

If the user asked to summarize the paper, use `summary-paper` after source extraction.
Pass it the dossier folder or extracted source directory:

```text
paper/2510.10125/
paper/2510.10125/source/
```

`summary-paper` owns reading TeX/PDF content, recovering metadata, and writing the summary
markdown.

### Step 5: Quality Check

Before finishing, verify:

- `paper/<arxiv_id>/source/` exists and contains extracted files.
- `paper/<arxiv_id>/source_archive` exists.
- `paper/<arxiv_id>/extraction_report.json` exists.
- the extraction report states whether TeX files were found.

## Handling Common Cases

### Source Is a Single Gzipped TeX File

The arXiv source endpoint may return a gzip-compressed single `.tex` file. The bundled
script writes it to `source/main.tex` when it detects this case.

### Source Has No TeX

Some submissions contain only PDF or nonstandard files. If no TeX files are present:

1. State that TeX source was unavailable after extraction.
2. Leave the extracted payload in `source/`.
3. If the user wants a summary, use `summary-paper` on any readable extracted files or ask
   for the PDF.

### Existing Folder Already Exists

If `paper/<arxiv_id>/` already exists:

1. Preserve existing notes and summaries.
2. Refresh source only if requested or if the folder lacks `source/`.
3. Use `--force` only when the user explicitly asks to refresh existing archive/source
   files.

### Multiple Versions

If the input includes a version such as `2510.10125v2`, use that exact version for the
download URL. Store the folder as the exact input ID unless the user requests otherwise.

## Output to User

After finishing, report only:

- the created folder;
- whether TeX source was found;
- any important uncertainty or missing source issue.

If a summary was also requested and completed by `summary-paper`, report the summary path
too.
