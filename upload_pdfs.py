#!/usr/bin/env python3
"""Script to upload multiple PDFs to the backend"""

import requests
import os
from pathlib import Path

# Backend API URL
API_URL = "http://localhost:8000/upload-pdf"

# PDF directory
PDF_DIR = "/home/evocenta/Dokumente/Mathematics-20251121T093622Z-1-001/Mathematics"

def upload_pdf(pdf_path):
    """Upload a single PDF file"""
    filename = os.path.basename(pdf_path)
    print(f"Uploading {filename}...", end=" ")

    try:
        with open(pdf_path, 'rb') as f:
            files = {'files': (filename, f, 'application/pdf')}
            response = requests.post(API_URL, files=files, timeout=300)

        if response.status_code == 200:
            print("✓ SUCCESS")
            return True
        else:
            print(f"✗ FAILED: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def main():
    """Upload all PDFs"""
    pdf_files = sorted(Path(PDF_DIR).glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {PDF_DIR}")
        return

    print(f"Found {len(pdf_files)} PDF files")
    print("=" * 60)

    success_count = 0
    failed_count = 0

    for pdf_path in pdf_files:
        if upload_pdf(str(pdf_path)):
            success_count += 1
        else:
            failed_count += 1

    print("=" * 60)
    print(f"Upload complete: {success_count} succeeded, {failed_count} failed")

if __name__ == "__main__":
    main()
