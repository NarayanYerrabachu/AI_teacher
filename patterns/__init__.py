"""Design Patterns Package for AI Teacher Application

This package contains implementations of common design patterns:
- Factory Pattern: Document loader selection
- Abstract Factory: Embedding provider creation
- Strategy Pattern: Document chunking strategies
- Singleton Pattern: Vector store manager
- Repository Pattern: Vector store data access

Usage:
    from patterns import (
        DocumentLoaderFactory,
        EmbeddingFactory,
        ChunkingContext, RecursiveChunkingStrategy,
        VectorStoreManagerSingleton,
        create_vector_repository
    )
"""

from patterns.document_loader_factory import (
    DocumentLoader,
    DocumentLoaderFactory,
    SimplePDFDocumentLoader,
    OCRPDFDocumentLoader,
)

from patterns.embedding_factory import (
    EmbeddingProvider,
    EmbeddingFactory,
    OpenAIEmbeddingProvider,
    HuggingFaceEmbeddingProvider,
)

from patterns.chunking_strategy import (
    ChunkingStrategy,
    ChunkingContext,
    RecursiveChunkingStrategy,
    FixedSizeChunkingStrategy,
    SemanticChunkingStrategy,
    MarkdownChunkingStrategy,
    create_chunking_strategy,
)

from patterns.vector_repository import (
    VectorRepository,
    ChromaVectorRepository,
    VectorStoreManagerSingleton,
    create_vector_repository,
)

__all__ = [
    # Factory Pattern
    "DocumentLoader",
    "DocumentLoaderFactory",
    "SimplePDFDocumentLoader",
    "OCRPDFDocumentLoader",

    # Abstract Factory Pattern
    "EmbeddingProvider",
    "EmbeddingFactory",
    "OpenAIEmbeddingProvider",
    "HuggingFaceEmbeddingProvider",

    # Strategy Pattern
    "ChunkingStrategy",
    "ChunkingContext",
    "RecursiveChunkingStrategy",
    "FixedSizeChunkingStrategy",
    "SemanticChunkingStrategy",
    "MarkdownChunkingStrategy",
    "create_chunking_strategy",

    # Singleton + Repository Pattern
    "VectorRepository",
    "ChromaVectorRepository",
    "VectorStoreManagerSingleton",
    "create_vector_repository",
]

__version__ = "1.0.0"
