# Contributing to Pygrad

Thank you for your interest in contributing to pygrad!

## Development Setup

### Prerequisites

- Python 3.10+
- Git
- Ollama (for local LLM testing)

### Installation

```bash
# Clone the repository
git clone https://github.com/AaLexUser/pygrad
cd pygrad

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev,docs]"
```

### Environment Setup

Create a `.env` file for local development:

```bash
LLM_PROVIDER="ollama"
LLM_MODEL="qwen3-coder:30b"
LLM_ENDPOINT="http://localhost:11434/v1"

EMBEDDING_PROVIDER="ollama"
EMBEDDING_MODEL="embeddinggemma:latest"
EMBEDDING_ENDPOINT="http://localhost:11434/api/embed"
EMBEDDING_DIMENSIONS="768"

TELEMETRY_DISABLED=true
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_processor.py -v

# Run with coverage
pytest tests/ --cov=pygrad --cov-report=html
```

## Code Style

We follow standard Python conventions:

- Use type hints for all function signatures
- Write docstrings in Google style
- Keep lines under 88 characters (Black default)
- Use meaningful variable names

### Formatting

```bash
# Format code (if you have black/ruff installed)
black src/pygrad tests/
ruff check src/pygrad tests/ --fix
```

## Documentation

### Building Docs Locally

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Serve docs locally
mkdocs serve

# Build docs
mkdocs build
```

### Writing Documentation

- Documentation lives in `docs/`
- Use Markdown with MkDocs Material extensions
- Include code examples that can be copy-pasted
- Add Mermaid diagrams for architecture explanations

## Pull Request Process

1. **Fork the repository** and create your branch from `main`

2. **Write tests** for new functionality

3. **Update documentation** if you're changing the API

4. **Run tests** to ensure they pass:
   ```bash
   pytest tests/ -v
   ```

5. **Create a Pull Request** with a clear description of changes

### PR Title Convention

Use conventional commit style:

- `feat: add new feature`
- `fix: resolve bug in X`
- `docs: update API documentation`
- `refactor: improve code structure`
- `test: add tests for X`

## Project Structure

```
pygrad/
├── src/pygrad/
│   ├── __init__.py      # Public API exports
│   ├── core.py          # Main API functions
│   ├── cli.py           # CLI entry point
│   ├── config.py        # Configuration
│   ├── repository.py    # Git operations
│   ├── xmlapi.py        # XML parsing
│   ├── prompt_store.py  # Prompt management
│   ├── processor/       # Code processing
│   │   ├── __init__.py
│   │   └── processor.py
│   └── parser/          # TreeSitter parsing
│       ├── __init__.py
│       └── treesitter.py
├── tests/               # Test files
├── docs/                # Documentation
└── pyproject.toml       # Project configuration
```

## Adding New Features

### Adding a New API Function

1. Add the function to `src/pygrad/core.py`
2. Export it from `src/pygrad/__init__.py`
3. Add CLI support in `src/pygrad/cli.py` (if applicable)
4. Write tests in `tests/`
5. Document in `docs/api/core.md`

### Adding a New CLI Command

1. Add the command parser in `src/pygrad/cli.py`
2. Implement the handler using module functions
3. Add tests
4. Document in `docs/examples/cli-usage.md`

## Getting Help

- Open an issue for bugs or feature requests
- Check existing issues before creating new ones
- Be respectful and constructive in discussions

## License

By contributing, you agree that your contributions will be licensed under the BSD 3-Clause License.
