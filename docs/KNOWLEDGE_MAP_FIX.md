# Knowledge Map Fix Documentation

## Problem Summary
The Knowledge Map was not displaying PDF source information (filename and page numbers) in the chat interface, even though the backend was sending this data correctly.

## Root Cause
The issue was caused by **incorrect data extraction in the API service**:
- Backend sends sources in a nested structure: `data.sources.sources`
- Frontend API service was passing the entire wrapper object instead of extracting the actual array
- ChatMessage component received the wrong data structure and couldn't display sources

### Data Structure Mismatch

**Backend Response Structure:**
```json
{
  "type": "sources",
  "sources": {
    "sources": [                    // <-- Actual array is nested here
      {
        "content": "...",
        "metadata": {
          "source": "uploads/iemh1a1.pdf",
          "page": 4
        }
      }
    ],
    "pdf_sources": [...],
    "web_sources": [],
    "total_sources": 2,
    "has_pdf": true,
    "has_web": false
  },
  "session_id": "..."
}
```

**Frontend Expected Structure:**
```typescript
interface Source {
  content: string;
  metadata: {
    source: string;    // Full path: "uploads/filename.pdf"
    page?: number;
  };
}
```

## Solution

### 1. Fix API Service Data Extraction

**File:** `/home/evocenta/PycharmProjects/AI_teacher/frontend/src/services/api.ts`

**Line 70 - Before:**
```typescript
case 'sources':
  onSources(data.sources, data.session_id);
  break;
```

**Line 70 - After:**
```typescript
case 'sources':
  // Extract the sources array from the nested structure
  onSources(data.sources.sources || data.sources, data.session_id);
  break;
```

**Why this works:**
- `data.sources.sources` extracts the actual array from the nested structure
- Fallback to `data.sources` for backward compatibility
- Now passes correct array structure to ChatWindow component

### 2. Add Knowledge Map Display Component

**File:** `/home/evocenta/PycharmProjects/AI_teacher/frontend/src/components/ChatMessage.tsx`

**Lines 37-64 - Added Knowledge Map Section:**
```typescript
{/* Knowledge Map - Show sources */}
{message.sources && message.sources.length > 0 && (
  <div className="knowledge-map">
    <div className="knowledge-map-header">
      📚 Knowledge Map ({message.sources.length} source{message.sources.length > 1 ? 's' : ''})
    </div>
    <div className="knowledge-map-items">
      {message.sources.map((source, index) => {
        // Extract filename from full path (e.g., "uploads/iemh102.pdf" -> "iemh102.pdf")
        const filename = source.metadata.source.split('/').pop() || source.metadata.source;

        return (
          <div key={index} className="knowledge-map-item">
            <div className="source-header">
              <span className="source-file">📄 {filename}</span>
              {source.metadata.page && (
                <span className="source-page">Page {source.metadata.page}</span>
              )}
            </div>
            <div className="source-content">
              {source.content.substring(0, 150)}...
            </div>
          </div>
        );
      })}
    </div>
  </div>
)}
```

**Key Features:**
- Conditional rendering only when sources exist
- Filename extraction using `split('/').pop()`
- Page number badge display
- Content preview (first 150 characters)
- Proper pluralization ("1 source" vs "2 sources")

### 3. Add Knowledge Map Styling

**File:** `/home/evocenta/PycharmProjects/AI_teacher/frontend/src/components/ChatMessage.css`

**Lines 134-203 - Added Styles:**
```css
/* Knowledge Map Styles */
.knowledge-map {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 2px solid #e8eaf6;
}

.knowledge-map-header {
  font-weight: 600;
  font-size: 0.95rem;
  color: #5e35b1;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.knowledge-map-items {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.knowledge-map-item {
  background: linear-gradient(135deg, #f5f7fa 0%, #f0f3f8 100%);
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  padding: 0.75rem;
  transition: all 0.2s ease;
}

.knowledge-map-item:hover {
  border-color: #5e35b1;
  box-shadow: 0 2px 8px rgba(94, 53, 177, 0.1);
  transform: translateY(-1px);
}

.source-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.knowledge-map-item .source-file {
  font-weight: 600;
  font-size: 0.85rem;
  color: #333;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.source-page {
  background: #5e35b1;
  color: white;
  padding: 0.15rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.knowledge-map-item .source-content {
  color: #666;
  font-size: 0.8rem;
  line-height: 1.4;
  font-style: italic;
}
```

