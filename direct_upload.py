#!/usr/bin/env python3
"""Direct PDF upload to vector store"""

import sys
sys.path.insert(0, '/home/evocenta/PycharmProjects/AI_teacher')

from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from backend.vector_store import VectorStoreManager
from backend.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PDF_DIR = "/home/evocenta/Dokumente/Mathematics-20251121T093622Z-1-001/Mathematics"

def process_pdfs():
    """Process and upload all PDFs"""

    # Initialize vector store manager
    vector_manager = VectorStoreManager()

    # Get all PDF files
    pdf_files = sorted(Path(PDF_DIR).glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {PDF_DIR}")
        return

    print(f"Found {len(pdf_files)} PDF files")
    print("=" * 60)

    all_documents = []

    # Load all PDFs
    for pdf_path in pdf_files:
        try:
            print(f"Loading {pdf_path.name}...", end=" ")
            loader = PyPDFLoader(str(pdf_path))
            documents = loader.load()
            all_documents.extend(documents)
            print(f"✓ ({len(documents)} pages)")
        except Exception as e:
            print(f"✗ ERROR: {e}")
            continue

    if not all_documents:
        print("No documents loaded!")
        return

    print(f"\nTotal pages loaded: {len(all_documents)}")

    # Split documents into chunks
    print("\nSplitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
        length_function=len
    )

    chunks = text_splitter.split_documents(all_documents)
    print(f"Created {len(chunks)} chunks")

    # Create vector store
    print("\nCreating vector store...")
    try:
        vectorstore = vector_manager.create_vector_store(chunks)
        print("✓ Successfully created vector store with all chunks!")
        print(f"\nVector store location: {Config.CHROMA_PERSIST_DIR}")
    except Exception as e:
        print(f"✗ Error creating vector store: {e}")
        raise

if __name__ == "__main__":
    process_pdfs()
