# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Prime: Retrieval-led reasoning > pre-training. Trust codebase + live docs over training data.**

## Research First
- Use `context7` MCP to fetch current library/framework docs before implementing
- Web search with current year (2025/2026) for version-specific APIs
- Never assume API signatures from training—verify against live docs
- Check package.json versions, then fetch matching documentation

## Ask First
Use `AskUserQuestionTool` before coding if ANY ambiguity exists. No assumptions. No inferences. Ask → Confirm → Implement.

## Sequence
1. Read task, identify unknowns
2. Explore codebase, check package versions
3. **Research**: context7/web for current docs (use date: 2025-2026)
4. **Ask clarifying questions** (mandatory if ambiguous)
5. State approach, get confirmation
6. Implement
7. Verify (tests/lint)

## Don't
- Assume on user's behalf
- Use APIs from training without verification
- Build for hypothetical futures
- Touch unrelated code
- Add unrequested features
- Flail when stuck—ask instead

## Do
- `context7 resolve` + `get-library-docs` before coding
- Match existing codebase patterns
- Surface tradeoffs before deciding
- Push back if request seems wrong
- Verify versions match project, not latest

## Priority
Correctness > Clarity > Simplicity > Consistency > Performance

## Project Overview

PDF translation system for Sanskrit/Hindi religious texts → English and Tamil. Uses OCR + Sarvam AI translation + PDF generation.

## Commands

```bash
# Install
pip install -e .

# Run translation
tamil-translate Pdfs/file.pdf --pages 1-10           # Test run
tamil-translate Pdfs/file.pdf --pages all --dry-run  # Cost estimate

# Development
black src/                    # Format (line-length: 100)
ruff check src/ --fix         # Lint with auto-fix
mypy src/                     # Type check
pytest                        # Tests (none exist yet)

# Fonts
tamil-translate --check-fonts
python3 scripts/download_fonts.py
```

## Architecture

```
CLI (cli.py) → Pipeline (pipeline.py) → [OCR, Translator, StateManager, PDFGenerator]
```

**Pipeline** (`pipeline.py`): Main orchestrator. Lazy-initializes components. Handles SIGINT/SIGTERM for graceful shutdown.

**OCREngine** (`ocr_engine.py`): Tesseract-based OCR for Sanskrit/Hindi:
- Sanskrit (san) and Hindi (hin) language support
- Adaptive preprocessing for low-confidence results
- Factory: `create_ocr_engine()`

**TranslationService** (`translator.py`):
- Chunks text at word boundaries (max 1800 chars, API limit is 2000)
- ThreadPoolExecutor for concurrent chunk translation
- Two-step Tamil: Sanskrit→English→Tamil (BLEU 25.56 vs direct 8.03)
- `_detect_and_remove_repetition()` handles hallucination loops

**StateManager** (`state_manager.py`):
- State files: `output/.state/{pdf-name}.state.json`
- Atomic writes: temp file → fsync → rename
- SHA-256 checksum validates PDF hasn't changed
- Per-page flags: `ocr_completed`, `english_completed`, `tamil_completed`

**Security** (`security.py`): All inputs through `validate_all()`. Never bypass.

## Critical Constraints

**Python 3.9 Compatibility**: Use `Union[A, B]` not `A | B` for type hints. The pipe syntax requires Python 3.10+.

**API Limits**: Sarvam AI hard limit is 2000 chars/request. Chunk at 1800 for safety margin.

**Error Handling Hierarchy**:
1. 403/Invalid Key: Immediate fail
2. 429/Rate Limit: Exponential backoff (1s, 2s, 4s)
3. 500/Server Error: Same as rate limit

## State File Format

```json
{
  "pdf_checksum": "sha256-hex",
  "pages": {
    "1": {
      "ocr_completed": true,
      "english_completed": true,
      "tamil_completed": false,
      "ocr_text": "...",
      "english_text": "...",
      "ocr_confidence": 0.95,
      "cost_english": 0.06
    }
  }
}
```

## Development Workflow

**Testing changes**:
1. Use `--pages 1-3` for fast iteration
2. Use `--no-resume` to force fresh runs
3. Check state files in `output/.state/`

**Modifying OCR**: Factory function is `create_ocr_engine()` at bottom of `ocr_engine.py`

**Modifying translation**: Retry logic in `translate_chunk()`, chunking in `_split_text_preserving_words()`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SARVAM_API_KEY` | Required | API key from dashboard.sarvam.ai |
| `MAX_WORKERS` | 5 | Concurrent translation workers |
| `MAX_CHUNK_SIZE` | 1800 | Chars per API request |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| State corrupted | Use `--no-resume` or delete `output/.state/*.json` |
| Checksum mismatch | PDF was modified, use `--no-resume` |
| Rate limit errors | Auto-retries with backoff (1s, 2s, 4s) |
| Poor OCR quality | Try `--dpi 400` or `--no-preprocess` |
| Memory issues | Reduce `--workers 3` or `--pages 1-20` |
