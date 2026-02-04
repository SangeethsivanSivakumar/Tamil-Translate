"""
Processing screen with live progress display.

Shows real-time translation progress with cost tracking and log output.
"""

import logging
from pathlib import Path
from typing import Optional

from textual import work

logger = logging.getLogger(__name__)
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, ProgressBar, RichLog, Static
from textual.worker import Worker, WorkerState

from tamil_translate.config import get_config
from tamil_translate.pipeline import PipelineResult, create_pipeline


class ProcessingScreen(Screen):
    """
    Live processing screen showing translation progress.

    Features:
    - Progress bar with percentage
    - Real-time cost tracking
    - Current page indicator
    - Log output viewer
    - Cancel/pause functionality
    """

    BINDINGS = [
        Binding("c", "cancel_translation", "Cancel"),
        Binding("escape", "cancel_translation", "Cancel", show=False),
    ]

    def __init__(
        self,
        pdf_path: Path,
        page_range: tuple,
        resume: bool = True,
        dry_run: bool = False,
    ):
        super().__init__()
        self.pdf_path = pdf_path
        self.page_range = page_range
        self.resume = resume
        self.dry_run = dry_run

        # Progress tracking
        self.total_pages = page_range[1] - page_range[0] + 1
        self.pages_processed = 0
        self.current_cost = 0.0
        self.current_page = 0

        # Pipeline instance
        self._pipeline = None
        self._worker: Optional[Worker] = None

    def compose(self) -> ComposeResult:
        """Build the processing screen layout."""
        mode_text = "Cost Estimation" if self.dry_run else "Translation"
        yield Static(f"{mode_text}: {self.pdf_path.name}", classes="title")

        with Container(id="processing-container"):
            # Progress panel
            with Vertical(id="progress-panel", classes="panel"):
                yield Static("Progress", classes="panel-title")
                yield ProgressBar(total=100, show_eta=True, id="main-progress")

                yield Static(
                    f"Pages: 0/{self.total_pages}",
                    id="pages-status",
                    classes="metric-label",
                )

                # Metrics row
                with Horizontal(id="metrics-row"):
                    with Vertical(classes="metric-box"):
                        yield Static("Current Page", classes="metric-label")
                        yield Static("-", id="current-page", classes="metric-value")

                    with Vertical(classes="metric-box"):
                        yield Static("Cost", classes="metric-label")
                        yield Static("₹0.00", id="cost-display", classes="cost-display")

                    with Vertical(classes="metric-box"):
                        yield Static("OCR Confidence", classes="metric-label")
                        yield Static("-", id="confidence", classes="metric-value")

            # Log panel
            with Vertical(id="log-panel", classes="panel"):
                yield Static("Processing Log", classes="panel-title")
                yield RichLog(id="log-viewer", highlight=True, markup=True)

            # Action row
            with Horizontal(id="action-row"):
                yield Button("Cancel", id="btn-cancel", variant="error")
                yield Static("Press C or Escape to cancel", classes="hint")

    def on_mount(self) -> None:
        """Start the translation when screen mounts."""
        log = self.query_one("#log-viewer", RichLog)
        log.write(f"[bold]Starting translation: {self.pdf_path.name}[/bold]")
        log.write(f"Pages: {self.page_range[0]}-{self.page_range[1]} ({self.total_pages} pages)")
        log.write(f"Resume: {'Yes' if self.resume else 'No'}")
        log.write(f"Mode: {'Dry Run' if self.dry_run else 'Full Processing'}")
        log.write("")

        # Start the translation worker
        self._start_translation()

    def _start_translation(self) -> None:
        """Start the translation in a background worker thread."""
        self._worker = self.run_translation()

    @work(thread=True, exclusive=True)
    def run_translation(self) -> PipelineResult:
        """
        Run the translation pipeline in a background thread.

        Uses @work(thread=True) to avoid blocking the UI.
        """
        config = get_config()

        def on_page_complete(page_num: int, cost: float) -> None:
            """Callback for page completion - update UI from thread."""
            self.app.call_from_thread(self._update_progress, page_num, cost)

        try:
            # Create pipeline with callback
            self._pipeline = create_pipeline(
                config=config,
                on_page_complete=on_page_complete,
            )

            # Run the pipeline
            result = self._pipeline.run(
                pdf_path=str(self.pdf_path),
                page_range=self.page_range,
                resume=self.resume,
                dry_run=self.dry_run,
            )

            return result

        except Exception as e:
            # Log error and return failed result
            self.app.call_from_thread(self._log_message, f"[red]Error: {e}[/red]")
            return PipelineResult(
                success=False,
                pages_processed=self.pages_processed,
                pages_failed=1,
                total_cost_inr=self.current_cost,
                error=str(e),
            )

    def _update_progress(self, page_num: int, cost: float) -> None:
        """Update progress display (called from worker thread via call_from_thread)."""
        self.pages_processed += 1
        self.current_cost += cost
        self.current_page = page_num

        # Update progress bar
        progress = (self.pages_processed / self.total_pages) * 100
        progress_bar = self.query_one("#main-progress", ProgressBar)
        progress_bar.update(progress=progress)

        # Update metrics
        self.query_one("#pages-status", Static).update(
            f"Pages: {self.pages_processed}/{self.total_pages}"
        )
        self.query_one("#current-page", Static).update(str(page_num))
        self.query_one("#cost-display", Static).update(f"₹{self.current_cost:.2f}")

        # Log completion
        self._log_message(f"Page {page_num} completed (₹{cost:.2f})")

    def _log_message(self, message: str) -> None:
        """Add a message to the log viewer."""
        log = self.query_one("#log-viewer", RichLog)
        log.write(message)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes."""
        if event.state == WorkerState.SUCCESS:
            result = event.worker.result
            self._on_translation_complete(result)
        elif event.state == WorkerState.ERROR:
            self._log_message("[red]Translation failed with error[/red]")
            self._on_translation_complete(
                PipelineResult(
                    success=False,
                    pages_processed=self.pages_processed,
                    pages_failed=1,
                    total_cost_inr=self.current_cost,
                    error="Worker error",
                )
            )
        elif event.state == WorkerState.CANCELLED:
            self._log_message("[yellow]Translation cancelled by user[/yellow]")
            self._on_translation_complete(
                PipelineResult(
                    success=False,
                    pages_processed=self.pages_processed,
                    pages_failed=0,
                    total_cost_inr=self.current_cost,
                    error="Cancelled by user",
                )
            )

    def _on_translation_complete(self, result: PipelineResult) -> None:
        """Handle translation completion."""
        # Update progress to 100% if successful
        if result.success:
            progress_bar = self.query_one("#main-progress", ProgressBar)
            progress_bar.update(progress=100)

        self._log_message("")
        if result.success:
            self._log_message("[green bold]Translation complete![/green bold]")
        else:
            self._log_message(f"[red bold]Translation failed: {result.error}[/red bold]")

        self._log_message(f"Pages processed: {result.pages_processed}")
        self._log_message(f"Total cost: ₹{result.total_cost_inr:.2f}")

        if result.english_pdf_path:
            self._log_message(f"English PDF: {result.english_pdf_path}")
        if result.tamil_pdf_path:
            self._log_message(f"Tamil PDF: {result.tamil_pdf_path}")

        # Show results screen after a brief delay
        self.set_timer(1.5, lambda: self._show_results(result))

    def _show_results(self, result: PipelineResult) -> None:
        """Navigate to results screen."""
        self.app.pop_screen()  # Remove processing screen
        self.app.show_results(
            success=result.success,
            pages_processed=result.pages_processed,
            total_cost=result.total_cost_inr,
            english_pdf=result.english_pdf_path,
            tamil_pdf=result.tamil_pdf_path,
            error=result.error,
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "btn-cancel":
            self.action_cancel_translation()

    def action_cancel_translation(self) -> None:
        """Cancel the running translation."""
        if self._worker and self._worker.is_running:
            # Signal pipeline to stop using public method (thread-safe)
            if self._pipeline:
                self._pipeline.request_interrupt()
                logger.info("Translation cancellation requested by user")

            # Cancel the worker
            self._worker.cancel()
            self._log_message("[yellow]Cancellation requested...[/yellow]")
            self.notify("Cancelling translation...", severity="warning")
