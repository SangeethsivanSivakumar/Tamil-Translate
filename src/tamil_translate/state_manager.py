"""
State management for translation pipeline.

Handles progress persistence, resume capability, and crash recovery
using atomic file writes and checksum-based validation.
"""

import hashlib
import json
import logging
import os
import shutil
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from tamil_translate.config import get_config

logger = logging.getLogger(__name__)


class StateError(Exception):
    """Base exception for state management errors."""

    pass


class StateCorruptedError(StateError):
    """Raised when state file is corrupted."""

    pass


@dataclass
class PageState:
    """State for a single page."""

    page_num: int
    ocr_completed: bool = False
    english_completed: bool = False
    tamil_completed: bool = False
    ocr_text: Optional[str] = None
    english_text: Optional[str] = None
    tamil_text: Optional[str] = None
    ocr_confidence: float = 0.0
    cost_english: float = 0.0
    cost_tamil: float = 0.0
    processing_time: float = 0.0
    error: Optional[str] = None

    @property
    def is_fully_completed(self) -> bool:
        """Check if all processing is done for this page."""
        return self.ocr_completed and self.english_completed and self.tamil_completed

    @property
    def total_cost(self) -> float:
        """Total cost for this page."""
        return self.cost_english + self.cost_tamil


@dataclass
class PipelineState:
    """Complete state for a translation pipeline run."""

    pdf_path: str
    pdf_checksum: str
    total_pages: int
    page_range_start: int
    page_range_end: int
    pages: Dict[int, PageState] = field(default_factory=dict)
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    version: str = "1.0"

    @property
    def completed_pages(self) -> Set[int]:
        """Set of fully completed page numbers."""
        return {num for num, state in self.pages.items() if state.is_fully_completed}

    @property
    def pages_completed_count(self) -> int:
        """Count of fully completed pages."""
        return len(self.completed_pages)

    @property
    def total_cost(self) -> float:
        """Total cost across all pages."""
        return sum(state.total_cost for state in self.pages.values())

    @property
    def english_cost(self) -> float:
        """Total English translation cost."""
        return sum(state.cost_english for state in self.pages.values())

    @property
    def tamil_cost(self) -> float:
        """Total Tamil translation cost."""
        return sum(state.cost_tamil for state in self.pages.values())

    @property
    def progress_percentage(self) -> float:
        """Progress as percentage."""
        expected_pages = self.page_range_end - self.page_range_start + 1
        return (self.pages_completed_count / expected_pages * 100) if expected_pages > 0 else 0

    def get_pending_pages(self) -> List[int]:
        """Get list of pages that still need processing."""
        expected = set(range(self.page_range_start, self.page_range_end + 1))
        return sorted(expected - self.completed_pages)

    def get_page_state(self, page_num: int) -> PageState:
        """Get or create page state."""
        if page_num not in self.pages:
            self.pages[page_num] = PageState(page_num=page_num)
        return self.pages[page_num]

    def update_page(self, page_state: PageState) -> None:
        """Update state for a page."""
        self.pages[page_state.page_num] = page_state
        self.last_updated = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "pdf_path": self.pdf_path,
            "pdf_checksum": self.pdf_checksum,
            "total_pages": self.total_pages,
            "page_range_start": self.page_range_start,
            "page_range_end": self.page_range_end,
            "pages": {str(k): asdict(v) for k, v in self.pages.items()},
            "started_at": self.started_at,
            "last_updated": self.last_updated,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PipelineState":
        """Create from dictionary."""
        pages = {}
        for page_num_str, page_data in data.get("pages", {}).items():
            page_num = int(page_num_str)
            pages[page_num] = PageState(**page_data)

        return cls(
            pdf_path=data["pdf_path"],
            pdf_checksum=data["pdf_checksum"],
            total_pages=data["total_pages"],
            page_range_start=data["page_range_start"],
            page_range_end=data["page_range_end"],
            pages=pages,
            started_at=data.get("started_at", datetime.utcnow().isoformat()),
            last_updated=data.get("last_updated", datetime.utcnow().isoformat()),
            version=data.get("version", "1.0"),
        )


