"""
OCR processing module supporting multiple OCR backends.

Supports:
- Tesseract OCR with Sanskrit/Hindi language packs (recommended for manuscripts)
- PaddleOCR PP-OCRv3 for modern Hindi text

Handles text extraction from PDF pages with Devanagari script support,
adaptive preprocessing for low-confidence pages, and Unicode normalization.
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
from typing import Iterator, List, Literal, Optional, Tuple, Union

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

        # Run Tesseract OCR
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
        )

        full_text = result.stdout.strip()

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
            try:
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp_path = Path(tmp.name)

                processed_image = self._apply_preprocessing_pipeline(Image.open(image_path))
                processed_image.save(tmp_path)

                result = self.extract_text(tmp_path, page_num)
                tmp_path.unlink()

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
            if len(img_array.shape) == 3:
                denoised = cv2.fastNlMeansDenoisingColored(img_array, None, 10, 10, 7, 21)
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


class OCREngine:
    """
    OCR engine using PaddleOCR PP-OCRv3 for Devanagari text extraction.

    Note: For classical Sanskrit manuscripts, TesseractOCREngine is recommended.

    Features:
    - Devanagari script recognition (Sanskrit and Hindi)
    - Adaptive preprocessing for low-confidence results
    - Unicode NFC normalization for consistent output
    - Memory-efficient page streaming
    """

    def __init__(self, use_gpu: bool = False):
        """
        Initialize the OCR engine.

        Args:
            use_gpu: Whether to use GPU acceleration (default False for CPU)
        """
        self.use_gpu = use_gpu
        self._ocr = None
        self._initialized = False

    def _lazy_init(self) -> None:
        """Lazily initialize PaddleOCR on first use."""
        if self._initialized:
            return

        try:
            from paddleocr import PaddleOCR

            # Initialize PaddleOCR with Hindi/Devanagari model
            # Using PP-OCRv3 which has stable support for Hindi ('hi')
            # The 'hi' language code for Devanagari script (Hindi/Sanskrit)
            self._ocr = PaddleOCR(
                lang="hi",  # Hindi/Devanagari script model
                ocr_version="PP-OCRv3",  # PP-OCRv3 for stable Hindi support
                use_textline_orientation=True,  # Detect text orientation
            )
            self._initialized = True
            self._use_predict_api = True  # PP-OCRv3 uses predict API
            logger.info("PaddleOCR initialized with Hindi/Devanagari model (PP-OCRv3)")
        except Exception as e:
            # Fallback to devanagari language code without version
            logger.warning(f"PP-OCRv3 initialization failed: {e}, trying devanagari lang")
            try:
                self._ocr = PaddleOCR(
                    lang="devanagari",  # Try devanagari language code
                    use_angle_cls=True,
                )
                self._initialized = True
                self._use_predict_api = False  # Legacy API uses .ocr() method
                logger.info("PaddleOCR initialized with Devanagari model (legacy)")
            except Exception as e2:
                # Final fallback: try Chinese model (multilingual)
                logger.warning(f"Devanagari init failed: {e2}, using multilingual model")
                try:
                    self._ocr = PaddleOCR(
                        lang="ch",  # Chinese/multilingual model
                        use_angle_cls=True,
                    )
                    self._initialized = True
                    self._use_predict_api = False
                    logger.info("PaddleOCR initialized with multilingual model (ch)")
                except ImportError as e3:
                    raise ImportError(
                        "PaddleOCR not installed. Install with: pip install paddleocr paddlepaddle"
                    ) from e3

    def extract_text(self, image_path: Path, page_num: int = 1) -> OCRResult:
        """
        Extract text from a single page image.

        Args:
            image_path: Path to the page image file
            page_num: Page number for tracking

        Returns:
            OCRResult with extracted text and metadata
        """
        self._lazy_init()
        start_time = time.time()

        lines = []
        confidences = []

        if getattr(self, '_use_predict_api', True):
            # Use predict API (PP-OCRv3/v4/v5)
            result = self._ocr.predict(input=str(image_path))
            if result:
                for res in result:
                    # PP-OCRv3+ format: uses dict-style access for rec_texts/rec_scores
                    try:
                        rec_texts = res['rec_texts'] or []
                        rec_scores = res['rec_scores'] or []
                        for text, score in zip(rec_texts, rec_scores):
                            if text:
                                lines.append(str(text))
                                confidences.append(float(score))
                    except (KeyError, TypeError):
                        # Alternative format: ocr_result list
                        if isinstance(res, dict) and "ocr_result" in res:
                            for item in res.get("ocr_result", []):
                                text = item.get("text", "")
                                score = item.get("score", 0.0)
                                if text:
                                    lines.append(text)
                                    confidences.append(score)
        else:
            # Use legacy .ocr() API
            result = self._ocr.ocr(str(image_path), cls=True)
            if result and result[0]:
                for line in result[0]:
                    if len(line) >= 2:
                        text = line[1][0]  # Extracted text
                        conf = line[1][1]  # Confidence score
                        lines.append(text)
                        confidences.append(conf)

        # Combine text and calculate average confidence
        full_text = "\n".join(lines)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Apply Unicode normalization (NFC)
        full_text = self.normalize_unicode(full_text)

        processing_time = time.time() - start_time

        # Detect language (basic heuristic based on script patterns)
        language = self._detect_language(full_text)

        return OCRResult(
            page_num=page_num,
            full_text=full_text,
            confidence=avg_confidence,
            language_detected=language,
            processing_time=processing_time,
            line_count=len(lines),
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
            try:
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp_path = Path(tmp.name)

                processed_image = self._apply_preprocessing_pipeline(Image.open(image_path))
                processed_image.save(tmp_path)

                result = self.extract_text(tmp_path, page_num)
                tmp_path.unlink()

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
            ("clahe", self._apply_clahe),
            ("denoise", self._apply_denoise),
            ("sharpen", self._apply_sharpen),
            ("binarize", self._apply_binarize),
        ]

        for strategy_name, preprocess_fn in preprocessing_strategies:
            try:
                # Create temporary preprocessed image
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp_path = Path(tmp.name)

                processed_image = preprocess_fn(Image.open(image_path))
                processed_image.save(tmp_path)

                # Try OCR on preprocessed image
                new_result = self.extract_text(tmp_path, page_num)

                # Keep if better confidence
                if new_result.confidence > best_result.confidence:
                    logger.info(
                        f"Page {page_num}: {strategy_name} improved confidence "
                        f"from {best_result.confidence:.2%} to {new_result.confidence:.2%}"
                    )
                    best_result = new_result

                # Clean up temp file
                tmp_path.unlink()

                # Stop if we've reached good enough confidence
                if best_result.is_high_confidence():
                    break

            except Exception as e:
                logger.debug(f"Preprocessing {strategy_name} failed: {e}")
                continue

        return best_result

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

    def _apply_clahe(self, image: Image.Image) -> Image.Image:
        """Apply Contrast Limited Adaptive Histogram Equalization."""
        try:
            import cv2
            import numpy as np

            # Convert to grayscale numpy array
            gray = image.convert("L")
            img_array = np.array(gray)

            # Apply CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(img_array)

            return Image.fromarray(enhanced)
        except ImportError:
            # Fallback: simple contrast enhancement
            enhancer = ImageEnhance.Contrast(image)
            return enhancer.enhance(1.5)

    def _apply_denoise(self, image: Image.Image) -> Image.Image:
        """Apply denoising filter."""
        try:
            import cv2
            import numpy as np

            img_array = np.array(image)
            denoised = cv2.fastNlMeansDenoisingColored(img_array, None, 10, 10, 7, 21)
            return Image.fromarray(denoised)
        except ImportError:
            # Fallback: median filter
            return image.filter(ImageFilter.MedianFilter(size=3))

    def _apply_sharpen(self, image: Image.Image) -> Image.Image:
        """Apply sharpening filter."""
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(2.0)

    def _apply_binarize(self, image: Image.Image) -> Image.Image:
        """Apply adaptive thresholding for binarization."""
        try:
            import cv2
            import numpy as np

            gray = image.convert("L")
            img_array = np.array(gray)

            # Adaptive thresholding
            binary = cv2.adaptiveThreshold(
                img_array,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2,
            )
            return Image.fromarray(binary)
        except ImportError:
            # Fallback: simple threshold
            gray = image.convert("L")
            return gray.point(lambda x: 255 if x > 128 else 0, mode="1").convert("L")

    def _detect_language(self, text: str) -> str:
        """
        Detect if text is primarily Sanskrit or Hindi.

        This is a basic heuristic based on common patterns.
        For production, consider using a proper language detection API.

        Args:
            text: Input text in Devanagari

        Returns:
            Language code ('sa-IN' for Sanskrit, 'hi-IN' for Hindi)
        """
        # Sanskrit indicators: more conjunct consonants, vedic markers
        # Hindi indicators: more common everyday words, specific particles

        # For now, default to Sanskrit as this is primarily for religious texts
        # The Sarvam API will handle mixed content appropriately
        return "sa-IN"

    @staticmethod
    def normalize_unicode(text: str) -> str:
        """
        Normalize Unicode text to NFC form.

        NFC (Canonical Composition) ensures consistent representation
        of Devanagari characters and prevents corruption from different
        encoding forms.

        Args:
            text: Input text

        Returns:
            NFC-normalized text
        """
        return unicodedata.normalize("NFC", text)

    @staticmethod
    def validate_devanagari(text: str) -> bool:
        """
        Validate that Devanagari text has no orphaned combining marks.

        Args:
            text: Input text to validate

        Returns:
            True if valid

        Raises:
            ValueError: If orphaned combining marks are found
        """
        for i, char in enumerate(text):
            category = unicodedata.category(char)
            # Mn = Mark, Nonspacing; Mc = Mark, Spacing Combining; Me = Mark, Enclosing
            if category in ("Mn", "Mc", "Me"):
                if i == 0:
                    raise ValueError(f"Orphaned combining mark at position 0: {repr(char)}")
                prev_category = unicodedata.category(text[i - 1])
                # Should follow a letter (Lo, Ll, Lu)
                if prev_category not in ("Lo", "Ll", "Lu", "Mn", "Mc"):
                    raise ValueError(
                        f"Orphaned combining mark at position {i}: {repr(char)}"
                    )
        return True


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


def create_ocr_engine(
    backend: Literal["tesseract", "paddle", "auto"] = "auto",
    **kwargs,
) -> Union[TesseractOCREngine, OCREngine]:
    """
    Factory function to create an OCR engine.

    Args:
        backend: OCR backend to use:
            - "tesseract": Use Tesseract (recommended for Sanskrit manuscripts)
            - "paddle": Use PaddleOCR (for modern Hindi text)
            - "auto": Try Tesseract first, fall back to PaddleOCR
        **kwargs: Additional arguments passed to the OCR engine

    Returns:
        Configured OCR engine instance
    """
    if backend == "tesseract":
        return TesseractOCREngine(**kwargs)
    elif backend == "paddle":
        return OCREngine(**kwargs)
    elif backend == "auto":
        # Try Tesseract first (better for Sanskrit manuscripts)
        try:
            if shutil.which("tesseract"):
                # Check if Sanskrit language is available
                result = subprocess.run(
                    ["tesseract", "--list-langs"],
                    capture_output=True, text=True
                )
                if "san" in result.stdout:
                    logger.info("Using Tesseract OCR (Sanskrit support detected)")
                    return TesseractOCREngine(**kwargs)
        except Exception as e:
            logger.debug(f"Tesseract check failed: {e}")

        # Fall back to PaddleOCR
        logger.info("Falling back to PaddleOCR")
        return OCREngine(**kwargs)
    else:
        raise ValueError(f"Unknown OCR backend: {backend}")
