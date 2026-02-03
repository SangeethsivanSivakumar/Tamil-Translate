"""
Tamil Translate - Sanskrit/Hindi PDF translation to English and Tamil.

This package provides a pipeline for translating scanned PDF documents
containing Sanskrit (Devanagari) and Hindi text to English and Tamil
using PaddleOCR PP-OCRv5 for OCR and Sarvam AI for translation.
"""

__version__ = "0.1.0"
__author__ = "Sangeeth Sivan"

from tamil_translate.config import Config
from tamil_translate.pipeline import TranslationPipeline

__all__ = ["Config", "TranslationPipeline", "__version__"]
