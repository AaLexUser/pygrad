"""Processor module for generating API documentation."""

from pygrad.processor.processor import (
    ClassInfo,
    FunctionInfo,
    PythonRepositoryProcessor,
    process_repository,
)
from pygrad.processor.example_extractor import (
    APIUsageGroup,
    ExampleExtractor,
    UsageExample,
    extract_examples_from_repository,
)
from pygrad.processor.utils import extract_test_example_paths, extract_important_api

__all__ = [
    "ClassInfo",
    "FunctionInfo",
    "PythonRepositoryProcessor",
    "process_repository",
    "APIUsageGroup",
    "ExampleExtractor",
    "UsageExample",
    "extract_examples_from_repository",
    "extract_test_example_paths",
    "extract_important_api",
]
