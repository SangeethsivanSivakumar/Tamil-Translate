# Contributing to Tamil Translate

First off, thank you for considering contributing to Tamil Translate! 🎉

This document provides guidelines for contributing to the project. Following these guidelines helps maintain code quality and makes the contribution process smooth for everyone.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## Code of Conduct

This project adheres to the Contributor Covenant [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the behavior
- **Expected vs actual behavior**
- **Environment details** (Python version, OS, package versions)
- **Error messages** and stack traces
- **Sample input files** (if applicable and shareable)

### 💡 Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide detailed description** of the proposed feature
- **Explain why this enhancement would be useful** to most users
- **List similar features** in other tools (if applicable)

### 📝 Code Contributions

1. **Fork the repository** and create a branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** if applicable (we're building test coverage)
4. **Update documentation** if needed
5. **Ensure all checks pass** (formatting, linting, type checking)
6. **Submit a pull request**

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Tamil-Translate.git
cd Tamil-Translate

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Download fonts (if needed)
python3 scripts/download_fonts.py

# Set up API key for testing
export SARVAM_API_KEY='your-test-api-key'
```

### Running Code Quality Checks

```bash
# Format code (automatic fixes)
black src/

# Check linting
ruff check src/

# Type checking
mypy src/

# Run tests (when available)
pytest

# Run all checks at once
black src/ && ruff check src/ && mypy src/
```

## Coding Standards

### Python Style

- **PEP 8** compliance with modifications
- **Line length**: 100 characters (Black default)
- **Type hints**: Required for all functions (Python 3.9+ syntax)
- **Docstrings**: Required for all public modules, classes, and functions

### Code Format

```python
"""Module docstring explaining purpose."""

from typing import Optional
import logging

logger = logging.getLogger(__name__)


def example_function(text: str, count: Optional[int] = None) -> dict:
    """
    Brief description of what the function does.

    Args:
        text: Description of text parameter
        count: Optional description

    Returns:
        Dictionary containing results

    Raises:
        ValueError: When text is empty
    """
    if not text:
        raise ValueError("Text cannot be empty")

    return {"text": text, "count": count or 0}
```

### Architecture Principles

1. **Security First**: Always validate inputs in `security.py`
2. **Atomic Operations**: Use temp + rename for file writes
3. **Resume Capability**: Update state after each page
4. **Error Handling**: Specific exceptions with helpful messages
5. **Logging**: Use appropriate levels (DEBUG, INFO, WARNING, ERROR)

### Key Areas for Contribution

#### High Priority
- **Test Coverage**: Add pytest tests for all modules
- **Documentation**: Improve docstrings and examples
- **Error Messages**: Make errors more user-friendly

#### Medium Priority
- **Performance**: Optimize chunking and translation logic
- **Additional OCR Backends**: Tesseract integration
- **Language Support**: Add more language pairs

#### Low Priority
- **GUI**: Desktop/web interface
- **Docker**: Container deployment
- **CI/CD**: GitHub Actions workflows

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```bash
feat(translator): add retry logic for rate limit errors

- Implement exponential backoff (1s, 2s, 4s)
- Handle 429 status codes from Sarvam API
- Add tests for retry mechanism

Closes #42
```

```bash
fix(state): prevent corruption on sudden shutdown

- Use atomic file writes (temp + rename)
- Add automatic backup recovery
- Update documentation

Fixes #38
```

### Scope Guidelines

- `cli`: Command-line interface
- `ocr`: OCR engine changes
- `translator`: Translation service
- `state`: State management
- `pdf`: PDF generation
- `security`: Security validation
- `config`: Configuration management
- `docs`: Documentation
- `tests`: Test files

## Pull Request Process

### Before Submitting

1. ✅ Code follows style guidelines (Black, Ruff, mypy pass)
2. ✅ Docstrings are complete and accurate
3. ✅ Tests added/updated (if applicable)
4. ✅ Documentation updated (if needed)
5. ✅ CLAUDE.md updated (if architecture changed)
6. ✅ No secrets or API keys in code
7. ✅ Commit messages follow guidelines

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to break)
- [ ] Documentation update

## Testing
Describe testing performed:
- [ ] Manual testing completed
- [ ] Unit tests added/updated
- [ ] Integration tests pass

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
```

### Review Process

1. **Automated checks** must pass (will be added via GitHub Actions)
2. **Maintainer review** required before merge
3. **Address feedback** in comments
4. **Squash commits** if requested
5. **Maintainer will merge** once approved

### After Your PR is Merged

- Delete your branch (if desired)
- Update your fork from main
- Celebrate! 🎉 You've contributed to open source!

## Reporting Bugs

### Before Reporting

- **Check existing issues** to avoid duplicates
- **Try latest version** - bug may be fixed
- **Read documentation** - might be expected behavior

### Bug Report Template

```markdown
**Describe the bug**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. With input file '...'
3. See error

**Expected behavior**
What you expected to happen

**Actual behavior**
What actually happened

**Environment:**
- OS: [e.g., macOS 13.5, Ubuntu 22.04]
- Python version: [e.g., 3.11.2]
- Package version: [e.g., 0.1.0]
- Installation method: [pip, git clone]

**Additional context**
- Error messages and stack traces
- Relevant log output (`--verbose`)
- Sample input (if shareable)
```

## Suggesting Enhancements

### Enhancement Proposal Template

```markdown
**Is your feature request related to a problem?**
Clear description of the problem

**Describe the solution you'd like**
Clear description of desired behavior

**Describe alternatives you've considered**
Other approaches you've thought about

**Additional context**
- Use cases
- Examples from other tools
- Mockups or diagrams (if helpful)
```

## Development Tips

### Testing Your Changes

```bash
# Test with small page range
tamil-translate test.pdf --pages 1-3 --verbose

# Test dry run
tamil-translate test.pdf --dry-run --pages all

# Test resume capability
tamil-translate test.pdf --pages 1-5
# Interrupt with Ctrl+C
tamil-translate test.pdf --pages 1-5 --resume

# Check fonts
tamil-translate --check-fonts
```

### Debugging

```bash
# Enable verbose logging
tamil-translate input.pdf --verbose

# Check state files
cat output/.state/input.state.json | jq '.'

# Validate API key
python -c "from tamil_translate.security import load_api_key_securely; print(load_api_key_securely())"
```

### Understanding the Codebase

Start with these files:
1. `CLAUDE.md` - Architecture overview
2. `pipeline.py` - Main workflow
3. `translator.py` - Translation logic
4. `state_manager.py` - Resume capability

## Questions?

- **Documentation**: Check [CLAUDE.md](CLAUDE.md) for architecture details
- **Issues**: Search existing GitHub issues
- **Contact**: Open a GitHub issue for questions

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- Release notes (for significant contributions)
- Project README (for major features)

---

Thank you for contributing to Tamil Translate! 🙏

Your contributions help preserve and translate important cultural and religious texts.
