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
from PIL import Image, ImageOps


def optimize_layout(page_images: List[Image.Image], max_pages: int = 2,
                    page_size: Tuple[int, int] = (1700, 2200),
                    dark_mode: bool = False) -> List[Image.Image]:
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
    """
    if max_pages < 1:
        raise ValueError("max_pages must be at least 1")

    target_width, target_height = page_size

    # First, scale all images to the target width
    scaled_images = []
    total_height = 0
    for img in page_images:
        w, h = img.size
        ratio = target_width / w
        new_h = int(h * ratio)
        resized = img.resize((target_width, new_h), Image.LANCZOS)
        scaled_images.append(resized)
        total_height += new_h

    # Calculate required height per page to fit everything into max_pages
    # We add a small buffer or just use the exact division
    required_page_height = total_height / max_pages

    # If required height per page is more than our target page_height,
    # we must scale everything down further.
    if required_page_height > target_height:
        overall_scale = target_height / required_page_height
        new_scaled_images = []
        total_height = 0
        for img in scaled_images:
            w, h = img.size
            new_h = int(h * overall_scale)
            # Ensure new_h is at least 1
            new_h = max(1, new_h)
            resized = img.resize((target_width, new_h), Image.LANCZOS)
            new_scaled_images.append(resized)
            total_height += new_h
        scaled_images = new_scaled_images

    # Now we pack them into pages. To strictly respect max_pages,
    # we might need to split an image if it crosses the page boundary.
    bg_color = (30, 30, 30) if dark_mode else 'white'
    pages: List[Image.Image] = []
    current_page = Image.new('RGB', page_size, color=bg_color)
    y_offset = 0

    for img in scaled_images:
        remaining_h = img.size[1]
        img_y = 0

        while remaining_h > 0:
            space_left = target_height - y_offset

            if space_left <= 0:
                pages.append(current_page)
                current_page = Image.new('RGB', page_size, color=bg_color)
                y_offset = 0
                space_left = target_height

            can_take = min(remaining_h, space_left)
            # Crop the part of the image that fits
            part = img.crop((0, img_y, target_width, img_y + can_take))
            if dark_mode:
                part = ImageOps.invert(part.convert("RGB"))
            current_page.paste(part, (0, y_offset))

            y_offset += can_take
            img_y += can_take
            remaining_h -= can_take

            if len(pages) >= max_pages:
                # We reached the limit, stop here even if more content
                # This ensures we strictly respect max_pages
                break
        if len(pages) >= max_pages:
            break

    if len(pages) < max_pages:
        pages.append(current_page)

    # Final check to ensure we don't exceed max_pages due to rounding/last page
    return pages[:max_pages]
