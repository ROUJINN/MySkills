---
name: add-reference
description: Add academic references from local PDFs or arXiv IDs into a references/ folder. Use when asked to add, download, parse, or organize PDFs/arXiv papers, using MinerU to convert PDFs and keeping only markdown plus images after parsing.
---

# Add Reference

## Goal

Create a compact paper reference folder under `references/` from either:

- a local PDF file
- an arXiv ID

Use MinerU for PDF parsing. After parsing, keep only the generated `.md` file(s) and image assets.
MinerU can be slow; budget roughly 6 minutes for a 22-page PDF.

## Directory Layout

```text
references/
  <arxiv_id>/
    original/
      source.tar.gz
      ...extracted source files when arXiv source exists...
      # If no source exists and PDF is parsed:
      arXiv-<arxiv_id>.pdf
      *.md
      images/
  <pdf_filename>/
    original/
      <pdf_filename>.pdf
      *.md
      images/
```

For PDFs, use the PDF basename as `<pdf_filename>`
For arXiv entries with a valid source archive, do not create markdown unless a PDF is actually parsed.

## Local PDF Workflow

1. Create `references/<pdf_filename>/original/`.
2. Copy the original PDF into `original/`.
3. Run MinerU:

```bash
uv run mineru -p <input_pdf_path> -o <temp_mineru_output_dir>
```

4. Copy only the MinerU markdown and images:

```bash
python3 <skill_dir>/scripts/copy_mineru_outputs.py <temp_mineru_output_dir> references/<pdf_filename>/original/
```

## arXiv Workflow

1. Normalize the arXiv ID by removing URL prefixes, `arXiv:`, and query fragments.
2. Use the bundled fetch script:

```bash
python3 <skill_dir>/scripts/fetch_arxiv.py <arxiv_id_or_url> --references-root references
```

3. The script writes into `references/<arxiv_id>/original/`, safely extracts tar/zip/gzip source payloads, and prints the final saved payload path.
4. If `original/` contains extracted source files and no PDF-only payload, stop after verifying source files were extracted. 
5. If the saved payload has a `.pdf` suffix, use the same Local PDF Workflow.