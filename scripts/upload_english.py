#!/usr/bin/env python3
"""Upload English Beehive PDFs to vector store"""

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

PDF_DIR = "/home/evocenta/Dokumente/English - Beehive-20251121T095800Z-1-001/English - Beehive"

def add_english_pdfs():
    """Add English Beehive PDFs to existing vector store"""

    # Initialize vector store manager
    vector_manager = VectorStoreManager()

    # Get all PDF files
    pdf_files = sorted(Path(PDF_DIR).glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {PDF_DIR}")
        return

    print(f"Found {len(pdf_files)} English Beehive PDF files")
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

    # Load existing vector store and add new chunks
    print("\nLoading existing vector store...")
    try:
        vectorstore = vector_manager.load_vector_store()
        print("✓ Existing vector store loaded")

        print(f"\nAdding {len(chunks)} new chunks to vector store...")
        vector_manager.add_documents(vectorstore, chunks)
        print("✓ Successfully added all chunks to existing vector store!")
        print(f"\nVector store location: {Config.CHROMA_PERSIST_DIR}")
    except Exception as e:
        print(f"✗ Error: {e}")
        raise

if __name__ == "__main__":
    add_english_pdfs()
