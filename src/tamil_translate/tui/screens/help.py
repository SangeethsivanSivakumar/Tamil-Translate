"""
Help screen with keyboard shortcuts and usage information.
"""

import logging

from textual.app import ComposeResult

logger = logging.getLogger(__name__)
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class HelpScreen(ModalScreen):
    """
    Modal help screen showing keyboard shortcuts and usage.

    Features:
    - Global keyboard shortcuts
    - Screen-specific shortcuts
    - Usage tips
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("?", "close", "Close", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Build the help layout."""
        with Container(id="help-container"):
            with Vertical(id="help-panel", classes="panel"):
                yield Static("Help & Keyboard Shortcuts", classes="title")

                yield Static("", id="spacer")

                # Global shortcuts
                yield Static("Global Shortcuts", classes="panel-title help-section")
                yield self._shortcut_row("q", "Quit application")
                yield self._shortcut_row("d", "Go to Dashboard")
                yield self._shortcut_row("n", "New Translation")
                yield self._shortcut_row("s", "Open Settings")
                yield self._shortcut_row("h", "Session History")
                yield self._shortcut_row("?", "Show this help")
                yield self._shortcut_row("Escape", "Go back / Cancel")

                yield Static("", id="spacer2")

                # Dashboard shortcuts
                yield Static("Dashboard", classes="panel-title help-section")
                yield self._shortcut_row("r", "Resume selected translation")
                yield self._shortcut_row("Enter", "Resume selected translation")

                yield Static("", id="spacer3")

                # File browser shortcuts
                yield Static("File Browser", classes="panel-title help-section")
                yield self._shortcut_row("Enter", "Select file / Open folder")
                yield self._shortcut_row("Arrows", "Navigate file tree")

                yield Static("", id="spacer4")

                # Processing shortcuts
                yield Static("Processing", classes="panel-title help-section")
                yield self._shortcut_row("c", "Cancel translation")

                yield Static("", id="spacer5")

                # Tips
                yield Static("Tips", classes="panel-title help-section")
                yield Static(
                    "- Use 'Dry Run' to estimate costs before translating",
                    classes="hint",
                )
                yield Static(
                    "- Translations can be resumed if interrupted",
                    classes="hint",
                )
                yield Static(
                    "- Smaller chunk sizes prevent translation loops but cost more",
                    classes="hint",
                )

                yield Static("", id="spacer6")

                yield Button("Close", id="btn-close", variant="primary")

    def _shortcut_row(self, key: str, description: str) -> Static:
        """Create a shortcut display row."""
        return Static(f"  [{key}]  {description}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "btn-close":
            self.action_close()

    def action_close(self) -> None:
        """Close the help screen."""
        self.app.pop_screen()
