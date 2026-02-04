"""
Security validation layer for Tamil Translate.

Handles API key validation, PDF file validation, path traversal prevention,
and filename sanitization to protect against common security vulnerabilities.
"""

import os
import re
from pathlib import Path
from typing import List, Optional

from tamil_translate.config import get_config


class SecurityError(Exception):
    """Base exception for security-related errors."""

    pass


class InvalidAPIKeyError(SecurityError):
    """Raised when API key is invalid or missing."""

    pass


class InvalidPDFError(SecurityError):
    """Raised when PDF file validation fails."""

    pass


class PathTraversalError(SecurityError):
    """Raised when path traversal attack is detected."""

    pass


# =========================================================================
# API Key Validation
# =========================================================================

# Known placeholder/invalid API key patterns
FORBIDDEN_API_KEYS = frozenset(
    [
        "your_api_key_here",
        "your_key_here",
        "invalid_key",
        "test_key",
        "demo_key",
        "placeholder",
        "xxx",
        "api_key",
        "sarvam_api_key",
    ]
)

# Minimum valid API key length
MIN_API_KEY_LENGTH = 32


def load_api_key_securely() -> str:
    """
    Securely load and validate the Sarvam API key.

    Returns:
        Validated API key string

    Raises:
        InvalidAPIKeyError: If API key is missing, invalid, or a placeholder
    """
    api_key = os.getenv("SARVAM_API_KEY", "").strip()

    # Check if key is set
    if not api_key:
        raise InvalidAPIKeyError(
            "SARVAM_API_KEY not set.\n"
            "Set it with: export SARVAM_API_KEY='your-actual-key'\n"
            "Get your key from: https://dashboard.sarvam.ai"
        )

    # Check for placeholder keys
    if api_key.lower() in FORBIDDEN_API_KEYS:
        raise InvalidAPIKeyError(
            "Placeholder API key detected. "
            "Replace with your actual key from: https://dashboard.sarvam.ai"
        )

    # Check minimum length
    if len(api_key) < MIN_API_KEY_LENGTH:
        raise InvalidAPIKeyError(
            f"API key too short ({len(api_key)} chars, minimum {MIN_API_KEY_LENGTH}).\n"
            "Verify your key at: https://dashboard.sarvam.ai"
        )

    return api_key


# =========================================================================
# PDF Validation
# =========================================================================


class SecurePDFValidator:
    """
    Comprehensive PDF validation to prevent malicious uploads.

    Validates:
    - File existence and accessibility
    - File size limits (prevent PDF bombs)
    - MIME type (magic bytes, not just extension)
    - PDF header structure
    - Page count limits
    """

    def __init__(self, max_size_mb: Optional[int] = None, max_pages: Optional[int] = None):
        """
        Initialize the PDF validator.

        Args:
            max_size_mb: Maximum file size in MB (default from config)
            max_pages: Maximum page count (default from config)
        """
        config = get_config()
        self.max_size_bytes = (max_size_mb or config.MAX_PDF_SIZE_MB) * 1024 * 1024
        self.max_pages = max_pages or config.MAX_PDF_PAGES
        self.allowed_mime_types = frozenset(["application/pdf", "application/x-pdf"])

    def validate(self, pdf_path: str) -> Path:
        """
        Perform comprehensive PDF validation.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Resolved Path object if valid

        Raises:
            InvalidPDFError: If any validation check fails
        """
        # Check for symbolic links BEFORE resolving
        raw_path = Path(pdf_path)
        if raw_path.is_symlink():
            raise InvalidPDFError("Symbolic links are not allowed for security reasons")

        # Check if any parent is a symlink
        for parent in raw_path.parents:
            if parent.is_symlink():
                raise InvalidPDFError("Symbolic links in path are not allowed for security reasons")

        # Now resolve to absolute path
        path = raw_path.resolve()

        # 1. File existence
        if not path.exists():
            raise InvalidPDFError(f"PDF file not found: {path}")

        if not path.is_file():
            raise InvalidPDFError(f"Path is not a file: {path}")

        # 2. File size check (prevent PDF bombs)
        file_size = path.stat().st_size
        if file_size > self.max_size_bytes:
            max_mb = self.max_size_bytes / (1024 * 1024)
            actual_mb = file_size / (1024 * 1024)
            raise InvalidPDFError(
                f"PDF too large: {actual_mb:.1f}MB (maximum {max_mb:.0f}MB)"
            )

        if file_size == 0:
            raise InvalidPDFError("PDF file is empty (0 bytes)")

        # 4. PDF header validation (magic bytes)
        if not self._validate_pdf_header(path):
            raise InvalidPDFError(
                "Invalid PDF header. File does not start with %PDF- signature."
            )

        # 5. MIME type validation using python-magic
        if not self._validate_mime_type(path):
            raise InvalidPDFError(
                "Invalid file type. MIME type is not application/pdf."
            )

        # 6. Page count check (optional, requires PyPDF2)
        page_count = self._get_page_count(path)
        if page_count is not None and page_count > self.max_pages:
            raise InvalidPDFError(
                f"PDF has too many pages: {page_count} (maximum {self.max_pages})"
            )

        return path

    def _validate_pdf_header(self, path: Path) -> bool:
        """Check if file starts with PDF magic bytes."""
        try:
            with open(path, "rb") as f:
                header = f.read(5)
                return header == b"%PDF-"
        except OSError:
            return False

    def _validate_mime_type(self, path: Path) -> bool:
        """Validate MIME type using python-magic."""
        try:
            import magic

            mime = magic.from_file(str(path), mime=True)
            return mime in self.allowed_mime_types
        except ImportError:
            # python-magic not installed, skip this check
            return True
        except Exception:
            return False

    def _get_page_count(self, path: Path) -> Optional[int]:
        """Get PDF page count using PyPDF2."""
        try:
            from PyPDF2 import PdfReader

            with open(path, "rb") as f:
                reader = PdfReader(f)
                return len(reader.pages)
        except Exception:
            # Can't read PDF, but header was valid - allow to proceed
            return None


