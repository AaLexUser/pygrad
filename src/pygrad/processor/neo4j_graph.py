"""Neo4j graph converter for Python repository data."""

import hashlib
import json
from typing import TYPE_CHECKING, Any

from neo4j import GraphDatabase

if TYPE_CHECKING:
    from pygrad.processor.processor import ClassInfo, FunctionInfo


class Neo4jGraphConverter:
    """Converts repository data to Neo4j knowledge graph."""

    def __init__(self, uri: str, username: str, password: str, database: str = "neo4j"):
        """Initialize Neo4j connection.

        Args:
            uri: Neo4j connection URI (e.g., "bolt://localhost:7687")
            username: Neo4j username
            password: Neo4j password
            database: Database name (default: "neo4j")
        """
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.database = database

    def close(self) -> None:
        """Close the Neo4j driver connection."""
        self.driver.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def save_repository_graph(
        self,
        classes: list["ClassInfo"],
        functions: list["FunctionInfo"],
        clear_existing: bool = True,
    ) -> dict[str, int]:
        """Save repository data as Neo4j graph.

        Args:
            classes: List of class information
            functions: List of function information
            clear_existing: Whether to clear existing graph data

        Returns:
            Dictionary with counts of created nodes and relationships
        """
        with self.driver.session(database=self.database) as session:
            if clear_existing:
                session.run("MATCH (n) DETACH DELETE n")

            # Create constraints and indexes
            self._create_constraints(session)

            # Track statistics
            stats = {
                "classes": 0,
                "functions": 0,
                "methods": 0,
                "examples": 0,
                "relationships": 0,
            }

            # Create class nodes and their methods
            for class_info in classes:
                self._create_class_node(session, class_info)
                stats["classes"] += 1

                # Create method nodes and relationships
                for method in class_info.methods:
                    self._create_method_node(session, method, class_info.api_path)
                    stats["methods"] += 1
                    stats["relationships"] += 1

                # Create class examples
                for example_json in class_info.usage_examples:
                    example_id = self._create_example_node(session, example_json)
                    if example_id:
                        self._create_example_relationship(
                            session, class_info.api_path, example_id, "Class"
                        )
                        stats["relationships"] += 1

                # Create method examples
                for method in class_info.methods:
                    for example_json in method.usage_examples:
                        example_id = self._create_example_node(session, example_json)
                        if example_id:
                            self._create_example_relationship(
                                session, method.api_path, example_id, "Method"
                            )
                            stats["relationships"] += 1

            # Create function nodes
            for func in functions:
                self._create_function_node(session, func)
                stats["functions"] += 1

                # Create function examples
                for example_json in func.usage_examples:
                    example_id = self._create_example_node(session, example_json)
                    if example_id:
                        self._create_example_relationship(
                            session, func.api_path, example_id, "Function"
                        )
                        stats["relationships"] += 1

            # Count unique examples
            result = session.run("MATCH (e:Example) RETURN count(e) as count")
            stats["examples"] = result.single()["count"]

            return stats

    def _create_constraints(self, session) -> None:
        """Create unique constraints and indexes."""
        constraints = [
            "CREATE CONSTRAINT class_api_path IF NOT EXISTS FOR (c:Class) REQUIRE c.api_path IS UNIQUE",
            "CREATE CONSTRAINT function_api_path IF NOT EXISTS FOR (f:Function) REQUIRE f.api_path IS UNIQUE",
            "CREATE CONSTRAINT method_api_path IF NOT EXISTS FOR (m:Method) REQUIRE m.api_path IS UNIQUE",
            "CREATE CONSTRAINT example_id IF NOT EXISTS FOR (e:Example) REQUIRE e.id IS UNIQUE",
        ]
        for constraint in constraints:
            try:
                session.run(constraint)
            except Exception:
                pass  # Constraint might already exist

    def _create_class_node(self, session, class_info: "ClassInfo") -> None:
        """Create a Class node."""
        query = """
        MERGE (c:Class {api_path: $api_path})
        SET c.name = $name,
            c.description = $description,
            c.init_parameters = $init_parameters,
            c.init_description = $init_description
        """
        session.run(
            query,
            api_path=class_info.api_path,
            name=class_info.name,
            description=class_info.description,
            init_parameters=class_info.initialization.get("parameters", ""),
            init_description=class_info.initialization.get("description", ""),
        )

    def _create_function_node(self, session, func: "FunctionInfo") -> None:
        """Create a Function node."""
        query = """
        MERGE (f:Function {api_path: $api_path})
        SET f.name = $name,
            f.description = $description,
            f.header = $header,
            f.output = $output
        """
        session.run(
            query,
            api_path=func.api_path,
            name=func.name,
            description=func.description,
            header=func.header,
            output=func.output,
        )

    def _create_method_node(
        self, session, method: "FunctionInfo", class_api_path: str
    ) -> None:
        """Create a Method node and link it to its Class."""
        # Create method node
        query = """
        MERGE (m:Method {api_path: $api_path})
        SET m.name = $name,
            m.description = $description,
            m.header = $header,
            m.output = $output
        """
        session.run(
            query,
            api_path=method.api_path,
            name=method.name,
            description=method.description,
            header=method.header,
            output=method.output,
        )

        # Create relationship to class
        relationship_query = """
        MATCH (c:Class {api_path: $class_api_path})
        MATCH (m:Method {api_path: $method_api_path})
        MERGE (c)-[:CONTAINS]->(m)
        """
        session.run(
            relationship_query,
            class_api_path=class_api_path,
            method_api_path=method.api_path,
        )

    def _create_example_node(self, session, example_json: str) -> str | None:
        """Create or merge an Example node, returns example ID."""
        try:
            data = json.loads(example_json)
        except (json.JSONDecodeError, TypeError):
            return None

        # Create unique ID for example
        example_id = self._generate_example_id(data)

        query = """
        MERGE (e:Example {id: $id})
        SET e.source_file = $source_file,
            e.example_type = $example_type,
            e.line = $line,
            e.variable = $variable,
            e.header = $header,
            e.source_code = $source_code
        """
        session.run(
            query,
            id=example_id,
            source_file=data.get("from", ""),
            example_type=data.get("type", ""),
            line=data.get("line"),
            variable=data.get("variable"),
            header=data.get("header"),
            source_code=data.get("source_code", ""),
        )

        return example_id

    def _create_example_relationship(
        self, session, api_path: str, example_id: str, node_type: str
    ) -> None:
        """Create HAS_EXAMPLE relationship between entity and example."""
        query = f"""
        MATCH (n:{node_type} {{api_path: $api_path}})
        MATCH (e:Example {{id: $example_id}})
        MERGE (n)-[:HAS_EXAMPLE]->(e)
        """
        session.run(query, api_path=api_path, example_id=example_id)

    def _generate_example_id(self, example_data: dict[str, Any]) -> str:
        """Generate unique ID for an example based on its content."""
        # Use source file, line, and source code hash for uniqueness
        source_file = example_data.get("from", "")
        line = str(example_data.get("line", ""))
        source_code = example_data.get("source_code", "")

        # Create hash of source code to handle duplicates
        code_hash = hashlib.md5(source_code.encode()).hexdigest()[:8]

        return f"{source_file}:{line}:{code_hash}"
