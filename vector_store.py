# ==================== vector_store.py ====================
"""Vector store management with Chroma DB"""

import logging
from typing import List, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from config import Config

logger = logging.getLogger(__name__)


class DirectOpenAIEmbeddings(Embeddings):
    """Direct OpenAI embeddings wrapper that bypasses LangChain's client"""

    def __init__(self, api_key: str, model: str, dimensions: int = None):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.dimensions = dimensions

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        kwargs = {"input": texts, "model": self.model}
        if self.dimensions:
            kwargs["dimensions"] = self.dimensions

        logger.info(f"Calling OpenAI with model={self.model}, dimensions={self.dimensions}, num_texts={len(texts)}")
        logger.debug(f"API key starts with: {self.client.api_key[:10]}...")
        try:
            response = self.client.embeddings.create(**kwargs)
            logger.info(f"OpenAI call successful, got {len(response.data)} embeddings")
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"OpenAI API Error: {e}")
            logger.error(f"Model: {self.model}, Dimensions: {self.dimensions}")
            raise

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        return self.embed_documents([text])[0]


class VectorStoreManager:
    """Manages Chroma vector store operations"""

    def __init__(
            self,
            persist_directory: str = Config.CHROMA_PERSIST_DIR,
            embedding_function: Optional[any] = None
    ):
        """
        Initialize the vector store manager

        Args:
            persist_directory: Directory to persist the Chroma database
            embedding_function: Custom embedding function (defaults to HuggingFace)
        """
        self.persist_directory = persist_directory

        if embedding_function:
            self.embeddings = embedding_function
        elif Config.USE_OPENAI_EMBEDDINGS:
            logger.info(f"Using Direct OpenAI embeddings: {Config.EMBEDDING_MODEL}")
            # Use direct OpenAI client to avoid LangChain routing issues
            dimensions = None
            if Config.EMBEDDING_MODEL.startswith("text-embedding-3") and hasattr(Config, 'EMBEDDING_DIMENSIONS'):
                dimensions = Config.EMBEDDING_DIMENSIONS
                logger.info(f"Using OpenAI embeddings with dimensions: {dimensions}")

            self.embeddings = DirectOpenAIEmbeddings(
                api_key=Config.OPENAI_API_KEY,
                model=Config.EMBEDDING_MODEL,
                dimensions=dimensions
            )
        else:
            logger.info(f"Using HuggingFace embeddings: {Config.EMBEDDING_MODEL}")
            from langchain_huggingface import HuggingFaceEmbeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name=Config.EMBEDDING_MODEL
            )

        logger.info(f"Initialized VectorStoreManager with persist_directory={persist_directory}")

    def create_vector_store(self, chunks: List[Document]) -> Chroma:
        """
        Create and populate Chroma vector store

        Args:
            chunks: List of document chunks to store

        Returns:
            Chroma vector store instance
        """
        if not chunks:
            raise ValueError("No chunks provided to create vector store")

        logger.info(f"Creating vector store with {len(chunks)} chunks in Chroma DB...")
        logger.debug(f"First chunk preview: {chunks[0].page_content[:100]}...")

        try:
            # Test embedding first
            logger.info("Testing embedding generation...")
            test_embedding = self.embeddings.embed_query("test")
            logger.info(f"Embedding test successful. Dimension: {len(test_embedding)}")

            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            logger.info("Vector store created successfully")
            return vectorstore
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}", exc_info=True)
            raise

    def load_vector_store(self) -> Chroma:
        """
        Load an existing Chroma vector store

        Returns:
            Chroma vector store instance
        """
        logger.info("Loading existing vector store...")
        try:
            vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            logger.info("Vector store loaded successfully")
            return vectorstore
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            raise

    def add_documents(self, vectorstore: Chroma, chunks: List[Document]):
        """
        Add more documents to existing vector store

        Args:
            vectorstore: Existing Chroma vector store
            chunks: New document chunks to add
        """
        logger.info(f"Adding {len(chunks)} chunks to existing vector store...")
        try:
            vectorstore.add_documents(chunks)
            logger.info("Documents added successfully to vector store")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise

    @staticmethod
    def query(
            vectorstore: Chroma,
            query: str,
            k: int = Config.DEFAULT_SEARCH_K
    ) -> List[Document]:
        """
        Query the vector store for similar documents

        Args:
            vectorstore: Chroma vector store to query
            query: Search query string
            k: Number of results to return

        Returns:
            List of relevant documents
        """
        logger.info(f"Querying vector store with: '{query}' (k={k})")
        try:
            results = vectorstore.similarity_search(query, k=k)
            logger.info(f"Found {len(results)} relevant chunks for query: '{query}'")

            for i, doc in enumerate(results, 1):
                logger.debug(f"Result {i}: {doc.page_content[:100]}... | Metadata: {doc.metadata}")

            return results
        except Exception as e:
            logger.error(f"Error querying vector store: {str(e)}")
            raise