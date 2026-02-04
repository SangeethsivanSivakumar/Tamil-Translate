"""
Main Textual application for Tamil Translate TUI.

Handles screen routing, global keybindings, and theme configuration.
"""

from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer

from tamil_translate.config import Config, get_config


class TamilTranslateApp(App):
    """
    Interactive TUI application for Tamil Translate.

    Features:
    - Dashboard with recent files and resume options
    - File browser for PDF selection
    - Live progress display during translation
    - Settings configuration
    - Session history tracking
    """

    TITLE = "Tamil Translate"
    SUB_TITLE = "Sanskrit/Hindi PDF Translation"

    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True, priority=True),
        Binding("d", "show_dashboard", "Dashboard", show=True),
        Binding("n", "new_translation", "New", show=True),
        Binding("s", "show_settings", "Settings", show=True),
        Binding("h", "show_history", "History", show=True),
        Binding("?", "show_help", "Help", show=True),
        Binding("escape", "go_back", "Back", show=False),
    ]

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the TUI application.

        Args:
            config: Optional configuration (uses global config if not provided)
        """
        super().__init__()
        self.config = config or get_config()

        # Current state
        self.selected_pdf: Optional[Path] = None
        self.current_page_range: Optional[tuple] = None

    def compose(self) -> ComposeResult:
        """Compose the app layout."""
        yield Footer()

    def on_mount(self) -> None:
        """Initialize app on startup."""
        # Import here to avoid circular imports
        from tamil_translate.tui.screens.dashboard import DashboardScreen

        # Push dashboard as initial screen
        self.push_screen(DashboardScreen())

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit(0)

    def action_show_dashboard(self) -> None:
        """Navigate to dashboard screen."""
        from tamil_translate.tui.screens.dashboard import DashboardScreen

        # If already on dashboard, do nothing
        if isinstance(self.screen, DashboardScreen):
            return

        # Pop all screens back to base, then push dashboard
        while len(self.screen_stack) > 1:
            self.pop_screen()

        # Push a fresh dashboard
        self.push_screen(DashboardScreen())

    def action_new_translation(self) -> None:
        """Start a new translation."""
        from tamil_translate.tui.screens.browser import FileBrowserScreen

        self.push_screen(FileBrowserScreen())

    def action_show_settings(self) -> None:
        """Show settings modal."""
        from tamil_translate.tui.screens.settings import SettingsScreen

        self.push_screen(SettingsScreen())

    def action_show_history(self) -> None:
        """Show session history."""
        from tamil_translate.tui.screens.history import HistoryScreen

        self.push_screen(HistoryScreen())

    def action_show_help(self) -> None:
        """Show help information."""
        from tamil_translate.tui.screens.help import HelpScreen

        self.push_screen(HelpScreen())

    def action_go_back(self) -> None:
        """Go back to previous screen."""
        if len(self.screen_stack) > 1:
            self.pop_screen()

    def start_translation(
        self,
        pdf_path: Path,
        page_range: tuple,
        resume: bool = True,
        dry_run: bool = False,
    ) -> None:
        """
        Start translation process.

        Args:
            pdf_path: Path to PDF file
            page_range: Tuple of (start_page, end_page)
            resume: Whether to resume from previous state
            dry_run: Whether to only estimate cost
        """
        from tamil_translate.tui.screens.processing import ProcessingScreen

        self.selected_pdf = pdf_path
        self.current_page_range = page_range

        self.push_screen(
            ProcessingScreen(
                pdf_path=pdf_path,
                page_range=page_range,
                resume=resume,
                dry_run=dry_run,
            )
        )

    def show_results(
        self,
        success: bool,
        pages_processed: int,
        total_cost: float,
        english_pdf: Optional[Path] = None,
        tamil_pdf: Optional[Path] = None,
        error: Optional[str] = None,
    ) -> None:
        """
        Show translation results.

        Args:
            success: Whether translation was successful
            pages_processed: Number of pages processed
            total_cost: Total cost in INR
            english_pdf: Path to English PDF output
            tamil_pdf: Path to Tamil PDF output
            error: Error message if failed
        """
        from tamil_translate.tui.screens.results import ResultsScreen

        self.push_screen(
            ResultsScreen(
                success=success,
                pages_processed=pages_processed,
                total_cost=total_cost,
                english_pdf=english_pdf,
                tamil_pdf=tamil_pdf,
                error=error,
            )
        )
