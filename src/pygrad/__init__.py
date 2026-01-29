"""Pygrad - Graph RAG API Doc library.

Build searchable knowledge graphs from Python repository documentation.

Usage:
    import pygrad as pg

    # Add a repository to the knowledge graph
    await pg.add("https://github.com/owner/repo")

    # List all indexed repositories
    datasets = await pg.list()

    # Search the knowledge graph
    result = await pg.search("https://github.com/owner/repo", "How to use X?")

    # Delete a repository
    await pg.delete("https://github.com/owner/repo")
"""

from pygrad.core import (
    add,
    search,
    delete,
    list,
    list_datasets,
    visualize,
    get_dataset,
)
from pygrad.repository import clone_repository, get_repository_id
from pygrad.processor.processor import (
    ClassInfo,
    FunctionInfo,
    PythonRepositoryProcessor,
    process_repository,
)
from pygrad.parser.treesitter import RepoTreeSitter
from pygrad.config import PYGRAD_HOME, REPO_STORAGE

__version__ = "0.1.0"

__all__ = [
    # Numpy-style API (primary)
    "add",
    "search",
    "delete",
    "list",
    "list_datasets",
    "visualize",
    "get_dataset",
    # Repository utilities
    "clone_repository",
    "get_repository_id",
    # Processor
    "ClassInfo",
    "FunctionInfo",
    "PythonRepositoryProcessor",
    "process_repository",
    # Parser
    "RepoTreeSitter",
    # Configuration
    "PYGRAD_HOME",
    "REPO_STORAGE",
    "__version__",
]
