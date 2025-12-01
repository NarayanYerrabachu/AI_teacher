# ==================== simple_document_loader.py ====================
"""Lightweight document loading without langchain_community dependencies"""

import logging
from typing import List
from pathlib import Path
from langchain_core.documents import Document
import pypdf

logger = logging.getLogger(__name__)


class SimplePDFLoader:
    """Lightweight PDF loader without langchain_community dependency"""

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
            documents = []

            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                num_pages = len(pdf_reader.pages)

                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()

                    if text.strip():  # Only add non-empty pages
                        documents.append(Document(
                            page_content=text,
                            metadata={
                                'source': pdf_path,
                                'page': page_num + 1,
                                'total_pages': num_pages
                            }
                        ))

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
            documents = SimplePDFLoader.load_pdf(pdf_path)
            all_documents.extend(documents)
        logger.info(f"Successfully loaded {len(all_documents)} total pages from {len(pdf_paths)} PDFs")
        return all_documents
