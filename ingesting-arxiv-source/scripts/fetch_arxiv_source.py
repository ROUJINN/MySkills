#!/usr/bin/env python3
"""Download and extract arXiv TeX source into paper/<arxiv_id>/."""

from __future__ import annotations

import argparse
import email.message
import gzip
import io
import json
import re
import shutil
import tarfile
import urllib.request
import zipfile
from pathlib import Path
from urllib.parse import unquote


def normalize_arxiv_id(value: str) -> str:
    value = value.strip()
    value = re.sub(r"^arXiv:\s*", "", value, flags=re.IGNORECASE)
    for marker in ("/abs/", "/pdf/", "/src/", "/e-print/"):
        if marker in value:
            value = value.split(marker, 1)[1]
            break
    value = value.split("?", 1)[0].split("#", 1)[0]
    value = re.sub(r"\.pdf$", "", value)
    return value.strip("/")


def safe_name(arxiv_id: str) -> str:
    return arxiv_id.replace("/", "_")


def default_archive_filename(arxiv_id: str) -> str:
    return f"arXiv-{safe_name(arxiv_id)}.tar.gz"


def content_disposition_filename(value: str | None) -> str | None:
    if not value:
        return None
    message = email.message.Message()
    message["content-disposition"] = value
    filename = message.get_param("filename", header="content-disposition")
    if filename:
        return Path(unquote(filename)).name
    filename_star = message.get_param("filename*", header="content-disposition")
    if isinstance(filename_star, tuple):
        _charset, _language, encoded = filename_star
        return Path(unquote(encoded)).name
    if isinstance(filename_star, str):
        return Path(unquote(filename_star)).name
    return None


def is_within_directory(directory: Path, target: Path) -> bool:
    directory = directory.resolve()
    target = target.resolve()
    try:
        target.relative_to(directory)
        return True
    except ValueError:
        return False


def safe_extract_tar(data: bytes, dest: Path) -> list[str]:
    extracted: list[str] = []
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as tf:
        for member in tf.getmembers():
            target = dest / member.name
            if not is_within_directory(dest, target):
                raise RuntimeError(f"Unsafe tar member path: {member.name}")
        tf.extractall(dest)
        extracted = [m.name for m in tf.getmembers()]
    return extracted


def safe_extract_zip(data: bytes, dest: Path) -> list[str]:
    extracted: list[str] = []
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        for member in zf.namelist():
            target = dest / member
            if not is_within_directory(dest, target):
                raise RuntimeError(f"Unsafe zip member path: {member}")
        zf.extractall(dest)
        extracted = zf.namelist()
    return extracted


def extract_source(archive_path: Path, source_dir: Path) -> dict:
    data = archive_path.read_bytes()
    source_dir.mkdir(parents=True, exist_ok=True)

    if data.startswith(b"%PDF-"):
        return {
            "kind": "pdf-only",
            "files": [],
            "issue": "arXiv returned a PDF instead of a source archive; no source TeX is available for this paper.",
        }

    if tarfile.is_tarfile(archive_path):
        return {"kind": "tar", "files": safe_extract_tar(data, source_dir)}

    if zipfile.is_zipfile(archive_path):
        return {"kind": "zip", "files": safe_extract_zip(data, source_dir)}

    try:
        decompressed = gzip.decompress(data)
    except OSError:
        decompressed = None

    if decompressed is not None:
        if decompressed.startswith(b"%PDF-"):
            return {
                "kind": "gzip-pdf-only",
                "files": [],
                "issue": "arXiv returned a gzipped PDF instead of a source archive; no source TeX is available for this paper.",
            }
        try:
            return {"kind": "gzip-tar", "files": safe_extract_tar(decompressed, source_dir)}
        except tarfile.TarError:
            pass
        tex_path = source_dir / "main.tex"
        tex_path.write_bytes(decompressed)
        return {"kind": "gzip-single-file", "files": [tex_path.name]}

    text_path = source_dir / "source_payload"
    text_path.write_bytes(data)
    return {"kind": "raw", "files": [text_path.name]}


def download(url: str, dest_dir: Path, arxiv_id: str) -> tuple[Path, dict]:
    request = urllib.request.Request(url, headers={"User-Agent": "codex-arxiv-source-ingester/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        filename = content_disposition_filename(response.headers.get("Content-Disposition"))
        dest = dest_dir / (filename or default_archive_filename(arxiv_id))
        with dest.open("wb") as fh:
            shutil.copyfileobj(response, fh)
        metadata = {
            "content_type": response.headers.get("Content-Type"),
            "content_disposition": response.headers.get("Content-Disposition"),
            "final_url": response.geturl(),
        }
    return dest, metadata


def existing_archive_file(archive_dir: Path) -> Path | None:
    if not archive_dir.exists():
        return None
    if archive_dir.is_file():
        return archive_dir
    archive_files = sorted(p for p in archive_dir.iterdir() if p.is_file())
    return archive_files[0] if archive_files else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Download arXiv source into paper/<arxiv_id>/")
    parser.add_argument("arxiv_id", help="arXiv ID or arXiv URL")
    parser.add_argument("--paper-root", default="paper", help="Root folder for paper dossiers")
    parser.add_argument("--force", action="store_true", help="Overwrite existing archive/source files")
    args = parser.parse_args()

    arxiv_id = normalize_arxiv_id(args.arxiv_id)
    if not arxiv_id:
        raise SystemExit("Could not parse arXiv ID")

    paper_root = Path(args.paper_root)
    dossier_dir = paper_root / safe_name(arxiv_id)
    source_dir = dossier_dir / "source"
    archive_dir = dossier_dir / "source_archive"
    url = f"https://arxiv.org/src/{arxiv_id}"

    dossier_dir.mkdir(parents=True, exist_ok=True)
    if archive_dir.exists() and args.force:
        if archive_dir.is_dir():
            shutil.rmtree(archive_dir)
        else:
            archive_dir.unlink()
    if not archive_dir.exists():
        archive_dir.mkdir(parents=True, exist_ok=True)

    existing_archive = existing_archive_file(archive_dir)
    if existing_archive and not args.force:
        archive_path = existing_archive
        downloaded = False
        download_metadata = {}
    else:
        archive_path, download_metadata = download(url, archive_dir, arxiv_id)
        downloaded = True

    if source_dir.exists() and args.force:
        shutil.rmtree(source_dir)
    if source_dir.exists() and any(source_dir.iterdir()) and not args.force:
        extraction = {"kind": "existing", "files": [str(p.relative_to(source_dir)) for p in source_dir.rglob("*") if p.is_file()]}
    else:
        extraction = extract_source(archive_path, source_dir)

    tex_files = [str(p.relative_to(dossier_dir)) for p in source_dir.rglob("*.tex")]
    source_issue = extraction.get("issue")
    if not tex_files and not source_issue:
        source_issue = "No .tex files were found after extracting the arXiv source payload."
    report = {
        "arxiv_id": arxiv_id,
        "url": url,
        "dossier_dir": str(dossier_dir),
        "archive_dir": str(archive_dir),
        "archive_path": str(archive_path),
        "source_dir": str(source_dir),
        "downloaded": downloaded,
        "download_metadata": download_metadata,
        "extraction": extraction,
        "tex_files": tex_files,
        "has_tex": bool(tex_files),
        "source_issue": source_issue,
        "suggested_summary_path": str(dossier_dir / f"{safe_name(arxiv_id).replace('.', '_')}.md"),
    }
    (dossier_dir / "extraction_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
