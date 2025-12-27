# PDF Upload Guide

## Current Status ✅

Your AI Teacher database currently contains:
- **26 PDFs total** (16 Mathematics + 10 English)
- **754 chunks** ready for queries
- **All Mathematics PDFs from `/home/evocenta/Dokumente/Mathematics-20251121T093622Z-1-001/Mathematics` are uploaded**

### Mathematics PDFs (16 files):
- iemh101.pdf through iemh112.pdf
- iemh1a1.pdf, iemh1a2.pdf
- iemh1an.pdf, iemh1ps.pdf

### English PDFs (10 files):
- iebe101.pdf through iebe109.pdf
- iebe1ps.pdf

---

## Uploading New PDFs

### Option 1: Batch Upload (Recommended)

Upload multiple PDFs in small batches (3 at a time):

```bash
python3 upload_pdfs_batch.py /path/to/pdf/folder
```

**Example:**
```bash
python3 upload_pdfs_batch.py /home/evocenta/Dokumente/NewTextbooks
```

**Features:**
- Uploads 3 PDFs per batch
- 5-second wait between batches
- 10-minute timeout per batch
- Progress tracking
- Error handling

### Option 2: Via Web UI

1. Open http://localhost:4200
2. Look for PDF upload button (if implemented)
3. Select PDFs and upload

### Option 3: Via API

```bash
curl -X POST http://localhost:8000/upload-pdf \
  -F "files=@textbook1.pdf" \
  -F "files=@textbook2.pdf" \
  -F "files=@textbook3.pdf"
```

---

## Checking Uploaded PDFs

```python
python3 << 'EOF'
from langchain_chroma import Chroma
from backend.vector_store import VectorStoreManager

vm = VectorStoreManager()
vs = vm.load_vector_store()
all_docs = vs.get()

sources = set()
for metadata in all_docs['metadatas']:
    if metadata and 'source' in metadata:
        import os
        sources.add(os.path.basename(metadata['source']))

print(f"📚 {len(sources)} PDFs in database:")
for src in sorted(sources):
    print(f"  ✓ {src}")
print(f"\n📊 Total chunks: {len(all_docs['ids'])}")
EOF
```

---

## Troubleshooting

### Memory Issues
If you encounter `std::bad_alloc` errors:
1. Reduce batch size in `upload_pdfs_batch.py` (change `BATCH_SIZE = 1`)
2. Increase wait time between batches (`WAIT_BETWEEN_BATCHES = 10`)
3. Restart backend between uploads

### Database Backup
Before uploading new PDFs, backup your database:

```bash
cp -r chroma_db chroma_db.backup_$(date +%Y%m%d_%H%M%S)
```

### Restore Backup
If something goes wrong:

```python
python3 -c "
import shutil
shutil.rmtree('chroma_db', ignore_errors=True)
shutil.copytree('chroma_db.backup_YYYYMMDD_HHMMSS', 'chroma_db')
print('✅ Database restored')
"
```

---

## Configuration

Edit `.env` to adjust settings:

```env
# Chunking (smaller = more chunks, better search, more memory)
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Search results
DEFAULT_SEARCH_K=4
```

---

## Notes

- Backend batches chunks internally (20 chunks at a time) to manage memory
- PDFs are processed with PyPDFLoader
- Text is split using RecursiveCharacterTextSplitter
- Embeddings: OpenAI text-embedding-3-small (384 dimensions)
- Vector store: ChromaDB with persistent storage
