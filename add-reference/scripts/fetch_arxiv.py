#!/usr/bin/env python3
"""Fetch an arXiv paper payload into references/<arxiv_id>/original/.

This script normalizes an arXiv ID or URL, downloads the arXiv source endpoint,
stores the payload as source.tar.gz, and safely extracts source archives in
place. It handles common arXiv payload shapes: tar, zip, gzipped tar, gzipped
single TeX file, raw unknown payloads, and PDF-only responses.

If arXiv returns a PDF instead of source, the script renames it to
arXiv-<arxiv_id>.pdf.
"""

from __future__ import annotations

import argparse
import gzip
import io
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
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as tf:
        for member in tf.getmembers():
            target = dest / member.name
            if not is_within_directory(dest, target):
                raise RuntimeError(f"Unsafe tar member path: {member.name}")
        tf.extractall(dest)
        return [m.name for m in tf.getmembers()]


def safe_extract_zip(data: bytes, dest: Path) -> list[str]:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        for member in zf.namelist():
            target = dest / member
            if not is_within_directory(dest, target):
                raise RuntimeError(f"Unsafe zip member path: {member}")
        zf.extractall(dest)
        return zf.namelist()


def download(url: str, dest_dir: Path) -> Path:
    request = urllib.request.Request(url, headers={"User-Agent": "codex-add-reference/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        dest = dest_dir / "source.tar.gz"
        with dest.open("wb") as fh:
            shutil.copyfileobj(response, fh)
    return dest


def replace_with_pdf(payload_path: Path, data: bytes, arxiv_id: str) -> Path:
    pdf_path = payload_path.parent / f"arXiv-{safe_name(arxiv_id)}.pdf"
    pdf_path.write_bytes(data)
    if payload_path != pdf_path and payload_path.exists():
        payload_path.unlink()
    return pdf_path


def extract_payload(payload_path: Path, original_dir: Path, arxiv_id: str) -> Path:
    data = payload_path.read_bytes()

    if data.startswith(b"%PDF-"):
        return replace_with_pdf(payload_path, data, arxiv_id)

    if tarfile.is_tarfile(payload_path):
        safe_extract_tar(data, original_dir)
        return payload_path

    if zipfile.is_zipfile(payload_path):
        safe_extract_zip(data, original_dir)
        return payload_path

    try:
        decompressed = gzip.decompress(data)
    except OSError:
        decompressed = None

    if decompressed is not None:
        if decompressed.startswith(b"%PDF-"):
            return replace_with_pdf(payload_path, decompressed, arxiv_id)
        try:
            safe_extract_tar(decompressed, original_dir)
            return payload_path
        except tarfile.TarError:
            tex_path = original_dir / "main.tex"
            tex_path.write_bytes(decompressed)
            return tex_path

    raw_path = original_dir / "source_payload"
    if payload_path != raw_path:
        payload_path.rename(raw_path)
    return raw_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Download arXiv source into references/<arxiv_id>/original/")
    parser.add_argument("arxiv_id", help="arXiv ID or arXiv URL")
    parser.add_argument("--references-root", default="references", help="Root references folder")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing original/ folder")
    args = parser.parse_args()

    arxiv_id = normalize_arxiv_id(args.arxiv_id)
    if not arxiv_id:
        raise SystemExit("Could not parse arXiv ID")

    reference_dir = Path(args.references_root) / safe_name(arxiv_id)
    original_dir = reference_dir / "original"
    if original_dir.exists() and args.force:
        shutil.rmtree(original_dir)
    original_dir.mkdir(parents=True, exist_ok=True)

    existing_files = sorted(p for p in original_dir.iterdir() if p.is_file())
    if existing_files and not args.force:
        payload_path = existing_files[0]
    else:
        payload_path = download(f"https://arxiv.org/src/{arxiv_id}", original_dir)

    final_payload = extract_payload(payload_path, original_dir, arxiv_id)
    print(f"original_dir={original_dir}")
    print(f"payload={final_payload}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
