# pygrad

Build searchable knowledge graphs from Python repository documentation using Graph RAG.

[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://aalexuser.github.io/pygrad/)
[![License](https://img.shields.io/badge/license-BSD%203--Clause-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)

## Installation

```bash
pip install git+https://github.com/AaLexUser/pygrad.git
```

## Quick Start

```python
import asyncio
import pygrad as pg

async def main():
    # Add a repository to the knowledge graph
    await pg.add("https://github.com/psf/requests")

    # Search the knowledge graph
    result = await pg.search(
        "https://github.com/psf/requests",
        "How do I make a POST request with JSON data?"
    )
    print(result)

    # List all indexed repositories
    datasets = await pg.list()
    for ds in datasets:
        print(f"  - {ds.name}")

    # Visualize the knowledge graph
    await pg.visualize("./graph.html")

    # Delete a repository
    await pg.delete("https://github.com/psf/requests")

asyncio.run(main())
```

### CLI Usage

```bash
# Add a repository
pygrad add https://github.com/owner/repo

# Search the knowledge graph
pygrad ask https://github.com/owner/repo "How do I authenticate?"

# List indexed repositories
pygrad list

# Visualize the graph
pygrad visualize -o ./graph.html

# Delete a repository
pygrad delete https://github.com/owner/repo
```

## Features

- **Graph RAG Search**: Semantic search powered by knowledge graphs
- **Automatic API Extraction**: Parses classes, functions, methods, and docstrings
- **Usage Example Mining**: Finds real examples from tests and documentation
- **Local LLM Support**: Works with Ollama for fully offline operation
- **Tree-sitter Parsing**: Fast and accurate Python code analysis

## How It Works

```
Repository → Parse (TreeSitter) → Extract API → Build Graph → Search (RAG)
```

1. **Clone**: Downloads the repository
2. **Parse**: Uses TreeSitter to extract code structure
3. **Extract**: Identifies classes, functions, docstrings, and examples
4. **Index**: Builds a knowledge graph with Cognee
5. **Search**: Enables natural language queries over the codebase

## API Reference

### Core Functions

| Function | Description |
|----------|-------------|
| `pg.add(url)` | Add a repository to the knowledge graph |
| `pg.search(url, query)` | Search with natural language |
| `pg.list()` | List all indexed datasets |
| `pg.delete(url)` | Remove a repository |
| `pg.visualize(path)` | Export graph as HTML |
| `pg.get_dataset(name)` | Get dataset by name |

## Configuration

Pygrad uses environment variables for configuration:

### Ollama (Local LLM)

```bash
# LLM
LLM_PROVIDER="ollama"
LLM_MODEL="qwen3-coder:30b"
LLM_ENDPOINT="http://localhost:11434/v1"

# Embeddings
EMBEDDING_PROVIDER="ollama"
EMBEDDING_MODEL="embeddinggemma:latest"
EMBEDDING_ENDPOINT="http://localhost:11434/api/embed"
EMBEDDING_DIMENSIONS="768"
```

### OpenAI

```bash
LLM_PROVIDER="openai"
LLM_API_KEY="sk-..."
LLM_MODEL="gpt-4o"

EMBEDDING_PROVIDER="openai"
EMBEDDING_MODEL="text-embedding-3-small"
```

### Database (Production)

```bash
# PostgreSQL + pgvector
VECTOR_DB_PROVIDER="pgvector"
DB_PROVIDER="postgres"
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="cognee_db"
DB_USERNAME="cognee"
DB_PASSWORD="cognee"

# Neo4j (optional)
GRAPH_DATABASE_PROVIDER="neo4j"
GRAPH_DATABASE_URL="bolt://localhost:7687"
```

See the [Configuration Guide](https://aalexuser.github.io/pygrad/configuration/) for more options.

## Development

```bash
# Clone
git clone https://github.com/AaLexUser/pygrad
cd pygrad

# Install
pip install -e ".[dev]"

# Test
pytest tests/ -v

# Docs
pip install -e ".[docs]"
mkdocs serve
```

## Documentation

Full documentation is available at [aalexuser.github.io/pygrad](https://aalexuser.github.io/pygrad/).

- [Getting Started](https://aalexuser.github.io/pygrad/getting-started/)
- [Examples](https://aalexuser.github.io/pygrad/examples/)
- [Architecture](https://aalexuser.github.io/pygrad/architecture/)
- [API Reference](https://aalexuser.github.io/pygrad/api/)

## License

BSD 3-Clause License
