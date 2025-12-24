---
name: ai-teacher-assistant
description: Development assistant for the AI Teacher educational platform. Use this skill when working with the full-stack Python FastAPI + React TypeScript application for AI-powered education, including chat services, mind maps, flash cards, PDF processing, studio components, location maps, and Exa search integration. Invoke for tasks involving backend services (hybrid_chat_service.py, exa_search_tool.py, studio_service.py), frontend components (ChatWindow, Studio, LocationMap, ChatMessage), or when debugging the educational AI system.
---

# AI Teacher Development Assistant

This skill provides specialized assistance for developing and maintaining the AI Teacher educational platform.

## Project Overview

AI Teacher is a full-stack educational platform that combines:
- **Backend**: Python FastAPI services with hybrid chat capabilities, Exa search integration, and ChromaDB vector storage
- **Frontend**: React TypeScript application with interactive chat, mind maps, flash cards, and studio components
- **AI Features**: LLM-powered educational content generation, PDF processing, and intelligent tutoring

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: ChromaDB for vector storage
- **AI Integration**: LLM services via hybrid chat
- **Search**: Exa API for web search capabilities
- **File Processing**: PDF upload and batch processing support

### Frontend
- **Framework**: React with TypeScript
- **UI Components**:
  - ChatWindow and ChatMessage for conversations
  - Studio for content creation
  - LocationMap for geographical context
  - Flash cards for learning reinforcement
- **Styling**: CSS modules
- **Build**: Vite/npm build system

## Key Services

### Backend Services (`/backend`)
- `hybrid_chat_service.py` - Core chat orchestration
- `exa_search_tool.py` - Web search integration
- `studio_service.py` - Content studio functionality
- `main.py` - FastAPI application entry point
- `models.py` - Data models and schemas

### Frontend Components (`/frontend/src/components`)
- `ChatWindow.tsx` - Main chat interface
- `ChatMessage.tsx` - Individual message rendering
- `ChatInput.tsx` - User input handling
- `Studio.tsx` - Content creation interface
- `LocationMap.tsx` - Geographic visualization

## Development Workflow

### Starting Services
```bash
./start-all.sh  # Starts both backend and frontend
```

### Code Quality
- **Testing**: pytest for backend (100% enforcement)
- **Linting**: pre-commit hooks configured
- **Type Checking**: TypeScript strict mode for frontend

### Environment Configuration
- Backend uses `.env` files for API keys (Exa, OpenAI, etc.)
- Never hardcode credentials
- Verify environment loading on startup

## Common Tasks

### Backend Development
- Adding new chat capabilities to `hybrid_chat_service.py`
- Integrating new search providers in `exa_search_tool.py`
- Extending data models in `models.py`
- API endpoint development in `main.py`

### Frontend Development
- Enhancing chat UI in ChatWindow/ChatMessage components
- Building educational tools (flash cards, mind maps)
- Styling with component-specific CSS files
- Type-safe API integration via `services/api.ts`

### Database Operations
- ChromaDB vector storage management
- Backup handling (`chroma_db.backup_*`)
- PDF document indexing

### PDF Processing
- Batch upload via `upload_pdfs_batch.py`
- PDF integration documentation in `PDF_UPLOAD_GUIDE.md`

## Architecture Principles

1. **Modular Services**: Backend microservices communicate via well-defined APIs
2. **Type Safety**: TypeScript for frontend, Pydantic models for backend
3. **Security First**: Environment-based configuration, no hardcoded secrets
4. **Educational Focus**: All features designed to enhance learning experiences
5. **Scalability**: ChromaDB for efficient vector storage and retrieval

## Recent Changes

Based on recent commits:
- Frontend updates and enhancements
- Logger implementation and fixes
- Router agent integration
- Design pattern implementations
- Code structure improvements

## Development Guidelines

### Before Code Changes
- Read existing implementations thoroughly
- Understand the WHY before the WHAT
- Question patterns that feel disconnected or unclear
- Prefer clarity over clever solutions

### Code Quality
- Run pytest before commits
- Ensure pre-commit hooks pass
- Maintain TypeScript type safety
- Document API changes

### Git Workflow
- Branch naming: feature/description or fix/description
- Commit messages: Clear, concise descriptions
- Current branch: `main`

## Debugging Tips

### API Connection Issues
1. Check `.env` file exists and is loaded
2. Verify API keys are set correctly
3. Review startup logs for environment loading
4. Ensure no conflicting environment overrides

### Frontend Issues
1. Check console for TypeScript errors
2. Verify API endpoint URLs in `services/api.ts`
3. Inspect network tab for failed requests
4. Review component state management

### Backend Issues
1. Check FastAPI logs for exceptions
2. Verify database connections (ChromaDB)
3. Test API endpoints with curl/Postman
4. Review service integration points

## File Locations

- **Backend Code**: `/backend`
- **Frontend Code**: `/frontend/src`
- **Components**: `/frontend/src/components`
- **Types**: `/frontend/src/types`
- **Services**: `/frontend/src/services`
- **Documentation Images**: `/img`
- **Startup Script**: `start-all.sh`
- **Logs**: `app.log`

## When to Use This Skill

Invoke this skill when:
- Developing or debugging AI Teacher features
- Working with educational AI components
- Integrating new services or APIs
- Troubleshooting chat, studio, or map features
- Understanding the architecture
- Planning feature implementations
- Reviewing code structure or patterns
- Setting up development environment
