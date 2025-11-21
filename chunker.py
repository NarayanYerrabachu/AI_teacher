# ==================== chunker.py ====================
"""Text chunking utilities"""

import logging
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config import Config

logger = logging.getLogger(__name__)


class DocumentChunker:
    """Handles document chunking with configurable parameters"""

    def __init__(
            self,
            chunk_size: int = Config.CHUNK_SIZE,
            chunk_overlap: int = Config.CHUNK_OVERLAP
    ):
        """
        Initialize the chunker

        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        logger.info(f"Initialized DocumentChunker with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks

        Args:
            documents: List of documents to chunk

        Returns:
            List of chunked documents
        """
        logger.info(f"Chunking {len(documents)} documents...")
        try:
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Successfully created {len(chunks)} chunks from {len(documents)} documents")
            return chunks
        except Exception as e:
            logger.error(f"Error chunking documents: {str(e)}")
            raise