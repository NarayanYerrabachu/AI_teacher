"""Strategy Pattern for Document Chunking

This module implements the Strategy design pattern to support different
text chunking strategies for various document types and use cases.
"""

from abc import ABC, abstractmethod
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)


class ChunkingStrategy(ABC):
    """Abstract chunking strategy interface"""

    @abstractmethod
    def chunk(self, documents: List[Document]) -> List[Document]:
        """Chunk documents into smaller pieces

        Args:
            documents: List of documents to chunk

        Returns:
            List of chunked documents
        """
        pass


class RecursiveChunkingStrategy(ChunkingStrategy):
    """Recursive character-based chunking strategy

    This strategy tries to keep paragraphs, sentences, and words together
    as much as possible by recursively trying different separators.
    Good for general text documents.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize recursive chunking strategy

        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, documents: List[Document]) -> List[Document]:
        """Chunk documents using recursive character splitting"""
        logger.info(
            f"Chunking with RecursiveCharacterTextSplitter "
            f"(size={self.chunk_size}, overlap={self.chunk_overlap})"
        )

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        chunks = splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
        return chunks


class FixedSizeChunkingStrategy(ChunkingStrategy):
    """Fixed-size chunking strategy

    Simple strategy that chunks text into fixed-size pieces.
    Fast but may split sentences or paragraphs awkwardly.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize fixed-size chunking strategy

        Args:
            chunk_size: Fixed size of each chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, documents: List[Document]) -> List[Document]:
        """Chunk documents using fixed-size splitting"""
        logger.info(
            f"Chunking with fixed size "
            f"(size={self.chunk_size}, overlap={self.chunk_overlap})"
        )

        from langchain_text_splitters import CharacterTextSplitter

        splitter = CharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separator="\n"
        )

        chunks = splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
        return chunks


class SemanticChunkingStrategy(ChunkingStrategy):
    """Semantic-based chunking strategy

    This strategy groups text based on semantic similarity, keeping
    related content together. Requires embeddings but produces better
    semantic coherence in chunks.
    """

    def __init__(self, embeddings, buffer_size: int = 1):
        """Initialize semantic chunking strategy

        Args:
            embeddings: Embedding function to use for semantic comparison
            buffer_size: Number of sentences to buffer for context
        """
        self.embeddings = embeddings
        self.buffer_size = buffer_size

    def chunk(self, documents: List[Document]) -> List[Document]:
        """Chunk documents using semantic similarity"""
        logger.info(f"Chunking with SemanticChunker (buffer_size={self.buffer_size})")

        try:
            from langchain_experimental.text_splitter import SemanticChunker

            splitter = SemanticChunker(
                embeddings=self.embeddings,
                buffer_size=self.buffer_size
            )

            chunks = splitter.split_documents(documents)
            logger.info(f"Created {len(chunks)} semantic chunks from {len(documents)} documents")
            return chunks
        except ImportError:
            logger.error(
                "SemanticChunker requires langchain_experimental. "
                "Install with: pip install langchain-experimental"
            )
            # Fallback to recursive chunking
            logger.warning("Falling back to RecursiveChunkingStrategy")
            fallback = RecursiveChunkingStrategy()
            return fallback.chunk(documents)


class MarkdownChunkingStrategy(ChunkingStrategy):
    """Markdown-aware chunking strategy

    This strategy preserves markdown structure by splitting on headers
    and keeping related content under each header together.
    Ideal for markdown documentation.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize markdown-aware chunking strategy

        Args:
            chunk_size: Target size of each chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, documents: List[Document]) -> List[Document]:
        """Chunk documents preserving markdown structure"""
        logger.info(
            f"Chunking with MarkdownHeaderTextSplitter "
            f"(size={self.chunk_size}, overlap={self.chunk_overlap})"
        )

        from langchain_text_splitters import MarkdownHeaderTextSplitter

        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]

        splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on
        )

        chunks = []
        for doc in documents:
            doc_chunks = splitter.split_text(doc.page_content)
            for chunk in doc_chunks:
                # Preserve metadata
                chunk.metadata.update(doc.metadata)
                chunks.append(chunk)

        logger.info(f"Created {len(chunks)} markdown chunks from {len(documents)} documents")
        return chunks


class ChunkingContext:
    """Context class for managing chunking strategies

    This class allows changing chunking strategies at runtime and
    provides a consistent interface for document chunking.
    """

    def __init__(self, strategy: ChunkingStrategy):
        """Initialize chunking context

        Args:
            strategy: Initial chunking strategy to use
        """
        self._strategy = strategy

    @property
    def strategy(self) -> ChunkingStrategy:
        """Get current chunking strategy"""
        return self._strategy

    def set_strategy(self, strategy: ChunkingStrategy) -> None:
        """Change chunking strategy at runtime

        Args:
            strategy: New chunking strategy to use
        """
        logger.info(
            f"Switching chunking strategy from {self._strategy.__class__.__name__} "
            f"to {strategy.__class__.__name__}"
        )
        self._strategy = strategy

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Execute chunking with current strategy

        Args:
            documents: Documents to chunk

        Returns:
            Chunked documents
        """
        return self._strategy.chunk(documents)


# Convenience factory function
def create_chunking_strategy(
    strategy_type: str = "recursive",
    **kwargs
) -> ChunkingStrategy:
    """Factory function to create chunking strategies

    Args:
        strategy_type: Type of strategy ('recursive', 'fixed', 'semantic', 'markdown')
        **kwargs: Strategy-specific parameters

    Returns:
        ChunkingStrategy instance

    Raises:
        ValueError: If strategy_type is not supported
    """
    strategies = {
        'recursive': RecursiveChunkingStrategy,
        'fixed': FixedSizeChunkingStrategy,
        'semantic': SemanticChunkingStrategy,
        'markdown': MarkdownChunkingStrategy,
    }

    if strategy_type not in strategies:
        available = ", ".join(strategies.keys())
        raise ValueError(
            f"Unknown strategy type: {strategy_type}. "
            f"Available strategies: {available}"
        )

    return strategies[strategy_type](**kwargs)
