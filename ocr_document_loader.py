"""OCR-enabled document loader for text and image-based PDFs"""

import logging
from typing import List
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from pypdf import PdfReader

logger = logging.getLogger(__name__)


class OCRDocumentLoader:
    """Document loader with automatic OCR fallback for image-based PDFs"""

    def __init__(self, min_text_threshold: int = 50):
        """
        Initialize OCR document loader

        Args:
            min_text_threshold: Minimum characters per page to consider text extraction successful
        """
        self.min_text_threshold = min_text_threshold
        self.ocr_available = self._check_ocr_available()

        if not self.ocr_available:
            logger.warning("OCR dependencies not fully available. Scanned PDFs won't be supported.")

    def _check_ocr_available(self) -> bool:
        """Check if OCR dependencies are available"""
        try:
            import pytesseract
            from pdf2image import convert_from_path
            from PIL import Image

            # Try to get tesseract version
            try:
                pytesseract.get_tesseract_version()
                logger.info("OCR fully available (Tesseract installed)")
                return True
            except Exception:
                logger.warning("pytesseract installed but Tesseract binary not found")
                return False
        except ImportError as e:
            logger.warning(f"OCR libraries not available: {e}")
            return False

    def _is_text_based_pdf(self, pdf_path: str) -> bool:
        """
        Check if PDF has extractable text

        Returns:
            True if PDF has sufficient text, False if it's likely scanned images
        """
        try:
            reader = PdfReader(pdf_path)

            # Check first few pages
            pages_to_check = min(3, len(reader.pages))
            total_text = 0

            for i in range(pages_to_check):
                text = reader.pages[i].extract_text()
                total_text += len(text.strip())

            avg_text_per_page = total_text / pages_to_check
            is_text_based = avg_text_per_page >= self.min_text_threshold

            logger.info(
                f"PDF analysis: {avg_text_per_page:.0f} chars/page "
                f"({'text-based' if is_text_based else 'image-based'})"
            )

            return is_text_based

        except Exception as e:
            logger.error(f"Error analyzing PDF: {e}")
            return True  # Default to trying text extraction

    def _load_pdf_with_ocr(self, pdf_path: str) -> List[Document]:
        """
        Load PDF using OCR

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of Document objects
        """
        if not self.ocr_available:
            raise RuntimeError(
                "OCR is not available. Please install tesseract-ocr:\n"
                "Ubuntu/Debian: sudo apt-get install tesseract-ocr poppler-utils\n"
                "macOS: brew install tesseract poppler\n"
                "Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
            )

        try:
            import pytesseract
            from pdf2image import convert_from_path

            logger.info(f"Converting PDF to images for OCR: {pdf_path}")

            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)
            logger.info(f"Converted {len(images)} pages to images")

            documents = []

            for i, image in enumerate(images):
                logger.info(f"OCR processing page {i+1}/{len(images)}...")

                # Perform OCR
                text = pytesseract.image_to_string(image, lang='eng')

                if text.strip():
                    doc = Document(
                        page_content=text,
                        metadata={
                            "source": pdf_path,
                            "page": i,
                            "ocr": True
                        }
                    )
                    documents.append(doc)
                    logger.info(f"Page {i+1}: Extracted {len(text)} characters via OCR")
                else:
                    logger.warning(f"Page {i+1}: No text extracted")

            logger.info(f"OCR complete: Extracted {len(documents)} pages from {pdf_path}")
            return documents

        except Exception as e:
            logger.error(f"OCR failed for {pdf_path}: {e}")
            raise

    def load_pdf(self, pdf_path: str) -> List[Document]:
        """
        Load a single PDF file with automatic OCR fallback

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of Document objects
        """
        logger.info(f"Loading PDF: {pdf_path}")

        # Check if PDF is text-based or image-based
        is_text_based = self._is_text_based_pdf(pdf_path)

        if is_text_based:
            # Use standard PDF loader
            logger.info(f"Using standard text extraction for {pdf_path}")
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from {pdf_path}")
            return documents
        else:
            # Use OCR
            logger.info(f"PDF appears to be scanned images, using OCR for {pdf_path}")
            return self._load_pdf_with_ocr(pdf_path)

    def load_pdfs(self, pdf_paths: List[str]) -> List[Document]:
        """
        Load multiple PDF files with automatic OCR fallback

        Args:
            pdf_paths: List of paths to PDF files

        Returns:
            List of all Document objects from all PDFs
        """
        logger.info(f"Loading {len(pdf_paths)} PDF files")
        all_documents = []

        for pdf_path in pdf_paths:
            try:
                documents = self.load_pdf(pdf_path)
                all_documents.extend(documents)
            except Exception as e:
                logger.error(f"Failed to load {pdf_path}: {e}")
                # Continue with other files

        logger.info(
            f"Successfully loaded {len(all_documents)} total pages from {len(pdf_paths)} PDFs"
        )
        return all_documents

    def load_web_pages(self, urls: List[str]) -> List[Document]:
        """
        Load web pages from URLs

        Args:
            urls: List of URLs to load

        Returns:
            List of Document objects
        """
        logger.info(f"Loading {len(urls)} web pages")
        loader = WebBaseLoader(urls)
        documents = loader.load()
        logger.info(f"Successfully loaded {len(documents)} web pages")
        return documents
