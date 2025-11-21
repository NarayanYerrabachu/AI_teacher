"""Factory Pattern for Document Loaders

This module implements the Factory design pattern to create appropriate
document loaders based on file type and requirements.
"""

from abc import ABC, abstractmethod
from typing import List
from langchain_core.documents import Document
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DocumentLoader(ABC):
    """Abstract base class for document loaders"""

    @abstractmethod
    def load(self, file_path: str) -> List[Document]:
        """Load documents from file

        Args:
            file_path: Path to the document file

        Returns:
            List of Document objects
        """
        pass


class SimplePDFDocumentLoader(DocumentLoader):
    """Simple PDF loader without OCR"""

    def load(self, file_path: str) -> List[Document]:
        """Load PDF using simple text extraction"""
        from simple_document_loader import SimplePDFLoader
        logger.info(f"Loading PDF with SimplePDFLoader: {file_path}")
        return SimplePDFLoader.load_pdf(file_path)


class OCRPDFDocumentLoader(DocumentLoader):
    """OCR-enabled PDF loader for scanned documents"""

    def __init__(self, min_text_threshold: int = 50):
        from ocr_document_loader import OCRDocumentLoader
        self.loader = OCRDocumentLoader(min_text_threshold)

    def load(self, file_path: str) -> List[Document]:
        """Load PDF with OCR fallback for scanned images"""
        logger.info(f"Loading PDF with OCRDocumentLoader: {file_path}")
        return self.loader.load_document(file_path)


class DocumentLoaderFactory:
    """Factory to create appropriate document loader

    This factory decides which loader to use based on:
    - File type
    - Whether OCR is needed
    - Auto-detection of scanned PDFs
    """

    @staticmethod
    def create_loader(
        file_path: str,
        enable_ocr: bool = False,
        auto_detect: bool = True
    ) -> DocumentLoader:
        """Create appropriate document loader

        Args:
            file_path: Path to document
            enable_ocr: Force OCR usage
            auto_detect: Auto-detect if OCR is needed by sampling text

        Returns:
            DocumentLoader instance

        Raises:
            ValueError: If file type is not supported
        """
        file_ext = Path(file_path).suffix.lower()

        # Check if file is PDF
        if file_ext != '.pdf':
            raise ValueError(f"Unsupported file type: {file_ext}. Only PDF files are supported.")

        # Auto-detect if PDF needs OCR
        if auto_detect and not enable_ocr:
            enable_ocr = DocumentLoaderFactory._needs_ocr(file_path)
            if enable_ocr:
                logger.info(f"Auto-detected scanned PDF: {file_path}")

        if enable_ocr:
            return OCRPDFDocumentLoader()
        else:
            return SimplePDFDocumentLoader()

    @staticmethod
    def _needs_ocr(file_path: str, threshold: int = 50) -> bool:
        """Check if PDF needs OCR by sampling text

        Args:
            file_path: Path to PDF file
            threshold: Minimum characters to consider text-based

        Returns:
            True if OCR is needed, False otherwise
        """
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)

            # Check first page
            if len(reader.pages) > 0:
                text = reader.pages[0].extract_text()
                text_length = len(text.strip())

                logger.debug(f"First page text length: {text_length} chars")

                # If very little text, likely scanned
                if text_length < threshold:
                    return True

            return False
        except Exception as e:
            logger.warning(f"Error checking if OCR needed: {e}")
            return False
