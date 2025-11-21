# AI Teacher - Full Stack RAG Chatbot

A complete chatbot application with:
- **Backend**: FastAPI + LangChain RAG + OpenAI
- **Frontend**: React + TypeScript + Vite
- **Features**: Document upload, streaming responses, conversation history

## Architecture

```
Backend (FastAPI)                    Frontend (React)
├── FastAPI REST API                 ├── Chat UI Components
├── LangChain RAG Pipeline          ├── Streaming Chat
├── Chroma Vector Store             ├── File Upload
├── OpenAI LLM Integration          └── Markdown Rendering
└── Conversation Memory
```

## Prerequisites

- Python 3.12+
- Node.js 18+
- OpenAI API Key (for LLM and embeddings)

## Backend Setup

### 1. Install Dependencies

```bash
cd /home/evocenta/PycharmProjects/AI_teacher
pipenv install
```

### 2. Configure Environment

Create or update `.env` file:

```bash
# Required for LLM
OPENAI_API_KEY=sk-proj-your-key-here

# Embedding Configuration
USE_OPENAI_EMBEDDINGS=true
EMBEDDING_MODEL=text-embedding-3-small

# LLM Configuration
LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.7
MAX_HISTORY_MESSAGES=10

# Storage
CHROMA_PERSIST_DIR=./chroma_db

# Chunking
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Search
DEFAULT_SEARCH_K=4

# Logging
LOG_LEVEL=INFO
```

### 3. Start Backend Server

```bash
pipenv run python main.py
```

Backend will run on: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

The `.env` file already exists with:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Start Frontend Dev Server

```bash
npm run dev
```

Frontend will run on: **http://localhost:5173**

## Using the Application

### 1. Upload Documents

Click the 📎 button in the chat interface to upload PDF files. The documents will be:
- Chunked into manageable pieces
- Converted to embeddings
- Stored in the vector database

### 2. Chat with Your Documents

Type your questions in the chat input. The AI will:
- Search relevant document chunks
- Use them as context for the LLM
- Stream responses in real-time
- Show source citations

### 3. Features

- **Streaming Responses**: See AI responses as they're generated
- **Source Citations**: View which documents informed each answer
- **Conversation History**: Maintains context across messages
- **Session Management**: Clear history with the 🗑️ button

## API Endpoints

### Chat Endpoints

- `POST /chat` - Send a chat message (non-streaming)
- `POST /chat/stream` - Stream chat responses
- `GET /chat/history/{session_id}` - Get chat history
- `DELETE /chat/clear/{session_id}` - Clear session

### Document Endpoints

- `POST /upload-pdf` - Upload PDF files
- `POST /process-webpages` - Process web pages
- `POST /query` - Query vector store (raw search)
- `DELETE /clear-vector-store` - Clear all documents

### Utility Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `GET /test-embeddings` - Test embedding setup

## Development

### Backend Development

```bash
# Run with auto-reload
pipenv run python main.py

# Run tests (if available)
pipenv run pytest

# Check logs
tail -f app.log
```

### Frontend Development

```bash
# Dev server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Project Structure

```
AI_teacher/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── chat_service.py         # Chat + RAG logic
│   ├── vector_store.py         # Vector DB management
│   ├── document_loader.py      # PDF/web loading
│   ├── chunker.py              # Document chunking
│   ├── config.py               # Configuration
│   └── models.py               # Pydantic models
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatWindow.tsx    # Main chat container
│   │   │   ├── ChatMessage.tsx   # Message component
│   │   │   └── ChatInput.tsx     # Input component
│   │   ├── services/
│   │   │   └── api.ts            # Backend API client
│   │   ├── types/
│   │   │   └── chat.ts           # TypeScript types
│   │   └── App.tsx               # Root component
│   └── package.json
│
└── README.md
```

## Troubleshooting

### Backend Issues

**OpenAI API Key Error**
```
ValueError: OPENAI_API_KEY not found
```
→ Set `OPENAI_API_KEY` in `.env` file

**Vector Store Not Found**
```
Error loading vector store
```
→ Upload documents first using the chat interface

**CORS Error**
```
CORS policy blocked
```
→ Backend CORS is configured for all origins in development

### Frontend Issues

**API Connection Failed**
```
Connection error
```
→ Ensure backend is running on http://localhost:8000

**Cannot Find Module**
```
Cannot find module 'axios'
```
→ Run `npm install` in the frontend directory

**Build Errors**
```
TypeScript errors
```
→ Check that all types are correctly imported

## Production Deployment

### Backend

1. Set production environment variables
2. Use a production WSGI server (e.g., Gunicorn)
3. Configure CORS for specific origins
4. Set up persistent storage for vector DB

### Frontend

1. Update `VITE_API_BASE_URL` to production backend URL
2. Build: `npm run build`
3. Serve `dist` folder with nginx/Apache
4. Configure CDN for static assets

## License

MIT

## Support

For issues, please open a ticket on the repository.
