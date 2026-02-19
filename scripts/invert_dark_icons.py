#!/usr/bin/env python3
"""
invert_dark_icons.py - Detect and invert dark-coloured icons for use on dark backgrounds.

An icon is considered "dark" if its mean brightness (non-transparent pixels, 0–255 scale)
is below the threshold (default 128). The script inverts the RGB channels using ImageMagick,
preserving the alpha channel, and saves the result as <name>-light.<ext>.

Usage:
  python3 invert_dark_icons.py icon.png                  # auto-detect, create icon-light.png
  python3 invert_dark_icons.py icon.png -o out.png       # write to a specific path
  python3 invert_dark_icons.py icon.png --force          # invert regardless of brightness
  python3 invert_dark_icons.py icon.png --check          # report brightness only
  python3 invert_dark_icons.py icon.png --threshold 100  # use custom darkness threshold

Requires: ImageMagick (convert, identify)
"""

import argparse
import subprocess
import sys
from pathlib import Path

DEFAULT_THRESHOLD = 128  # mean brightness below this = "dark icon", invert it


def get_mean_brightness(path: str) -> float:
    """Return the mean pixel brightness (0–255) using ImageMagick.

    Flattens alpha before measuring so transparent regions don't skew the result.
    """
    result = subprocess.run(
        [
            "convert", path,
            "-background", "white",
            "-alpha", "remove",
            "-colorspace", "gray",
            "-format", "%[fx:mean*255]",
            "info:",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ImageMagick 'convert' failed: {result.stderr.strip()}")
    try:
        return float(result.stdout.strip())
    except ValueError:
        raise RuntimeError(f"Unexpected output from ImageMagick: {result.stdout!r}")


def invert_icon(src: str, dst: str) -> None:
    """Invert RGB channels of src, write result to dst. Alpha channel is preserved."""
    result = subprocess.run(
        ["convert", src, "-channel", "RGB", "-negate", dst],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ImageMagick 'convert' failed: {result.stderr.strip()}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Detect and invert dark icons for use on dark-background diagrams.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("icon", help="Path to the icon file (PNG, WebP, SVG, etc.)")
    parser.add_argument(
        "-o", "--output",
        help="Output path (default: <name>-light.<ext> in the same directory)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Invert regardless of brightness (skip the dark-icon check)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report brightness and whether inversion is recommended, then exit",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=DEFAULT_THRESHOLD,
        metavar="N",
        help=f"Mean brightness threshold 0–255 (default {DEFAULT_THRESHOLD}); "
             f"icons below this are treated as dark",
    )
    args = parser.parse_args()

    src = Path(args.icon)
    if not src.exists():
        print(f"Error: file not found: {src}", file=sys.stderr)
        sys.exit(1)

    try:
        brightness = get_mean_brightness(str(src))
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    is_dark = brightness < args.threshold

    if args.check:
        verdict = "DARK — recommend inverting" if is_dark else "LIGHT — no inversion needed"
        print(f"{src.name}: mean brightness = {brightness:.1f}/255 → {verdict}")
        sys.exit(0)

    if not is_dark and not args.force:
        print(
            f"{src.name}: already light (brightness={brightness:.1f}/255) — skipping. "
            f"Use --force to invert anyway."
        )
        sys.exit(0)

    dst = Path(args.output) if args.output else src.parent / f"{src.stem}-light{src.suffix}"

    try:
        invert_icon(str(src), str(dst))
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    action = "force-inverted" if args.force and not is_dark else "inverted"
    print(f"{src.name}: brightness={brightness:.1f}/255 ({action}) → {dst.name}")


if __name__ == "__main__":
    main()
