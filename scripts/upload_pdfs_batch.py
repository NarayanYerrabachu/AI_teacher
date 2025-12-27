#!/usr/bin/env python3
"""
Batch PDF Upload Script
Uploads PDFs in small batches to avoid memory issues
"""

import requests
from pathlib import Path
import time
import sys

BACKEND_URL = "http://localhost:8000"
BATCH_SIZE = 3  # Upload 3 PDFs at a time
WAIT_BETWEEN_BATCHES = 5  # Seconds to wait between batches

def upload_batch(pdf_files):
    """Upload a batch of PDFs"""
    print(f"📦 Uploading batch of {len(pdf_files)} PDFs...")

    try:
        # Prepare files for multi-file upload
        files = []
        for pdf_file in pdf_files:
            files.append(('files', (pdf_file.name, open(pdf_file, 'rb'), 'application/pdf')))

        response = requests.post(
            f"{BACKEND_URL}/upload-pdf",
            files=files,
            timeout=600  # 10 minutes for batch
        )

        # Close file handles
        for _, (_, file_handle, _) in files:
            file_handle.close()

        if response.status_code == 200:
            result = response.json()
            chunks = result.get('details', {}).get('total_chunks', '?')
            print(f"   ✅ Success! {chunks} chunks created")
            print(f"   Files: {', '.join([f.name for f in pdf_files])}\n")
            return True
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Error: {response.text[:300]}\n")
            return False

    except Exception as e:
        print(f"   ❌ Error: {str(e)}\n")
        return False

def main(folder_path):
    """Main upload function"""
    pdf_folder = Path(folder_path)

    if not pdf_folder.exists():
        print(f"❌ Error: Folder not found: {folder_path}")
        sys.exit(1)

    # Find all PDF files
    pdf_files = sorted(pdf_folder.glob("*.pdf"))

    if not pdf_files:
        print(f"❌ No PDF files found in {folder_path}")
        sys.exit(1)

    print(f"🚀 Found {len(pdf_files)} PDF files")
    print(f"📊 Will upload in batches of {BATCH_SIZE}")
    print("=" * 60)

    # Process in batches
    success_count = 0
    total_batches = (len(pdf_files) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(pdf_files), BATCH_SIZE):
        batch = pdf_files[i:i+BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1

        print(f"\n[Batch {batch_num}/{total_batches}]")

        if upload_batch(batch):
            success_count += len(batch)

        # Wait between batches to let backend process
        if i + BATCH_SIZE < len(pdf_files):
            print(f"⏳ Waiting {WAIT_BETWEEN_BATCHES}s before next batch...")
            time.sleep(WAIT_BETWEEN_BATCHES)

    print("=" * 60)
    print(f"✅ Complete: {success_count}/{len(pdf_files)} PDFs uploaded successfully")

    if success_count < len(pdf_files):
        print(f"⚠️  {len(pdf_files) - success_count} PDFs failed to upload")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 upload_pdfs_batch.py <folder_path>")
        print("\nExample:")
        print("  python3 upload_pdfs_batch.py /path/to/pdf/folder")
        sys.exit(1)

    folder = sys.argv[1]
    print(f"📁 Target folder: {folder}")
    print(f"🔗 Backend URL: {BACKEND_URL}\n")

    main(folder)
