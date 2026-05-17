#!/usr/bin/env python3
"""Download and extract arXiv TeX source into paper/<arxiv_id>/."""

from __future__ import annotations

import argparse
import gzip
import io
import json
import os
import re
import shutil
import tarfile
import urllib.request
import zipfile
from pathlib import Path


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

    if tarfile.is_tarfile(archive_path):
        return {"kind": "tar", "files": safe_extract_tar(data, source_dir)}

    if zipfile.is_zipfile(archive_path):
        return {"kind": "zip", "files": safe_extract_zip(data, source_dir)}

    try:
        decompressed = gzip.decompress(data)
    except OSError:
        decompressed = None

    if decompressed is not None:
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


def download(url: str, dest: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "codex-arxiv-source-ingester/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        with dest.open("wb") as fh:
            shutil.copyfileobj(response, fh)


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
    archive_path = dossier_dir / "source_archive"
    url = f"https://arxiv.org/src/{arxiv_id}"

    dossier_dir.mkdir(parents=True, exist_ok=True)
    if archive_path.exists() and not args.force:
        downloaded = False
    else:
        download(url, archive_path)
        downloaded = True

    if source_dir.exists() and args.force:
        shutil.rmtree(source_dir)
    if source_dir.exists() and any(source_dir.iterdir()) and not args.force:
        extraction = {"kind": "existing", "files": [str(p.relative_to(source_dir)) for p in source_dir.rglob("*") if p.is_file()]}
    else:
        extraction = extract_source(archive_path, source_dir)

    tex_files = [str(p.relative_to(dossier_dir)) for p in source_dir.rglob("*.tex")]
    report = {
        "arxiv_id": arxiv_id,
        "url": url,
        "dossier_dir": str(dossier_dir),
        "archive_path": str(archive_path),
        "source_dir": str(source_dir),
        "downloaded": downloaded,
        "extraction": extraction,
        "tex_files": tex_files,
        "suggested_summary_path": str(dossier_dir / f"{safe_name(arxiv_id).replace('.', '_')}.md"),
    }
    (dossier_dir / "extraction_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
