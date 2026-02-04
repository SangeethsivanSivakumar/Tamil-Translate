"""
OCR processing module using Tesseract for Sanskrit/Hindi text extraction.

Features:
- Sanskrit (san) and Hindi (hin) language support via Tesseract
- Adaptive preprocessing for low-confidence results
- Unicode NFC normalization for consistent output
- Memory-efficient page streaming
"""

import gc
import logging
import shutil
import subprocess
import tempfile
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional, Tuple

from PIL import Image, ImageEnhance, ImageFilter

from tamil_translate.config import get_config

logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    """Result from OCR processing of a single page."""

    page_num: int
    full_text: str
    confidence: float
    language_detected: str  # 'sa-IN' (Sanskrit) or 'hi-IN' (Hindi)
    processing_time: float
    line_count: int
    char_count: int

    def is_high_confidence(self) -> bool:
        """Check if confidence meets the threshold."""
        config = get_config()
        return self.confidence >= config.OCR_CONFIDENCE_THRESHOLD

    def __repr__(self) -> str:
        return (
            f"OCRResult(page={self.page_num}, confidence={self.confidence:.2%}, "
            f"chars={self.char_count}, time={self.processing_time:.2f}s)"
        )


class TesseractOCREngine:
    """
    OCR engine using Tesseract with Sanskrit/Hindi language support.

    Recommended for classical Sanskrit manuscripts where PaddleOCR struggles.
    Requires tesseract-ocr and tesseract-lang packages installed.

    Features:
    - Sanskrit (san) and Hindi (hin) language support
    - Better recognition of traditional Devanagari typography
    - Configurable page segmentation modes
    - Unicode NFC normalization for consistent output
    """

    def __init__(self, languages: str = "san+hin", psm: int = 6):
        """
        Initialize the Tesseract OCR engine.

        Args:
            languages: Tesseract language codes (default "san+hin" for Sanskrit+Hindi)
            psm: Page segmentation mode (default 6 = uniform block of text)
                 3 = fully automatic, 6 = uniform block, 11 = sparse text
        """
        self.languages = languages
        self.psm = psm
        self._tesseract_path = shutil.which("tesseract")

        if not self._tesseract_path:
            raise RuntimeError(
                "Tesseract not found. Install with:\n"
                "  macOS: brew install tesseract tesseract-lang\n"
                "  Ubuntu: apt-get install tesseract-ocr tesseract-ocr-san tesseract-ocr-hin"
            )

        logger.info(f"TesseractOCREngine initialized with languages={languages}, psm={psm}")

    def extract_text(self, image_path: Path, page_num: int = 1) -> OCRResult:
        """
        Extract text from a single page image using Tesseract.

        Args:
            image_path: Path to the page image file
            page_num: Page number for tracking

        Returns:
            OCRResult with extracted text and metadata
        """
        start_time = time.time()

        # Run Tesseract OCR with timeout
        # Note: close_fds=True is needed for thread safety when running from worker threads
        try:
            result = subprocess.run(
                [
                    self._tesseract_path,
                    str(image_path),
                    "stdout",
                    "-l", self.languages,
                    "--psm", str(self.psm),
                ],
                capture_output=True,
                text=True,
                timeout=120,
                close_fds=True,
            )
            full_text = result.stdout.strip()
        except subprocess.TimeoutExpired:
            logger.error(f"Page {page_num}: Tesseract OCR timed out after 120 seconds")
            return OCRResult(
                page_num=page_num,
                full_text="",
                confidence=0.0,
                language_detected="sa-IN",
                processing_time=time.time() - start_time,
                line_count=0,
                char_count=0,
            )

        # Apply Unicode normalization (NFC)
        full_text = self.normalize_unicode(full_text)

        # Count lines
        lines = [line for line in full_text.split("\n") if line.strip()]
        line_count = len(lines)

        processing_time = time.time() - start_time

        # Tesseract doesn't provide per-line confidence easily,
        # so we estimate based on content quality
        confidence = self._estimate_confidence(full_text)

        # Detect language
        language = self._detect_language(full_text)

        return OCRResult(
            page_num=page_num,
            full_text=full_text,
            confidence=confidence,
            language_detected=language,
            processing_time=processing_time,
            line_count=line_count,
            char_count=len(full_text),
        )

    def extract_with_adaptive_preprocessing(
        self, image_path: Path, page_num: int = 1
    ) -> OCRResult:
        """
        Extract text with preprocessing applied BEFORE OCR.

        If preprocessing is enabled in config, applies the full pipeline
        (grayscale → denoise → binarize) before initial OCR attempt.
        If result is still low confidence, tries original image as fallback.

        Args:
            image_path: Path to the page image file
            page_num: Page number for tracking

        Returns:
            Best OCRResult from preprocessing attempts
        """
        config = get_config()

        # If preprocessing is enabled, apply it BEFORE initial OCR
        if config.OCR_PREPROCESS_ENABLED:
            logger.debug(f"Page {page_num}: Applying preprocessing pipeline before OCR")
            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp_path = Path(tmp.name)

                processed_image = self._apply_preprocessing_pipeline(Image.open(image_path))
                processed_image.save(tmp_path)

                result = self.extract_text(tmp_path, page_num)

                if result.is_high_confidence():
                    return result

                # Low confidence with preprocessing, try original as fallback
                logger.warning(
                    f"Page {page_num}: Preprocessed confidence low ({result.confidence:.2%}), "
                    "trying original image..."
                )
                original_result = self.extract_text(image_path, page_num)
                if original_result.confidence > result.confidence:
                    logger.info(
                        f"Page {page_num}: Original image better "
                        f"({original_result.confidence:.2%} vs {result.confidence:.2%})"
                    )
                    return original_result
                return result

            except Exception as e:
                logger.warning(f"Page {page_num}: Preprocessing failed ({e}), using original")
                return self.extract_text(image_path, page_num)
            finally:
                if tmp_path is not None and tmp_path.exists():
                    tmp_path.unlink()

        # Preprocessing disabled: use original approach
        result = self.extract_text(image_path, page_num)

        if result.is_high_confidence():
            return result

        logger.warning(
            f"Page {page_num}: Low confidence ({result.confidence:.2%}), "
            "trying adaptive preprocessing..."
        )

        # Try different preprocessing strategies
        best_result = result
        preprocessing_strategies = [
            ("binarize", self._apply_binarize),
            ("denoise", self._apply_denoise),
            ("sharpen", self._apply_sharpen),
        ]

        for strategy_name, preprocess_fn in preprocessing_strategies:
            try:
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp_path = Path(tmp.name)

                processed_image = preprocess_fn(Image.open(image_path))
                processed_image.save(tmp_path)

                new_result = self.extract_text(tmp_path, page_num)

                if new_result.confidence > best_result.confidence:
                    logger.info(
                        f"Page {page_num}: {strategy_name} improved confidence "
                        f"from {best_result.confidence:.2%} to {new_result.confidence:.2%}"
                    )
                    best_result = new_result

                tmp_path.unlink()

                if best_result.is_high_confidence():
                    break

            except Exception as e:
                logger.debug(f"Preprocessing {strategy_name} failed: {e}")
                continue

        return best_result

    def _estimate_confidence(self, text: str) -> float:
        """
        Estimate OCR confidence based on text quality heuristics.

        Args:
            text: Extracted text

        Returns:
            Estimated confidence score (0.0 to 1.0)
        """
        if not text:
            return 0.0

        # Count Devanagari characters
        devanagari_count = sum(1 for c in text if '\u0900' <= c <= '\u097F')
        total_chars = len(text.replace(" ", "").replace("\n", ""))

        if total_chars == 0:
            return 0.0

        # Ratio of Devanagari to total characters
        devanagari_ratio = devanagari_count / total_chars

        # High Devanagari ratio indicates good Sanskrit/Hindi recognition
        # Penalize for too much garbage (non-Devanagari, non-punctuation)
        punctuation = set("।॥,.!?;:'-()\"")
        noise_count = sum(
            1 for c in text
            if not ('\u0900' <= c <= '\u097F')
            and c not in punctuation
            and not c.isspace()
            and not c.isdigit()
        )
        noise_ratio = noise_count / total_chars if total_chars > 0 else 0

        # Calculate confidence
        confidence = devanagari_ratio * (1 - noise_ratio * 0.5)
        return min(max(confidence, 0.0), 1.0)

    def _detect_language(self, text: str) -> str:
        """Detect if text is primarily Sanskrit or Hindi."""
        return "sa-IN"  # Default to Sanskrit for manuscript texts

    def _apply_preprocessing_pipeline(self, image: Image.Image) -> Image.Image:
        """
        Apply full preprocessing pipeline: grayscale → denoise → binarize.

        This pipeline runs BEFORE OCR to improve recognition quality.

        Args:
            image: Input image

        Returns:
            Preprocessed image ready for OCR
        """
        logger.debug("Applying preprocessing pipeline: grayscale → denoise → binarize")

        # Step 1: Convert to grayscale
        gray = image.convert("L")

        # Step 2: Denoise
        try:
            import cv2
            import numpy as np

            img_array = np.array(gray)
            denoised = cv2.fastNlMeansDenoising(img_array, None, 10, 7, 21)
            gray = Image.fromarray(denoised)
        except ImportError:
            gray = gray.filter(ImageFilter.MedianFilter(size=3))

        # Step 3: Binarize (adaptive thresholding)
        try:
            import cv2
            import numpy as np

            img_array = np.array(gray)
            binary = cv2.adaptiveThreshold(
                img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2,
            )
            return Image.fromarray(binary)
        except ImportError:
            return gray.point(lambda x: 255 if x > 128 else 0, mode="1").convert("L")

    def _apply_binarize(self, image: Image.Image) -> Image.Image:
        """Apply adaptive thresholding for binarization."""
        try:
            import cv2
            import numpy as np

            gray = image.convert("L")
            img_array = np.array(gray)

            binary = cv2.adaptiveThreshold(
                img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2,
            )
            return Image.fromarray(binary)
        except ImportError:
            gray = image.convert("L")
            return gray.point(lambda x: 255 if x > 128 else 0, mode="1").convert("L")

    def _apply_denoise(self, image: Image.Image) -> Image.Image:
        """Apply denoising filter."""
        try:
            import cv2
            import numpy as np

            img_array = np.array(image)
            if len(img_array.shape) == 3 and img_array.shape[2] >= 3:
                # Handle alpha channel if present
                has_alpha = img_array.shape[2] == 4
                if has_alpha:
                    alpha = img_array[:, :, 3]
                    rgb = img_array[:, :, :3]
                else:
                    rgb = img_array

                # Convert RGB to BGR for OpenCV
                bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
                denoised_bgr = cv2.fastNlMeansDenoisingColored(bgr, None, 10, 10, 7, 21)
                # Convert BGR back to RGB
                denoised_rgb = cv2.cvtColor(denoised_bgr, cv2.COLOR_BGR2RGB)

                if has_alpha:
                    # Reattach alpha channel
                    denoised = np.dstack((denoised_rgb, alpha)).astype(np.uint8)
                else:
                    denoised = denoised_rgb.astype(np.uint8)
            else:
                denoised = cv2.fastNlMeansDenoising(img_array, None, 10, 7, 21)
            return Image.fromarray(denoised)
        except ImportError:
            return image.filter(ImageFilter.MedianFilter(size=3))

    def _apply_sharpen(self, image: Image.Image) -> Image.Image:
        """Apply sharpening filter."""
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(2.0)

    @staticmethod
    def normalize_unicode(text: str) -> str:
        """Normalize Unicode text to NFC form."""
        return unicodedata.normalize("NFC", text)