# =========================================================================
# Path Traversal Prevention
# =========================================================================


class SecureFileHandler:
    """
    Secure file path handling to prevent path traversal attacks.

    Ensures all file operations stay within allowed directories.
    """

    def __init__(self, allowed_input_dirs: Optional[List[Path]] = None):
        """
        Initialize the secure file handler.

        Args:
            allowed_input_dirs: List of allowed input directories
        """
        config = get_config()
        self.project_root = config.project_root
        self.allowed_input_dirs = allowed_input_dirs or [config.input_dir]
        self.allowed_output_dirs = [
            config.output_dir,
            config.english_output_dir,
            config.tamil_output_dir,
            config.intermediate_dir,
            config.state_dir,
        ]

    def validate_input_path(self, user_path: str) -> Path:
        """
        Validate that an input path is within allowed directories.

        Args:
            user_path: User-provided file path

        Returns:
            Resolved, validated Path object

        Raises:
            PathTraversalError: If path is outside allowed directories
        """
        # Check for symbolic links BEFORE resolving
        raw_path = Path(user_path)
        if raw_path.is_symlink():
            raise PathTraversalError("Symbolic links are not allowed for input files")

        # Check if any parent is a symlink
        for parent in raw_path.parents:
            if parent.is_symlink():
                raise PathTraversalError("Symbolic links in path are not allowed for input files")

        # Now resolve to absolute path
        path = raw_path.resolve()

        # Check if path is within allowed directories
        is_allowed = any(
            self._is_subpath(path, allowed_dir) for allowed_dir in self.allowed_input_dirs
        )

        if not is_allowed:
            allowed_str = ", ".join(str(d) for d in self.allowed_input_dirs)
            raise PathTraversalError(
                f"Input file must be in allowed directories: {allowed_str}\n"
                f"Provided path: {path}"
            )

        return path

    def validate_output_path(self, user_path: str) -> Path:
        """
        Validate that an output path is within allowed directories.

        Args:
            user_path: User-provided output path

        Returns:
            Resolved, validated Path object

        Raises:
            PathTraversalError: If path is outside allowed directories
        """
        path = Path(user_path).resolve()

        is_allowed = any(
            self._is_subpath(path, allowed_dir) for allowed_dir in self.allowed_output_dirs
        )

        if not is_allowed:
            allowed_str = ", ".join(str(d) for d in self.allowed_output_dirs)
            raise PathTraversalError(
                f"Output file must be in allowed directories: {allowed_str}\n"
                f"Provided path: {path}"
            )

        return path

    def _is_subpath(self, path: Path, parent: Path) -> bool:
        """Check if path is a subpath of parent directory."""
        try:
            path.relative_to(parent)
            return True
        except ValueError:
            return False


# =========================================================================
# Filename Sanitization
# =========================================================================


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize a filename to remove dangerous characters.

    Args:
        filename: Original filename
        max_length: Maximum filename length (default 255)

    Returns:
        Sanitized filename safe for filesystem use
    """
    # Remove path separators
    filename = filename.replace("/", "_").replace("\\", "_")

    # Remove or replace dangerous characters
    # Allow: alphanumeric, dots, underscores, hyphens
    filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)

    # Remove leading dots (hidden files)
    filename = filename.lstrip(".")

    # Collapse multiple underscores
    filename = re.sub(r"_+", "_", filename)

    # Ensure filename is not empty
    if not filename:
        filename = "unnamed"

    # Truncate to max length while preserving extension
    if len(filename) > max_length:
        # Find extension
        if "." in filename:
            name, ext = filename.rsplit(".", 1)
            # Handle empty extension (filename ending with dot)
            if not ext:
                # Strip trailing dots and truncate
                filename = name.rstrip(".")[:max_length]
            else:
                max_name_len = max_length - len(ext) - 1
                if max_name_len > 0:
                    filename = f"{name[:max_name_len]}.{ext}"
                else:
                    # Extension too long, truncate whole filename
                    filename = filename[:max_length]
        else:
            filename = filename[:max_length]

    return filename


def generate_output_filename(input_filename: str, language: str, suffix: str = "pdf") -> str:
    """
    Generate a safe output filename from input filename and language.

    Args:
        input_filename: Original input filename
        language: Target language (e.g., 'english', 'tamil')
        suffix: File extension (default 'pdf')

    Returns:
        Safe output filename like 'original_english.pdf'
    """
    # Remove extension from input
    base_name = Path(input_filename).stem

    # Sanitize the base name
    safe_name = sanitize_filename(base_name)

    # Construct output name
    output_name = f"{safe_name}_{language}.{suffix}"

    return sanitize_filename(output_name)


# =========================================================================
# Combined Security Validation
# =========================================================================


def validate_all(pdf_path: str, validate_api_key: bool = True) -> Path:
    """
    Perform all security validations for a PDF processing request.

    Args:
        pdf_path: Path to the PDF file to process
        validate_api_key: Whether to validate the API key (default True)

    Returns:
        Validated, resolved Path to the PDF

    Raises:
        SecurityError: If any validation fails
    """
    # 1. Validate API key (if requested)
    if validate_api_key:
        load_api_key_securely()

    # 2. Validate path is within allowed directories
    file_handler = SecureFileHandler()
    validated_path = file_handler.validate_input_path(pdf_path)

    # 3. Validate PDF structure
    pdf_validator = SecurePDFValidator()
    validated_path = pdf_validator.validate(str(validated_path))

    return validated_path