class StateManager:
    """
    Manages pipeline state with atomic writes and crash recovery.

    Features:
    - Checksum-based PDF verification
    - Atomic state file writes (temp + rename)
    - Automatic backup recovery
    - Resume capability detection
    """

    def __init__(self, state_dir: Optional[Path] = None):
        """
        Initialize the state manager.

        Args:
            state_dir: Directory for state files (default from config)
        """
        config = get_config()
        self.state_dir = state_dir or config.state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def _get_state_path(self, pdf_path: Path) -> Path:
        """Get the state file path for a PDF."""
        # Use PDF filename as base for state file
        state_filename = f"{pdf_path.stem}.state.json"
        return self.state_dir / state_filename

    def _calculate_checksum(self, pdf_path: Path) -> str:
        """Calculate SHA-256 checksum of a PDF file."""
        sha256 = hashlib.sha256()
        with open(pdf_path, "rb") as f:
            # Read in chunks for large files
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def create_state(
        self,
        pdf_path: Path,
        total_pages: int,
        page_range: tuple,
    ) -> PipelineState:
        """
        Create a new pipeline state.

        Args:
            pdf_path: Path to the PDF file
            total_pages: Total number of pages in PDF
            page_range: Tuple of (start_page, end_page)

        Returns:
            New PipelineState instance
        """
        checksum = self._calculate_checksum(pdf_path)

        state = PipelineState(
            pdf_path=str(pdf_path),
            pdf_checksum=checksum,
            total_pages=total_pages,
            page_range_start=page_range[0],
            page_range_end=page_range[1],
        )

        # Save initial state
        self.save_state(state)

        logger.info(
            f"Created new state for {pdf_path.name} "
            f"(pages {page_range[0]}-{page_range[1]}, checksum: {checksum[:8]}...)"
        )

        return state

    def load_state(self, pdf_path: Path) -> Optional[PipelineState]:
        """
        Load existing state for a PDF.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            PipelineState if exists and valid, None otherwise
        """
        state_path = self._get_state_path(pdf_path)

        if not state_path.exists():
            return None

        try:
            with open(state_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            state = PipelineState.from_dict(data)

            # Verify checksum matches
            current_checksum = self._calculate_checksum(pdf_path)
            if state.pdf_checksum != current_checksum:
                logger.warning(
                    f"PDF checksum mismatch - file may have been modified. "
                    f"Expected: {state.pdf_checksum[:8]}..., "
                    f"Got: {current_checksum[:8]}..."
                )
                return None

            logger.info(
                f"Loaded existing state: {state.pages_completed_count} pages completed, "
                f"₹{state.total_cost:.2f} spent"
            )

            return state

        except json.JSONDecodeError as e:
            logger.warning(f"State file corrupted: {e}")
            return self._try_recover_from_backup(state_path)

        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return None

    def save_state(self, state: PipelineState) -> None:
        """
        Save state with atomic write pattern.

        Uses temp file + rename to prevent corruption from crashes.

        Args:
            state: PipelineState to save
        """
        state_path = self._get_state_path(Path(state.pdf_path))
        temp_path = state_path.with_suffix(".tmp")
        backup_path = state_path.with_suffix(".backup")

        # Update timestamp
        state.last_updated = datetime.utcnow().isoformat()

        try:
            # 1. Backup existing state
            if state_path.exists():
                shutil.copy2(state_path, backup_path)

            # 2. Write to temp file
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(state.to_dict(), f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())  # Force disk write

            # 3. Atomic rename
            os.replace(temp_path, state_path)

            logger.debug(f"State saved: {state.pages_completed_count} pages completed")

        except Exception as e:
            # 4. Restore from backup on failure
            if backup_path.exists():
                try:
                    os.replace(backup_path, state_path)
                    logger.warning("State save failed, restored from backup")
                except Exception:
                    pass
            raise StateError(f"Failed to save state: {e}") from e

        finally:
            # Clean up temp file if it exists
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass

    def _try_recover_from_backup(self, state_path: Path) -> Optional[PipelineState]:
        """
        Attempt to recover state from backup file.

        Args:
            state_path: Path to the corrupted state file

        Returns:
            Recovered PipelineState or None
        """
        backup_path = state_path.with_suffix(".backup")

        if not backup_path.exists():
            logger.warning("No backup file available for recovery")
            return None

        try:
            logger.info("Attempting recovery from backup file...")

            with open(backup_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            state = PipelineState.from_dict(data)

            # Restore the backup
            shutil.copy2(backup_path, state_path)

            logger.info(
                f"Recovered state from backup: {state.pages_completed_count} pages completed"
            )

            return state

        except Exception as e:
            logger.error(f"Backup recovery failed: {e}")
            return None

    def can_resume(self, pdf_path: Path) -> bool:
        """
        Check if a previous run can be resumed.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            True if valid state exists that can be resumed
        """
        state = self.load_state(pdf_path)
        if state is None:
            return False

        # Check if there's work left to do
        pending = state.get_pending_pages()
        return len(pending) > 0

    def get_resume_info(self, pdf_path: Path) -> Optional[Dict[str, Any]]:
        """
        Get information about a resumable state.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary with resume information or None
        """
        state = self.load_state(pdf_path)
        if state is None:
            return None

        pending = state.get_pending_pages()

        return {
            "pages_completed": state.pages_completed_count,
            "pages_pending": len(pending),
            "progress_percentage": state.progress_percentage,
            "cost_so_far": state.total_cost,
            "started_at": state.started_at,
            "last_updated": state.last_updated,
            "page_range": (state.page_range_start, state.page_range_end),
        }

    def clear_state(self, pdf_path: Path) -> bool:
        """
        Clear state for a PDF (start fresh).

        Args:
            pdf_path: Path to the PDF file

        Returns:
            True if state was cleared
        """
        state_path = self._get_state_path(pdf_path)
        backup_path = state_path.with_suffix(".backup")

        cleared = False

        for path in [state_path, backup_path]:
            if path.exists():
                try:
                    path.unlink()
                    cleared = True
                except Exception as e:
                    logger.warning(f"Failed to delete {path}: {e}")

        if cleared:
            logger.info(f"Cleared state for {pdf_path.name}")

        return cleared

    def update_page_state(
        self,
        state: PipelineState,
        page_num: int,
        **updates,
    ) -> None:
        """
        Update a specific page's state and save.

        Args:
            state: Current pipeline state
            page_num: Page number to update
            **updates: Key-value pairs to update
        """
        page_state = state.get_page_state(page_num)

        for key, value in updates.items():
            if hasattr(page_state, key):
                setattr(page_state, key, value)
            else:
                logger.warning(f"Unknown page state attribute: {key}")

        state.update_page(page_state)
        self.save_state(state)


def create_state_manager(state_dir: Optional[Path] = None) -> StateManager:
    """
    Factory function to create a state manager.

    Args:
        state_dir: Optional state directory

    Returns:
        Configured StateManager instance
    """
    return StateManager(state_dir=state_dir)
