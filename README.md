<div align="center">

# Tamil Translate

### Transform Sanskrit & Hindi PDFs into English and Tamil

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black)

<br />

**Production-ready translation pipeline** that converts scanned PDFs containing Devanagari script into searchable, beautifully formatted PDFs in English and Tamil.

[Getting Started](#-quick-start) · [Features](#-features) · [Documentation](#-documentation) · [Contributing](#-contributing)

<br />

<!-- Add a demo GIF here for maximum impact -->
<!-- ![Tamil Translate Demo](docs/demo.gif) -->

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   📄 Scanned PDF  ──▶  🔍 OCR  ──▶  🌐 Translate  ──▶  📑 PDF   │
│   (Sanskrit/Hindi)    (PaddleOCR)   (Sarvam AI)     (EN + TA)   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

</div>

---

## Why Tamil Translate?

Translating religious and classical texts from Sanskrit to Tamil is challenging. Direct translation produces poor results (BLEU score: 8.03). **Tamil Translate solves this** with an intelligent two-step approach: Sanskrit → English → Tamil, dramatically improving translation quality.

| Challenge | Our Solution |
|-----------|-------------|
| Low-quality OCR on scanned texts | PaddleOCR with adaptive preprocessing |
| Poor Sanskrit→Tamil translation | Two-step translation via English |
| Lost progress on large documents | Checksum-based resume capability |
| High API costs | Smart chunking & cost estimation |

---

## ✨ Features

<table>
<tr>
<td width="50%">

### Core Capabilities

- **High-Accuracy OCR** — PaddleOCR with adaptive preprocessing for Devanagari
- **Smart Translation** — Two-step Sanskrit→English→Tamil for best quality
- **Resume Support** — Never lose progress on large documents
- **Cost Control** — Real-time estimation and tracking

</td>
<td width="50%">

### Developer Experience

- **Beautiful TUI** — Full-featured terminal interface
- **Powerful CLI** — Scriptable command-line interface
- **Python API** — Integrate into your own applications
- **State Persistence** — Atomic writes after each page

</td>
</tr>
</table>

### Interactive Terminal UI

```
tamil-translate     # Launch the TUI
```

The TUI provides:
- 📊 **Dashboard** — Recent files, resume options, quick actions
- 📁 **File Browser** — Navigate and select PDFs visually
- ⚙️ **Settings** — Configure workers, chunk size, DPI
- 📜 **History** — Track all your translation sessions
- 📈 **Live Progress** — Real-time status with cost tracking

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- [Sarvam AI API key](https://dashboard.sarvam.ai) (includes ₹1,000 free credits)

### Installation

```bash
# Clone the repository
git clone https://github.com/SangeethsivanSivakumar/Tamil-Translate.git
cd Tamil-Translate

# Install the package
pip install -e .

# Download required fonts
python3 scripts/download_fonts.py

# Set your API key
export SARVAM_API_KEY='your-api-key'
```

### Your First Translation

```bash
# Launch interactive TUI
tamil-translate

# Or use CLI directly
tamil-translate document.pdf --pages 1-10
```

<details>
<summary><strong>More CLI Examples</strong></summary>

```bash
# Translate entire document
tamil-translate document.pdf --pages all

# Estimate cost before processing
tamil-translate document.pdf --dry-run --pages all

# Resume interrupted translation
tamil-translate document.pdf --resume

# High quality OCR (slower)
tamil-translate document.pdf --dpi 400

# Adjust chunk size to prevent translation loops
tamil-translate document.pdf --chunk-size 500
```

</details>

---

## 📖 How It Works

```
                    ┌──────────────────┐
                    │   Input PDF      │
                    │ (Scanned images) │
                    └────────┬─────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     OCR EXTRACTION                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ Adaptive    │───▶│  PaddleOCR  │───▶│ Confidence  │     │
│  │ Preprocess  │    │  Sanskrit   │    │  Scoring    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      TRANSLATION                            │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  Sanskrit   │───▶│   English   │───▶│    Tamil    │     │
│  │   (OCR)     │    │ (Sarvam AI) │    │ (Sarvam AI) │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     PDF GENERATION                          │
│  ┌─────────────────────┐    ┌─────────────────────┐        │
│  │   english/          │    │   tamil/            │        │
│  │   document_en.pdf   │    │   document_ta.pdf   │        │
│  └─────────────────────┘    └─────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Translation Quality Comparison

| Source | Target | Method | BLEU Score |
|--------|--------|--------|------------|
| Sanskrit | English | Direct | 25.56 |
| Hindi | English | Direct | 32.15 |
| Sanskrit | Tamil | Direct | 8.03 |
| Sanskrit | Tamil | **Two-step (via English)** | **Significantly Better** |

---

## 💰 Pricing

**Sarvam AI**: ₹20 per 10,000 characters | **Free Credits**: ₹1,000 included

<details>
<summary><strong>Cost Example: 300-page Document</strong></summary>

Assuming ~3,000 characters per page:

| Translation | Cost |
|-------------|------|
| English translation | ₹1,800 |
| Tamil translation (two-step) | ₹3,600 |
| **Total** | **₹5,400** (~$65 USD) |
| With free credits | ₹4,400 (~$53 USD) |

Use `--dry-run` to estimate costs before processing.

</details>

---

## 🛠️ Configuration

### CLI Options

```
tamil-translate [OPTIONS] INPUT_PDF

Options:
  --pages RANGE      Page range: "1-50", "all" (default: "1-10")
  --output DIR       Output directory (default: ./output)
  --workers N        Concurrent workers (default: 5)
  --dpi N            OCR resolution 150-600 (default: 400)
  --chunk-size N     Characters per chunk 100-2000 (default: 800)
  --dry-run          Estimate cost only
  --resume           Resume previous run (default)
  --no-resume        Start fresh
  --no-preprocess    Skip image preprocessing
  --check-fonts      Verify font installation
  -v, --verbose      Enable debug logging
```

### Environment Variables

```bash
export SARVAM_API_KEY='your-api-key'      # Required
export MAX_WORKERS=5                       # Concurrent workers
export MAX_CHUNK_SIZE=800                  # Characters per chunk
export OCR_DPI=400                         # PDF render resolution
```

### Python API

```python
from tamil_translate import TranslationPipeline

pipeline = TranslationPipeline()
result = pipeline.run(
    pdf_path="document.pdf",
    page_range=(1, 50),
    resume=True,
)

print(f"Pages: {result.pages_processed}")
print(f"Cost: ₹{result.total_cost_inr:.2f}")
print(f"English: {result.english_pdf_path}")
print(f"Tamil: {result.tamil_pdf_path}")
```

---

## 🏗️ Project Structure

```
tamil-translate/
├── src/tamil_translate/
│   ├── cli.py              # Command-line interface
│   ├── config.py           # Configuration management
│   ├── ocr_engine.py       # PaddleOCR integration
│   ├── translator.py       # Sarvam AI translation
│   ├── pdf_generator.py    # PDF creation with Unicode fonts
│   ├── state_manager.py    # Resume capability
│   ├── pipeline.py         # Main orchestration
│   ├── security.py         # Input validation
│   └── tui/                # Terminal UI
│       ├── app.py          # Main TUI application
│       ├── styles.tcss     # TUI styling
│       └── screens/        # TUI screens
├── scripts/
│   └── download_fonts.py   # Font installer
├── output/                 # Generated PDFs
│   ├── english/
│   ├── tamil/
│   └── .state/            # Resume state files
└── Documentations/        # API reference
```

---

## 🐛 Troubleshooting

<details>
<summary><strong>Missing Fonts</strong></summary>

```bash
tamil-translate --check-fonts
python3 scripts/download_fonts.py
```

</details>

<details>
<summary><strong>API Key Issues</strong></summary>

- Verify: `echo $SARVAM_API_KEY`
- Key must be 32+ characters
- Get a key: [dashboard.sarvam.ai](https://dashboard.sarvam.ai)

</details>

<details>
<summary><strong>Resume Not Working</strong></summary>

- State files: `output/.state/*.json`
- Clear with `--no-resume` flag
- Checksum mismatch = PDF was modified

</details>

<details>
<summary><strong>Poor Translation Quality</strong></summary>

- Check OCR confidence in state files
- Try higher DPI: `--dpi 400`
- Use smaller chunks: `--chunk-size 500`

</details>

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [CLAUDE.md](CLAUDE.md) | Architecture & development guide |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines |
| [Documentations/](Documentations/) | Sarvam AI API reference |

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) to get started.

### Development Setup

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/
```

### Roadmap

- [ ] Comprehensive test suite
- [ ] Additional language pairs
- [ ] Docker containerization
- [ ] Batch processing optimization
- [ ] GPU acceleration for OCR

---

## 🙏 Acknowledgments

- **[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)** — Powerful multilingual OCR
- **[Sarvam AI](https://sarvam.ai)** — High-quality Indic language translation
- **[Textual](https://textual.textualize.io/)** — Beautiful terminal UI framework
- **[fpdf2](https://py-pdf.github.io/fpdf2/)** — PDF generation library

---

<div align="center">

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

**Built with care for preserving and translating Sanskrit religious texts**

<br />

[⬆ Back to Top](#tamil-translate)

<br />

If you find this useful, please consider giving it a ⭐

[![GitHub stars](https://img.shields.io/github/stars/SangeethsivanSivakumar/Tamil-Translate?style=social)](https://github.com/SangeethsivanSivakumar/Tamil-Translate)

</div>