def extract_pages_from_pdf(
    pdf_path: Path, page_range: Optional[Tuple[int, int]] = None, dpi: Optional[int] = None
) -> Iterator[Tuple[int, Path]]:
    """
    Stream pages from a PDF as images.

    Memory-efficient: yields one page at a time and cleans up after use.

    Args:
        pdf_path: Path to the PDF file
        page_range: Optional (start, end) tuple for page range (1-indexed)
        dpi: Resolution for page rendering (default from config.OCR_DPI)

    Yields:
        Tuple of (page_number, temp_image_path)
    """
    # Use config DPI if not specified
    if dpi is None:
        config = get_config()
        dpi = config.OCR_DPI
    try:
        from pdf2image import convert_from_path
    except ImportError as e:
        raise ImportError(
            "pdf2image not installed. Install with: pip install pdf2image\n"
            "Also install poppler: brew install poppler (macOS) or apt-get install poppler-utils (Linux)"
        ) from e

    # Get total page count
    from PyPDF2 import PdfReader

    with open(pdf_path, "rb") as f:
        reader = PdfReader(f)
        total_pages = len(reader.pages)

    # Determine page range
    if page_range:
        start_page, end_page = page_range
        start_page = max(1, start_page)
        end_page = min(total_pages, end_page)
    else:
        start_page, end_page = 1, total_pages

    logger.info(f"Extracting pages {start_page}-{end_page} from {pdf_path.name}")

    # Stream pages one at a time (memory efficient)
    for page_num in range(start_page, end_page + 1):
        try:
            # Convert single page
            images = convert_from_path(
                pdf_path,
                first_page=page_num,
                last_page=page_num,
                dpi=dpi,
            )

            if images:
                # Save to temporary file
                with tempfile.NamedTemporaryFile(
                    suffix=".png", delete=False, prefix=f"page_{page_num}_"
                ) as tmp:
                    tmp_path = Path(tmp.name)
                    images[0].save(tmp_path, "PNG")

                yield page_num, tmp_path

                # Clean up image from memory
                del images

            # Force garbage collection to free memory
            gc.collect()

        except Exception as e:
            logger.error(f"Failed to extract page {page_num}: {e}")
            continue


def get_pdf_page_count(pdf_path: Path) -> int:
    """
    Get the number of pages in a PDF.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Number of pages
    """
    from PyPDF2 import PdfReader

    with open(pdf_path, "rb") as f:
        reader = PdfReader(f)
        return len(reader.pages)


def create_ocr_engine(**kwargs) -> TesseractOCREngine:
    """
    Factory function to create the Tesseract OCR engine.

    Args:
        **kwargs: Arguments passed to TesseractOCREngine (languages, psm)

    Returns:
        Configured TesseractOCREngine instance
    """
    return TesseractOCREngine(**kwargs)
