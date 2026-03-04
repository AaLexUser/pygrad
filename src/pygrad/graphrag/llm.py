"""LLM implementations for neo4j-graphrag integration."""

import os
from typing import Any, Optional

import httpx
from neo4j_graphrag.llm import LLMInterface


class CustomAPILLM(LLMInterface):
    """Custom LLM implementation for OpenRouter and OpenAI-compatible APIs.

    Implements the neo4j-graphrag LLMInterface for custom API endpoints.
    """

    def __init__(
        self,
        model: str,
        api_key: str,
        endpoint: str,
        temperature: float = 0.0,
        max_tokens: int = 2000,
    ):
        """Initialize CustomAPILLM.

        Args:
            model: Model name/identifier
            api_key: API key for authentication
            endpoint: API endpoint URL
            temperature: Sampling temperature (default: 0.0)
            max_tokens: Maximum tokens in response (default: 2000)
        """
        self.model = model
        self.api_key = api_key
        self.endpoint = endpoint
        self.temperature = temperature
        self.max_tokens = max_tokens

    def invoke(self, input: str) -> str:
        """Synchronous LLM invocation.

        Args:
            input: Input prompt text

        Returns:
            Generated text response
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": input}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(self.endpoint, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"]

    async def ainvoke(self, input: str) -> str:
        """Asynchronous LLM invocation.

        Args:
            input: Input prompt text

        Returns:
            Generated text response
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": input}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self.endpoint, json=payload, headers=headers)

            # Better error handling
            if response.status_code != 200:
                error_detail = response.text
                raise ValueError(f"API Error {response.status_code}: {error_detail}")

            data = response.json()

        return data["choices"][0]["message"]["content"]


def create_llm_from_env() -> LLMInterface:
    """Create LLM instance from environment variables.

    Supports providers: custom, ollama, openai

    Environment variables:
        LLM_PROVIDER: Provider name (custom, ollama, openai)
        LLM_MODEL: Model name
        LLM_API_KEY: API key
        LLM_ENDPOINT: API endpoint URL

    Returns:
        LLMInterface implementation

    Raises:
        ValueError: If required environment variables are missing
        ImportError: If provider-specific package is not installed
    """
    provider = os.getenv("LLM_PROVIDER", "").lower()
    model = os.getenv("LLM_MODEL")
    api_key = os.getenv("LLM_API_KEY")
    endpoint = os.getenv("LLM_ENDPOINT")

    if not provider:
        raise ValueError("LLM_PROVIDER environment variable is required")
    if not model:
        raise ValueError("LLM_MODEL environment variable is required")

    if provider == "custom":
        if not api_key:
            raise ValueError("LLM_API_KEY environment variable is required for custom provider")
        if not endpoint:
            raise ValueError("LLM_ENDPOINT environment variable is required for custom provider")
        return CustomAPILLM(
            model=model,
            api_key=api_key,
            endpoint=endpoint,
        )

    elif provider == "ollama":
        try:
            from neo4j_graphrag.llm import OllamaLLM
        except ImportError:
            raise ImportError(
                "Ollama support requires: pip install neo4j-graphrag[ollama]"
            )

        if not endpoint:
            endpoint = "http://localhost:11434"

        return OllamaLLM(
            model_name=model,
            base_url=endpoint,
        )

    elif provider == "openai":
        try:
            from neo4j_graphrag.llm import OpenAILLM
        except ImportError:
            raise ImportError(
                "OpenAI support requires: pip install neo4j-graphrag[openai]"
            )

        if not api_key:
            raise ValueError("LLM_API_KEY environment variable is required for openai provider")

        return OpenAILLM(
            model_name=model,
            api_key=api_key,
        )

    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER: {provider}. "
            f"Supported providers: custom, ollama, openai"
        )
