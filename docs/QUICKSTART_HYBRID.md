# Quick Start: Hybrid RAG Agent

Get your hybrid PDF + Web search agent running in 5 minutes!

## Step 1: Install Dependencies (2 minutes)

```bash
cd /home/evocenta/PycharmProjects/AI_teacher
pipenv install
```

This installs:
- `langgraph` - Agent orchestration
- `exa-py` - Web search API

## Step 2: Verify Configuration (30 seconds)

Check your `.env` file has the Exa API key:

```bash
cat .env | grep EXA_API_KEY
```

Should show:
```
EXA_API_KEY=2b5d818d-e693-40aa-9cb7-0f5a0a8d9c9b
```

✅ Already configured!

## Step 3: Test the System (2 minutes)

### Test 1: Web Search

```bash
pipenv run python exa_search_tool.py
```

Expected output:
```
=== Testing Exa Search ===
Found 3 results:
1. Latest developments in artificial intelligence
   URL: https://...
   Score: 0.892
```

### Test 2: Hybrid Agent

```bash
pipenv run python hybrid_agent.py
```

Tests all routing modes:
- PDF only (textbook queries)
- Web only (recent info)
- Both (comprehensive)
- None (greetings)

### Test 3: Chat Service

```bash
pipenv run python hybrid_chat_service.py
```

Interactive test with streaming responses.

## Step 4: Choose Integration Method

### Option A: Replace Existing Service (Recommended)

Edit `main.py` (around line 80):

```python
# BEFORE:
from simple_chat_service import SimpleChatService
chat_service = SimpleChatService()

# AFTER:
from hybrid_chat_service import HybridChatService
chat_service = HybridChatService()
```

That's it! All existing endpoints work the same.

### Option B: Add as New Endpoint

Keep both services and add a new endpoint:

```python
# In main.py

from simple_chat_service import SimpleChatService
from hybrid_chat_service import HybridChatService

# Initialize both
simple_service = SimpleChatService()
hybrid_service = HybridChatService()

# Add new endpoint
@app.post("/chat-hybrid")
async def chat_hybrid(request: ChatRequest):
    """Chat with hybrid PDF + Web search"""
    async def generate():
        async for chunk, session_id, sources in hybrid_service.chat_stream(
            request.message,
            request.session_id,
            use_hybrid=True
        ):
            # Format and yield...
            pass

    return StreamingResponse(generate(), media_type="text/event-stream")
```

## Step 5: Test API (1 minute)

### Test Textbook Query (PDF)

```bash
curl -X POST "http://localhost:8000/chat-stream" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are rational numbers?", "session_id": null}'
```

Should return textbook content from Class 9 Math.

### Test Recent Info Query (Web)

```bash
curl -X POST "http://localhost:8000/chat-stream" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the latest AI developments in 2024?", "session_id": null}'
```

Should return recent web articles.

### Test Hybrid Query (Both)

```bash
curl -X POST "http://localhost:8000/chat-stream" \
  -H "Content-Type: application/json" \
  -d '{"message": "How do modern computers use fractions?", "session_id": null}'
```

Should combine textbook math + web sources about computing.

## Done! 🎉

Your hybrid agent is ready. Try these queries:

### Textbook Queries
- "Explain rational numbers from Chapter 1"
- "What is section 1.2 about?"
- "Give me examples of irrational numbers"

### Current Info Queries
- "Latest machine learning breakthroughs 2024"
- "Current trends in quantum computing"
- "Recent developments in renewable energy"

### Hybrid Queries
- "How are polynomials used in modern cryptography?"
- "Real-world applications of trigonometry today"
- "Evolution of mathematical notation"

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'langgraph'`

```bash
pipenv install langgraph exa-py
```

### Issue: `EXA_API_KEY not found`

```bash
echo "EXA_API_KEY=2b5d818d-e693-40aa-9cb7-0f5a0a8d9c9b" >> .env
```

### Issue: Web search returns no results

Check Exa.ai API status:
```bash
curl https://api.exa.ai/search -H "x-api-key: 2b5d818d-e693-40aa-9cb7-0f5a0a8d9c9b"
```

## Next Steps

- Read [HYBRID_AGENT_GUIDE.md](./HYBRID_AGENT_GUIDE.md) for full documentation
- Customize routing logic in `hybrid_agent.py`
- Update frontend to display dual sources (PDF + Web)
- Add more search providers (Wikipedia, arXiv, etc.)

## Questions?

Check the logs:
```bash
tail -f app.log
```

Enable debug mode in `.env`:
```
LOG_LEVEL=DEBUG
```

---

Happy learning! 🚀📚🌐
