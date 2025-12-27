# AI Teacher Project Context

## Project Overview

AI Teacher is an **educational AI assistant platform** that combines local PDF knowledge with real-time web search to provide intelligent, contextual answers for students. The system specializes in Class 9 Mathematics and English education with beautiful LaTeX math rendering and emoji-enriched responses.

**Working Directory**: `/home/evocenta/PycharmProjects/AI_teacher`

## System Architecture

### Full-Stack Application

```
┌─────────────────────────────────────────────────────┐
│  FRONTEND (React 19 + TypeScript + Vite 7.2.2)     │
│  Port: 4200                                         │
│  • ChatWindow, ChatMessage, ChatInput, Studio       │
│  • AnimatedExplanation, LocationMap                 │
│  • ReactMarkdown + KaTeX for LaTeX rendering        │
│  • Server-Sent Events for streaming responses       │
└──────────────┬──────────────────────────────────────┘
               │ HTTP/WebSocket
               ▼
┌─────────────────────────────────────────────────────┐
│  BACKEND (Python 3.12 + FastAPI)                    │
│  Port: 8000                                         │
│  • HybridChatService (session management)           │
│  • HybridRAGAgent (LangGraph state machine)         │
│  • StudioService (quiz, flashcards, reports)        │
│  • ExplanationService (animated explanations)       │
│  • HeyGenService (avatar integration, disabled)     │
└──────────────┬──────────────────────────────────────┘
               │
     ┌─────────┴─────────┐
     ▼                   ▼
┌──────────┐      ┌────────────────┐
│ ChromaDB │      │ OpenAI GPT-4   │
│ Vectors  │      │ + Embeddings   │
│ Local    │      │ + Exa.ai       │
└──────────┘      └────────────────┘
```

### LangGraph Hybrid RAG Agent

The core intelligence uses a **state machine architecture** with parallel search:

```
1. ROUTER NODE
   ↓ Analyzes query intent
   ↓ Routes to: pdf_only / web_only / both / none

2. PARALLEL SEARCH (ThreadPoolExecutor, max_workers=2)
   ├─ PDF Search (ChromaDB similarity search, k=4)
   └─ Web Search (Exa.ai, limit=3, days_back=90)
   ↓ Executes in parallel (20% faster than sequential)

3. COMBINE CONTEXT NODE
   ↓ Merges PDF + Web results
   ↓ Formats for LLM consumption

4. GENERATE ANSWER NODE
   ↓ OpenAI GPT-4 streaming
   ↓ Educational tone with LaTeX formatting
   ↓ Emoji enrichment (📚, 🎓, ✨, 💡)
```

## Technology Stack

### Frontend
- **React 19** with **TypeScript** for type safety
- **Vite 7.2.2** for fast builds and HMR
- **ReactMarkdown 10.1.0** for markdown rendering
- **KaTeX 0.16.25** for LaTeX math rendering ($x^2$, $\frac{a}{b}$)
- **remark-math 6.0.0** + **rehype-katex 7.0.1** for math plugins
- **ReactFlow 11.11.4** for mind maps and diagrams
- **Framer Motion 12.23.26** for animations
- **TanStack Query 5.90.10** for data fetching
- **Tesseract.js 7.0.0** for OCR support

### Backend
- **Python 3.12** with **FastAPI** (async/await)
- **Uvicorn** ASGI server
- **Pydantic** for data validation
- **LangChain** for LLM framework
- **LangGraph** for agent orchestration (state machines)
- **OpenAI GPT-4** (gpt-4o-mini) for language generation
- **OpenAI Embeddings** (text-embedding-3-small, 384 dimensions)
- **ChromaDB** for persistent vector storage
- **Exa.ai API** for web search
- **PyPDF** + **OCR** for document processing

### Dependencies Management
- **Pipenv** for Python (see Pipfile, Pipfile.lock)
- **npm** for Node.js (see frontend/package.json)

## Key Features

### 1. Hybrid RAG (Retrieval-Augmented Generation)
- Combines local PDF knowledge base with real-time web search
- Intelligent routing: query → pdf_only | web_only | both | none
- **Parallel search execution** (20% performance boost)
- Session-based conversation history

### 2. Educational Content Generation
- LaTeX math rendering: `$x^2 + y^2 = r^2$`
- Structured responses with examples
- Emoji enrichment for engagement
- Specialized for Class 9 Mathematics and English

