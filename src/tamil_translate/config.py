"""
Configuration management for Tamil Translate.

Handles environment variables, API settings, language codes, and processing limits.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional


@dataclass
class Config:
    """
    Central configuration for the PDF translation pipeline.

    All settings can be overridden via environment variables.
    """

    # =========================================================================
    # API Configuration
    # =========================================================================
    SARVAM_API_KEY: str = field(default_factory=lambda: os.getenv("SARVAM_API_KEY", ""))
    API_ENDPOINT: str = "https://api.sarvam.ai/translate"
    MODEL: str = "sarvam-translate:v1"

    # =========================================================================
    # Language Codes (ISO 639-1 with region)
    # =========================================================================
    LANG_CODES: Dict[str, str] = field(
        default_factory=lambda: {
            "sanskrit": "sa-IN",
            "hindi": "hi-IN",
            "english": "en-IN",
            "tamil": "ta-IN",
        }
    )

    # =========================================================================
    # Processing Limits
    # =========================================================================
    # Maximum characters per API request (Sarvam limit is 2000)
    # Default 800 to prevent translation hallucination loops with large chunks
    MAX_CHUNK_SIZE: int = field(
        default_factory=lambda: int(os.getenv("MAX_CHUNK_SIZE", "800"))
    )

    # Minimum OCR confidence threshold (pages below this get adaptive preprocessing)
    OCR_CONFIDENCE_THRESHOLD: float = field(
        default_factory=lambda: float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.80"))
    )

    # =========================================================================
    # OCR Settings
    # =========================================================================
    # DPI for PDF page rendering (higher = better quality but slower)
    OCR_DPI: int = field(
        default_factory=lambda: int(os.getenv("OCR_DPI", "400"))
    )

    # Enable preprocessing pipeline before OCR (grayscale → denoise → binarize)
    OCR_PREPROCESS_ENABLED: bool = field(
        default_factory=lambda: os.getenv("OCR_PREPROCESS_ENABLED", "true").lower() == "true"
    )

    # Number of concurrent translation workers
    MAX_WORKERS: int = field(default_factory=lambda: int(os.getenv("MAX_WORKERS", "5")))

    # Maximum retry attempts for API calls
    MAX_RETRIES: int = 3

    # Default page limit for test runs (safety first)
    DEFAULT_TEST_PAGES: int = 10

    # =========================================================================
    # File Size Limits
    # =========================================================================
    MAX_PDF_SIZE_MB: int = 100
    MAX_PDF_PAGES: int = 1000

    # =========================================================================
    # Pricing (INR)
    # =========================================================================
    # Cost per 10,000 characters translated
    COST_PER_10K_CHARS: float = 20.0

    # Free credits for new accounts
    FREE_CREDITS_INR: float = 1000.0

    # =========================================================================
    # Translation Settings
    # =========================================================================
    # Speaker gender for translation (affects tone/style)
    SPEAKER_GENDER: str = "Male"

    # Translation mode (only 'formal' available for sarvam-translate:v1)
    TRANSLATION_MODE: str = "formal"

    # Numerals format: 'native' for Devanagari numerals, 'international' for 0-9
    # Use 'native' for traditional religious texts
    NUMERALS_FORMAT: str = "native"

    # =========================================================================
    # Directory Paths
    # =========================================================================
    @property
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent

    @property
    def input_dir(self) -> Path:
        """Directory containing input PDFs."""
        return self.project_root / "Pdfs"

    @property
    def output_dir(self) -> Path:
        """Base output directory."""
        return self.project_root / "output"

    @property
    def english_output_dir(self) -> Path:
        """Directory for English translated PDFs."""
        return self.output_dir / "english"

    @property
    def tamil_output_dir(self) -> Path:
        """Directory for Tamil translated PDFs."""
        return self.output_dir / "tamil"

    @property
    def intermediate_dir(self) -> Path:
        """Directory for intermediate files (English text for two-step Tamil)."""
        return self.output_dir / "intermediate"

    @property
    def state_dir(self) -> Path:
        """Directory for state/progress files."""
        return self.output_dir / ".state"

    @property
    def fonts_dir(self) -> Path:
        """Directory containing font files."""
        return self.project_root / "fonts"

    @property
    def logs_dir(self) -> Path:
        """Directory for log files."""
        return self.project_root / "logs"

    # =========================================================================
    # Utility Methods
    # =========================================================================
    def ensure_directories(self) -> None:
        """Create all required output directories if they don't exist."""
        for dir_path in [
            self.output_dir,
            self.english_output_dir,
            self.tamil_output_dir,
            self.intermediate_dir,
            self.state_dir,
            self.fonts_dir,
            self.logs_dir,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def get_lang_code(self, language: str) -> str:
        """
        Get the ISO language code for a language name.

        Args:
            language: Language name (e.g., 'sanskrit', 'tamil')

        Returns:
            ISO language code (e.g., 'sa-IN', 'ta-IN')

        Raises:
            ValueError: If language is not supported
        """
        lang_lower = language.lower()
        if lang_lower not in self.LANG_CODES:
            supported = ", ".join(self.LANG_CODES.keys())
            raise ValueError(f"Unsupported language: {language}. Supported: {supported}")
        return self.LANG_CODES[lang_lower]

    def calculate_cost(self, char_count: int) -> float:
        """
        Calculate translation cost in INR.

        Args:
            char_count: Number of characters to translate

        Returns:
            Cost in INR (rounded to 2 decimal places)
        """
        cost = (char_count / 10000) * self.COST_PER_10K_CHARS
        return round(cost, 2)

    def estimate_document_cost(self, page_count: int, chars_per_page: int = 3000) -> Dict:
        """
        Estimate cost for translating a document.

        Args:
            page_count: Number of pages
            chars_per_page: Estimated characters per page (default 3000)

        Returns:
            Dictionary with cost breakdown
        """
        total_chars = page_count * chars_per_page

        # Cost for each language (Sanskrit → English, English → Tamil)
        english_cost = self.calculate_cost(total_chars)
        tamil_cost = self.calculate_cost(total_chars)  # Two-step uses English as source
        total_cost = english_cost + tamil_cost

        # Apply free credits
        cost_after_credits = max(0, total_cost - self.FREE_CREDITS_INR)

        return {
            "page_count": page_count,
            "total_characters": total_chars * 2,  # Both languages
            "english_cost_inr": english_cost,
            "tamil_cost_inr": tamil_cost,
            "total_cost_inr": total_cost,
            "free_credits_inr": self.FREE_CREDITS_INR,
            "cost_after_credits_inr": cost_after_credits,
            "estimated_usd": round(cost_after_credits / 83, 2),  # Approx INR to USD
        }

    def validate(self) -> bool:
        """
        Validate critical configuration settings.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.SARVAM_API_KEY:
            raise ValueError(
                "SARVAM_API_KEY not set. "
                "Export in shell: export SARVAM_API_KEY='your-actual-key'\n"
                "Get key from: https://dashboard.sarvam.ai"
            )

        if not 100 <= self.MAX_CHUNK_SIZE <= 2000:
            raise ValueError(
                f"MAX_CHUNK_SIZE ({self.MAX_CHUNK_SIZE}) must be between 100 and 2000"
            )

        if not 0.0 <= self.OCR_CONFIDENCE_THRESHOLD <= 1.0:
            raise ValueError(
                f"OCR_CONFIDENCE_THRESHOLD ({self.OCR_CONFIDENCE_THRESHOLD}) "
                "must be between 0.0 and 1.0"
            )

        if not 150 <= self.OCR_DPI <= 600:
            raise ValueError(
                f"OCR_DPI ({self.OCR_DPI}) must be between 150 and 600"
            )

        return True


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance.

    Returns:
        Config instance (created on first call)
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


def reset_config() -> None:
    """Reset the global configuration (useful for testing)."""
    global _config
    _config = None
