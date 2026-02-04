"""
Interactive TUI for Tamil Translate.

Provides a keyboard-driven terminal interface with:
- Dashboard view showing recent files and resume options
- Built-in file browser for PDF selection
- Live progress display during translation
- Interactive settings configuration
- Session history tracking
"""

import sys
from typing import List, Optional


def should_launch_tui(argv: Optional[List[str]] = None) -> bool:
    """
    Determine if TUI mode should be launched.

    TUI launches when:
    - No command line arguments provided (except program name)
    - Only --tui flag provided

    Args:
        argv: Command line arguments (defaults to sys.argv)

    Returns:
        True if TUI should be launched
    """
    if argv is None:
        argv = sys.argv[1:]  # Exclude program name

    # No args = TUI mode
    if not argv:
        return True

    # Explicit --tui flag
    if "--tui" in argv or "-t" in argv:
        return True

    return False


def run_tui() -> int:
    """
    Launch the interactive TUI application.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    from tamil_translate.tui.app import TamilTranslateApp

    app = TamilTranslateApp()
    app.run()
    return 0


__all__ = ["should_launch_tui", "run_tui"]
