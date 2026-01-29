"""Pygrad - Graph RAG API Doc library for building searchable knowledge graphs."""

from __future__ import annotations

from pathlib import Path
from typing import Any, List

import cognee
from cognee.api.v1.visualize.visualize import visualize_graph
from cognee.modules.engine.operations.setup import setup

from pygrad.config import REPO_STORAGE, ensure_storage_exists
from pygrad.repository import clone_repository, get_repository_id
from pygrad.xmlapi import extract_entities
from pygrad.processor.processor import process_repository
from pygrad.prompt_store import prompt_store


async def add(url: str) -> None:
    """Add a repository to the knowledge graph.

    This function clones the repository (if not already cached), parses all Python
    files using TreeSitter, extracts API documentation, and indexes it into the
    knowledge graph.

    Args:
        url: GitHub repository URL (e.g., https://github.com/owner/repo)

    Example:
        >>> import pygrad as pg
        >>> await pg.add("https://github.com/psf/requests")
    """
    await setup()
    xml_api_path = await _create_xml_api_doc(url)
    await _cognee_add_xml_api(xml_api_path, get_repository_id(url))


async def search(url: str, query: str) -> str:
    """Search a repository's knowledge graph using natural language.

    Uses Graph RAG (Retrieval Augmented Generation) to search the knowledge graph
    and generate contextual answers based on the indexed API documentation.

    Args:
        url: GitHub repository URL
        query: Natural language query

    Returns:
        Query result as a string

    Example:
        >>> import pygrad as pg
        >>> result = await pg.search(
        ...     "https://github.com/psf/requests",
        ...     "How do I make a POST request with JSON?"
        ... )
        >>> print(result)
    """
    await setup()
    repo_id = get_repository_id(url)
    dataset = await get_dataset(repo_id)

    if not dataset:
        return "The library is not yet indexed."

    system_prompt = prompt_store.load("grad.md")
    result = await cognee.search(
        query_text=query,
        dataset_ids=[dataset.id],
        query_type=cognee.SearchType.GRAPH_COMPLETION_CONTEXT_EXTENSION,
        system_prompt=system_prompt,
    )

    if isinstance(result, builtins_list):
        if not result:
            return "No results found."
        return "\n".join(
            str(item.get("search_result", ["No results found."])[0])  # type: ignore[union-attr]
            for item in result
        )
    if result and hasattr(result, "result") and result.result:
        return str(result.result)
    return "No results found."


async def visualize(path: str = "./pygrad.html") -> str:
    """Export the knowledge graph as an interactive HTML visualization.

    Args:
        path: Output file path (default: "./pygrad.html")

    Returns:
        Path to the generated HTML file

    Example:
        >>> import pygrad as pg
        >>> await pg.visualize("./knowledge-graph.html")
    """
    await setup()
    await visualize_graph(path)
    return path


async def get_dataset(dataset_name: str, default: Any = None) -> Any:
    """Get a dataset by name.

    Args:
        dataset_name: Name of the dataset (repository ID)
        default: Default value if dataset not found

    Returns:
        Dataset object or default if not found

    Example:
        >>> import pygrad as pg
        >>> from pygrad import get_repository_id
        >>> repo_id = get_repository_id("https://github.com/owner/repo")
        >>> dataset = await pg.get_dataset(repo_id)
    """
    await setup()
    datasets = await list_datasets()
    for dataset in datasets:
        if dataset.name.lower() == dataset_name.lower():
            return dataset
    return default


async def delete(url: str) -> None:
    """Delete a repository from the knowledge graph.

    This removes the indexed data but does not delete the cached repository files.

    Args:
        url: GitHub repository URL

    Example:
        >>> import pygrad as pg
        >>> await pg.delete("https://github.com/owner/repo")
    """
    await setup()
    dataset = await get_dataset(get_repository_id(url))
    if dataset:
        await cognee.datasets.delete_dataset(dataset.id)


async def list_datasets() -> List[Any]:
    """List all indexed datasets (repositories).

    Returns:
        List of dataset objects with name and id attributes

    Example:
        >>> import pygrad as pg
        >>> datasets = await pg.list()
        >>> for ds in datasets:
        ...     print(ds.name)
    """
    await setup()
    return await cognee.datasets.list_datasets()


# Keep a reference to built-in list for isinstance checks
import builtins

builtins_list = builtins.list

# Alias for numpy-style API (pg.list())
list = list_datasets


async def _create_xml_api_doc(url: str) -> Path:
    """Create XML API documentation for a repository."""
    ensure_storage_exists()
    repo_path = Path(REPO_STORAGE) / get_repository_id(url)
    xml_api_filename = "api.xml"
    xml_api_path = repo_path / xml_api_filename

    if not xml_api_path.exists():
        if not repo_path.exists():
            clone_repository(url, repo_path)
        await process_repository(
            repository_path=str(repo_path),
            output_file=xml_api_filename,
        )
    return xml_api_path


def _split_xml_api(xml_api_path: Path) -> List[str]:
    """Split XML API into documents for indexing."""
    classes, methods, functions, examples = extract_entities(xml_api_path)
    return [*classes, *methods, *functions, *examples]


async def _cognee_add_xml_api(xml_api_path: Path, dataset_name: str) -> None:
    """Add XML API to Cognee knowledge graph."""
    custom_prompt = """
    Extract methods, functions and classes as entities, add their parameters to description.
    Connect classes to methods with the relationship "has_method".
    Connect methods to classes with the relationship "belongs_to".
    Connect examples to methods, classes, and functions that are used in this example with the relationship "is_used".
    """
    documents = _split_xml_api(xml_api_path)
    await cognee.add(
        documents,
        dataset_name=dataset_name,
        preferred_loaders=["text_loader"],
        data_per_batch=1,
    )
    await cognee.cognify(data_per_batch=1, custom_prompt=custom_prompt)
