"""
Command-line interface for Tamil Translate.

Provides a user-friendly CLI for running the translation pipeline
with progress tracking, cost estimation, and resume capability.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional, Tuple

from tamil_translate import __version__
from tamil_translate.config import get_config
from tamil_translate.pdf_generator import check_fonts_available, get_font_download_instructions
from tamil_translate.pipeline import TranslationPipeline, create_pipeline
from tamil_translate.state_manager import StateManager


def setup_logging(verbose: bool = False, log_file: Optional[Path] = None) -> None:
    """
    Configure logging for the CLI.

    Args:
        verbose: Enable verbose (DEBUG) logging to console
        log_file: Optional path to log file
    """
    # Console handler
    console_level = logging.DEBUG if verbose else logging.INFO
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_format = logging.Formatter(
        "%(message)s" if not verbose else "%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    console_handler.setFormatter(console_format)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)

    # File handler (always DEBUG level)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s"
        )
        file_handler.setFormatter(file_format)
        root_logger.addHandler(file_handler)

    # Quiet noisy loggers
    logging.getLogger("paddleocr").setLevel(logging.WARNING)
    logging.getLogger("ppocr").setLevel(logging.WARNING)


def parse_page_range(page_str: str, max_pages: int) -> Tuple[int, int]:
    """
    Parse page range string.

    Args:
        page_str: Page range like "1-10", "all", or "5"
        max_pages: Maximum page number

    Returns:
        Tuple of (start_page, end_page)
    """
    page_str = page_str.strip().lower()

    if page_str == "all":
        return (1, max_pages)

    if "-" in page_str:
        parts = page_str.split("-")
        start = int(parts[0])
        end = int(parts[1])
        return (max(1, start), min(max_pages, end))

    # Single page number - treat as range to that page
    page_num = int(page_str)
    return (1, min(max_pages, page_num))


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="tamil-translate",
        description="Translate Sanskrit/Hindi PDFs to English and Tamil",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test run (default 10 pages)
  tamil-translate Pdfs/input.pdf

  # Specific page range
  tamil-translate Pdfs/input.pdf --pages 1-50

  # Full document
  tamil-translate Pdfs/input.pdf --pages all

  # With more workers
  tamil-translate Pdfs/input.pdf --workers 10 --pages 1-100

  # Dry run (cost estimation only)
  tamil-translate Pdfs/input.pdf --dry-run --pages all

  # Resume previous run
  tamil-translate Pdfs/input.pdf --resume

  # Start fresh (ignore previous progress)
  tamil-translate Pdfs/input.pdf --no-resume

  # Higher DPI for better OCR quality
  tamil-translate Pdfs/input.pdf --dpi 400

  # Smaller chunks to prevent translation loops
  tamil-translate Pdfs/input.pdf --chunk-size 500

  # Disable preprocessing (use original images)
  tamil-translate Pdfs/input.pdf --no-preprocess

Environment Variables:
  SARVAM_API_KEY    Your Sarvam AI API key (required)
  MAX_WORKERS       Number of concurrent workers (default: 5)
  MAX_CHUNK_SIZE    Max characters per API request (default: 800)
  OCR_DPI           DPI for PDF rendering (default: 400)
        """,
    )

    parser.add_argument(
        "input",
        type=str,
        nargs="?",
        help="Path to input PDF file (or omit for batch mode)",
    )

    parser.add_argument(
        "--pages",
        type=str,
        default="1-10",
        help='Page range (e.g., "1-50", "all", or "25"). Default: "1-10"',
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory (default: output/)",
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of concurrent translation workers (default: 5)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Estimate cost without processing",
    )

    parser.add_argument(
        "--resume",
        action="store_true",
        default=True,
        help="Resume from previous run if state exists (default)",
    )

    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Start fresh, ignore previous progress",
    )

    parser.add_argument(
        "--check-fonts",
        action="store_true",
        help="Check if required fonts are installed",
    )

    parser.add_argument(
        "--ocr",
        type=str,
        choices=["tesseract", "paddle", "auto"],
        default="auto",
        help="OCR backend: tesseract (best for Sanskrit), paddle, or auto (default: auto)",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=None,
        metavar="N",
        help="Max characters per translation chunk (100-2000). Smaller values prevent "
             "translation loops but increase API calls (default: 800)",
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=None,
        metavar="N",
        help="DPI for PDF page rendering (150-600). Higher values improve OCR quality "
             "but use more memory (default: 400)",
    )

    parser.add_argument(
        "--no-preprocess",
        action="store_true",
        help="Disable image preprocessing before OCR (use original images)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser


def cmd_check_fonts() -> int:
    """Check and report font availability."""
    print("\nChecking required fonts...\n")

    fonts_status = check_fonts_available()
    all_available = True

    for lang, available in fonts_status.items():
        status = "✓" if available else "✗"
        print(f"  {status} {lang.capitalize()}")
        if not available:
            all_available = False

    if all_available:
        print("\nAll fonts are available. PDF generation ready.")
        return 0
    else:
        print(get_font_download_instructions())
        return 1


def cmd_translate(args: argparse.Namespace) -> int:
    """Run the translation pipeline."""
    config = get_config()

    # Update config from args
    if args.workers:
        config.MAX_WORKERS = args.workers

    if args.chunk_size is not None:
        if not 100 <= args.chunk_size <= 2000:
            print(f"Error: --chunk-size must be between 100 and 2000 (got {args.chunk_size})")
            return 1
        config.MAX_CHUNK_SIZE = args.chunk_size

    if args.dpi is not None:
        if not 150 <= args.dpi <= 600:
            print(f"Error: --dpi must be between 150 and 600 (got {args.dpi})")
            return 1
        config.OCR_DPI = args.dpi

    if args.no_preprocess:
        config.OCR_PREPROCESS_ENABLED = False

    # Set up logging
    log_file = config.logs_dir / "tamil_translate.log" if args.verbose else None
    setup_logging(verbose=args.verbose, log_file=log_file)

    logger = logging.getLogger(__name__)

    # Validate input
    if not args.input:
        logger.error("No input PDF specified. Use --help for usage.")
        return 1

    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return 1

    # Ensure directories exist
    config.ensure_directories()

    # Check fonts before processing
    fonts_status = check_fonts_available()
    if not all(fonts_status.values()):
        missing = [lang for lang, avail in fonts_status.items() if not avail]
        logger.warning(f"Missing fonts for: {', '.join(missing)}")
        logger.warning("PDF generation may fail. Run with --check-fonts for details.")

    # Parse page range (need page count first)
    from tamil_translate.ocr_engine import get_pdf_page_count

    try:
        total_pages = get_pdf_page_count(input_path)
    except Exception as e:
        logger.error(f"Failed to read PDF: {e}")
        return 1

    try:
        page_range = parse_page_range(args.pages, total_pages)
    except ValueError as e:
        logger.error(f"Invalid page range '{args.pages}': {e}")
        return 1

    # Resume handling
    resume = args.resume and not args.no_resume

    # Check for resumable state
    if resume:
        state_manager = StateManager()
        resume_info = state_manager.get_resume_info(input_path)
        if resume_info:
            print(f"\n{'='*50}")
            print("Previous run detected:")
            print(f"  Completed: {resume_info['pages_completed']} pages")
            print(f"  Remaining: {resume_info['pages_pending']} pages")
            print(f"  Cost so far: ₹{resume_info['cost_so_far']:.2f}")
            print(f"  Last updated: {resume_info['last_updated']}")
            print(f"{'='*50}\n")

    # Print run summary
    expected_pages = page_range[1] - page_range[0] + 1
    print(f"\n{'='*50}")
    print("Tamil Translate")
    print(f"{'='*50}")
    print(f"Input:  {input_path.name}")
    print(f"Pages:  {page_range[0]}-{page_range[1]} ({expected_pages} pages)")
    print(f"OCR:    {args.ocr} (DPI: {config.OCR_DPI})")
    print(f"Preprocess: {'Yes' if config.OCR_PREPROCESS_ENABLED else 'No'}")
    print(f"Chunk size: {config.MAX_CHUNK_SIZE} chars")
    print(f"Mode:   {'Dry run' if args.dry_run else 'Full processing'}")
    print(f"Resume: {'Yes' if resume else 'No'}")
    print(f"{'='*50}\n")

    # Create and run pipeline
    def on_page_complete(page_num: int, cost: float) -> None:
        """Callback for page completion."""
        if args.verbose:
            logger.info(f"Page {page_num} completed (₹{cost:.2f})")

    pipeline = create_pipeline(
        config=config,
        on_page_complete=on_page_complete,
        ocr_backend=args.ocr,
    )

    result = pipeline.run(
        pdf_path=str(input_path),
        page_range=page_range,
        output_dir=Path(args.output) if args.output else None,
        resume=resume,
        dry_run=args.dry_run,
    )

    # Print result summary
    print(f"\n{'='*50}")
    if result.success:
        print("Translation Complete!")
    else:
        print("Translation Failed")
    print(f"{'='*50}")

    print(f"Pages processed: {result.pages_processed}")
    if result.pages_failed:
        print(f"Pages failed:    {result.pages_failed}")
    print(f"Total cost:      ₹{result.total_cost_inr:.2f}")
    print(f"Processing time: {result.processing_time:.1f}s")

    if result.english_pdf_path:
        print(f"\nEnglish PDF: {result.english_pdf_path}")
    if result.tamil_pdf_path:
        print(f"Tamil PDF:   {result.tamil_pdf_path}")

    if result.error:
        print(f"\nError: {result.error}")

    print(f"{'='*50}\n")

    return 0 if result.success else 1


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Handle subcommands
    if args.check_fonts:
        return cmd_check_fonts()

    return cmd_translate(args)


if __name__ == "__main__":
    sys.exit(main())
