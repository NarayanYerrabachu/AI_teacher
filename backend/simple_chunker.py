# ==================== simple_chunker.py ====================
"""Lightweight text chunking without heavy dependencies"""

import logging
from typing import List
from langchain_core.documents import Document
from .config import Config

logger = logging.getLogger(__name__)


class SimpleDocumentChunker:
    """Lightweight document chunker without langchain_text_splitters dependency"""

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
        self.separators = ["\n\n", "\n", " ", ""]
        logger.info(f"Initialized SimpleDocumentChunker with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")

    def _split_text(self, text: str) -> List[str]:
        """
        Split text into chunks using separators

        Args:
            text: Text to split

        Returns:
            List of text chunks
        """
        chunks = []

        # Try each separator in order
        for separator in self.separators:
            if separator == "":
                # Character-level splitting as last resort
                for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
                    chunk = text[i:i + self.chunk_size]
                    if chunk:
                        chunks.append(chunk)
                break
            elif separator in text:
                # Split by separator and recombine into chunks
                parts = text.split(separator)
                current_chunk = ""

                for part in parts:
                    # If adding this part would exceed chunk size, save current chunk
                    if len(current_chunk) + len(separator) + len(part) > self.chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk)
                            # Start new chunk with overlap
                            overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                            current_chunk = current_chunk[overlap_start:] + separator + part
                        else:
                            # Part itself is too large, force split
                            if len(part) > self.chunk_size:
                                for i in range(0, len(part), self.chunk_size - self.chunk_overlap):
                                    chunks.append(part[i:i + self.chunk_size])
                            else:
                                current_chunk = part
                    else:
                        # Add part to current chunk
                        if current_chunk:
                            current_chunk += separator + part
                        else:
                            current_chunk = part

                # Add final chunk
                if current_chunk:
                    chunks.append(current_chunk)
                break

        return chunks

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
            all_chunks = []

            for doc in documents:
                # Split the text
                text_chunks = self._split_text(doc.page_content)

                # Create new documents for each chunk
                for i, chunk in enumerate(text_chunks):
                    # Copy metadata and add chunk info
                    chunk_metadata = doc.metadata.copy()
                    chunk_metadata['chunk_index'] = i
                    chunk_metadata['total_chunks'] = len(text_chunks)

                    all_chunks.append(Document(
                        page_content=chunk,
                        metadata=chunk_metadata
                    ))

            logger.info(f"Successfully created {len(all_chunks)} chunks from {len(documents)} documents")
            return all_chunks
        except Exception as e:
            logger.error(f"Error chunking documents: {str(e)}")
            raise
