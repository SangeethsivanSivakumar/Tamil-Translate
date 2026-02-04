"""
Results screen showing translation completion status.

Displays success/failure, output paths, and actions.
"""

import logging
import subprocess
import sys
from pathlib import Path
from typing import Optional

from textual.app import ComposeResult

logger = logging.getLogger(__name__)
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static


class ResultsScreen(Screen):
    """
    Results screen showing translation completion.

    Features:
    - Success/failure status
    - Page count and cost summary
    - Output file paths
    - Open PDF buttons
    """

    BINDINGS = [
        Binding("enter", "done", "Done"),
        Binding("escape", "done", "Done", show=False),
        Binding("e", "open_english", "Open English"),
        Binding("t", "open_tamil", "Open Tamil"),
    ]

    def __init__(
        self,
        success: bool,
        pages_processed: int,
        total_cost: float,
        english_pdf: Optional[Path] = None,
        tamil_pdf: Optional[Path] = None,
        error: Optional[str] = None,
    ):
        super().__init__()
        self.success = success
        self.pages_processed = pages_processed
        self.total_cost = total_cost
        self.english_pdf = english_pdf
        self.tamil_pdf = tamil_pdf
        self.error = error

    def compose(self) -> ComposeResult:
        """Build the results layout."""
        with Container(id="results-container"):
            with Vertical(id="results-panel", classes="panel"):
                # Status header
                if self.success:
                    yield Static(
                        "Translation Complete!",
                        classes="result-success title",
                    )
                else:
                    yield Static(
                        "Translation Failed",
                        classes="result-error title",
                    )

                yield Static("", id="spacer")

                # Summary statistics
                yield Static("Summary", classes="panel-title")

                with Horizontal(classes="setting-row"):
                    yield Static("Pages processed:", classes="metric-label")
                    yield Static(str(self.pages_processed), classes="metric-value")

                with Horizontal(classes="setting-row"):
                    yield Static("Total cost:", classes="metric-label")
                    yield Static(f"₹{self.total_cost:.2f}", classes="cost-display")

                # Error message if failed
                if self.error:
                    yield Static("", id="spacer2")
                    yield Static("Error", classes="panel-title")
                    yield Static(self.error, classes="error-text")

                # Output files
                if self.english_pdf or self.tamil_pdf:
                    yield Static("", id="spacer3")
                    yield Static("Output Files", classes="panel-title")

                    if self.english_pdf:
                        yield Static(
                            f"English: {self.english_pdf}",
                            classes="output-path",
                        )
                        yield Button(
                            "Open English PDF",
                            id="btn-open-english",
                            variant="default",
                        )

                    if self.tamil_pdf:
                        yield Static(
                            f"Tamil: {self.tamil_pdf}",
                            classes="output-path",
                        )
                        yield Button(
                            "Open Tamil PDF",
                            id="btn-open-tamil",
                            variant="default",
                        )

                yield Static("", id="spacer4")

                # Action buttons
                with Horizontal(id="button-row"):
                    yield Button("Done", id="btn-done", variant="primary")
                    yield Button("New Translation", id="btn-new")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        button_id = event.button.id

        if button_id == "btn-done":
            self.action_done()
        elif button_id == "btn-new":
            self.action_new_translation()
        elif button_id == "btn-open-english":
            self.action_open_english()
        elif button_id == "btn-open-tamil":
            self.action_open_tamil()

    def action_done(self) -> None:
        """Return to dashboard."""
        self.app.action_show_dashboard()

    def action_new_translation(self) -> None:
        """Start a new translation."""
        self.app.action_new_translation()

    def action_open_english(self) -> None:
        """Open the English PDF in system viewer."""
        self._open_pdf(self.english_pdf)

    def action_open_tamil(self) -> None:
        """Open the Tamil PDF in system viewer."""
        self._open_pdf(self.tamil_pdf)

    def _open_pdf(self, pdf_path: Optional[Path]) -> None:
        """Open a PDF file in the system's default viewer."""
        if not pdf_path or not pdf_path.exists():
            self.notify("PDF file not found", severity="error")
            return

        try:
            if sys.platform == "darwin":
                # macOS
                subprocess.run(["open", str(pdf_path)], check=True)
            elif sys.platform == "win32":
                # Windows
                subprocess.run(["start", "", str(pdf_path)], shell=True, check=True)
            else:
                # Linux
                subprocess.run(["xdg-open", str(pdf_path)], check=True)

            self.notify(f"Opened: {pdf_path.name}", severity="information")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to open PDF {pdf_path}: {e}")
            self.notify(f"Failed to open PDF: {e}", severity="error")
        except FileNotFoundError:
            logger.warning(f"No PDF viewer found on platform {sys.platform}")
            self.notify("No PDF viewer found", severity="error")
