"""
File browser screen for PDF selection.

Allows users to navigate the filesystem and select a PDF to translate.
"""

import logging
from pathlib import Path
from typing import Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DirectoryTree, Input, Static

from tamil_translate.config import get_config

logger = logging.getLogger(__name__)


class PDFDirectoryTree(DirectoryTree):
    """Directory tree that filters to show only PDF files."""

    def filter_paths(self, paths):
        """Filter to show only directories and PDF files."""
        return [
            path
            for path in paths
            if path.is_dir() or path.suffix.lower() == ".pdf"
        ]


class FileBrowserScreen(Screen):
    """
    File browser for selecting PDF files.

    Features:
    - Navigate filesystem with keyboard
    - Filter to show only PDF files
    - Preview file metadata (pages, size)
    - Quick path input for direct navigation
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm", "Select", show=False),
    ]

    def __init__(self):
        super().__init__()
        self.selected_path: Optional[Path] = None
        config = get_config()
        # Start in the input directory or home
        self.start_path = config.input_dir if config.input_dir.exists() else Path.home()

    def compose(self) -> ComposeResult:
        """Build the file browser layout."""
        yield Static("Select PDF File", classes="title")

        with Horizontal(id="browser-container"):
            # Left: Directory tree
            with Vertical(id="tree-panel", classes="panel"):
                yield Static("File Browser", classes="panel-title")
                yield PDFDirectoryTree(self.start_path, id="dir-tree")

            # Right: Preview and actions
            with Vertical(id="preview-panel", classes="panel"):
                yield Static("File Preview", classes="panel-title")
                yield Static("Select a PDF file to see details", id="file-info")

                yield Static("", id="spacer")

                # Page range selection
                yield Static("Page Range:", classes="setting-label")
                yield Input(
                    placeholder='e.g., "1-10", "all", or "5"',
                    id="page-range-input",
                    value="1-10",
                )
                yield Static(
                    'Use "all" for entire document, or specify range like "1-50"',
                    classes="hint",
                )

                yield Static("", id="spacer2")

                # Action buttons
                yield Button(
                    "Start Translation",
                    id="btn-start",
                    variant="primary",
                    disabled=True,
                )
                yield Button("Dry Run (Cost Estimate)", id="btn-dry-run", disabled=True)
                yield Button("Cancel", id="btn-cancel")

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Handle file selection in the tree."""
        path = event.path

        if path.suffix.lower() == ".pdf":
            self.selected_path = path
            self._show_preview(path)
            self._enable_buttons(True)
        else:
            self.selected_path = None
            self._show_preview(None)
            self._enable_buttons(False)

    def _show_preview(self, pdf_path: Optional[Path]) -> None:
        """Display PDF file information."""
        info_widget = self.query_one("#file-info", Static)

        if pdf_path is None:
            info_widget.update("Select a PDF file to see details")
            return

        try:
            from tamil_translate.ocr_engine import get_pdf_page_count

            page_count = get_pdf_page_count(pdf_path)
            size_bytes = pdf_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)

            info_text = (
                f"[bold]File:[/bold] {pdf_path.name}\n"
                f"[bold]Pages:[/bold] {page_count}\n"
                f"[bold]Size:[/bold] {size_mb:.1f} MB\n"
                f"[bold]Path:[/bold] {pdf_path.parent}"
            )
            info_widget.update(info_text)

        except Exception as e:
            info_widget.update(f"Error reading PDF: {e}")
            self._enable_buttons(False)

    def _enable_buttons(self, enabled: bool) -> None:
        """Enable or disable action buttons."""
        self.query_one("#btn-start", Button).disabled = not enabled
        self.query_one("#btn-dry-run", Button).disabled = not enabled

    def _get_page_range(self) -> Optional[tuple]:
        """Parse the page range input."""
        from tamil_translate.cli import parse_page_range
        from tamil_translate.ocr_engine import get_pdf_page_count

        if not self.selected_path:
            return None

        page_input = self.query_one("#page-range-input", Input).value.strip()

        try:
            total_pages = get_pdf_page_count(self.selected_path)
            return parse_page_range(page_input, total_pages)
        except (ValueError, Exception) as e:
            self.notify(f"Invalid page range: {e}", severity="error")
            return None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        button_id = event.button.id

        if button_id == "btn-start":
            self._start_translation(dry_run=False)
        elif button_id == "btn-dry-run":
            self._start_translation(dry_run=True)
        elif button_id == "btn-cancel":
            self.action_cancel()

    def _start_translation(self, dry_run: bool = False) -> None:
        """Start the translation process."""
        if not self.selected_path:
            self.notify("Please select a PDF file", severity="warning")
            return

        page_range = self._get_page_range()
        if not page_range:
            return

        # Start translation
        self.app.start_translation(
            pdf_path=self.selected_path,
            page_range=page_range,
            resume=True,
            dry_run=dry_run,
        )

    def action_cancel(self) -> None:
        """Cancel and return to previous screen."""
        self.app.pop_screen()

    def action_confirm(self) -> None:
        """Confirm selection and start translation."""
        if self.selected_path:
            self._start_translation(dry_run=False)
