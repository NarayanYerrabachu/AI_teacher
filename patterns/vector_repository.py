"""Repository and Singleton Patterns for Vector Store

This module implements:
1. Repository Pattern - Abstract data access layer for vector operations
2. Singleton Pattern - Ensures single instance of vector store manager
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from langchain_core.documents import Document
import threading
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Singleton Pattern
# ============================================================================

class SingletonMeta(type):
    """Thread-safe Singleton metaclass

    This metaclass ensures that only one instance of a class exists
    and provides thread-safe access to that instance.
    """

    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        """Thread-safe instance creation"""
        # Double-checked locking pattern
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


# ============================================================================
# Repository Pattern
# ============================================================================

class VectorRepository(ABC):
    """Abstract repository for vector store operations

    This interface defines all vector store operations,
    allowing us to swap implementations without changing application code.
    """

    @abstractmethod
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to vector store

        Args:
            documents: List of documents to add
        """
        pass

    @abstractmethod
    def search(self, query: str, k: int = 4) -> List[Document]:
        """Search for similar documents

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of similar documents
        """
        pass

    @abstractmethod
    def delete_all(self) -> None:
        """Delete all documents from vector store"""
        pass

    @abstractmethod
    def get_collection_size(self) -> int:
        """Get number of documents in collection

        Returns:
            Number of documents
        """
        pass


class ChromaVectorRepository(VectorRepository):
    """Chroma implementation of vector repository

    This implementation wraps VectorStoreManager to provide
    a clean repository interface.
    """

    def __init__(self, vector_store_manager):
        """Initialize repository with vector store manager

        Args:
            vector_store_manager: VectorStoreManager instance
        """
        self.manager = vector_store_manager
        logger.info("ChromaVectorRepository initialized")

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to Chroma vector store"""
        logger.info(f"Adding {len(documents)} documents to Chroma")
        self.manager.add_documents(documents)

    def search(self, query: str, k: int = 4) -> List[Document]:
        """Search Chroma vector store for similar documents"""
        logger.info(f"Searching Chroma for: '{query[:50]}...' (k={k})")
        vectorstore = self.manager.load_vector_store()
        return vectorstore.similarity_search(query, k=k)

    def delete_all(self) -> None:
        """Delete all documents from Chroma"""
        logger.info("Clearing all documents from Chroma")
        self.manager.clear_vector_store()

    def get_collection_size(self) -> int:
        """Get number of documents in Chroma collection"""
        try:
            vectorstore = self.manager.load_vector_store()
            # Chroma specific way to get collection size
            collection = vectorstore._collection
            return collection.count()
        except Exception as e:
            logger.error(f"Error getting collection size: {e}")
            return 0


class PineconeVectorRepository(VectorRepository):
    """Pinecone implementation of vector repository

    This is a placeholder implementation for future Pinecone support.
    Demonstrates how easy it is to add new vector store backends.
    """

    def __init__(self, index_name: str, api_key: str, embeddings):
        """Initialize Pinecone repository

        Args:
            index_name: Pinecone index name
            api_key: Pinecone API key
            embeddings: Embedding function
        """
        self.index_name = index_name
        self.api_key = api_key
        self.embeddings = embeddings
        logger.info(f"PineconeVectorRepository initialized (index: {index_name})")
        # TODO: Initialize Pinecone client

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to Pinecone"""
        logger.info(f"Adding {len(documents)} documents to Pinecone")
        # TODO: Implement Pinecone document addition
        raise NotImplementedError("Pinecone support not yet implemented")

    def search(self, query: str, k: int = 4) -> List[Document]:
        """Search Pinecone for similar documents"""
        logger.info(f"Searching Pinecone for: '{query[:50]}...' (k={k})")
        # TODO: Implement Pinecone search
        raise NotImplementedError("Pinecone support not yet implemented")

    def delete_all(self) -> None:
        """Delete all vectors from Pinecone index"""
        logger.info("Clearing all vectors from Pinecone")
        # TODO: Implement Pinecone clear
        raise NotImplementedError("Pinecone support not yet implemented")

    def get_collection_size(self) -> int:
        """Get number of vectors in Pinecone index"""
        # TODO: Implement Pinecone collection size
        raise NotImplementedError("Pinecone support not yet implemented")


# ============================================================================
# Singleton Vector Store Manager
# ============================================================================

class VectorStoreManagerSingleton(metaclass=SingletonMeta):
    """Singleton wrapper for VectorStoreManager

    This ensures only one vector store manager instance exists
    throughout the application lifecycle.
    """

    def __init__(self, persist_directory: str = None, embedding_function=None):
        """Initialize singleton vector store manager

        Only initializes once, subsequent calls return the same instance.

        Args:
            persist_directory: Directory to persist vector store
            embedding_function: Embedding function to use
        """
        # Only initialize once
        if not hasattr(self, '_initialized'):
            from config import Config
            from vector_store import VectorStoreManager

            self.persist_directory = persist_directory or Config.CHROMA_PERSIST_DIR

            if embedding_function:
                self.embeddings = embedding_function
            else:
                # Use factory to create embeddings
                from patterns.embedding_factory import EmbeddingFactory
                self.embeddings = EmbeddingFactory.from_config(Config)

            # Create the actual vector store manager
            self._manager = VectorStoreManager(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )

            self._initialized = True
            logger.info("VectorStoreManagerSingleton initialized (first time)")
        else:
            logger.debug("VectorStoreManagerSingleton already initialized, reusing instance")

    def __getattr__(self, name):
        """Delegate all other methods to the wrapped manager"""
        return getattr(self._manager, name)

    @classmethod
    def reset(cls):
        """Reset singleton instance (useful for testing)"""
        with cls._lock:
            if cls in cls._instances:
                del cls._instances[cls]
                logger.info("VectorStoreManagerSingleton reset")


# ============================================================================
# Repository Factory
# ============================================================================

def create_vector_repository(
    repository_type: str = "chroma",
    **kwargs
) -> VectorRepository:
    """Factory function to create vector repositories

    Args:
        repository_type: Type of repository ('chroma', 'pinecone')
        **kwargs: Repository-specific parameters

    Returns:
        VectorRepository instance

    Raises:
        ValueError: If repository_type is not supported
    """
    if repository_type == "chroma":
        from config import Config

        # Get or create singleton vector store manager
        if 'vector_store_manager' in kwargs:
            manager = kwargs['vector_store_manager']
        else:
            manager = VectorStoreManagerSingleton()

        return ChromaVectorRepository(manager)

    elif repository_type == "pinecone":
        return PineconeVectorRepository(**kwargs)

    else:
        raise ValueError(
            f"Unknown repository type: {repository_type}. "
            f"Available types: chroma, pinecone"
        )
