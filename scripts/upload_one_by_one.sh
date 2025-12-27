#!/usr/bin/env bash
# Upload PDFs one at a time to avoid memory issues

set -e

API_URL="http://localhost:8000/upload-pdf"

echo "=== PDF Upload Script ==="
echo "Uploading PDFs one at a time with 3-second delays"
echo ""

# Mathematics PDFs
MATH_DIR="/home/evocenta/Dokumente/Mathematics-20251121T093622Z-1-001/Mathematics"
count=0
total=0

if [ -d "$MATH_DIR" ]; then
    math_pdfs=("$MATH_DIR"/*.pdf)
    total=$((total + ${#math_pdfs[@]}))
fi

# English PDFs
ENGLISH_DIR="/home/evocenta/Dokumente/English - Beehive-20251121T095800Z-1-001/English - Beehive"
if [ -d "$ENGLISH_DIR" ]; then
    english_pdfs=("$ENGLISH_DIR"/*.pdf)
    total=$((total + ${#english_pdfs[@]}))
fi

echo "Found $total PDF files total"
echo ""

# Upload Mathematics PDFs
if [ -d "$MATH_DIR" ]; then
    for pdf in "$MATH_DIR"/*.pdf; do
        count=$((count + 1))
        filename=$(basename "$pdf")
        echo "[$count/$total] Uploading: $filename"

        if curl -X POST "$API_URL" \
            -F "files=@$pdf" \
            -H "accept: application/json" \
            --silent --show-error --fail \
            --max-time 120; then
            echo "  ✓ Success"
        else
            echo "  ✗ Failed"
        fi

        echo ""
        sleep 3
    done
fi

# Upload English PDFs
if [ -d "$ENGLISH_DIR" ]; then
    for pdf in "$ENGLISH_DIR"/*.pdf; do
        count=$((count + 1))
        filename=$(basename "$pdf")
        echo "[$count/$total] Uploading: $filename"

        if curl -X POST "$API_URL" \
            -F "files=@$pdf" \
            -H "accept: application/json" \
            --silent --show-error --fail \
            --max-time 120; then
            echo "  ✓ Success"
        else
            echo "  ✗ Failed"
        fi

        echo ""
        sleep 3
    done
fi

echo "=== Upload Complete ==="
echo "Uploaded $count files"
