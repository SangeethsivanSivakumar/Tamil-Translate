"""
Dashboard screen - main entry point for TUI.

Shows recent files, resume options, and quick actions.
"""

import logging
from pathlib import Path
from typing import Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Static

from tamil_translate.config import get_config
from tamil_translate.state_manager import StateManager

logger = logging.getLogger(__name__)


class DashboardScreen(Screen):
    """
    Main dashboard showing recent files and quick actions.

    Features:
    - Recent files with progress and cost info
    - Resume incomplete translations
    - Quick action buttons for common operations
    """

    BINDINGS = [
        Binding("n", "new_translation", "New Translation"),
        Binding("r", "resume_selected", "Resume Selected"),
        Binding("enter", "resume_selected", "Resume Selected", show=False),
    ]

    def __init__(self):
        super().__init__()
        self.state_manager = StateManager()
        self.selected_file: Optional[Path] = None

    def compose(self) -> ComposeResult:
        """Build the dashboard layout."""
        yield Static("Tamil Translate", classes="title")
        yield Static("Sanskrit/Hindi PDF Translation to English & Tamil", classes="subtitle")

        with Container(id="dashboard-container"):
            # Recent files panel (left side)
            with Vertical(id="recent-panel", classes="panel"):
                yield Static("Recent Files", classes="panel-title")
                yield DataTable(id="recent-table", cursor_type="row")

            # Right side panels
            with Vertical():
                # Quick actions panel
                with Vertical(id="actions-panel", classes="panel"):
                    yield Static("Quick Actions", classes="panel-title")
                    yield Button("New Translation", id="btn-new", variant="primary")
                    yield Button("Resume Selected", id="btn-resume", variant="default")
                    yield Button("Settings", id="btn-settings", variant="default")
                    yield Button("Session History", id="btn-history", variant="default")

                # Stats panel
                with Vertical(id="stats-panel", classes="panel"):
                    yield Static("Session Stats", classes="panel-title")
                    yield Static("Total translations: 0", id="stat-total")
                    yield Static("Total cost: ₹0.00", id="stat-cost")

    def on_mount(self) -> None:
        """Initialize dashboard data."""
        self._setup_table()
        self._load_recent_files()
        self._load_stats()

    def _setup_table(self) -> None:
        """Configure the recent files table."""
        table = self.query_one("#recent-table", DataTable)
        table.add_columns("File", "Status", "Progress", "Cost")

    def _load_recent_files(self) -> None:
        """Load recent files from state directory."""
        table = self.query_one("#recent-table", DataTable)
        table.clear()

        config = get_config()
        state_dir = config.state_dir

        if not state_dir.exists():
            return

        # Scan for state files
        state_files = sorted(
            state_dir.glob("*.state.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        for state_file in state_files[:10]:  # Show last 10
            pdf_name = state_file.stem.replace(".state", "")

            # Try to load state info
            pdf_path = config.input_dir / f"{pdf_name}.pdf"
            if not pdf_path.exists():
                # Try without .pdf extension
                pdf_path = config.input_dir / pdf_name

            resume_info = self.state_manager.get_resume_info(pdf_path)

            if resume_info:
                progress = resume_info["progress_percentage"]
                cost = resume_info["cost_so_far"]
                pending = resume_info["pages_pending"]

                if pending > 0:
                    status = "Resume Available"
                else:
                    status = "Completed"

                table.add_row(
                    pdf_name,
                    status,
                    f"{progress:.1f}%",
                    f"₹{cost:.2f}",
                    key=str(pdf_path),
                )
            else:
                # State exists but can't load (might be corrupted or PDF moved)
                table.add_row(
                    pdf_name,
                    "Unknown",
                    "-",
                    "-",
                    key=str(state_file),
                )

    def _load_stats(self) -> None:
        """Load session statistics."""
        config = get_config()
        state_dir = config.state_dir

        total_translations = 0
        total_cost = 0.0

        if state_dir.exists():
            for state_file in state_dir.glob("*.state.json"):
                total_translations += 1
                # Try to get cost info
                pdf_name = state_file.stem.replace(".state", "")
                pdf_path = config.input_dir / f"{pdf_name}.pdf"
                resume_info = self.state_manager.get_resume_info(pdf_path)
                if resume_info:
                    total_cost += resume_info.get("cost_so_far", 0)

        self.query_one("#stat-total", Static).update(
            f"Total translations: {total_translations}"
        )
        self.query_one("#stat-cost", Static).update(f"Total cost: ₹{total_cost:.2f}")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in the table."""
        if event.row_key:
            self.selected_file = Path(str(event.row_key.value))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        button_id = event.button.id

        if button_id == "btn-new":
            self.action_new_translation()
        elif button_id == "btn-resume":
            self.action_resume_selected()
        elif button_id == "btn-settings":
            self.app.action_show_settings()
        elif button_id == "btn-history":
            self.app.action_show_history()

    def action_new_translation(self) -> None:
        """Start a new translation."""
        self.app.action_new_translation()

    def action_resume_selected(self) -> None:
        """Resume the selected translation."""
        if not self.selected_file:
            self.notify("Please select a file to resume", severity="warning")
            return

        # Check if file exists and has pending pages
        resume_info = self.state_manager.get_resume_info(self.selected_file)
        if not resume_info:
            self.notify("Cannot resume: state file invalid or PDF modified", severity="error")
            return

        if resume_info["pages_pending"] == 0:
            self.notify("This translation is already complete", severity="information")
            return

        # Get page range from state
        page_range = resume_info["page_range"]

        # Start translation with resume
        self.app.start_translation(
            pdf_path=self.selected_file,
            page_range=page_range,
            resume=True,
        )
