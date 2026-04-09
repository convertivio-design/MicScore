"""Top‑level package for MicScore.

This package exposes a minimal API for converting piano scores into
performance‑friendly accompaniment layouts.  The core functions live in
``parser``, ``simplifier``, and ``layout`` modules.  See the
``README.md`` for usage instructions.
"""

__all__ = ["parse_pdf", "simplify_score", "optimize_layout"]

from .parser import parse_pdf
from .simplifier import simplify_score
from .layout import optimize_layout
