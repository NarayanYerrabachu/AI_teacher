#!/usr/bin/env python3
"""Upload all PDFs from specified directories to the API"""
import requests
from pathlib import Path
import sys

def upload_pdfs(pdf_paths, api_url="http://localhost:8000/upload-pdf"):
    """Upload multiple PDFs to the API"""
    files = [('files', (pdf.name, open(pdf, 'rb'), 'application/pdf')) for pdf in pdf_paths]

    try:
        print(f"Uploading {len(pdf_paths)} PDFs...")
        response = requests.post(api_url, files=files)
        response.raise_for_status()

        result = response.json()
        print(f"✓ Success: {result['message']}")
        print(f"  Files processed: {result['details']['files_processed']}")
        print(f"  Total chunks: {result['details']['total_chunks']}")
        return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

    finally:
        # Close all file handles
        for _, file_tuple in files:
            file_tuple[1].close()

def main():
    # Define directories
    math_dir = Path("/home/evocenta/Dokumente/Mathematics-20251121T093622Z-1-001/Mathematics")
    english_dir = Path("/home/evocenta/Dokumente/English - Beehive-20251121T095800Z-1-001/English - Beehive")

    # Collect all PDFs
    all_pdfs = list(math_dir.glob("*.pdf")) + list(english_dir.glob("*.pdf"))

    print(f"Found {len(all_pdfs)} PDF files:")
    print(f"  - Mathematics: {len(list(math_dir.glob('*.pdf')))} PDFs")
    print(f"  - English - Beehive: {len(list(english_dir.glob('*.pdf')))} PDFs")
    print()

    # Upload all PDFs
    success = upload_pdfs(all_pdfs)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
