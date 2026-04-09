import unittest
from PIL import Image
import os
from micscore.utils import crop_margins
from micscore.layout import optimize_layout

class TestMicScore(unittest.TestCase):
    def test_crop_margins(self):
        # Create a 100x100 white image with a 50x50 black square in the middle
        img = Image.new('RGB', (100, 100), color='white')
        for x in range(25, 75):
            for y in range(25, 75):
                img.putpixel((x, y), (0, 0, 0))

        cropped = crop_margins(img)
        # BBox should be (25, 25, 75, 75)
        self.assertEqual(cropped.size, (50, 50))

    def test_optimize_layout_respects_max_pages(self):
        # Create 5 images of 100x200
        images = [Image.new('RGB', (100, 200), color='white') for _ in range(5)]

        # Merge into 2 pages of size 100x400
        merged = optimize_layout(images, max_pages=2, page_size=(100, 400))
        self.assertEqual(len(merged), 2)

    def test_optimize_layout_splits_images(self):
        # Create one large image that is taller than one page
        images = [Image.new('RGB', (100, 600), color='white')]

        # Merge into 2 pages of size 100x400
        # The 600 height image should be split: 400 on page 1, 200 on page 2
        merged = optimize_layout(images, max_pages=2, page_size=(100, 400))
        self.assertEqual(len(merged), 2)
        self.assertEqual(merged[0].size, (100, 400))
        self.assertEqual(merged[1].size, (100, 400))

    def test_dark_mode(self):
        # Create a white 50x50 image
        img = Image.new('RGB', (50, 50), color='white')

        # Merge into 100x100 page with dark mode
        # The 50x50 image will be scaled to 100x100
        merged = optimize_layout([img], max_pages=1, page_size=(100, 100), dark_mode=True)

        # Check pixel at (50, 50), should be near black (inverting white gives black)
        pixel = merged[0].getpixel((50, 50))
        self.assertTrue(pixel[0] < 50) # Should be (0,0,0) but allow some buffer if needed

        # We don't have empty background if the image covers the whole page
        # Let's try with a smaller image that doesn't cover the whole page
        img2 = Image.new('RGB', (100, 50), color='white')
        merged2 = optimize_layout([img2], max_pages=1, page_size=(100, 100), dark_mode=True)

        # Bottom half should be background color (30, 30, 30)
        bg_pixel = merged2[0].getpixel((50, 75))
        self.assertEqual(bg_pixel, (30, 30, 30))

if __name__ == '__main__':
    unittest.main()
