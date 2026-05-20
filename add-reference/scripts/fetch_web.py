#!/usr/bin/env python3
"""Fetch web pages into references/<name>/original/<name>.md."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md


def safe_name(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-._")
    return value or "web-reference"


def parse_item(item: str) -> tuple[str, str]:
    if "=" not in item:
        raise SystemExit(f"Expected name=url, got: {item}")
    name, url = item.split("=", 1)
    name = safe_name(name)
    url = url.strip()
    if not url:
        raise SystemExit(f"Missing URL for {name}")
    return name, url


def fetch_markdown(name: str, url: str) -> str:
    response = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    markdown = md(str(soup))
    return f"# {name}\n\nSource: {url}\n\n{markdown}".strip() + "\n"


def write_reference(name: str, url: str, references_root: Path, force: bool) -> Path:
    original_dir = references_root / name / "original"
    if original_dir.exists() and force:
        shutil.rmtree(original_dir)
    original_dir.mkdir(parents=True, exist_ok=True)

    out = original_dir / f"{name}.md"
    if out.exists() and not force:
        raise SystemExit(f"Refusing to overwrite existing file: {out}")
    out.write_text(fetch_markdown(name, url), encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch web pages into references/<name>/original/")
    parser.add_argument("items", nargs="+", help="One or more name=url pairs")
    parser.add_argument("--references-root", default="references", help="Root references folder")
    parser.add_argument("--force", action="store_true", help="Overwrite existing reference folders")
    args = parser.parse_args()

    references_root = Path(args.references_root)
    for item in args.items:
        name, url = parse_item(item)
        out = write_reference(name, url, references_root, args.force)
        print(f"wrote={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
