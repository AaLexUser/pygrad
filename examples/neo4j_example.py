"""Example: Convert repository data to Neo4j graph database.

This example demonstrates how to process a Python repository and save
the extracted API information directly to a Neo4j graph database.

Requirements:
    - Neo4j database running (e.g., via Docker or Neo4j Desktop)
    - neo4j Python driver installed (included in pygrad dependencies)

Usage:
    python examples/neo4j_example.py
"""

import asyncio
import os

from pygrad.processor import process_repository_to_neo4j


async def main():
    # Neo4j connection parameters
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
    NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

    # Repository to process (use current pygrad repository as example)
    repository_path = "/home/stas/.autods/repos/sb-ai-lab/replay"

    print("Processing repository and saving to Neo4j...")
    print(f"Neo4j URI: {NEO4J_URI}")
    print(f"Database: {NEO4J_DATABASE}")
    print(f"Repository: {repository_path}")
    print("-" * 50)

    try:
        stats = await process_repository_to_neo4j(
            repository_path=repository_path,
            neo4j_uri=NEO4J_URI,
            neo4j_username=NEO4J_USERNAME,
            neo4j_password=NEO4J_PASSWORD,
            database=NEO4J_DATABASE,
            clear_existing=True,  # Clear existing data before import
        )

        print("\nGraph creation completed successfully!")
        print(f"Classes created: {stats['classes']}")
        print(f"Functions created: {stats['functions']}")
        print(f"Methods created: {stats['methods']}")
        print(f"Examples created: {stats['examples']}")
        print(f"Relationships created: {stats['relationships']}")

        print("\n" + "=" * 50)
        print("Example Cypher queries to explore the graph:")
        print("=" * 50)

        print("\n1. Get all classes:")
        print("   MATCH (c:Class) RETURN c.name, c.api_path")

        print("\n2. Find classes with their methods:")
        print("   MATCH (c:Class)-[:CONTAINS]->(m:Method)")
        print("   RETURN c.name, collect(m.name) as methods")

        print("\n3. Find examples for a specific class:")
        print("   MATCH (c:Class {name: 'YourClassName'})-[:HAS_EXAMPLE]->(e:Example)")
        print("   RETURN e.source_file, e.line, e.source_code")

        print("\n4. Find all functions with examples:")
        print("   MATCH (f:Function)-[:HAS_EXAMPLE]->(e:Example)")
        print("   RETURN f.name, count(e) as example_count")

        print("\n5. Get the full structure of a class:")
        print("   MATCH (c:Class)-[:CONTAINS]->(m:Method)")
        print("   OPTIONAL MATCH (c)-[:HAS_EXAMPLE]->(ce:Example)")
        print("   OPTIONAL MATCH (m)-[:HAS_EXAMPLE]->(me:Example)")
        print("   RETURN c, m, ce, me")

    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
