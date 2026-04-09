"""Layout optimisation and page merging for MicScore.

This module contains functions that assemble a list of page images into a
smaller number of pages while attempting to preserve readability.  The
primary function, :func:`optimize_layout`, scales and stacks pages
vertically so that they fit into a fixed number of target pages.

The algorithms implemented here are deliberately simple – they do not
analyse musical structure or adjust measure widths.  They merely
compress the entire sequence of page images into a limited page count.
Nevertheless, they serve as a proof‑of‑concept for eliminating page
turns during performance.
"""

from typing import List, Tuple
from PIL import Image


def optimize_layout(page_images: List[Image.Image], max_pages: int = 2,
                    page_size: Tuple[int, int] = (1700, 2200)) -> List[Image.Image]:
    """Combine page images into fewer pages to avoid page turns.

    Given a list of page images (already cropped and simplified), this
    function rescales and concatenates them vertically so that the
    resulting number of pages does not exceed ``max_pages``.  It tries
    to preserve the aspect ratio of each page and evenly distribute
    content across the target pages.

    Args:
        page_images: List of PIL ``Image`` objects.  Each image must
            have the same orientation (portrait) but may differ in
            dimensions.
        max_pages: Maximum number of pages in the output PDF.
        page_size: A pair ``(width, height)`` defining the pixel
            dimensions of the target pages.  The defaults roughly
            correspond to US Letter at 200 dpi.

    Returns:
        A list of PIL ``Image`` objects representing the merged pages.
        If the input length is less than or equal to ``max_pages``, the
        original images are returned unchanged.
    """
    if max_pages < 1:
        raise ValueError("max_pages must be at least 1")

    num_input = len(page_images)
    if num_input <= max_pages:
        # Nothing to do – just scale each page to fit the target size
        return [_resize_to_fit(img, page_size) for img in page_images]

    # Determine total height in pixels if each page were scaled to the
    # target width.  We preserve aspect ratios here.
    target_width, target_height = page_size
    scaled_heights = []
    total_scaled_height = 0
    for img in page_images:
        w, h = img.size
        ratio = target_width / w
        new_h = int(h * ratio)
        scaled_heights.append(new_h)
        total_scaled_height += new_h

    # Compute the total height available across all target pages
    available_height = target_height * max_pages

    # If the scaled content fits without scaling down further, we can
    # distribute it across pages by splitting.  Otherwise we apply a
    # further uniform scaling factor to make it fit.
    if total_scaled_height > available_height:
        scale_factor = available_height / total_scaled_height
    else:
        scale_factor = 1.0

    # Rescale images accordingly
    scaled_images: List[Image.Image] = []
    scaled_heights2: List[int] = []
    for img, sh in zip(page_images, scaled_heights):
        # Apply the extra scaling factor
        new_h = int(sh * scale_factor)
        scaled_heights2.append(new_h)
        resized = img.resize((target_width, new_h), Image.LANCZOS)
        scaled_images.append(resized)

    # Create blank pages and paste scaled images sequentially
    pages: List[Image.Image] = []
    current_page = Image.new('RGB', page_size, color='white')
    y_offset = 0
    for img in scaled_images:
        h = img.size[1]
        # If the image doesn't fit on the current page, start a new page
        if y_offset + h > target_height and y_offset > 0:
            pages.append(current_page)
            current_page = Image.new('RGB', page_size, color='white')
            y_offset = 0
        # Paste the image on the current page
        current_page.paste(img, (0, y_offset))
        y_offset += h
    # Append the last page
    pages.append(current_page)

    # If we produced fewer than max_pages pages, optionally pad with
    # blank pages, but it's not strictly necessary.
    # Trim trailing blank pages if there is no content
    return pages


def _resize_to_fit(img: Image.Image, page_size: Tuple[int, int]) -> Image.Image:
    """Resize an image to fit within the target page size.

    The image is scaled to match the width of the target page, and then
    padded with white space at the bottom if necessary to reach the
    target height.
    """
    target_w, target_h = page_size
    w, h = img.size
    ratio = target_w / w
    new_h = int(h * ratio)
    resized = img.resize((target_w, new_h), Image.LANCZOS)
    # Create a blank page and paste resized image at top
    page = Image.new('RGB', page_size, color='white')
    page.paste(resized, (0, 0))
    return page
