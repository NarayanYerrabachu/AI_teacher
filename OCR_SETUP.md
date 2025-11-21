# OCR Setup Guide

Your AI Teacher chatbot now supports **both text-based and scanned (image) PDFs** using OCR!

## What Was Added

✅ **Automatic Detection** - System detects if PDF is text-based or scanned
✅ **Smart Fallback** - Uses fast text extraction for text PDFs, OCR for scanned PDFs
✅ **Python Packages** - Already installed (pytesseract, pdf2image, Pillow)
⚠️ **Tesseract Binary** - Needs to be installed (see below)

## Install Tesseract OCR

You need to install the Tesseract OCR engine on your system:

### Ubuntu/Debian (Your System)

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng poppler-utils
```

### Verify Installation

```bash
tesseract --version
```

You should see something like: `tesseract 4.x.x`

### Other Systems (for reference)

**macOS:**
```bash
brew install tesseract poppler
```

**Windows:**
Download installer from: https://github.com/UB-Mannheim/tesseract/wiki

## How It Works

### 1. Text-Based PDFs (Fast)
```
PDF → Direct text extraction → Chunks → Vector Store
⏱️ Seconds
```

### 2. Scanned PDFs (Slower)
```
PDF → Convert to Images → OCR → Text → Chunks → Vector Store
⏱️ Minutes (depends on PDF size)
```

## Testing OCR

### Step 1: Install Tesseract

Run the command above to install Tesseract OCR.

### Step 2: Restart Backend

The backend should auto-reload, but if not:

```bash
# Kill current backend
pkill -f "python main.py"

# Start fresh
cd /home/evocenta/PycharmProjects/AI_teacher
pipenv run python main.py
```

### Step 3: Upload Your Scanned PDF

1. Go to http://localhost:5173
2. Click the 📎 button
3. Upload your Maharashtra textbook PDF
4. Wait for processing (may take a few minutes for 86 pages)
5. Look for "✓ Uploaded X files"

### Step 4: Ask Questions!

Once uploaded, ask questions about the textbook:
- "What topics are covered in this math textbook?"
- "Explain fractions from the textbook"
- "What is the first chapter about?"

## Progress Indicators

When OCR is processing, you'll see logs like:

```
INFO - Converting PDF to images for OCR: uploads/textbook.pdf
INFO - Converted 86 pages to images
INFO - OCR processing page 1/86...
INFO - Page 1: Extracted 542 characters via OCR
INFO - OCR processing page 2/86...
...
INFO - OCR complete: Extracted 86 pages
```

## Performance Tips

### For Large Scanned PDFs:

1. **Be Patient** - OCR takes time (30-60 seconds per page)
2. **Process During Off-Hours** - Upload large PDFs when you don't need immediate results
3. **Check Logs** - Monitor progress in the terminal running the backend

### Expected Times:

- **10 pages**: ~5-10 minutes
- **50 pages**: ~25-50 minutes
- **100 pages**: ~50-100 minutes

## Troubleshooting

### Error: "OCR is not available"

**Solution:** Install Tesseract:
```bash
sudo apt-get install tesseract-ocr poppler-utils
```

### Error: "Tesseract binary not found"

**Solution:** Check installation:
```bash
which tesseract
# Should return: /usr/bin/tesseract
```

If not found, reinstall:
```bash
sudo apt-get install --reinstall tesseract-ocr
```

### Upload Takes Forever

**Normal for OCR!** Check backend logs to see progress:
```bash
tail -f app.log
```

### No Text Extracted

Some PDFs might have:
- Very low quality scans
- Handwritten text (OCR works best with printed text)
- Non-English text (default is English OCR)

For non-English text, you can install language packs:
```bash
# For Hindi (if your textbook is in Hindi)
sudo apt-get install tesseract-ocr-hin

# For other languages, check: apt-cache search tesseract-ocr
```

## What Files Were Changed

1. **ocr_document_loader.py** - New OCR-enabled document loader
2. **main.py** - Updated to use OCR loader
3. **Pipfile** - Added OCR dependencies

## Reverting (If Needed)

If you want to disable OCR and go back to text-only:

```python
# In main.py, change:
from ocr_document_loader import OCRDocumentLoader
loader = OCRDocumentLoader()

# Back to:
from document_loader import DocumentLoader
loader = DocumentLoader()
```

## Next Steps

1. ✅ Install Tesseract (`sudo apt-get install tesseract-ocr poppler-utils`)
2. ✅ Restart backend
3. ✅ Upload your scanned PDF
4. ✅ Start chatting!

---

**Questions?** Check the main README or the troubleshooting section above.
