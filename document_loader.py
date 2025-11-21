# ==================== document_loader.py ====================
"""Document loading utilities for PDFs and web pages"""

import logging
from typing import List
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class DocumentLoader:
    """Handles loading documents from various sources"""

    @staticmethod
    def load_pdf(pdf_path: str) -> List[Document]:
        """
        Load a PDF file and return documents

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of Document objects
        """
        logger.info(f"Loading PDF: {pdf_path}")
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            logger.info(f"Successfully loaded {len(documents)} pages from PDF: {pdf_path}")
            return documents
        except Exception as e:
            logger.error(f"Error loading PDF {pdf_path}: {str(e)}")
            raise

    @staticmethod
    def load_pdfs(pdf_paths: List[str]) -> List[Document]:
        """
        Load multiple PDF files

        Args:
            pdf_paths: List of paths to PDF files

        Returns:
            Combined list of Document objects
        """
        logger.info(f"Loading {len(pdf_paths)} PDF files")
        all_documents = []
        for pdf_path in pdf_paths:
            documents = DocumentLoader.load_pdf(pdf_path)
            all_documents.extend(documents)
        logger.info(f"Successfully loaded {len(all_documents)} total pages from {len(pdf_paths)} PDFs")
        return all_documents

    @staticmethod
    def load_web_pages(urls: List[str]) -> List[Document]:
        """
        Load web pages from URLs

        Args:
            urls: List of URLs to load

        Returns:
            List of Document objects
        """
        logger.info(f"Loading {len(urls)} web pages")
        try:
            loader = WebBaseLoader(urls)
            documents = loader.load()
            logger.info(f"Successfully loaded {len(documents)} web pages")
            return documents
        except Exception as e:
            logger.error(f"Error loading web pages: {str(e)}")
            raise