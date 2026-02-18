#!/usr/bin/env python3
"""
embed_icons.py — Replace file:/// icon URIs with inline base64 data URIs.

Makes .drawio files self-contained and portable for sharing.

Usage:
    python embed_icons.py <input.drawio> [--output output.drawio]

If --output is not specified, the file is modified in place (a .bak backup is created).
"""
import argparse
import base64
import mimetypes
import re
import shutil
import sys
from pathlib import Path


def embed_match(match: re.Match) -> str:
    """Replace a file:/// URI with an inline base64 data URI."""
    path_str = match.group(1)
    p = Path(path_str)
    if not p.exists():
        print(f"  Warning: icon not found, skipping: {p}", file=sys.stderr)
        return match.group(0)
    mime = mimetypes.guess_type(str(p))[0] or "image/png"
    b64 = base64.b64encode(p.read_bytes()).decode()
    print(f"  Embedded: {p.name} ({mime}, {len(b64)} chars)")
    return f"image=data:{mime};base64,{b64}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Embed file:/// icons as base64 in .drawio files.")
    parser.add_argument("input", type=Path, help="Path to the .drawio file")
    parser.add_argument("--output", type=Path, default=None, help="Output path (default: modify in place)")
    args = parser.parse_args()

    input_path: Path = args.input.resolve()

    if not input_path.exists():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        return 1

    xml = input_path.read_text(encoding="utf-8")

    # Count file:/// icon references
    refs = re.findall(r"image=file:///([^;\"]+)", xml)
    if not refs:
        print("No file:/// icon references found — nothing to embed.")
        return 0

    print(f"Found {len(refs)} icon reference(s) to embed:")

    # Replace all file:/// URIs with base64 data URIs
    result = re.sub(r"image=file:///([^;\"]+)", embed_match, xml)

    # Write output
    output_path = args.output.resolve() if args.output else input_path
    if output_path == input_path:
        shutil.copy2(input_path, input_path.with_suffix(".drawio.bak"))
        print(f"Backup saved: {input_path.with_suffix('.drawio.bak')}")

    output_path.write_text(result, encoding="utf-8")
    print(f"Done — icons embedded in {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
