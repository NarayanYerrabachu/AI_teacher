# 🚀 Quick Start Guide

Get your AI Teacher chatbot running in 3 steps!

## Prerequisites Check

```bash
# Check Python version (need 3.12+)
python --version

# Check Node.js version (need 18+)
node --version

# Check if you have pipenv
pipenv --version
```

## Step 1: Configure Backend

1. Make sure you have an OpenAI API key
2. Open `.env` file in the project root
3. Set your API key:
   ```
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ```

## Step 2: Start Backend Server

Open Terminal 1:

```bash
cd /home/evocenta/PycharmProjects/AI_teacher

# Option A: Use the start script
./start-backend.sh

# Option B: Run directly
pipenv run python main.py
```

**Wait for:** "Application startup complete" message

**Backend URL:** http://localhost:8000
**API Docs:** http://localhost:8000/docs

## Step 3: Start Frontend

Open Terminal 2 (keep Terminal 1 running):

```bash
cd /home/evocenta/PycharmProjects/AI_teacher/frontend

# Option A: Use the start script
./start-frontend.sh

# Option B: Run directly
npm run dev
```

**Wait for:** "Local: http://localhost:5173" message

**Frontend URL:** http://localhost:5173

## Step 4: Use the Chatbot

1. Open http://localhost:5173 in your browser
2. Click the 📎 button to upload PDF files
3. Wait for "✓ Uploaded" confirmation
4. Ask questions about your documents!

## Example Questions

After uploading documents, try:
- "What is this document about?"
- "Summarize the main points"
- "Explain [specific topic] from the document"

## Quick Commands Reference

```bash
# Backend
cd /home/evocenta/PycharmProjects/AI_teacher
pipenv run python main.py

# Frontend
cd /home/evocenta/PycharmProjects/AI_teacher/frontend
npm run dev

# Build frontend for production
npm run build

# View API documentation
open http://localhost:8000/docs
```

## Troubleshooting

### Backend won't start

**Error:** "OPENAI_API_KEY not found"
```bash
# Edit .env file and add your key
nano .env
```

**Error:** "Module not found"
```bash
cd /home/evocenta/PycharmProjects/AI_teacher
pipenv install
```

### Frontend won't start

**Error:** "Cannot find module"
```bash
cd frontend
npm install
```

**Error:** "Connection error in chat"
→ Make sure backend is running on port 8000

### Chat not working

**No response from AI**
→ Check that documents are uploaded (look for ✓ confirmation)

**Slow responses**
→ First request takes longer (loading models)

**"Vector store not found" error**
→ Upload at least one document first

## Features

✅ **Streaming Responses** - See AI typing in real-time
✅ **Source Citations** - Click "📚 Sources" to see where answers came from
✅ **Conversation Memory** - AI remembers context within a session
✅ **Multiple Documents** - Upload multiple PDFs at once
✅ **Markdown Support** - AI responses with formatting

## Development Mode

Both servers run in development mode with hot-reload:
- Backend: Changes to `.py` files auto-reload
- Frontend: Changes to `.tsx` files instantly update

## Next Steps

- Read [FULLSTACK_README.md](./FULLSTACK_README.md) for detailed documentation
- Explore the API at http://localhost:8000/docs
- Customize the UI in `frontend/src/components/`
- Adjust AI behavior in `chat_service.py`

## Stop Servers

Press `Ctrl+C` in each terminal window to stop the servers.

---

**Need Help?** Check the full documentation in FULLSTACK_README.md
