# MicScore

MicScore is a **proof‑of‑concept tool** that demonstrates how one might begin to automate
the process of turning a full piano/vocal score into a performance‑ready
accompaniment sheet that fits on a limited number of pages.  The original
specification calls for intelligent musical reduction, detection of repeated
sections, simplification of dense textures, and layout optimisation to avoid
page turns.  Delivering a complete solution requires advanced optical music
recognition (OMR) and music theory heuristics which are outside the scope of
this prototype.  Instead, this project focuses on building a modular
foundation and implementing the page optimisation pipeline while leaving
place‑holders where more sophisticated score analysis and reduction
algorithms could be integrated.

## Features

* **PDF ingestion** – the tool accepts a PDF score as input and converts it
  into a sequence of images using `pdf2image`.  This supports scores that are
  already typeset in a PDF format.
* **Margin cropping** – pages are automatically cropped to remove white
  margins.  This helps maximise the usable space when multiple pages are
  merged together.
* **Page merging** – given a target page count (e.g. 2 pages), the tool
  combines the original pages vertically into a smaller number of pages while
  preserving the aspect ratio.  This eliminates page turns during
  performance.
* **Modular design** – the code base is structured into parser, simplifier
  and layout modules.  Functions that would handle musical simplification
  (detecting structure, reducing left/right hand parts, adding chord
  symbols, etc.) are included as stubs with detailed docstrings.  These
  stubs provide guidance on where and how future logic should be implemented.

## Limitations

* **No optical music recognition** – this prototype does not interpret
  musical notation.  It cannot detect melodies, harmonies or section
  structure.  Libraries such as `audiveris` or commercial OMR APIs would be
  required for a full solution.
* **No actual musical reduction** – the `simplifier` module contains
  placeholder functions for reducing accompaniment patterns and extracting
  chord symbols.  They currently return the input unchanged.
* **Scaling only** – the layout optimiser simply scales and stacks the
  original pages into the desired number of pages.  Consequently, the
  resulting notation may be very small if the original score is long.

## Installation

This project targets Python 3.8+ and depends on a few open‑source libraries
that are commonly available.  To install the dependencies, run:

```bash
pip install -r requirements.txt
```

The primary dependencies are:

* **pdf2image** – converts PDFs into PIL images.  Requires `poppler` on
  your system (see the pdf2image documentation).
* **Pillow** – image processing library used for cropping and merging pages.
* **reportlab** – used in unit tests for generating sample PDFs.

## Usage

To run the command‑line interface and generate a simplified (merged) score:

```bash
python3 -m micscore --input /path/to/score.pdf --output simplified.pdf --pages 2 --dark-mode
```

* `--input` specifies the path to the source PDF.
* `--output` is the path where the generated PDF will be written.
* `--pages` sets the maximum number of pages in the output (default: 2).
* `--dark-mode` (optional) generates a dark-themed PDF with inverted colors.

The program converts each page of the input into an image, crops margins,
scales the pages to fit the target page count, and merges them. The
resulting PDF will contain exactly the requested number of pages, splitting
images across pages if necessary to maximize readability and fit.

## Project structure

```
micscore/
├─ README.md             – this file
├─ requirements.txt      – Python dependencies
├─ app.py                – command‑line interface
├─ parser.py             – PDF ingestion and image conversion
├─ simplifier.py         – placeholder for musical simplification logic
├─ layout.py             – layout optimiser and page merging functions
└─ utils.py              – helper functions (margin detection, cropping)
```

## Contributing

The current implementation is a minimal starting point.  If you wish to
extend it, the following areas are prime candidates:

* **Score analysis** – integrate an OMR library (such as Audiveris) to
  convert page images into symbolic notation (MusicXML).  Then use a music
  theory library (e.g. `music21`) to detect structure and harmonies.
* **Reduction algorithms** – implement functions in `simplifier.py` to
  reduce left hand arpeggios, extract and preserve melody cues, and
  generate chord symbols.
* **Layout improvements** – instead of uniformly scaling pages, use the
  structure information to group related measures and avoid splitting
  phrases across page boundaries.

We hope this prototype serves as a useful foundation for further research
and development of the MicScore concept.