### 3. Studio Features (Studio.tsx)
- **Quizzes**: Auto-generated from conversation history
- **Flashcards**: Key concepts extraction
- **Mind Maps**: Visual knowledge graphs using ReactFlow
- **Reports**: Learning progress summaries

### 4. Animated Explanations
- Step-by-step visual explanations (AnimatedExplanation.tsx)
- Multi-part answer animations
- Synchronized with answer segments

### 5. OCR & Image Processing
- Upload images for text extraction (Tesseract.js)
- Process handwritten or scanned educational content
- Image-based queries

### 6. Location-Based Learning
- LocationMap.tsx for geographical context
- Integration with learning materials

## Directory Structure

```
AI_teacher/
├── backend/
│   ├── main.py                    # FastAPI app & endpoints
│   ├── hybrid_agent.py            # LangGraph state machine ⚡
│   ├── hybrid_chat_service.py     # Chat orchestration
│   ├── studio_service.py          # Quiz, flashcards, reports
│   ├── explanation_service.py     # Animated explanations
│   ├── heygen_service.py          # Avatar integration (disabled)
│   ├── exa_search_tool.py         # Web search (Exa.ai)
│   ├── vector_store.py            # ChromaDB manager
│   ├── config.py                  # Configuration loader
│   ├── models.py                  # Pydantic models
│   ├── document_loader.py         # PDF loading
│   ├── chunker.py                 # Text chunking strategy
│   ├── ocr_document_loader.py     # OCR support
│   └── patterns/                  # Design patterns
│       ├── chunking_strategy.py
│       ├── document_loader_factory.py
│       ├── embedding_factory.py
│       └── vector_repository.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatWindow.tsx         # Main chat UI
│   │   │   ├── ChatMessage.tsx        # Message rendering
│   │   │   ├── ChatInput.tsx          # User input with OCR
│   │   │   ├── Studio.tsx             # Quiz/flashcard/report
│   │   │   ├── AnimatedExplanation.tsx # Step animations
│   │   │   └── LocationMap.tsx        # Geography integration
│   │   ├── services/
│   │   │   └── api.ts                 # Backend API client
│   │   ├── types/
│   │   │   └── chat.ts                # TypeScript types
│   │   ├── App.tsx                    # Root component
│   │   └── main.tsx                   # Entry point
│   ├── package.json
│   └── vite.config.ts
│
├── chroma_db/                     # Vector database storage
├── uploads/                       # Uploaded PDF files
├── .env                           # Environment variables
├── .gitignore
├── Pipfile                        # Python dependencies
├── Pipfile.lock
├── start-backend.sh               # Backend startup script
├── start-all.sh                   # Full stack startup
├── app.log                        # Application logs
├── backend.log
│
└── Documentation/
    ├── SYSTEM_ARCHITECTURE.md     # Complete architecture
    ├── QUICKSTART.md              # Quick start guide
    ├── HYBRID_AGENT_GUIDE.md      # Agent implementation
    ├── DESIGN_PATTERNS.md         # Code patterns
    ├── KNOWLEDGE_MAP_FIX.md       # Mind map implementation
    ├── LATEX_RENDERING_FIX.md     # Math rendering guide
    ├── PDF_UPLOAD_GUIDE.md        # Document upload
    ├── OCR_SETUP.md               # OCR configuration
    └── AVATAR.md                  # HeyGen avatar setup
```

## Environment Configuration (.env)

**CRITICAL**: All API keys MUST be in `.env` file (never hardcode!)

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-...              # Required for LLM & embeddings
OPENAI_API_BASE=https://api.openai.com/v1

USE_OPENAI_EMBEDDINGS=true
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=384

# LLM Configuration
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
MAX_HISTORY_MESSAGES=10

# Vector Database
CHROMA_PERSIST_DIR=./chroma_db
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
DEFAULT_SEARCH_K=4

# Web Search
EXA_API_KEY=...                          # Required for web search
WEB_SEARCH_RESULTS_LIMIT=3
WEB_SEARCH_DAYS_BACK=90

# Hybrid Agent
USE_HYBRID_AGENT=true

# HeyGen Avatar (disabled by default)
ENABLE_HEYGEN_AVATAR=false
# HEYGEN_API_KEY=...
# HEYGEN_AVATAR_ID=...

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## API Endpoints (main.py)

### Health & Info
- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive Swagger UI

### Chat System
- `POST /chat` - Non-streaming chat
- `POST /chat/stream` - **Streaming chat (SSE)** ⭐
- `GET /chat/history/{session_id}` - Get conversation history
- `DELETE /chat/clear/{session_id}` - Clear session

