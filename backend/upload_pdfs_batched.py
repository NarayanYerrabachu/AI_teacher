#!/usr/bin/env python3
"""Upload PDFs in batches to avoid overwhelming the API"""
import requests
from pathlib import Path
import sys
import time

def upload_pdf_batch(pdf_paths, batch_num, total_batches, api_url="http://localhost:8000/upload-pdf"):
    """Upload a batch of PDFs"""
    files = [('files', (pdf.name, open(pdf, 'rb'), 'application/pdf')) for pdf in pdf_paths]

    try:
        print(f"\n[Batch {batch_num}/{total_batches}] Uploading {len(pdf_paths)} PDFs...")
        for pdf in pdf_paths:
            print(f"  - {pdf.name}")

        response = requests.post(api_url, files=files, timeout=300)
        response.raise_for_status()

        result = response.json()
        print(f"[Batch {batch_num}/{total_batches}] ✓ Success!")
        print(f"  Files processed: {result['details']['files_processed']}")
        print(f"  Total chunks: {result['details']['total_chunks']}")
        return True

    except Exception as e:
        print(f"[Batch {batch_num}/{total_batches}] ✗ Error: {str(e)}")
        return False

    finally:
        for _, file_tuple in files:
            file_tuple[1].close()

def main():
    # Define directories
    math_dir = Path("/home/evocenta/Dokumente/Mathematics-20251121T093622Z-1-001/Mathematics")
    english_dir = Path("/home/evocenta/Dokumente/English - Beehive-20251121T095800Z-1-001/English - Beehive")

    # Collect all PDFs
    all_pdfs = sorted(list(math_dir.glob("*.pdf")) + list(english_dir.glob("*.pdf")))

    print(f"Found {len(all_pdfs)} PDF files")
    print(f"  - Mathematics: {len(list(math_dir.glob('*.pdf')))} PDFs")
    print(f"  - English - Beehive: {len(list(english_dir.glob('*.pdf')))} PDFs")

    # Split into batches of 5
    batch_size = 5
    batches = [all_pdfs[i:i + batch_size] for i in range(0, len(all_pdfs), batch_size)]
    total_batches = len(batches)

    print(f"\nUploading in {total_batches} batches of {batch_size} PDFs each...")
    print("="*60)

    # Upload each batch
    success_count = 0
    for i, batch in enumerate(batches, 1):
        if upload_pdf_batch(batch, i, total_batches):
            success_count += 1
        else:
            print(f"\n⚠ Batch {i} failed. Continuing with next batch...")

        # Small delay between batches
        if i < total_batches:
            time.sleep(2)

    print("\n" + "="*60)
    print(f"Upload complete: {success_count}/{total_batches} batches successful")
    print(f"Total PDFs uploaded: {success_count * batch_size} out of {len(all_pdfs)}")

    sys.exit(0 if success_count == total_batches else 1)

if __name__ == "__main__":
    main()
