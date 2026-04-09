"""Utility functions for MicScore.

This module contains helper functions used throughout the project,
including margin detection and cropping.
"""

from typing import Tuple
from PIL import Image

def crop_margins(img: Image.Image, threshold: int = 240) -> Image.Image:
    """Crop white margins from an image.

    Args:
        img: A PIL Image in RGB or grayscale mode.  The function
            converts the image to grayscale internally.
        threshold: A value between 0 and 255 that defines what is
            considered "white".  Pixels with values above this
            threshold are treated as background.

    Returns:
        A new PIL Image with the surrounding white margins removed.  If
        the entire image is blank (all pixels above the threshold), the
        original image is returned unchanged.
    """
    # Convert to grayscale for easier processing
    gray = img.convert("L")
    width, height = gray.size
    # Get pixel data as a list
    data = gray.load()

    # Find top
    top = 0
    for y in range(height):
        for x in range(width):
            if data[x, y] < threshold:
                top = y
                break
        else:
            continue
        break

    # Find bottom
    bottom = height - 1
    for y in range(height - 1, -1, -1):
        for x in range(width):
            if data[x, y] < threshold:
                bottom = y
                break
        else:
            continue
        break

    # Find left
    left = 0
    for x in range(width):
        for y in range(height):
            if data[x, y] < threshold:
                left = x
                break
        else:
            continue
        break

    # Find right
    right = width - 1
    for x in range(width - 1, -1, -1):
        for y in range(height):
            if data[x, y] < threshold:
                right = x
                break
        else:
            continue
        break

    # If we didn't find any non‑white pixels, return original image
    if top >= bottom or left >= right:
        return img

    # Crop using computed bounds
    bbox = (left, top, right + 1, bottom + 1)
    return img.crop(bbox)


def scale_image(img: Image.Image, target_width: int) -> Image.Image:
    """Scale an image to a given width while maintaining aspect ratio.

    Args:
        img: A PIL Image.
        target_width: The desired width in pixels.

    Returns:
        A new PIL Image scaled so that its width equals ``target_width``
        and its height is adjusted to preserve the aspect ratio.
    """
    w, h = img.size
    ratio = target_width / w
    new_height = int(h * ratio)
    return img.resize((target_width, new_height), Image.LANCZOS)
