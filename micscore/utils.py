"""Utility functions for MicScore.

This module contains helper functions used throughout the project,
including margin detection and cropping.
"""

from typing import Tuple
from PIL import Image, ImageOps

def crop_margins(img: Image.Image, threshold: int = 240) -> Image.Image:
    """Crop white margins from an image.

    Args:
        img: A PIL Image in RGB or grayscale mode.
        threshold: A value between 0 and 255 that defines what is
            considered "white". Pixels with values above this
            threshold are treated as background.

    Returns:
        A new PIL Image with the surrounding white margins removed. If
        the entire image is blank, the original image is returned.
    """
    # Convert to grayscale and invert so white becomes black
    gray = img.convert("L")

    # Apply threshold: anything > threshold becomes white (255), else black (0)
    # Then invert so the original white background becomes black (0)
    bw = gray.point(lambda x: 0 if x > threshold else 255, '1')

    # getbbox() returns the bounding box of non-zero (white) pixels
    bbox = bw.getbbox()

    if not bbox:
        return img

    return img.crop(bbox)