### Document Management
- `POST /upload-pdf` - Upload & process PDFs
- `POST /process-webpages` - Process URLs
- `POST /query` - Direct vector similarity search
- `DELETE /clear-vector-store` - Clear all documents
- `GET /test-embeddings` - Test embedding functionality

### Studio Features
- `POST /studio/generate` - Generate quiz/flashcards/reports

### Explanations
- `POST /explanation/generate` - Generate animated explanations

## Startup Scripts

### Local Development (Without Docker)

#### Full Stack
```bash
./start-all.sh
# Starts backend (port 8000) + frontend (port 4200)
```

#### Backend Only
```bash
./start-backend.sh
# OR
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Only
```bash
cd frontend && npm run dev
```

### Docker Deployment (Recommended for Production)

#### Quick Start
```bash
# Initial setup
make setup

# Start services
make up

# View logs
make logs

# Stop services
make down
```

#### Docker Architecture
```
Host System
├── Frontend Container (nginx:alpine)
│   ├── Port: 4200
│   ├── Built assets from Vite
│   └── API proxy to backend
├── Backend Container (python:3.12-slim)
│   ├── Port: 8000
│   ├── FastAPI + LangGraph
│   └── Vector DB + Uploads
└── Docker Volumes
    ├── chroma_data (ChromaDB persistence)
    ├── uploads_data (PDF files)
    └── logs (Application logs)
```

#### Key Docker Files
- `docker-compose.yml` - Orchestration configuration
- `backend/Dockerfile` - Backend container definition
- `frontend/Dockerfile` - Frontend container with nginx
- `frontend/nginx.conf` - Nginx reverse proxy config
- `Makefile` - Convenient management commands
- `DOCKER_DEPLOYMENT.md` - Complete Docker guide
- `DOCKER_QUICKSTART.md` - Quick start guide

#### Docker Commands
```bash
make help          # Show all available commands
make setup         # Initial setup (copy .env, build, start)
make up            # Start all services
make down          # Stop all services
make logs          # View logs (all services)
make logs-backend  # View backend logs only
make restart       # Restart services
make backup        # Backup data volumes
make clean         # Remove containers
make rebuild       # Rebuild from scratch
make shell-backend # Access backend container shell
```

## Core Services Explained

### HybridChatService (hybrid_chat_service.py)
- **Purpose**: Session management & streaming coordination
- **Key Methods**:
  - `stream_chat()`: Handles SSE streaming
  - `get_session_history()`: Retrieves conversation history
  - `clear_session()`: Clears chat session
- **Session Storage**: In-memory dictionary (session_id → messages)

### HybridRAGAgent (hybrid_agent.py)
- **Purpose**: LangGraph state machine for intelligent retrieval
- **State**: TypedDict with messages, contexts, sources, routing decisions
- **Nodes**:
  1. `route_query` - LLM-based intent classification
  2. `parallel_search_node` - Concurrent PDF + Web search
  3. `combine_context` - Merge and format contexts
  4. `generate_answer` - OpenAI streaming response
- **Performance**: Parallel execution saves ~20% time

### StudioService (studio_service.py)
- **Purpose**: Generate educational content from chat history
- **Content Types**:
  - **Quizzes**: Multiple choice questions
  - **Flashcards**: Front/back cards with key concepts
  - **Reports**: Learning progress summaries
- **Input**: session_id, content_type
- **Output**: Structured JSON data

### ExplanationService (explanation_service.py)
- **Purpose**: Generate step-by-step animated explanations
- **Process**:
  1. Analyze user question + assistant answer
  2. Break down into logical steps
  3. Create animation timeline
  4. Generate optional audio narration (disabled)
- **Output**: Animation data structure for frontend

### VectorStoreManager (vector_store.py)
- **Purpose**: ChromaDB operations wrapper
- **Operations**:
  - Add documents (chunked text with metadata)
  - Similarity search (cosine similarity)
  - Clear store
  - Get collection info
- **Persistence**: Local disk (`./chroma_db`)

## Design Patterns

### Factory Pattern
- `DocumentLoaderFactory` (patterns/document_loader_factory.py)
- `EmbeddingFactory` (patterns/embedding_factory.py)

### Strategy Pattern
- `ChunkingStrategy` (patterns/chunking_strategy.py)
  - RecursiveChunkingStrategy
  - SimpleChunkingStrategy

### Repository Pattern
- `VectorRepository` (patterns/vector_repository.py)

## Frontend Components Explained

### ChatWindow.tsx
- **Purpose**: Main chat interface
- **Features**:
  - Message display with streaming
  - User input handling
  - Session management
  - Source citations
  - Studio integration button
- **State Management**: React hooks (useState, useEffect)

### ChatMessage.tsx
- **Purpose**: Render individual messages
- **Features**:
  - Markdown rendering (ReactMarkdown)
  - LaTeX math (KaTeX via rehype-katex)
  - Syntax highlighting for code
  - User/assistant styling
- **Math Support**: `$...$` inline, `$$...$$` block

### ChatInput.tsx
- **Purpose**: User input with enhancements
- **Features**:
  - Text input with Enter/Shift+Enter
  - Image upload for OCR
  - Tesseract.js integration
  - Loading states
- **OCR Flow**: Image → Tesseract → Extracted text → Chat

### Studio.tsx
- **Purpose**: Educational content generation UI
- **Features**:
  - Quiz generation with scoring
  - Flashcard deck viewer
  - Mind map visualization (ReactFlow + dagre layout)
  - Report generation
- **Integration**: Uses session history via `/studio/generate`

### AnimatedExplanation.tsx
- **Purpose**: Step-by-step visual explanations
- **Features**:
  - Sequential animation of explanation steps
  - Auto-play with configurable timing
  - Synchronized with answer content
  - Handles multi-part answers
- **Animation**: Framer Motion for smooth transitions

### LocationMap.tsx
- **Purpose**: Geographical context for learning
- **Features**:
  - Interactive map display
  - Location-based educational content
  - Integration with geography lessons

## Data Flow Examples

### Example 1: Chat with PDF + Web Search
```
User: "Explain rational numbers AND what's new in AI?"
  ↓
