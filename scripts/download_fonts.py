#!/usr/bin/env python3
"""
Download required Noto Sans fonts for PDF generation.

This script downloads the necessary font files from Google Fonts
and places them in the fonts/ directory.
"""

import sys
import urllib.request
from pathlib import Path

# Font URLs from Google Fonts GitHub repository
FONTS = {
    "NotoSans-Regular.ttf": "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf",
    "NotoSansTamil-Regular.ttf": "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansTamil/NotoSansTamil-Regular.ttf",
    "NotoSansDevanagari-Regular.ttf": "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf",
}


def download_fonts(fonts_dir: Path) -> bool:
    """
    Download all required fonts.

    Args:
        fonts_dir: Directory to save fonts

    Returns:
        True if all fonts downloaded successfully
    """
    fonts_dir.mkdir(parents=True, exist_ok=True)

    success = True
    for filename, url in FONTS.items():
        font_path = fonts_dir / filename

        if font_path.exists():
            print(f"  ✓ {filename} (already exists)")
            continue

        print(f"  ⬇ Downloading {filename}...")

        try:
            urllib.request.urlretrieve(url, font_path)
            print(f"  ✓ {filename} ({font_path.stat().st_size // 1024} KB)")
        except Exception as e:
            print(f"  ✗ {filename}: {e}")
            success = False

    return success


def main() -> int:
    """Main entry point."""
    # Determine fonts directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    fonts_dir = project_root / "fonts"

    print(f"\nDownloading Noto Sans fonts to: {fonts_dir}\n")

    if download_fonts(fonts_dir):
        print("\n✓ All fonts downloaded successfully!")
        print("\nRun 'tamil-translate --check-fonts' to verify.\n")
        return 0
    else:
        print("\n✗ Some fonts failed to download.")
        print("Please download manually from: https://fonts.google.com/noto\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
