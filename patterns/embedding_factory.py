"""Abstract Factory Pattern for Embedding Providers

This module implements the Abstract Factory design pattern to create
embedding instances from different AI providers (OpenAI, HuggingFace, etc.)
"""

from abc import ABC, abstractmethod
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Abstract embedding provider interface"""

    @abstractmethod
    def create_embeddings(self, model: str, **kwargs) -> Any:
        """Create embeddings instance for the provider

        Args:
            model: Model name/identifier
            **kwargs: Provider-specific arguments

        Returns:
            Embedding instance from the provider's SDK
        """
        pass


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider"""

    def create_embeddings(
        self,
        model: str,
        api_key: str,
        chunk_size: int = 16,
        **kwargs
    ) -> Any:
        """Create OpenAI embeddings

        Args:
            model: OpenAI model name (e.g., 'text-embedding-3-small')
            api_key: OpenAI API key
            chunk_size: Number of texts to embed per API call

        Returns:
            OpenAIEmbeddings instance
        """
        from langchain_openai import OpenAIEmbeddings
        logger.info(f"Creating OpenAI embeddings with model: {model}")

        return OpenAIEmbeddings(
            model=model,
            openai_api_key=api_key,
            chunk_size=chunk_size
        )


class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    """HuggingFace embedding provider"""

    def create_embeddings(self, model: str, **kwargs) -> Any:
        """Create HuggingFace embeddings

        Args:
            model: HuggingFace model name (e.g., 'sentence-transformers/all-MiniLM-L6-v2')

        Returns:
            HuggingFaceEmbeddings instance
        """
        from langchain_huggingface import HuggingFaceEmbeddings
        logger.info(f"Creating HuggingFace embeddings with model: {model}")

        return HuggingFaceEmbeddings(model_name=model)


class CohereEmbeddingProvider(EmbeddingProvider):
    """Cohere embedding provider (for future expansion)"""

    def create_embeddings(
        self,
        model: str,
        api_key: str,
        **kwargs
    ) -> Any:
        """Create Cohere embeddings

        Args:
            model: Cohere model name
            api_key: Cohere API key

        Returns:
            CohereEmbeddings instance
        """
        try:
            from langchain_cohere import CohereEmbeddings
            logger.info(f"Creating Cohere embeddings with model: {model}")

            return CohereEmbeddings(
                model=model,
                cohere_api_key=api_key
            )
        except ImportError:
            logger.error("langchain_cohere not installed. Install with: pip install langchain-cohere")
            raise


class EmbeddingFactory:
    """Factory to create embedding providers

    This factory manages creation of embeddings from different AI providers,
    making it easy to switch between providers without changing application code.
    """

    # Registry of available providers
    _providers = {
        'openai': OpenAIEmbeddingProvider(),
        'huggingface': HuggingFaceEmbeddingProvider(),
        'cohere': CohereEmbeddingProvider(),
    }

    @staticmethod
    def create_embeddings(provider: str, model: str, **kwargs) -> Any:
        """Create embeddings from specified provider

        Args:
            provider: Provider name ('openai', 'huggingface', 'cohere')
            model: Model name
            **kwargs: Provider-specific arguments (api_key, chunk_size, etc.)

        Returns:
            Embedding instance

        Raises:
            ValueError: If provider is not supported
        """
        if provider not in EmbeddingFactory._providers:
            available = ", ".join(EmbeddingFactory._providers.keys())
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Available providers: {available}"
            )

        return EmbeddingFactory._providers[provider].create_embeddings(
            model=model,
            **kwargs
        )

    @staticmethod
    def from_config(config) -> Any:
        """Create embeddings from Config object

        This is a convenience method that reads configuration and
        creates the appropriate embeddings automatically.

        Args:
            config: Config object with embedding settings

        Returns:
            Configured embedding instance
        """
        if config.USE_OPENAI_EMBEDDINGS:
            logger.info("Creating embeddings from config: OpenAI")
            return EmbeddingFactory.create_embeddings(
                provider='openai',
                model=config.EMBEDDING_MODEL,
                api_key=config.OPENAI_API_KEY,
                chunk_size=16
            )
        else:
            logger.info("Creating embeddings from config: HuggingFace")
            return EmbeddingFactory.create_embeddings(
                provider='huggingface',
                model=config.EMBEDDING_MODEL
            )

    @staticmethod
    def register_provider(name: str, provider: EmbeddingProvider) -> None:
        """Register a new embedding provider

        This allows extending the factory with custom providers at runtime.

        Args:
            name: Provider identifier
            provider: EmbeddingProvider instance
        """
        EmbeddingFactory._providers[name] = provider
        logger.info(f"Registered new embedding provider: {name}")

    @staticmethod
    def list_providers() -> list:
        """List all registered providers

        Returns:
            List of provider names
        """
        return list(EmbeddingFactory._providers.keys())
