"""FastAPI application for document processing"""

import os
import logging
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import json
import shutil
from pathlib import Path

from config import Config, setup_logging
from models import StatusResponse, WebPageRequest, QueryResponse, QueryRequest, ChatRequest, ChatResponse
from simple_chat_service import SimpleChatService

# Import design patterns
from patterns import (
    DocumentLoaderFactory,
    EmbeddingFactory,
    ChunkingContext,
    RecursiveChunkingStrategy,
    create_vector_repository,
    VectorStoreManagerSingleton
)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Validate config
try:
    Config.validate()
    if Config.USE_OPENAI_EMBEDDINGS:
        os.environ["OPENAI_API_KEY"] = Config.OPENAI_API_KEY
        logger.info("Using OpenAI embeddings - API key loaded")
    else:
        logger.info("Using FREE local HuggingFace embeddings - no API key needed!")
except ValueError as e:
    logger.error(str(e))
    raise

# Initialize FastAPI app
app = FastAPI(
    title="Document Processing API",
    description="API for processing PDFs and web pages with LangChain and Chroma DB",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components using Design Patterns

# Singleton Pattern - Vector Store Manager (ensures single instance)
vector_manager = VectorStoreManagerSingleton()

# Repository Pattern - Clean data access layer
vector_repository = create_vector_repository(
    repository_type="chroma",
    vector_store_manager=vector_manager
)

# Strategy Pattern - Chunking strategy (can be changed at runtime)
chunking_context = ChunkingContext(
    RecursiveChunkingStrategy(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP
    )
)

# Chat service
chat_service = SimpleChatService()

# Create uploads directory
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

logger.info("Document Processing API initialized")


@app.on_event("startup")
async def startup_event():
    """Log startup event"""
    logger.info("FastAPI application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown event"""
    logger.info("FastAPI application shutting down")


@app.get("/", response_model=StatusResponse)
async def root():
    """Root endpoint with API information"""
    logger.info("Root endpoint accessed")
    return StatusResponse(
        status="success",
        message="Document Processing API is running",
        details={
            "endpoints": [
                "/docs - API documentation",
                "/health - Health check",
                "/test-embeddings - Test embeddings",
                "/upload-pdf - Upload and process PDF files",
                "/process-webpages - Process web pages from URLs",
                "/query - Query the vector store",
                "/chat - Chat with AI (with optional RAG)",
                "/chat/stream - Stream chat responses",
                "/chat/history/{session_id} - Get chat history",
                "/chat/clear/{session_id} - Clear chat session",
                "/clear-vector-store - Clear all documents"
            ]
        }
    )


@app.get("/health", response_model=StatusResponse)
async def health_check():
    """Health check endpoint"""
    logger.debug("Health check endpoint accessed")
    return StatusResponse(
        status="healthy",
        message="Service is operational"
    )


@app.get("/test-embeddings", response_model=StatusResponse)
async def test_embeddings():
    """Test if embeddings are working"""
    logger.info("Testing embeddings...")
    try:
        # Use the same embeddings as VectorStoreManager
        if Config.USE_OPENAI_EMBEDDINGS:
            from langchain_openai import OpenAIEmbeddings
            embeddings = OpenAIEmbeddings()
            embedding_type = "OpenAI"
        else:
            from langchain_huggingface import HuggingFaceEmbeddings
            embeddings = HuggingFaceEmbeddings(
                model_name=Config.EMBEDDING_MODEL
            )
            embedding_type = f"HuggingFace ({Config.EMBEDDING_MODEL})"

        # Test embedding generation
        test_text = "This is a test sentence for embeddings."
        logger.info(f"Generating test embedding with {embedding_type}...")
        embedding = embeddings.embed_query(test_text)

        logger.info(f"Embedding test successful. Type: {embedding_type}, Dimension: {len(embedding)}")
        return StatusResponse(
            status="success",
            message="Embeddings are working correctly",
            details={
                "embedding_type": embedding_type,
                "embedding_dimension": len(embedding),
                "test_text": test_text
            }
        )
    except Exception as e:
        logger.error(f"Embedding test failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Embedding test failed: {str(e)}"
        )


@app.post("/upload-pdf", response_model=StatusResponse)
async def upload_pdf(files: List[UploadFile] = File(...)):
    """
    Upload and process PDF files

    - **files**: List of PDF files to upload and process
    """
    logger.info(f"Received request to upload {len(files)} PDF files")
    try:
        pdf_paths = []

        # Save uploaded files
        for file in files:
            if not file.filename.endswith('.pdf'):
                logger.warning(f"Rejected non-PDF file: {file.filename}")
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} is not a PDF"
                )

            file_path = UPLOAD_DIR / file.filename
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            pdf_paths.append(str(file_path))
            logger.info(f"Saved uploaded file: {file.filename}")

        # Factory Pattern: Load PDFs using appropriate loader
        all_documents = []
        for pdf_path in pdf_paths:
            try:
                # Factory automatically detects if OCR is needed
                document_loader = DocumentLoaderFactory.create_loader(
                    file_path=pdf_path,
                    auto_detect=True  # Auto-detect scanned PDFs
                )
                documents = document_loader.load(pdf_path)
                all_documents.extend(documents)
                logger.info(f"Loaded {len(documents)} pages from {Path(pdf_path).name}")
            except Exception as e:
                logger.error(f"Error loading {pdf_path}: {e}")
                raise HTTPException(status_code=400, detail=f"Error loading {Path(pdf_path).name}: {str(e)}")

        if not all_documents:
            raise HTTPException(
                status_code=400,
                detail="No content could be extracted from the PDFs"
            )

        logger.info(
            f"Loaded {len(all_documents)} pages with total characters: {sum(len(doc.page_content) for doc in all_documents)}")

        # Strategy Pattern: Chunk documents using configured strategy
        chunks = chunking_context.chunk_documents(all_documents)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No chunks created from documents. Documents may be empty."
            )

        logger.info(f"Created {len(chunks)} chunks using {chunking_context.strategy.__class__.__name__}")

        # Repository Pattern: Add documents to vector store
        vector_repository.add_documents(chunks)
        action = "updated"

        logger.info(f"Successfully processed {len(files)} PDFs. Vector store {action}.")
        return StatusResponse(
            status="success",
            message=f"PDFs processed successfully. Vector store {action}.",
            details={
                "files_processed": len(files),
                "total_chunks": len(chunks),
                "filenames": [f.filename for f in files]
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDFs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-webpages", response_model=StatusResponse)
async def process_webpages(request: WebPageRequest):
    """
    Process web pages from URLs

    - **urls**: List of URLs to process
    """
    urls = [str(url) for url in request.urls]
    logger.info(f"Received request to process {len(urls)} web pages")
    try:
        # Load web pages using WebBaseLoader
        from langchain_community.document_loaders import WebBaseLoader

        all_documents = []
        for url in urls:
            try:
                web_loader = WebBaseLoader(url)
                documents = web_loader.load()
                all_documents.extend(documents)
                logger.info(f"Loaded content from {url}")
            except Exception as e:
                logger.error(f"Error loading {url}: {e}")
                raise HTTPException(status_code=400, detail=f"Error loading {url}: {str(e)}")

        if not all_documents:
            raise HTTPException(
                status_code=400,
                detail="No content could be extracted from the URLs"
            )

        # Strategy Pattern: Chunk documents using configured strategy
        chunks = chunking_context.chunk_documents(all_documents)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No chunks created from documents. Documents may be empty."
            )

        logger.info(f"Created {len(chunks)} chunks using {chunking_context.strategy.__class__.__name__}")

        # Repository Pattern: Add documents to vector store
        vector_repository.add_documents(chunks)

        logger.info(f"Successfully processed {len(urls)} web pages. Vector store updated.")
        return StatusResponse(
            status="success",
            message=f"Web pages processed successfully. Vector store updated.",
            details={
                "urls_processed": len(urls),
                "total_chunks": len(chunks),
                "urls": urls
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing web pages: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query_vector_store(request: QueryRequest):
    """
    Query the vector store for similar documents

    - **query**: Search query string
    - **k**: Number of results to return (default: 4)
    """
    logger.info(f"Received query request: '{request.query}' with k={request.k}")
    try:
        # Repository Pattern: Search for similar documents
        results = vector_repository.search(request.query, k=request.k)

        # Format results
        formatted_results = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in results
        ]

        logger.info(f"Query completed successfully. Returning {len(formatted_results)} results")
        return QueryResponse(
            query=request.query,
            results=formatted_results,
            total_results=len(formatted_results)
        )

    except Exception as e:
        logger.error(f"Error querying vector store: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/clear-vector-store", response_model=StatusResponse)
async def clear_vector_store():
    """Clear the vector store (delete all documents)"""
    logger.warning("Received request to clear vector store")
    try:
        chroma_dir = Path(Config.CHROMA_PERSIST_DIR)

        if chroma_dir.exists():
            shutil.rmtree(chroma_dir)
            logger.info("Vector store cleared successfully")
            return StatusResponse(
                status="success",
                message="Vector store cleared successfully"
            )
        else:
            logger.info("Vector store was already empty")
            return StatusResponse(
                status="success",
                message="Vector store was already empty"
            )

    except Exception as e:
        logger.error(f"Error clearing vector store: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the AI assistant

    - **message**: User message
    - **session_id**: Optional session ID for conversation continuity
    - **use_rag**: Whether to use RAG (default: true)
    """
    logger.info(f"Received chat request: '{request.message[:50]}...' with RAG={request.use_rag}")
    try:
        response, session_id, sources = await chat_service.chat(
            message=request.message,
            session_id=request.session_id,
            use_rag=request.use_rag
        )

        logger.info(f"Chat response generated for session {session_id}")
        return ChatResponse(
            response=response,
            session_id=session_id,
            sources=sources
        )

    except Exception as e:
        logger.error(f"Error in chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat responses from the AI assistant

    - **message**: User message
    - **session_id**: Optional session ID for conversation continuity
    - **use_rag**: Whether to use RAG (default: true)
    """
    logger.info(f"Received streaming chat request: '{request.message[:50]}...'")

    async def event_generator():
        try:
            async for chunk, session_id, sources in chat_service.chat_stream(
                message=request.message,
                session_id=request.session_id,
                use_rag=request.use_rag
            ):
                # Send text chunks
                if chunk:
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"

                # Send sources in final message
                if sources is not None:
                    yield f"data: {json.dumps({'type': 'sources', 'sources': sources, 'session_id': session_id})}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            logger.error(f"Error in streaming chat: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    logger.info(f"Retrieving history for session {session_id}")
    try:
        history = chat_service.get_session_history(session_id)

        if history is None:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "session_id": session_id,
            "history": history
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/chat/clear/{session_id}", response_model=StatusResponse)
async def clear_chat_session(session_id: str):
    """Clear a chat session"""
    logger.info(f"Clearing session {session_id}")
    try:
        success = chat_service.clear_session(session_id)

        if not success:
            raise HTTPException(status_code=404, detail="Session not found")

        return StatusResponse(
            status="success",
            message=f"Session {session_id} cleared successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting uvicorn server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )