"""TUI screens for Tamil Translate."""

from tamil_translate.tui.screens.dashboard import DashboardScreen
from tamil_translate.tui.screens.browser import FileBrowserScreen
from tamil_translate.tui.screens.processing import ProcessingScreen
from tamil_translate.tui.screens.settings import SettingsScreen
from tamil_translate.tui.screens.results import ResultsScreen
from tamil_translate.tui.screens.history import HistoryScreen
from tamil_translate.tui.screens.help import HelpScreen

__all__ = [
    "DashboardScreen",
    "FileBrowserScreen",
    "ProcessingScreen",
    "SettingsScreen",
    "ResultsScreen",
    "HistoryScreen",
    "HelpScreen",
]
