"""
Main translation pipeline orchestrator.

Coordinates OCR extraction, translation, and PDF generation
with progress tracking, error handling, and resume capability.
"""

import logging
import signal
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple

from tqdm import tqdm

from tamil_translate.config import Config, get_config
from tamil_translate.ocr_engine import (
    OCRResult,
    TesseractOCREngine,
    create_ocr_engine,
    extract_pages_from_pdf,
    get_pdf_page_count,
)
from tamil_translate.pdf_generator import TranslationPDFBuilder, check_fonts_available
from tamil_translate.security import validate_all
from tamil_translate.state_manager import PipelineState, StateManager
from tamil_translate.translator import TranslationService

logger = logging.getLogger(__name__)


class PipelineError(Exception):
    """Base exception for pipeline errors."""

    pass


class PipelineInterruptedError(PipelineError):
    """Raised when pipeline is interrupted (e.g., Ctrl+C)."""

    pass


@dataclass
class PipelineResult:
    """Result from running the translation pipeline."""

    success: bool
    pages_processed: int
    pages_failed: int
    total_cost_inr: float
    english_pdf_path: Optional[Path] = None
    tamil_pdf_path: Optional[Path] = None
    processing_time: float = 0.0
    error: Optional[str] = None

    def __repr__(self) -> str:
        status = "SUCCESS" if self.success else "FAILED"
        return (
            f"PipelineResult({status}, pages={self.pages_processed}, "
            f"cost=₹{self.total_cost_inr:.2f}, time={self.processing_time:.1f}s)"
        )


