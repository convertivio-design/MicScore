"""Command‑line interface for MicScore.

This module provides a simple CLI around the MicScore library.  It
accepts a piano/vocal score in PDF format, applies optional
simplification, and produces a new PDF with a reduced number of pages.
The default operation merges all pages into two pages to eliminate
page turns.
"""

import argparse
from pathlib import Path
from typing import Any, Dict

from PIL import Image

from .parser import parse_pdf
from .simplifier import simplify_score
from .layout import optimize_layout


def main(args: Any = None) -> None:
    parser = argparse.ArgumentParser(description="MicScore – simplify and merge piano scores")
    parser.add_argument("--input", "-i", required=True, help="Path to input PDF score")
    parser.add_argument("--output", "-o", required=True, help="Path to output simplified PDF")
    parser.add_argument("--pages", "-p", type=int, default=2, help="Maximum number of pages in output (default: 2)")
    parser.add_argument("--dpi", type=int, default=200, help="DPI for PDF rendering (default: 200)")
    parser.add_argument("--no-crop", action="store_true", help="Disable margin cropping")
    parser.add_argument("--dark-mode", action="store_true", help="Use a dark theme for the output PDF")
    parser.add_argument("--difficulty", choices=["easy", "intermediate", "advanced"], default="intermediate",
                        help="Target difficulty level (currently unused)")
    parser.add_argument("--preserve_style", choices=["strict", "moderate", "loose"], default="moderate",
                        help="How strictly to preserve the original style (currently unused)")
    parser.add_argument("--include_chords", action="store_true", help="Include chord symbols (currently unused)")
    parser.add_argument("--include_melody", action="store_true", help="Include melody cues (currently unused)")
    args_ns = parser.parse_args(args)

    input_path = Path(args_ns.input)
    output_path = Path(args_ns.output)
    max_pages = args_ns.pages

    # Minimalist CLI design using ANSI escape codes
    # Use dark gray/muted tones for the UI
    RESET = "\033[0m"
    DIM = "\033[2m"
    CYAN = "\033[36m"
    GRAY = "\033[90m"

    print(f"\n{GRAY}MicScore{RESET} {DIM}v0.1.0{RESET}\n")

    # Step 1: parse PDF into images
    print(f"{DIM}→ {RESET}Converting {CYAN}{input_path.name}{RESET}...")
    pages = parse_pdf(str(input_path), dpi=args_ns.dpi, crop=not args_ns.no_crop)

    # Step 2: simplify the score (no‑op for now)
    simplify_options: Dict[str, Any] = {
        "difficulty": args_ns.difficulty,
        "preserve_style": args_ns.preserve_style,
        "include_chords": args_ns.include_chords,
        "include_melody": args_ns.include_melody,
    }
    simplified_pages = simplify_score(pages, **simplify_options)

    # Step 3: optimise layout to fit target number of pages
    print(f"{DIM}→ {RESET}Merging into {CYAN}{max_pages}{RESET} page(s)...")
    merged_pages = optimize_layout(simplified_pages, max_pages=max_pages, dark_mode=args_ns.dark_mode)

    # Step 4: save as PDF
    if not merged_pages:
        raise RuntimeError("No pages produced by layout optimiser")

    print(f"{DIM}→ {RESET}Saving to {CYAN}{output_path.name}{RESET}...")
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # The first page calls save with append_images for the rest
    first_page: Image.Image = merged_pages[0]
    other_pages = merged_pages[1:]
    first_page.save(str(output_path), save_all=True, append_images=other_pages)
    print(f"\n{GRAY}Done.{RESET}\n")


if __name__ == "__main__":  # pragma: no cover
    main()