Frontend POST /chat/stream {message, session_id, use_rag: true}
  ↓
HybridChatService.stream_chat()
  ↓
HybridRAGAgent.query()
  ↓
Router Node: Decision = "both"
  ↓
Parallel Search:
  ├─ PDF: ChromaDB similarity search → 4 chunks
  └─ Web: Exa.ai search → 3 articles
  ↓ (executes simultaneously)
Combine Context: Merge PDF + Web
  ↓
Generate Answer: OpenAI GPT-4 streaming
  ↓
Server-Sent Events:
  data: {type: "chunk", content: "**Rational Numbers** 📚\n..."}
  data: {type: "sources", sources: [...]}
  data: {type: "done"}
  ↓
Frontend: ReactMarkdown + KaTeX rendering
  ↓
User sees: Beautiful formatted answer with math & sources
```

### Example 2: Generate Quiz from Chat
```
User clicks "Generate Quiz" in Studio
  ↓
Frontend POST /studio/generate {session_id, content_type: "quiz"}
  ↓
StudioService.generate_quiz(session_id)
  ↓
1. Fetch session history (all Q&A pairs)
2. Analyze conversation topics
3. Generate 5 multiple choice questions
4. Format as JSON: {questions: [{question, options, correct}]}
  ↓
Frontend renders quiz UI with scoring
  ↓
User answers → Frontend calculates score → Display results
```

### Example 3: OCR Image Upload
```
User uploads image in ChatInput
  ↓
Tesseract.js processes image
  ↓
Extracted text displayed for user confirmation
  ↓
User clicks "Send" → POST /chat/stream {message: "", extracted_text: "..."}
  ↓
Backend processes extracted text as user query
  ↓
Same hybrid RAG flow as Example 1
```

## Development Workflow

### Starting Development
```bash
# 1. Activate Python environment
pipenv shell

# 2. Start full stack
./start-all.sh

# 3. Access application
# Frontend: http://localhost:4200
# Backend: http://localhost:8000/docs
```

### Adding New Features

#### Backend (Python)
1. Define Pydantic models in `backend/models.py`
2. Add endpoint in `backend/main.py`
3. Implement service logic in appropriate service file
4. Update `.env` if new configuration needed
5. Test via Swagger UI at `/docs`

#### Frontend (React)
1. Define TypeScript types in `frontend/src/types/`
2. Create/update component in `frontend/src/components/`
3. Add API call in `frontend/src/services/api.ts`
4. Test in browser at `http://localhost:4200`

### Common Tasks

#### Upload New PDFs
```bash
# Manual via API
curl -X POST "http://localhost:8000/upload-pdf" \
  -F "files=@document.pdf"

# Batch upload script
python upload_pdfs_batch.py
```

#### Clear Vector Store
```bash
curl -X DELETE "http://localhost:8000/clear-vector-store"
```