**Design Features:**
- Purple theme (#5e35b1) for consistency
- Gradient background with subtle hover effect
- Badge-style page numbers
- Responsive flexbox layout
- Italic font for content preview
- Transform animation on hover

## Verification

### Backend Verification
```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "explain x squared >= x", "session_id": "test123", "use_rag": true}' \
  2>/dev/null | grep -A 20 '"type": "sources"'
```

**Expected Output:**
```json
data: {"type": "sources", "sources": {"sources": [
  {"content": "...", "metadata": {"source": "uploads/iemh1a1.pdf", "page": 4}},
  {"content": "...", "metadata": {"source": "uploads/iemh102.pdf", "page": 2}}
]}}
```

### Frontend Testing
1. **Hard refresh:** `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac)
2. **Clear chat session:** Click 🗑️ button
3. **Ask question:** "Explain the inequality x squared >= x"
4. **Verify display:** Knowledge Map should show:
   ```
   📚 Knowledge Map (2 sources)

   ┌─────────────────────────────────┐
   │ 📄 iemh1a1.pdf        Page 4    │
   │ "they become true statements..." │
   └─────────────────────────────────┘

   ┌─────────────────────────────────┐
   │ 📄 iemh102.pdf        Page 2    │
   │ "26 MATHEMATICS Now, consider..." │
   └─────────────────────────────────┘
   ```

## Troubleshooting

### Problem: Knowledge Map still not showing

**Possible Causes:**
1. Browser cache contains old JavaScript bundle
2. Service file changes not picked up by HMR

**Solutions:**
1. **Hard refresh:** `Ctrl + Shift + R` or `Cmd + Shift + R`
2. **Clear application cache:**
   - Press F12 → Application tab (Chrome) or Storage tab (Firefox)
   - Click "Clear site data"
   - Close DevTools and refresh
3. **Restart dev server:**
   ```bash
   cd frontend
   npm run dev
   ```

### Problem: Shows "undefined" or empty sources

**Cause:** API service not extracting nested array correctly

**Solution:** Verify line 70 in `api.ts` uses:
```typescript
onSources(data.sources.sources || data.sources, data.session_id);
```

### Problem: Filename shows full path like "uploads/file.pdf"

**Cause:** Filename extraction not working

**Solution:** Verify ChatMessage.tsx line 46:
```typescript
const filename = source.metadata.source.split('/').pop() || source.metadata.source;
```

## Technical Details

### Data Flow
1. **User sends message** → ChatWindow.tsx
2. **API streams response** → api.ts (line 32-89)
3. **Parse sources event** → api.ts line 68-70
4. **Extract nested array** → `data.sources.sources`
5. **Pass to callback** → ChatWindow.tsx line 74
6. **Create message with sources** → ChatWindow.tsx line 77-83
7. **Render in ChatMessage** → ChatMessage.tsx line 38-64
8. **Display Knowledge Map** → With filename and page number

### Why Nested Structure?
The backend wraps sources in an object to provide metadata:
- `sources`: The actual array
- `pdf_sources`: PDF-specific sources
- `web_sources`: Web search results
- `total_sources`: Count
- `has_pdf`, `has_web`: Boolean flags
- `route_used`: Which retrieval method was used

The frontend only needs the `sources` array for display.

### TypeScript Interfaces

**Already Defined in `/frontend/src/types/chat.ts`:**
```typescript
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Source[];  // Optional sources array
}

export interface Source {
  content: string;
  metadata: {
    source: string;    // Full path
    page?: number;     // Optional page number
  };
}
```

## Date Fixed
2025-11-28

## Related Files
- `/home/evocenta/PycharmProjects/AI_teacher/frontend/src/services/api.ts` (line 70)
- `/home/evocenta/PycharmProjects/AI_teacher/frontend/src/components/ChatMessage.tsx` (lines 37-64)
- `/home/evocenta/PycharmProjects/AI_teacher/frontend/src/components/ChatMessage.css` (lines 134-203)
- `/home/evocenta/PycharmProjects/AI_teacher/frontend/src/types/chat.ts` (Source interface)

## Summary
The Knowledge Map now correctly displays PDF sources with filenames and page numbers by:
1. Extracting the nested sources array in api.ts
2. Rendering the sources in a styled component in ChatMessage.tsx
3. Providing visual feedback with filename, page badges, and content previews
