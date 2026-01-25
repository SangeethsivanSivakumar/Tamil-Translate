# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **PDF Translation System** for Sanskrit and Hindi religious texts (Vidyamadhaviyam). The project translates scanned PDFs containing Devanagari script to English and Tamil using:
- **PaddleOCR PP-OCRv5** for OCR extraction
- **Sarvam AI Translation API** for translation
- Python-based pipeline (no code yet - planning phase only)

**Source Documents**: 3 PDFs in `./Pdfs/` (~75MB total):
- Religious/philosophical content in Sanskrit (Devanagari script) and Hindi
- Scanned images (not searchable PDFs)

**Target Outputs**: 2 translated PDFs per input (English + Tamil)

## Current Project Status

**Phase: Planning Complete** ✅

The project is currently in the planning stage with NO implementation code yet. All work exists as:
- Comprehensive enhanced plan (`.claude/plans/feat-sanskrit-hindi-pdf-translation-system-ENHANCED.md`)
- Sarvam AI API documentation (`Documentations/`)

## Key Architectural Decisions from Plan

### API Configuration
**Model**: `sarvam-translate:v1` (NOT Mayura)
- Character limit: 2000 chars/request (chunk at 1800 for safety)
- Supports Sanskrit (`sa-IN`), English (`en-IN`), Tamil (`ta-IN`)
- Mode: `formal` only (appropriate for religious texts)
- Numerals format: `native` recommended for cultural authenticity

**Language Codes**:
```python
{
    "sanskrit": "sa-IN",
    "english": "en-IN",
    "tamil": "ta-IN",
    "hindi": "hi-IN"
}
```

### Implementation Strategy

**Recommended Hybrid Approach**:
1. **Phase 1 (MVP - 2 days)**: Use official `sarvamai` SDK with tutorial pattern
   - Sequential chunk translation
   - Basic error handling
   - Validate on 10-page test

2. **Phase 2 (Optimization - 1.5 days)**: Add production features
   - AsyncIO wrapper (10 concurrent requests → 10x speedup)
   - Tiered caching (30% cost savings)
   - Circuit breaker pattern

**Performance Targets**:
- OCR: <5 seconds/page
- Translation: <2 seconds/page (with AsyncIO)
- Memory: <1GB peak (streaming page extraction)

### Security Requirements (BLOCKING)

Before any code implementation:
1. **NO hardcoded API keys** - use environment variables only
2. **PDF validation**: size limits, MIME type checks, header validation
3. **Path traversal protection**: restrict to `./Pdfs/` directory
4. **Add to `.gitignore`**: `.env`, `*.env` files

### Text Chunking Pattern

From official Sarvam AI tutorial (MUST use this approach):
```python
def chunk_text(text, max_length=1800):
    """Splits at word boundaries, preserves context."""
    chunks = []
    while len(text) > max_length:
        split_index = text.rfind(" ", 0, max_length)  # Last space
        if split_index == -1:
            split_index = max_length
        chunks.append(text[:split_index].strip())
        text = text[split_index:].lstrip()
    if text:
        chunks.append(text.strip())
    return chunks
```

### Critical API Error Codes

Handle these explicitly (from tutorial):
- **403**: `invalid_api_key_error` → Verify API key
- **429**: `insufficient_quota_error` → Exponential backoff
- **500**: `internal_server_error` → Retry with backoff
- **400**: `invalid_request_error` → Check request structure

### Data Integrity Requirements

1. **Unicode Normalization**: Apply NFC normalization after OCR to prevent Devanagari character corruption
2. **Chunking Validation**: Verify no data loss when splitting text
3. **Atomic State Writes**: Use temp files + atomic rename to prevent corruption
4. **OCR Confidence**: Minimum 80% confidence threshold

## Cost Estimates

**For 300 pages**:
- Without caching: ₹3,600 (~$43 USD)
- With 30% cache savings: ₹2,520 (~$30 USD)
- Free credits: ₹1,000 (covers ~30-40 pages for testing)

**Pricing**: ₹20 per 10,000 characters

## Quality Expectations (BLEU Scores)

- **Sanskrit → English**: 25.56 (moderate quality)
- **Hindi → English**: 32.15 (good quality)
- **Sanskrit/Hindi → Tamil**: 8.03 ⚠️ **(LOW - plan for manual review)**

## When Starting Implementation

### Installation Commands
```bash
pip install -Uqq sarvamai
pip install paddleocr
pip install reportlab
pip install PyPDF2
pip install python-magic
pip install aiohttp
```

### Development Workflow
1. Set up virtual environment
2. Create `.gitignore` with `.env` BEFORE first commit
3. Get API key from https://dashboard.sarvam.ai/
4. Start with 10-page test run to validate quality and cost
5. Review Tamil output quality before full run

## Important Files

**Enhanced Plan**: `.claude/plans/feat-sanskrit-hindi-pdf-translation-system-ENHANCED.md`
- Complete security enhancements
- Performance optimizations
- AsyncIO implementation patterns
- Error handling strategies
- Official tutorial integration

**API Documentation**: `Documentations/`
- `Translate Tutorial.md` - Official Sarvam AI tutorial with examples
- `Overview.md` - Model comparison (Mayura vs Sarvam-Translate)
- `Translation API.md` - Complete API reference

**Source PDFs**: `Pdfs/`
- 3 Vidyamadhaviyam texts (10MB, 49MB, 16MB)
- DO NOT commit large PDFs to git

## Key Risks & Mitigations

1. **Tamil Translation Quality**: BLEU 8.03 indicates low quality
   - Mitigation: Budget for manual review OR use 2-step translation (Sanskrit→English→Tamil)

2. **Memory Exhaustion**: 49MB PDF → 14GB without streaming
   - Mitigation: Use generator pattern for page extraction

3. **API Rate Limiting**: No documented limits
   - Mitigation: Conservative 10 req/sec with circuit breaker + exponential backoff

## Architecture Pattern

```
PDF Input (Streaming)
    ↓
OCR (PaddleOCR PP-OCRv5)
    ↓ Unicode Normalization (NFC)
Validation (>80% confidence)
    ↓
Text Chunking (1800 chars, word boundaries)
    ↓
Translation (AsyncIO, 10 concurrent)
    ↓ Tiered Cache (Memory + SQLite)
PDF Generation (ReportLab + Unicode fonts)
    ↓
Output PDFs (English + Tamil)
```

## Development Principles

1. **Security First**: Validate all inputs, protect API keys, prevent path traversal
2. **Data Integrity**: Unicode normalization, chunking validation, atomic writes
3. **Performance**: Streaming for memory, AsyncIO for speed, caching for cost
4. **Quality Control**: OCR confidence checks, manual review process for Tamil output

## Next Steps for Implementation

1. Review enhanced plan with stakeholders
2. Obtain Sarvam AI API key
3. Set up git repository with security hooks
4. Begin Phase 1 (MVP) with security-first approach
5. Run 10-page test to validate assumptions
6. Decide on Tamil translation approach based on results