#### View Logs
```bash
tail -f app.log        # Combined logs
tail -f backend.log    # Backend only
```

## Performance Considerations

### Parallel Search Optimization
- **Before**: Sequential PDF → Web (10 seconds total)
- **After**: Parallel PDF || Web (8 seconds total)
- **Gain**: 20% faster response times

### Streaming Responses
- Uses Server-Sent Events (SSE) for real-time streaming
- Better UX: Users see responses as they're generated
- Lower perceived latency

### ChromaDB Persistence
- Vector store persists to disk (`./chroma_db`)
- No re-indexing needed on restart
- Fast similarity search with cosine distance

### Frontend Optimization
- Vite for fast HMR (Hot Module Replacement)
- React 19 with modern concurrent features
- Code splitting with dynamic imports

## Common Issues & Solutions

### Issue: "OPENAI_API_KEY not found"
**Solution**: Verify `.env` file exists and contains valid key
```bash
# Check .env file
cat .env | grep OPENAI_API_KEY

# Restart backend to reload environment
./start-backend.sh
```

### Issue: LaTeX not rendering
**Solution**: Check math plugin configuration
- Ensure `remark-math` and `rehype-katex` are installed
- Use correct delimiters: `$...$` inline, `$$...$$` block
- Import KaTeX CSS in component

### Issue: ChromaDB persistence errors
**Solution**: Clear and reinitialize
```bash
# Backup existing
mv chroma_db chroma_db.backup

# Reinitialize (will create new on next run)
./start-backend.sh
```

### Issue: Web search not working
**Solution**: Verify Exa.ai API key in `.env`
```bash
cat .env | grep EXA_API_KEY
# Should show: EXA_API_KEY=2b5d818d-...
```

## Testing

### Backend Testing
```bash
# Manual testing via Swagger UI
# http://localhost:8000/docs

# Test embeddings
curl http://localhost:8000/test-embeddings

# Health check
curl http://localhost:8000/health
```

### Frontend Testing
```bash
cd frontend
npm run lint    # ESLint
npm run build   # Test build
```

## Git Workflow

### Current State
- **Branch**: main
- **Modified Files**: Backend services, frontend components
- **Untracked**: AVATAR.md, chroma_db backups

### Commit Strategy
- Commit after completing features
- Clear, descriptive commit messages
- Reference issue numbers if applicable

## Key Documentation Files

Read these for detailed information:
- `SYSTEM_ARCHITECTURE.md` - Complete architecture diagrams
- `HYBRID_AGENT_GUIDE.md` - LangGraph agent implementation
- `DESIGN_PATTERNS.md` - Code patterns used
- `QUICKSTART.md` - Quick start guide
- `LATEX_RENDERING_FIX.md` - Math rendering troubleshooting
- `KNOWLEDGE_MAP_FIX.md` - Mind map implementation details
- `PDF_UPLOAD_GUIDE.md` - Document upload workflows
- `OCR_SETUP.md` - OCR configuration
- `AVATAR.md` - HeyGen avatar integration (disabled)

## Recent Changes (from git log)

1. **"Fix animated explanation to cover all statements"** (628bd1b)
   - Fixed multi-part answer animations

2. **"mindmap & quiz"** (ab6bc32)
   - Added mind map and quiz features

3. **"update frontend"** (ae03537)
   - Frontend component updates

4. **"logger fixed"** (7a46dac)
   - Logging improvements

5. **"router agent"** (f527252)
   - Implemented LangGraph router

## Project Goals & Philosophy

### Educational Focus
- Make learning engaging with emojis and visuals
- Provide accurate, well-cited information
- Support visual learners with math rendering
- Interactive learning through quizzes and flashcards

### Technical Excellence
- Modern, type-safe frontend (TypeScript)
- Robust backend with proper error handling
- Modular, maintainable code structure
- Performance optimization (parallel search)

### User Experience
- Real-time streaming responses
- Beautiful LaTeX math rendering
- Intuitive chat interface
- Studio for content generation

## Future Enhancements

### Planned Features
- HeyGen avatar integration (currently disabled)
- Voice input/output
- Multi-language support
- Advanced analytics dashboard
- Mobile app

### Technical Improvements
- Unit tests (pytest for backend)
- E2E tests (Playwright for frontend)
- CI/CD pipeline
- Docker containerization
- Cloud deployment (AWS/GCP)

---

**Last Updated**: 2025-12-26
**Project Status**: Active Development
**Team**: Solo developer (evocenta)