class TranslationPipeline:
    """
    Main translation pipeline that orchestrates the entire workflow.

    Flow:
    1. Validate input PDF and security
    2. Load or create state (for resume capability)
    3. For each page:
       a. Extract page image
       b. OCR with Tesseract
       c. Translate to English
       d. Translate to Tamil (two-step)
       e. Update state atomically
    4. Generate output PDFs
    5. Print cost summary
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        on_page_complete: Optional[Callable[[int, float], None]] = None,
    ):
        """
        Initialize the translation pipeline.

        Args:
            config: Configuration instance (default: global config)
            on_page_complete: Optional callback(page_num, cost) after each page
        """
        self.config = config or get_config()
        self.on_page_complete = on_page_complete

        # Components (lazy initialized)
        self._ocr_engine: Optional[TesseractOCREngine] = None
        self._translator: Optional[TranslationService] = None
        self._state_manager: Optional[StateManager] = None

        # State
        self._current_state: Optional[PipelineState] = None
        self._interrupted = False

        # Previous signal handlers (saved during run)
        self._prev_sigint = None
        self._prev_sigterm = None

    def _setup_signal_handlers(self) -> None:
        """Register signal handlers for graceful shutdown during run()."""
        # Signal handlers can only be set in the main thread
        if threading.current_thread() is not threading.main_thread():
            logger.debug("Skipping signal handlers (not in main thread)")
            return
        self._prev_sigint = signal.signal(signal.SIGINT, self._handle_interrupt)
        self._prev_sigterm = signal.signal(signal.SIGTERM, self._handle_interrupt)

    def _restore_signal_handlers(self) -> None:
        """Restore previous signal handlers after run() completes."""
        # Only restore if we're in the main thread and handlers were set
        if threading.current_thread() is not threading.main_thread():
            return
        if self._prev_sigint is not None:
            signal.signal(signal.SIGINT, self._prev_sigint)
        if self._prev_sigterm is not None:
            signal.signal(signal.SIGTERM, self._prev_sigterm)

    def _handle_interrupt(self, signum, frame) -> None:
        """Handle interrupt signals gracefully."""
        logger.warning("\nInterrupt received, saving state and shutting down...")
        self._interrupted = True

        # Save current state if available
        if self._current_state and self._state_manager:
            try:
                self._state_manager.save_state(self._current_state)
                logger.info("State saved successfully. Run again to resume.")
            except Exception as e:
                logger.error(f"Failed to save state: {e}")

    def request_interrupt(self) -> None:
        """
        Request the pipeline to stop gracefully.

        Thread-safe method to signal interruption from external code (e.g., TUI).
        The pipeline will save state and exit at the next safe checkpoint.
        """
        self._interrupted = True
        logger.info("Interrupt requested via request_interrupt()")

    @property
    def ocr_engine(self) -> TesseractOCREngine:
        """Get or create OCR engine."""
        if self._ocr_engine is None:
            self._ocr_engine = create_ocr_engine()
        return self._ocr_engine

    @property
    def translator(self) -> TranslationService:
        """Get or create translation service."""
        if self._translator is None:
            self._translator = TranslationService()
        return self._translator

    @property
    def state_manager(self) -> StateManager:
        """Get or create state manager."""
        if self._state_manager is None:
            self._state_manager = StateManager()
        return self._state_manager

    def run(
        self,
        pdf_path: str,
        page_range: Optional[Tuple[int, int]] = None,
        output_dir: Optional[Path] = None,
        resume: bool = True,
        dry_run: bool = False,
    ) -> PipelineResult:
        """
        Run the translation pipeline.

        Args:
            pdf_path: Path to the input PDF file
            page_range: Optional (start, end) tuple for page range
            output_dir: Optional output directory override
            resume: Whether to resume from previous run (default True)
            dry_run: If True, only estimate cost without processing

        Returns:
            PipelineResult with status and paths
        """
        start_time = time.time()

        # Set up signal handlers for graceful shutdown
        self._setup_signal_handlers()

        try:
            # 1. Validate input (skip API key check for dry runs)
            validated_path = validate_all(pdf_path, validate_api_key=not dry_run)
            logger.info(f"Processing: {validated_path.name}")

            # 2. Get PDF info
            total_pages = get_pdf_page_count(validated_path)
            logger.info(f"Total pages in PDF: {total_pages}")

            # 3. Determine page range
            if page_range is None:
                # Default to first 10 pages (safety)
                page_range = (1, min(self.config.DEFAULT_TEST_PAGES, total_pages))
                logger.info(
                    f"Using default page range: {page_range[0]}-{page_range[1]} "
                    f"(use --pages to change)"
                )
            else:
                # Validate and clamp page range
                start, end = page_range
                start = max(1, start)
                end = min(total_pages, end)
                page_range = (start, end)

            expected_pages = page_range[1] - page_range[0] + 1

            # 4. Dry run: just estimate cost
            if dry_run:
                return self._estimate_cost(validated_path, page_range, expected_pages)

            # 5. Check fonts
            fonts_status = check_fonts_available()
            if not all(fonts_status.values()):
                missing = [lang for lang, available in fonts_status.items() if not available]
                logger.warning(f"Missing fonts for: {missing}. PDF generation may fail.")

            # 6. Load or create state
            state = self._load_or_create_state(validated_path, total_pages, page_range, resume)
            self._current_state = state

            # 7. Process pages
            pages_processed = 0
            pages_failed = 0
            english_texts: Dict[int, str] = {}
            tamil_texts: Dict[int, str] = {}

            pending_pages = state.get_pending_pages()
            logger.info(f"Pages to process: {len(pending_pages)}")

            # Create progress bar
            with tqdm(total=len(pending_pages), desc="Processing", unit="page") as pbar:
                for page_num, image_path in extract_pages_from_pdf(
                    validated_path, page_range
                ):
                    # Check for interrupt
                    if self._interrupted:
                        raise PipelineInterruptedError("Pipeline interrupted by user")

                    # Skip completed pages
                    if page_num not in pending_pages:
                        # Load existing translations
                        page_state = state.get_page_state(page_num)
                        if page_state.english_text:
                            english_texts[page_num] = page_state.english_text
                        if page_state.tamil_text:
                            tamil_texts[page_num] = page_state.tamil_text
                        continue

                    try:
                        # Process single page
                        pbar.set_description(f"Page {page_num}")
                        page_cost = self._process_page(
                            page_num, image_path, state, english_texts, tamil_texts
                        )
                        pages_processed += 1

                        # Update progress
                        pbar.update(1)
                        pbar.set_postfix(
                            cost=f"₹{state.total_cost:.2f}",
                            progress=f"{state.progress_percentage:.1f}%",
                        )

                        # Callback
                        if self.on_page_complete:
                            self.on_page_complete(page_num, page_cost)

                    except Exception as e:
                        logger.error(f"Page {page_num} failed: {e}")
                        pages_failed += 1

                        # Update state with error
                        self.state_manager.update_page_state(
                            state, page_num, error=str(e)
                        )

                    finally:
                        # Clean up temp image
                        try:
                            image_path.unlink()
                        except Exception:
                            pass

            # 8. Generate output PDFs
            english_pdf = None
            tamil_pdf = None

            if english_texts:
                english_builder = TranslationPDFBuilder("english")
                english_pdf = english_builder.build_from_pages(
                    english_texts,
                    validated_path.name,
                    source_language="sanskrit",
                )
                logger.info(f"Generated: {english_pdf}")

            if tamil_texts:
                tamil_builder = TranslationPDFBuilder("tamil")
                tamil_pdf = tamil_builder.build_from_pages(
                    tamil_texts,
                    validated_path.name,
                    source_language="sanskrit",
                )
                logger.info(f"Generated: {tamil_pdf}")

            # 9. Return result
            processing_time = time.time() - start_time

            return PipelineResult(
                success=pages_failed == 0,
                pages_processed=pages_processed,
                pages_failed=pages_failed,
                total_cost_inr=state.total_cost,
                english_pdf_path=english_pdf,
                tamil_pdf_path=tamil_pdf,
                processing_time=processing_time,
            )

        except PipelineInterruptedError:
            processing_time = time.time() - start_time
            return PipelineResult(
                success=False,
                pages_processed=0,
                pages_failed=0,
                total_cost_inr=self._current_state.total_cost if self._current_state else 0,
                processing_time=processing_time,
                error="Pipeline interrupted. State saved. Run again to resume.",
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.exception(f"Pipeline failed: {e}")
            return PipelineResult(
                success=False,
                pages_processed=0,
                pages_failed=1,
                total_cost_inr=0,
                processing_time=processing_time,
                error=str(e),
            )
        finally:
            # Restore previous signal handlers
            self._restore_signal_handlers()

    def _load_or_create_state(
        self,
        pdf_path: Path,
        total_pages: int,
        page_range: Tuple[int, int],
        resume: bool,
    ) -> PipelineState:
        """Load existing state or create new one."""
        if resume:
            existing_state = self.state_manager.load_state(pdf_path)
            if existing_state:
                # Check if page range matches
                if (
                    existing_state.page_range_start == page_range[0]
                    and existing_state.page_range_end == page_range[1]
                ):
                    pending = existing_state.get_pending_pages()
                    logger.info(
                        f"Resuming from previous run: "
                        f"{existing_state.pages_completed_count} pages done, "
                        f"{len(pending)} remaining"
                    )
                    return existing_state
                else:
                    logger.warning(
                        f"Page range changed, starting fresh. "
                        f"Previous: {existing_state.page_range_start}-{existing_state.page_range_end}, "
                        f"New: {page_range[0]}-{page_range[1]}"
                    )

        return self.state_manager.create_state(pdf_path, total_pages, page_range)

    def _process_page(
        self,
        page_num: int,
        image_path: Path,
        state: PipelineState,
        english_texts: Dict[int, str],
        tamil_texts: Dict[int, str],
    ) -> float:
        """
        Process a single page through OCR and translation.

        Returns the cost for this page.
        """
        page_state = state.get_page_state(page_num)
        page_start = time.time()
        page_cost = 0.0

        # 1. OCR
        if not page_state.ocr_completed:
            ocr_result = self.ocr_engine.extract_with_adaptive_preprocessing(
                image_path, page_num
            )

            page_state.ocr_text = ocr_result.full_text
            page_state.ocr_confidence = ocr_result.confidence
            page_state.ocr_completed = True

            logger.debug(
                f"Page {page_num} OCR: {ocr_result.char_count} chars, "
                f"{ocr_result.confidence:.1%} confidence"
            )

        # 2. Translate to English
        if not page_state.english_completed and page_state.ocr_text:
            english_result = self.translator.translate_to_english(
                page_state.ocr_text,
                source_lang=self.config.get_lang_code("sanskrit"),
            )

            page_state.english_text = english_result.translated_text
            page_state.cost_english = english_result.cost_inr
            page_state.english_completed = True
            page_cost += english_result.cost_inr

            logger.debug(
                f"Page {page_num} English: {len(english_result.translated_text)} chars, "
                f"₹{english_result.cost_inr:.2f}"
            )

        # 3. Translate to Tamil (two-step)
        if not page_state.tamil_completed and page_state.ocr_text:
            tamil_result = self.translator.translate_to_tamil(
                page_state.ocr_text,
                source_lang=self.config.get_lang_code("sanskrit"),
                use_two_step=True,
            )

            page_state.tamil_text = tamil_result.translated_text
            page_state.cost_tamil = tamil_result.cost_inr
            page_state.tamil_completed = True
            page_cost += tamil_result.cost_inr

            logger.debug(
                f"Page {page_num} Tamil: {len(tamil_result.translated_text)} chars, "
                f"₹{tamil_result.cost_inr:.2f}"
            )

        # 4. Update state atomically
        page_state.processing_time = time.time() - page_start
        state.update_page(page_state)
        self.state_manager.save_state(state)

        # 5. Collect texts for PDF
        if page_state.english_text:
            english_texts[page_num] = page_state.english_text
        if page_state.tamil_text:
            tamil_texts[page_num] = page_state.tamil_text

        return page_cost

    def _estimate_cost(
        self,
        pdf_path: Path,
        page_range: Tuple[int, int],
        expected_pages: int,
    ) -> PipelineResult:
        """Estimate cost without processing."""
        # Rough estimate: 3000 chars per page
        estimated_chars = expected_pages * 3000

        # English + Tamil (two-step = 2x for Tamil)
        english_cost = self.config.calculate_cost(estimated_chars)
        tamil_cost = english_cost * 2  # Two-step translation
        total_cost = english_cost + tamil_cost

        logger.info(f"\n{'='*50}")
        logger.info("DRY RUN - Cost Estimate")
        logger.info(f"{'='*50}")
        logger.info(f"PDF: {pdf_path.name}")
        logger.info(f"Pages: {page_range[0]}-{page_range[1]} ({expected_pages} pages)")
        logger.info(f"Estimated characters: {estimated_chars:,}")
        logger.info(f"\nCost breakdown:")
        logger.info(f"  English translation: ₹{english_cost:.2f}")
        logger.info(f"  Tamil translation:   ₹{tamil_cost:.2f} (two-step)")
        logger.info(f"  Total:              ₹{total_cost:.2f}")
        logger.info(f"\nWith ₹{self.config.FREE_CREDITS_INR:.0f} free credits:")
        logger.info(f"  Net cost:           ₹{max(0, total_cost - self.config.FREE_CREDITS_INR):.2f}")
        logger.info(f"{'='*50}\n")

        return PipelineResult(
            success=True,
            pages_processed=0,
            pages_failed=0,
            total_cost_inr=total_cost,
            processing_time=0,
        )


def create_pipeline(
    config: Optional[Config] = None,
    on_page_complete: Optional[Callable[[int, float], None]] = None,
) -> TranslationPipeline:
    """
    Factory function to create a translation pipeline.

    Args:
        config: Optional configuration
        on_page_complete: Optional callback after each page

    Returns:
        Configured TranslationPipeline instance
    """
    return TranslationPipeline(
        config=config,
        on_page_complete=on_page_complete,
    )
