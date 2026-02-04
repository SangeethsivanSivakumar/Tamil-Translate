"""
Session history screen.

Shows past translation sessions with details.
"""

import logging
from pathlib import Path

from textual.app import ComposeResult

logger = logging.getLogger(__name__)
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Static

from tamil_translate.config import get_config
from tamil_translate.state_manager import StateManager


class HistoryScreen(Screen):
    """
    Session history screen showing past translations.

    Features:
    - List of all translation sessions
    - Status, progress, and cost for each
    - Filter by status (completed, in-progress)
    """

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self):
        super().__init__()
        self.state_manager = StateManager()

    def compose(self) -> ComposeResult:
        """Build the history layout."""
        yield Static("Session History", classes="title")
        yield Static("Past translation sessions", classes="subtitle")

        with Container(id="history-container"):
            with Vertical(id="history-panel", classes="panel"):
                yield Static("All Sessions", classes="panel-title")
                yield DataTable(id="history-table", cursor_type="row")

                yield Static("", id="spacer")

                yield Button("Back to Dashboard", id="btn-back", variant="default")
                yield Button("Refresh", id="btn-refresh", variant="default")

    def on_mount(self) -> None:
        """Initialize history data."""
        self._setup_table()
        self._load_history()

    def _setup_table(self) -> None:
        """Configure the history table."""
        table = self.query_one("#history-table", DataTable)
        table.add_columns("File", "Status", "Pages", "Cost", "Last Updated")

    def _load_history(self) -> None:
        """Load session history from state files."""
        table = self.query_one("#history-table", DataTable)
        table.clear()

        config = get_config()
        state_dir = config.state_dir

        if not state_dir.exists():
            return

        # Scan all state files
        state_files = sorted(
            state_dir.glob("*.state.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        for state_file in state_files:
            pdf_name = state_file.stem.replace(".state", "")

            # Try to load state info
            pdf_path = config.input_dir / f"{pdf_name}.pdf"
            if not pdf_path.exists():
                pdf_path = config.input_dir / pdf_name

            resume_info = self.state_manager.get_resume_info(pdf_path)

            if resume_info:
                progress = resume_info["progress_percentage"]
                cost = resume_info["cost_so_far"]
                pending = resume_info["pages_pending"]
                completed = resume_info["pages_completed"]
                last_updated = resume_info.get("last_updated", "-")

                # Format last updated
                if last_updated and last_updated != "-":
                    try:
                        from datetime import datetime

                        dt = datetime.fromisoformat(last_updated)
                        last_updated = dt.strftime("%Y-%m-%d %H:%M")
                    except (ValueError, TypeError):
                        pass

                if pending > 0:
                    status = f"In Progress ({progress:.0f}%)"
                else:
                    status = "Completed"

                total_pages = completed + pending

                table.add_row(
                    pdf_name,
                    status,
                    f"{completed}/{total_pages}",
                    f"₹{cost:.2f}",
                    last_updated,
                )
            else:
                # State file exists but can't load
                table.add_row(
                    pdf_name,
                    "Unknown",
                    "-",
                    "-",
                    "-",
                )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "btn-back":
            self.action_go_back()
        elif event.button.id == "btn-refresh":
            self.action_refresh()

    def action_go_back(self) -> None:
        """Return to previous screen."""
        self.app.pop_screen()

    def action_refresh(self) -> None:
        """Refresh the history data."""
        self._load_history()
        self.notify("History refreshed", severity="information")
