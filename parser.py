"""PDF ingestion utilities for MicScore.

This module wraps the ``pdf2image`` library to convert PDF documents
containing piano scores into a list of PIL ``Image`` objects.  It also
performs basic pre‑processing such as margin cropping to remove excess
white space.  More advanced optical music recognition is intentionally
omitted; the goal of this parser is simply to produce clean page images
that downstream algorithms can operate on.
"""

from typing import List, Optional
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image

from .utils import crop_margins


def parse_pdf(path: str, dpi: int = 200, crop: bool = True) -> List[Image.Image]:
    """Convert a PDF score into a list of PIL Images.

    Args:
        path: Path to the PDF file.
        dpi: Dots per inch used for rendering.  Higher values yield
            higher‑resolution images at the expense of performance.
        crop: Whether to crop white margins from each page.

    Returns:
        A list of PIL Image objects, one per page in the PDF.  If
        ``crop`` is True, margins will be removed using
        :func:`micscore.utils.crop_margins`.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        RuntimeError: If pdf2image cannot render the PDF (e.g. poppler
            is not installed).
    """
    pdf_path = Path(path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Convert pages to images.  We specify single_thread=True for
    # deterministic behaviour and fewer system resource requirements.
    try:
        pages = convert_from_path(str(pdf_path), dpi=dpi, single_file=False)
    except Exception as exc:
        raise RuntimeError(f"Failed to convert PDF to images: {exc}")

    images: List[Image.Image] = []
    for page in pages:
        if crop:
            page = crop_margins(page)
        images.append(page)
    return images
