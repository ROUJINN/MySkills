#!/usr/bin/env python3
"""Copy MinerU markdown and images into a reference original/ folder.

MinerU often writes nested output like:

  <output>/<pdf_name>/hybrid_auto/<pdf_name>.md
  <output>/<pdf_name>/hybrid_auto/images/

This script finds the best markdown output directory under the MinerU output
root, copies its .md files into the destination folder, and copies the sibling
images/ directory when present. It intentionally ignores MinerU JSON, layout
PDFs, origin PDFs, model files, and other intermediate artifacts.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def find_markdown_dir(output_dir: Path) -> Path:
    md_files = sorted(output_dir.rglob("*.md"))
    if not md_files:
        raise SystemExit(f"No markdown files found under {output_dir}")

    def score(md_path: Path) -> tuple[int, int]:
        parent = md_path.parent
        has_images = (parent / "images").is_dir()
        is_hybrid = parent.name == "hybrid_auto"
        return (int(has_images) + int(is_hybrid), -len(parent.parts))

    return max(md_files, key=score).parent


def copy_outputs(markdown_dir: Path, dest_dir: Path, force: bool) -> list[Path]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []

    for md_file in sorted(markdown_dir.glob("*.md")):
        dest = dest_dir / md_file.name
        if dest.exists() and not force:
            raise SystemExit(f"Refusing to overwrite existing file: {dest}")
        shutil.copy2(md_file, dest)
        copied.append(dest)

    images_src = markdown_dir / "images"
    if images_src.is_dir():
        images_dest = dest_dir / "images"
        if images_dest.exists():
            if not force:
                raise SystemExit(f"Refusing to overwrite existing directory: {images_dest}")
            shutil.rmtree(images_dest)
        shutil.copytree(images_src, images_dest)
        copied.append(images_dest)

    return copied


def main() -> int:
    parser = argparse.ArgumentParser(description="Copy MinerU .md files and images into original/")
    parser.add_argument("mineru_output_dir", help="Directory passed to MinerU with -o")
    parser.add_argument("dest_original_dir", help="Destination references/<id-or-name>/original directory")
    parser.add_argument("--force", action="store_true", help="Overwrite existing markdown/images")
    args = parser.parse_args()

    output_dir = Path(args.mineru_output_dir)
    dest_dir = Path(args.dest_original_dir)
    if not output_dir.is_dir():
        raise SystemExit(f"MinerU output directory does not exist: {output_dir}")

    markdown_dir = find_markdown_dir(output_dir)
    copied = copy_outputs(markdown_dir, dest_dir, args.force)

    print(f"markdown_dir={markdown_dir}")
    for path in copied:
        print(f"copied={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
