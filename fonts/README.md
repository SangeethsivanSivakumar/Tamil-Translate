# Font Files

This directory should contain the following Noto Sans font files for PDF generation:

## Required Fonts

1. **NotoSans-Regular.ttf** - For English/Latin text
2. **NotoSansTamil-Regular.ttf** - For Tamil text
3. **NotoSansDevanagari-Regular.ttf** - For Sanskrit/Hindi text

## Download Instructions

### Option 1: Direct Download

1. Visit Google Fonts Noto page: https://fonts.google.com/noto
2. Download each font:
   - [Noto Sans](https://fonts.google.com/noto/specimen/Noto+Sans)
   - [Noto Sans Tamil](https://fonts.google.com/noto/specimen/Noto+Sans+Tamil)
   - [Noto Sans Devanagari](https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari)
3. Extract the downloaded ZIP files
4. Copy the `*-Regular.ttf` files to this directory

### Option 2: Using the Download Script

Run the font download script from the project root:

```bash
python scripts/download_fonts.py
```

### Option 3: Using curl

```bash
# From the project fonts/ directory

# Noto Sans (English)
curl -L "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf" -o NotoSans-Regular.ttf

# Noto Sans Tamil
curl -L "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansTamil/NotoSansTamil-Regular.ttf" -o NotoSansTamil-Regular.ttf

# Noto Sans Devanagari
curl -L "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf" -o NotoSansDevanagari-Regular.ttf
```

## Verification

After downloading, run:

```bash
tamil-translate --check-fonts
```

You should see:
```
✓ english
✓ tamil
✓ devanagari
```

## License

Noto fonts are released under the SIL Open Font License (OFL).
See: https://scripts.sil.org/OFL
