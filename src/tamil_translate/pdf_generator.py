"""
PDF generation module using fpdf2.

Creates searchable PDFs with embedded Unicode fonts for
English, Tamil, and Devanagari text.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from tamil_translate.config import get_config

logger = logging.getLogger(__name__)


class PDFGenerationError(Exception):
    """Base exception for PDF generation errors."""

    pass


class FontNotFoundError(PDFGenerationError):
    """Raised when required font file is not found."""

    pass


@dataclass
class PDFMetadata:
    """Metadata for generated PDF."""

    title: str
    author: str = "Tamil Translate"
    subject: str = "Translation"
    keywords: str = "sanskrit, tamil, translation, religious texts"
    creator: str = "Tamil Translate Pipeline"
    source_pdf: Optional[str] = None
    source_language: Optional[str] = None
    target_language: Optional[str] = None


class PDFGenerator:
    """
    PDF generator using fpdf2 with Unicode font support.

    Features:
    - Embedded Unicode fonts (Noto Sans family)
    - Support for English, Tamil, and Devanagari scripts
    - Searchable text layer
    - Automatic text wrapping and pagination
    - Metadata preservation
    """

    # Font configurations for different scripts
    FONT_CONFIG = {
        "english": {
            "name": "NotoSans",
            "file": "NotoSans-Regular.ttf",
            "fallback": None,
        },
        "tamil": {
            "name": "NotoSansTamil",
            "file": "NotoSansTamil-Regular.ttf",
            "fallback": "NotoSans-Regular.ttf",
        },
        "devanagari": {
            "name": "NotoSansDevanagari",
            "file": "NotoSansDevanagari-Regular.ttf",
            "fallback": "NotoSans-Regular.ttf",
        },
    }

    def __init__(
        self,
        language: str,
        fonts_dir: Optional[Path] = None,
        page_size: str = "A4",
        margin: float = 20,
        font_size: int = 12,
        line_height: float = 1.5,
    ):
        """
        Initialize the PDF generator.

        Args:
            language: Target language ('english', 'tamil', 'devanagari')
            fonts_dir: Directory containing font files
            page_size: Page size (default 'A4')
            margin: Page margin in mm (default 20)
            font_size: Base font size in points (default 12)
            line_height: Line height multiplier (default 1.5)
        """
        config = get_config()
        self.language = language.lower()
        self.fonts_dir = fonts_dir or config.fonts_dir
        self.page_size = page_size
        self.margin = margin
        self.font_size = font_size
        self.line_height = line_height

        # Lazy initialization
        self._pdf = None
        self._font_loaded = False
        self._pages_added = 0

    def _lazy_init(self) -> None:
        """Lazily initialize the PDF document."""
        if self._pdf is not None:
            return

        try:
            from fpdf import FPDF
        except ImportError as e:
            raise ImportError(
                "fpdf2 not installed. Install with: pip install fpdf2"
            ) from e

        # Create PDF with Unicode support
        self._pdf = FPDF()
        self._pdf.set_auto_page_break(auto=True, margin=self.margin)

        # Load appropriate font
        self._load_font()

    def _load_font(self) -> None:
        """Load the appropriate font for the language."""
        if self._font_loaded:
            return

        font_config = self.FONT_CONFIG.get(self.language)
        if font_config is None:
            # Default to English/Latin fonts
            font_config = self.FONT_CONFIG["english"]
            logger.warning(f"Unknown language '{self.language}', using English fonts")

        font_path = self.fonts_dir / font_config["file"]

        if not font_path.exists():
            # Try to provide helpful error with download instructions
            raise FontNotFoundError(
                f"Font file not found: {font_path}\n"
                f"Download Noto Sans fonts from: https://fonts.google.com/noto\n"
                f"Required: {font_config['file']}\n"
                f"Place in: {self.fonts_dir}"
            )

        try:
            # Add font with Unicode support
            self._pdf.add_font(
                font_config["name"],
                "",
                str(font_path),
                uni=True,
            )
            self._pdf.set_font(font_config["name"], size=self.font_size)
            self._font_loaded = True
            logger.info(f"Loaded font: {font_config['name']} from {font_path}")
        except Exception as e:
            raise PDFGenerationError(f"Failed to load font: {e}") from e

    def set_metadata(self, metadata: PDFMetadata) -> None:
        """
        Set PDF metadata.

        Args:
            metadata: PDFMetadata instance with document info
        """
        self._lazy_init()

        self._pdf.set_title(metadata.title)
        self._pdf.set_author(metadata.author)
        self._pdf.set_subject(metadata.subject)
        self._pdf.set_keywords(metadata.keywords)
        self._pdf.set_creator(metadata.creator)

    def add_page_content(
        self,
        text: str,
        page_num: int,
        add_page_number: bool = True,
    ) -> None:
        """
        Add translated text as a new page.

        Args:
            text: Translated text content
            page_num: Original page number (for reference)
            add_page_number: Whether to add page number footer
        """
        self._lazy_init()

        # Add new page
        self._pdf.add_page()
        self._pages_added += 1

        # Set margins
        self._pdf.set_margins(self.margin, self.margin, self.margin)
        self._pdf.set_xy(self.margin, self.margin)

        # Calculate effective width
        effective_width = self._pdf.w - 2 * self.margin

        # Add text with automatic wrapping
        self._pdf.multi_cell(
            w=effective_width,
            h=self.font_size * self.line_height / 2.8,  # Convert to mm
            txt=text,
            align="L",
        )

        # Add page number footer if requested
        if add_page_number:
            self._add_page_footer(page_num)

    def _add_page_footer(self, original_page_num: int) -> None:
        """Add footer with page number."""
        # Save current position
        current_y = self._pdf.get_y()

        # Go to footer position
        self._pdf.set_y(-15)
        self._pdf.set_font_size(8)

        # Add centered page number
        self._pdf.cell(
            w=0,
            h=10,
            txt=f"Page {original_page_num} | Generated by Tamil Translate",
            align="C",
        )

        # Restore font size
        self._pdf.set_font_size(self.font_size)

    def add_title_page(
        self,
        title: str,
        subtitle: Optional[str] = None,
        source_info: Optional[str] = None,
    ) -> None:
        """
        Add a title page to the PDF.

        Args:
            title: Main title
            subtitle: Optional subtitle
            source_info: Optional source document information
        """
        self._lazy_init()

        self._pdf.add_page()
        self._pages_added += 1

        # Center content vertically
        self._pdf.set_y(80)

        # Title
        self._pdf.set_font_size(24)
        self._pdf.multi_cell(w=0, h=12, txt=title, align="C")

        # Subtitle
        if subtitle:
            self._pdf.ln(10)
            self._pdf.set_font_size(16)
            self._pdf.multi_cell(w=0, h=10, txt=subtitle, align="C")

        # Source info
        if source_info:
            self._pdf.ln(20)
            self._pdf.set_font_size(12)
            self._pdf.multi_cell(w=0, h=8, txt=source_info, align="C")

        # Reset font size
        self._pdf.set_font_size(self.font_size)

    def save(self, output_path: Path) -> None:
        """
        Save the PDF to file.

        Args:
            output_path: Path to save the PDF
        """
        self._lazy_init()

        if self._pages_added == 0:
            raise PDFGenerationError("Cannot save empty PDF (no pages added)")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            self._pdf.output(str(output_path))
            logger.info(f"Saved PDF: {output_path} ({self._pages_added} pages)")
        except Exception as e:
            raise PDFGenerationError(f"Failed to save PDF: {e}") from e

    def get_page_count(self) -> int:
        """Get the number of pages added."""
        return self._pages_added


class TranslationPDFBuilder:
    """
    High-level builder for creating translation PDFs.

    Simplifies the process of building complete translated PDFs
    from page data.
    """

    def __init__(
        self,
        language: str,
        output_dir: Optional[Path] = None,
        fonts_dir: Optional[Path] = None,
    ):
        """
        Initialize the PDF builder.

        Args:
            language: Target language ('english' or 'tamil')
            output_dir: Output directory (default from config)
            fonts_dir: Fonts directory (default from config)
        """
        config = get_config()
        self.language = language.lower()
        self.fonts_dir = fonts_dir or config.fonts_dir

        # Set output directory based on language
        if output_dir:
            self.output_dir = output_dir
        elif self.language == "english":
            self.output_dir = config.english_output_dir
        elif self.language == "tamil":
            self.output_dir = config.tamil_output_dir
        else:
            self.output_dir = config.output_dir

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_from_pages(
        self,
        pages: Dict[int, str],
        source_filename: str,
        source_language: str = "sanskrit",
        include_title_page: bool = True,
    ) -> Path:
        """
        Build a complete PDF from translated pages.

        Args:
            pages: Dictionary mapping page numbers to translated text
            source_filename: Original PDF filename
            source_language: Source language name
            include_title_page: Whether to add a title page

        Returns:
            Path to the generated PDF
        """
        # Create generator
        generator = PDFGenerator(
            language=self.language,
            fonts_dir=self.fonts_dir,
        )

        # Set metadata
        title = f"{Path(source_filename).stem} ({self.language.capitalize()} Translation)"
        metadata = PDFMetadata(
            title=title,
            subject=f"Translation from {source_language} to {self.language}",
            source_pdf=source_filename,
            source_language=source_language,
            target_language=self.language,
        )
        generator.set_metadata(metadata)

        # Add title page
        if include_title_page:
            generator.add_title_page(
                title=Path(source_filename).stem,
                subtitle=f"{self.language.capitalize()} Translation",
                source_info=f"Translated from {source_language.capitalize()}",
            )

        # Add content pages in order
        for page_num in sorted(pages.keys()):
            text = pages[page_num]
            if text and text.strip():
                generator.add_page_content(text, page_num)

        # Generate output filename
        output_filename = f"{Path(source_filename).stem}_{self.language}.pdf"
        output_path = self.output_dir / output_filename

        # Save PDF
        generator.save(output_path)

        return output_path


def check_fonts_available(fonts_dir: Optional[Path] = None) -> Dict[str, bool]:
    """
    Check if required fonts are available.

    Args:
        fonts_dir: Directory to check (default from config)

    Returns:
        Dictionary mapping font names to availability status
    """
    config = get_config()
    fonts_dir = fonts_dir or config.fonts_dir

    results = {}
    for lang, font_config in PDFGenerator.FONT_CONFIG.items():
        font_path = fonts_dir / font_config["file"]
        results[lang] = font_path.exists()

    return results


def get_font_download_instructions() -> str:
    """
    Get instructions for downloading required fonts.

    Returns:
        Instruction string
    """
    config = get_config()

    return f"""
Required fonts for PDF generation:

1. Noto Sans (for English/Latin text)
   - File: NotoSans-Regular.ttf
   - Download: https://fonts.google.com/noto/specimen/Noto+Sans

2. Noto Sans Tamil (for Tamil text)
   - File: NotoSansTamil-Regular.ttf
   - Download: https://fonts.google.com/noto/specimen/Noto+Sans+Tamil

3. Noto Sans Devanagari (for Sanskrit/Hindi text)
   - File: NotoSansDevanagari-Regular.ttf
   - Download: https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari

Place all font files in: {config.fonts_dir}

Alternative: Download full Noto Sans package:
https://github.com/googlefonts/noto-fonts/releases
"""
