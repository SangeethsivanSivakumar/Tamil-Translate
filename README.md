# Tamil Translate

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **High-quality Sanskrit and Hindi PDF translation to English and Tamil using OCR and AI**

A production-ready translation pipeline that converts scanned PDFs containing Devanagari script (Sanskrit/Hindi) into searchable, translated PDFs in English and Tamil. Built with PaddleOCR for text extraction and Sarvam AI for translation.

![Translation Pipeline](https://img.shields.io/badge/Pipeline-OCR%20%E2%86%92%20Translate%20%E2%86%92%20PDF-blue)

## ✨ Features

- 🔍 **High-Accuracy OCR**: PaddleOCR PP-OCRv5 with adaptive preprocessing
- 🌐 **Multi-Language Support**: Sanskrit (Devanagari), Hindi → English, Tamil
- 📄 **PDF Generation**: Searchable PDFs with proper Unicode font embedding
- 💾 **Resume Capability**: Checksum-based state management for interrupted runs
- 🔒 **Security First**: Input validation, API key protection, path traversal prevention
- ⚡ **Concurrent Processing**: ThreadPoolExecutor for parallel translation
- 🎯 **Two-Step Tamil Translation**: Sanskrit → English → Tamil for improved quality
- 💰 **Cost Tracking**: Real-time translation cost estimation
- 🔄 **Automatic Retry**: Exponential backoff for API rate limits
- 📊 **Progress Tracking**: Per-page state persistence with tqdm progress bars

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- [Sarvam AI API key](https://dashboard.sarvam.ai) (₹1,000 free credits)
- Fonts: Noto Sans (Tamil, Devanagari, Regular)

### Installation

```bash
# Clone the repository
git clone https://github.com/SangeethsivanSivakumar/Tamil-Translate.git
cd Tamil-Translate

# Install the package
pip install -e .

# Download required fonts (if not already installed)
python3 scripts/download_fonts.py

# Set your API key
export SARVAM_API_KEY='your-sarvam-api-key-here'
```

### Basic Usage

```bash
# Test run (first 10 pages)
tamil-translate input.pdf

# Translate specific page range
tamil-translate input.pdf --pages 1-50

# Translate entire document
tamil-translate input.pdf --pages all

# Dry run (cost estimate only)
tamil-translate input.pdf --dry-run --pages all

# Resume from previous run
tamil-translate input.pdf --resume

# Start fresh (ignore previous state)
tamil-translate input.pdf --no-resume
```

## 📖 How It Works

```
┌─────────────┐
│  Input PDF  │ (Scanned images with Devanagari text)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  PaddleOCR  │ Extract text from images
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Sarvam AI  │ Translate Sanskrit/Hindi → English
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Sarvam AI  │ Translate English → Tamil (optional two-step)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  PDF Output │ Searchable PDFs with Unicode fonts
└─────────────┘
```

### Pipeline Architecture

1. **Security Validation**: All inputs validated (PDF format, API key, paths)
2. **OCR Extraction**: PaddleOCR processes each page with confidence scoring
3. **Text Chunking**: Smart word-boundary preserving splits (1800 chars max)
4. **Concurrent Translation**: ThreadPoolExecutor handles parallel API calls
5. **State Persistence**: Atomic writes after each page for resume capability
6. **PDF Generation**: fpdf2 creates searchable PDFs with proper fonts

## 📊 Translation Quality

| Source | Target | BLEU Score | Quality | Method |
|--------|--------|------------|---------|--------|
| Sanskrit | English | 25.56 | Moderate | Direct |
| Hindi | English | 32.15 | Good | Direct |
| Sanskrit | Tamil | 8.03 | Poor | Direct |
| Sanskrit | Tamil | **Better** | **Improved** | **Two-step (via English)** |

**Why Two-Step Tamil?**
Direct Sanskrit→Tamil translation produces low-quality results (BLEU 8.03). The system automatically uses Sanskrit→English→Tamil for significantly better output.

## 💰 Pricing

**Sarvam AI**: ₹20 per 10,000 characters
**Free Credits**: ₹1,000 included

### Cost Example (300-page document)

Assuming ~3,000 characters per page:

- **English translation**: ₹1,800
- **Tamil translation** (two-step): ₹3,600
- **Total**: ₹5,400 (~$65 USD)
- **With free credits**: ₹4,400 (~$53 USD)

Use `--dry-run` to estimate costs before processing.

## 🛠️ Advanced Usage

### CLI Options

```bash
tamil-translate [OPTIONS] INPUT_PDF

Options:
  --pages RANGE         Page range: "1-50", "all" (default: "1-10")
  --output DIR          Output directory (default: ./output)
  --workers N           Concurrent workers (default: 5)
  --verbose, -v         Enable verbose logging
  --dry-run             Estimate cost without processing
  --resume              Resume from previous run (default)
  --no-resume           Start fresh, ignore previous state
  --check-fonts         Verify required fonts are installed
  --version             Show version
```

### Environment Variables

```bash
# Required
export SARVAM_API_KEY='your-api-key'

# Optional
export MAX_WORKERS=5                    # Concurrent translation workers
export MAX_CHUNK_SIZE=1800              # Max chars per API request
export OCR_CONFIDENCE_THRESHOLD=0.80    # Min OCR confidence
```

### Python API

```python
from tamil_translate import TranslationPipeline

# Create pipeline
pipeline = TranslationPipeline()

# Process PDF
result = pipeline.run(
    pdf_path="input.pdf",
    page_range=(1, 50),
    resume=True,
    dry_run=False
)

print(f"Success: {result.success}")
print(f"Pages: {result.pages_processed}")
print(f"Cost: ₹{result.total_cost_inr:.2f}")
print(f"English PDF: {result.english_pdf_path}")
print(f"Tamil PDF: {result.tamil_pdf_path}")
```

## 🏗️ Project Structure

```
tamil-translate/
├── src/tamil_translate/      # Main package
│   ├── cli.py                # CLI entry point
│   ├── config.py             # Configuration management
│   ├── security.py           # Input validation
│   ├── ocr_engine.py         # PaddleOCR wrapper
│   ├── translator.py         # Sarvam AI translation
│   ├── state_manager.py      # Resume capability
│   ├── pdf_generator.py      # PDF creation
│   └── pipeline.py           # Main orchestration
├── scripts/                  # Helper scripts
│   └── download_fonts.py     # Font downloader
├── fonts/                    # Noto Sans fonts
├── output/                   # Generated PDFs
│   ├── english/
│   ├── tamil/
│   ├── intermediate/
│   └── .state/               # Resume state files
├── Documentations/           # API documentation
├── pyproject.toml            # Package configuration
├── CLAUDE.md                 # AI assistant guide
├── README.md                 # This file
└── LICENSE                   # MIT License
```

## 🔧 Development

### Setup Development Environment

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/

# Run tests (when available)
pytest
```

### Code Quality Standards

- **Formatting**: Black (line length: 100)
- **Linting**: Ruff
- **Type Hints**: Python 3.9+ with mypy
- **Testing**: pytest (tests to be added)

## 🐛 Troubleshooting

### Missing Fonts

```bash
tamil-translate --check-fonts
python3 scripts/download_fonts.py
```

### API Key Issues

- Verify key: `echo $SARVAM_API_KEY`
- Key must be 32+ characters
- Get key from: https://dashboard.sarvam.ai

### Resume Not Working

- State files: `output/.state/*.json`
- Clear state: `--no-resume` flag
- Checksum mismatch means PDF was modified

### Translation Quality

- Check OCR confidence in state files
- Low confidence? Try different PDF quality
- Repetitive output? System auto-detects and removes loops

See [CLAUDE.md](CLAUDE.md) for detailed troubleshooting and architecture guide.

## 📚 Documentation

- [CLAUDE.md](CLAUDE.md) - Complete architecture and development guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) - Community standards
- [Documentations/](Documentations/) - Sarvam AI API reference

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Priorities

- [ ] Add comprehensive test suite
- [ ] Support additional OCR backends (Tesseract)
- [ ] Add more language pairs
- [ ] GUI interface
- [ ] Docker containerization
- [ ] Batch processing optimization

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PaddleOCR** - Excellent open-source OCR toolkit
- **Sarvam AI** - High-quality Indic language translation API
- **fpdf2** - Python PDF generation library
- **Vidyamadhaviyam** - Source religious texts

## 📧 Contact

**Sangeeth Sivan**
- GitHub: [@SangeethsivanSivakumar](https://github.com/SangeethsivanSivakumar)
- Project: [Tamil-Translate](https://github.com/SangeethsivanSivakumar/Tamil-Translate)

## ⭐ Star History

If you find this project helpful, please consider giving it a star! ⭐

---

**Built with ❤️ for preserving and translating Sanskrit religious texts**
