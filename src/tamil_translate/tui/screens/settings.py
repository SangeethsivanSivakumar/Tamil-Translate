"""
Settings screen for configuration.

Allows users to modify processing settings interactively.
"""

import logging

from textual.app import ComposeResult

logger = logging.getLogger(__name__)
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static, Switch

from tamil_translate.config import get_config


class SettingsScreen(ModalScreen):
    """
    Modal settings screen for configuration.

    Features:
    - Edit workers, chunk size, DPI
    - Toggle preprocessing
    - Input validation with hints
    - Save/cancel actions
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("ctrl+s", "save", "Save"),
    ]

    def __init__(self):
        super().__init__()
        self.config = get_config()

    def _get_masked_api_key(self) -> str:
        """Get masked display of API key."""
        key = self.config.SARVAM_API_KEY
        if not key:
            return ""
        if len(key) <= 8:
            return "*" * len(key)
        # Show first 4 and last 4 characters
        return key[:4] + "*" * (len(key) - 8) + key[-4:]

    def _get_api_key_status(self) -> str:
        """Get status text for API key."""
        if self.config.SARVAM_API_KEY:
            return "[green]✓ API key configured[/green]"
        return "[red]✗ API key not set[/red]"

    def compose(self) -> ComposeResult:
        """Build the settings layout."""
        with Container(id="settings-container"):
            with Vertical(id="settings-panel", classes="panel"):
                yield Static("Settings", classes="title")
                yield Static("Configure translation options", classes="subtitle")

                # API Key setting (at the top for importance)
                with Horizontal(classes="setting-row"):
                    yield Static("API Key:", classes="setting-label")
                    yield Input(
                        self._get_masked_api_key(),
                        id="input-api-key",
                        password=True,
                        placeholder="Enter Sarvam API key",
                        classes="setting-input api-key-input",
                    )
                yield Static(
                    self._get_api_key_status(),
                    id="api-key-status",
                    classes="hint",
                )
                yield Static(
                    "Get your key from: https://dashboard.sarvam.ai",
                    classes="hint",
                )

                yield Static("", id="spacer-api")

                # Workers setting
                with Horizontal(classes="setting-row"):
                    yield Static("Workers:", classes="setting-label")
                    yield Input(
                        str(self.config.MAX_WORKERS),
                        id="input-workers",
                        type="integer",
                        classes="setting-input",
                    )
                yield Static(
                    "Concurrent translation workers (1-20)",
                    classes="hint",
                )

                # Chunk size setting
                with Horizontal(classes="setting-row"):
                    yield Static("Chunk Size:", classes="setting-label")
                    yield Input(
                        str(self.config.MAX_CHUNK_SIZE),
                        id="input-chunk-size",
                        type="integer",
                        classes="setting-input",
                    )
                yield Static(
                    "Characters per API request (100-2000). Smaller = safer, more API calls",
                    classes="hint",
                )

                # DPI setting
                with Horizontal(classes="setting-row"):
                    yield Static("OCR DPI:", classes="setting-label")
                    yield Input(
                        str(self.config.OCR_DPI),
                        id="input-dpi",
                        type="integer",
                        classes="setting-input",
                    )
                yield Static(
                    "PDF rendering resolution (150-600). Higher = better quality, slower",
                    classes="hint",
                )

                # Preprocessing toggle
                with Horizontal(classes="setting-row"):
                    yield Static("Preprocessing:", classes="setting-label")
                    yield Switch(
                        value=self.config.OCR_PREPROCESS_ENABLED,
                        id="switch-preprocess",
                    )
                yield Static(
                    "Apply image preprocessing before OCR (grayscale, denoise, binarize)",
                    classes="hint",
                )

                yield Static("", id="spacer")

                # Action buttons
                with Horizontal(id="button-row"):
                    yield Button("Save", id="btn-save", variant="primary")
                    yield Button("Cancel", id="btn-cancel")

    def _is_new_api_key(self, value: str) -> bool:
        """Check if the API key input contains a new key (not the masked version)."""
        if not value:
            return False
        # If it contains asterisks in the middle, it's likely the masked version
        if value == self._get_masked_api_key():
            return False
        # If it's all asterisks, user cleared it
        if all(c == "*" for c in value):
            return False
        return True

    def _validate_inputs(self) -> bool:
        """Validate all input values."""
        try:
            workers = int(self.query_one("#input-workers", Input).value)
            chunk_size = int(self.query_one("#input-chunk-size", Input).value)
            dpi = int(self.query_one("#input-dpi", Input).value)

            # Validate ranges
            if not 1 <= workers <= 20:
                self.notify("Workers must be between 1 and 20", severity="error")
                return False

            if not 100 <= chunk_size <= 2000:
                self.notify("Chunk size must be between 100 and 2000", severity="error")
                return False

            if not 150 <= dpi <= 600:
                self.notify("DPI must be between 150 and 600", severity="error")
                return False

            # Validate API key if a new one was entered
            api_key_input = self.query_one("#input-api-key", Input).value
            if self._is_new_api_key(api_key_input):
                if len(api_key_input) < 10:
                    self.notify("API key seems too short", severity="warning")

            return True

        except ValueError as e:
            self.notify(f"Invalid input: {e}", severity="error")
            return False

    def _apply_settings(self) -> None:
        """Apply settings to config."""
        # Apply API key if a new one was entered
        api_key_input = self.query_one("#input-api-key", Input).value
        if self._is_new_api_key(api_key_input):
            self.config.SARVAM_API_KEY = api_key_input
            logger.info("API key updated")

        self.config.MAX_WORKERS = int(self.query_one("#input-workers", Input).value)
        self.config.MAX_CHUNK_SIZE = int(self.query_one("#input-chunk-size", Input).value)
        self.config.OCR_DPI = int(self.query_one("#input-dpi", Input).value)
        self.config.OCR_PREPROCESS_ENABLED = self.query_one("#switch-preprocess", Switch).value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "btn-save":
            self.action_save()
        elif event.button.id == "btn-cancel":
            self.action_cancel()

    def action_save(self) -> None:
        """Save settings and close modal."""
        if self._validate_inputs():
            self._apply_settings()
            logger.info(
                f"Settings saved: workers={self.config.MAX_WORKERS}, "
                f"chunk_size={self.config.MAX_CHUNK_SIZE}, dpi={self.config.OCR_DPI}, "
                f"preprocess={self.config.OCR_PREPROCESS_ENABLED}"
            )
            self.notify("Settings saved", severity="information")
            self.app.pop_screen()

    def action_cancel(self) -> None:
        """Cancel and close modal."""
        self.app.pop_screen()
